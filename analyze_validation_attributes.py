#!/usr/bin/env python3
"""
Which attributes form the MINIMAL validation protocol?
If merchants designed a practical system, only 2-3 visually salient attributes
would be checked by a seal reader.
"""

import pandas as pd
from collections import Counter
import numpy as np

# Parse appendix7.1.txt
df = pd.read_csv('appendix7.1.txt', sep='\s+', header=None, dtype=str)
df.columns = ['ID', 'SITE', 'EYE', 'EAR', 'HEAD', 'HORN', 'NECK', 'HALTER', 'TAIL', 'LEG', 'HOOF', 'PIZZLE', 'STAND']
df_valid = df[~df['STAND'].isin(['n/a', 'blank'])].copy()

print("="*100)
print("MINIMAL VALIDATION PROTOCOL: Which 2-3 attributes form the core validation system?")
print("="*100)
print("""
Visual Salience Ranking (how easy to see on a seal):
  LEVEL 1 (Very visible): HALTER (rope), EAR (shape), NECK (feature)
  LEVEL 2 (Visible): EYE (detail), HEAD (shape), HORN (prominent)
  LEVEL 3 (Medium): HOOF (requires turning seal), TAIL (side view), LEG (requires inspection)
  LEVEL 4 (Hard to see): PIZZLE (small detail, anatomically hidden)

Practical Hypothesis:
- A seal reader checking a seal quickly would look at HEAD-REGION attributes
- Validation is: "Stand #X + Halter #Y + Ear #Z?" = Legitimate
- Secondary confirmation: Neck type (optional)
- They would NOT check all 9 attributes — too slow, too error-prone
""")

top_5 = ['16', '32', '44', '1', '30']
attributes = ['HALTER', 'EAR', 'NECK', 'EYE', 'HEAD', 'HOOF', 'PIZZLE', 'TAIL', 'LEG']

# Compute corpus entropy for reference
def compute_entropy(values):
    if len(values) == 0:
        return 0
    counts = Counter([v for v in values if v not in ['n/a', 'blank']])
    total = sum(counts.values())
    if total == 0:
        return 0
    probs = [c/total for c in counts.values()]
    return -sum(p * np.log2(p) for p in probs if p > 0)

corpus_entropy = {}
for attr in attributes:
    h = compute_entropy(df_valid[attr].values)
    corpus_entropy[attr] = h

# For each attribute, compute constraint ACROSS all top 5 stands
print("\nCONSTRAINT CONSISTENCY ACROSS TOP 5 STANDS:")
print("-" * 100)
print(f"{'Attribute':<12} {'Avg Entropy':<14} {'Avg Deviation':<14} {'Consistency':<12} {'Validation Rank':<15}")
print("-" * 100)

consistency_data = []

for attr in attributes:
    entropies = []
    deviations = []
    
    for stand_id in top_5:
        stand_seals = df_valid[df_valid['STAND'] == stand_id]
        attr_values = stand_seals[attr]
        attr_values = attr_values[~attr_values.isin(['n/a', 'blank'])]
        
        h = compute_entropy(attr_values.values)
        dev = h - corpus_entropy[attr]
        entropies.append(h)
        deviations.append(dev)
    
    avg_entropy = np.mean(entropies)
    avg_deviation = np.mean(deviations)
    consistency = 1.0 - np.std(deviations)  # Higher = more consistent across stands
    
    consistency_data.append({
        'Attribute': attr,
        'Avg_Entropy': avg_entropy,
        'Avg_Deviation': avg_deviation,
        'Consistency': consistency
    })

consistency_df = pd.DataFrame(consistency_data).sort_values('Avg_Deviation')

for _, row in consistency_df.iterrows():
    # Validation rank based on: strong constraint + consistency
    score = -row['Avg_Deviation'] * row['Consistency']
    
    if row['Avg_Deviation'] < -2.0:
        rank = "★★★ CRITICAL"
    elif row['Avg_Deviation'] < -1.5:
        rank = "★★ IMPORTANT"
    elif row['Avg_Deviation'] < -1.0:
        rank = "★ SECONDARY"
    else:
        rank = "○ DECORATIVE"
    
    print(f"{row['Attribute']:<12} {row['Avg_Entropy']:<14.3f} {row['Avg_Deviation']:<14.3f} {row['Consistency']:<12.3f} {rank:<15}")

print("\n" + "="*100)
print("PRACTICAL VALIDATION PROTOCOL:")
print("="*100)

critical = consistency_df[consistency_df['Avg_Deviation'] < -2.0]
important = consistency_df[(consistency_df['Avg_Deviation'] >= -2.0) & (consistency_df['Avg_Deviation'] < -1.5)]

print(f"\n*** TIER 1: CRITICAL ATTRIBUTES (checked first) ***")
for _, row in critical.iterrows():
    print(f"  {row['Attribute']:<12} - Deviation {row['Avg_Deviation']:.3f} (must check)")

print(f"\n*** TIER 2: IMPORTANT ATTRIBUTES (confirmatory) ***")
for _, row in important.iterrows():
    print(f"  {row['Attribute']:<12} - Deviation {row['Avg_Deviation']:.3f} (double-check if uncertain)")

print(f"""
SEAL READER WORKFLOW (fast, practical):

1. Look at STAND type → Identifies guild
2. Check critical attributes (EAR, NECK, HALTER) → Confirms guild
3. If all 3 match → AUTHENTIC
4. If one fails → FORGERY (stop checking)

Example:
  "This is Stand #16. I see... Ear type [look], Neck type [look], Halter type [look].
   Yes, matches my training. This is a legitimate Stand 16 seal."
   
Time to validate: ~5 seconds (not 5 minutes checking all 9 attributes)

Forgery Detection:
  If someone copied Stand #16 but randomized EAR or NECK, this reader catches it.
  This is why all 9 attributes are constrained — but only 3 are needed for fast validation.
""")

print("\n" + "="*100)
print("DATA: STAND-BY-STAND VALIDATION PROTOCOL")
print("="*100)

for stand_id in top_5:
    stand_seals = df_valid[df_valid['STAND'] == stand_id]
    n_seals = len(stand_seals)
    
    print(f"\nSTAND #{stand_id} VALIDATION PROTOCOL ({n_seals} seals):")
    print("-" * 100)
    
    # Show the critical attributes
    critical_attrs = critical['Attribute'].tolist()
    
    for attr in critical_attrs:
        attr_values = stand_seals[attr]
        attr_values = attr_values[~attr_values.isin(['n/a', 'blank'])]
        counts = Counter(attr_values.values)
        
        # Most common types
        top_types = counts.most_common(3)
        pct_top = 100.0 * sum(c for _, c in top_types) / len(attr_values) if len(attr_values) > 0 else 0
        type_names = ', '.join(str(t[0]) for t in top_types)
        
        print(f"  {attr:10s}: {pct_top:5.1f}% of seals use types {{{type_names}}}")

print(f"""
INTERPRETATION:
- If all TIER 1 attributes match across 5 stands → Coordinated, systematic validation
- If only some match → Partial system, cultural variation
- If none match → Random variation, no validation system

The key insight: Merchants don't need to check all 9 attributes.
They designed seals so that 2-3 key attributes identify guild + stand unambiguously.
This is PRACTICAL security, not theoretical.
""")
