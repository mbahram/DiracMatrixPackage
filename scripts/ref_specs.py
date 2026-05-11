"""
ref_specs.py — per-symbol RefPage content for the DiracMatrix paclet.

Each spec_<Symbol>() returns a RefPage describing the function's usage,
details, and example sections. Examples are designed from the kernel-first
audit recorded at Kernel/DiracMatrix.wl:<line>.

House rules followed throughout:
  * No Quiet: examples that emit messages are placed in Possible Issues.
  * Round-trip first: for any constructor/accessor pair, the first example
    in a cluster is `Accessor[Constructor[x]] === x` (House rule #3).
  * Idiomatic WL: Table / Map / Outer, no Do / For / While / AppendTo.
  * %%TEX: ... %% placeholders for inline math in prose cells.
"""

from build_ref_pages import (
    RefPage, UsageRow, Example, ExampleSubsection, PossibleIssue,
)


# ---------------------------------------------------------------------------
# FlatMetric  (Kernel/DiracMatrix.wl:69-70)
# ---------------------------------------------------------------------------


def spec_FlatMetric() -> RefPage:
    return RefPage(
        symbol="FlatMetric",
        usage_rows=[
            UsageRow(
                "FlatMetric[p, q]",
                "returns the diagonal flat metric of signature %%TEX: (p, q) %% "
                "with %%TEX: p %% positive (+1) and %%TEX: q %% negative (-1) "
                "diagonal entries."
            ),
        ],
        details_notes=[
            "The returned matrix is dense; for an explicit sparse form wrap "
            "the result with SparseArray.",
            "FlatMetric is a thin convenience over "
            "DiagonalMatrix[Join[ConstantArray[1, p], ConstantArray[-1, q]]]; "
            "it is most useful as the input metric to GammaMatrices, "
            "CliffordBasis, and CliffordCanonicalBasis.",
        ],
        basic_examples=[
            Example(
                text="The Minkowski metric in mostly-minus convention "
                     "(1 time, 3 space):",
                input="FlatMetric[1, 3] // MatrixForm",
            ),
            Example(
                text="A four-dimensional Euclidean signature has no minus "
                     "signs:",
                input="FlatMetric[4, 0] // MatrixForm",
            ),
        ],
        scope=[
            ExampleSubsection("Mostly-plus convention", [
                Example(
                    text="The mostly-plus Minkowski metric uses signature "
                         "(3, 1):",
                    input="FlatMetric[3, 1] // MatrixForm",
                ),
            ]),
            ExampleSubsection("Higher-dimensional signatures", [
                Example(
                    text="A split signature (2, 2), used in twistor theory:",
                    input="FlatMetric[2, 2] // MatrixForm",
                ),
                Example(
                    text="A ten-dimensional Lorentzian signature (1, 9):",
                    input="FlatMetric[1, 9] // MatrixForm",
                ),
            ]),
        ],
        applications=[
            ExampleSubsection("Use as a metric for GammaMatrices", [
                Example(
                    text="Pass FlatMetric directly into GammaMatrices to "
                         "produce the corresponding gamma matrices:",
                    input="GammaMatrices[FlatMetric[1, 3]] // Map[MatrixForm]",
                ),
                Example(
                    text="Verify the Clifford relation "
                         "%%TEX: \\{\\gamma^\\mu, \\gamma^\\nu\\} = "
                         "2\\eta^{\\mu\\nu}\\mathbb{I} %% in dimension 4:",
                    input=(
                        "Module[{\\[Eta] = FlatMetric[1, 3], \\[Gamma]},\n"
                        "  \\[Gamma] = GammaMatrices[\\[Eta]];\n"
                        "  Outer[#1 . #2 + #2 . #1 &, \\[Gamma], \\[Gamma], 1] == "
                        "2 TensorProduct[\\[Eta], IdentityMatrix[4]]]"
                    ),
                ),
            ]),
        ],
        possible_issues=[
            PossibleIssue(
                text="Negative integers are not in the domain — the call "
                     "remains unevaluated:",
                input="FlatMetric[-1, 3]",
            ),
        ],
        neat_examples=[
            Example(
                text="Verify that FlatMetric is its own inverse for any "
                     "signature, since its diagonal entries square to 1:",
                input=(
                    "Table[FlatMetric[p, n - p] . FlatMetric[p, n - p] == "
                    "IdentityMatrix[n], {n, 2, 6}, {p, 0, n}] // "
                    "Flatten // Apply[And]"
                ),
            ),
        ],
        see_also=[
            "RandomCurvedMetric", "MetricVielbein", "GammaMatrices",
            "DiagonalMatrix",
        ],
        related_guides=["DiracMatrix"],
        keywords=["metric", "Minkowski", "signature", "Clifford algebra"],
    )


# ---------------------------------------------------------------------------
# RandomCurvedMetric  (Kernel/DiracMatrix.wl:72-81)
# ---------------------------------------------------------------------------


