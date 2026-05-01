# DiracMatrix

A Wolfram Language paclet that **constructs** Dirac gamma matrices for an
arbitrary real symmetric metric in any dimension. Given a metric `η`, it returns
the literal `2^Floor[n/2] × 2^Floor[n/2]` matrices satisfying the Clifford
relation

$$
\{\gamma^{\mu},\gamma^{\nu}\} \;=\; 2\,\eta^{\mu\nu}\,\mathbb{I}.
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

## Documentation

Full mathematical background, examples across signatures and dimensions, and
verification of standard γ-matrix identities live in
[`DiracMatrix-Documentation.md`](DiracMatrix-Documentation.md) (rendered from
[`DiracMatrix-Documentation.nb`](DiracMatrix-Documentation.nb)).
