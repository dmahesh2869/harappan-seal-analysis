#!/usr/bin/env python3
"""
Diachronic analysis of Indus seals across periods 3A, 3B, 3C.
Merges appendix7.1.txt with period data from diachronic_seal_data.txt.
Uses Alstott's powerlaw library for power law analysis (same as analyze_appendix71.py).
"""

import powerlaw
import matplotlib.pyplot as plt
import numpy as np
import warnings
from collections import defaultdict

# Suppress scipy optimization warnings during bootstrap
warnings.filterwarnings('ignore', category=Warning)


def parse_diachronic_data(filepath):
    """
    Parse diachronic_seal_data.txt to extract Period -> ID# mappings.
    Only parse lines between "------------------------" markers (first and last dash lines).
    Format: Period TAB ID# [optional comment - ignore this]
    Only uses columns 1 and 2 (Period and ID#).
    Returns periods 3A, 3B, 3C only.
    """
    period_to_ids = defaultdict(list)
    all_diachronic_ids = set()
    
    in_data_section = False
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.rstrip('\n')
            
            # Check for section markers (dashes)
            if line.strip().startswith('-'):
                if in_data_section:
                    # End of data section
                    break
                else:
                    # Start of data section
                    in_data_section = True
                    continue
            
            if not in_data_section:
                continue
            
            # Skip empty lines
            if not line.strip():
                continue
            
            # Parse Period and ID (separated by whitespace/tabs)
            # Only use first 2 columns, ignore comments
            parts = line.split()
            if len(parts) >= 2:
                period = parts[0]
                seal_id = parts[1]
                
                # Only process valid periods (3A, 3B, 3C)
                if period in ['3A', '3B', '3C']:
                    if seal_id:
                        period_to_ids[period].append(seal_id)
                        all_diachronic_ids.add(seal_id)
    
    return period_to_ids, all_diachronic_ids


def parse_appendix_data(filepath):
    """
    Parse appendix7.1.txt to extract seal data with all columns.
    Returns list of tuples: (ID#, full_line) and set of all seal IDs.
    """
    seals = []
    seal_ids = set()
    header = None
    
    with open(filepath, 'r') as f:
        for i, line in enumerate(f):
            line = line.rstrip('\n')
            
            if i == 0:
                header = line
                continue
            
            if not line.strip():
                continue
            
            parts = line.split()
            if len(parts) > 0:
                seal_id = parts[0]
                seal_ids.add(seal_id)
                seals.append((seal_id, line))
    
    return seals, seal_ids, header


def create_merged_appendix(seals, header, period_to_ids, output_file):
    """
    Create appendix7.1.diachronic.txt by adding PERIOD column.
    14 columns total: original 13 columns + PERIOD column
    """
    # Build reverse mapping: ID -> Period
    id_to_period = {}
    for period, ids in period_to_ids.items():
        for seal_id in ids:
            if seal_id not in id_to_period:
                id_to_period[seal_id] = period
    
    matched = 0
    unmatched = 0
    
    with open(output_file, 'w') as f:
        # Write new header with PERIOD column
        f.write(f"{header} PERIOD\n")
        
        for seal_id, line in seals:
            period = id_to_period.get(seal_id, 'n/a')
            
            if period != 'n/a':
                matched += 1
            else:
                unmatched += 1
            
            f.write(f"{line} {period}\n")
    
    return matched, unmatched


def create_missing_seals(period_to_ids, seal_ids, output_file):
    """
    Create diachronic_missing_seals.txt with seals in diachronic data
    but not in appendix7.1.txt
    """
    missing_seals = []
    
    for period, ids in period_to_ids.items():
        for seal_id in ids:
            if seal_id not in seal_ids:
                missing_seals.append((period, seal_id))
    
    with open(output_file, 'w') as f:
        f.write("Period ID#\n")
        for period, seal_id in sorted(missing_seals):
            f.write(f"{period} {seal_id}\n")
    
    return len(missing_seals)


def extract_stand_by_period(appendix_file):
    """
    Extract Stand types by Period from appendix7.1.diachronic.txt
    Returns: dict[period][stand] = count
    """
    period_stand_counts = defaultdict(lambda: defaultdict(int))
    
    with open(appendix_file, 'r') as f:
        for i, line in enumerate(f):
            if i == 0:  # Skip header
                continue
            
            parts = line.strip().split()
            if len(parts) >= 14:  # 13 original columns + PERIOD column
                # Last column is PERIOD, second-to-last is STAND
                period = parts[-1]
                stand = parts[-2]
                
                # Only count valid periods and non-n/a stands
                if period in ['3A', '3B', '3C'] and stand != 'n/a':
                    period_stand_counts[period][stand] += 1
    
    return period_stand_counts


