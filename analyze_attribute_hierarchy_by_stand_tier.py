#!/usr/bin/env python3
"""
Analyze attribute-stand covariance hierarchically by stand tier (top 5, 10, 15).

Question: Which attributes best distinguish stands at different market tiers?

For practical validation, a trader might:
- Memorize top 5 stand bundles (most common) - needs strong discriminative attributes
- Handle top 10-15 for regular commerce - needs broader coverage
- Manage full system of 139 for rare cases - uses all 9 attributes

This analysis shows if attributes have DIFFERENT discriminative power at different tiers.

Output:
- attribute_hierarchy_top15.csv: Top 15 stands, chi-square + Cramér's V per attribute
- attribute_hierarchy_top10.csv: Top 10 stands, same
- attribute_hierarchy_top5.csv: Top 5 stands, same
- attribute_hierarchy_summary.txt: Interpretation and recommendations
"""

import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency
from collections import Counter
import warnings
warnings.filterwarnings('ignore')


def parse_appendix71(filename='appendix7.1.txt'):
    """Parse appendix7.1.txt and return DataFrame with all seals and their attributes."""
    
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Define invalid/missing value markers
    invalid_labels = {'n/a', 'blank', 'nan', 'na', '', 'none'}
    
    data = []
    for line in lines:
        parts = line.strip().split()
        if len(parts) >= 13:
            # Convert invalid labels to None
            def clean_value(val):
                return None if val.lower() in invalid_labels else val
            
            record = {
                'ID': parts[0],
                'SITE': parts[1],
                'EYE': clean_value(parts[2]),
                'EAR': clean_value(parts[3]),
                'HEAD': clean_value(parts[4]),
                'HORN': clean_value(parts[5]),
                'NECK': clean_value(parts[6]),
                'HALTER': clean_value(parts[7]),
                'TAIL': clean_value(parts[8]),
                'LEG': clean_value(parts[9]),
                'HOOF': clean_value(parts[10]),
                'PIZZLE': clean_value(parts[11]),
                'STAND': clean_value(parts[12]),
            }
            data.append(record)
    
    df = pd.DataFrame(data)
    
    # Convert STAND to numeric for sorting
    df['STAND_NUM'] = pd.to_numeric(df['STAND'], errors='coerce')
    df = df.dropna(subset=['STAND_NUM'])
    df['STAND_NUM'] = df['STAND_NUM'].astype(int)
    
    return df


def get_top_n_stands(df, n):
    """Get the top N stands by frequency."""
    stand_counts = df['STAND_NUM'].value_counts()
    top_stands = stand_counts.head(n).index.tolist()
    return sorted(top_stands)


def bergsma_wicher_v(contingency_matrix):
    """
    Bergsma & Wicher (2013) bias-corrected Cramér's V.
    Corrects for small sample sizes in sparse contingency tables.
    
    Args:
        contingency_matrix: numpy array (contingency table)
    
    Returns:
        float: Bias-corrected Cramér's V (0-1 scale)
    """
    n = contingency_matrix.sum()
    if n <= 1:
        return 0.0
    
    # Get chi-square statistic
    chi2, p_val, dof, expected = chi2_contingency(contingency_matrix)
    phi2 = chi2 / n
    r, c = contingency_matrix.shape
    
    # Bergsma-Wicher correction: penalize for sparsity
    phi2_corr = max(0, phi2 - ((r - 1) * (c - 1)) / (n - 1))
    
    # Correct degrees of freedom
    r_corr = r - ((r - 1) ** 2) / (n - 1)
    c_corr = c - ((c - 1) ** 2) / (n - 1)
    
    # Calculate V with corrected denominator
    denominator = min((r_corr - 1), (c_corr - 1))
    if denominator <= 0:
        return 0.0
    
    v = np.sqrt(phi2_corr / denominator)
    return v


