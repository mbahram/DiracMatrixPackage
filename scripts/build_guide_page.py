#!/usr/bin/env python3
"""
build_guide_page.py
===================

Generate Documentation/English/Guides/DiracMatrix.nb — the paclet's main
Guide page in the WFR (Wolfram Function Repository) style. Lists the ten
public symbols grouped into thematic subsections (gamma matrices, metric
utilities, basis transformations, Clifford operator basis, numerical
utilities) and links each to its ref/<Symbol> page.

Layout cribbed from:
  Wolfram/QuantumFramework/Documentation/English/Guides/
  WolframQuantumComputationFramework.nb

The Guide page is the MainPage referenced from PacletInfo.wl and is what
the front end shows when the user opens the paclet documentation.

House rules:
  * No kernel evaluation needed (Guide pages contain no Input cells).
  * Cell structure assembled with the same nb_quote helper used by
    build_ref_pages.py so quoting / named-character handling stays
    consistent across all paclet doc files.

Usage:
    python3 build_guide_page.py
"""

from __future__ import annotations

import random
import re
import sys
import uuid
from dataclasses import dataclass, field
from pathlib import Path

# Reuse the string-quoting helper from build_ref_pages so that Wolfram
# named-character escapes (\[Gamma], \[Mu], ...) survive into the .nb
# verbatim — the validator otherwise double-escapes the leading backslash.
sys.path.insert(0, str(Path(__file__).parent))
from build_ref_pages import nb_quote  # noqa: E402

PACLET_ROOT = Path(
    "/Users/mohammadb/Nextcloud/Mads/Quantum/DiracMatrix/DiracMatrixPackage"
)
GUIDES_DIR  = PACLET_ROOT / "Documentation" / "English" / "Guides"
PACLET_NAME = "DiracMatrix"
PACLET_CTX  = "DiracMatrix`"
GUIDE_NAME  = "DiracMatrix"

# Distinct seed from build_ref_pages so the two scripts can be run in
# sequence without colliding UUIDs / CellIDs.
_RNG = random.Random(0xD17AC6)


def uuid_str() -> str:
    return str(uuid.UUID(int=_RNG.getrandbits(128), version=4))


def cell_id() -> int:
    return _RNG.randint(10_000_000, 2_147_483_647)


# ---------------------------------------------------------------------------
# TeX placeholder handling
# ---------------------------------------------------------------------------
#
# Mathematica renders math correctly only when the boxes live inside
# Cell[BoxData[FormBox[..., TraditionalForm]], "InlineFormula"]. Plain
# strings such as "\[Gamma]^\[Mu]" show as a Greek letter, a literal caret,
# and another Greek letter — never as a typeset superscript.
#
# To stay consistent with build_ref_pages.py and ref_specs.py, prose with
# inline math uses %%TEX: <LaTeX> %% placeholders. The Wolfram nb-writer
# skill's validator (`validate_nb.py`) rewrites every "%%TEX: ... %%"
# string into a proper InlineFormula cell on write.
#
# The helper below splits prose at placeholder boundaries and emits a
# TextData[{seg, seg, ...}] list — necessary because the validator only
# matches "%%TEX: ... %%" when it is the entire quoted string, not a
# substring of a longer one.

_TEX_PLACEHOLDER_RE = re.compile(r"(%%TEX:.*?%%)")


def _textdata_with_placeholders(prose: str) -> str:
    """Render prose that may contain %%TEX:%% placeholders.

    No placeholders → return a plain quoted String (lighter notebook source).
    Has placeholders → return TextData[{seg, "%%TEX: ... %%", seg, ...}]
    with each placeholder isolated in its own string element so the
    validator can swap it for an InlineFormula cell.
    """
    parts = [p for p in _TEX_PLACEHOLDER_RE.split(prose) if p]
    has_placeholder = any(
        p.startswith("%%TEX:") and p.endswith("%%") for p in parts
    )
    if not has_placeholder:
        return nb_quote(prose)
    quoted: list[str] = []
    for p in parts:
        if p.startswith("%%TEX:") and p.endswith("%%"):
            # Preserve the placeholder verbatim — the validator pattern
            # matches the literal "%%TEX:...%%" inside a string literal.
            quoted.append('"' + p + '"')
        else:
            quoted.append(nb_quote(p))
    return "TextData[{\n  " + ",\n  ".join(quoted) + "\n}]"


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class GuideEntry:
    symbol: str
    description: str


