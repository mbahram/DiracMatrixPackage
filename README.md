# DiracMatrix

A Wolfram Language paclet that **constructs** Dirac gamma matrices for an
arbitrary real symmetric metric in any dimension. Given a metric `η`, it returns
the literal `2^Floor[n/2] × 2^Floor[n/2]` matrices satisfying the Clifford
relation

$$
\lbrace \gamma^{\mu}, \gamma^{\nu} \rbrace = 2 \eta^{\mu\nu} \mathbf{I}.
$$

— **Author:** Mads Bahrami · **License:** MIT · **Version:** 1.0.0

## What's different

Existing Mathematica packages in this space — *GammaMaP*, *GAMMA*, *Tracer*,
*FeynCalc*'s `DiracMatrix`, *Clifford Algebra with Mathematica* — are all
**symbolic engines**: they manipulate abstract Lorentz indices, anticommutators,
Fierz identities, and traces, and assume the user already has a representation
in hand.

`DiracMatrix` is **constructive** and **numerically explicit**:

- Hand it any real symmetric metric — flat `(p,q)`, Schwarzschild on the
  equatorial plane, FLRW, or a randomly generated curved metric — and it
  returns the actual matrix entries.
- For non-flat metrics the vielbein decomposition `η = eᵀ·signature·e` is done
  for you (`MetricVielbein`).
- The flat-space step uses the textbook **Brauer–Weyl (Pauli–Kronecker)**
  construction.
- Basis transformations to the **Dirac** and **Weyl/chiral** bases are exposed
  as one-liners.
- The **canonical graded Clifford operator basis** ships in two
  implementations: a pedagogically transparent one (literal antisymmetrisation
  sum) and a numerically stable recursive one for production use.

## Install

```wolfram
PacletInstall["/path/to/DiracMatrixPackage"]
Needs["DiracMatrix`"]
```

or, without installing,

```wolfram
PacletDirectoryLoad["/path/to/DiracMatrixPackage"];
Needs["DiracMatrix`"]
```

## Examples

**Minkowski (1, 3) in the Brauer–Weyl basis:**

```wolfram
GammaMatrices[FlatMetric[1, 3]]
```

**Schwarzschild components on the equatorial plane at `r = 3M`:**

```wolfram
GammaMatrices[DiagonalMatrix[{-1/3, 3, 9, 9}]]
```

**A random non-diagonal curved metric of signature (2, 2):**

```wolfram
SeedRandom[42];
GammaMatrices[RandomCurvedMetric[2, 2]]
```

**Switch into the Weyl/chiral basis:**

```wolfram
ToWeylBasis @ GammaMatrices[FlatMetric[1, 3]]
```

**The canonical graded Clifford operator basis:**

```wolfram
CliffordBasis[FlatMetric[1, 3]]
```

The Clifford anticommutator, tracelessness, the squares of single γ's, the
trace of two and four γ's, the contraction identities, the commutator
identity, and chirality (in even dimension) are all verified across signatures
in [`DiracMatrix-Documentation.md`](DiracMatrix-Documentation.md).

## Public symbols

| Symbol                    | Purpose                                                                  |
|---------------------------|--------------------------------------------------------------------------|
| `GammaMatrices`           | γ matrices for an integer dim, a flat `(p,q)` metric, or a general `η`   |
| `EuclideanGammaMatrices`  | Brauer–Weyl Γ matrices in flat Euclidean space                           |
| `FlatMetric`              | Diagonal flat metric of signature `(p,q)`                                |
| `RandomCurvedMetric`      | Random real symmetric non-diagonal metric of signature `(p,q)`           |
| `MetricVielbein`          | Returns `{signature, e}` such that `eᵀ·signature·e = η`                  |
| `ToDiracBasis`            | Similarity transform into the Dirac basis (γ⁰ diagonal)                  |
| `ToWeylBasis`             | Similarity transform into the Weyl/chiral basis                          |
| `CliffordCanonicalBasis`  | Graded operator basis via explicit antisymmetrisation (pedagogical)      |
| `CliffordBasis`           | Graded operator basis via stable antisymmetric recursion (production)    |
| `NumericZeroQ`            | Tolerance-based zero test for numerical identity verification            |

## Calling from other languages

The package runs on a Wolfram kernel; the free
[**Wolfram Engine**](https://www.wolfram.com/engine/) is enough for development
and research use. Three practical bridges:

**Python — persistent session via [`wolframclient`](https://reference.wolfram.com/language/WolframClientForPython/):**

```python
from wolframclient.evaluation import WolframLanguageSession
from wolframclient.language import wl, wlexpr
import numpy as np

session = WolframLanguageSession()
session.evaluate(wlexpr('PacletDirectoryLoad["/path/to/DiracMatrixPackage"]'))
session.evaluate(wlexpr('Needs["DiracMatrix`"]'))

gammas = session.evaluate(
    wl.DiracMatrix.GammaMatrices(np.diag([-1.0, 1.0, 1.0, 1.0]))
)
# gammas: tuple of 4×4 NumPy arrays
session.terminate()
```

NumPy ↔ Wolfram packed arrays auto-convert in both directions.

**Julia** — [`MathLink.jl`](https://github.com/JuliaInterop/MathLink.jl) offers
the same persistent-kernel pattern over WSTP.

**One-shots from anywhere** — `wolframscript` (ships with Wolfram Engine):

```bash
wolframscript -code 'Needs["DiracMatrix`"]; \
  ExportString[GammaMatrices[FlatMetric[1, 3]], "JSON"]'