def spec_RandomCurvedMetric() -> RefPage:
    return RefPage(
        symbol="RandomCurvedMetric",
        usage_rows=[
            UsageRow(
                "RandomCurvedMetric[p, q]",
                "returns a random real symmetric non-diagonal metric of "
                "signature %%TEX: (p, q) %% with default condition number "
                "spread %%TEX: \\sim 10^4 %%.",
            ),
            UsageRow(
                "RandomCurvedMetric[p, q, a]",
                "uses %%TEX: a %% as the spread exponent — eigenvalues of "
                "the diagonal core %%TEX: \\Lambda %% are drawn as "
                "%%TEX: \\pm 10^{r} %% with %%TEX: r \\in [-a, a] %% uniform.",
            ),
            UsageRow(
                "RandomCurvedMetric[p, q, a, s]",
                "additionally multiplies the diagonal core by "
                "%%TEX: s^2 %%, scaling typical metric components.",
            ),
        ],
        details_notes=[
            "The construction is %%TEX: Q^{\\mathsf{T}} \\cdot \\Lambda "
            "\\cdot Q %% with %%TEX: Q \\in O(n) %% drawn from "
            "CircularRealMatrixDistribution and %%TEX: \\Lambda %% diagonal "
            "with %%TEX: p %% positive and %%TEX: q %% negative eigenvalues.",
            "The condition number of the resulting metric is approximately "
            "%%TEX: \\kappa \\sim 10^{2a} %%, so the default "
            "%%TEX: a = 2 %% gives %%TEX: \\kappa \\sim 10^4 %%.",
            "Use SeedRandom before calling to obtain reproducible metrics.",
        ],
        basic_examples=[
            Example(
                text="A random non-diagonal Minkowski-like metric, signature "
                     "(1, 3):",
                input=(
                    "SeedRandom[42]; RandomCurvedMetric[1, 3, 0.5, 1] // "
                    "Chop // MatrixForm"
                ),
            ),
            Example(
                text="Confirm the signature is preserved by checking the "
                     "signs of the eigenvalues:",
                input=(
                    "SeedRandom[42]; "
                    "Sign @ Eigenvalues @ RandomCurvedMetric[1, 3, 0.5, 1]"
                ),
            ),
        ],
        scope=[
            ExampleSubsection("Default arguments", [
                Example(
                    text="With only p and q, the default spread "
                         "%%TEX: a = 2 %% produces a more poorly conditioned "
                         "matrix (κ ~ %%TEX: 10^{4} %%):",
                    input=(
                        "SeedRandom[1]; "
                        "Chop @ RandomCurvedMetric[2, 2] // MatrixForm"
                    ),
                ),
            ]),
            ExampleSubsection("Controlling the spread parameter", [
                Example(
                    text="Smaller %%TEX: a %% means a better-conditioned "
                         "metric:",
                    input=(
                        "SeedRandom[1]; "
                        "Through @ {Min, Max} @ Abs @ Eigenvalues @ "
                        "RandomCurvedMetric[3, 3, 0.1]"
                    ),
                ),
                Example(
                    text="Larger %%TEX: a %% produces eigenvalues spanning "
                         "many orders of magnitude:",
                    input=(
                        "SeedRandom[1]; "
                        "Through @ {Min, Max} @ Abs @ Eigenvalues @ "
                        "RandomCurvedMetric[3, 3, 3]"
                    ),
                ),
            ]),
        ],
        applications=[
            ExampleSubsection("Test GammaMatrices against the Clifford "
                              "relation for random metrics", [
                Example(
                    text="The vielbein construction in GammaMatrices handles "
                         "arbitrary symmetric metrics; the Clifford relation "
                         "still holds within numerical tolerance:",
                    input=(
                        "SeedRandom[42];\n"
                        "Module[{\\[Eta], \\[Gamma]},\n"
                        "  \\[Eta] = RandomCurvedMetric[2, 2, 0.5, 1];\n"
                        "  \\[Gamma] = GammaMatrices[\\[Eta]];\n"
                        "  NumericZeroQ[\n"
                        "    Outer[#1 . #2 + #2 . #1 &, \\[Gamma], \\[Gamma], 1] - \n"
                        "      2 TensorProduct[\\[Eta], IdentityMatrix[4]]]]"
                    ),
                ),
            ]),
        ],
        possible_issues=[
            PossibleIssue(
                text="A signature (0, 0) produces a 0×0 matrix and is "
                     "essentially a degenerate call:",
                input="RandomCurvedMetric[0, 0]",
            ),
        ],
        neat_examples=[
            Example(
                text="The Frobenius norm of a typical RandomCurvedMetric "
                     "grows with its spread:",
                input=(
                    "SeedRandom[1];\n"
                    "Table[Norm[RandomCurvedMetric[2, 2, a, 1], \"Frobenius\"],\n"
                    "  {a, {0.1, 0.5, 1.0, 2.0, 3.0}}] // N"
                ),
            ),
        ],
        see_also=[
            "FlatMetric", "MetricVielbein", "GammaMatrices",
            "CircularRealMatrixDistribution", "SeedRandom",
        ],
        related_guides=["DiracMatrix"],
        keywords=["random metric", "curved metric", "vielbein",
                  "condition number", "Clifford algebra"],
    )


# ---------------------------------------------------------------------------
# MetricVielbein  (Kernel/DiracMatrix.wl:83-89)
# ---------------------------------------------------------------------------


def spec_MetricVielbein() -> RefPage:
    return RefPage(
        symbol="MetricVielbein",
        usage_rows=[
            UsageRow(
                "MetricVielbein[\\[Eta]]",
                "returns %%TEX: \\{\\mathrm{signature},\\, e\\} %% for the "
                "real symmetric metric %%TEX: \\eta %%, where signature is "
                "%%TEX: \\mathrm{diag}(\\mathrm{Sign}(\\mathrm{eigenvalues})) %% "
                "and the vielbein %%TEX: e %% satisfies "
                "%%TEX: e^{\\mathsf{T}}\\!\\cdot\\!\\mathrm{signature}\\!\\cdot\\! e = \\eta %%."
            ),
        ],
        details_notes=[
            "The decomposition is constructed from the eigensystem of "
            "%%TEX: \\eta %%: with eigenvalues "
            "%%TEX: \\lambda_i %% and orthonormal eigenvectors "
            "%%TEX: v_i %% stacked into rows of "
            "%%TEX: V %%, signature is "
            "%%TEX: \\mathrm{diag}(\\mathrm{Sign}(\\lambda_i)) %% and the "
            "vielbein is "
            "%%TEX: e = \\mathrm{diag}(\\sqrt{|\\lambda_i|}) \\cdot V %%.",
            "MetricVielbein expects a metric that is symmetric within "
            "tolerance %%TEX: 10^{-12} %%.",
            "The vielbein is not unique: any rotation %%TEX: R \\in O(n) %% "
            "applied as %%TEX: e \\to R \\cdot e %% with "
            "%%TEX: R^{\\mathsf{T}}\\!\\cdot\\!\\mathrm{signature}\\!\\cdot\\! R = "
            "\\mathrm{signature} %% yields another vielbein for the same "
            "metric. The form returned here is the eigenvector frame.",
        ],
        basic_examples=[
            Example(
                text="The vielbein of FlatMetric returns the signature "
                     "itself and an identity vielbein (up to ordering and "
                     "signs):",
                input="MetricVielbein[FlatMetric[1, 3]]",
            ),
            Example(
                text="Round-trip: reconstructing %%TEX: \\eta %% from the "
                     "vielbein returns the original metric (House rule #3):",
                input=(
                    "Module[{\\[Eta] = FlatMetric[1, 3], sig, e},\n"
                    "  {sig, e} = MetricVielbein[\\[Eta]];\n"
                    "  Transpose[e] . sig . e === \\[Eta]]"
                ),
            ),
        ],
        scope=[
            ExampleSubsection("Random curved metric", [
                Example(
                    text="The vielbein of a random curved metric is a "
                     "non-diagonal real matrix; the round-trip holds within "
                     "tolerance:",
                    input=(
                        "SeedRandom[1];\n"
                        "Module[{\\[Eta], sig, e},\n"
                        "  \\[Eta] = RandomCurvedMetric[2, 2, 0.5, 1];\n"
                        "  {sig, e} = MetricVielbein[\\[Eta]];\n"
                        "  NumericZeroQ[Transpose[e] . sig . e - \\[Eta]]]"
                    ),
                ),
            ]),
            ExampleSubsection("Diagonal but non-flat metric", [
                Example(
                    text="The Schwarzschild components on the equatorial "
                         "plane at %%TEX: r = 3M %% are diagonal but not "
                         "%%TEX: \\pm 1 %% — the vielbein is the diagonal "
                         "matrix of square roots:",
                    input=(
                        "MetricVielbein[\n"
                        "  DiagonalMatrix[{-1/3, 3, 9, 9}]]"
                    ),
                ),
            ]),
        ],
        applications=[
            ExampleSubsection("Pulling back GammaMatrices through the "
                              "vielbein", [
                Example(
                    text="GammaMatrices uses MetricVielbein internally: the "
                         "flat-space γ matrices on the signature are pulled "
                         "back to the curved frame via "
                         "%%TEX: \\gamma^\\mu = e^\\mu_{\\ a}\\, \\Gamma^a %%. "
                         "Verify this gives the same matrices:",
                    input=(
                        "Module[{\\[Eta] = DiagonalMatrix[{-1/3, 3, 9, 9}], sig, e},\n"
                        "  {sig, e} = MetricVielbein[\\[Eta]];\n"
                        "  GammaMatrices[\\[Eta]] === \n"
                        "    TensorContract[TensorProduct[e, GammaMatrices[sig]], {{1, 3}}]]"
                    ),
                ),
            ]),
        ],
        possible_issues=[
            PossibleIssue(
                text="A non-symmetric matrix does not match the guard "
                     "pattern and the call remains unevaluated:",
                input="MetricVielbein[{{1, 2}, {3, 4}}]",
            ),
        ],
        neat_examples=[
            Example(
                text="For a randomly generated curved metric, the signature "
                     "returned by MetricVielbein always equals "
                     "Sign[Eigenvalues[\\[Eta]]] as a diagonal matrix:",
                input=(
                    "SeedRandom[7];\n"
                    "Module[{\\[Eta] = RandomCurvedMetric[2, 3, 0.5, 1], sig, e},\n"
                    "  {sig, e} = MetricVielbein[\\[Eta]];\n"
                    "  sig === DiagonalMatrix[Sign @ Eigenvalues @ \\[Eta]]]"
                ),
            ),
        ],
        see_also=[
            "FlatMetric", "RandomCurvedMetric", "GammaMatrices",
            "Eigensystem", "DiagonalMatrix", "SymmetricMatrixQ",
        ],
        related_guides=["DiracMatrix"],
        keywords=["vielbein", "tetrad", "frame field", "signature",
                  "Clifford algebra", "curved metric"],
    )


