(* ::Package:: *)

(* :Title: DiracMatrix *)
(* :Author: Mads Bahrami *)
(* :Summary:
    Construction of Dirac gamma matrices satisfying the Clifford relation
    {\[Gamma]^\[Mu], \[Gamma]^\[Nu]} = 2 \[Eta]^{\[Mu]\[Nu]} \[DoubleStruckCapitalI]
    for an arbitrary real symmetric metric \[Eta] in any dimension n,
    using the Brauer\[Dash]Weyl (Pauli\[Dash]Kronecker) construction
    composed with a vielbein decomposition.
*)
(* :Context: DiracMatrix` *)
(* :Package Version: 1.0.0 *)
(* :Mathematica Version: 13.0+ *)
(* :Keywords: Dirac, gamma matrices, Clifford algebra, vielbein, spinor *)

BeginPackage["DiracMatrix`"];

(* ----- Public symbols ----- *)

GammaMatrices::usage =
  "GammaMatrices[n] returns n Euclidean gamma matrices of dimension 2^Floor[n/2] in the Brauer\[Dash]Weyl (Pauli\[Dash]Kronecker) representation.\n" <>
  "GammaMatrices[\[Eta]] returns gamma matrices satisfying the Clifford relation {\!\(\*SuperscriptBox[\(\[Gamma]\), \(\[Mu]\)]\),\!\(\*SuperscriptBox[\(\[Gamma]\), \(\[Nu]\)]\)} = 2\!\(\*SuperscriptBox[\(\[Eta]\), \(\[Mu]\[Nu]\)]\) \[DoubleStruckCapitalI] for any real symmetric metric \[Eta]. \
For a flat diagonal metric of signature (p,q) the result is \[ImaginaryI] \!\(\*SuperscriptBox[\(\[CapitalGamma]\), \(\[Mu]\)]\) for time-like indices and \!\(\*SuperscriptBox[\(\[CapitalGamma]\), \(\[Mu]\)]\) for space-like indices; for a general metric a vielbein decomposition is used.";

EuclideanGammaMatrices::usage =
  "EuclideanGammaMatrices[n] returns the n Euclidean gamma matrices in the Brauer\[Dash]Weyl representation: \!\(\*SuperscriptBox[\(\[CapitalGamma]\), \"2 k - 1\"]\) = \!\(\*SuperscriptBox[\(\[DoubleStruckCapitalI]\), \"\[CircleTimes] (k - 1)\"]\) \[CircleTimes] \!\(\*SubscriptBox[\(\[Sigma]\), \(1\)]\) \[CircleTimes] \!\(\*SuperscriptBox[\(\*SubscriptBox[\(\[Sigma]\), \(3\)]\), \"\[CircleTimes] (m - k)\"]\), \!\(\*SuperscriptBox[\(\[CapitalGamma]\), \"2 k\"]\) = \!\(\*SuperscriptBox[\(\[DoubleStruckCapitalI]\), \"\[CircleTimes] (k - 1)\"]\) \[CircleTimes] \!\(\*SubscriptBox[\(\[Sigma]\), \(2\)]\) \[CircleTimes] \!\(\*SuperscriptBox[\(\*SubscriptBox[\(\[Sigma]\), \(3\)]\), \"\[CircleTimes] (m - k)\"]\), and for odd n a final \!\(\*SuperscriptBox[\(\[CapitalGamma]\), \"2 m + 1\"]\) = \!\(\*SuperscriptBox[\(\*SubscriptBox[\(\[Sigma]\), \(3\)]\), \"\[CircleTimes] m\"]\).";

FlatMetric::usage =
  "FlatMetric[p, q] returns the diagonal flat metric DiagonalMatrix[Join[ConstantArray[1,p], ConstantArray[-1,q]]] of signature (p,q).";

RandomCurvedMetric::usage =
  "RandomCurvedMetric[p, q] (or RandomCurvedMetric[p, q, a, s]) returns a random real symmetric non-diagonal metric of signature (p,q) constructed as \!\(\*SuperscriptBox[\(Q\), \(T\)]\) . \[CapitalLambda] . Q with Q \[Element] O(n) a random orthogonal matrix and \[CapitalLambda] a diagonal matrix whose first p eigenvalues are \!\(\*SuperscriptBox[\(s\), \(2\)]\) \!\(\*SuperscriptBox[\(10\), \(r\)]\) and last q eigenvalues are -\!\(\*SuperscriptBox[\(s\), \(2\)]\) \!\(\*SuperscriptBox[\(10\), \(r\)]\) for independent r drawn uniformly from [-a, a]. The default a = 2 gives a condition number \[Kappa] ~ \!\(\*SuperscriptBox[\(10\), \"2 a\"]\); s = 1 sets the typical magnitude of the metric components.";

MetricVielbein::usage =
  "MetricVielbein[\[Eta]] returns {signature, vielbein} for the real symmetric metric \[Eta], where signature = DiagonalMatrix[Sign[eigenvalues]] and the vielbein e satisfies \!\(\*SuperscriptBox[\(e\), \(T\)]\) . signature . e = \[Eta].";

ToDiracBasis::usage =
  "ToDiracBasis[\[Gamma]] takes a list of gamma matrices in the Brauer\[Dash]Weyl basis and returns them in the Dirac basis (where \!\(\*SuperscriptBox[\(\[Gamma]\), \(0\)]\) is diagonal).";

ToWeylBasis::usage =
  "ToWeylBasis[\[Gamma]] takes a list of gamma matrices in the Brauer\[Dash]Weyl basis and returns them in the Weyl/chiral basis. For odd dimension there is no chiral decomposition; the Dirac basis is returned with a message.";

NumericZeroQ::usage =
  "NumericZeroQ[a] returns True if every entry of a (after Chop with tolerance \!\(\*SuperscriptBox[\(10\), \"-8\"]\)) is zero.\n" <>
  "NumericZeroQ[a, tol] uses the supplied tolerance.";

CliffordCanonicalBasis::usage =
  "CliffordCanonicalBasis[\[Eta]] returns the canonical graded operator basis of the Clifford algebra Cl(\[Eta]) as a list grouped by grade {grade-0, grade-1, \[Ellipsis], grade-n}. The grade-k element on indices \!\(\*SubscriptBox[\(i\), \(1\)]\), \[Ellipsis], \!\(\*SubscriptBox[\(i\), \(k\)]\) is the explicitly antisymmetrised product \!\(\*FractionBox[\(1\), \(k!\)]\) \!\(\*UnderscriptBox[\(\[Sum]\), \"\[Sigma] \[Element] S_k\"]\) sgn(\[Sigma]) \!\(\*SubscriptBox[\(\[CapitalGamma]\), \"i_(\[Sigma](1))\"]\) \[CenterDot] \[CenterDot] \[CenterDot] \!\(\*SubscriptBox[\(\[CapitalGamma]\), \"i_(\[Sigma](k))\"]\). Pedagogically transparent but combinatorially expensive; for non-flat metrics with widely scaled eigenvalues precision can degrade at high grades. Prefer CliffordBasis for production use.";

CliffordBasis::usage =
  "CliffordBasis[\[Eta]] returns the canonical graded Clifford operator basis using the antisymmetrised recursion \!\(\*SubscriptBox[\(\[CapitalGamma]\), \"\[ScriptCapitalI] \[Union] {\[Mu]}\"]\) = \!\(\*SubscriptBox[\(\[CapitalGamma]\), \(\[ScriptCapitalI]\)]\) \[CenterDot] \!\(\*SubscriptBox[\(\[CapitalGamma]\), \(\[Mu]\)]\) - \!\(\*SubsuperscriptBox[\(\[Sum]\), \"j = 1\", \"|\[ScriptCapitalI]|\"]\) \!\(\*SuperscriptBox[\((\(-1\))\), \"j - 1\"]\) \!\(\*SubscriptBox[\(\[Eta]\), \"\[Mu], i_j\"]\) \!\(\*SubscriptBox[\(\[CapitalGamma]\), \"\[ScriptCapitalI] \[Backslash] {i_j}\"]\). Much faster than CliffordCanonicalBasis and numerically stable; agrees with it on flat metrics at all grades.";

(* ----- Messages ----- *)

ToWeylBasis::oddDim =
  "For odd dimension there is no Weyl/chiral basis. The result is returned in the Dirac basis.";

GammaMatrices::nonsym =
  "The metric `1` is not symmetric within tolerance 10^-12.";


Begin["`Private`"];

(* ===================================================================== *)
(* Metrics                                                                *)
(* ===================================================================== *)

FlatMetric[p_Integer?NonNegative, q_Integer?NonNegative] :=
  DiagonalMatrix[Join[ConstantArray[1, p], ConstantArray[-1, q]]];

RandomCurvedMetric[p_Integer?NonNegative, q_Integer?NonNegative,
              a : _?NumericQ : 2, s : _?NumericQ : 1] :=
  Module[{n, Q, \[CapitalLambda]},
    n = p + q;
    Q = RandomVariate @ CircularRealMatrixDistribution[n];
    \[CapitalLambda] = DiagonalMatrix[
      s^2 Join[
        10^RandomReal[{-a, a}, p],
       -10^RandomReal[{-a, a}, q]]];
    Transpose[Q] . \[CapitalLambda] . Q];

MetricVielbein[\[Eta]_ /; SymmetricMatrixQ[\[Eta], Tolerance -> 10^-12]] :=
  Module[{vals, vecs, signature, scale, vielbein},
    {vals, vecs} = Eigensystem[\[Eta]];
    signature = DiagonalMatrix[Sign[vals]];
    scale     = DiagonalMatrix[Sqrt[Abs[vals]]];
    vielbein  = scale . vecs;
    {signature, vielbein}];

(* ===================================================================== *)
(* Brauer-Weyl construction in Euclidean space                            *)
(* ===================================================================== *)

EuclideanGammaMatrices[1] := {PauliMatrix[3]};
EuclideanGammaMatrices[2] := {PauliMatrix[1], PauliMatrix[2]};
EuclideanGammaMatrices[3] := Append[EuclideanGammaMatrices[2], PauliMatrix[3]];

EuclideanGammaMatrices[n_Integer] /; n >= 4 :=
  Module[{m = Floor[n/2], \[CapitalGamma]},
    \[CapitalGamma] = Join @@ Table[
      {KroneckerProduct @@ Join[
          ConstantArray[IdentityMatrix[2], k - 1],
          {PauliMatrix[1]},
          ConstantArray[PauliMatrix[3], m - k]],
       KroneckerProduct @@ Join[
          ConstantArray[IdentityMatrix[2], k - 1],
          {PauliMatrix[2]},
          ConstantArray[PauliMatrix[3], m - k]]},
      {k, m}];
    If[EvenQ[n],
      \[CapitalGamma],
      Append[\[CapitalGamma], KroneckerProduct @@ ConstantArray[PauliMatrix[3], m]]]];

(* ===================================================================== *)
(* GammaMatrices: integer / signed-diagonal / general symmetric metric    *)
(* ===================================================================== *)

GammaMatrices[n_Integer?Positive] := EuclideanGammaMatrices[n];

GammaMatrices[\[Eta]_?DiagonalMatrixQ] /;
    ContainsOnly[Diagonal[\[Eta]], {-1, 1}] :=
  Diagonal[\[Eta] /. {-1 :> I}] *
    EuclideanGammaMatrices[Length @ \[Eta]];

GammaMatrices[\[Eta]_ /; SymmetricMatrixQ[\[Eta], Tolerance -> 10^-12]] :=
  Module[{signature, vielbein, \[CapitalGamma]flat},
    {signature, vielbein} = MetricVielbein[\[Eta]];
    \[CapitalGamma]flat = GammaMatrices[signature];
    TensorContract[TensorProduct[vielbein, \[CapitalGamma]flat], {{1, 3}}]];

(* ===================================================================== *)
(* Basis transformations                                                  *)
(* ===================================================================== *)

ToDiracBasis[\[Gamma]_List] :=
  Module[{\[Gamma]0, vals, vecs, order, S},
    \[Gamma]0 = First[\[Gamma]];
    {vals, vecs} = Chop @ Eigensystem[\[Gamma]0];
    (* Order so that +i eigenvalues come first, then -i (mostly-plus convention). *)
    order = Ordering[vals, All, Im[#1] > Im[#2] &];
    S = Transpose[vecs[[order]]];
    Inverse[S] . # . S & /@ \[Gamma]];

ToWeylBasis[\[Gamma]_List] :=
  Module[{\[Gamma]D, dim, half, T},
    \[Gamma]D = ToDiracBasis[\[Gamma]];
    dim = Length[\[Gamma]];
    If[OddQ[dim],
      Message[ToWeylBasis::oddDim];
      Return[\[Gamma]D]];
    half = dim/2;
    T = KroneckerProduct[{{1, 1}, {1, -1}}, IdentityMatrix[half]] / Sqrt[2];
    T . # . Inverse[T] & /@ \[Gamma]D];

(* ===================================================================== *)
(* Numerical helper                                                       *)
(* ===================================================================== *)

NumericZeroQ[a_, tol : _?NumericQ : 10^-8] :=
  Norm[Chop[Flatten[a], tol], "Frobenius"] == 0;

(* ===================================================================== *)
(* Clifford operator bases                                                *)
(* ===================================================================== *)

CliffordCanonicalBasis[\[Eta]_ /; SymmetricMatrixQ[\[Eta], Tolerance -> 10^-12]] :=
  Module[{n, \[Gamma], id},
    n  = Length[\[Eta]];
    \[Gamma]  = GammaMatrices[\[Eta]];
    id = IdentityMatrix[2^Floor[n/2]];
    Table[
      If[k == 0,
        {id},
        With[{subs = Subsets[\[Gamma], {k}]},
          (Total[Signature /@ Permutations[Range[k]] *
                 (Dot @@@ Permutations[#])] / k!) & /@ subs]],
      {k, 0, n}]];

(* Recursion step: append index \[Mu] to the antisymmetrised basis element on
   index list \[ScriptCapitalI], using the algebraic relation that re-uses
   already-computed lower-grade elements. *)
gammaAppendAntisym[\[Eta]_, \[Gamma]_, \[CapitalGamma]_, is_, \[Mu]_] :=
  Module[{k = Length[is]},
    Dot[\[CapitalGamma][is], \[Gamma][[\[Mu]]]] -
    Sum[(-1)^(j - 1) \[Eta][[\[Mu], is[[j]]]] \[CapitalGamma][Delete[is, j]],
        {j, k}]];

CliffordBasis[\[Eta]_ /; SymmetricMatrixQ[\[Eta], Tolerance -> 10^-12]] :=
  Module[{n, \[Gamma], d, \[CapitalGamma]},
    n = Length[\[Eta]];
    \[Gamma] = GammaMatrices[\[Eta]];
    d = Length[\[Gamma][[1]]];
    \[CapitalGamma] = <|{} -> IdentityMatrix[d]|>;
    Do[\[CapitalGamma][{\[Mu]}] = \[Gamma][[\[Mu]]], {\[Mu], n}];
    Do[
      Do[
        With[{is = sub},
          \[CapitalGamma][is] = gammaAppendAntisym[\[Eta], \[Gamma], \[CapitalGamma], Most[is], Last[is]]],
        {sub, Subsets[Range[n], {k}]}],
      {k, 2, n}];
    Table[\[CapitalGamma] /@ Subsets[Range[n], {k}], {k, 0, n}]];


End[];     (* `Private` *)
EndPackage[];
