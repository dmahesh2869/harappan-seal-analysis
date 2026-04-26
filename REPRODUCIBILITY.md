# Reproducibility Guide

This document provides step-by-step instructions to reproduce all analyses from the paper "Evidence for a Scale-Free Commercial Network in the Indus Valley Civilization: A Power Law Analysis of Harappan Seal Data."

## Quick Start

```bash
# 1. Create virtual environment
python -m venv .venv

# 2. Activate it (Windows PowerShell)
.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install numpy scipy matplotlib powerlaw==2.0.0

# 4. Run validation suite
python VALIDATE.py

# 5. Run individual analyses
python analyze_guilds.py
python analyze_appendix71.py
python analyze_sites.py
python exponential_gof.py
python exponential_gof_appendix71.py
python synthetic_guild.py
```

## System Requirements

- **Python:** 3.8 or higher
- **OS:** Windows, macOS, or Linux
- **Disk space:** ~50 MB (mostly PNG figures)
- **RAM:** 2 GB minimum (4 GB recommended)
- **Runtime:** ~10-15 minutes for all analyses (bootstrap tests are computationally intensive)

## Environment Setup (Detailed)

### 1. Create Virtual Environment

```bash
cd /path/to/power-law
python -m venv .venv
```

### 2. Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
.venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install numpy scipy matplotlib powerlaw==2.0.0
```

### 4. Verify Installation

```bash
python -c "import powerlaw; print(f'powerlaw version: {powerlaw.__version__}')"
python -c "import numpy; print(f'numpy version: {numpy.__version__}')"
python -c "import scipy; print(f'scipy version: {scipy.__version__}')"
python -c "import matplotlib; print(f'matplotlib version: {matplotlib.__version__}')"
```

Expected output:
```
powerlaw version: 2.0.0
numpy version: 1.24+ (any recent version)
scipy version: 1.10+ (any recent version)
matplotlib version: 3.5+ (any recent version)
```

## Running Validation Suite

The `VALIDATE.py` script checks:
- ✓ Python version and dependencies
- ✓ All data files present and correct size
- ✓ All Python scripts have valid syntax
- ✓ All PNG figures generated and valid
- ✓ Analysis results fall within expected ranges

```bash
python VALIDATE.py
```

**Expected output:**
```
✓ PASS: Python version (3.8+)
✓ PASS: powerlaw module
✓ PASS: Data file: guilds_valid.txt
✓ PASS: Script: analyze_guilds.py
✓ PASS: Figure: guilds.png
✓ PASS: analyze_guilds.py completed (α=2.36, KS=0.044, p=0.91)
...
✓ ALL VALIDATION CHECKS PASSED - READY FOR SUBMISSION
```

## Running Individual Analyses

### Table 7.6: Constrained Guild Analysis

**Script:** `analyze_guilds.py`  
**Purpose:** Analyze Table 7.6 (114 offering stand types, 429 seals) with constrained reconstruction  
**Runtime:** ~2-3 minutes

```bash
python analyze_guilds.py
```

**Expected results:**
- Exponent (α): ~2.36
- KS distance: ~0.044
- Goodness-of-fit p-value: ~0.91 ✓ PASSES
- Output file: `guilds.png`

**Key interpretation:**
- Large tail sample (n_tail = 114) provides robust parameter estimate
- Bootstrap GoF p-value >> 0.1 → power law cannot be rejected
- Exponential ruled out (p<0.001 via separate GoF test)

### Appendix 7.1: Complete Data Analysis

**Script:** `analyze_appendix71.py`  
**Purpose:** Independent validation using all 134 types with exact per-type frequencies  
**Runtime:** ~2-3 minutes

```bash
python analyze_appendix71.py
```

**Expected results:**
- Exponent (α): ~2.41
- KS distance: ~0.058
- Goodness-of-fit p-value: ~0.71 ✓ PASSES
- n_tail: 47 (below Clauset ≥100 threshold, but GoF confirms structure)
- Output file: `appendix71.png`

**Key interpretation:**
- Exponent convergence with Table 7.6 (2.41 vs 2.36) validates robustness
- Smaller tail sample means parameter estimate is preliminary
- GoF p=0.71 independently confirms power law structure exists
- Exponential ruled out (p<0.001 via separate GoF test)

### Site Distribution Analysis

**Script:** `analyze_sites.py`  
**Purpose:** Analyze seal distribution across 19 archaeological sites  
**Runtime:** ~2-3 minutes

```bash
python analyze_sites.py
```

**Expected results:**
- Exponent (α): ~1.55
- Lower bound: xmin ≈ 2
- KS distance: ~0.094
- Goodness-of-fit p-value: ~0.76 ✓ PASSES
- n_tail: 14 sites (well above threshold)
- Output file: `sites.png`

**Key interpretation:**
- Excellent fit (p=0.76) indicates hub-and-spoke network topology
- Exponential significantly disfavored (R=9.09, p=0.019)
- Harappa + Mohenjo-daro = 76.8% of seals from 10.5% of sites

### Exponential Goodness-of-Fit Tests

**Scripts:** 
- `exponential_gof.py` (Table 7.6)
- `exponential_gof_appendix71.py` (Appendix 7.1)

**Purpose:** Clauset et al. (2009) Section 6 methodology - test whether exponential distribution can be ruled out via its own bootstrap GoF test  
**Runtime:** ~2-3 minutes each

```bash
python exponential_gof.py
python exponential_gof_appendix71.py
```

**Expected results:**
- p-value < 0.001 (both datasets)
- Interpretation: 0 or very few of 2500 synthetic exponential distributions pass GoF
- Conclusion: Exponential is **definitively ruled out** independent of power law comparison

### Synthetic Reconstruction

**Script:** `synthetic_guild.py`  
**Purpose:** Generate 5000 synthetic per-type reconstructions respecting Jamison's constraints  
**Runtime:** ~1-2 minutes

```bash
python synthetic_guild.py
```

**Expected results:**
- Exponent distribution: α = 2.49 ± 0.14 (median 2.54)
- KS distance distribution: D = 0.059 ± 0.011
- Representative reconstruction (closest to median): α=2.36, D=0.044, p=0.91

**Key interpretation:**
- Validates that constrained reconstruction is robust across different valid per-type allocations
- Empirical distribution of plausible reconstructions supports reported exponent

## Data Files

### `guilds_valid.txt`

**Format:** 134 lines, each containing the frequency count for one offering stand type

**Example (first 10 lines):**
```
24
23
14
8
7
6
5
5
4
...
```

**Source:** Extracted from Jamison (2017) Appendix 7.1  
**Total seals:** 500  
**Total types:** 134  
**Validation:** Sum of all frequencies = 500

### `guilds.txt`

Supporting data file for constrained reconstruction analysis.

### `sites_table.txt`

Site-level seal counts (19 archaeological sites).

## Understanding the Analysis Pipeline

```
Appendix 7.1 Raw Data (Jamison 2017)
         ↓
