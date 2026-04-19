import powerlaw
import matplotlib.pyplot as plt
import numpy as np

# Table 7.1: Distribution of unicorn seals by site (seals analyzed)
site_names = ["Harappa", "Mohenjo-daro", "Lothal", "Kalibangan", "Chanhu-daro",
              "Bagasra", "Dholavira", "Allahdino", "Balakot", "Nausharo",
              "Rakhigarhi", "Banawali", "Farmana", "Nindowari", "Jhukar",
              "Kot Diji", "Lohumjo-daro", "Pabumath", "Surkotada"
]

site_seals = [193, 191, 35, 24, 16,
             7, 6, 5, 4, 4,
             3, 3, 2, 2,
             1, 1, 1, 1, 1
]

data = site_seals

# Fit the data to a power law distribution (discrete since these are counts)
fit = powerlaw.Fit(data, discrete=True)

# Print the power law exponent and other metrics
print("alpha (power law exponent):", fit.power_law.alpha)
print("xmin (cutoff):", fit.power_law.xmin)
print("Kolmogorov-Smirnov distance (KS Statistic D):", fit.power_law.D)

# Goodness-of-fit test using bootstrap method (CSN 2009)
print("\nPerforming bootstrap goodness-of-fit test (2500 iterations)...")
print("This may take a few minutes...")
n_boot = 2500
observed_D = fit.power_law.D
n_data = len(data)
count_ge = 0
for i in range(n_boot): 
    synthetic_data = fit.power_law.generate_random(n_data)
    synthetic_fit = powerlaw.Fit(synthetic_data, discrete=True, xmin=fit.power_law.xmin)
    if synthetic_fit.power_law.D >= observed_D:
        count_ge += 1

p_value = count_ge / n_boot
print(f"Goodness-of-fit p-value: {p_value:.4f} ({count_ge}/{n_boot} synthetic D >= observed D)")

# Compare to alternative distributions (exponential, lognormal, stretched exponential, truncated power law)
for alt_dist in ['exponential', 'lognormal', 'stretched_exponential', 'truncated_power_law']:
    R, p = fit.distribution_compare('power_law', alt_dist)
    print(f"\nComparing power law to {alt_dist}:")
    print(f"Log-likelihood ratio (R): {R:.4f}")
    print(f"p-value: {p:.4f}")
    
# --- Plot 1: All 19 sites rank-frequency distribution with power law fit ---
freqs = np.array(sorted(data, reverse=True))
ranks = np.arange(1, len(freqs) + 1)

alpha = fit.power_law.alpha
C = freqs[0]
fit_line = C *(ranks ** (-1/(alpha - 1)))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

ax1.scatter(ranks, freqs, color='darkorange', s=60, zorder=3, label=f"Data ({len(data)} sites)")
ax1.plot(ranks, fit_line, 'r--', linewidth=2, label=f'Power law fit (α={alpha:.2f})')
ax1.set_xscale('log')
ax1.set_yscale('log')
ax1.set_xlabel('Site (ranked by seal count, log scale)', fontsize=12)
ax1.set_ylabel('Seal Analyzed (log scale)', fontsize=12)
ax1.set_title('a) All Sites - Rank-Frequency', fontsize=13)
ax1.legend(fontsize=10)
ax1.grid(True, which='both', ls=':', alpha=0.5)

# --- Plot 2: Labeled scatter (all sites named) ---
ax2.scatter(ranks, freqs, color='darkorange', s=60, zorder=3, label=f"Sites ({len(data)} total)")
ax2.plot(ranks, fit_line, 'r--', linewidth=2, label=f'Power law fit (α={alpha:.2f})')
for i, name in enumerate(site_names):
    offset = (5, 5) if freqs[i] > 10 else (5, -10)  # Offset labels for better visibility
    ax2.annotate(f'{name} ({freqs[i]})', (ranks[i], freqs[i]), textcoords="offset points", xytext=offset, ha='center', fontsize=7, color='dimgray')

ax2.set_xscale('log')
ax2.set_yscale('log')
ax2.set_xlabel('Site (ranked by seal count, log scale)', fontsize=12)
ax2.set_ylabel('Seal Analyzed (log scale)', fontsize=12)
ax2.set_title('b) All Sites - Labeled (by Site Name)', fontsize=13)
ax2.legend(fontsize=10)
ax2.grid(True, which='both', ls=':', alpha=0.5)

plt.tight_layout()
plt.savefig("sites.png", dpi=150)  # Save the figure as a high-res PNG
print("✓ Log-log plots saved to: sites.png")
plt.show()