"""
Bundle Consistency Across Geographic Locations
Test: Do multi-site stands use the SAME validation attributes (NECK, HALTER, EAR) at each location?

If NECK types match across sites for the same stand → proves standardized validation protocol
If NECK types vary across sites → proves local customization within framework

Output:
- bundle_consistency_data.csv: Detailed attribute type matching per stand per site
- bundle_consistency_visualization.png: Multi-site stands with attribute consistency heatmap
- bundle_consistency_summary.txt: Human-readable summary of key findings
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# 1. PARSE APPENDIX7.1.TXT FOR SEAL-LEVEL DATA (OPTIMIZED)
# ============================================================================

def parse_appendix71_full():
    """Parse appendix7.1.txt with full attribute details per seal (space-separated format)."""
    data = []
    
    # Site name mapping for ID prefix resolution (from appendix7.1.txt SITE column)
    # Note: appendix7.1.txt already contains full site names, so this is only used as fallback
    site_map = {
        'AD': 'Allahdino', 'B': 'Banawali', 'BLK': 'Balakot', 
        'BSR': 'Bagasra', 'CDO': 'Chanhu-daro', 'DHL': 'Dholavira', 
        'F': 'Farmana', 'JHK': 'Jhukar', 'KBG': 'Kalibangan',
        'KOT': 'Kot-Diji', 'LHJ': 'Lohumjodaro', 'L': 'Lothal',
        'MRD': 'Mohenjo-daro', 'N': 'Nausharo', 'NI': 'Nindowari',
        'PBD': 'Pabumath', 'RKG': 'Rakigarhi', 'SKG': 'Surkotada'
    }
    
    with open('appendix7.1.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Skip header line
    for line in lines[1:]:
        parts = line.strip().split()
        if len(parts) < 13:
            continue
        
        try:
            seal_id = parts[0]
            site_name = parts[1]
            
            # Column mapping (space-separated):
            # 0: ID#, 1: SITE, 2: EYE, 3: EAR, 4: HEAD, 5: HORN, 6: NECK, 7: HALTER, 8: TAIL, 9: LEG, 10: HOOF, 11: PIZZLE, 12: STAND
            stand = parts[12] if len(parts) > 12 else ''
            
            # Skip if stand is invalid
            if stand in ('n/a', 'blank', '', 'nan', 'na', 'none'):
                continue
            
            # Use site name directly if available, otherwise extract from ID
            if site_name in site_map.values():
                site = site_name
            else:
                # Extract site code from seal_id
                code = seal_id.split('-')[0] if '-' in seal_id else seal_id[:3]
                site = site_map.get(code, site_name)
            
            data.append({
                'Seal_ID': seal_id,
                'Site': site,
                'Stand': stand,
                'EYE': parts[2],
                'EAR': parts[3],
                'HEAD': parts[4],
                'HORN': parts[5],
                'NECK': parts[6],
                'HALTER': parts[7],
                'TAIL': parts[8],
                'LEG': parts[9],
                'HOOF': parts[10],
                'PIZZLE': parts[11]
            })
        except (ValueError, IndexError):
            continue
    
    return pd.DataFrame(data)


# ============================================================================
# 2. GET TOP STANDS BY FREQUENCY, THEN FILTER TO MULTI-SITE
# ============================================================================

def get_top_stands_by_frequency(df, n=15):
    """
    Get top N stands by frequency (total seal count).
    Then return only those that appear at 2+ sites.
    
    This tests whether the MOST FREQUENT stands use consistent validation
    attributes across the sites where they appear.
    """
    # Count seals per stand
    stand_counts = df['Stand'].value_counts()
    top_n_stands = stand_counts.head(n).index.tolist()
    
    # Filter to those that appear at 2+ sites
    stand_sites = df[df['Stand'].isin(top_n_stands)].groupby('Stand')['Site'].nunique()
    multisite_top_stands = stand_sites[stand_sites >= 2].index.tolist()
    
    return multisite_top_stands, stand_counts

# ============================================================================
# 3. ANALYZE ATTRIBUTE CONSISTENCY
# ============================================================================

def analyze_bundle_consistency(df, top_stands_list):
    """
    For top N stands by frequency, check if validation attributes (NECK, HALTER, EAR)
    use the same types across sites (for stands that appear at 2+ sites).
    """
    validation_attrs = ['NECK', 'HALTER', 'EAR']
    invalid_labels = {'n/a', 'blank', 'nan', 'na', '', 'none'}
    consistency_data = []
    
    for stand in top_stands_list:
        # Get sites where this stand appears
        stand_df = df[df['Stand'] == stand]
        sites = stand_df['Site'].unique().tolist()
        
        if len(sites) < 2:  # Skip if not multi-site
            continue
        
        for attr in validation_attrs:
            # Get attribute types per site
            attr_by_site = {}
            for site in sites:
                site_seals = stand_df[stand_df['Site'] == site]
                if len(site_seals) == 0:
                    continue
                
                # Pairwise deletion: keep only rows with valid attribute (not None, not in invalid_labels)
                attr_values = site_seals[attr].dropna()
                attr_types = set(attr_values[~attr_values.isin(invalid_labels)].unique())
                
                if len(attr_types) > 0:
                    attr_by_site[site] = attr_types
            
            # Check consistency: Do all sites use at least one common type?
            if len(attr_by_site) >= 2:  # Only if we have data from multiple sites
                common_types = set.intersection(*attr_by_site.values())
                is_consistent = len(common_types) > 0
                
                consistency_data.append({
                    'Stand': stand,
                    'Attribute': attr,
                    'Num_Sites': len(sites),
                    'Sites_With_Data': len(attr_by_site),
                    'Sites': ', '.join(sorted(sites)),
                    'Is_Consistent': is_consistent,
                    'Common_Types': ', '.join(sorted(common_types)) if common_types else 'NONE',
                    'Total_Unique_Types': len(set.union(*attr_by_site.values())) if attr_by_site else 0
                })
    
    return pd.DataFrame(consistency_data)

# ============================================================================
# 4. GENERATE VISUALIZATIONS
# ============================================================================

def create_consistency_visualizations(consistency_df, df):
    """Create multiple visualizations of bundle consistency."""
    
    if len(consistency_df) == 0:
        print("✗ No data for visualizations")
        return
    
    # Get all stands in the consistency data (already filtered to top stands by frequency)
    stands_to_plot = consistency_df['Stand'].unique()
    filtered_df = consistency_df[consistency_df['Stand'].isin(stands_to_plot)]
    
    # Create figure with subplots
    fig = plt.figure(figsize=(16, 12))
    
    # Subplot 1: Heatmap - Consistency by Stand and Attribute (using matplotlib)
    ax1 = plt.subplot(2, 2, 1)
    consistency_pivot = filtered_df.pivot_table(
        index='Stand',
        columns='Attribute',
        values='Is_Consistent',
        aggfunc='first'
    ).astype(int)
    
    # Create matplotlib heatmap using imshow
    im = ax1.imshow(consistency_pivot.values, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
    ax1.set_xticks(range(len(consistency_pivot.columns)))
    ax1.set_yticks(range(len(consistency_pivot.index)))
    ax1.set_xticklabels(consistency_pivot.columns, rotation=45, ha='right')
    ax1.set_yticklabels([f"Stand {s}" for s in consistency_pivot.index])
    
    # Add text annotations
    for i in range(len(consistency_pivot.index)):
        for j in range(len(consistency_pivot.columns)):
            val = consistency_pivot.values[i, j]
            text = ax1.text(j, i, int(val), ha='center', va='center', 
                          color='white' if val == 0.5 else 'black', fontsize=8)
    
    cbar = plt.colorbar(im, ax=ax1)
    cbar.set_label('Consistent (1) vs Variable (0)')
    ax1.set_title('Validation Attribute Consistency Across Sites\n(Top Frequency Stands with Multiple Sites)', 
                  fontsize=12, fontweight='bold')
    ax1.set_ylabel('Offering Stand')
    ax1.set_xlabel('Validation Attribute')
    
    # Subplot 2: Bar chart - Number of unique types per attribute
    ax2 = plt.subplot(2, 2, 2)
    type_variety = filtered_df.groupby('Attribute')['Total_Unique_Types'].mean()
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    type_variety.plot(kind='bar', ax=ax2, color=colors[:len(type_variety)])
    ax2.set_title('Average Type Variety by Validation Attribute', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Average # of Unique Types')
    ax2.set_xlabel('Attribute')
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(axis='y', alpha=0.3)
    
    # Subplot 3: Consistency rate
    ax3 = plt.subplot(2, 2, 3)
    consistency_rate = filtered_df.groupby('Attribute')['Is_Consistent'].mean() * 100
    colors_rate = ['#FF6B6B' if x < 50 else '#FFA500' if x < 75 else '#90EE90' 
                   for x in consistency_rate.values]
    bars = ax3.bar(range(len(consistency_rate)), consistency_rate.values, color=colors_rate)
    ax3.set_xticks(range(len(consistency_rate)))
    ax3.set_xticklabels(consistency_rate.index, rotation=45, ha='right')
    ax3.set_title('Consistency Rate by Attribute\n(% of multi-site stands with common types)', 
                  fontsize=12, fontweight='bold')
    ax3.set_ylabel('Consistency Rate (%)')
    ax3.set_xlabel('Attribute')
    ax3.set_ylim([0, 100])
    ax3.axhline(y=50, color='gray', linestyle='--', alpha=0.5, label='50% threshold')
    ax3.grid(axis='y', alpha=0.3)
    
    # Subplot 4: Stand frequency vs consistency score
    ax4 = plt.subplot(2, 2, 4)
    stand_consistency = filtered_df.groupby('Stand')['Is_Consistent'].mean()
    stand_freqs = [df[df['Stand'] == s]['Site'].nunique() for s in stand_consistency.index]
    
    scatter = ax4.scatter(stand_freqs, stand_consistency.values * 100, s=200, alpha=0.6, c=stand_freqs, cmap='viridis')
    
    # Label top stands
    for i, (stand, freq) in enumerate(zip(stand_consistency.index[:5], stand_freqs[:5])):
        ax4.annotate(f'Stand {stand}', 
                    (freq, stand_consistency[stand] * 100),
                    xytext=(5, 5), textcoords='offset points', fontsize=9)
    
    ax4.set_xlabel('Number of Sites Stand Appears At')
    ax4.set_ylabel('Consistency Score (%)')
    ax4.set_title('Hub Stands vs Consistency\n(Do multi-site stands use consistent attributes?)', 
                  fontsize=12, fontweight='bold')
    ax4.grid(alpha=0.3)
    plt.colorbar(scatter, ax=ax4, label='# Sites')
    
    plt.tight_layout()
    plt.savefig('bundle_consistency_visualization.png', dpi=300, bbox_inches='tight')
    print("✓ Saved bundle_consistency_visualization.png")
    plt.close()

# ============================================================================
# 5. GENERATE DETAILED SUMMARY
# ============================================================================

def generate_summary(consistency_df, top_stands_list, seal_df):
    """Generate human-readable summary."""
    summary = []
    summary.append("=" * 80)
    summary.append("BUNDLE CONSISTENCY ANALYSIS: VALIDATION ATTRIBUTES ACROSS SITES")
    summary.append("=" * 80)
    summary.append("")
    summary.append("SCOPE: Top 15 stands by frequency that appear at 2+ sites")
    summary.append("")
    
    # Overall statistics
    total_top_stands = len(top_stands_list)
    total_records = len(consistency_df)
    consistent_records = consistency_df['Is_Consistent'].sum() if len(consistency_df) > 0 else 0
    consistency_pct = (consistent_records / total_records * 100) if total_records > 0 else 0
    
    summary.append(f"Top Frequency Stands Analyzed: {total_top_stands}")
    summary.append(f"Total Attribute Records: {total_records}")
    summary.append(f"Consistent Records: {consistent_records} ({consistency_pct:.1f}%)")
    summary.append("")
    
    if len(consistency_df) == 0:
        summary.append("NO DATA: Could not analyze consistency patterns")
        return '\n'.join(summary)
    
    # By attribute
    summary.append("CONSISTENCY BY ATTRIBUTE:")
    summary.append("-" * 80)
    for attr in ['NECK', 'HALTER', 'EAR']:
        attr_df = consistency_df[consistency_df['Attribute'] == attr]
        if len(attr_df) > 0:
            attr_consistent = attr_df['Is_Consistent'].sum()
            attr_total = len(attr_df)
            attr_pct = (attr_consistent / attr_total * 100) if attr_total > 0 else 0
            summary.append(f"  {attr}: {attr_consistent}/{attr_total} consistent ({attr_pct:.1f}%)")
    summary.append("")
    
    # Top findings
    summary.append("TOP FREQUENCY STANDS WITH CONSISTENT BUNDLES:")
    summary.append("-" * 80)
    if len(consistency_df) > 0:
        top_consistent = consistency_df[consistency_df['Is_Consistent']].groupby('Stand').size().sort_values(ascending=False).head(10)
        if len(top_consistent) > 0:
            for stand, count in top_consistent.items():
                stand_seals = seal_df[seal_df['Stand'] == stand]
                sites = sorted(stand_seals['Site'].unique().tolist())
                seals_count = len(stand_seals)
                summary.append(f"  Stand {stand}: {count}/3 attributes consistent across {len(sites)} sites ({seals_count} seals)")
                summary.append(f"    Sites: {', '.join(sorted(sites))}")
        else:
            summary.append("  No stands with consistent attributes found")
    summary.append("")
    
    # Hypothesis interpretation
    summary.append("HYPOTHESIS INTERPRETATION:")
    summary.append("-" * 80)
    if consistency_pct > 70:
        summary.append("✓ HIGH CONSISTENCY: Same stands use same validation attributes across sites")
        summary.append("  → Supports FRAGMENTATION hypothesis: Independent workshops coordinate on")
        summary.append("    shared validation protocols for inter-party trust")
    elif consistency_pct > 40:
        summary.append("◊ MODERATE CONSISTENCY: Mixed patterns - some attributes standardized, others local")
        summary.append("  → Supports HYBRID model: Framework standardization with local customization")
    else:
        summary.append("✗ LOW/NO CONSISTENCY: Stands vary their attributes by site")
        summary.append("  → Suggests LOCAL AUTONOMY: Each workshop uses own validation system")
    
    summary.append("")
    summary.append("=" * 80)
    
    return '\n'.join(summary)

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    print("=" * 80)
    print("BUNDLE CONSISTENCY ANALYSIS - Geographic/Site-Based Validation Attributes")
    print("=" * 80)
    
    print("\n[1/6] Parsing appendix7.1.txt for seal-level data...")
    try:
        df = parse_appendix71_full()
        print(f"✓ Loaded {len(df)} seals with {df['Stand'].nunique()} unique stands")
        print(f"  Sites represented: {df['Site'].nunique()}")
    except Exception as e:
        print(f"✗ Error parsing data: {e}")
        exit(1)
    
    print("\n[2/6] Getting top stands by frequency...")
    try:
        top_stands, stand_counts = get_top_stands_by_frequency(df, n=15)
        print(f"✓ Found {len(top_stands)} of top 15 frequency stands that appear at 2+ sites")
        
        if len(top_stands) > 0:
            # Show info about these top stands
            print("  Top frequency stands with multiple sites:")
            for stand in top_stands[:5]:
                seal_count = stand_counts[stand]
                site_count = df[df['Stand'] == stand]['Site'].nunique()
                sites = df[df['Stand'] == stand]['Site'].unique().tolist()
                print(f"    - Stand {stand}: {seal_count} seals, {site_count} sites ({', '.join(sites)})")
        else:
            print("✗ No top frequency stands appear at multiple sites")
    except Exception as e:
        print(f"✗ Error identifying stands: {e}")
        exit(1)
    
    print("\n[3/6] Analyzing bundle consistency...")
    try:
        consistency_df = analyze_bundle_consistency(df, top_stands)
        if len(consistency_df) > 0:
            print(f"✓ Analyzed {len(consistency_df)} stand-attribute combinations")
            consistent_pct = (consistency_df['Is_Consistent'].sum() / len(consistency_df) * 100)
            print(f"  Consistency rate: {consistent_pct:.1f}%")
        else:
            print("✗ No data available for consistency analysis")
    except Exception as e:
        print(f"✗ Error analyzing consistency: {e}")
        exit(1)
    
    print("\n[4/6] Generating consistency data CSV...")
    try:
        consistency_df.to_csv('bundle_consistency_data.csv', index=False)
        print("✓ Saved bundle_consistency_data.csv")
    except Exception as e:
        print(f"✗ Error saving CSV: {e}")
    
    print("\n[5/6] Generating visualizations...")
    try:
        if len(consistency_df) > 0:
            create_consistency_visualizations(consistency_df, df)
        else:
            print("✗ No data for visualizations")
    except Exception as e:
        print(f"✗ Error creating visualizations: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n[6/6] Generating summary report...")
    try:
        summary = generate_summary(consistency_df, top_stands, df)
        print(summary)
        
        with open('bundle_consistency_summary.txt', 'w') as f:
            f.write(summary)
        print("✓ Saved bundle_consistency_summary.txt")
    except Exception as e:
        print(f"✗ Error generating summary: {e}")
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
