#!/usr/bin/env python3
"""
Comprehensive Singleton Stand Analysis
Analyzes stand types that appear exactly once in the Indus seal dataset.

Outputs:
1. singleton_seal.txt - Table of all singleton stands (Seal, Site, Stand)
2. geographic_distribution_of_singleton_stands.png - Geographic map showing spatial dispersion

Key Question: Are singleton stands concentrated at major hubs or widely dispersed?
This reveals whether innovation/experimentation was centralized or distributed.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# SITE COORDINATES (from bipartite_network_analysis.py)
# ============================================================================

def get_site_coordinates():
    """
    Approximate geographical coordinates for Harappan sites
    (Latitude, Longitude) - based on standard archaeological references
    """
    coords = {
        'Harappa': (30.6236, 72.8042),
        'Mohenjo-daro': (27.3347, 68.1374),
        'Dholavira': (23.8859, 70.2157),
        'Lothal': (22.5224, 72.2423),
        'Kalibangan': (29.1286, 74.3044),
        'Chanhu-daro': (24.8542, 68.5156),
        'Banawali': (29.0928, 77.3261),
        'Allahdino': (25.2128, 68.4108),
        'Balakot': (25.3678, 67.2308),
        'Nausharo': (27.5614, 68.4083),
        'Rakigarhi': (29.3206, 77.9061),
        'Farmana': (29.1867, 77.5511),
        'Nindowari': (25.3544, 67.3208),
        'Jhukar': (25.1667, 68.0833),
        'Kot Diji': (28.0578, 69.5083),
        'Lohumjodaro': (27.4033, 68.4719),
        'Pabumath': (25.9428, 68.9039),
        'Surkotada': (23.0542, 69.6625),
        'Bagasra': (22.1311, 70.1261),
    }
    return coords

# ============================================================================
# PARSING AND DATA EXTRACTION
# ============================================================================

def parse_and_extract_singletons(filename='appendix7.1.txt'):
    """
    Parse appendix7.1.txt and extract singleton stand types.
    
    Returns:
        df_singleton: DataFrame with columns [ID, SITE, STAND]
        stand_counts: Series of stand type frequencies
    """
    
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Define invalid/missing value markers
    invalid_labels = {'n/a', 'blank', 'nan', 'na', '', 'none'}
    
    data = []
    for line in lines[1:]:  # Skip header
        parts = line.strip().split()
        if len(parts) >= 13:
            stand_val = parts[12]
            # SKIP if STAND is n/a or blank
            if stand_val.lower() not in invalid_labels:
                record = {
                    'ID': parts[0],
                    'SITE': parts[1],
                    'STAND': stand_val,
                }
                data.append(record)
    
    df = pd.DataFrame(data)
    
    # Count occurrences of each Stand type
    stand_counts = df['STAND'].value_counts()
    
    # Filter for singleton stands (count = 1)
    singleton_stands = stand_counts[stand_counts == 1].index.tolist()
    
    # Extract rows with singleton stands
    df_singleton = df[df['STAND'].isin(singleton_stands)].copy()
    
    # Sort by Stand for readability
    df_singleton = df_singleton.sort_values('STAND')
    
    return df_singleton, stand_counts, df

# ============================================================================
# OUTPUT 1: SAVE SINGLETON TABLE
# ============================================================================

def save_singleton_table(df_singleton):
    """Save singleton stands to TSV file."""
    
    output = df_singleton[['ID', 'SITE', 'STAND']].copy()
    output.columns = ['Seal', 'Site', 'Stand']
    
    output.to_csv('singleton_seal.txt', sep='\t', index=False)
    print(f"\n[OUTPUT 1] ✓ singleton_seal.txt ({len(output)} rows)")
    return output

# ============================================================================
# OUTPUT 2: GEOGRAPHIC VISUALIZATION
# ============================================================================

def visualize_singleton_geographic_distribution(df_singleton):
    """
    Create geographic map showing distribution of singleton stand types.
    Each site gets a unique color. All singletons plotted as equal-sized points.
    """
    
    coords = get_site_coordinates()
    
    # Get unique sites in singleton data
    unique_sites = sorted(df_singleton['SITE'].unique())
    
    # Count singletons per site
    singleton_per_site = df_singleton['SITE'].value_counts().to_dict()
    
    # Define colors for each site
    colors = plt.cm.tab20(np.linspace(0, 1, max(len(unique_sites), 10)))
    site_color_map = {site: colors[i] for i, site in enumerate(unique_sites)}
    
    # Create figure
    fig, ax = plt.subplots(figsize=(16, 14))
    
    # Set geographic bounds (Indus Valley region)
    ax.set_xlim(66, 79)
    ax.set_ylim(21, 33)
    
    # Add grid
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5, color='gray')
    
    # Plot all singleton points
    for idx, row in df_singleton.iterrows():
        site = row['SITE']
        if site in coords:
            lat, lon = coords[site]
            color = site_color_map[site]
            # Plot as small circle, all equal size
            ax.scatter(lon, lat, s=50, alpha=0.6, c=[color], 
                      edgecolors='black', linewidth=0.5, zorder=2)
    
    # Plot site locations as larger dots with labels
    for site, (lat, lon) in coords.items():
        if site in singleton_per_site:
            # Larger circle for site marker
            ax.scatter(lon, lat, s=400, alpha=0.3, c=[site_color_map[site]], 
                      edgecolors='black', linewidth=2.5, zorder=3, 
                      marker='o', label=f'{site} ({singleton_per_site[site]})')
            
            # Determine label position based on map quadrant
            map_center_lon = 72.5
            map_center_lat = 27.0
            
            dx, dy = 0.4, 0.4
            ha, va = 'left', 'bottom'
            
            if lon < map_center_lon and lat > map_center_lat:
                dx, dy = -0.4, 0.4
                ha, va = 'right', 'bottom'
            elif lon >= map_center_lon and lat > map_center_lat:
                dx, dy = 0.4, 0.4
                ha, va = 'left', 'bottom'
            elif lon < map_center_lon and lat <= map_center_lat:
                dx, dy = -0.4, -0.4
                ha, va = 'right', 'top'
            else:
                dx, dy = 0.4, -0.4
                ha, va = 'left', 'top'
            
            ax.text(lon + dx, lat + dy, site, fontsize=11, fontweight='bold',
                   ha=ha, va=va, bbox=dict(boxstyle='round,pad=0.3', 
                   facecolor='white', edgecolor='black', alpha=0.8))
    
    # Legend
    legend_elements = [Patch(facecolor=site_color_map[site], edgecolor='black', 
                            label=f'{site} ({singleton_per_site.get(site, 0)} singletons)')
                      for site in unique_sites]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=10, 
             title='Sites with Singleton Stands', title_fontsize=11, framealpha=0.95)
    
    # Labels and title
    ax.set_xlabel('Longitude (°E)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Latitude (°N)', fontsize=12, fontweight='bold')
    ax.set_title('Geographic Distribution of Singleton Stand Types\n' + 
                 f'(n={len(df_singleton)} unique stands appearing only once across {len(unique_sites)} sites)',
                 fontsize=14, fontweight='bold', pad=20)
    
    # Add note
    ax.text(0.5, -0.08, 'Small dots = individual singleton stands at their archaeological site location\n' +
                       'Larger circles = site markers. Colors distinguish different sites.',
           transform=ax.transAxes, ha='center', fontsize=10, style='italic',
           bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('geographic_distribution_of_singleton_stands.png', dpi=150, bbox_inches='tight')
    print(f"[OUTPUT 2] ✓ geographic_distribution_of_singleton_stands.png")
    plt.close()
    
    return singleton_per_site

# ============================================================================
# ANALYSIS AND INTERPRETATION
# ============================================================================

def analyze_dispersion(df_singleton, df_full, singleton_per_site, stand_counts):
    """Analyze concentration and dispersion patterns."""
    
    print("\n" + "="*80)
    print("SINGLETON STAND ANALYSIS: GEOGRAPHIC DISPERSION")
    print("="*80)
    
    print(f"\n[DATA SUMMARY]")
    print(f"  Total seals (valid STAND): {len(df_full)}")
    print(f"  Total unique stands: {len(stand_counts)}")
    print(f"  Singleton stands: {len(df_singleton)}")
    print(f"  Singleton percentage: {100*len(df_singleton)/len(stand_counts):.1f}% of all stands")
    
    print(f"\n[GEOGRAPHIC DISTRIBUTION]")
    print(f"  Sites with singleton stands: {len(singleton_per_site)}")
    print(f"\n  Breakdown by site:")
    for site in sorted(singleton_per_site.keys(), 
                      key=lambda x: singleton_per_site[x], reverse=True):
        count = singleton_per_site[site]
        pct = 100 * count / len(df_singleton)
        print(f"    {site:20s}: {count:2d} singletons ({pct:5.1f}%)")
    
    # Concentration analysis
    concentration = max(singleton_per_site.values()) / len(df_singleton)
    top2_concentration = sum(sorted(singleton_per_site.values(), reverse=True)[:2]) / len(df_singleton)
    
    print(f"\n[CONCENTRATION METRICS]")
    print(f"  Top site concentration: {concentration:.1%}")
    print(f"  Top 2 sites concentration: {top2_concentration:.1%}")
    
    print(f"\n[INTERPRETATION]")
    if concentration > 0.50:
        print(f"  → Singletons are CONCENTRATED (>50% at one site)")
        print(f"  → Innovation concentrated at major hubs (power-center model)")
    elif concentration > 0.30:
        print(f"  → Singletons are MODERATELY CONCENTRATED (30-50%)")
        print(f"  → Mixed innovation: some concentration, some dispersion")
    else:
        print(f"  → Singletons are DISPERSED (<30% at top site)")
        print(f"  → Innovation spread across multiple sites (distributed model)")
    
    if top2_concentration > 0.80:
        print(f"  → Top 2 sites account for >80% of singletons")
        print(f"  → Suggests independent development at major trading hubs")
    
    print("\n" + "="*80)

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("\n" + "="*80)
    print("COMPREHENSIVE SINGLETON STAND ANALYSIS")
    print("="*80)
    
    print(f"\n[STEP 1] Parsing appendix7.1.txt...")
    df_singleton, stand_counts, df_full = parse_and_extract_singletons()
    print(f"  Parsed: {len(df_full)} seals with valid STAND values")
    print(f"  Identified: {len(df_singleton)} singleton stands")
    
    print(f"\n[STEP 2] Generating outputs...")
    output_table = save_singleton_table(df_singleton)
    singleton_per_site = visualize_singleton_geographic_distribution(df_singleton)
    
    print(f"\n[STEP 3] Analyzing geographic dispersion...")
    analyze_dispersion(df_singleton, df_full, singleton_per_site, stand_counts)
    
    print(f"\nAnalysis complete.")

if __name__ == '__main__':
    main()
