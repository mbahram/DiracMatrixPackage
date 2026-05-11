#!/usr/bin/env python3
"""
build_ref_pages.py
==================

Generate WFR-paclet-style Mathematica reference pages for every public symbol
of the DiracMatrix paclet. Follows the regime-(d) workflow from
~/.claude/prompts/paclet-doc-rewrite-template.md (pure-function regime).

Pipeline:
  1.  For each example (Input cell), invoke the Wolfram kernel ONCE via
      wolframscript and obtain:
        (a) the parsed BoxData[RowBox[...]] of the input code (via
            FrontEnd`UndocumentedTestFEParserPacket — the front-end parser
            Mathematica uses when saving notebooks);
        (b) optionally, the BoxData of the evaluation result
            (ToBoxes[result, StandardForm]); and
        (c) any messages emitted while evaluating.
  2.  Assemble each .nb file from these payloads using the WFR-paclet
      FunctionPageStylesExt style sheet, mirroring the structure of
      EinsteinSummation.nb (TensorNetworks).
  3.  Validate every output with
      ~/.claude/skills/nb-writer/scripts/validate_nb.py.

House rules followed:
  * No Quiet — every Message that fires is captured and surfaced in
    the Possible Issues section.
  * wolframscript via subprocess; never the WolframLanguageEvaluator MCP.
  * Bootstrap mode: no source pages to back up; sibling style cribbed
    from Wolfram/TensorNetworks/.../EinsteinSummation.nb.

Usage:
    python3 build_ref_pages.py --symbol FlatMetric
    python3 build_ref_pages.py                       # all 10
"""

from __future__ import annotations

import argparse
import os
import random
import re
import subprocess
import sys
import textwrap
import uuid
from dataclasses import dataclass, field
from pathlib import Path

PACLET_ROOT = Path("/Users/mohammadb/Nextcloud/Mads/Quantum/DiracMatrix/DiracMatrixPackage")
DOCS_DIR    = PACLET_ROOT / "Documentation" / "English" / "ReferencePages" / "Symbols"
PACLET_NAME = "DiracMatrix"
PACLET_CTX  = "DiracMatrix`"

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class UsageRow:
    code: str
    gloss: str


@dataclass
class Example:
    """One Input/Output cell pair, optionally preceded by an ExampleText."""
    text: str | None
    input: str
    show_output: bool = True
    # filled in by verify_examples():
    in_box: str | None = field(default=None, repr=False)
    out_box: str | None = field(default=None, repr=False)
    messages: list[str] = field(default_factory=list, repr=False)


@dataclass
class ExampleSubsection:
    title: str
    examples: list[Example] = field(default_factory=list)


@dataclass
class PossibleIssue:
    text: str
    input: str
    show_output: bool = True
    # filled in by verify_examples():
    in_box: str | None = field(default=None, repr=False)
    out_box: str | None = field(default=None, repr=False)
    messages: list[str] = field(default_factory=list, repr=False)


@dataclass
class RefPage:
    symbol: str
    usage_rows: list[UsageRow]
    details_notes: list[str]                       # one Notes cell per item
    basic_examples: list[Example]
    scope: list[ExampleSubsection] = field(default_factory=list)
    generalizations: list[ExampleSubsection] = field(default_factory=list)
    applications: list[ExampleSubsection] = field(default_factory=list)
    possible_issues: list[PossibleIssue] = field(default_factory=list)
    neat_examples: list[Example] = field(default_factory=list)
    see_also: list[str] = field(default_factory=list)
    related_guides: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Wolfram string utilities
# ---------------------------------------------------------------------------


