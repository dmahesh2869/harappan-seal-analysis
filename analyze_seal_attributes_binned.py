#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze Harappan unicorn seal attributes using binned frequency data from unicorn_attributes.txt.

This script:
1. Parses binned frequency tables for 10 seal attributes (Halter, Ear, Neck, Eye, Head, Hoof, Pizzle, Leg, Tail, Horn)
2. Fits each attribute distribution to a power law using the powerlaw library
3. Tests goodness-of-fit against alternative distributions (exponential, lognormal, etc.)
4. Outputs statistics for each attribute in tabular format

The analysis follows the same methodology as analyze_guilds.py to maintain consistency.
"""

import powerlaw
import sys

# Fix encoding for Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)


def parse_unicorn_attributes_binned():
    """
    Extract Jamison's binned frequency tables from unicorn_attributes.txt.
    Returns dict mapping attribute name to binned frequency data.
    Handles Horn separately as it contains actual per-type data (not binned).
    """
    binned_data = {}
    
    with open('unicorn_attributes.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Attribute names in order of appearance (including Stand)
    attribute_names = ['Stand', 'Halter', 'Ear', 'Neck', 'Eye', 'Head', 'Hoof', 'Pizzle', 'Leg', 'Tail', 'Horn']
    
    for attr in attribute_names:
        # Find the table start for this attribute (search patterns account for naming variations)
        table_start = None
        # Handle 'Stand' vs other attributes (Stand has capital S)
        search_patterns = [f'Table - {attr}', f'Table - {attr.lower()}', f'Table - {attr.capitalize()}', f'Table - Front {attr}', f'Table - {attr} ']
        
        for i, line in enumerate(lines):
            for pattern in search_patterns:
                if pattern.lower() in line.lower():
                    table_start = i
                    break
            if table_start is not None:
                break
        
        if table_start is None:
            print(f"[WARNING] Could not find table for {attr}")
            continue
        
        # SPECIAL CASE: Horn has actual per-type data, not binned
        if attr == 'Horn':
            # Parse actual type frequencies for Horn (Types 1-5, exclude Type 0)
            types_and_counts = {}
            total_seals_with_type0 = 0
            type0_count = 0
            
            for i in range(table_start + 1, min(table_start + 20, len(lines))):
                line = lines[i].strip()
                
                if not line or 'Type' in line or 'Total' in line or line.startswith('-'):
                    continue
                
                parts = line.split()
                if len(parts) < 2:
                    continue
                
                try:
                    type_num = int(parts[0])
                    count = int(parts[1])
                    
                    if type_num == 0:
                        # Type 0 = unclassified, exclude from analysis
                        type0_count = count
                    else:
                        # Actual types (1-5)
                        types_and_counts[type_num] = count
                    
                    total_seals_with_type0 += count
                except (ValueError, IndexError):
                    pass
            
            if types_and_counts:
                n_types = len(types_and_counts)
                n_seals = total_seals_with_type0 - type0_count  # Exclude Type 0
                
                # Create frequency list directly from actual type counts
                freq_list = []
                for type_num in sorted(types_and_counts.keys()):
                    freq_list.append(types_and_counts[type_num])
                
                binned_data[attr] = {
                    'n_types': n_types,
                    'n_seals': n_seals,
                    'bins': [{'freq_label': f'Type {t}', 'n_types': 1, 'n_seals': c} for t, c in sorted(types_and_counts.items())],
                    'is_actual_data': True,  # Flag indicating this is actual per-type, not binned
                    'freq_list': freq_list  # Direct frequency list for power law fitting
                }
            continue
        
        # STANDARD CASE: Binned frequency tables
        bins = []
        n_types = None
        n_seals = None
        
        for i in range(table_start + 1, min(table_start + 25, len(lines))):
            line = lines[i].strip()
            
            # Skip empty lines, headers, and separators
            if not line or 'Frequency' in line or 'Table' in line or 'Proportion' in line or line.startswith('-') or 'Type' in line and 'Table' not in line:
                continue
            
            parts = line.split()
            if len(parts) < 2:
                continue
            
            # Look for Sum line
            if parts[0] == 'Sum':
                try:
                    n_types = int(parts[1])
                    n_seals = int(parts[2])
                except (ValueError, IndexError):
                    pass
                break
            
            # Parse frequency bin
            try:
                # Standard format: freq_range n_types_in_range n_seals_in_range
                freq_label = parts[0]
                n_types_bin = int(parts[1])
                n_seals_bin = int(parts[2])
                if n_types_bin > 0 and n_seals_bin > 0:
                    bins.append({
                        'freq_label': freq_label,
                        'n_types': n_types_bin,
                        'n_seals': n_seals_bin
                    })
            except (ValueError, IndexError):
                pass
        
        if n_types is not None and n_seals is not None:
            binned_data[attr] = {
                'n_types': n_types,
                'n_seals': n_seals,
                'bins': bins,
                'is_actual_data': False  # Flag indicating this is binned, not actual per-type
            }
    
    return binned_data


def create_frequency_list(bins):
    """
    Convert binned data to frequency list for powerlaw fitting.
    Each type is represented once per its mean frequency (seals / types in bin).
    """
    freq_list = []
    for bin_data in bins:
        mean_freq = bin_data['n_seals'] / bin_data['n_types']
        freq_list.extend([mean_freq] * bin_data['n_types'])
    return freq_list


def analyze_attribute(attr_name, binned_data):
    """
    Analyze single attribute for power law distribution.
    Returns dict with statistics.
    Handles both binned data and actual per-type data (e.g., Horn).
    """
    if attr_name not in binned_data:
        return None
    
    attr_data = binned_data[attr_name]
    n_types = attr_data['n_types']
    n_seals = attr_data['n_seals']
    
    # Create frequency list
    if attr_data.get('is_actual_data'):
        # Horn: use actual per-type frequencies directly
        freq_list = attr_data['freq_list']
    else:
        # Other attributes: convert binned data to frequency list
        bins = attr_data['bins']
        freq_list = create_frequency_list(bins)
    
    # Fit to power law
    # Use discrete=True: frequency distribution of discrete types (each with mean frequency from bin)
    fit = powerlaw.Fit(freq_list, discrete=True)
    alpha = fit.power_law.alpha
    xmin = fit.power_law.xmin
    ks_distance = fit.power_law.D
    
    # Bootstrap goodness-of-fit test (2500 iterations)
    print(f"  Bootstrap GoF test for {attr_name}...", end='', flush=True)
    observed_D = fit.power_law.D
    n_data = len(freq_list)
    count_ge = 0
    for i in range(2500):
        synthetic_data = fit.power_law.generate_random(n_data)
        synthetic_fit = powerlaw.Fit(synthetic_data, discrete=True, xmin=fit.power_law.xmin)
        if synthetic_fit.power_law.D >= observed_D:
            count_ge += 1
    p_gof = count_ge / 2500
    print(" done")
    
    # Compare to alternatives
    comparisons = {}
    for alt_dist in ['exponential', 'lognormal', 'stretched_exponential', 'truncated_power_law']:
        R, p = fit.distribution_compare('power_law', alt_dist)
        comparisons[alt_dist] = {'R': R, 'p': p}
    
    return {
        'n_types': n_types,
        'n_seals': n_seals,
        'alpha': alpha,
        'xmin': xmin,
        'ks_distance': ks_distance,
        'p_gof': p_gof,
        'comparisons': comparisons,
        'is_actual_data': attr_data.get('is_actual_data', False)
    }


def print_statistics_table(results):
    """Print summary statistics table for all attributes."""
    print("\n" + "="*150)
    print("POWER LAW ANALYSIS: UNICORN SEAL ATTRIBUTES (INCLUDING STAND)")
    print("="*150)
    
    header = f"{'Attribute':<12} | {'n_types':<8} | {'n_seals':<8} | {'α':<8} | {'x_min':<8} | {'KS D':<10} | {'GoF p':<10} | {'Clauset':<15} | {'Data Type':<15}"
    print(header)
    print("-" * 150)
    
    for attr in ['Stand', 'Halter', 'Ear', 'Neck', 'Eye', 'Head', 'Hoof', 'Pizzle', 'Leg', 'Tail', 'Horn']:
        if attr not in results:
            continue
        
        r = results[attr]
        clauset = "✓ PASS" if r['n_types'] >= 100 else f"✗ FAIL ({r['n_types']}/100)"
        data_type = "Actual" if r.get('is_actual_data') else "Binned"
        
        print(f"{attr:<12} | {r['n_types']:<8} | {r['n_seals']:<8} | {r['alpha']:<8.4f} | {r['xmin']:<8.4f} | {r['ks_distance']:<10.4f} | {r['p_gof']:<10.4f} | {clauset:<15} | {data_type:<15}")
    
    print("="*150)


def print_detailed_results(results):
    """Print detailed results for each attribute."""
    print("\n" + "="*120)
    print("DETAILED RESULTS BY ATTRIBUTE")
    print("="*120)
    
    for attr in ['Stand', 'Halter', 'Ear', 'Neck', 'Eye', 'Head', 'Hoof', 'Pizzle', 'Leg', 'Tail', 'Horn']:
        if attr not in results:
            continue
        
        r = results[attr]
        
        print(f"\n{attr.upper()}")
        print("-" * 60)
        print(f"  Types: {r['n_types']:<10} Seals: {r['n_seals']:<10}", end='')
        if r.get('is_actual_data'):
            print(" [ACTUAL PER-TYPE DATA]")
        else:
            print(" [BINNED DATA]")
        
        print(f"  α (exponent): {r['alpha']:.4f}")
        print(f"  x_min: {r['xmin']:.4f}")
        print(f"  KS Distance: {r['ks_distance']:.4f}")
        print(f"  GoF p-value (bootstrap): {r['p_gof']:.4f}")
        
        # Clauset criterion
        if r['n_types'] >= 100:
            print(f"  Clauset Criterion: ✓ PASS (n_types = {r['n_types']} >= 100)")
        else:
            print(f"  Clauset Criterion: ✗ FAIL (n_types = {r['n_types']} < 100)")
        
        # Distribution comparisons
        print(f"\n  Distribution Comparisons (vs. Power Law):")
        for alt_dist in ['exponential', 'lognormal', 'stretched_exponential', 'truncated_power_law']:
            comp = r['comparisons'][alt_dist]
            print(f"    {alt_dist:<30} R={comp['R']:>8.4f}   p={comp['p']:>8.4f}")


def save_summary_table_csv(results):
    """Save results to CSV for comparison with complete data analysis."""
    import pandas as pd
    
    rows = []
    for attr_name, result in sorted(results.items()):
        rows.append({
            'Attribute': attr_name,
            'n_types': result['n_types'],
            'n_seals': result['n_seals'],
            'alpha': f"{result['alpha']:.4f}",
            'xmin': f"{result['xmin']:.4f}",
            'D': f"{result['ks_distance']:.4f}",
            'p_value': f"{result['p_gof']:.4f}",
            'data_type': 'Actual' if result.get('is_actual_data') else 'Binned'
        })
    
    df = pd.DataFrame(rows)
    df.to_csv('attribute_analysis_summary_binned.csv', index=False)
    print("[OK] Binned summary table saved to: attribute_analysis_summary_binned.csv")
    
    return df


def main():
    print("Parsing unicorn_attributes.txt...")
    binned_data = parse_unicorn_attributes_binned()
    
    if not binned_data:
        print("ERROR: No attributes parsed from unicorn_attributes.txt")
        return
    
    print(f"Successfully parsed {len(binned_data)} attributes")
    
    # Analyze each attribute
    print("\nAnalyzing power law distributions...")
    results = {}
    for attr in ['Stand', 'Halter', 'Ear', 'Neck', 'Eye', 'Head', 'Hoof', 'Pizzle', 'Leg', 'Tail', 'Horn']:
        if attr in binned_data:
            print(f"Analyzing {attr}...")
            results[attr] = analyze_attribute(attr, binned_data)
    
    # Print results
    print_statistics_table(results)
    print_detailed_results(results)
    
    # Save CSV
    print("\nSaving results...")
    save_summary_table_csv(results)
    
    # Summary
    print("\n" + "="*120)
    print("SUMMARY")
    print("="*120)
    print("\nAttributes meeting Clauset's n_types >= 100 criterion:")
    passing = [attr for attr in results if results[attr]['n_types'] >= 100]
    if passing:
        for attr in passing:
            print(f"  ✓ {attr} ({results[attr]['n_types']} types)")
    else:
        print("  None. All attributes fall below threshold.")
    
    print("\nAttributes with strong power law (GoF p >= 0.05):")
    strong_pl = [attr for attr in results if results[attr]['p_gof'] >= 0.05]
    if strong_pl:
        for attr in strong_pl:
            is_actual = " [ACTUAL DATA]" if results[attr].get('is_actual_data') else " [BINNED]"
            print(f"  ✓ {attr} (p = {results[attr]['p_gof']:.4f}){is_actual}")
    else:
        print("  None significantly support power law hypothesis.")
    
    print("\nAttributes favoring exponential over power law:")
    exp_favored = [attr for attr in results if results[attr]['comparisons']['exponential']['R'] < -1.0]
    if exp_favored:
        for attr in exp_favored:
            r = results[attr]['comparisons']['exponential']['R']
            print(f"  × {attr} (R = {r:.4f}, favors exponential)")
    else:
        print("  None strongly favor exponential.")


if __name__ == '__main__':
    main()
