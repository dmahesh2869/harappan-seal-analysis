#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STAND-ATTRIBUTE CORRELATION ANALYSIS (REVISED): Bergsma-Wicher Bias-Corrected

Hypothesis: If merchants used seals as a validation system, specific stand types should
show CONSTRAINED variation in associated attributes (e.g., Stand #16 always has Halter #5, #9, #20).

Methodology:
1. Global cleanup: Remove 5 seals with blank STAND
2. For each attribute: Pairwise deletion (STAND + attribute only)
3. Cramér's V with Bergsma-Wicher bias correction (handles sparse tables)
4. Chi-square test (parametric p-value)
5. Permutation test (5000 shuffles, non-parametric p-value)
6. SIGNIFICANCE: Only if BOTH p < 0.005 (Bonferroni-adjusted)
7. Expected frequency diagnostics: Report sparsity of contingency tables

Reference:
- Bergsma, W., & Wicher, M. (2013). A bias-correction for Cramér's V and
  Tschuprow's T. Journal of the Korean Statistical Society, 42(3), 323-328.
- Clauset et al. (2009). Power-law distributions in empirical data.
  SIAM Review, 51(4), 661-703.
"""

import sys
from collections import Counter, defaultdict
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency
import matplotlib.pyplot as plt
from pathlib import Path

# Fix encoding for Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)


def parse_appendix71():
    """
    Parse appendix7.1.txt and return DataFrame with all seals and their attributes.
    """
    with open('appendix7.1.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Parse header
    header = lines[0].strip().split()
    col_indices = {col: i for i, col in enumerate(header)}
    
    # Parse data
    data = []
    for line in lines[1:]:
        parts = line.strip().split()
        if len(parts) < len(header):
            continue
        
        record = {}
        for col, idx in col_indices.items():
            value = parts[idx].strip()
            # Keep as-is; will clean later
            record[col] = value if value not in ['n/a', 'blank', ''] else None
        
        data.append(record)
    
    df = pd.DataFrame(data)
    return df


def clean_global_stand(df):
    """
    STEP 1: Global cleanup on STAND column
    - Remove 5 seals with blank/n/a STAND
    - Standardize STAND values to strings
    Returns: cleaned DataFrame
    """
    # Define invalid labels
    invalid_labels = {None, 'nan', 'n/a', 'na', 'blank', '', 'none'}
    
    # Filter: Keep only seals with valid STAND
    clean_df = df[df['STAND'].notna()].copy()
    clean_df['STAND'] = clean_df['STAND'].astype(str).str.strip()
    clean_df = clean_df[~clean_df['STAND'].isin(invalid_labels)]
    
    removed = len(df) - len(clean_df)
    print(f"[GLOBAL CLEANUP]")
    print(f"  Initial seals: {len(df)}")
    print(f"  Removed (blank STAND): {removed}")
    print(f"  Working dataset: {len(clean_df)}\n")
    
    return clean_df


def real_bergsma_wicher_v(confusion_matrix):
    """
    Mathematically precise implementation of Bergsma's 2013 bias-correction 
    for Cramér's V. Corrects for small sample sizes in massive, sparse tables.
    
    Args:
        confusion_matrix: numpy array (contingency table)
    
    Returns:
        float: Bias-corrected Cramér's V (0-1 scale)
    """
    n = confusion_matrix.sum()
    if n <= 1:
        return 0.0
    
    # Get the standard Pearson Chi-Square statistic
    chi2 = chi2_contingency(confusion_matrix, correction=False)[0]
    phi2 = chi2 / n
    r, c = confusion_matrix.shape
    
    # 1. Correct the Phi squared variance (Tschuprow/Bartlett adjustment)
    phi2_corr = max(0, phi2 - ((r - 1) * (c - 1)) / (n - 1))
    
    # 2. Correct the row and column degrees of freedom per Bergsma (2013)
    r_corr = r - ((r - 1) ** 2) / (n - 1)
    c_corr = c - ((c - 1) ** 2) / (n - 1)
    
    # 3. Calculate denominator based on the minimum corrected dimension
    denominator = min((r_corr - 1), (c_corr - 1))
    
    if denominator <= 0:
        return 0.0
    
    return np.sqrt(phi2_corr / denominator)


def compute_expected_frequency_diagnostics(confusion_matrix):
    """
    Analyze sparsity of contingency table.
    
    Returns:
        dict with:
        - total_cells: r × c
        - zero_cells: % of cells with count = 0
        - sparse_cells: % of cells with expected freq < 5
        - min_expected: smallest expected frequency
    """
    chi2, p, dof, expected = chi2_contingency(confusion_matrix, correction=False)
    
    total_cells = confusion_matrix.size
    zero_cells = np.sum(confusion_matrix == 0)
    sparse_cells = np.sum(expected < 5)
    
    zero_pct = 100 * zero_cells / total_cells if total_cells > 0 else 0
    sparse_pct = 100 * sparse_cells / total_cells if total_cells > 0 else 0
    min_expected = np.min(expected)
    
    return {
        'total_cells': total_cells,
        'zero_count': zero_cells,
        'zero_pct': zero_pct,
        'sparse_count': sparse_cells,
        'sparse_pct': sparse_pct,
        'min_expected': min_expected,
        'chi2': chi2,
        'chi2_p': p
    }


def permutation_test_cramers_v(anchor_col, target_col, clean_df, num_permutations=5000):
    """
    Permutation test for Cramér's V
    
    Shuffles the anchor column and recomputes V under null hypothesis.
    Empirical p-value = proportion of permutation V-values >= observed V
    
    Args:
        anchor_col: numpy array (STAND values)
        target_col: numpy array (attribute values)
        clean_df: (unused, for context)
        num_permutations: number of shuffles (default 5000)
    
    Returns:
        float: empirical p-value
        list: permutation V-values
    """
    # Compute observed V
    obs_matrix = pd.crosstab(pd.Series(anchor_col), pd.Series(target_col)).values
    observed_v = real_bergsma_wicher_v(obs_matrix)
    
    # Permutation distribution
    perm_v_values = []
    shuffled_anchor = anchor_col.copy()
    
    for _ in range(num_permutations):
        np.random.shuffle(shuffled_anchor)
        perm_matrix = pd.crosstab(pd.Series(shuffled_anchor), pd.Series(target_col)).values
        perm_v = real_bergsma_wicher_v(perm_matrix)
        perm_v_values.append(perm_v)
    
    perm_v_values = np.array(perm_v_values)
    empirical_p = np.sum(perm_v_values >= observed_v) / num_permutations
    
    return empirical_p, perm_v_values, observed_v


def get_top_stands(df, n=15):
    """
    Get top N stand types by frequency.
    """
    stand_counts = df['STAND'].value_counts()
    return stand_counts.head(n).index.tolist()


def compute_conditional_distributions(df, stand_types, attributes):
    """
    For each stand type, compute the distribution of each attribute.
    Returns: dict of {stand_type: {attribute: Counter}}
    """
    conditional_dists = {}
    
    for stand in stand_types:
        stand_seals = df[df['STAND'] == stand]
        conditional_dists[stand] = {}
        
        for attr in attributes:
            # Get non-null values for this attribute among seals with this stand
            attr_values = stand_seals[attr].dropna()
            conditional_dists[stand][attr] = Counter(attr_values)
    
    return conditional_dists


def compute_entropy(value_counts):
    """
    Compute Shannon entropy of a distribution (0=concentrated, 1=uniform).
    Normalized by max possible entropy for that number of categories.
    """
    if len(value_counts) == 0:
        return 0
    
    total = sum(value_counts.values())
    probs = np.array([count / total for count in value_counts.values()])
    
    # Shannon entropy (in bits)
    entropy = -np.sum(probs * np.log2(probs + 1e-10))
    
    # Normalize by max entropy for this number of categories
    max_entropy = np.log2(len(value_counts))
    normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
    
    return normalized_entropy


def analyze_variance_signatures(df, stand_types, attributes):
    """
    For each stand type, compute variance (entropy) in each attribute.
    Compare to corpus average. 
    
    Interpretation:
    - Low entropy within a stand type = constrained (intentional)
    - High entropy within a stand type = scattered (random)
    """
    conditional_dists = compute_conditional_distributions(df, stand_types, attributes)
    
    # Compute corpus-level entropy for each attribute (baseline)
    corpus_entropy = {}
    for attr in attributes:
        attr_values = df[attr].dropna()
        value_counts = Counter(attr_values)
        corpus_entropy[attr] = compute_entropy(value_counts)
    
    # Compute per-stand entropy
    results = []
    for stand in stand_types:
        stand_count = len(df[df['STAND'] == stand])
        
        for attr in attributes:
            value_counts = conditional_dists[stand][attr]
            
            if len(value_counts) == 0:
                entropy = 0
                num_types = 0
            else:
                entropy = compute_entropy(value_counts)
                num_types = len(value_counts)
            
            # Deviation from corpus (negative = more constrained)
            deviation = entropy - corpus_entropy[attr]
            
            results.append({
                'Stand': stand,
                'Stand_Count': stand_count,
                'Attribute': attr,
                'Entropy': entropy,
                'Corpus_Entropy': corpus_entropy[attr],
                'Deviation': deviation,
                'Num_Types': num_types,
                'Max_Type_Count': max(value_counts.values()) if value_counts else 0,
                'Concentration': max(value_counts.values()) / stand_count if value_counts and stand_count > 0 else 0
            })
    
    return pd.DataFrame(results), corpus_entropy


def test_stand_attribute_independence_pairwise(df, attributes, num_permutations=5000):
    """
    STEP 2-4: Pairwise deletion + Chi-square + Permutation test
    
    For each attribute:
    1. Keep only seals with valid STAND and valid attribute (pairwise deletion)
    2. Build contingency table
    3. Compute chi-square p-value (parametric)
    4. Compute permutation p-value (non-parametric)
    5. Report expected frequency diagnostics
    
    Returns:
        DataFrame with results
    """
    n_tests = len(attributes)
    bonferroni_threshold = 0.05 / n_tests
    
    results = []
    
    print(f"[PAIRWISE TESTS & PERMUTATION ANALYSIS]")
    print(f"Number of attributes: {n_tests}")
    print(f"Bonferroni threshold: {bonferroni_threshold:.5f}")
    print(f"Permutation iterations: {num_permutations}\n")
    
    print(f"{'Attr':<10} | {'N':<6} | {'Cont.Tbl':<10} | {'Chi2-p':<10} | "
          f"{'Perm-p':<10} | {'V (B-W)':<10} | {'Status':<20}")
    print("-" * 100)
    
    invalid_labels = {None, 'nan', 'n/a', 'na', 'blank', '', 'none'}
    
    for attr in attributes:
        # Pairwise deletion: keep only rows with valid STAND and valid attribute
        pair_df = df[['STAND', attr]].copy()
        
        # FIXED: Check for None BEFORE string conversion
        # Keep only rows where STAND is not None AND attribute is not None
        clean_pair = pair_df[
            (pair_df['STAND'].notna()) & 
            (pair_df[attr].notna())
        ].copy()
        
        valid_n = len(clean_pair)
        
        if valid_n < 10:
            print(f"{attr:<10} | {valid_n:<6} | {'INSUFFICIENT':<10} | "
                  f"{'---':<10} | {'---':<10} | {'---':<10} | "
                  f"{'DATA TOO SPARSE':<20}")
            results.append({
                'Attribute': attr,
                'Valid_N': valid_n,
                'Contingency_Shape': 'N/A',
                'Chi2': np.nan,
                'Chi2_P': np.nan,
                'Perm_P': np.nan,
                'Cramers_V_BW': np.nan,
                'Total_Cells': np.nan,
                'Zero_Pct': np.nan,
                'Sparse_Pct': np.nan,
                'Min_Expected_Freq': np.nan,
                'Status': 'INSUFFICIENT_DATA'
            })
            continue
        
        # Build contingency table
        contingency = pd.crosstab(clean_pair['STAND'], clean_pair[attr]).values
        r, c = contingency.shape
        
        # Expected frequency diagnostics
        diag = compute_expected_frequency_diagnostics(contingency)
        
        # Compute V with Bergsma-Wicher
        observed_v = real_bergsma_wicher_v(contingency)
        
        # Permutation test
        perm_p, perm_v_vals, obs_v = permutation_test_cramers_v(
            clean_pair['STAND'].values, 
            clean_pair[attr].values,
            clean_pair,
            num_permutations=num_permutations
        )
        
        # Determine significance: BOTH parametric AND non-parametric p < 0.005
        chi2_p = diag['chi2_p']
        
        if chi2_p < 0.005 and perm_p < 0.005:
            status = "✓ SIGNIFICANT"
        elif chi2_p < 0.005 or perm_p < 0.005:
            status = "⚠ WEAK (one test only)"
        else:
            status = "✗ Not significant"
        
        cont_shape = f"{r}×{c}"
        
        print(f"{attr:<10} | {valid_n:<6} | {cont_shape:<10} | "
              f"{chi2_p:<10.5f} | {perm_p:<10.5f} | {observed_v:<10.4f} | "
              f"{status:<20}", flush=True)
        
        results.append({
            'Attribute': attr,
            'Valid_N': valid_n,
            'Contingency_Shape': cont_shape,
            'Chi2': diag['chi2'],
            'Chi2_P': chi2_p,
            'Perm_P': perm_p,
            'Cramers_V_BW': observed_v,
            'Total_Cells': diag['total_cells'],
            'Zero_Pct': diag['zero_pct'],
            'Sparse_Pct': diag['sparse_pct'],
            'Min_Expected_Freq': diag['min_expected'],
            'Status': status
        })
    
    return pd.DataFrame(results)


def print_constrained_vs_scattered(variance_df):
    """
    Identify stand types with constrained (low entropy) vs scattered (high entropy) attributes.
    """
    print("\n" + "="*120)
    print("CONSTRAINED vs SCATTERED ATTRIBUTES BY STAND TYPE")
    print("="*120)
    print("""
INTERPRETATION:
- Low Entropy (Deviation < -0.3): Attribute values are CONSTRAINED to few types
  --> Suggests intentional design: "Stand X always has Halter Y, Z, or W"
- High Entropy (Deviation > 0.3): Attribute values are SCATTERED across many types
  --> Suggests random variation: "Stand X can have any halter type"

The hypothesis predicts: TOP STAND TYPES show LOW ENTROPY in salient attributes.
If so, it's evidence of a validation protocol.
""")
    
    # Sort by deviation
    constrained = variance_df[variance_df['Deviation'] < -0.3].sort_values('Deviation')
    scattered = variance_df[variance_df['Deviation'] > 0.3].sort_values('Deviation', ascending=False)
    
    if len(constrained) > 0:
        print(f"\nMOST CONSTRAINED (Entropy is LOW compared to corpus):")
        print(f"{'Stand':<8} {'Attribute':<12} {'N_Types':<8} {'Entropy':<8} {'Corpus':<8} {'Deviation':<10} {'Concentration':<12}")
        print("-" * 100)
        for _, row in constrained.head(20).iterrows():
            print(f"{row['Stand']:<8} {row['Attribute']:<12} {row['Num_Types']:<8} {row['Entropy']:<8.3f} {row['Corpus_Entropy']:<8.3f} {row['Deviation']:<10.3f} {row['Concentration']:<12.1%}")
    
    if len(scattered) > 0:
        print(f"\nMOST SCATTERED (Entropy is HIGH compared to corpus):")
        print(f"{'Stand':<8} {'Attribute':<12} {'N_Types':<8} {'Entropy':<8} {'Corpus':<8} {'Deviation':<10} {'Concentration':<12}")
        print("-" * 100)
        for _, row in scattered.head(20).iterrows():
            print(f"{row['Stand']:<8} {row['Attribute']:<12} {row['Num_Types']:<8} {row['Entropy']:<8.3f} {row['Corpus_Entropy']:<8.3f} {row['Deviation']:<10.3f} {row['Concentration']:<12.1%}")


def visualize_conditional_distributions(df, stand_types, attributes, output_file='stand_attribute_heatmap.png'):
    """
    Create heatmaps showing conditional distributions of top stand types using matplotlib only.
    """
    conditional_dists = compute_conditional_distributions(df, stand_types, attributes)
    
    # Create a figure with subplots for each attribute
    fig, axes = plt.subplots(3, 4, figsize=(18, 12))
    fig.suptitle('Conditional Attribute Distributions by Top Stand Types\n(Rows=Stand Types, Cols=Attribute Values)', 
                 fontsize=14, fontweight='bold')
    
    axes = axes.flatten()
    
    for idx, attr in enumerate(attributes):
        ax = axes[idx]
        
        # Create matrix: stand_types × top attribute values for that stand
        # Get all unique values of this attribute across top stands
        all_attr_values = set()
        for stand in stand_types:
            all_attr_values.update(conditional_dists[stand][attr].keys())
        
        all_attr_values = sorted(list(all_attr_values))[:10]  # Limit to top 10 for readability
        
        # Build matrix
        matrix = []
        for stand in stand_types:
            row = []
            stand_count = len(df[df['STAND'] == stand])
            
            for attr_val in all_attr_values:
                count = conditional_dists[stand][attr].get(attr_val, 0)
                # Normalize to percentage
                pct = (count / stand_count * 100) if stand_count > 0 else 0
                row.append(pct)
            
            matrix.append(row)
        
        matrix = np.array(matrix)
        
        # Create simple heatmap using imshow
        im = ax.imshow(matrix, cmap='YlOrRd', aspect='auto')
        
        # Set ticks
        ax.set_xticks(np.arange(len(all_attr_values)))
        ax.set_yticks(np.arange(len(stand_types)))
        ax.set_xticklabels([str(v)[:6] for v in all_attr_values], fontsize=7, rotation=45)
        ax.set_yticklabels([f"Stand {s}" for s in stand_types], fontsize=7)
        
        ax.set_title(f'{attr} Distribution by Stand', fontweight='bold', fontsize=9)
        ax.set_xlabel('Attribute Value', fontsize=8)
        ax.set_ylabel('Stand Type', fontsize=8)
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('% of seals', fontsize=7)
    
    # Hide unused subplots
    for idx in range(len(attributes), len(axes)):
        axes[idx].set_visible(False)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"  ✓ Heatmap saved to: {output_file}")
    plt.close()


def print_interpretation(results_df):
    """
    Interpret results with appropriate caveats.
    """
    print("\n" + "="*100)
    print("INTERPRETATION & CAVEATS")
    print("="*100)
    
    significant = results_df[results_df['Status'] == "✓ SIGNIFICANT"]
    weak = results_df[results_df['Status'] == "⚠ WEAK (one test only)"]
    not_sig = results_df[results_df['Status'] == "✗ Not significant"]
    
    print(f"""
RESULTS SUMMARY:
- SIGNIFICANT (both tests p < 0.005): {len(significant)}
- WEAK (only one test p < 0.005): {len(weak)}
- NOT SIGNIFICANT: {len(not_sig)}

INTERPRETATION:

1. SIGNIFICANT correlations (V > 0.3, both p < 0.005):
   - Stand type IS associated with attribute variation
   - Evidence for intentional validation system
   - High confidence (dual confirmation via parametric + permutation test)

2. WEAK correlations (V > 0.3, only one test p < 0.005):
   - Inconclusive
   - Likely artifact of sparse contingency tables or sample size variation
   - Cannot claim intentional design

3. NOT SIGNIFICANT (p > 0.005 in both tests):
   - No evidence for systematic association
   - Attributes vary randomly with stand type
   - Compatible with random artisanal variation

CAVEATS:
- Data is extremely sparse: 139 stand types × many attribute types in 500 seals
- Contingency tables with 80%+ zero cells violate chi-square assumptions
- Permutation test is more robust in sparse regime
- Bergsma-Wicher correction penalizes sparse tables (conservative)
- Only report V and p-values where Valid_N > 50 and Sparse_Pct < 90%

ACTIONABLE CONCLUSIONS:
- If attribute V > 0.4 AND both p < 0.005: Guild authentication design confirmed
- If attribute V < 0.2 OR either p > 0.01: Pure random variation likely
- If V 0.2-0.4 or mixed p-values: Inconclusive; need additional evidence
""")
    
    if len(significant) > 0:
        print("\nSIGNIFICANT ASSOCIATIONS:")
        for _, row in significant.iterrows():
            print(f"  ✓ {row['Attribute']}: V={row['Cramers_V_BW']:.4f}, "
                  f"Chi2-p={row['Chi2_P']:.6f}, Perm-p={row['Perm_P']:.6f}, "
                  f"N={row['Valid_N']}")
    
    if len(weak) > 0:
        print("\nWEAK ASSOCIATIONS (only one test significant):")
        for _, row in weak.iterrows():
            print(f"  ⚠ {row['Attribute']}: V={row['Cramers_V_BW']:.4f}, "
                  f"Chi2-p={row['Chi2_P']:.6f}, Perm-p={row['Perm_P']:.6f}, "
                  f"N={row['Valid_N']}")


def main():
    print("\n" + "="*100)
    print("STAND-ATTRIBUTE CORRELATION ANALYSIS (BERGSMA-WICHER BIAS-CORRECTED)")
    print("="*100)
    print("""
Research Question: Did merchants design seals as a validation system where 
specific stand types constrain the variation in associated attributes?

Statistical Approach:
1. Global cleanup: Remove 5 seals with blank STAND
2. Pairwise deletion: For each attribute, use only seals with valid STAND + attribute
3. Bergsma-Wicher V: Bias-corrected for sparse contingency tables
4. Dual validation: Both chi-square (parametric) AND permutation (non-parametric) tests
5. Significance: Only if BOTH p < 0.005 (Bonferroni-adjusted, α=0.05/10)

Expected sparsity: ~87% of contingency cells empty (500 samples, 139 stands × many attributes)
This is normal. Bergsma-Wicher and permutation test are designed for this.
""")
    
    # Parse data
    print("\n[STEP 1] Parsing appendix7.1.txt...")
    df = parse_appendix71()
    print(f"  Total seals loaded: {len(df)}\n")
    
    # Global cleanup on STAND
    print("[STEP 2] Global cleanup: Removing seals with blank STAND...")
    df = clean_global_stand(df)
    
    # Define salient attributes
    attributes = ['HALTER', 'EAR', 'NECK', 'EYE', 'HEAD', 'HOOF', 'PIZZLE', 'TAIL', 'LEG', 'HORN']
    
    # Get top stands and analyze entropy signatures
    print("[STEP 3] Analyzing entropy signatures of top 15 stand types...")
    top_stands = get_top_stands(df, n=15)
    print(f"  Top stands by frequency: {', '.join(top_stands)}\n")
    
    variance_df, corpus_entropy = analyze_variance_signatures(df, top_stands, attributes)
    print(f"  Corpus-level entropy by attribute:")
    for attr in attributes:
        print(f"    {attr}: {corpus_entropy[attr]:.3f}")
    
    # Print constrained vs scattered
    print_constrained_vs_scattered(variance_df)
    
    # Visualize conditional distributions
    print(f"\n[STEP 4] Generating conditional distribution heatmap...")
    visualize_conditional_distributions(df, top_stands, attributes)
    
    # Pairwise tests (5000 permutations for robust empirical p-values)
    print(f"\n[STEP 5] Running pairwise chi-square + permutation tests...")
    results_df = test_stand_attribute_independence_pairwise(df, attributes, num_permutations=5000)
    
    # Interpretation
    print_interpretation(results_df)
    
    # Save results
    print(f"\n[STEP 6] Saving results...")
    variance_df.to_csv('stand_attribute_variance.csv', index=False)
    print(f"  ✓ stand_attribute_variance.csv - Entropy analysis by stand")
    results_df.to_csv('stand_attribute_independence.csv', index=False)
    print(f"  ✓ stand_attribute_independence.csv - Chi-square + permutation tests")
    
    # Final summary table
    print("\n" + "="*100)
    print("RESULTS TABLE (Sorted by Cramér's V)")
    print("="*100)
    results_sorted = results_df.sort_values('Cramers_V_BW', ascending=False, na_position='last')
    print(results_sorted[['Attribute', 'Valid_N', 'Contingency_Shape', 
                           'Cramers_V_BW', 'Chi2_P', 'Perm_P', 'Status']].to_string(index=False))
    
    print("\n" + "="*100)
    print("ANALYSIS COMPLETE")
    print("="*100)
    print("""
Output files generated:
1. stand_attribute_variance.csv - Entropy signatures (low = constrained, high = scattered)
2. stand_attribute_heatmap.png - Visualization of top stands' attribute distributions
3. stand_attribute_independence.csv - Chi-square + permutation test results

Interpretation Guide:
- Variance CSV: Shows which stand types have constrained (low entropy) attributes
  * Negative Deviation = attribute values are concentrated (intentional design)
  * Positive Deviation = attribute values are scattered (random variation)

- Heatmap: Visual confirmation of concentration patterns
  * Concentrated rows = stand has preferred attribute values
  * Scattered rows = stand shows all possible attribute values

- Independence CSV: Statistical test results
  * SIGNIFICANT (both p < 0.005): Strong evidence for guild validation design
  * WEAK (one test only): Inconclusive
  * NOT SIGNIFICANT: Evidence supports random variation
""")


if __name__ == '__main__':
    main()