# Wolfram-string escape sequences that must be preserved verbatim when we
# wrap a Python string as a .nb string literal. The naive replace("\\","\\\\")
# would corrupt every one of these.
#
#   \[Name]      named character (Bullet, LineSeparator, LeftFloor, ...)
#   \n \t \r \f  whitespace escapes
#   \"           escaped quote
#   \\           literal backslash (already-escaped)
#   \:NNNN       four-hex Unicode codepoint
#   \.HH         two-hex byte
_PRESERVED_ESC_RE = re.compile(
    r'\\\[[A-Za-z][A-Za-z0-9]*\]'   # \[Name]
    r'|\\:[0-9a-fA-F]{4}'            # \:NNNN
    r'|\\\.[0-9a-fA-F]{2}'           # \.HH
    r'|\\[ntrf\\"]'                  # \n \t \r \f \\ \"
)


def nb_quote(s: str) -> str:
    """Quote a Python string as a .nb string literal, preserving Wolfram
    string escape sequences as single-backslash forms in the file so the
    front end interprets them correctly. Anything not recognised as an
    escape is treated as a literal character — bare backslashes in
    arbitrary input get doubled to '\\\\' as expected."""
    matches = _PRESERVED_ESC_RE.findall(s)
    sentinel = "\x00\x01ESC\x01\x00"
    masked = _PRESERVED_ESC_RE.sub(sentinel, s)
    body = masked.replace("\\", "\\\\").replace('"', '\\"')
    for m in matches:
        body = body.replace(sentinel, m, 1)
    return '"' + body + '"'


def wl_string(s: str) -> str:
    """Embed a Python str as a Wolfram String literal (for the helper .wl)."""
    body = s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return '"' + body + '"'


# ---------------------------------------------------------------------------
# Deterministic UUID / CellID generators
# ---------------------------------------------------------------------------

_RNG = random.Random(0xD17AC)  # deterministic & reproducible across runs


def uuid_str() -> str:
    return str(uuid.UUID(int=_RNG.getrandbits(128), version=4))


def cell_id() -> int:
    return _RNG.randint(10_000_000, 2_147_483_647)


# ---------------------------------------------------------------------------
# Wolfram kernel batch: parse inputs + capture outputs in one pass
# ---------------------------------------------------------------------------


def kernel_batch(items: list[tuple[int, str, bool]]) -> dict[int, dict[str, object]]:
    """Run a batch of items through wolframscript. Each item is
       (i, wolfram-code, want_output).
    Returns a dict keyed by i with the in_box / out_box / messages.

    Implementation: writes one .wl file, runs wolframscript -file, parses
    the marker-delimited stdout.
    """
    if not items:
        return {}
    wl_items = (
        "{" +
        ", ".join(
            "{" + str(i) + ", " + wl_string(code) + ", " +
            ("True" if want else "False") + "}"
            for i, code, want in items
        ) +
        "}"
    )
    script = textwrap.dedent(
        """
        Off[General::stop];   (* never collapse repeated messages *)
        PacletDirectoryLoad["__PACLET_ROOT__"];
        Needs["__PACLET_CTX__"];

        captureMessages[expr_] := Module[{msgs = {}, value, h},
          h = Function[{tag, args}, AppendTo[msgs, ToString[Hold[tag][args],
                InputForm, CharacterEncoding -> "PrintableASCII"]], HoldAll];
          Internal`HandlerBlock[
            {"Message", Function[m,
               AppendTo[msgs, ToString[First[m], InputForm,
                 CharacterEncoding -> "PrintableASCII"]]]},
            value = expr];
          {value, msgs}];

        Do[
          Module[{i = it[[1]], code = it[[2]], wantOut = it[[3]],
                  inBox, value, outBox, msgs, ok},
            (* (a) parse the input code via the front-end parser *)
            inBox = First @ UsingFrontEnd[
              MathLink`CallFrontEnd[
                FrontEnd`UndocumentedTestFEParserPacket[code, False]]];
            Print["===IBOX_", i, "==="];
            Print[ToString[inBox, InputForm,
              CharacterEncoding -> "PrintableASCII", PageWidth -> Infinity]];
            Print["===END==="];
            If[TrueQ[wantOut],
              (* Guard against runaway evaluation (RecursionLimit, etc.). *)
              ok = TimeConstrained[
                Block[{$RecursionLimit = 4096, $IterationLimit = 4096},
                  {value, msgs} = captureMessages[ToExpression[code, InputForm]];
                  outBox = ToBoxes[value, StandardForm];
                  True], 30, False];
              If[!ok,
                outBox = RowBox[{StyleBox["(* timeout / runaway evaluation *)",
                  FontColor -> RGBColor[0.6, 0.6, 0.6]]}];
                msgs   = {"TIMEOUT or recursion limit exceeded"}];
              Print["===OBOX_", i, "==="];
              Print[ToString[outBox, InputForm,
                CharacterEncoding -> "PrintableASCII", PageWidth -> Infinity]];
              Print["===END==="];
              Print["===MSGS_", i, "==="];
              Print[StringRiffle[msgs, "\n"]];
              Print["===END==="]]
          ],
          {it, $items}]
        """.strip()
    )
    full = (
        "$items = " + wl_items + ";\n" +
        script
            .replace("__PACLET_ROOT__", str(PACLET_ROOT))
            .replace("__PACLET_CTX__",  PACLET_CTX)
    )
    script_path = Path("/tmp/dirac-kernel-batch.wl")
    script_path.write_text(full)
    print(f"[kernel] running {len(items)} items via {script_path}")
    res = subprocess.run(
        ["wolframscript", "-file", str(script_path)],
        capture_output=True, text=True, timeout=900,
    )
    if res.returncode != 0:
        sys.stderr.write("---- STDERR ----\n" + res.stderr + "\n")
        sys.stderr.write("---- STDOUT ----\n" + res.stdout[:2000] + "\n")
        raise RuntimeError(
            f"kernel_batch: wolframscript exit {res.returncode}")
    return _parse_kernel_output(res.stdout, items)


