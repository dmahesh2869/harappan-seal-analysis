"""
Clauset et al. (2009) Section 6: Test whether the exponential distribution
can be ruled out via its own GoF bootstrap using discrete methodology.

Uses a single constrained reconstruction with the same logic as synthetic_guild.py.
Implements discrete KS distance calculation matching powerlaw's methodology.
"""
import powerlaw
import numpy as np
import warnings

np.random.seed(42)

# --- Fixed data points ---
fixed = [44]  # Type #16
bin_20_49_options = [(a, 44 - a) for a in range(20, 25)]

def random_partition(total, n, lo, hi):
    while True:
        vals = np.random.randint(lo, hi + 1, size=n)
        diff = total - vals.sum()
        if diff == 0:
            return vals.tolist()
        indices = np.random.permutation(n)
        adjusted = vals.copy()
        for idx in indices:
            room = min(diff, hi - adjusted[idx]) if diff > 0 else max(diff, lo - adjusted[idx])
            adjusted[idx] += room
            diff -= room
            if diff == 0:
                break
        if diff == 0 and all(lo <= v <= hi for v in adjusted):
            return adjusted.tolist()

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

# Generate a reconstruction
split_20 = bin_20_49_options[np.random.randint(len(bin_20_49_options))]
bin_10_14 = random_partition(62, 5, 10, 14)
bin_5_9 = random_partition(100, 16, 5, 9)
bin_2_4 = random_partition(115, 40, 2, 4)
data = list(fixed) + list(split_20) + [15] + bin_10_14 + bin_5_9 + bin_2_4 + [1]*49

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
