#!/usr/bin/env python3
"""
Analyze ONLY the top 5 stands to see if THEY all show constraint patterns.
This tests whether the merchant validation system is coordinated across guild types.
"""

import pandas as pd
from collections import Counter
import numpy as np

# Parse appendix7.1.txt
df = pd.read_csv('appendix7.1.txt', sep='\s+', header=None, dtype=str)
df.columns = ['ID', 'SITE', 'EYE', 'EAR', 'HEAD', 'HORN', 'NECK', 'HALTER', 'TAIL', 'LEG', 'HOOF', 'PIZZLE', 'STAND']

# Exclude seals with missing STAND values
df_valid = df[~df['STAND'].isin(['n/a', 'blank'])].copy()

# Debug: Check what stands we actually have
stand_counts = df_valid['STAND'].value_counts()
print(f"DEBUG: Total stands found: {len(stand_counts)}")
print(f"DEBUG: Top 5 should be: {stand_counts.head(5).to_dict()}\n")

print("="*100)
print("TOP 5 STANDS CONSTRAINT ANALYSIS")
print("="*100)
print("\nIf these are coordinated guild validation systems, they should ALL show LOW entropy")
print("in key attributes like HALTER, EAR, NECK (the 'confirmation checks')\n")

# Top 5 stands only
top_5 = ['16', '32', '44', '1', '30']

attributes = ['HALTER', 'EAR', 'NECK', 'EYE', 'HEAD', 'HOOF', 'PIZZLE', 'TAIL', 'LEG']

# Compute corpus entropy for reference
def compute_entropy(values):
    """Shannon entropy of a distribution."""
    if len(values) == 0:
        return 0
    counts = Counter([v for v in values if v not in ['n/a', 'blank']])
    total = sum(counts.values())
    if total == 0:
        return 0
    probs = [c/total for c in counts.values()]
    return -sum(p * np.log2(p) for p in probs if p > 0)

# Corpus baseline
print("CORPUS BASELINE (all seals combined):")
corpus_entropy = {}
for attr in attributes:
    h = compute_entropy(df_valid[attr].values)
    corpus_entropy[attr] = h
    print(f"  {attr:10s}: {h:.3f}")

print("\n" + "="*100)
print("TOP 5 STANDS: CONSTRAINT ANALYSIS")
print("="*100)

# For each top stand, show constraint for each attribute
results = []

for stand_id in top_5:
    stand_seals = df_valid[df_valid['STAND'] == stand_id]
    n_seals = len(stand_seals)
    
    print(f"\nSTAND {stand_id} ({n_seals} seals)")
    print("-" * 100)
    print(f"{'Attribute':<12} {'Types':<8} {'Entropy':<10} {'Corpus':<10} {'Deviation':<12} {'Concentration':<12}")
    print("-" * 100)
    
    for attr in attributes:
        attr_values = stand_seals[attr]
        attr_values = attr_values[~attr_values.isin(['n/a', 'blank'])]
        
        counts = Counter(attr_values.values)
        n_types = len(counts)
        entropy = compute_entropy(attr_values.values)
        corpus_h = corpus_entropy[attr]
        deviation = entropy - corpus_h
        
        # Concentration = % in most common type
        if len(counts) > 0:
            max_count = max(counts.values())
            concentration = 100.0 * max_count / len(attr_values)
        else:
            concentration = 0
        
        # Color code: LOW entropy = constraint = GOOD
        status = "✓ CONSTRAINED" if deviation < -0.2 else "○ NEUTRAL" if -0.2 <= deviation <= 0.2 else "✗ SCATTERED"
        
        print(f"{attr:<12} {n_types:<8} {entropy:<10.3f} {corpus_h:<10.3f} {deviation:<12.3f} {concentration:<12.1f}% {status}")
        
        results.append({
            'Stand': stand_id,
            'Attribute': attr,
            'N_Types': n_types,
            'Entropy': entropy,
            'Corpus_Entropy': corpus_h,
            'Deviation': deviation,
            'Concentration': concentration,
            'Status': status
        })

# Summary: Average constraint across top 5 stands
print("\n" + "="*100)
print("SUMMARY: Is constraint COORDINATED across top 5 stands?")
print("="*100)

results_df = pd.DataFrame(results)

# Count constrained vs scattered by attribute
print("\nAttribute-level summary (% of top 5 stands showing CONSTRAINT):")
for attr in attributes:
    attr_results = results_df[results_df['Attribute'] == attr]
    constrained_count = len(attr_results[attr_results['Deviation'] < -0.2])
    pct = 100.0 * constrained_count / len(top_5)
    avg_deviation = attr_results['Deviation'].mean()
    print(f"  {attr:10s}: {constrained_count}/5 stands ({pct:5.1f}%) -- avg deviation {avg_deviation:+.3f}")

print("\nStand-level summary (# of attributes each stand constrains):")
for stand_id in top_5:
    stand_results = results_df[results_df['Stand'] == stand_id]
    constrained_count = len(stand_results[stand_results['Deviation'] < -0.2])
    scattered_count = len(stand_results[stand_results['Deviation'] > 0.2])
    print(f"  Stand {stand_id}: {constrained_count:2d} constrained, {scattered_count:2d} scattered")

print("\n" + "="*100)
print("INTERPRETATION:")
print("="*100)
print("""
HYPOTHESIS: Merchant validation system
- Prediction: ALL top 5 stands should show CONSTRAINT (deviation < -0.2) on key attributes
- Expected pattern: Stand 16 constrained, Stand 32 constrained, Stand 44 constrained, etc.
- Coordinated system: 5/5 stands × 9 attributes = multiple coordinated guild standards

ALTERNATIVE: Noise/Outliers
- If only 1-2 stands constrained: signal from outliers, not a system
- If scattered: no pattern at all

If results show:
✓ All 5 stands constrained on 5+ attributes each → STRONG evidence of merchant system
○ Some constrained, some scattered → MIXED evidence (some guilds followed protocol, others didn't)
✗ Only Stand 30 constrained → Likely OUTLIER, not a system
""")

# Generate top5_stand.txt with all seals from top 5 stands
print("\n" + "="*100)
print("GENERATING: top5_stand.txt (all seals from top 5 stands)")
print("="*100)

with open('top5_stand.txt', 'w') as f:
    f.write("STAND ID# SITE\n")
    
    # For each top 5 stand, extract and write all its seals
    for stand_id in top_5:
        stand_seals = df_valid[df_valid['STAND'] == stand_id]
        for idx, row in stand_seals.iterrows():
            f.write(f"{stand_id} {row['ID']} {row['SITE']}\n")

# Summary
total_seals_top5 = len(df_valid[df_valid['STAND'].isin(top_5)])
print(f"\nFile saved: top5_stand.txt")
print(f"Total seals in top 5 stands: {total_seals_top5}")
for stand_id in top_5:
    count = len(df_valid[df_valid['STAND'] == stand_id])
    print(f"  Stand {stand_id}: {count} seals")