def _slice(text: str, marker: str) -> str | None:
    """Return the text between marker and the next ===END===, or None."""
    s = text.find(marker)
    if s == -1:
        return None
    s += len(marker)
    if text[s] == "\n":
        s += 1
    e = text.find("\n===END===", s)
    if e == -1:
        return None
    return text[s:e]


def _strip_boxdata(s: str) -> str:
    """If a payload comes wrapped in BoxData[...], strip the wrapper."""
    s = s.strip()
    if s.startswith("BoxData[") and s.endswith("]"):
        return s[len("BoxData["):-1]
    return s


def _parse_kernel_output(stdout: str, items: list[tuple[int, str, bool]]) -> dict[int, dict[str, object]]:
    out: dict[int, dict[str, object]] = {}
    for i, code, want in items:
        in_marker  = f"===IBOX_{i}==="
        out_marker = f"===OBOX_{i}==="
        msg_marker = f"===MSGS_{i}==="
        in_text  = _slice(stdout, in_marker)
        if in_text is None:
            raise RuntimeError(f"kernel_batch: missing IBOX for {i}: {code!r}")
        record: dict[str, object] = {"in_box": _strip_boxdata(in_text)}
        if want:
            out_text = _slice(stdout, out_marker)
            msg_text = _slice(stdout, msg_marker)
            if out_text is None:
                raise RuntimeError(f"kernel_batch: missing OBOX for {i}: {code!r}")
            record["out_box"] = _strip_boxdata(out_text)
            msgs = [m for m in (msg_text or "").splitlines() if m.strip()]
            record["messages"] = msgs
        out[i] = record
    return out


# ---------------------------------------------------------------------------
# Walk a RefPage and feed every example through the kernel
# ---------------------------------------------------------------------------


def all_examples(page: RefPage) -> list[Example]:
    """Flatten every Example / PossibleIssue in a RefPage so they can be
    indexed for the kernel batch."""
    flat: list[Example] = list(page.basic_examples)
    for grp in (page.scope, page.generalizations, page.applications):
        for sub in grp:
            flat.extend(sub.examples)
    flat.extend(page.neat_examples)
    flat.extend(page.possible_issues)
    return flat