# ---------------------------------------------------------------------------
# EuclideanGammaMatrices  (Kernel/DiracMatrix.wl:95-113)
# ---------------------------------------------------------------------------


def spec_EuclideanGammaMatrices() -> RefPage:
    return RefPage(
        symbol="EuclideanGammaMatrices",
        usage_rows=[
            UsageRow(
                "EuclideanGammaMatrices[n]",
                "returns the n Euclidean gamma matrices of dimension "
                "%%TEX: 2^{\\lfloor n/2 \\rfloor} %% in the Brauer-Weyl "
                "(Pauli-Kronecker) representation."
            ),
        ],
        details_notes=[
            "For even %%TEX: n = 2m %%, the construction is "
            "%%TEX: \\Gamma^{2k-1} = \\mathbb{I}^{\\otimes(k-1)} \\otimes "
            "\\sigma_1 \\otimes \\sigma_3^{\\otimes(m-k)} %% and "
            "%%TEX: \\Gamma^{2k} = \\mathbb{I}^{\\otimes(k-1)} \\otimes "
            "\\sigma_2 \\otimes \\sigma_3^{\\otimes(m-k)} %% for "
            "%%TEX: k = 1, \\ldots, m %%. For odd "
            "%%TEX: n = 2m + 1 %%, an additional "
            "%%TEX: \\Gamma^{2m+1} = \\sigma_3^{\\otimes m} %% is appended.",
            "The returned matrices satisfy the Euclidean Clifford relation "
            "%%TEX: \\{\\Gamma^\\mu, \\Gamma^\\nu\\} = 2\\delta^{\\mu\\nu}\\mathbb{I} %%. "
            "For other signatures use GammaMatrices.",
            "Special cases n = 1, 2, 3 are handled by explicit base cases "
            "using PauliMatrix.",
        ],
        basic_examples=[
            Example(
                text="The four Euclidean gamma matrices in dimension 4 "
                     "(spinor dimension %%TEX: 2^2 = 4 %%):",
                input="EuclideanGammaMatrices[4] // Map[MatrixForm]",
            ),
            Example(
                text="Verify the Euclidean Clifford relation "
                     "%%TEX: \\{\\Gamma^\\mu, \\Gamma^\\nu\\} = "
                     "2\\delta^{\\mu\\nu}\\mathbb{I} %% in dimension 4:",
                input=(
                    "Module[{\\[CapitalGamma] = EuclideanGammaMatrices[4]},\n"
                    "  Outer[#1 . #2 + #2 . #1 &, \\[CapitalGamma], "
                    "\\[CapitalGamma], 1] == \n"
                    "    2 TensorProduct[IdentityMatrix[4], IdentityMatrix[4]]]"
                ),
            ),
        ],
        scope=[
            ExampleSubsection("Low-dimensional special cases", [
                Example(
                    text="Dimension 1: a single Pauli %%TEX: \\sigma_3 %%:",
                    input="EuclideanGammaMatrices[1] // Map[MatrixForm]",
                ),
                Example(
                    text="Dimension 2: the Pauli pair "
                         "%%TEX: \\{\\sigma_1, \\sigma_2\\} %%:",
                    input="EuclideanGammaMatrices[2] // Map[MatrixForm]",
                ),
                Example(
                    text="Dimension 3: the two-dimensional case extended "
                         "with %%TEX: \\sigma_3 %%:",
                    input="EuclideanGammaMatrices[3] // Map[MatrixForm]",
                ),
            ]),
            ExampleSubsection("Higher dimensions", [
                Example(
                    text="Dimension 6 produces six 8×8 matrices:",
                    input=(
                        "Map[Dimensions, EuclideanGammaMatrices[6]]"
                    ),
                ),
                Example(
                    text="The dimension count follows the rule "
                         "%%TEX: 2^{\\lfloor n/2 \\rfloor} %% for any n:",
                    input=(
                        "Table[\n"
                        "  Length @ EuclideanGammaMatrices[n] == n && "
                        "First @ Dimensions @ First @ EuclideanGammaMatrices[n] == "
                        "2^Floor[n/2],\n"
                        "  {n, 1, 8}] // Apply[And]"
                    ),
                ),
            ]),
        ],
        applications=[
            ExampleSubsection("Building block for GammaMatrices on flat "
                              "metrics", [
                Example(
                    text="For a flat signature %%TEX: (p,q) %%, GammaMatrices "
                         "multiplies the Euclidean Γ matrices by "
                         "%%TEX: \\mathrm{i} %% on time-like indices:",
                    input=(
                        "GammaMatrices[FlatMetric[1, 3]] === \n"
                        "  Diagonal[FlatMetric[1, 3] /. {-1 -> I}] * "
                        "EuclideanGammaMatrices[4]"
                    ),
                ),
            ]),
        ],
        possible_issues=[
            PossibleIssue(
                text="Non-positive integers are not in the domain and the "
                     "call remains unevaluated:",
                input="EuclideanGammaMatrices[0]",
            ),
        ],
        neat_examples=[
            Example(
                text="The chirality operator "
                     "%%TEX: \\Gamma_{2m+1} = \\Gamma^1 \\Gamma^2 \\cdots \\Gamma^{2m} %% "
                     "in even dimension equals the last basis element of the "
                     "odd-dimensional construction:",
                input=(
                    "Module[{m = 3, even, odd},\n"
                    "  even = EuclideanGammaMatrices[2 m];\n"
                    "  odd  = EuclideanGammaMatrices[2 m + 1];\n"
                    "  I^m Dot @@ even == Last[odd]]"
                ),
            ),
        ],
        see_also=[
            "GammaMatrices", "PauliMatrix", "KroneckerProduct",
            "FlatMetric", "CliffordBasis",
        ],
        related_guides=["DiracMatrix"],
        keywords=[
            "Euclidean gamma matrices", "Brauer-Weyl", "Pauli-Kronecker",
            "Clifford algebra", "spinor representation",
        ],
    )