@dataclass
class GuideSubsection:
    title: str
    entries: list[GuideEntry] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Content
# ---------------------------------------------------------------------------

GUIDE_TITLE = "DiracMatrix"

# Math is delivered via %%TEX: ... %% placeholders (LaTeX inside the
# %% markers). The nb-writer validator rewrites each placeholder into a
# real InlineFormula cell on write — see _textdata_with_placeholders.
GUIDE_ABSTRACT = (
    "The DiracMatrix paclet constructs Dirac gamma matrices "
    "%%TEX: \\gamma^\\mu %% that satisfy the Clifford anticommutation "
    "relation "
    "%%TEX: \\{\\gamma^\\mu, \\gamma^\\nu\\} = 2 \\eta^{\\mu \\nu} \\mathbb{I} %% "
    "for an arbitrary real symmetric metric %%TEX: \\eta %% in any "
    "dimension. The flat case uses the Brauer\\[Dash]Weyl "
    "(Pauli\\[Dash]Kronecker) construction; non-flat metrics are "
    "reached through a vielbein decomposition "
    "%%TEX: g = e^{\\mathsf{T}} \\cdot \\eta \\cdot e %%. The package "
    "also provides basis transformations into the Dirac and Weyl "
    "(chiral) representations, and two implementations of the canonical "
    "graded Clifford operator basis: an explicit antisymmetrisation sum "
    "(pedagogically transparent) and an antisymmetric recursion "
    "(numerically stable, production-ready)."
)

KEYWORDS = [
    "Dirac matrices",
    "gamma matrices",
    "Clifford algebra",
    "Brauer-Weyl",
    "Pauli-Kronecker",
    "vielbein",
    "tetrad",
    "spinor",
    "Dirac basis",
    "Weyl basis",
    "chiral basis",
    "Minkowski",
    "signature",
    "curved spacetime",
]

SUBSECTIONS: list[GuideSubsection] = [
    GuideSubsection(
        title="Gamma matrices",
        entries=[
            GuideEntry(
                "GammaMatrices",
                "n gamma matrices satisfying the Clifford relation for an "
                "arbitrary real symmetric metric in any dimension",
            ),
            GuideEntry(
                "EuclideanGammaMatrices",
                "flat Euclidean gamma matrices in the Brauer\\[Dash]Weyl "
                "(Pauli\\[Dash]Kronecker) representation",
            ),
        ],
    ),
    GuideSubsection(
        title="Metrics and vielbeins",
        entries=[
            GuideEntry(
                "FlatMetric",
                "diagonal flat metric of signature (p, q)",
            ),
            GuideEntry(
                "RandomCurvedMetric",
                "random real symmetric non-diagonal metric of given "
                "signature, with a controllable condition number",
            ),
            GuideEntry(
                "MetricVielbein",
                "vielbein decomposition "
                "%%TEX: e^{\\mathsf{T}} \\cdot \\eta \\cdot e %% of a "
                "real symmetric metric",
            ),
        ],
    ),
    GuideSubsection(
        title="Basis transformations",
        entries=[
            GuideEntry(
                "ToDiracBasis",
                "transform gamma matrices from the Brauer\\[Dash]Weyl "
                "basis to the Dirac basis "
                "(%%TEX: \\gamma^0 %% diagonal)",
            ),
            GuideEntry(
                "ToWeylBasis",
                "transform gamma matrices from the Brauer\\[Dash]Weyl "
                "basis to the Weyl (chiral) basis",
            ),
        ],
    ),
    GuideSubsection(
        title="Canonical Clifford operator basis",
        entries=[
            GuideEntry(
                "CliffordBasis",
                "graded Clifford operator basis built via an "
                "antisymmetric recursion \\[Dash] numerically stable, "
                "production-ready",
            ),
            GuideEntry(
                "CliffordCanonicalBasis",
                "graded Clifford operator basis built via the explicit "
                "antisymmetrisation sum \\[Dash] pedagogically transparent "
                "but combinatorially expensive",
            ),
        ],
    ),
    GuideSubsection(
        title="Numerical utilities",
        entries=[
            GuideEntry(
                "NumericZeroQ",
                "test whether every entry of an array is numerically zero, "
                "with a user-supplied tolerance",
            ),
        ],
    ),
]


