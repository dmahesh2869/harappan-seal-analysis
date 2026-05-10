"""
Power law analysis on complete Appendix 7.1 data.
Using sites_guild.txt with cleaned data (413 seals, 139 stand types).
Same methodology as analyze_guilds.py, using Alstott's powerlaw library.
"""

import powerlaw
import matplotlib.pyplot as plt
import numpy as np
import warnings
from collections import defaultdict

# Suppress scipy optimization warnings during bootstrap
warnings.filterwarnings('ignore', category=Warning)

# Extract frequency data from sites_guild.txt
def parse_sites_guild(filename):
    """Extract stand type counts from sites_guild.txt (consolidated, n/a and blank excluded)"""
    stand_counts = {}
    
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Look for STAND X (Total: Y) lines
            if line.startswith('STAND ') and '(Total:' in line:
                # Extract stand name and total count
                # Format: "STAND 16 (Total: 25)"
                parts = line.split('(Total:')
                if len(parts) == 2:
                    stand_name = parts[0].replace('STAND ', '').strip()
                    count_str = parts[1].replace(')', '').strip()
                    try:
                        total_count = int(count_str)
                        stand_counts[stand_name] = total_count
                    except ValueError:
                        continue
    
    # Return list of counts (not including stand names, just frequencies)
    return list(stand_counts.values()), stand_counts

# Read the corrected data
counts_list, stand_data = parse_sites_guild('sites_guild.txt')
data = counts_list
num_types = len(data)
total_seals = sum(data)

# Print dataset information
print("=" * 70)
print("POWER LAW ANALYSIS: COMPLETE APPENDIX 7.1 DATASET")
print("=" * 70)
print(f"Data source: sites_guild.txt")
print(f"Total seals analyzed: {total_seals}")
print(f"Offering stand types: {num_types}")
print("=" * 70)
print()

# Fit the data to a power law distribution
fit = powerlaw.Fit(data, discrete=True)

# Print the power law exponent and other metrics
print("POWER LAW ANALYSIS RESULTS")
print("-" * 70)
print(f"alpha (power law exponent): {fit.power_law.alpha:.4f}")
print(f"xmin (cutoff): {fit.power_law.xmin}")

# Goodness-of-fit test using Kolmogorov-Smirnov distance
print(f"Kolmogorov-Smirnov distance (KS Statistic D): {fit.power_law.D:.6f}")

# Goodness-of-fit p-value using bootstrap method (Clauset et al. 2009)
# Generating synthetic datasets from the fitted power law, refit each and 
# compare the resulting KS Statistic to the original data's KS statistic

print("\nPERFORMING BOOTSTRAP GOODNESS-OF-FIT TEST")
print("-" * 70)
print("Generating synthetic datasets from the fitted power law, refit each and")
print("compare the resulting KS Statistic to the original data's KS statistic")
print("(Clauset et al. 2009 methodology)")
print()
n_boot = 2500
observed_D = fit.power_law.D
n_data = len(data)
count_ge = 0
for i in range(n_boot):
    synthetic_data = fit.power_law.generate_random(n_data)
    synthetic_fit = powerlaw.Fit(synthetic_data, discrete=True, xmin=fit.power_law.xmin, verbose=False)
    if synthetic_fit.power_law.D >= observed_D:
        count_ge += 1
p_gof = count_ge / n_boot
print(f"Goodness-of-fit p-value: {p_gof:.4f} ({count_ge}/{n_boot} synthetic D >= observed D)")
print()
if p_gof > 0.05:
    print("[OK] RESULT: Consistent with power law (p > 0.05)")
    print("  The data are consistent with a power law distribution.")
else:
    print("[FAIL] RESULT: Less consistent with power law (p <= 0.05)")
    print("  The data show significant deviation from power law predictions.")
print()

# Compare to alternative distributions (exponential, lognormal, stretched exponential, truncated power law)
print("ALTERNATIVE DISTRIBUTION COMPARISONS")
print("-" * 70)
for alt_dist in ['exponential', 'lognormal', 'stretched_exponential', 'truncated_power_law']:
    R, p = fit.distribution_compare('power_law', alt_dist)
    print(f"\nPower law vs {alt_dist}:")
    print(f"  Log-likelihood ratio (R): {R:.4f}")
    print(f"  p-value: {p:.4f}")
    if R > 0:
        print(f"  → Power law is favored")
    elif R < 0:
        print(f"  → {alt_dist} is favored")
    else:
        print(f"  → Indifferent")
print()

# Plot: Full rank-frequency distribution with power law fit (corrected data)
freqs = np.array(sorted(data, reverse=True))
ranks = np.arange(1, len(freqs) + 1)

alpha = fit.power_law.alpha
C = freqs[0]
fit_line = C * (ranks ** (-1/(alpha - 1)))

fig, ax = plt.subplots(figsize=(10, 6))

ax.scatter(ranks, freqs, color='steelblue', s=40, zorder=3, label=f"Data ({num_types} types, {total_seals} seals)")
ax.plot(ranks, fit_line, 'r--', linewidth=2, label=f'Power Law Fit (α = {alpha:.2f})')
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('Type (ranked by frequency, log scale)', fontsize=12)
ax.set_ylabel('Frequency (log scale)', fontsize=12)
ax.set_title(f'Corrected All Types ({num_types} types, {total_seals} seals)\nvs. Paper claim (134 types, 500 seals)', fontsize=13)
ax.legend(fontsize=10)
ax.grid(True, which='both', ls=':', alpha=0.5)

plt.tight_layout()
plt.savefig('appendix71.png', dpi=150, bbox_inches='tight')
print("\nPLOTS SAVED")
print("-" * 70)
print("[OK] Plot saved to: appendix71.png")
print()

# Print summary
print("SUMMARY")
print("=" * 70)
print(f"Dataset: Corrected Appendix 7.1 analysis")
print(f"Seals: {total_seals}")
print(f"Types: {num_types}")
print(f"Power law exponent (α): {fit.power_law.alpha:.4f}")
print(f"Goodness-of-fit p-value: {p_gof:.4f}")
print(f"Status: {'[OK] VALID' if p_gof > 0.05 else '[FAIL] INVALID'} power law (p {'>' if p_gof > 0.05 else '<='} 0.05)")
print("=" * 70)