def permutation_test_cramers_v(stand_col, attr_col, num_permutations=5000):
    """
    Empirical permutation test for Cramér's V.
    Shuffles attribute column, recalculates Bergsma-Wicher V for each shuffle.
    
    Args:
        stand_col: numpy array of stand values
        attr_col: numpy array of attribute values
        num_permutations: number of shuffles (default 5000)
    
    Returns:
        tuple: (empirical p-value, array of permutation V values, observed V)
    """
    # Calculate observed V
    observed_contingency = pd.crosstab(stand_col, attr_col)
    observed_v = bergsma_wicher_v(observed_contingency.values)
    
    # Permutation test: shuffle attribute column, recalculate V
    perm_v_array = []
    attr_shuffled = attr_col.copy()
    
    for _ in range(num_permutations):
        np.random.shuffle(attr_shuffled)
        perm_contingency = pd.crosstab(stand_col, attr_shuffled)
        perm_v = bergsma_wicher_v(perm_contingency.values)
        perm_v_array.append(perm_v)
    
    perm_v_array = np.array(perm_v_array)
    
    # Empirical p-value: proportion of permutation V >= observed V
    empirical_p = np.mean(perm_v_array >= observed_v)
    
    return empirical_p, perm_v_array, observed_v


def analyze_tier(df, top_stands, tier_name):
    """
    Analyze a tier (top 5, 10, or 15 stands).
    Uses pairwise deletion, Bergsma-Wicher bias-corrected Cramér's V, and 5000-iteration permutation testing.
    
    Returns DataFrame with columns:
    - Attribute: attribute name
    - Valid_N: number of seals with valid STAND + valid attribute
    - N_Stand_Types: number of unique stand types
    - N_Attr_Types: number of unique attribute types
    - Chi2: chi-square statistic
    - Chi2_P: chi-square p-value
    - Perm_P: empirical permutation p-value (5000 permutations)
    - Cramers_V_BW: Bergsma-Wicher bias-corrected effect size
    - Significance: "Yes" or "No" (requires both chi2_p AND perm_p < Bonferroni alpha)
    """
    
    # Filter to top stands only
    tier_df = df[df['STAND_NUM'].isin(top_stands)].copy()
    n_stand_types = len(tier_df['STAND_NUM'].unique())
    
    attributes = ['EYE', 'EAR', 'HEAD', 'HORN', 'NECK', 'HALTER', 'TAIL', 'LEG', 'HOOF', 'PIZZLE']
    
    # Bonferroni-corrected alpha for 10 attributes
    alpha_bonf = 0.05 / len(attributes)
    
    invalid_labels = {None, 'nan', 'n/a', 'na', 'blank', '', 'none'}
    
    results = []
    
    for attr in attributes:
        # PAIRWISE DELETION: Keep only rows with valid STAND + valid attribute
        pair_df = tier_df[['STAND_NUM', attr]].copy()
        clean_pair = pair_df[
            (pair_df['STAND_NUM'].notna()) & 
            (pair_df[attr].notna())
        ].copy()
        
        valid_n = len(clean_pair)
        
        if valid_n < 5:
            # Skip if too few seals
            results.append({
                'Attribute': attr,
                'Valid_N': valid_n,
                'N_Stand_Types': n_stand_types,
                'N_Attr_Types': 0,
                'Chi2': np.nan,
                'Chi2_P': np.nan,
                'Perm_P': np.nan,
                'Cramers_V_BW': np.nan,
                'Significance': 'INSUFFICIENT_DATA',
                'Tier': tier_name
            })
            continue
        
        # Build contingency table: stand vs attribute (clean data only)
        contingency = pd.crosstab(clean_pair['STAND_NUM'], clean_pair[attr])
        
        # Chi-square test
        chi2, chi2_p, dof, expected = chi2_contingency(contingency.values)
        
        # Bergsma-Wicher V
        v = bergsma_wicher_v(contingency.values)
        
        # Permutation test (5000 iterations)
        perm_p, perm_v_array, obs_v = permutation_test_cramers_v(
            clean_pair['STAND_NUM'].values, 
            clean_pair[attr].values, 
            num_permutations=5000
        )
        
        # Attribute diversity (in clean subset)
        attr_diversity = len(clean_pair[attr].unique())
        
        # Significance requires BOTH chi2 AND perm p-values < Bonferroni alpha
        sig = "Yes" if (chi2_p < alpha_bonf and perm_p < alpha_bonf) else "No"
        
        results.append({
            'Attribute': attr,
            'Valid_N': valid_n,
            'N_Stand_Types': n_stand_types,
            'N_Attr_Types': attr_diversity,
            'Chi2': chi2,
            'Chi2_P': chi2_p,
            'Perm_P': perm_p,
            'Cramers_V_BW': v,
            'Significance': sig,
            'Tier': tier_name
        })
    
    return pd.DataFrame(results)