def verify_examples(page: RefPage) -> None:
    """For every example in the page, run the kernel batch and write
    in_box / out_box / messages back into the example objects."""
    items: list[tuple[int, str, bool]] = []
    flat = all_examples(page)
    for i, ex in enumerate(flat):
        items.append((i, ex.input, ex.show_output))
    # Add Needs[…] (always needed for the ExampleInitialization cell).
    needs_idx = len(items)
    items.append((needs_idx, 'Needs["DiracMatrix`"]', False))
    # Add each Usage code (boxify only; no evaluation needed).
    usage_start = len(items)
    for j, r in enumerate(page.usage_rows):
        items.append((usage_start + j, r.code, False))

    records = kernel_batch(items)
    for i, ex in enumerate(flat):
        rec = records[i]
        ex.in_box = rec["in_box"]                  # type: ignore
        if ex.show_output:
            ex.out_box  = rec["out_box"]           # type: ignore
            captured = rec["messages"]             # type: ignore
            # Preserve spec-supplied messages if the kernel didn't capture
            # any (some messages go directly to stderr / FE channel and
            # don't show up in our HandlerBlock capture).
            if captured:
                ex.messages = captured             # type: ignore

    # stash Needs and usage boxes on the page object
    page._needs_box   = records[needs_idx]["in_box"]                    # type: ignore[attr-defined]
    page._usage_boxes = [
        records[usage_start + j]["in_box"] for j in range(len(page.usage_rows))
    ]                                                                    # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# Cell builders
# ---------------------------------------------------------------------------

WL_STYLE = (
    'StyleDefinitions->FrontEnd`FileName[{"Wolfram"}, '
    '"FunctionPageStylesExt.nb", CharacterEncoding -> "UTF-8"]'
)


def _textdata_with_tex(prose: str) -> str:
    """If prose contains %%TEX%% placeholders, build a TextData list.
    Else return a plain quoted string."""
    parts = re.split(r"(%%TEX:.*?%%)", prose)
    if len(parts) == 1:
        return nb_quote(prose)
    out: list[str] = []
    for p in parts:
        if not p:
            continue
        if p.startswith("%%TEX:"):
            # TeX placeholders carry their own escaping — only escape quotes.
            out.append('"' + p.replace('"', '\\"') + '"')
        else:
            out.append(nb_quote(p))
    return "TextData[{" + ", ".join(out) + "}]"


def _text_cell(body: str, style: str) -> str:
    body_rendered = _textdata_with_tex(body)
    return (
        f"Cell[{body_rendered}, {nb_quote(style)},\n"
        f" CellID->{cell_id()}, ExpressionUUID->{nb_quote(uuid_str())}]"
    )


def cell_objectname(symbol: str) -> str:
    return (
        f'Cell[{nb_quote(symbol)}, "ObjectName",\n'
        f' CellID->{cell_id()}, ExpressionUUID->{nb_quote(uuid_str())}]'
    )


