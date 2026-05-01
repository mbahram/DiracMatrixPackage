#!/usr/bin/env wolframscript
(* ::Package:: *)

(* render-hero-images.wls
   Generate three candidate hero images for the DiracMatrix package, using
   only low-level Graphics primitives so layout is identical with or without
   a notebook front end.
     (1) Clifford basis pyramid for Cl(1,3)  -> hero-clifford-pyramid.png
     (2) Brauer-Weyl gamma stack in dim 8    -> hero-brauer-weyl-d8.png
     (3) Schwarzschild metric -> gamma       -> hero-metric-to-gamma.png
*)

pkgDir = "/Users/mohammadb/Nextcloud/Mads/Quantum/DiracMatrix/DiracMatrixPackage";
imgDir = FileNameJoin[{pkgDir, "assets"}];

PacletDirectoryLoad[pkgDir];
Needs["DiracMatrix`"];

(* --- Color: real positive -> warm red, real negative -> cool blue,
        imaginary positive -> green, imaginary negative -> amber, else purple.
        Magnitude scales from white. --- *)

signColor[z_] := Module[{a = Min[N @ Abs[z], 1.]},
  Which[
    Chop[z, 10^-10] === 0,                              White,
    Abs[Im[z]] < 10^-10 && Re[z] > 0,                   Blend[{White, RGBColor[0.78, 0.18, 0.18]}, a],
    Abs[Im[z]] < 10^-10 && Re[z] < 0,                   Blend[{White, RGBColor[0.18, 0.38, 0.80]}, a],
    Abs[Re[z]] < 10^-10 && Im[z] > 0,                   Blend[{White, RGBColor[0.20, 0.62, 0.36]}, a],
    Abs[Re[z]] < 10^-10 && Im[z] < 0,                   Blend[{White, RGBColor[0.85, 0.55, 0.10]}, a],
    True,                                               Blend[{White, RGBColor[0.55, 0.25, 0.55]}, a]
  ]];

(* --- Render an N x N matrix as a square of N^2 colored Rectangles
       at `origin`, occupying `outerSize` x `outerSize` in plot coords. --- *)

matGraphic[m_, origin_, outerSize_] := Module[{n = Length[m], cs, cells},
  cs = outerSize / n;
  cells = Flatten @ Table[
    {EdgeForm[Directive[GrayLevel[0.90], AbsoluteThickness[0.35]]],
     FaceForm @ signColor[m[[i, j]]],
     Rectangle[
       origin + {(j - 1) * cs, (n - i) * cs},
       origin + {j     * cs, (n - i + 1) * cs}]},
    {i, n}, {j, n}];
  {cells,
   EdgeForm[Directive[GrayLevel[0.55], AbsoluteThickness[1.1]]],
   FaceForm[None],
   Rectangle[origin, origin + {outerSize, outerSize}]}
];

(* ===================================================================== *)
(* Hero 1: Cl(1,3) Clifford-basis pyramid                                 *)
(* ===================================================================== *)

basis13 = CliffordBasis[FlatMetric[1, 3]];
Print["Cl(1,3) row sizes: ", Length /@ basis13];

cs1  = 1.0;  hs1 = 0.18;  vs1 = 0.45;  pad1 = 0.4;
n1   = Length[basis13];
ws1  = Length /@ basis13;
wMax1 = Max[ws1];
contentW1 = wMax1 * cs1 + (wMax1 - 1) * hs1;
totalW1 = contentW1 + 2 * pad1;
totalH1 = n1 * cs1 + (n1 - 1) * vs1 + 2 * pad1;

items1 = Flatten[
  Table[
    Module[{row = basis13[[r]], k = ws1[[r]], rowW, x0, y0},
      rowW = k * cs1 + (k - 1) * hs1;
      x0   = pad1 + (contentW1 - rowW) / 2;
      y0   = totalH1 - pad1 - r * cs1 - (r - 1) * vs1;
      Table[
        matGraphic[row[[i]], {x0 + (i - 1) * (cs1 + hs1), y0}, cs1],
        {i, k}]
    ],
    {r, n1}], 1];