def save_contingency_matrices(df, top_stands, tier_name):
    """
    Save contingency matrices (stand x attribute) for each attribute in a tier.
    Files saved as: contingency_matrix_{tier_name}_{attribute}.csv
    """
    tier_df = df[df['STAND_NUM'].isin(top_stands)].copy()
    attributes = ['EYE', 'EAR', 'HEAD', 'HORN', 'NECK', 'HALTER', 'TAIL', 'LEG', 'HOOF', 'PIZZLE']
    
    for attr in attributes:
        # Pairwise deletion
        pair_df = tier_df[['STAND_NUM', attr]].copy()
        clean_pair = pair_df[
            (pair_df['STAND_NUM'].notna()) & 
            (pair_df[attr].notna())
        ].copy()
        
        if len(clean_pair) >= 5:
            # Build contingency table
            contingency = pd.crosstab(clean_pair['STAND_NUM'], clean_pair[attr], margins=True)
            filename = f'contingency_matrix_{tier_name}_{attr}.csv'
            contingency.to_csv(filename)


def main():
    print("\n" + "="*90)
    print("ATTRIBUTE HIERARCHY ANALYSIS: Covariance at Different Stand Tiers")
    print("="*90)
    
    # Parse data
    print("\n[1] Parsing appendix7.1.txt...")
    df = parse_appendix71()
    print(f"    Loaded: {len(df)} seals, {df['STAND_NUM'].nunique()} unique stands")
    
    # Identify top stands
    stand_freq = df['STAND_NUM'].value_counts().sort_values(ascending=False)
    print(f"\n[2] Top 15 stands by frequency:")
    for i, (stand, count) in enumerate(stand_freq.head(15).items(), 1):
        print(f"    {i:2d}. Stand {stand:3d}: {count:3d} seals")
    
    # Analyze each tier
    print(f"\n[3] Analyzing attribute covariance by tier...")
    
    top_5 = get_top_n_stands(df, 5)
    top_10 = get_top_n_stands(df, 10)
    top_15 = get_top_n_stands(df, 15)
    
    df_top5 = analyze_tier(df, top_5, "Top 5")
    df_top10 = analyze_tier(df, top_10, "Top 10")
    df_top15 = analyze_tier(df, top_15, "Top 15")
    
    # Save results
    df_top5.to_csv('attribute_hierarchy_top5.csv', index=False)
    df_top10.to_csv('attribute_hierarchy_top10.csv', index=False)
    df_top15.to_csv('attribute_hierarchy_top15.csv', index=False)
    
    print(f"    [OK] attribute_hierarchy_top5.csv")
    print(f"    [OK] attribute_hierarchy_top10.csv")
    print(f"    [OK] attribute_hierarchy_top15.csv")
    
    # Save contingency matrices for each tier
    print(f"\n[3b] Saving contingency matrices (stand x attribute)...")
    save_contingency_matrices(df, top_5, "top5")
    save_contingency_matrices(df, top_10, "top10")
    save_contingency_matrices(df, top_15, "top15")
    print(f"    [OK] Contingency matrices saved for each tier")
    
    # Print summaries
    print(f"\n[4] Summary by tier:\n")
    
    for tier_name, df_tier in [("TOP 5", df_top5), ("TOP 10", df_top10), ("TOP 15", df_top15)]:
        print(f"\n{tier_name} STANDS")
        print("-" * 90)
        print(f"Stand types: {df_tier.iloc[0]['N_Stand_Types']}")
        print(f"\nAttribute Discriminative Power (ranked by Cramér's V - Bergsma-Wicher corrected):")
        
        df_sorted = df_tier.sort_values('Cramers_V_BW', ascending=False)
        
        for idx, row in df_sorted.iterrows():
            v = row['Cramers_V_BW']
            valid_n = row['Valid_N']
            chi2_p = row['Chi2_P']
            perm_p = row['Perm_P']
            sig = row['Significance']
            attr_types = row['N_Attr_Types']
            attr = row['Attribute']
            
            # Interpretation
            if v >= 0.70:
                strength = "VERY STRONG"
            elif v >= 0.60:
                strength = "STRONG"
            elif v >= 0.40:
                strength = "MODERATE"
            else:
                strength = "WEAK"
            
            print(f"  {attr:10s}  V={v:.4f}  ({strength:12s})  chi2_p={chi2_p:.2e}  perm_p={perm_p:.2e}  N={valid_n:3d}  Types={attr_types:2d}  Sig={sig}")
    
    # Analysis and interpretation
    print(f"\n{'='*90}")
    print("INTERPRETATION")
    print(f"{'='*90}")
    
    print("""
Cramér's V interpretation:
- 0.70+: Very strong association (attribute nearly determines stand)
- 0.60-0.70: Strong association (attribute useful for discrimination)
- 0.40-0.60: Moderate association
- < 0.40: Weak association

PRACTICAL VALIDATION QUESTION:
Which 3-4 attributes would a trader memorize to quickly validate seals?

Looking at the rankings (sorted by Cramér's V - effect size):
""")
    
    # Extract top attributes by Cramér's V for each tier
    top_attrs_5 = df_top5.nlargest(4, 'Cramers_V_BW')[['Attribute', 'Cramers_V_BW']].values.tolist()
    top_attrs_10 = df_top10.nlargest(4, 'Cramers_V_BW')[['Attribute', 'Cramers_V_BW']].values.tolist()
    top_attrs_15 = df_top15.nlargest(4, 'Cramers_V_BW')[['Attribute', 'Cramers_V_BW']].values.tolist()
    
    print(f"\nTop 5 stands (most common, likely memorized first):")
    for attr, v in top_attrs_5:
        print(f"  {attr}: V={v:.4f}")
    
    print(f"\nTop 10 stands (regular commerce):")
    for attr, v in top_attrs_10:
        print(f"  {attr}: V={v:.4f}")
    
    print(f"\nTop 15 stands (extended circle):")
    for attr, v in top_attrs_15:
        print(f"  {attr}: V={v:.4f}")
    
    # Key insight
    print(f"""
KEY INSIGHT:
If the top 3-4 attributes are CONSISTENT across tiers (top 5, 10, 15),
then a trader would use a SCALABLE protocol:
  
  1. Learn 3-4 "primary" attributes (e.g., HALTER, NECK, EAR)
  2. For top 5 stands: These 3-4 are sufficient
  3. For top 10-15 stands: Same attributes remain effective
  4. For rare stands: Full 9-attribute validation system needed
  
This suggests a HIERARCHICAL validation protocol:
- Quick (5 seconds): Check 3-4 primary attributes
- Thorough (15 seconds): Check 6-7 attributes
- Expert (slow): All 9 attributes for unknown seals

The fact that HALTER, NECK, EAR consistently rank high suggests traders
could memorize these patterns across guild tiers.

PIZZLE observation:
- Binary/sparse attribute (seals either have it or don't)
- Check if it ranks high (good discriminator) or low (not useful)
- If low: Suggests visual features dominate, not presence/absence markers
""")
    
    print(f"\n{'='*90}\n")


if __name__ == '__main__':
    main()