def cell_usage(rows: list[UsageRow], usage_boxes: list[str]) -> str:
    """Render the Usage cell following the canonical WFR pattern used by
    every native QuantumFramework symbol page (QuantumState.nb,
    QuantumOperator.nb, QuantumChannel.nb, etc.):

        Cell[TextData[{
          Cell[BoxData[<sig1>], "InlineFormula", ...],
          "\\[LineSeparator]<gloss1>.\\n",
          Cell["   ", "ModInfo", ...],
          Cell[BoxData[<sig2>], "InlineFormula", ...],
          "\\[LineSeparator]<gloss2>.\\n",
          ...
          Cell[BoxData[<sigN>], "InlineFormula", ...],
          "\\[LineSeparator]<glossN>."
        }], "Usage", ...]

    NB: no `\\[Bullet]` between rows — that decoration appears in some
    paclets (e.g. TensorNetworks) but is absent from QF natives and was
    flagged as visually noisy in user review.
    """
    elements: list[str] = []
    for i, (r, box) in enumerate(zip(rows, usage_boxes)):
        is_last = (i == len(rows) - 1)
        # Signature
        elements.append(
            f'Cell[BoxData[{box}], "InlineFormula",\n'
            f' ExpressionUUID->{nb_quote(uuid_str())}]'
        )
        # Gloss — \[LineSeparator] introduces, \n soft-breaks (skip on last)
        gloss = "\\[LineSeparator]" + r.gloss
        if not is_last:
            gloss += "\\n"
        elements.append(_textdata_with_tex(gloss))
        # ModInfo indent for the next row
        if not is_last:
            elements.append(
                f'Cell["   ", "ModInfo",\n'
                f' ExpressionUUID->{nb_quote(uuid_str())}]'
            )
    # Splice in any TextData[{...}] returned by the TeX placeholder expander
    flat: list[str] = []
    for el in elements:
        if el.startswith("TextData[{") and el.endswith("}]"):
            flat.append(el[len("TextData[{"):-2])
        else:
            flat.append(el)
    inner = ", ".join(flat)
    return (
        f'Cell[TextData[{{\n{inner}\n}}], "Usage",\n'
        f' CellID->{cell_id()}, ExpressionUUID->{nb_quote(uuid_str())}]'
    )


def cell_input(in_box: str) -> str:
    return (
        f'Cell[BoxData[{in_box}], "Input",\n'
        f' CellID->{cell_id()}, ExpressionUUID->{nb_quote(uuid_str())}]'
    )


def cell_output(out_box: str) -> str:
    return (
        f'Cell[BoxData[{out_box}], "Output",\n'
        f' CellID->{cell_id()}, ExpressionUUID->{nb_quote(uuid_str())}]'
    )


def cell_message(msg_text: str) -> str:
    """Format a captured message as a Cell of type Message/MSG."""
    return (
        f'Cell[BoxData[{nb_quote(msg_text)}], "Message", "MSG",\n'
        f' CellID->{cell_id()}, ExpressionUUID->{nb_quote(uuid_str())}]'
    )


def cell_example_text(text: str) -> str:
    return _text_cell(text, "ExampleText")


def cell_notes(text: str) -> str:
    return _text_cell(text, "Notes")


def cell_section_header(
    title: str, style: str, more_info: str | None = None
) -> str:
    """Standard <X>Section header. The optional more_info is accepted for
    API symmetry but ignored: the WFR FunctionPage style sheet renders
    plain section headers cleanly without the More-Info popup.
    """
    return (
        f'Cell[{nb_quote(title)}, {nb_quote(style)},\n'
        f' CellID->{cell_id()}, ExpressionUUID->{nb_quote(uuid_str())}]'
    )


def cell_example_section(title: str) -> str:
    inner = uuid_str()
    return (
        f'Cell[BoxData[\n'
        f' InterpretationBox[Cell[\n'
        f'  {nb_quote(title)}, "ExampleSection",ExpressionUUID->{nb_quote(inner)}],\n'
        f'  $Line = 0; Null]], "ExampleSection",\n'
        f' CellID->{cell_id()}, ExpressionUUID->{nb_quote(uuid_str())}]'
    )


def cell_seealso(symbols: list[str]) -> str:
    """A SeeAlso TextData with plain ButtonBox links separated by
    \\[FilledVerySmallSquare] glyphs."""
    if not symbols:
        return (
            f'Cell[" ", "SeeAlso",\n'
            f' CellID->{cell_id()}, ExpressionUUID->{nb_quote(uuid_str())}]'
        )
    sep = nb_quote(" \\[FilledVerySmallSquare] ")
    parts: list[str] = []
    for i, sym in enumerate(symbols):
        if i > 0:
            parts.append(sep)
        parts.append(
            f'Cell[BoxData[ButtonBox[{nb_quote(sym)},\n'
            f' BaseStyle->"Link",\n'
            f' ButtonData->"paclet:{PACLET_NAME}/ref/{sym}"]],\n'
            f' "InlineFormula", ExpressionUUID->{nb_quote(uuid_str())}]'
        )
    return (
        f'Cell[TextData[{{\n{", ".join(parts)}\n}}], "SeeAlso",\n'
        f' CellID->{cell_id()}, ExpressionUUID->{nb_quote(uuid_str())}]'
    )


