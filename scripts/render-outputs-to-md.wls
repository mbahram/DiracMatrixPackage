#!/usr/bin/env wolframscript
(* ::Package:: *)

(* render-outputs-to-md.wls
   Rasterize every Output / Print / Echo / Message cell of the DiracMatrix
   documentation notebook, then insert each PNG into the corresponding
   ```wolfram fence of the hand-curated markdown file. Idempotent. *)

pkgDir = DirectoryName[DirectoryName[$InputFileName]];
nbPath = FileNameJoin[{pkgDir, "DiracMatrix-Documentation.nb"}];
mdPath = FileNameJoin[{pkgDir, "DiracMatrix-Documentation.md"}];
imgDir = FileNameJoin[{pkgDir, "images"}];
imgRel = "images";

If[! DirectoryQ[imgDir], CreateDirectory[imgDir, CreateIntermediateDirectories -> True]];

(* ── Helpers ─────────────────────────────────────────── *)

normalize[s_String] := StringDelete[
  StringReplace[s, "(*" ~~ Shortest[___] ~~ "*)" -> ""],
  Whitespace
];

cellText[cell_Cell] := normalize @ StringJoin[Cases[cell[[1]], _String, {0, Infinity}]];

flattenCells[Notebook[c_, ___]]                  := Flatten[flattenCells /@ c];
flattenCells[Cell[CellGroupData[c_, ___], ___]]  := Flatten[flattenCells /@ c];
flattenCells[CellGroupData[c_, ___]]             := Flatten[flattenCells /@ c];
flattenCells[c_Cell]                             := {c};
flattenCells[l_List]                             := Flatten[flattenCells /@ l];
flattenCells[___]                                := {};

(* ── Phase A: load notebook, group cells, rasterize outputs ───────── *)

Print["Loading ", nbPath];
nb = Get[nbPath];
cells = flattenCells[nb];
Print["Total cells: ", Length[cells]];

groups = Fold[
  Function[{acc, c},
    Switch[c[[2]],
      "Input" | "Code",
        Append[acc, {c, {}}],
      "Output" | "Print" | "Echo" | "Message",
        If[acc === {}, acc, MapAt[Append[#, c] &, acc, {-1, 2}]],
      _, acc
    ]
  ],
  {},
  cells
];

inputCount  = Length[groups];
outputCount = Total[Length[#[[2]]] & /@ groups];
Print["Input/Code cells: ", inputCount, ", Output cells: ", outputCount];

(* Rasterize each output and build records: {{normalizedInputText, {imgPath, ...}}, ...} *)
records = MapIndexed[
  Function[{group, idx},
    Module[{i = idx[[1]], inputCell = group[[1]], outs = group[[2]]},
      {
        cellText[inputCell],
        MapIndexed[
          Function[{out, jdx},
            Module[{j = jdx[[1]], name, fullPath, img},
              name = "out_" <> IntegerString[i, 10, 3] <> "_" <> ToString[j] <> ".png";
              fullPath = FileNameJoin[{imgDir, name}];
              img = Quiet @ UsingFrontEnd[
                Rasterize[out, "Image",
                  ImageResolution -> 144,
                  Background -> White
                ]
              ];
              If[ImageQ[img],
                Export[fullPath, img];
                imgRel <> "/" <> name
              ,
                Print["  ! Rasterize failed for output ", i, "_", j, ": ", Short[out, 60]];
                Missing["RasterizeFailed"]
              ]
            ]
          ],
          outs
        ]
      }
    ]
  ],
  groups
];

(* Drop failed renders from records *)
records = MapAt[DeleteCases[#, _Missing] &, records, {All, 2}];

successCount = Total[Length[#[[2]]] & /@ records];
Print["Wrote ", successCount, " PNGs to ", imgDir];

(* Build association: normalized input text -> list of image paths *)
recordsWithOutputs = Select[records, #[[2]] =!= {} &];
assoc = AssociationThread[
  recordsWithOutputs[[All, 1]],
  recordsWithOutputs[[All, 2]]
];
Print["Inputs that produced output: ", Length[assoc]];

(* ── Phase B: augment the .md ─────────────────────────────────────── *)

md = Import[mdPath, "Text"];

(* Idempotence: strip prior insertions of the form ![](images/out_NNN_M.png) on its own line *)
md = StringReplace[md,
  ("\n![](" ~~ imgRel ~~ "/out_" ~~ DigitCharacter .. ~~ "_" ~~ DigitCharacter .. ~~ ".png)") -> ""
];

(* Walk fences and insert image refs after each match *)
{augmented, sown} = Reap[
  StringReplace[md,
    ("```wolfram\n" ~~ code : Shortest[___] ~~ "\n```") :>
      Module[{normCode = normalize[code], refs},
        refs = Lookup[assoc, normCode, {}];
        Sow[refs];
        If[refs === {},
          "```wolfram\n" <> code <> "\n```",
          "```wolfram\n" <> code <> "\n```\n" <>
            StringRiffle["![](" <> # <> ")" & /@ refs, "\n"]
        ]
      ]
  ]
];

matchedRefs = Flatten[sown];
Print["Inserted ", Length[matchedRefs], " image refs into .md"];

Export[mdPath, augmented, "Text"];
Print["Wrote ", mdPath];

(* Orphan check *)
allRefs = Flatten[records[[All, 2]]];
orphans = Complement[allRefs, matchedRefs];
If[orphans === {},
  Print["No orphan PNGs (every PNG is referenced in the .md)."]
,
  Print["Orphan PNGs (output exists in .nb but no matching fence in .md): ", Length[orphans]];
  Print["First 5 orphans: ", Take[orphans, UpTo[5]]]
];

Print["Done."]