```

**HTTP from any language** — wrap in an `APIFunction` and `CloudDeploy` for a
language-agnostic endpoint.

Notes: the Wolfram Engine licence is free for development, not for commercial
production; kernel startup is the dominant cost, so keep one session alive
across calls.

## Documentation

Full mathematical background, examples across signatures and dimensions, and
verification of standard γ-matrix identities live in
[`DiracMatrix-Documentation.md`](DiracMatrix-Documentation.md) (rendered from
[`DiracMatrix-Documentation.nb`](DiracMatrix-Documentation.nb)).

## Related work

The Clifford / γ-matrix software landscape is well-developed. Existing packages
broadly fall into three design points, and `DiracMatrix` sits in the
least-populated of the three. Each tool below is excellent for its intended
use; the goal of this section is to help you pick the right one.

### Symbolic abstract-index engines (Mathematica)

These manipulate `γ^μ` as a formal object with Lorentz indices, applying
anticommutation, Fierz, and trace identities. They do not return matrix
entries; the user supplies an explicit representation only when needed.

- **[GammaMaP](https://github.com/PyryKuusela/GammaMaP)** ([Kuusela 2019, arXiv:1905.00429](https://arxiv.org/abs/1905.00429)) — the most modern
  and feature-rich. Spinor bilinears, intertwiners A/B/C, charge conjugation,
  Majorana/Weyl projections, Fierz, decomposition under SO(d₁)×…×SO(dₘ)
  subalgebras. Designed for SUGRA and string-theory book-keeping.
- **[GAMMA](https://arxiv.org/abs/hep-th/0105086)** (Gran 2001) — gamma-matrix
  algebra and Fierz transformations in arbitrary integer dimension.
- **[Tracer](https://library.wolfram.com/infocenter/ID/2987/)** (Jamin & Lautenbacher 1991) —
  γ-traces in arbitrary `D` (’t Hooft–Veltman scheme), aimed at QFT loop
  integrals.
- **[FeynCalc](https://feyncalc.github.io/)**'s `DiracMatrix` / `GA` — abstract
  Dirac objects for Feynman-diagram automation; flat Minkowski + dimensional
  regularisation only.
- **[Clifford Algebra with Mathematica](https://arxiv.org/abs/0810.2412)**
  (Aragón et al. 2008) — general-purpose Clifford manipulation in 3D and
  pedagogy.

### Multivector-based geometric algebra (Python, Julia)

These represent elements of `Cl(p,q)` or `Cl(p,q,r)` directly as multivectors
in a basis of grades, rather than as matrices. The Dirac γ's are the grade-1
basis vectors of the algebra; products and traces are computed in that
representation.

- **[`clifford`](https://github.com/pygae/clifford)** (pygae, Python) —
  numerical GA over arbitrary `Cl(p,q,r)` signatures. Multivectors as NumPy
  arrays. Strong tooling, used in computer-graphics, robotics, conformal GA.
- **[`galgebra`](https://github.com/pygae/galgebra)** (pygae, Python on SymPy) —
  *symbolic* GA with an **arbitrary symbolic metric tensor**, including
  position-dependent metrics for curved manifolds. The closest competitor in
  scope to `DiracMatrix` for the curved-metric use case, but works in
  multivector form, not matrix form.
- **[Grassmann.jl](https://github.com/chakravala/Grassmann.jl)** (Julia) —
  Grassmann–Clifford–Hodge algebra with `DiagonalForm` and `MetricTensor`
  (non-diagonal). High-dimensional, sparse-tensor backend.
- **[`sympy.physics.matrices.mgamma`](https://docs.sympy.org/latest/modules/physics/matrices.html)** —
  the standard 4×4 Dirac γ matrices in SymPy. Fixed dimension and basis;
  included for completeness.

### Explicit matrix realisations (where this package sits)

Given a metric, return the actual `2^⌊n/2⌋ × 2^⌊n/2⌋` matrices. This is the
representation you want when you need to plug `γ^μ` into a concrete
Hamiltonian, simulate a Dirac equation numerically, build a discrete
Bogoliubov–de Gennes operator, or check identities by direct computation.

To my knowledge, no other package combines, in this style:

1. arbitrary **real symmetric** metric (not just signed-diagonal `(p, q)`) via
   automatic vielbein decomposition,
2. the explicit Brauer–Weyl Pauli–Kronecker construction in any dimension,
3. similarity transforms into the Dirac and Weyl/chiral bases, and
4. the canonical graded antisymmetrised Clifford operator basis with both a
   pedagogical implementation and a numerically stable recursive one.

`galgebra` is the closest in scope but lives in the symbolic-multivector world;
`clifford` and `Grassmann.jl` are numerical but multivector-based and signature-
restricted (no automatic vielbein for an arbitrary curved metric).

### Which to pick

| Your goal                                                                | Use                       |
|--------------------------------------------------------------------------|---------------------------|
| Algebraic identities, Fierz, traces, SUGRA/string book-keeping in WL     | GammaMaP, FeynCalc        |
| QFT loop traces with dimensional regularisation                          | Tracer, FeynCalc          |
| GA in graphics / robotics / conformal models, Python                     | `clifford` (pygae)        |
| Symbolic GA with a position-dependent metric, Python                     | `galgebra`                |
| Multivector GA in Julia, high-dimensional                                | Grassmann.jl              |
| **Explicit γ matrices for a given (possibly curved, non-diagonal) metric** | **`DiracMatrix` (this package)** |
| Dirac/Weyl basis transforms or graded operator basis as concrete matrices | **`DiracMatrix`**         |

Corrections and additions are welcome — open an issue if a package belongs in
this list.