# ---------------------------------------------------------------------------
# Cell builders
# ---------------------------------------------------------------------------


def cell_history() -> str:
    return (
        'Cell[TextData[{\n'
        ' "New in: ",\n'
        f' Cell["1.0.0", "HistoryData",\n'
        f'  CellTags->"New", ExpressionUUID->{nb_quote(uuid_str())}],\n'
        ' " | Modified in: ",\n'
        f' Cell[" ", "HistoryData",\n'
        f'  CellTags->"Modified", ExpressionUUID->{nb_quote(uuid_str())}],\n'
        ' " | Obsolete in: ",\n'
        f' Cell[" ", "HistoryData",\n'
        f'  CellTags->"Obsolete", ExpressionUUID->{nb_quote(uuid_str())}],\n'
        ' " | Excised in: ",\n'
        f' Cell[" ", "HistoryData",\n'
        f'  CellTags->"Excised", ExpressionUUID->{nb_quote(uuid_str())}]\n'
        '}], "History",\n'
        f' CellID->{cell_id()}, ExpressionUUID->{nb_quote(uuid_str())}]'
    )


def cell_categorization(label: str, value: str) -> str:
    return (
        f'Cell[{nb_quote(value)}, "Categorization",\n'
        f' CellLabel->{nb_quote(label)},\n'
        f' CellID->{cell_id()}, ExpressionUUID->{nb_quote(uuid_str())}]'
    )


def keywords_group() -> str:
    cells = [
        f'Cell["Keywords", "KeywordsSection",\n'
        f' CellID->{cell_id()}, ExpressionUUID->{nb_quote(uuid_str())}]'
    ]
    for kw in KEYWORDS:
        cells.append(
            f'Cell[{nb_quote(kw)}, "Keywords",\n'
            f' CellID->{cell_id()}, ExpressionUUID->{nb_quote(uuid_str())}]'
        )
    return _cellgroup(cells)


def title_abstract_group() -> str:
    title_cell = (
        f'Cell[{nb_quote(GUIDE_TITLE)}, "GuideTitle",\n'
        f' CellID->{cell_id()}, ExpressionUUID->{nb_quote(uuid_str())}]'
    )
    abstract_cell = (
        f'Cell[{_textdata_with_placeholders(GUIDE_ABSTRACT)}, "GuideAbstract",\n'
        f' CellID->{cell_id()}, ExpressionUUID->{nb_quote(uuid_str())}]'
    )
    return _cellgroup([title_cell, abstract_cell])


def guidetext_cell(entry: GuideEntry) -> str:
    r"""Render one symbol entry in the Guide:
       Symbol [InlineGuideFunction button] \[LongDash] description

    Descriptions may contain %%TEX: ... %% placeholders; those are split
    into separate string elements (validator replaces each with an
    InlineFormula cell).
    """
    button_cell = (
        f'Cell[BoxData[ButtonBox[{nb_quote(entry.symbol)},\n'
        f'  BaseStyle->"Link",\n'
        f'  ButtonData->{nb_quote("paclet:" + PACLET_NAME + "/ref/" + entry.symbol)}]],\n'
        f' "InlineGuideFunction", ExpressionUUID->{nb_quote(uuid_str())}]'
    )
    # Split the prose-with-math at %%TEX:%% boundaries; one element per
    # segment so the validator's placeholder regex matches.
    desc = " \\[LongDash] " + entry.description
    desc_parts = [p for p in _TEX_PLACEHOLDER_RE.split(desc) if p]
    desc_elements: list[str] = []
    for p in desc_parts:
        if p.startswith("%%TEX:") and p.endswith("%%"):
            desc_elements.append('"' + p + '"')
        else:
            desc_elements.append(nb_quote(p))
    inner = ",\n ".join([button_cell] + desc_elements)
    return (
        'Cell[TextData[{\n'
        f' {inner}\n'
        '}], "GuideText",\n'
        f' CellID->{cell_id()}, ExpressionUUID->{nb_quote(uuid_str())}]'
    )