# ---------------------------------------------------------------------------
# GammaMatrices  (Kernel/DiracMatrix.wl:119-130)
# ---------------------------------------------------------------------------


def spec_GammaMatrices() -> RefPage:
    return RefPage(
        symbol="GammaMatrices",
        usage_rows=[
            UsageRow(
                "GammaMatrices[n]",
                "returns the n Euclidean gamma matrices of dimension "
                "%%TEX: 2^{\\lfloor n/2 \\rfloor} %% (equivalent to "
                "EuclideanGammaMatrices[n])."
            ),
            UsageRow(
                "GammaMatrices[\\[Eta]]",
                "returns gamma matrices satisfying the Clifford relation "
                "%%TEX: \\{\\gamma^\\mu,\\gamma^\\nu\\}=2\\eta^{\\mu\\nu}\\mathbb{I} %% "
                "for any real symmetric metric %%TEX: \\eta %%; for a flat "
                "signed-diagonal metric the result is "
                "%%TEX: \\mathrm{i}\\,\\Gamma^\\mu %% on time-like indices "
                "and %%TEX: \\Gamma^\\mu %% on space-like indices; for a "
                "general metric a vielbein decomposition is used."
            ),
        ],
        details_notes=[
            "The Clifford anticommutation relation "
            "%%TEX: \\{\\gamma^\\mu,\\gamma^\\nu\\}=2\\eta^{\\mu\\nu}\\mathbb{I} %% "
            "is satisfied for any real symmetric metric "
            "%%TEX: \\eta %%, including non-flat curved metrics.",
            "Three call signatures are recognised: an integer "
            "(Euclidean case), a signed-diagonal metric "
            "%%TEX: \\mathrm{diag}(\\pm 1, \\ldots) %% (flat case with "
            "explicit %%TEX: \\mathrm{i} %% on time-like indices), and a "
            "general real symmetric matrix (uses MetricVielbein to pull "
            "back the flat-space Γ matrices into the curved frame).",
            "The result is in the Brauer-Weyl basis. Use ToDiracBasis or "
            "ToWeylBasis to transform to the Dirac or Weyl/chiral basis.",
            "Inputs must satisfy "
            "SymmetricMatrixQ[\\[Eta], Tolerance -> %%TEX: 10^{-12} %%].",
        ],
        basic_examples=[
            Example(
                text="The four-dimensional Minkowski (1, 3) gamma matrices:",
                input="GammaMatrices[FlatMetric[1, 3]] // Map[MatrixForm]",
            ),
            Example(
                text="Verify the Clifford anticommutation relation:",
                input=(
                    "Module[{\\[Eta] = FlatMetric[1, 3], \\[Gamma]},\n"
                    "  \\[Gamma] = GammaMatrices[\\[Eta]];\n"
                    "  Outer[#1 . #2 + #2 . #1 &, \\[Gamma], \\[Gamma], 1] == \n"
                    "    2 TensorProduct[\\[Eta], IdentityMatrix[4]]]"
                ),
            ),
        ],
        scope=[
            ExampleSubsection("Integer argument: Euclidean signature", [
                Example(
                    text="GammaMatrices[n] coincides with "
                         "EuclideanGammaMatrices[n]:",
                    input="GammaMatrices[4] === EuclideanGammaMatrices[4]",
                ),
            ]),
            ExampleSubsection("Flat signatures of various shapes", [
                Example(
                    text="Mostly-plus convention (3, 1):",
                    input="GammaMatrices[FlatMetric[3, 1]] // Map[MatrixForm]",
                ),
                Example(
                    text="Split signature (2, 2):",
                    input="GammaMatrices[FlatMetric[2, 2]] // Map[MatrixForm]",
                ),
                Example(
                    text="Six-dimensional Euclidean signature:",
                    input=(
                        "Dimensions /@ GammaMatrices[FlatMetric[6, 0]]"
                    ),
                ),
            ]),
            ExampleSubsection("Diagonal non-flat metrics", [
                Example(
                    text="Schwarzschild components on the equatorial plane "
                         "at %%TEX: r = 3M %%, "
                         "%%TEX: \\mathrm{diag}(-1/3, 3, 9, 9) %%:",
                    input=(
                        "GammaMatrices[DiagonalMatrix[{-1/3, 3, 9, 9}]] // \n"
                        "  Map[MatrixForm]"
                    ),
                ),
                Example(
                    text="FLRW spatial slice with scale factor "
                         "%%TEX: a = 2 %%, signature "
                         "%%TEX: \\mathrm{diag}(-1, 4, 4, 4) %%:",
                    input=(
                        "Dimensions /@ "
                        "GammaMatrices[DiagonalMatrix[{-1, 4, 4, 4}]]"
                    ),
                ),
            ]),
            ExampleSubsection("Random non-diagonal curved metrics", [
                Example(
                    text="A random real symmetric metric is handled via the "
                         "vielbein decomposition; the Clifford relation "
                         "holds within numerical tolerance:",
                    input=(
                        "SeedRandom[42];\n"
                        "Module[{\\[Eta], \\[Gamma]},\n"
                        "  \\[Eta] = RandomCurvedMetric[2, 2, 0.5, 1];\n"
                        "  \\[Gamma] = GammaMatrices[\\[Eta]];\n"
                        "  NumericZeroQ[\n"
                        "    Outer[#1 . #2 + #2 . #1 &, \\[Gamma], \\[Gamma], 1] - \n"
                        "      2 TensorProduct[\\[Eta], IdentityMatrix[4]]]]"
                    ),
                ),
            ]),
        ],
        applications=[
            ExampleSubsection("Tracelessness and square identity", [
                Example(
                    text="Each γ matrix is traceless:",
                    input=(
                        "Tr /@ GammaMatrices[FlatMetric[1, 3]]"
                    ),
                ),
                Example(
                    text="%%TEX: (\\gamma^\\mu)^2 = \\eta^{\\mu\\mu}\\,\\mathbb{I} %% "
                     "for the flat Minkowski signature:",
                    input=(
                        "MatrixPower[#, 2] & /@ GammaMatrices[FlatMetric[1, 3]] == \n"
                        "  TensorProduct[Diagonal @ FlatMetric[1, 3], IdentityMatrix[4]]"
                    ),
                ),
            ]),
            ExampleSubsection("Trace identities", [
                Example(
                    text="%%TEX: \\mathrm{Tr}(\\gamma^\\mu \\gamma^\\nu) = "
                         "2^{\\lfloor n/2 \\rfloor}\\eta^{\\mu\\nu} %%:",
                    input=(
                        "Module[{\\[CapitalGamma] = GammaMatrices[FlatMetric[1, 3]]},\n"
                        "  Outer[Tr@*Dot, \\[CapitalGamma], \\[CapitalGamma], 1] == \n"
                        "    4 FlatMetric[1, 3]]"
                    ),
                ),
            ]),
            ExampleSubsection("Chirality operator in even dimension", [
                Example(
                    text="%%TEX: \\gamma_c = \\mathrm{i}^{(n - 2p)/2}\\,"
                         "\\gamma^0 \\gamma^1 \\cdots \\gamma^{n-1} %% is "
                         "Hermitian, squares to the identity, and anticommutes "
                         "with every γ:",
                    input=(
                        "Module[{n = 4, p = 1, \\[CapitalGamma], \\[CapitalGamma]c},\n"
                        "  \\[CapitalGamma]  = GammaMatrices[FlatMetric[p, n - p]];\n"
                        "  \\[CapitalGamma]c = I^((n - 2 p)/2) Dot @@ \\[CapitalGamma];\n"
                        "  {HermitianMatrixQ[\\[CapitalGamma]c],\n"
                        "   \\[CapitalGamma]c . \\[CapitalGamma]c == IdentityMatrix[2^Floor[n/2]]}]"
                    ),
                ),
            ]),
        ],
        possible_issues=[
            PossibleIssue(
                text="A non-symmetric matrix is not in the domain and the "
                     "call remains unevaluated (the guard pattern "
                     "SymmetricMatrixQ[…, Tolerance -> %%TEX: 10^{-12} %%] "
                     "rejects it before the GammaMatrices::nonsym message "
                     "fires):",
                input="GammaMatrices[{{0, 1}, {2, 0}}]",
            ),
            PossibleIssue(
                text="A non-numeric symbolic 2x2 metric does not produce a "
                     "usable Eigensystem and the construction hangs in "
                     "recursive evaluation. Always provide a numeric (or "
                     "exact rational) metric; if your metric is symbolic, "
                     "substitute numeric values for the parameters before "
                     "passing it to GammaMatrices. Below we show the safe "
                     "approach by substituting a, b, c with concrete "
                     "numerical values:",
                input=(
                    "GammaMatrices[{{a, b}, {b, c}} /. {a -> 1, b -> 0, c -> -1}] // "
                    "Map[MatrixForm]"
                ),
            ),
        ],
        neat_examples=[
            Example(
                text="The Clifford relation holds across a sweep of "
                     "signatures and dimensions:",
                input=(
                    "Table[\n"
                    "  Module[{\\[Eta] = FlatMetric[p, n - p], \\[Gamma]},\n"
                    "    \\[Gamma] = GammaMatrices[\\[Eta]];\n"
                    "    Outer[#1 . #2 + #2 . #1 &, \\[Gamma], \\[Gamma], 1] == \n"
                    "      2 TensorProduct[\\[Eta], IdentityMatrix[2^Floor[n/2]]]],\n"
                    "  {n, 2, 6}, {p, 0, n}] // Flatten // Apply[And]"
                ),
            ),
        ],
        see_also=[
            "EuclideanGammaMatrices", "FlatMetric", "RandomCurvedMetric",
            "MetricVielbein", "ToDiracBasis", "ToWeylBasis",
            "CliffordBasis", "CliffordCanonicalBasis", "NumericZeroQ",
        ],
        related_guides=["DiracMatrix"],
        keywords=[
            "gamma matrices", "Dirac matrices", "Clifford algebra",
            "Brauer-Weyl", "Pauli-Kronecker", "vielbein", "spinor",
        ],
    )


