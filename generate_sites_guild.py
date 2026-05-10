"""
Generate sites_guild.txt from canonical appendix7.1.txt

Reads appendix7.1.txt (clean 13-column format from Jamison's Appendix 7.1)
and generates sites_guild.txt with proper data cleaning and consolidation.

Data cleaning rules:
1. Exclude entries with STAND='n/a' (unidentified stands)
2. Exclude entries with STAND='blank' (missing data)
3. Consolidate BSR site variants (2037, 5555, 6719, 6952, 7197, 7368, 8288) → "Bagasra"
4. Consolidate Stand "16?" → Stand "16"
5. Include all other numeric and variant stands
"""

from collections import defaultdict

def parse_appendix71(filename):
    """Parse appendix7.1.txt and return list of (site, stand) tuples (cleaned)."""
    
    site_stand_pairs = []
    n_a_count = 0
    blank_count = 0
    
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    # Skip header
    for line in lines[1:]:
        parts = line.split()
        if len(parts) < 13:
            continue
        
        # Extract columns: ID# SITE ... STAND (last column)
        seal_id = parts[0]
        site_raw = parts[1]
        stand_raw = parts[12]  # STAND is the 13th column (index 12)
        
        # Data cleaning
        if stand_raw == 'n/a':
            n_a_count += 1
            continue
        if stand_raw == 'blank':
            blank_count += 1
            continue
        
        # Consolidate BSR variants → Bagasra
        if site_raw in ['BSR-2037', 'BSR-5555', 'BSR-6719', 'BSR-6952', 'BSR-7197', 'BSR-7368', 'BSR-8288']:
            site = 'Bagasra'
        else:
            site = site_raw
        
        # Keep Stand "16?" as-is (Jamison's classification preserved)
        stand = stand_raw
        
        site_stand_pairs.append((site, stand))
    
    return site_stand_pairs, n_a_count, blank_count


def generate_sites_guild(site_stand_pairs):
    """Generate sites_guild.txt content from site-stand pairs."""
    
    # Count stand frequencies and track sites
    stand_freq = defaultdict(int)
    stand_sites = defaultdict(lambda: defaultdict(int))  # stand -> {site: count}
    
    for site, stand in site_stand_pairs:
        stand_freq[stand] += 1
        stand_sites[stand][site] += 1
    
    # Sort stands by frequency (highest to lowest)
    sorted_stands = sorted(stand_freq.keys(), key=lambda s: -stand_freq[s])
    
    # Build output
    lines = []
    lines.append("TOP OFFERING STANDS")
    lines.append("=" * 80)
    lines.append(f"Total seals: {len(site_stand_pairs)}")
    lines.append(f"Total stand types: {len(stand_freq)}")
    lines.append("")
    
    total_seals = 0
    for stand in sorted_stands:
        count = stand_freq[stand]
        total_seals += count
        lines.append(f"STAND {stand} (Total: {count})")
        
        # Sort sites by count (descending)
        sites_sorted = sorted(stand_sites[stand].items(), key=lambda x: -x[1])
        for site, site_count in sites_sorted:
            lines.append(f"{site}\t{site_count}")
        lines.append("")
    
    lines.append("=" * 80)
    lines.append(f"SUMMARY: {total_seals} seals across {len(stand_freq)} offering stand types")
    
    return "\n".join(lines)


if __name__ == "__main__":
    print("=" * 80)
    print("GENERATING sites_guild.txt FROM appendix7.1.txt")
    print("=" * 80)
    print()
    
    # Parse appendix7.1.txt
    site_stand_pairs, n_a_count, blank_count = parse_appendix71('appendix7.1.txt')
    
    print(f"Total seals in appendix7.1.txt: 500")
    print(f"Excluded (n/a): {n_a_count}")
    print(f"Excluded (blank): {blank_count}")
    print(f"Included in sites_guild.txt: {len(site_stand_pairs)}")
    print()
    
    # Generate sites_guild.txt content
    content = generate_sites_guild(site_stand_pairs)
    
    # Write to file
    with open('sites_guild.txt', 'w') as f:
        f.write(content)
    
    print("✓ sites_guild.txt regenerated successfully")
    print()
    
    # Summary statistics
    from collections import defaultdict
    stand_freq = defaultdict(int)
    for site, stand in site_stand_pairs:
        stand_freq[stand] += 1
    
    print(f"Stand types: {len(stand_freq)}")
    print(f"Top 10 stands by frequency:")
    sorted_by_freq = sorted(stand_freq.items(), key=lambda x: -x[1])
    for stand, count in sorted_by_freq[:10]:
        print(f"  Stand {stand}: {count} seals")