def subsection_group(sub: GuideSubsection) -> str:
    cells = [
        f'Cell[{nb_quote(sub.title)}, "GuideFunctionsSubsection",\n'
        f' CellID->{cell_id()}, ExpressionUUID->{nb_quote(uuid_str())}]'
    ]
    for entry in sub.entries:
        cells.append(guidetext_cell(entry))
    return _cellgroup(cells)


def functions_group() -> str:
    cells = [
        f'Cell["", "GuideFunctionsSection",\n'
        f' CellID->{cell_id()}, ExpressionUUID->{nb_quote(uuid_str())}]'
    ]
    for sub in SUBSECTIONS:
        cells.append(subsection_group(sub))
    return _cellgroup(cells)


def tutorials_group() -> str:
    """Tech Notes section. The paclet doesn't yet ship tutorials, so we
    emit the standard placeholder cell that WFR Guides use when empty.
    """
    cells = [
        f'Cell["Tech Notes", "GuideTutorialsSection",\n'
        f' CellID->{cell_id()}, ExpressionUUID->{nb_quote(uuid_str())}]',
        f'Cell[" ", "GuideTutorial",\n'
        f' CellID->{cell_id()}, ExpressionUUID->{nb_quote(uuid_str())}]',
    ]
    return _cellgroup(cells)


def more_about_group() -> str:
    cells = [
        f'Cell["More About", "GuideMoreAboutSection",\n'
        f' CellID->{cell_id()}, ExpressionUUID->{nb_quote(uuid_str())}]',
        f'Cell[" ", "GuideMoreAbout",\n'
        f' CellID->{cell_id()}, ExpressionUUID->{nb_quote(uuid_str())}]',
    ]
    return _cellgroup(cells)


def related_links_cell() -> str:
    return (
        f'Cell["Related Links", "GuideRelatedLinksSection",\n'
        f' CellID->{cell_id()}, ExpressionUUID->{nb_quote(uuid_str())}]'
    )


# ---------------------------------------------------------------------------
# Notebook assembly
# ---------------------------------------------------------------------------


def _cellgroup(cells: list[str], open_state: str = "Open") -> str:
    inner = ",\n".join(cells)
    return f"Cell[CellGroupData[{{\n{inner}\n}}, {open_state}]]"


GUIDE_STYLE = (
    'StyleDefinitions->FrontEnd`FileName[{"Wolfram"}, '
    '"GuidePageStylesExt.nb", CharacterEncoding -> "UTF-8"]'
)


def build_notebook() -> str:
    # Top-level cells (not wrapped in CellGroupData) mirror QuantumFramework:
    # History + 4 Categorization cells appear at the top level.
    top_cells = [
        cell_history(),
        cell_categorization("Entity Type", "Guide"),
        cell_categorization("Paclet Name", PACLET_NAME),
        cell_categorization("Context", PACLET_CTX),
        cell_categorization("URI", PACLET_NAME + "/guide/" + GUIDE_NAME),
    ]
    groups = [
        keywords_group(),
        title_abstract_group(),
        functions_group(),
        tutorials_group(),
        more_about_group(),
        related_links_cell(),
    ]
    body = ",\n\n".join(top_cells + groups)
    return (
        "(* Content-type: application/vnd.wolfram.mathematica *)\n"
        "(* Wolfram Notebook File *)\n"
        "(* http://www.wolfram.com/nb *)\n"
        "(* CreatedBy='build_guide_page.py' *)\n"
        "Notebook[{\n\n"
        + body
        + "\n\n},\n"
        "WindowSize->{900, 700},\n"
        "WindowMargins->{{Automatic, 0}, {Automatic, 0}},\n"
        f'TaggingRules-><|"Paclet" -> "{PACLET_NAME}"|>,\n'
        "CellContext->\"Global`\",\n"
        'FrontEndVersion->"15.0 for Mac OS X ARM (64-bit) (February 17, 2026)",\n'
        f"{GUIDE_STYLE},\n"
        f"ExpressionUUID->{nb_quote(uuid_str())}\n"
        "]\n"
    )


def main() -> int:
    GUIDES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = GUIDES_DIR / f"{GUIDE_NAME}.nb"
    out_path.write_text(build_notebook())
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
