import powerlaw
import matplotlib.pyplot as plt
import numpy as np

# Frequency distribution of offering stand style (Table 1)
# Using actual mean frequency per bin = Total Seals / Count of Types
data = []
data  += [88/3] * 3      # 3 types, mean frequency 29.33 (20-49 range)
data  += [15/1] * 1      # 1 type, mean frequency 15.00 (15-19 range)
data  += [62/5] * 5      # 5 types, mean frequency 12.40 (10-14 range)
data  += [100/16] * 16   # 16 types, mean frequency 6.25 (5-9 range)
data  += [115/40] * 40   # 40 types, mean frequency 2.875 (2-4 range)
data  += [49/49] * 49    # 49 types, mean frequency 1.00 (singleton types)

# Fit the data to a power law distribution
fit = powerlaw.Fit(data, discrete=False)

# Print the power law exponent and other metrics
print("alpha (power law exponent):", fit.power_law.alpha)
print("xmin (cutoff):", fit.power_law.xmin)

# Goodness-of-fit test using Kolmogorov-Smirnov distance
print("Kolmogorov-Smirnov distance (KS Statistic D):", fit.power_law.D)  

# Goodness-of-fit p-value using bootstrap method (CSN 2009)
# Generating synthetic datasets from the fitted power law, refit each and 
# compare the resulting KS Statistic to the original data's KS statistic

print("\nPerforming bootstrap goodness-of-fit test (2500 iterations)...")
print("This may take a few minutes...")
n_boot = 2500
observed_D = fit.power_law.D
n_data = len(data)
count_ge = 0
for i in range(n_boot): 
    synthetic_data = fit.power_law.generate_random(n_data)
    synthetic_fit = powerlaw.Fit(synthetic_data, discrete=False, xmin=fit.power_law.xmin)
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
    
#  --- Plot 1: Full rank-frequency distribution with power law fit (all 114 types) ---
freqs = np.array(sorted(data, reverse=True))
ranks = np.arange(1, len(freqs) + 1)

alpha = fit.power_law.alpha
C = freqs[0]
fit_line = C *(ranks ** (-1/(alpha - 1)))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

ax1.scatter(ranks, freqs, color='steelblue', s=40, zorder=3, label="Data (114 types)")
ax1.plot(ranks, fit_line, 'r--', linewidth=2, label=f'Power Law Fit (α = {alpha:.2f})')
ax1.set_xscale('log')
ax1.set_yscale('log')
ax1.set_xlabel('Type (ranked by frequency, log scale)', fontsize=12)
ax1.set_ylabel('Frequency (log scale))', fontsize=12)
ax1.set_title('(a) All Types (114 types)', fontsize=13)
ax1.legend(fontsize=10)
ax1.grid(True, which='both', ls =':', alpha=0.5)

# --- Plot 2: Bin centroids with power law fit (showing linear log-log trend) ---
bin_labels = ['20-49', '15-19', '10-14', '5-9', '2-4', '1']
bin_types = [3, 1, 5, 16, 40, 49]
bin_totals = [88, 15, 62, 100, 115, 49]
bin_means = [total/count for total, count in zip(bin_totals, bin_types)]

# Cumulative midpoint ranks for bins (middle of its rank range)
cum = 0
bin_ranks = []
for n in bin_types:
    bin_ranks.append(cum + (n + 1) / 2)  # Midpoint rank for the bin
    cum += n

bin_ranks = np.array(bin_ranks)
bin_means = np.array(bin_means)

fit_line_bins = C * (bin_ranks ** (-1/(alpha - 1)))

ax2.scatter(bin_ranks, bin_means, color='steelblue', s=80, zorder=3, label='Bin Centroids (6 bins)')
for i, lbl in enumerate(bin_labels):
    ax2.annotate(f'  {lbl}\n  ({bin_types[i]} types)', (bin_ranks[i], bin_means[i]), fontsize=8, color='dimgrey')

ax2.plot(bin_ranks, fit_line_bins, 'r--', linewidth=2, label=f'Power Law Fit (α = {alpha:.2f})')
ax2.set_xscale('log')
ax2.set_yscale('log')
ax2.set_xlabel('Type (ranked by frequency, log scale)', fontsize=12)
ax2.set_ylabel('Mean Frequency (log scale)', fontsize=12)
ax2.set_title('(b) Bin Centroids (6 bins)', fontsize=13)
ax2.legend(fontsize=10)
ax2.grid(True, which='both', ls =':', alpha=0.5)

plt.tight_layout()
plt.savefig('guilds.png', dpi=150)
print("[OK] Log-log plots saved to: guilds.png")
# plt.show()  # Uncomment to view plot interactively

