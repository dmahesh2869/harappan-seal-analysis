# Harappan Seal Power-Law and Confirmation-Bundle Analysis

This repository reproduces the statistical analyses reported in the manuscript’s power-law and seal-authentication sections. The project uses Jamison’s published unicorn-seal typology to test whether offering-stand frequencies follow heavy-tailed distributions and whether stand identity is systematically associated with anatomical attributes in a confirmation protocol.

## Overview

The analysis is built around the empirical dataset described in the manuscript and uses the complete Appendix 7.1 attribute table as the canonical source for seal-level distribution fitting and association tests. The repository supports the following components of the study:

- Power-law fitting for all 11 seal attributes
- Formal comparison of the offering stand against exponential and alternative heavy-tailed models
- Global stand-attribute association tests via Cramér’s V
- Tiered confirmation-bundle analysis across the top 5, 10, and 15 stand types
- Diachronic robustness checks of the power-law pattern over the Harappan sequence

## Key findings from the manuscript

### Power-law structure

The strongest evidence for the offering stand comes from the complete Appendix 7.1 dataset:

| Attribute | Types | Seals | $\alpha$ | $x_{min}$ | $D$ | GoF $p$ | Interpretation |
|---|---:|---:|---:|---:|---:|---:|---|
| Stand | 139 | 413 | 2.3591 | 3.0 | 0.0514 | 0.9764 | Power law compatible |
| Ear | 52 | 438 | 2.4210 | 7.0 | 0.1035 | 0.4064 | Compatible |
| Neck | 72 | 458 | 2.5234 | 7.0 | 0.0925 | 0.4700 | Compatible |
| Hoof | 38 | 442 | 2.9396 | 13.0 | 0.0655 | 0.8936 | Compatible |
| Leg | 18 | 449 | 1.4175 | 1.0 | 0.0714 | 0.8808 | BHS-like drift regime |
| Tail | 25 | 351 | 1.6333 | 2.0 | 0.1125 | 0.5708 | BHS-like drift regime |
| Halter | 55 | 470 | 1.7537 | 2.0 | 0.0801 | 0.7452 | BHS-like drift regime |
| Pizzle | 20 | 436 | 1.7606 | 5.0 | 0.1287 | 0.5200 | BHS-like drift regime |
| Head | 39 | 431 | 1.8454 | 4.0 | 0.1016 | 0.5040 | BHS-like drift regime |

The offering stand is the clearest commercial signal in the analysis: its power-law fit is the strongest and most stable, with the highest GoF statistic in this run. The manuscript explicitly notes that the exponential model is rejected for the complete dataset ($p_{GoF} < 0.001$), while the lognormal, stretched exponential, and truncated power-law alternatives do not significantly outperform the power-law model.

### Cramér’s V confirmation bundle

The manuscript tests whether stand identity is systematically associated with anatomical attributes. The global results are:

| Attribute | $n$ | Cramér’s V | $p_{perm}$ | Status |
|---|---:|---:|---:|---|
| LEG | 402 | 0.484 | < 0.001 | Significant |
| HALTER | 407 | 0.431 | < 0.001 | Significant |
| PIZZLE | 383 | 0.365 | 0.001 | Significant |
| TAIL | 309 | 0.340 | 0.0038 | Significant |
| HOOF | 393 | 0.337 | 0.0004 | Significant |
| HEAD | 388 | 0.330 | 0.0008 | Significant |
| EAR | 386 | 0.307 | 0.0002 | Significant |
| NECK | 401 | 0.303 | 0.0008 | Significant |
| HORN | 389 | 0.294 | 0.0538 | Weak |
| EYE | 379 | 0.221 | 0.0656 | Weak |

Across the top 5, 10, and 15 stand tiers, the strongest confirmation bundle is NECK, HALTER, and EAR, with the following mean associations:

- NECK: mean $V = 0.437$
- HALTER: mean $V = 0.425$
- EAR: mean $V = 0.362$