# ---------------------------------------------------------------------------
# Grouping and assembly
# ---------------------------------------------------------------------------


def _cellgroup(cells: list[str], open_state: str = "Open") -> str:
    inner = ",\n".join(cells)
    return f"Cell[CellGroupData[{{\n{inner}\n}}, {open_state}]]"


def _render_example(ex: Example) -> list[str]:
    out: list[str] = []
    if ex.text is not None:
        out.append(cell_example_text(ex.text))
    cells: list[str] = [cell_input(ex.in_box or "")]
    for m in ex.messages:
        cells.append(cell_message(m))
    if ex.show_output and ex.out_box:
        cells.append(cell_output(ex.out_box))
    if len(cells) == 1:
        out.extend(cells)
    else:
        out.append(_cellgroup(cells))
    return out


def _render_issue(issue: PossibleIssue) -> list[str]:
    out: list[str] = [cell_example_text(issue.text)]
    cells: list[str] = [cell_input(issue.in_box or "")]
    for m in issue.messages:
        cells.append(cell_message(m))
    if issue.show_output and issue.out_box:
        cells.append(cell_output(issue.out_box))
    if len(cells) == 1:
        out.extend(cells)
    else:
        out.append(_cellgroup(cells))
    return out


def _categorization_group(symbol: str) -> str:
    return _cellgroup([
        cell_section_header("Categorization", "CategorizationSection",
            more_info="Metadata such as page URI, context, and type of documentation page."),
        f'Cell["Symbol", "Categorization",\n CellLabel->"Entity Type",\n'
        f' CellID->{cell_id()}, ExpressionUUID->{nb_quote(uuid_str())}]',
        f'Cell[{nb_quote(PACLET_NAME)}, "Categorization",\n CellLabel->"Paclet Name",\n'
        f' CellID->{cell_id()}, ExpressionUUID->{nb_quote(uuid_str())}]',
        f'Cell[{nb_quote(PACLET_CTX)}, "Categorization",\n CellLabel->"Context",\n'
        f' CellID->{cell_id()}, ExpressionUUID->{nb_quote(uuid_str())}]',
        f'Cell[{nb_quote(PACLET_NAME + "/ref/" + symbol)}, "Categorization",\n'
        f' CellLabel->"URI",\n'
        f' CellID->{cell_id()}, ExpressionUUID->{nb_quote(uuid_str())}]',
    ], open_state="Closed")


def _keywords_group(kws: list[str]) -> str:
    cells = [cell_section_header("Keywords", "KeywordsSection")]
    if not kws:
        cells.append(
            f'Cell[" ", "Keywords",\n'
            f' CellID->{cell_id()}, ExpressionUUID->{nb_quote(uuid_str())}]'
        )
    else:
        for kw in kws:
            cells.append(
                f'Cell[{nb_quote(kw)}, "Keywords",\n'
                f' CellID->{cell_id()}, ExpressionUUID->{nb_quote(uuid_str())}]'
            )
    return _cellgroup(cells, open_state="Closed")


def _templates_group() -> str:
    cells = [cell_section_header("Syntax Templates", "TemplatesSection")]
    for label in (
        "Additional Function Template",
        "Arguments Pattern",
        "Local Variables",
        "Color Equal Signs",
    ):
        cells.append(
            f'Cell[BoxData[""], "Template",\n CellLabel->{nb_quote(label)},\n'
            f' CellID->{cell_id()}, ExpressionUUID->{nb_quote(uuid_str())}]'
        )
    return _cellgroup(cells, open_state="Closed")


