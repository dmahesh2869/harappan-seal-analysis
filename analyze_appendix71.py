"""
Power law analysis on complete Appendix 7.1 data (500 seals, 134 valid types).
Same methodology as analyze_guilds.py, using Alstott's powerlaw library.
"""

import powerlaw
import matplotlib.pyplot as plt
import numpy as np
import warnings

# Suppress scipy optimization warnings during bootstrap
warnings.filterwarnings('ignore', category=Warning)

# Frequency distribution of offering stand style (Appendix 7.1, all 134 types)
# Parse per-type counts directly from guilds_valid.txt
def parse_guilds_valid(filename):
    """Extract stand type counts from guilds_valid.txt"""
    counts = []
    with open(filename, 'r') as f:
        for line in f:
            if '=' in line or '-' in line or 'Stand Type' in line or 'TOTAL' in line or 'Valid Seals' in line:
                continue
            
            parts = line.strip().split()
            if len(parts) >= 2:
                try:
                    count = int(parts[1])
                    counts.append(count)
                except (ValueError, IndexError):
                    continue
    
    return counts

# Read the data
data = parse_guilds_valid('guilds_valid.txt')

# Fit the data to a power law distribution
fit = powerlaw.Fit(data, discrete=True)

# Print the power law exponent and other metrics
print("alpha (power law exponent):", fit.power_law.alpha)
print("xmin (cutoff):", fit.power_law.xmin)

# Goodness-of-fit test using Kolmogorov-Smirnov distance
print("Kolmogorov-Smirnov distance (KS Statistic D):", fit.power_law.D)

# Goodness-of-fit p-value using bootstrap method (Clauset et al. 2009)
# Generating synthetic datasets from the fitted power law, refit each and 
# compare the resulting KS Statistic to the original data's KS statistic

print("\nPerforming bootstrap goodness-of-fit test (2500 iterations)...")
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

# Compare to alternative distributions (exponential, lognormal, stretched exponential, truncated power law)
for alt_dist in ['exponential', 'lognormal', 'stretched_exponential', 'truncated_power_law']:
    R, p = fit.distribution_compare('power_law', alt_dist)
    print(f"\nComparing power law to {alt_dist}:")
    print(f"Log-likelihood ratio (R): {R:.4f}")
    print(f"p-value: {p:.4f}")

# Plot: Full rank-frequency distribution with power law fit (all 134 types)
freqs = np.array(sorted(data, reverse=True))
ranks = np.arange(1, len(freqs) + 1)

alpha = fit.power_law.alpha
C = freqs[0]
fit_line = C * (ranks ** (-1/(alpha - 1)))

fig, ax = plt.subplots(figsize=(10, 6))

ax.scatter(ranks, freqs, color='steelblue', s=40, zorder=3, label=f"Data ({len(data)} types)")
ax.plot(ranks, fit_line, 'r--', linewidth=2, label=f'Power Law Fit (α = {alpha:.2f})')
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('Type (ranked by frequency, log scale)', fontsize=12)
ax.set_ylabel('Frequency (log scale)', fontsize=12)
ax.set_title('All Types (134 types)', fontsize=13)
ax.legend(fontsize=10)
ax.grid(True, which='both', ls=':', alpha=0.5)

plt.tight_layout()
plt.show()
print("✓ Closed plot window")