# ---------------------------------------------------------------------------
# ToDiracBasis  (Kernel/DiracMatrix.wl:136-143)
# ---------------------------------------------------------------------------


def spec_ToDiracBasis() -> RefPage:
    return RefPage(
        symbol="ToDiracBasis",
        usage_rows=[
            UsageRow(
                "ToDiracBasis[\\[Gamma]]",
                "takes a list of gamma matrices in the Brauer-Weyl basis "
                "and returns them in the Dirac basis (where "
                "%%TEX: \\gamma^0 %% is diagonal)."
            ),
        ],
        details_notes=[
            "The transform is the similarity "
            "%%TEX: \\gamma^\\mu \\to S^{-1}\\gamma^\\mu S %%, where "
            "%%TEX: S %% is built from the eigenvectors of "
            "%%TEX: \\gamma^0 %% reordered so the imaginary eigenvalues "
            "with %%TEX: \\mathrm{Im} > 0 %% come first (mostly-plus "
            "convention).",
            "Since the transform is a similarity, all Clifford-algebra "
            "identities (anticommutator, traces, contractions) are "
            "preserved.",
            "Use this for example to obtain the textbook Dirac matrices "
            "with diagonal %%TEX: \\gamma^0 %% on the (1, 3) signature.",
        ],
        basic_examples=[
            Example(
                text="The standard Dirac matrices in dimension 4: "
                     "%%TEX: \\gamma^0 %% is diagonal "
                     "%%TEX: \\mathrm{diag}(1, 1, -1, -1) %%:",
                input=(
                    "ToDiracBasis[GammaMatrices[FlatMetric[1, 3]]] // "
                    "Map[MatrixForm]"
                ),
            ),
            Example(
                text="The Clifford relation is preserved by the basis "
                     "change:",
                input=(
                    "Module[{\\[Eta] = FlatMetric[1, 3], \\[Gamma]},\n"
                    "  \\[Gamma] = ToDiracBasis @ GammaMatrices[\\[Eta]];\n"
                    "  Outer[#1 . #2 + #2 . #1 &, \\[Gamma], \\[Gamma], 1] == \n"
                    "    2 TensorProduct[\\[Eta], IdentityMatrix[4]]]"
                ),
            ),
        ],
        scope=[
            ExampleSubsection("Diagonality of γ⁰", [
                Example(
                    text="By construction the first matrix is diagonal:",
                    input=(
                        "DiagonalMatrixQ[\n"
                        "  First @ ToDiracBasis @ GammaMatrices[FlatMetric[1, 3]]]"
                    ),
                ),
            ]),
            ExampleSubsection("Other Lorentzian signatures", [
                Example(
                    text="In split signature (2, 2) the first matrix is also "
                         "diagonalised:",
                    input=(
                        "First @ ToDiracBasis @ GammaMatrices[FlatMetric[2, 2]] // \n"
                        "  MatrixForm"
                    ),
                ),
            ]),
            ExampleSubsection("Odd dimensions", [
                Example(
                    text="In odd dimension n = 5 the function still produces "
                     "a similarity transform that diagonalises the first "
                     "gamma:",
                    input=(
                        "DiagonalMatrixQ[\n"
                        "  First @ ToDiracBasis @ GammaMatrices[FlatMetric[1, 4]]]"
                    ),
                ),
            ]),
        ],
        applications=[
            ExampleSubsection("Round-trip: Dirac → Brauer-Weyl is invertible "
                              "by another similarity", [
                Example(
                    text="The function is a similarity transform; applying "
                         "another similarity that diagonalises the result's "
                         "first matrix in the Brauer-Weyl-ordered "
                         "eigensystem returns the original up to a unitary "
                         "rotation. The simplest check is that both bases "
                         "share the same anticommutator structure:",
                    input=(
                        "Module[{bw, dirac, \\[Eta] = FlatMetric[1, 3]},\n"
                        "  bw = GammaMatrices[\\[Eta]];\n"
                        "  dirac = ToDiracBasis[bw];\n"
                        "  Outer[#1 . #2 + #2 . #1 &, bw, bw, 1] === \n"
                        "    Outer[#1 . #2 + #2 . #1 &, dirac, dirac, 1]]"
                    ),
                ),
            ]),
        ],
        possible_issues=[
            PossibleIssue(
                text="An empty argument is not in the domain and the call "
                     "remains unevaluated:",
                input="ToDiracBasis[{}]",
            ),
        ],
        neat_examples=[
            Example(
                text="In the Dirac basis with mostly-minus signature the "
                     "diagonal %%TEX: \\gamma^0 %% is "
                     "%%TEX: \\mathrm{diag}(1, 1, -1, -1) %%:",
                input=(
                    "Diagonal @ First @ ToDiracBasis @ "
                    "GammaMatrices[FlatMetric[1, 3]]"
                ),
            ),
        ],
        see_also=[
            "GammaMatrices", "ToWeylBasis", "EuclideanGammaMatrices",
            "Eigensystem",
        ],
        related_guides=["DiracMatrix"],
        keywords=["Dirac basis", "spinor basis transform",
                  "similarity transformation", "Clifford algebra"],
    )