def save_stand_table(period_stand_counts, output_file):
    """
    Save stand type counts as: Period Stand Count
    Sorted by Count (highest first)
    """
    with open(output_file, 'w') as f:
        f.write("Period Stand Count\n")
        
        for period in sorted(period_stand_counts.keys()):
            stands = period_stand_counts[period]
            # Sort by count (descending), then by stand name for ties
            for stand, count in sorted(stands.items(), key=lambda x: (-x[1], x[0])):
                f.write(f"{period} {stand} {count}\n")


def extract_stand_geographic_by_period(appendix_file):
    """
    Extract Stand types by Period and Site from appendix7.1.diachronic.txt
    Returns: (period_stand_site_counts, period_stand_totals)
    - period_stand_site_counts: dict[period][stand][site] = count
    - period_stand_totals: dict[period][stand] = total_count
    
    Only includes periods 3B and 3C (3A has insufficient data: 4 seals, 3 stands)
    """
    period_stand_site_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    period_stand_totals = defaultdict(lambda: defaultdict(int))
    
    with open(appendix_file, 'r') as f:
        for i, line in enumerate(f):
            if i == 0:  # Skip header
                continue
            
            parts = line.strip().split()
            if len(parts) >= 14:  # 13 original columns + PERIOD column
                site = parts[1]
                period = parts[-1]
                stand = parts[-2]
                
                # Only count valid periods (3B, 3C) and non-n/a stands
                if period in ['3B', '3C'] and stand != 'n/a':
                    period_stand_site_counts[period][stand][site] += 1
                    period_stand_totals[period][stand] += 1
    
    return period_stand_site_counts, period_stand_totals


def save_stand_geographic_table(period_stand_site_counts, period_stand_totals, output_file):
    """
    Save stand-site geographic distribution as: Period Stand Site Count
    For each period, only include top 5 stands by total frequency.
    Output as flat rows (one row per site occurrence of a top stand).
    Also appends pivot table at end of file.
    """
    with open(output_file, 'w') as f:
        # ===== FLAT VIEW =====
        f.write("=" * 100 + "\n")
        f.write("FLAT VIEW: Top 5 Stands per Period with Geographic Distribution\n")
        f.write("=" * 100 + "\n")
        f.write("Period Stand Site Count\n")
        
        for period in sorted(period_stand_site_counts.keys()):
            stands_in_period = period_stand_totals[period]
            
            # Get top 5 stands by total count
            top_stands = sorted(stands_in_period.items(), key=lambda x: -x[1])[:5]
            
            for stand, total_count in top_stands:
                sites = period_stand_site_counts[period][stand]
                # Sort sites for consistent output
                for site in sorted(sites.keys()):
                    count = sites[site]
                    f.write(f"{period} {stand} {site} {count}\n")
        
        # ===== PIVOT VIEW =====
        f.write("\n" + "=" * 100 + "\n")
        f.write("PIVOT VIEW: Top 5 Stands per Period with Site Counts in Columns\n")
        f.write("=" * 100 + "\n")
        
        # Collect all unique sites across all periods
        all_sites = set()
        for period in period_stand_site_counts.keys():
            for stand in period_stand_site_counts[period]:
                all_sites.update(period_stand_site_counts[period][stand].keys())
        
        all_sites_sorted = sorted(all_sites)
        
        # Write header
        header = "Period Stand " + " ".join(f"{site:>12}" for site in all_sites_sorted) + " Total"
        f.write(header + "\n")
        f.write("-" * len(header) + "\n")
        
        # Write data rows
        for period in sorted(period_stand_site_counts.keys()):
            stands_in_period = period_stand_totals[period]
            
            # Get top 5 stands by total count
            top_stands = sorted(stands_in_period.items(), key=lambda x: -x[1])[:5]
            
            for stand, total_count in top_stands:
                sites = period_stand_site_counts[period][stand]
                row = f"{period:<6} {stand:<5} "
                for site in all_sites_sorted:
                    count = sites.get(site, 0)
                    row += f"{count:>12} "
                row += f"{total_count:>5}"
                f.write(row + "\n")


