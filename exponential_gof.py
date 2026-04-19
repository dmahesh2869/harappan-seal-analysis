"""
Clauset et al. (2009) Section 6: Test whether the exponential distribution
can be ruled out via its own GoF bootstrap.

Uses a single constrained reconstruction with the same logic as synthetic_guild.py.
"""
import powerlaw
import numpy as np
from scipy import stats
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

# === Clauset et al. Section 6: Exponential GoF bootstrap ===
print(f"\n{'='*60}")
print(f"Clauset et al. competing distribution GoF test")
print(f"{'='*60}")

xmin = fit.power_law.xmin
data_above = np.array([x for x in data if x >= xmin])
n_above = len(data_above)
print(f"Data above xmin={xmin}: {n_above} points")

# Fit exponential (shifted by xmin) via MLE
# For exponential(λ) shifted by xmin: f(x) = λ*exp(-λ*(x-xmin))
# MLE: λ = 1/mean(x - xmin)
shifted = data_above - xmin
mean_shifted = np.mean(shifted)
if mean_shifted == 0:
    mean_shifted = 0.5  # fallback for all-at-xmin case
exp_lambda = 1.0 / mean_shifted

# KS test: compare empirical CDF of data_above to exponential CDF
exp_D_obs = stats.kstest(data_above, 'expon', args=(xmin, 1.0/exp_lambda)).statistic
print(f"Exponential MLE: lambda={exp_lambda:.4f}, scale={1/exp_lambda:.4f}")
print(f"Exponential KS D (observed): {exp_D_obs:.4f}")

# Bootstrap
n_boot = 2500
count_ge = 0
print(f"Running {n_boot} bootstrap iterations...")
for j in range(n_boot):
    # Generate synthetic from fitted exponential
    syn = np.random.exponential(1.0/exp_lambda, n_above) + xmin
    syn = np.round(syn).astype(int)  # discretize
    syn = syn[syn >= xmin]
    if len(syn) < 5:
        continue
    # Refit exponential
    syn_shifted = syn - xmin
    syn_mean = np.mean(syn_shifted)
    if syn_mean == 0:
        syn_mean = 0.5
    syn_lambda = 1.0 / syn_mean
    syn_D = stats.kstest(syn, 'expon', args=(xmin, 1.0/syn_lambda)).statistic
    if syn_D >= exp_D_obs:
        count_ge += 1

p_gof_exp = count_ge / n_boot
print(f"\nExponential GoF p-value: {p_gof_exp:.4f} ({count_ge}/{n_boot})")
if p_gof_exp < 0.1:
    print("=> EXPONENTIAL RULED OUT as a plausible model (p < 0.1)")
else:
    print("=> Exponential NOT ruled out (p >= 0.1)")
    print("   (Data is also consistent with an exponential distribution)")