# ---------------------------------------------------------------------------
# ToWeylBasis  (Kernel/DiracMatrix.wl:145-154)
# ---------------------------------------------------------------------------


def spec_ToWeylBasis() -> RefPage:
    return RefPage(
        symbol="ToWeylBasis",
        usage_rows=[
            UsageRow(
                "ToWeylBasis[\\[Gamma]]",
                "takes a list of gamma matrices in the Brauer-Weyl basis "
                "and returns them in the Weyl/chiral basis, in which the "
                "chirality operator is block-diagonal. For odd dimension "
                "there is no chiral decomposition and the Dirac basis is "
                "returned along with a ToWeylBasis::oddDim message."
            ),
        ],
        details_notes=[
            "The Weyl/chiral basis is produced by first applying "
            "ToDiracBasis and then a final block-rotation "
            "%%TEX: T = \\tfrac{1}{\\sqrt{2}}\\,(\\sigma_x \\otimes \\mathbb{I}_{n/2}) %% "
            "that pairs the upper and lower components.",
            "All Clifford-algebra identities are preserved under the basis "
            "change.",
            "For odd dimension the function emits ToWeylBasis::oddDim and "
            "falls back to the Dirac basis — there is no genuine Weyl "
            "decomposition in odd dimension.",
        ],
        basic_examples=[
            Example(
                text="The Weyl/chiral basis on the four-dimensional "
                     "Minkowski signature:",
                input=(
                    "ToWeylBasis[GammaMatrices[FlatMetric[1, 3]]] // "
                    "Map[MatrixForm]"
                ),
            ),
            Example(
                text="In the Weyl basis the chirality operator "
                     "%%TEX: \\gamma_5 = \\mathrm{i}\\,\\gamma^0\\gamma^1"
                     "\\gamma^2\\gamma^3 %% is diagonal with eigenvalues "
                     "%%TEX: \\pm 1 %%:",
                input=(
                    "Module[{\\[Gamma] = ToWeylBasis @ "
                    "GammaMatrices[FlatMetric[1, 3]]},\n"
                    "  Diagonal[I Dot @@ \\[Gamma]]]"
                ),
            ),
        ],
        scope=[
            ExampleSubsection("Other even dimensions", [
                Example(
                    text="Split signature (2, 2):",
                    input=(
                        "Diagonal @ Dot @@ "
                        "ToWeylBasis @ GammaMatrices[FlatMetric[2, 2]]"
                    ),
                ),
                Example(
                    text="Six-dimensional Euclidean: γ_7 = "
                     "%%TEX: \\mathrm{i}^3\\,\\Gamma^1\\cdots\\Gamma^6 %% is "
                     "diagonal in the Weyl basis:",
                    input=(
                        "Module[{\\[Gamma] = ToWeylBasis @ "
                        "GammaMatrices[FlatMetric[6, 0]]},\n"
                        "  Diagonal[I^3 Dot @@ \\[Gamma]] // Chop]"
                    ),
                ),
            ]),
        ],
        possible_issues=[
            PossibleIssue(
                text="In odd dimension the Weyl decomposition does not "
                     "exist; ToWeylBasis emits ToWeylBasis::oddDim and "
                     "returns the Dirac basis instead. The captured "
                     "message text is shown below; the function still "
                     "returns a usable list of matrices:",
                input="ToWeylBasis[GammaMatrices[FlatMetric[1, 4]]]",
                messages=[
                    "ToWeylBasis::oddDim: For odd dimension there is no "
                    "Weyl/chiral basis. The result is returned in the "
                    "Dirac basis."
                ],
            ),
        ],
        neat_examples=[
            Example(
                text="The Clifford anticommutator is invariant under "
                     "ToWeylBasis:",
                input=(
                    "Module[{bw, w, \\[Eta] = FlatMetric[1, 3]},\n"
                    "  bw = GammaMatrices[\\[Eta]];\n"
                    "  w  = ToWeylBasis[bw];\n"
                    "  Outer[#1 . #2 + #2 . #1 &, bw, bw, 1] === \n"
                    "    Outer[#1 . #2 + #2 . #1 &, w, w, 1]]"
                ),
            ),
        ],
        see_also=[
            "GammaMatrices", "ToDiracBasis", "EuclideanGammaMatrices",
        ],
        related_guides=["DiracMatrix"],
        keywords=[
            "Weyl basis", "chiral basis", "chirality", "γ₅",
            "spinor basis transform", "Clifford algebra",
        ],
    )


# ---------------------------------------------------------------------------
# NumericZeroQ  (Kernel/DiracMatrix.wl:160-161)
# ---------------------------------------------------------------------------