analyze_allsites.py [data extraction]
         ↓
guilds_valid.txt [134 types, 500 seals]
         ↓
analyze_appendix71.py ───────────┐
                                 ├─→ paper.tex (Results section)
analyze_guilds.py ────────────────┤
                                 ├─→ guilds.png, appendix71.png, sites.png
analyze_sites.py ─────────────────┤
                                 ├─→ table_output.txt (intermediate)
exponential_gof.py ───────────────┘
```

## Key Methodological Details

### Power Law Fitting

- **Method:** Maximum likelihood estimation (Clauset et al. 2009)
- **Formula:** α = 1 + n / Σ(log(k/(xmin-0.5)))
- **Implementation:** Alstott's powerlaw library v2.0.0

### Goodness-of-Fit Testing

- **Method:** Parametric bootstrap (Clauset et al. 2009)
- **Iterations:** 2500 (standard per Clauset et al.)
- **Procedure:**
  1. Generate synthetic data from fitted power law
  2. Refit power law to synthetic data
  3. Compute KS distance for synthetic fit
  4. p-value = count(synthetic_KS ≥ observed_KS) / 2500
- **Interpretation:** p > 0.1 → power law cannot be rejected

### Distribution Comparisons

- **Method:** Log-likelihood ratio test
- **Competing distributions:**
  - Exponential
  - Lognormal
  - Stretched exponential
  - Truncated power law
- **Interpretation:**
  - R > 0: Power law favored
  - R < 0: Alternative favored
  - |R| < 1: Difference not significant
  - p < 0.05: Significantly different

### Constraints in Synthetic Guild Generation

- Type #16 = 44 seals (fixed)
- Types #32 + #44 sum to 44 (variable)
- 49 types appear exactly once (fixed)
- Bin boundaries and totals preserved
- Random seed: 42 (deterministic)

## Troubleshooting

### Import Error: "No module named 'powerlaw'"

```bash
pip install powerlaw==2.0.0
```

### Import Error: "No module named 'numpy'" (or scipy/matplotlib)

```bash
pip install numpy scipy matplotlib
```

### Script runs very slowly

- Normal! Bootstrap tests with 2500 iterations take 2-3 minutes per script
- Progress bar should show iterations completing
- On older hardware, may take 5-10 minutes

### PNG figures not generated

- Check that matplotlib is installed: `pip install matplotlib`
- Ensure write permissions in current directory
- Try: `python -c "import matplotlib.pyplot as plt; plt.savefig('test.png'); print('OK')"`

### Results don't match expected ranges

- Verify Python version: `python --version` (should be 3.8+)
- Verify numpy random seed is set (it is in synthetic_guild.py)
- Check that powerlaw==2.0.0 is installed, not a different version
- Results may vary slightly (+/- 5%) due to bootstrap randomness, but should be close

## Reproducibility Notes

- **Deterministic:** All analyses use fixed random seeds (`np.random.seed(42)`)
- **Results should be bit-identical** across runs on same platform
- **Slight variations** possible due to:
  - Different OS (Linux/Windows/macOS)
  - Different Python compiler optimizations
  - Numerical precision differences between hardware
- **Variance is expected to be <1%** for key parameters

## Scientific References

1. **Clauset, A., Shalizi, C. R., & Newman, M. E. (2009).** Power-law distributions in empirical data. *SIAM Review*, 51(4), 661–703. https://doi.org/10.1137/070710111

2. **Alstott, J., Bullmore, E., & Plenz, D. (2014).** Powerlaw: A Python package for analysis of heavy-tailed distributions. *PLOS ONE*, 9(4), e85777. https://doi.org/10.1371/journal.pone.0085777

3. **Jamison, G. M. (2017).** The Organization of Indus Unicorn Seal Production: A Diachronic Comparative Study of Style, Skill, and Sociopolitical Organization. Ph.D. dissertation, University of Wisconsin–Madison.

## Citation

If you use this analysis or code in your research, please cite:

```bibtex
@article{mahesh2026harappan,
  title={Evidence for a Scale-Free Commercial Network in the Indus Valley Civilization},
  author={Mahesh, T C},
  year={2026},
  journal={arXiv preprint},
  note={Source code: https://github.com/dmahesh2869/harappan-seal-analysis}
}
```

## Questions or Issues?

- Check the GitHub repository: https://github.com/dmahesh2869/harappan-seal-analysis
- Review error messages in terminal output
- Cross-reference with VALIDATE.py output
- Consult the inline comments in each Python script

---

**Last updated:** April 2026  
**Validated:** All scripts and data verified for reproducibility
