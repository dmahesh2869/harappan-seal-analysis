"""
Seal Attribute Power Law Analysis
Complete analysis of all seal attributes (EYE, EAR, HEAD, HORN, NECK, HALTER, TAIL, LEG, HOOF, PIZZLE)
to test information hierarchy hypothesis: STAND as primary classifier, others as confirmatory features.

Methodology:
- Extract each attribute directly from appendix7.1.txt
- Exclude 'n/a' and 'blank' entries per attribute
- Fit power law to frequency distribution
- Compare exponents across all attributes
- Test hypothesis: STAND (shallow α) vs. others (steeper α) = information hierarchy

Output:
- summary_table: CSV with all attributes, exponents, and statistics
- attribute_power_laws.png: Multi-panel log-log plots for all attributes
"""

import powerlaw
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

# ============================================================================
# 1. PARSE APPENDIX7.1.TXT AND EXTRACT ATTRIBUTES
# ============================================================================

def parse_appendix71_attributes():
    """
    Extract all attributes from appendix7.1.txt
    Returns dict: {attribute_name: list_of_values_excluding_na_and_blank}
    """
    
    attributes = ['EYE', 'EAR', 'HEAD', 'HORN', 'NECK', 'HALTER', 'TAIL', 'LEG', 'HOOF', 'PIZZLE', 'STAND']
    attr_data = {attr: [] for attr in attributes}
    
    with open('appendix7.1.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Skip header line
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
        
        parts = line.split()
        if len(parts) < 13:  # Must have all columns
            continue
        
        # Extract each attribute (skipping ID and SITE columns)
        # Format: ID# SITE EYE EAR HEAD HORN NECK HALTER TAIL LEG HOOF PIZZLE STAND
        try:
            eye = parts[2]
            ear = parts[3]
            head = parts[4]
            horn = parts[5]
            neck = parts[6]
            halter = parts[7]
            tail = parts[8]
            leg = parts[9]
            hoof = parts[10]
            pizzle = parts[11]
            stand = parts[12]
            
            # Only add if attribute is not 'n/a' or 'blank'
            if eye not in ['n/a', 'blank']:
                attr_data['EYE'].append(eye)
            if ear not in ['n/a', 'blank']:
                attr_data['EAR'].append(ear)
            if head not in ['n/a', 'blank']:
                attr_data['HEAD'].append(head)
            if horn not in ['n/a', 'blank']:
                attr_data['HORN'].append(horn)
            if neck not in ['n/a', 'blank']:
                attr_data['NECK'].append(neck)
            if halter not in ['n/a', 'blank']:
                attr_data['HALTER'].append(halter)
            if tail not in ['n/a', 'blank']:
                attr_data['TAIL'].append(tail)
            if leg not in ['n/a', 'blank']:
                attr_data['LEG'].append(leg)
            if hoof not in ['n/a', 'blank']:
                attr_data['HOOF'].append(hoof)
            if pizzle not in ['n/a', 'blank']:
                attr_data['PIZZLE'].append(pizzle)
            if stand not in ['n/a', 'blank']:
                attr_data['STAND'].append(stand)
        except (IndexError, ValueError):
            continue
    
    return attr_data

# ============================================================================
# 2. FIT POWER LAW TO EACH ATTRIBUTE
# ============================================================================

def analyze_attribute(attr_name, attr_values):
    """
    Fit power law to attribute frequency distribution.
    Returns dict with analysis results.
    """
    
    # Count frequency of each type
    freq_counter = Counter(attr_values)
    frequencies = list(freq_counter.values())
    
    if len(frequencies) < 2:
        return None
    
    # Fit power law
    fit = powerlaw.Fit(frequencies, discrete=True)
    
    # Goodness-of-fit test
    n_boot = 2500
    observed_D = fit.power_law.D
    n_data = len(frequencies)
    count_ge = 0
    
    for i in range(n_boot):
        synthetic_data = fit.power_law.generate_random(n_data)
        synthetic_fit = powerlaw.Fit(synthetic_data, discrete=True, xmin=fit.power_law.xmin)
        if synthetic_fit.power_law.D >= observed_D:
            count_ge += 1
    
    p_value = count_ge / n_boot
    
    return {
        'attribute': attr_name,
        'n_types': len(freq_counter),
        'n_seals': len(attr_values),
        'alpha': fit.power_law.alpha,
        'xmin': fit.power_law.xmin,
        'D': fit.power_law.D,
        'p_value': p_value,
        'frequencies': frequencies,
        'freq_counter': freq_counter,
        'fit': fit
    }

# ============================================================================
# 3. GENERATE VISUALIZATIONS
# ============================================================================

def visualize_attribute_power_laws(results):
    """Create multi-panel log-log plots for all attributes."""
    
    # Sort by alpha value for visual grouping
    sorted_results = sorted(results, key=lambda x: x['alpha'])
    
    fig, axes = plt.subplots(3, 4, figsize=(18, 14))
    axes = axes.flatten()
    
    colors_by_role = {
        'STAND': '#E41A1C',  # Red - primary
        'HALTER': '#377EB8',  # Blue - secondary
        'NECK': '#4DAF4A',   # Green - secondary
        'EAR': '#FF7F00',    # Orange - secondary
        'EYE': '#984EA3',    # Purple - secondary/fine
        'HEAD': '#A65628',   # Brown
        'HORN': '#F781BF',   # Pink
        'TAIL': '#999999',   # Gray
        'LEG': '#E7298A',    # Magenta
        'HOOF': '#66C2A5',   # Teal
        'PIZZLE': '#FC8D62'  # Light orange
    }
    
    for idx, result in enumerate(sorted_results):
        ax = axes[idx]
        attr = result['attribute']
        
        # Prepare data for log-log plot
        freqs = np.array(sorted(result['frequencies'], reverse=True))
        ranks = np.arange(1, len(freqs) + 1)
        
        alpha = result['alpha']
        C = freqs[0]
        fit_line = C * (ranks ** (-1/(alpha - 1)))
        
        # Plot
        color = colors_by_role.get(attr, '#999999')
        ax.scatter(ranks, freqs, color=color, s=50, alpha=0.6, zorder=3)
        ax.plot(ranks, fit_line, 'r--', linewidth=2, label=f'α={alpha:.2f}')
        
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel('Rank', fontsize=10)
        ax.set_ylabel('Frequency', fontsize=10)
        
        title = f'{attr}\n'
        title += f'({result["n_types"]} types, {result["n_seals"]} seals)\n'
        title += f'p={result["p_value"]:.3f}'
        ax.set_title(title, fontsize=11, fontweight='bold')
        
        ax.grid(True, which='both', ls=':', alpha=0.4)
        ax.legend(fontsize=9, loc='upper right')
    
    plt.tight_layout()
    plt.savefig('attribute_power_laws.png', dpi=300, bbox_inches='tight')
    print("[OK] Multi-attribute power law plots saved to: attribute_power_laws.png")
    plt.close()

# ============================================================================
# 4. GENERATE SUMMARY STATISTICS
# ============================================================================

def print_summary_statistics(results):
    """Print comprehensive comparison of all attributes."""
    
    print("\n" + "="*100)
    print("SEAL ATTRIBUTE POWER LAW ANALYSIS: INFORMATION HIERARCHY TEST")
    print("="*100)
    
    print(f"\n{'Attribute':<12} {'Types':<8} {'Seals':<8} {'α':<8} {'xmin':<8} {'D':<8} {'p-value':<10}")
    print("-"*100)
    
    for result in sorted(results, key=lambda x: x['alpha']):
        attr = result['attribute']
        n_types = result['n_types']
        n_seals = result['n_seals']
        alpha = result['alpha']
        xmin = result['xmin']
        D = result['D']
        p_val = result['p_value']
        
        print(f"{attr:<12} {n_types:<8} {n_seals:<8} {alpha:>7.4f} {xmin:>7.1f} {D:>7.4f} {p_val:>9.4f}")
    
    print("-"*100)
    
    # Identify primary vs. confirmatory attributes
    print(f"\nINTERPRETATION:")
    print(f"  STAND (primary identifier):     α ≈ {[r['alpha'] for r in results if r['attribute'] == 'STAND'][0]:.4f}")
    
    secondary_attrs = [(r['attribute'], r['alpha']) for r in results if r['attribute'] != 'STAND']
    secondary_attrs.sort(key=lambda x: x[1])
    
    print(f"\n  Secondary attributes (ranked by steepness, higher α = less standardized):")
    for attr, alpha in secondary_attrs:
        print(f"    {attr:<12}  α = {alpha:.4f}")
    
    print(f"\nHYPOTHESIS TEST:")
    stand_alpha = [r['alpha'] for r in results if r['attribute'] == 'STAND'][0]
    shallower_than_stand = sum(1 for r in results if r['attribute'] != 'STAND' and r['alpha'] > stand_alpha)
    
    print(f"  STAND exponent:            {stand_alpha:.4f}")
    print(f"  Secondary attrs > STAND:   {shallower_than_stand}/{len(secondary_attrs)}")
    
    if shallower_than_stand == len(secondary_attrs):
        print(f"\n  ✓ CONFIRMED: All attributes show steeper power law than STAND")
        print(f"    This suggests STAND is the PRIMARY standardized identifier,")
        print(f"    while other attributes serve as CONFIRMATORY verification features.")
        print(f"    Pattern consistent with merchant guild classification system.")
    else:
        print(f"\n  ✗ PARTIAL: {len(secondary_attrs) - shallower_than_stand} attributes have shallower exponent than STAND")
        print(f"    Possible explanation: Some attributes equally standardized as STAND")
    
    print("="*100)

# ============================================================================
# 5. GENERATE CSV SUMMARY TABLE
# ============================================================================

def save_summary_table(results):
    """Save results to CSV for inclusion in paper."""
    
    df = pd.DataFrame([
        {
            'Attribute': r['attribute'],
            'n_types': r['n_types'],
            'n_seals': r['n_seals'],
            'alpha': f"{r['alpha']:.4f}",
            'xmin': f"{r['xmin']:.1f}",
            'D': f"{r['D']:.4f}",
            'p_value': f"{r['p_value']:.4f}",
            'passes_GOF': "Yes" if r['p_value'] > 0.1 else "No"
        }
        for r in sorted(results, key=lambda x: x['alpha'])
    ])
    
    df.to_csv('attribute_analysis_summary.csv', index=False)
    print("[OK] Summary table saved to: attribute_analysis_summary.csv")
    
    return df

# ============================================================================
# 6. FREQUENCY DISTRIBUTION TABLES (like unicorn_attributes.txt)
# ============================================================================

def print_frequency_tables(results):
    """Print frequency distribution tables for each attribute."""
    
    print("\n" + "="*100)
    print("FREQUENCY DISTRIBUTION TABLES BY ATTRIBUTE")
    print("="*100)
    
    for result in sorted(results, key=lambda x: x['attribute']):
        attr = result['attribute']
        freq_counter = result['freq_counter']
        
        # Bin frequencies
        bins = {
            '50+': 0,
            '20-49': 0,
            '15-19': 0,
            '10-14': 0,
            '5-9': 0,
            '2-4': 0,
            '1': 0
        }
        
        total_seals_binned = 0
        type_counts = {
            '50+': 0,
            '20-49': 0,
            '15-19': 0,
            '10-14': 0,
            '5-9': 0,
            '2-4': 0,
            '1': 0
        }
        
        for type_val, count in freq_counter.items():
            if count >= 50:
                bins['50+'] += count
                type_counts['50+'] += 1
            elif count >= 20:
                bins['20-49'] += count
                type_counts['20-49'] += 1
            elif count >= 15:
                bins['15-19'] += count
                type_counts['15-19'] += 1
            elif count >= 10:
                bins['10-14'] += count
                type_counts['10-14'] += 1
            elif count >= 5:
                bins['5-9'] += count
                type_counts['5-9'] += 1
            elif count >= 2:
                bins['2-4'] += count
                type_counts['2-4'] += 1
            else:
                bins['1'] += count
                type_counts['1'] += 1
            
            total_seals_binned += count
        
        print(f"\n{attr}")
        print("-" * 80)
        print(f"{'Frequency of Occurrence':<25} {'Count of Types':<20} {'Total Seals':<20}")
        print("-" * 80)
        
        for bin_name in ['50+', '20-49', '15-19', '10-14', '5-9', '2-4', '1']:
            if bins[bin_name] > 0:
                print(f"{bin_name:<25} {type_counts[bin_name]:<20} {bins[bin_name]:<20}")
        
        print("-" * 80)
        print(f"{'Sum':<25} {result['n_types']:<20} {result['n_seals']:<20}")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("Analyzing seal attributes for power law distribution...")
    print("Extracting data from appendix7.1.txt...\n")
    
    # Parse attributes
    attr_data = parse_appendix71_attributes()
    
    # Analyze each attribute
    results = []
    for attr_name in ['STAND', 'HALTER', 'NECK', 'EAR', 'EYE', 'HEAD', 'HORN', 'TAIL', 'LEG', 'HOOF', 'PIZZLE']:
        print(f"Analyzing {attr_name}...", end=' ')
        result = analyze_attribute(attr_name, attr_data[attr_name])
        if result:
            results.append(result)
            print(f"✓ ({result['n_types']} types, α={result['alpha']:.4f}, p={result['p_value']:.4f})")
        else:
            print("✗ (insufficient data)")
    
    # Print summaries
    print_summary_statistics(results)
    print_frequency_tables(results)
    
    # Generate visualizations
    print("\nGenerating visualizations...")
    visualize_attribute_power_laws(results)
    
    # Save summary table
    print("\nSaving results...")
    df = save_summary_table(results)
    
    print("\n" + "="*100)
    print("ANALYSIS COMPLETE!")
    print("="*100)
    print("\nOutputs generated:")
    print("  1. attribute_power_laws.png - Multi-panel log-log plots")
    print("  2. attribute_analysis_summary.csv - Summary statistics table")
    print("\nKey files for paper:")
    print("  - Use attribute_power_laws.png for main text (information hierarchy evidence)")
    print("  - Use attribute_analysis_summary.csv as supplementary table")