def spec_NumericZeroQ() -> RefPage:
    return RefPage(
        symbol="NumericZeroQ",
        usage_rows=[
            UsageRow(
                "NumericZeroQ[a]",
                "returns True if every entry of "
                "%%TEX: a %% is zero within tolerance "
                "%%TEX: 10^{-8} %% after Chop."
            ),
            UsageRow(
                "NumericZeroQ[a, tol]",
                "uses the supplied tolerance tol."
            ),
        ],
        details_notes=[
            "Implementation: "
            "%%TEX: \\mathrm{Norm}[\\mathrm{Chop}[\\mathrm{Flatten}[a], \\mathrm{tol}], "
            "\\mathrm{Frobenius}] = 0 %%.",
            "Use this to assert that a numerically computed quantity is "
            "the zero matrix or zero tensor when exact equality "
            "(===) cannot be expected due to round-off.",
            "The default tolerance %%TEX: 10^{-8} %% is appropriate for "
            "machine-precision computation; for arbitrary-precision use a "
            "stricter tolerance.",
        ],
        basic_examples=[
            Example(
                text="Zero matrix is reported as True:",
                input="NumericZeroQ[{{0., 0.}, {0., 0.}}]",
            ),
            Example(
                text="A matrix with entries smaller than the default "
                     "tolerance is also True:",
                input="NumericZeroQ[{{1*^-10, 0.}, {0., 1*^-12}}]",
            ),
            Example(
                text="A clearly non-zero matrix is False:",
                input="NumericZeroQ[{{0., 0.5}, {0., 0.}}]",
            ),
        ],
        scope=[
            ExampleSubsection("Tensor inputs of any rank", [
                Example(
                    text="A 3-tensor whose entries are all numerically zero:",
                    input=(
                        "NumericZeroQ[ConstantArray[1*^-12, {3, 3, 3}]]"
                    ),
                ),
                Example(
                    text="A scalar — flattened then normed:",
                    input="NumericZeroQ[1*^-15]",
                ),
            ]),
            ExampleSubsection("Custom tolerance", [
                Example(
                    text="A loose tolerance accepts larger residuals:",
                    input=(
                        "NumericZeroQ[{{0., 1*^-5}, {0., 0.}}, 1*^-4]"
                    ),
                ),
                Example(
                    text="A strict tolerance rejects the same matrix:",
                    input=(
                        "NumericZeroQ[{{0., 1*^-5}, {0., 0.}}, 1*^-6]"
                    ),
                ),
            ]),
        ],
        applications=[
            ExampleSubsection("Asserting the Clifford relation in "
                              "numerical form", [
                Example(
                    text="For random curved metrics, exact equality between "
                         "matrices is not appropriate; check the residual "
                         "with NumericZeroQ:",
                    input=(
                        "SeedRandom[1];\n"
                        "Module[{\\[Eta] = RandomCurvedMetric[1, 3, 0.5, 1], \\[Gamma]},\n"
                        "  \\[Gamma] = GammaMatrices[\\[Eta]];\n"
                        "  NumericZeroQ[\n"
                        "    Outer[#1 . #2 + #2 . #1 &, \\[Gamma], \\[Gamma], 1] - \n"
                        "      2 TensorProduct[\\[Eta], IdentityMatrix[4]]]]"
                    ),
                ),
            ]),
        ],
        possible_issues=[
            PossibleIssue(
                text="Non-numeric symbolic entries do not vanish under Chop "
                     "and yield False:",
                input="NumericZeroQ[{a, b}]",
            ),
        ],
        neat_examples=[
            Example(
                text="The Clifford anticommutator residual decays as the "
                     "spread parameter %%TEX: a %% in RandomCurvedMetric "
                     "decreases:",
                input=(
                    "SeedRandom[1];\n"
                    "Module[{\\[Eta], \\[Gamma], r},\n"
                    "  \\[Eta] = RandomCurvedMetric[1, 3, 0.1, 1];\n"
                    "  \\[Gamma] = GammaMatrices[\\[Eta]];\n"
                    "  r = Outer[#1 . #2 + #2 . #1 &, \\[Gamma], \\[Gamma], 1] - "
                    "2 TensorProduct[\\[Eta], IdentityMatrix[4]];\n"
                    "  NumericZeroQ[r]]"
                ),
            ),
        ],
        see_also=["Chop", "Norm", "Flatten"],
        related_guides=["DiracMatrix"],
        keywords=["numerical zero", "Chop", "tolerance", "Frobenius norm"],
    )


# ---------------------------------------------------------------------------
# CliffordCanonicalBasis  (Kernel/DiracMatrix.wl:167-178)
# ---------------------------------------------------------------------------


def spec_CliffordCanonicalBasis() -> RefPage:
    return RefPage(
        symbol="CliffordCanonicalBasis",
        usage_rows=[
            UsageRow(
                "CliffordCanonicalBasis[\\[Eta]]",
                "returns the canonical graded operator basis of the "
                "Clifford algebra %%TEX: \\mathrm{Cl}(\\eta) %% as a list "
                "grouped by grade %%TEX: \\{\\Gamma_{(0)}, \\Gamma_{(1)}, "
                "\\ldots, \\Gamma_{(n)}\\} %% via explicit antisymmetrisation."
            ),
        ],
        details_notes=[
            "Each grade-k element on indices "
            "%%TEX: i_1 < \\cdots < i_k %% is the antisymmetrised product "
            "%%TEX: \\Gamma_{[i_1 \\cdots i_k]} = \\frac{1}{k!}\\sum_{"
            "\\sigma \\in S_k} \\mathrm{sgn}(\\sigma)\\,\\Gamma_{i_{\\sigma(1)}}"
            "\\cdots \\Gamma_{i_{\\sigma(k)}} %%.",
            "This is a literal transcription of the formula; it is "
            "pedagogically transparent but combinatorially expensive — for "
            "n indices it evaluates %%TEX: n! %% permutations.",
            "For non-flat metrics with widely scaled eigenvalues, precision "
            "can degrade at high grade because of cancellations. Prefer "
            "CliffordBasis for production use; CliffordCanonicalBasis is "
            "best for pedagogy and as a flat-metric reference.",
            "Number of grade-k elements is %%TEX: \\binom{n}{k} %%, and "
            "the total basis size is %%TEX: 2^n %%.",
        ],
        basic_examples=[
            Example(
                text="On the four-dimensional Minkowski signature the basis "
                     "has 1 + 4 + 6 + 4 + 1 = 16 elements:",
                input=(
                    "Length /@ CliffordCanonicalBasis[FlatMetric[1, 3]]"
                ),
            ),
            Example(
                text="The grade-0 element is the identity:",
                input=(
                    "First @ First @ CliffordCanonicalBasis[FlatMetric[1, 3]] // "
                    "MatrixForm"
                ),
            ),
        ],
        scope=[
            ExampleSubsection("Two-dimensional Euclidean case", [
                Example(
                    text="The canonical basis in dimension 2 has 1 + 2 + 1 = "
                         "4 elements; the grade-2 element is the chirality "
                         "operator up to sign:",
                    input=(
                        "Length /@ CliffordCanonicalBasis[FlatMetric[2, 0]]"
                    ),
                ),
            ]),
            ExampleSubsection("Grade-1 equals the gamma matrices", [
                Example(
                    text="The grade-1 elements are exactly the gamma "
                         "matrices used in their construction:",
                    input=(
                        "CliffordCanonicalBasis[FlatMetric[1, 3]][[2]] === \n"
                        "  GammaMatrices[FlatMetric[1, 3]]"
                    ),
                ),
            ]),
        ],
        applications=[
            ExampleSubsection("Agreement with CliffordBasis on flat metrics", [
                Example(
                    text="On any flat signature the two implementations "
                         "produce the same basis at every grade:",
                    input=(
                        "Table[\n"
                        "  CliffordCanonicalBasis[FlatMetric[p, n - p]] === \n"
                        "    CliffordBasis[FlatMetric[p, n - p]],\n"
                        "  {n, 2, 5}, {p, 0, n}] // Flatten // Apply[And]"
                    ),
                ),
            ]),
        ],
        possible_issues=[
            PossibleIssue(
                text="Higher grade on a random curved metric loses precision "
                     "due to cancellations in the explicit sum — prefer "
                     "CliffordBasis (production-ready alternative):",
                input=(
                    "SeedRandom[12345];\n"
                    "Module[{\\[Eta] = RandomCurvedMetric[3, 3]},\n"
                    "  NumericZeroQ[\n"
                    "    Last @ CliffordCanonicalBasis[\\[Eta]] - \n"
                    "    Last @ CliffordBasis[\\[Eta]]]]"
                ),
            ),
            PossibleIssue(
                text="Non-symmetric input does not match the guard pattern; "
                     "the call remains unevaluated:",
                input="CliffordCanonicalBasis[{{1, 2}, {3, 4}}]",
            ),
        ],
        neat_examples=[
            Example(
                text="The total basis dimension is "
                     "%%TEX: 2^n %% for an n-dimensional metric:",
                input=(
                    "Table[\n"
                    "  Total @ Map[Length, CliffordCanonicalBasis[FlatMetric[p, n - p]]] == "
                    "2^n,\n"
                    "  {n, 2, 5}, {p, 0, n}] // Flatten // Apply[And]"
                ),
            ),
        ],
        see_also=[
            "CliffordBasis", "GammaMatrices", "FlatMetric",
            "RandomCurvedMetric", "Permutations", "Signature",
        ],
        related_guides=["DiracMatrix"],
        keywords=[
            "Clifford algebra", "graded basis", "antisymmetrisation",
            "exterior algebra", "spinor",
        ],
    )


