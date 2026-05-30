"""
Clauset et al. (2009) Section 6: Test whether the exponential distribution
can be ruled out via its own GoF bootstrap using discrete methodology.

Uses corrected Appendix 7.1 data from sites_guild.txt (consolidated, n/a and blank excluded).
413 seals, 139 offering stand types.
Implements discrete KS distance calculation matching powerlaw's methodology.
"""
import powerlaw
import numpy as np
import warnings

# Parse sites_guild.txt to get actual per-type frequencies
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

    # Return list of counts
    return list(stand_counts.values())

def discrete_ks_distance(data, cdf_func):
    """
    Compute Kolmogorov-Smirnov distance for discrete data.
    Matches powerlaw's methodology for discrete distributions.

    Parameters:
    - data: array of observed values (sorted)
    - cdf_func: function that takes x and returns theoretical CDF value

    Returns:
    - KS distance (maximum absolute difference between empirical and theoretical CDF)
    """
    data = np.sort(data)
    n = len(data)

    # Empirical CDF: at each point, the proportion of data <= that point
    empirical_cdf = np.arange(1, n + 1) / n
    theoretical_cdf = np.array([cdf_func(x) for x in data])

    # KS statistic is max absolute difference
    ks_distance = np.max(np.abs(empirical_cdf - theoretical_cdf))
    return ks_distance

def exponential_cdf(x, xmin, lambda_param):
    """CDF of shifted exponential: P(X <= x) for X ~ Exp(lambda) + xmin"""
    if x < xmin:
        return 0.0
    return 1.0 - np.exp(-lambda_param * (x - xmin))

data = parse_sites_guild('sites_guild.txt')

print(f"Data: {len(data)} types, {sum(data)} total seals")
print(f"Sorted (desc): {sorted(data, reverse=True)[:20]}...")

# Fit power law
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    fit = powerlaw.Fit(data, discrete=True, verbose=False)

print(f"Power law fit: alpha={fit.power_law.alpha:.4f}, xmin={fit.power_law.xmin}, D={fit.power_law.D:.4f}")

# Distribution comparison (likelihood ratio)
R, p = fit.distribution_compare('power_law', 'exponential')
print(f"PL vs Exponential LR: R={R:.4f}, p={p:.4f}")

# === Clauset et al. Section 6: Exponential GoF bootstrap (discrete methodology) ===
print(f"\n{'='*60}")
print(f"Clauset et al. competing distribution GoF test (discrete)")
print(f"{'='*60}")

xmin = fit.power_law.xmin
data_above = np.array([x for x in data if x >= xmin])
n_above = len(data_above)
print(f"Data above xmin={xmin}: {n_above} points")

# Fit exponential (shifted by xmin) via discrete MLE
# For exponential(λ) shifted by xmin: MLE λ = 1/mean(x - xmin)
shifted = data_above - xmin
mean_shifted = np.mean(shifted)
if mean_shifted == 0:
    mean_shifted = 0.5  # fallback
exp_lambda = 1.0 / mean_shifted

# Compute discrete KS distance for observed data
exp_D_obs = discrete_ks_distance(data_above,
                                  lambda x: exponential_cdf(x, xmin, exp_lambda))
print(f"Exponential MLE: lambda={exp_lambda:.4f}, scale={1/exp_lambda:.4f}")
print(f"Exponential KS D (observed): {exp_D_obs:.4f}")

# === Bootstrap GoF test (Clauset et al. methodology) ===
# Generate synthetic exponential data, fit, and compare KS distances
n_boot = 2500
count_ge = 0
print(f"Running {n_boot} bootstrap iterations...")

for j in range(n_boot):
    # Generate synthetic exponential data discretely
    syn = np.random.exponential(1.0/exp_lambda, n_above)
    syn = np.round(syn + xmin).astype(int)  # shift and discretize
    syn = syn[syn >= xmin]  # ensure all >= xmin

    if len(syn) < 5:
        continue

    # Refit exponential to synthetic data
    syn_shifted = syn - xmin
    syn_mean = np.mean(syn_shifted)
    if syn_mean == 0:
        syn_mean = 0.5
    syn_lambda = 1.0 / syn_mean

    # Compute discrete KS distance
    syn_D = discrete_ks_distance(syn, lambda x: exponential_cdf(x, xmin, syn_lambda))

    # Count how many synthetic D >= observed D
    if syn_D >= exp_D_obs:
        count_ge += 1

p_gof_exp = count_ge / n_boot
print(f"\nExponential GoF p-value: {p_gof_exp:.4f} ({count_ge}/{n_boot})")
if p_gof_exp < 0.1:
    print("=> EXPONENTIAL RULED OUT as a plausible model (p < 0.1)")
else:
    print("=> Exponential NOT ruled out (p >= 0.1)")
    print("   (Data is also consistent with an exponential distribution)")