hero1 = Graphics[items1,
  PlotRange -> {{0, totalW1}, {0, totalH1}},
  AspectRatio -> totalH1 / totalW1,
  ImageSize -> 2000,
  Background -> White,
  PlotRangePadding -> 0];

Export[FileNameJoin[{imgDir, "hero-clifford-pyramid.png"}], hero1, "PNG"];
Print["[1/3] wrote hero-clifford-pyramid.png"];

(* ===================================================================== *)
(* Hero 2: Brauer-Weyl gamma stack in dim 8 (4 x 2 layout)                *)
(* ===================================================================== *)

g8 = GammaMatrices[8];
Print["dim-8 gammas: ", Length[g8], " of ", Dimensions[First @ g8]];

cs2 = 1.0; hs2 = 0.16; vs2 = 0.16; pad2 = 0.4;
totalW2 = 4 * cs2 + 3 * hs2 + 2 * pad2;
totalH2 = 2 * cs2 + 1 * vs2 + 2 * pad2;

items2 = Flatten @ Table[
  matGraphic[
    g8[[(r - 1) * 4 + c]],
    {pad2 + (c - 1) * (cs2 + hs2),
     totalH2 - pad2 - r * cs2 - (r - 1) * vs2},
    cs2],
  {r, 2}, {c, 4}];

hero2 = Graphics[items2,
  PlotRange -> {{0, totalW2}, {0, totalH2}},
  AspectRatio -> totalH2 / totalW2,
  ImageSize -> 2400,
  Background -> White,
  PlotRangePadding -> 0];

Export[FileNameJoin[{imgDir, "hero-brauer-weyl-d8.png"}], hero2, "PNG"];
Print["[2/3] wrote hero-brauer-weyl-d8.png"];

(* ===================================================================== *)
(* Hero 3: Schwarzschild metric -> gamma diptych                          *)
(* ===================================================================== *)

\[Eta]Sch = N @ DiagonalMatrix[{-1/3, 3, 9, 9}];
gSch      = GammaMatrices[\[Eta]Sch];
maxG = Max[Abs @ Flatten @ gSch];
maxE = Max[Abs @ Flatten @ \[Eta]Sch];
Print["Schwarzschild max|gamma|=", maxG, ", max|eta|=", maxE];
gSchN  = gSch / maxG;
\[Eta]SchN = \[Eta]Sch / maxE;

metricSize = 1.6;
gSize      = 0.72;
gSep       = 0.06;
gridW      = 2 * gSize + gSep;
arrowW     = 0.55;
gap        = 0.32;
pad3       = 0.40;

xMet = pad3;
xArr = xMet + metricSize + gap;
xGri = xArr + arrowW + gap;
totalW3 = xGri + gridW + pad3;
totalH3 = Max[metricSize, gridW] + 2 * pad3;

yMet = (totalH3 - metricSize) / 2;
yGri = (totalH3 - gridW)      / 2;
yArr = totalH3 / 2;

items3 = Flatten[{
  matGraphic[\[Eta]SchN, {xMet, yMet}, metricSize],
  Table[
    matGraphic[
      gSchN[[(r - 1) * 2 + c]],
      {xGri + (c - 1) * (gSize + gSep),
       yGri + gridW - r * gSize - (r - 1) * gSep},
      gSize],
    {r, 2}, {c, 2}],
  {GrayLevel[0.42], AbsoluteThickness[4.0],
   Arrowheads[{{0.045, 1}}],
   Arrow[{{xArr, yArr}, {xArr + arrowW, yArr}}]}
}, 1];

hero3 = Graphics[items3,
  PlotRange -> {{0, totalW3}, {0, totalH3}},
  AspectRatio -> totalH3 / totalW3,
  ImageSize -> 2400,
  Background -> White,
  PlotRangePadding -> 0];

Export[FileNameJoin[{imgDir, "hero-metric-to-gamma.png"}], hero3, "PNG"];
Print["[3/3] wrote hero-metric-to-gamma.png"];

Print["Done."];