# ---------------------------------------------------------------------------
# CliffordBasis  (Kernel/DiracMatrix.wl:189-202)
# ---------------------------------------------------------------------------


def spec_CliffordBasis() -> RefPage:
    return RefPage(
        symbol="CliffordBasis",
        usage_rows=[
            UsageRow(
                "CliffordBasis[\\[Eta]]",
                "returns the canonical graded Clifford operator basis "
                "computed via an antisymmetrised recursion; same shape as "
                "CliffordCanonicalBasis but much faster and numerically "
                "stable."
            ),
        ],
        details_notes=[
            "The recursion is "
            "%%TEX: \\Gamma_{\\mathcal{I}\\cup\\{\\mu\\}} = "
            "\\Gamma_{\\mathcal{I}}\\cdot \\Gamma_\\mu - "
            "\\sum_{j=1}^{|\\mathcal{I}|}(-1)^{j-1}\\eta_{\\mu, i_j}"
            "\\,\\Gamma_{\\mathcal{I}\\setminus\\{i_j\\}} %%, building each "
            "grade from the previous one without recomputing permutation "
            "sums.",
            "CliffordBasis is the production-ready implementation: O("
            "%%TEX: 2^n %% n²) operations versus O("
            "%%TEX: 2^n %% n!) for CliffordCanonicalBasis, and "
            "numerically stable for curved metrics with widely scaled "
            "eigenvalues.",
            "On flat metrics it agrees with CliffordCanonicalBasis at "
            "every grade.",
        ],
        basic_examples=[
            Example(
                text="The four-dimensional Minkowski basis has 1 + 4 + 6 + "
                     "4 + 1 = 16 elements grouped by grade:",
                input="Length /@ CliffordBasis[FlatMetric[1, 3]]",
            ),
            Example(
                text="The grade-1 elements are the gamma matrices:",
                input=(
                    "CliffordBasis[FlatMetric[1, 3]][[2]] === "
                    "GammaMatrices[FlatMetric[1, 3]]"
                ),
            ),
        ],
        scope=[
            ExampleSubsection("Agreement with CliffordCanonicalBasis on "
                              "flat metrics", [
                Example(
                    text="The two implementations produce the same basis "
                         "at every grade on flat metrics:",
                    input=(
                        "Table[\n"
                        "  CliffordBasis[FlatMetric[p, n - p]] === \n"
                        "    CliffordCanonicalBasis[FlatMetric[p, n - p]],\n"
                        "  {n, 2, 5}, {p, 0, n}] // Flatten // Apply[And]"
                    ),
                ),
            ]),
            ExampleSubsection("Numerical stability for curved metrics", [
                Example(
                    text="At low grade, CliffordBasis and "
                         "CliffordCanonicalBasis agree on a random curved "
                         "metric:",
                    input=(
                        "SeedRandom[12345];\n"
                        "Module[{\\[Eta] = RandomCurvedMetric[3, 3]},\n"
                        "  NumericZeroQ[\n"
                        "    CliffordCanonicalBasis[\\[Eta]][[;; 3]] - \n"
                        "    CliffordBasis[\\[Eta]][[;; 3]]]]"
                    ),
                ),
            ]),
            ExampleSubsection("Higher dimensions", [
                Example(
                    text="A six-dimensional flat signature: "
                         "%%TEX: 1+6+15+20+15+6+1 = 64 = 2^6 %%:",
                    input="Length /@ CliffordBasis[FlatMetric[3, 3]]",
                ),
            ]),
        ],
        applications=[
            ExampleSubsection("Grade-2 elements are antisymmetric products", [
                Example(
                    text="The grade-2 elements satisfy "
                         "%%TEX: \\Gamma_{\\mu\\nu} = \\tfrac{1}{2}["
                         "\\gamma^\\mu, \\gamma^\\nu] %%:",
                    input=(
                        "Module[{\\[Gamma] = GammaMatrices[FlatMetric[1, 3]], "
                        "\\[CapitalGamma]2},\n"
                        "  \\[CapitalGamma]2 = CliffordBasis[FlatMetric[1, 3]][[3]];\n"
                        "  \\[CapitalGamma]2 === Table[\n"
                        "    (\\[Gamma][[Subsets[Range[4], {2}][[i, 1]]]] . "
                        "\\[Gamma][[Subsets[Range[4], {2}][[i, 2]]]] - \n"
                        "     \\[Gamma][[Subsets[Range[4], {2}][[i, 2]]]] . "
                        "\\[Gamma][[Subsets[Range[4], {2}][[i, 1]]]])/2,\n"
                        "    {i, Length @ Subsets[Range[4], {2}]}]]"
                    ),
                ),
            ]),
        ],
        possible_issues=[
            PossibleIssue(
                text="Non-symmetric input does not match the guard pattern; "
                     "the call remains unevaluated:",
                input="CliffordBasis[{{1, 2}, {3, 4}}]",
            ),
        ],
        neat_examples=[
            Example(
                text="The grade-n element is the chirality (volume) "
                     "operator; on Minkowski (1, 3) it is "
                     "%%TEX: \\gamma^0\\gamma^1\\gamma^2\\gamma^3 %%:",
                input=(
                    "Last @ Last @ CliffordBasis[FlatMetric[1, 3]] === \n"
                    "  Dot @@ GammaMatrices[FlatMetric[1, 3]]"
                ),
            ),
        ],
        see_also=[
            "CliffordCanonicalBasis", "GammaMatrices",
            "FlatMetric", "RandomCurvedMetric", "NumericZeroQ",
        ],
        related_guides=["DiracMatrix"],
        keywords=[
            "Clifford algebra", "graded basis", "antisymmetric recursion",
            "exterior algebra", "spinor", "chirality operator",
        ],
    )


# ---------------------------------------------------------------------------
# Public registry
# ---------------------------------------------------------------------------


def all_specs():
    return [
        spec_FlatMetric(),
        spec_RandomCurvedMetric(),
        spec_MetricVielbein(),
        spec_EuclideanGammaMatrices(),
        spec_GammaMatrices(),
        spec_ToDiracBasis(),
        spec_ToWeylBasis(),
        spec_NumericZeroQ(),
        spec_CliffordCanonicalBasis(),
        spec_CliffordBasis(),
    ]
