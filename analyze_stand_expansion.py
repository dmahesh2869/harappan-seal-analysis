"""
Analyze stand type expansion from Jamison's Appendix 7.1
- Compare raw stands in appendix7.1.txt vs final stands in sites_guild.txt
- Identify missing and variant stands
- Generate comprehensive analysis
"""

import re
from collections import defaultdict

# Read stands from sites_guild.txt
stands = []
with open('sites_guild.txt', 'r') as f:
    for line in f:
        line = line.strip()
        if line.startswith('STAND ') and '(Total:' in line:
            parts = line.split('(Total:')
            if len(parts) == 2:
                stand_name = parts[0].replace('STAND ', '').strip()
                stands.append(stand_name)

# Get frequencies from sites_guild.txt
stand_freq = {}
with open('sites_guild.txt', 'r') as f:
    for line in f:
        line = line.strip()
        if line.startswith('STAND ') and '(Total:' in line:
            match = re.search(r'STAND (\S+) \(Total: (\d+)\)', line)
            if match:
                stand_name = match.group(1)
                count = int(match.group(2))
                stand_freq[stand_name] = count

print("=" * 70)
print("STAND TYPE EXPANSION ANALYSIS")
print("=" * 70)
print(f"\nTotal types in sites_guild.txt: {len(stands)}")
print(f"Jamison's claim (Table 7.6): 114 types")
print(f"Expansion in Appendix 7.1: +{len(stands) - 114} types")
print("\n" + "-" * 70)
print("COMPLETE LIST (sorted by frequency):\n")

# Sort stands by frequency (descending)
stands_sorted = sorted(stands, key=lambda s: -stand_freq.get(s, 0))

# Separate numeric and letter variants
numeric_only = []
with_variants = []

for s in stands_sorted:
    # Check if it's purely numeric
    if s.isdigit():
        numeric_only.append((int(s), s))
    else:
        # Has letters - extract numeric part for sorting
        # e.g., "61b" -> 61
        match = re.match(r'(\d+)', s)
        if match:
            base = int(match.group(1))
            with_variants.append((base, s))
        else:
            with_variants.append((999, s))

# Sort
numeric_only.sort(key=lambda x: -x[0])  # By numeric value (descending)
with_variants.sort(key=lambda x: (-x[0], x[1]))  # By numeric base, then alphabetically

# Combine sorted lists
all_sorted = [s[1] for s in numeric_only] + [s[1] for s in with_variants]

# Analyze which numeric stands (1-114) are MISSING in sites_guild.txt
numeric_stands_set = set()
for s in stands:
    if s.isdigit():
        numeric_stands_set.add(int(s))

all_1_to_114 = set(range(1, 115))
missing_stands = sorted(all_1_to_114 - numeric_stands_set)

print(f"\nAnalyzing missing stands from 1-114 range...")
print(f"Missing stands: {missing_stands}")

# Check if missing stands appear in appendix7.1.txt (raw data)
missing_stand_info = {}
raw_stand_freq = defaultdict(int)

with open('appendix7.1.txt', 'r') as f:
    lines = f.readlines()

# Count all stands in raw appendix7.1.txt
for line in lines[1:]:  # Skip header
    parts = line.split()
    if len(parts) >= 13:
        stand_raw = parts[12]
        if stand_raw not in ['n/a', 'blank']:
            raw_stand_freq[stand_raw] += 1

# Check missing stands
for stand_num in missing_stands:
    count = raw_stand_freq.get(str(stand_num), 0)
    missing_stand_info[stand_num] = count

print(f"\nStands present in raw appendix7.1.txt but not in sites_guild.txt:")
for stand_num in missing_stands:
    if missing_stand_info[stand_num] > 0:
        print(f"  Stand {stand_num}: {missing_stand_info[stand_num]} seals")

# Display stand types by frequency
cols = 5
print("\n" + "-" * 70)
print("TOP STAND TYPES BY FREQUENCY:\n")
for i in range(0, min(20, len(all_sorted)), cols):
    row = all_sorted[i:i+cols]
    freq_str = "  ".join(f"{s:>5}({stand_freq.get(s, 0):>2})" for s in row)
    print("  " + freq_str)

print("\n" + "-" * 70)
print("\nSAVING TO: guild_list_139.txt")
with open('guild_list_139.txt', 'w') as f:
    f.write("=" * 70 + "\n")
    f.write("ALL 139 OFFERING STAND TYPES FROM sites_guild.txt\n")
    f.write("=" * 70 + "\n")
    f.write(f"Total types: {len(stands)}\n")
    f.write(f"Jamison's Table 7.6 claim: 114 types\n")
    f.write(f"Appendix 7.1 actual count: {len(stands)} types\n\n")
    
    f.write("ANALYSIS OF STAND TYPE COUNTS\n")
    f.write("-" * 70 + "\n")
    f.write(f"Numeric stands in sites_guild.txt: {len(numeric_stands_set)}\n")
    f.write(f"Missing from 1-114 range: {missing_stands}\n")
    f.write(f"Variant stands (with letter suffixes): {len([s for s in all_sorted if not s.isdigit()])}\n\n")
    
    f.write("MISSING STANDS (consolidated or excluded):\n")
    for stand_num in missing_stands:
        count = missing_stand_info.get(stand_num, 0)
        if count > 0:
            f.write(f"  Stand {stand_num}: {count} seals in raw appendix7.1.txt -> consolidated/excluded\n")
        else:
            f.write(f"  Stand {stand_num}: not found in raw data\n")
    
    f.write(f"\nFormula: 114 (Jamison's base) -> {len(stands)} (actual in cleaned dataset)\n")
    f.write(f"  Stands consolidated/excluded: {len(missing_stands)}\n")
    f.write(f"  Variant types added: {len([s for s in all_sorted if not s.isdigit()])}\n\n")
    
    f.write("NUMERIC STANDS (1-114, minus consolidated):\n")
    f.write("-" * 70 + "\n")
    numeric_range = sorted([int(s) for s in all_sorted if s.isdigit()])
    f.write(", ".join(str(n) for n in numeric_range) + "\n\n")
    
    f.write("VARIANT STANDS (with letter suffixes):\n")
    f.write("-" * 70 + "\n")
    variants = sorted([s for s in all_sorted if not s.isdigit()])
    f.write(", ".join(variants) + "\n")
    f.write(f"Total variants: {len(variants)}\n\n")
    
    f.write("COMPLETE LIST (sorted by frequency, with seal counts):\n")
    f.write("-" * 70 + "\n")
    for stand in all_sorted:
        count = stand_freq.get(stand, 0)
        f.write(f"  {stand:>5}: {count:>3} seals\n")

print("Done! File saved to guild_list_139.txt")