def power_law_analysis_by_period(period_stand_counts, output_file):
    """
    Perform power law analysis on stand frequencies for each period.
    Using Alstott's powerlaw library (same methodology as analyze_appendix71.py).
    """
    results = {}
    
    with open(output_file, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("DIACHRONIC POWER LAW ANALYSIS (Periods 3A, 3B, 3C)\n")
        f.write("=" * 70 + "\n\n")
        
        for period in sorted(period_stand_counts.keys()):
            stands = period_stand_counts[period]
            frequencies = sorted(stands.values(), reverse=True)
            
            if len(frequencies) < 3:
                f.write(f"Period {period}: Insufficient data (only {len(frequencies)} stands)\n\n")
                continue
            
            # Fit power law using Alstott's library
            fit = powerlaw.Fit(frequencies, discrete=True)
            alpha = fit.power_law.alpha
            D = fit.power_law.D
            
            # Goodness-of-fit p-value (bootstrap method, Clauset et al. 2009)
            print(f"Computing bootstrap GOF for period {period}...")
            n_boot = 1000
            observed_D = D
            n_data = len(frequencies)
            count_ge = 0
            for i in range(n_boot):
                synthetic_data = fit.power_law.generate_random(n_data)
                synthetic_fit = powerlaw.Fit(synthetic_data, discrete=True, xmin=fit.power_law.xmin, verbose=False)
                if synthetic_fit.power_law.D >= observed_D:
                    count_ge += 1
            p_gof = count_ge / n_boot
            
            results[period] = {
                'alpha': alpha,
                'D': D,
                'p_gof': p_gof,
                'num_stands': len(frequencies),
                'total_seals': sum(frequencies),
                'xmin': fit.power_law.xmin
            }
            
            f.write(f"PERIOD {period}\n")
            f.write("-" * 70 + "\n")
            f.write(f"Number of distinct stands: {len(frequencies)}\n")
            f.write(f"Total seals: {sum(frequencies)}\n")
            f.write(f"Alpha (power law exponent): {alpha:.4f}\n")
            f.write(f"KS Statistic (D): {D:.6f}\n")
            f.write(f"xmin (cutoff): {fit.power_law.xmin}\n")
            f.write(f"Goodness-of-fit p-value: {p_gof:.4f} ({count_ge}/{n_boot})\n")
            
            if p_gof > 0.05:
                f.write(f"[OK] Consistent with power law (p > 0.05)\n")
            else:
                f.write(f"[FAIL] Less consistent with power law (p <= 0.05)\n")
            
            f.write(f"\nTop 10 stands by frequency:\n")
            stand_freqs = sorted(stands.items(), key=lambda x: x[1], reverse=True)
            for i, (stand, count) in enumerate(stand_freqs[:10], 1):
                f.write(f"  {i:2d}. Stand {stand:3s}: {count:3d} seals\n")
            
            f.write("\n" + "=" * 70 + "\n\n")
    
    return results


def plot_power_law_by_period(period_stand_counts, output_file):
    """
    Create visualization of power law distributions across periods.
    """
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle('Power Law Distribution of Stand Types by Period (3A, 3B, 3C)', 
                 fontsize=14, fontweight='bold')
    
    for idx, period in enumerate(sorted(period_stand_counts.keys())):
        ax = axes[idx]
        stands = period_stand_counts[period]
        
        # Get frequencies sorted by count (descending)
        frequencies = sorted(stands.values(), reverse=True)
        ranks = np.arange(1, len(frequencies) + 1)
        
        # Fit power law
        fit = powerlaw.Fit(frequencies, discrete=True)
        alpha = fit.power_law.alpha
        
        # Plot data
        ax.scatter(ranks, frequencies, alpha=0.6, s=50, color='steelblue', zorder=3)
        
        # Plot fitted line
        C = frequencies[0]
        fit_line = C * (ranks ** (-1/(alpha - 1)))
        ax.plot(ranks, fit_line, 'r--', linewidth=2, label=f'α = {alpha:.3f}')
        
        ax.set_xlabel('Rank (log scale)', fontsize=11)
        ax.set_ylabel('Frequency (log scale)', fontsize=11)
        ax.set_title(f'Period {period}\n({len(frequencies)} stands, {sum(frequencies)} seals)', 
                     fontsize=11)
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.grid(True, alpha=0.3, which='both')
        ax.legend(fontsize=10)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()


def main():
    print("=" * 70)
    print("DIACHRONIC ANALYSIS OF INDUS SEALS")
    print("=" * 70)
    print()
    
    # Step 1: Parse diachronic data
    print("Step 1: Parsing diachronic period data...")
    period_to_ids, all_diachronic_ids = parse_diachronic_data('diachronic_seal_data.txt')
    print(f"  Periods found: {sorted(period_to_ids.keys())}")
    for period in sorted(period_to_ids.keys()):
        print(f"    {period}: {len(period_to_ids[period])} seals")
    print()
    
    # Step 2: Parse appendix data
    print("Step 2: Parsing appendix7.1.txt...")
    seals, seal_ids, header = parse_appendix_data('appendix7.1.txt')
    print(f"  Total seals in appendix7.1.txt: {len(seals)}")
    print()
    
    # Step 3: Create merged appendix with period column
    print("Step 3: Creating appendix7.1.diachronic.txt (14 columns)...")
    matched, unmatched = create_merged_appendix(seals, header, period_to_ids, 'appendix7.1.diachronic.txt')
    print(f"  Matched: {matched} seals with period data")
    print(f"  Unmatched: {unmatched} seals without period data")
    print()
    
    # Step 4: Create missing seals file
    print("Step 4: Creating diachronic_missing_seals.txt...")
    num_missing = create_missing_seals(period_to_ids, seal_ids, 'diachronic_missing_seals.txt')
    print(f"  Missing seals: {num_missing} (in diachronic data but not in appendix7.1.txt)")
    print()
    
    # Step 5: Extract stand types by period
    print("Step 5: Creating diachronic_stand_table.txt...")
    period_stand_counts = extract_stand_by_period('appendix7.1.diachronic.txt')
    save_stand_table(period_stand_counts, 'diachronic_stand_table.txt')
    print(f"  Stand types by period:")
    for period in sorted(period_stand_counts.keys()):
        num_stands = len(period_stand_counts[period])
        total_seals = sum(period_stand_counts[period].values())
        print(f"    {period}: {num_stands} distinct stands, {total_seals} total seals")
    print()
    
    # Step 6: Extract stand geographic distribution by period
    print("Step 6: Creating diachronic_stand_geographic.txt (top 5 stands per period)...")
    period_stand_site_counts, period_stand_totals = extract_stand_geographic_by_period('appendix7.1.diachronic.txt')
    save_stand_geographic_table(period_stand_site_counts, period_stand_totals, 'diachronic_stand_geographic.txt')
    print(f"  Top 5 stands by period (with geographic distribution):")
    for period in sorted(period_stand_site_counts.keys()):
        top_stands = sorted(period_stand_totals[period].items(), key=lambda x: -x[1])[:5]
        print(f"    {period}: {[s[0] for s in top_stands]}")
    print()
    
    # Step 7: Power law analysis
    print("Step 7: Performing power law analysis (Alstott's library with bootstrap)...")
    results = power_law_analysis_by_period(period_stand_counts, 'diachronic_power_law_analysis.txt')
    print()
    
    # Step 8: Power law visualization
    print("Step 8: Creating power law visualization...")
    plot_power_law_by_period(period_stand_counts, 'diachronic_power_law_plot.png')
    print()
    
    print("=" * 70)
    print("DIACHRONIC ANALYSIS COMPLETE")
    print("=" * 70)
    print("\nGenerated files:")
    print("  1. appendix7.1.diachronic.txt        - 14 columns (merged data with PERIOD)")
    print("  2. diachronic_missing_seals.txt      - Seals in period data but not in appendix")
    print("  3. diachronic_stand_table.txt        - Stand counts by period")
    print("  4. diachronic_stand_geographic.txt   - Top 5 stands with geographic distribution (3B, 3C)")
    print("  5. diachronic_power_law_analysis.txt - Power law analysis by period")
    print("  6. diachronic_power_law_plot.png     - Visualization of power law fits")
    print()
    
    # Summary table
    print("\nSummary Statistics:")
    print("-" * 70)
    print(f"{'Period':<10} {'Stands':<10} {'Seals':<10} {'Alpha':<10} {'GOF p-val':<10} {'Status':<15}")
    print("-" * 70)
    for period in sorted(results.keys()):
        r = results[period]
        status = "PASS (p>0.05)" if r['p_gof'] > 0.05 else "FAIL (p<=0.05)"
        print(f"{period:<10} {r['num_stands']:<10} {r['total_seals']:<10} {r['alpha']:<10.4f} {r['p_gof']:<10.4f} {status:<15}")
    print()


if __name__ == '__main__':
    main()