def _metadata_group(page: RefPage) -> str:
    history = (
        'Cell[TextData[{\n'
        ' "New in: ",\n'
        f' Cell["1.0.0", "HistoryData",\n'
        f'  CellTags->"New", ExpressionUUID->{nb_quote(uuid_str())}],\n'
        ' " | Modified in: ",\n'
        f' Cell[" ", "HistoryData",\n'
        f'  CellTags->"Modified", ExpressionUUID->{nb_quote(uuid_str())}],\n'
        ' " | Obsolete in: ",\n'
        f' Cell[" ", "HistoryData",\n'
        f'  CellTags->"Obsolete", ExpressionUUID->{nb_quote(uuid_str())}]\n'
        '}], "History",\n'
        f' CellID->{cell_id()}, ExpressionUUID->{nb_quote(uuid_str())}]'
    )
    return _cellgroup([
        cell_section_header("Metadata", "MetadataSection",
            more_info="Metadata such as page URI, context, and type of documentation page."),
        history,
        _categorization_group(page.symbol),
        _keywords_group(page.keywords),
        _templates_group(),
    ])


def build_notebook(page: RefPage) -> str:
    sym = page.symbol
    usage_boxes = getattr(page, "_usage_boxes", [])
    needs_box   = getattr(page, "_needs_box", '""')

    # Top: ObjectName + Usage + Notes
    top_cells: list[str] = [
        cell_objectname(sym),
        cell_usage(page.usage_rows, usage_boxes),
    ]
    for n in page.details_notes:
        top_cells.append(cell_notes(n))
    top_group = _cellgroup(top_cells)

    # See Also
    seealso_group = _cellgroup([
        cell_section_header("See Also", "SeeAlsoSection",
            more_info="Related Wolfram Language and DiracMatrix symbols."),
        cell_seealso(page.see_also),
    ])

    # Tech Notes / More About / Related Links — minimal placeholders
    technotes_group = _cellgroup([
        cell_section_header("Tech Notes", "TechNotesSection"),
        f'Cell[" ", "Tutorials",\n CellID->{cell_id()}, '
        f'ExpressionUUID->{nb_quote(uuid_str())}]',
    ])
    if page.related_guides:
        more_about_cells: list[str] = []
        for g in page.related_guides:
            more_about_cells.append(
                'Cell[TextData[{\n'
                f'Cell[BoxData[ButtonBox[{nb_quote(g)},\n'
                f' BaseStyle->"Link",\n'
                f' ButtonData->"paclet:{PACLET_NAME}/guide/{g}"]],\n'
                f' "InlineFormula", ExpressionUUID->{nb_quote(uuid_str())}]\n'
                f'}}], "MoreAbout",\n'
                f' CellID->{cell_id()}, ExpressionUUID->{nb_quote(uuid_str())}]'
            )
    else:
        more_about_cells = [
            f'Cell[" ", "MoreAbout",\n CellID->{cell_id()}, '
            f'ExpressionUUID->{nb_quote(uuid_str())}]'
        ]
    moreabout_group = _cellgroup([
        cell_section_header("More About", "MoreAboutSection"),
    ] + more_about_cells)
    relatedlinks_group = _cellgroup([
        cell_section_header("Related Links", "RelatedLinksSection"),
        f'Cell[" ", "RelatedLinks",\n CellID->{cell_id()}, '
        f'ExpressionUUID->{nb_quote(uuid_str())}]',
    ])

    # Examples Initialization
    init_group = _cellgroup([
        cell_section_header(
            "Examples Initialization", "ExamplesInitializationSection",
            more_info="Code preceding the Basic Examples is run "
                      "once when the notebook is opened."),
        f'Cell[BoxData[{needs_box}], "ExampleInitialization",\n'
        f' CellID->{cell_id()}, ExpressionUUID->{nb_quote(uuid_str())}]',
    ])

    # Basic Examples
    basic_cells: list[str] = [
        cell_section_header("Basic Examples", "PrimaryExamplesSection"),
    ]
    for ex in page.basic_examples:
        basic_cells.extend(_render_example(ex))
    basic_group = _cellgroup(basic_cells)

    # Extended Examples
    ext_cells: list[str] = [
        cell_section_header("ExamplesSection", "ExtendedExamplesSection",
            more_info="Additional examples organized by section.")
    ]
    if page.scope:
        ext_cells.append(cell_example_section("Scope"))
        for sub in page.scope:
            ext_cells.append(cell_section_header(sub.title, "ExampleSubsection"))
            for ex in sub.examples:
                ext_cells.extend(_render_example(ex))
    if page.generalizations:
        ext_cells.append(cell_example_section("Generalizations"))
        for sub in page.generalizations:
            ext_cells.append(cell_section_header(sub.title, "ExampleSubsection"))
            for ex in sub.examples:
                ext_cells.extend(_render_example(ex))
    if page.applications:
        ext_cells.append(cell_example_section("Applications"))
        for sub in page.applications:
            ext_cells.append(cell_section_header(sub.title, "ExampleSubsection"))
            for ex in sub.examples:
                ext_cells.extend(_render_example(ex))
    if page.possible_issues:
        ext_cells.append(cell_example_section("Possible Issues"))
        for issue in page.possible_issues:
            ext_cells.extend(_render_issue(issue))
    if page.neat_examples:
        ext_cells.append(cell_example_section("Neat Examples"))
        for ex in page.neat_examples:
            ext_cells.extend(_render_example(ex))
    extended_group = _cellgroup(ext_cells)

    metadata_group = _metadata_group(page)

    cells = [
        top_group, seealso_group, technotes_group, moreabout_group,
        relatedlinks_group, init_group, basic_group, extended_group,
        metadata_group,
    ]
    return (
        "(* Content-type: application/vnd.wolfram.mathematica *)\n"
        "(* Wolfram Notebook File *)\n"
        "(* http://www.wolfram.com/nb *)\n"
        "(* CreatedBy='build_ref_pages.py' *)\n"
        "Notebook[{\n\n"
        + ",\n\n".join(cells)
        + "\n\n},\n"
        "WindowSize->{1107, 652},\n"
        "WindowMargins->{{4, Automatic}, {Automatic, 0}},\n"
        f'TaggingRules-><|"Paclet" -> "{PACLET_NAME}"|>,\n'
        'CellContext->"Global`",\n'
        'FrontEndVersion->"15.0 for Mac OS X ARM (64-bit) (February 17, 2026)",\n'
        f"{WL_STYLE},\n"
        f"ExpressionUUID->{nb_quote(uuid_str())}\n"
        "]\n"
    )


# ---------------------------------------------------------------------------
# Spec loader (kept in a sibling module so the per-symbol content is
# isolated from the rendering machinery).
# ---------------------------------------------------------------------------


def load_specs() -> list[RefPage]:
    # add the script's directory to sys.path so we can import ref_specs
    here = Path(__file__).parent
    if str(here) not in sys.path:
        sys.path.insert(0, str(here))
    import ref_specs  # noqa: WPS433
    return ref_specs.all_specs()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--symbol", action="append", default=None,
                   help="only build this symbol (repeatable)")
    args = p.parse_args()
    pages = load_specs()
    if args.symbol:
        wanted = set(args.symbol)
        pages = [pg for pg in pages if pg.symbol in wanted]
    if not pages:
        print("no pages to build", file=sys.stderr)
        return 1
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    for page in pages:
        print(f"\n=== {page.symbol} ===")
        verify_examples(page)
        out_path = DOCS_DIR / f"{page.symbol}.nb"
        out_path.write_text(build_notebook(page))
        print(f"wrote {out_path}")
        for ex in all_examples(page):
            if ex.messages:
                print(f"  ! messages from `{ex.input}`:")
                for m in ex.messages:
                    print(f"    - {m}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