The manuscript interprets this as evidence for a scalable visual confirmation protocol in which seal readers rely on a limited set of diagnostic attribute bundles rather than full literacy or script-based verification.

## Data availability

The manuscript’s Data Availability statement is as follows:

> All code, data, and reproducibility documentation are openly available in the GitHub repository: https://github.com/dmahesh2869/harappan-seal-analysis
>
> The repository is organized in three layers:
> - Core reproducibility pipeline: primary scripts, validation checks, and run instructions needed to regenerate the manuscript’s main statistical results, tables, and figures.
> - Supplementary analyses: additional scripts used for robustness checks and exploratory diagnostics (e.g., stand hierarchy, bundle consistency, singleton dispersion, and diachronic analyses).
> - Versioned outputs: generated CSV, TXT, and PNG artifacts used to audit and verify claims in the manuscript.
>
> All analyses are deterministic and reproducible in Python 3.8+ with powerlaw (v2.0.0).

This repository follows that structure and is intended to support reproducible regeneration of the paper’s main claims.

## Repository layout

The project is organized into three main layers:

1. Core reproducibility pipeline
   - Primary scripts for power-law fitting, Cramér’s V analysis, and manuscript figures
   - Validation and data-cleaning routines
2. Supplementary analyses
   - Stand hierarchy, bundle consistency, singleton dispersion, and diachronic analyses
3. Versioned outputs
   - CSV, TXT, and PNG artifacts used to check and verify the paper results

## Main analysis scripts

The current repository includes scripts that correspond to the manuscript’s analytical workflow, including but not limited to:

- `analyze_appendix71.py` — complete-dataset power-law fitting for offering stands and other attributes
- `analyze_seal_attributes.py` — attribute-level distribution analysis
- `analyze_attribute_hierarchy_by_stand_tier.py` — tiered Cramér’s V analysis across stand groups
- `analyze_stand_attribute_correlation.py` — global stand-attribute association tests
- `diachronic_analysis.py` — diachronic power-law checks across periods
- `compare_attribute_analysis.py` — comparative summaries across attributes

Scripts are intended to be run from the repository root in a Python 3.8+ environment.

## Environment and dependencies

### Requirements

- Python 3.8+
- NumPy
- SciPy
- Matplotlib
- powerlaw 2.0.0

### Installation

```bash
python -m venv .venv
. .venv/bin/activate
pip install numpy scipy matplotlib powerlaw
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install numpy scipy matplotlib powerlaw
```

## Reproducibility notes

- The manuscript’s power-law tests use the `powerlaw` package with maximum-likelihood estimation and bootstrap goodness-of-fit testing.
- The correlation analyses compute Cramér’s V with pairwise deletion for missing values and apply Bonferroni correction for multiple comparisons.
- The reported threshold for power-law plausibility is $p > 0.10$.
- Statistical significance for confirmation-bundle tests uses a corrected threshold of $\alpha = 0.005$ for the tiered analysis and $\alpha = 0.005$ with 10 attributes for the global tests.

## Key references

- Clauset, A., Shalizi, C. R., and Newman, M. E. J. (2009). Power-law distributions in empirical data. SIAM Review, 51(4), 661–703.
- Jamison, G. M. (2017). The Organization of Indus Unicorn Seal Production. University of Wisconsin–Madison dissertation.
- Alstott, J., Bullmore, E., and Plenz, D. (2014). powerlaw: A Python package for analysis of heavy-tailed distributions. PLoS ONE, 9(4), e85777.

## Summary

This repository is the computational companion to the manuscript’s argument that Harappan seal variation is structured by heavy-tailed statistical processes and a scalable visual confirmation system. The key evidence is the strong power-law fit for the offering stand and the persistent, stand-dependent Cramér’s V associations that identify the core confirmation bundle.

## License

This code and analysis are provided for academic and reproducibility purposes.

---

**Analysis Date:** April 2026  
**Reproducible:** Yes (all code included, data deterministic with seed control)
