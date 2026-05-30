"""
Synthetic guild frequency reconstruction.

We know the bin totals and counts from Jamison's Table 7.6,
plus specific data points from the text. This script generates
many plausible per-type frequency allocations consistent with
all constraints, fits a power law to each, and reports the
distribution of alpha and KS D values.
"""
import powerlaw
import numpy as np
from itertools import product as iterproduct

np.random.seed(42)
N_SAMPLES = 5000

# --- Fixed data points ---
# Type #16 = 44, one type in 15-19 bin = 15, 49 types at 1
fixed = [44]  # Type #16

# Types #32 and #44: two integers >= 20 summing to 44
# Possible: (20,24), (21,23), (22,22), (23,21), (24,20)
bin_20_49_options = [(a, 44 - a) for a in range(20, 25)]  # each must be >= 20, <= 44

# 15-19 bin: exactly 1 type with 15 seals
fixed_15 = [15]

# 10-14 bin: 5 types summing to 62, each in [10, 14]
def random_partition(total, n, lo, hi):
    """Generate a random partition of `total` into `n` integers each in [lo, hi]."""
    while True:
        vals = np.random.randint(lo, hi + 1, size=n)
        diff = total - vals.sum()
        if diff == 0:
            return vals.tolist()
        # Try to adjust
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

# Collect results
alphas = []
ks_ds = []
xmins = []
gof_pass = 0

print(f"Running {N_SAMPLES} synthetic reconstructions...")
for i in range(N_SAMPLES):
    # Pick a random split for #32 and #44
    split_20 = bin_20_49_options[np.random.randint(len(bin_20_49_options))]
    
    # Generate constrained random partitions for each bin
    bin_10_14 = random_partition(62, 5, 10, 14)
    bin_5_9 = random_partition(100, 16, 5, 9)
    bin_2_4 = random_partition(115, 40, 2, 4)
    bin_1 = [1] * 49
    
    # Assemble full dataset
    data = list(fixed) + list(split_20) + fixed_15 + bin_10_14 + bin_5_9 + bin_2_4 + bin_1
    
    assert len(data) == 114, f"Expected 114 types, got {len(data)}"
    assert sum(data) == 429, f"Expected 429 seals, got {sum(data)}"
    
    # Fit power law
    fit = powerlaw.Fit(data, discrete=True, verbose=False)
    alphas.append(fit.power_law.alpha)
    ks_ds.append(fit.power_law.D)
    xmins.append(fit.power_law.xmin)

alphas = np.array(alphas)
ks_ds = np.array(ks_ds)
xmins = np.array(xmins)

print(f"\n{'='*60}")
print(f"Results from {N_SAMPLES} synthetic reconstructions")
print(f"{'='*60}")
print(f"Alpha:  mean={alphas.mean():.4f}, std={alphas.std():.4f}, "
      f"median={np.median(alphas):.4f}, range=[{alphas.min():.4f}, {alphas.max():.4f}]")
print(f"KS D:   mean={ks_ds.mean():.4f}, std={ks_ds.std():.4f}, "
      f"median={np.median(ks_ds):.4f}, range=[{ks_ds.min():.4f}, {ks_ds.max():.4f}]")
print(f"xmin:   mean={xmins.mean():.4f}, std={xmins.std():.4f}, "
      f"median={np.median(xmins):.4f}, range=[{xmins.min():.4f}, {xmins.max():.4f}]")
print(f"\nxmin frequency distribution:")
unique_xmins, counts = np.unique(np.round(xmins, 1), return_counts=True)
for xval, cnt in sorted(zip(unique_xmins, counts), key=lambda x: -x[1])[:10]:  # Top 10
    print(f"  xmin ≈ {xval:.1f}: {cnt} reconstructions ({100*cnt/N_SAMPLES:.1f}%)")

# Compare with our bin-mean fit
print(f"\nBin-mean fit:  alpha=2.175, D=0.281")
print(f"Synthetic fit: alpha={alphas.mean():.3f} +/- {alphas.std():.3f}, "
      f"D={ks_ds.mean():.3f} +/- {ks_ds.std():.3f}")

# Percentiles
print(f"\nAlpha percentiles: 5th={np.percentile(alphas, 5):.4f}, "
      f"25th={np.percentile(alphas, 25):.4f}, "
      f"75th={np.percentile(alphas, 75):.4f}, "
      f"95th={np.percentile(alphas, 95):.4f}")
print(f"KS D percentiles:  5th={np.percentile(ks_ds, 5):.4f}, "
      f"25th={np.percentile(ks_ds, 25):.4f}, "
      f"75th={np.percentile(ks_ds, 75):.4f}, "
      f"95th={np.percentile(ks_ds, 95):.4f}")
print(f"xmin percentiles:  5th={np.percentile(xmins, 5):.4f}, "
      f"25th={np.percentile(xmins, 25):.4f}, "
      f"75th={np.percentile(xmins, 75):.4f}, "
      f"95th={np.percentile(xmins, 95):.4f}")

# Also do a GoF bootstrap on the median reconstruction
print(f"\nRunning GoF bootstrap on best reconstruction (closest to median alpha)...")
best_idx = np.argmin(np.abs(alphas - np.median(alphas)))
# Regenerate that specific reconstruction for the bootstrap
np.random.seed(best_idx)
split_20 = bin_20_49_options[np.random.randint(len(bin_20_49_options))]
bin_10_14 = random_partition(62, 5, 10, 14)
bin_5_9 = random_partition(100, 16, 5, 9)
bin_2_4 = random_partition(115, 40, 2, 4)
best_data = list(fixed) + list(split_20) + fixed_15 + bin_10_14 + bin_5_9 + bin_2_4 + [1]*49

best_fit = powerlaw.Fit(best_data, discrete=True, verbose=False)
print(f"Best reconstruction: alpha={best_fit.power_law.alpha:.4f}, xmin={best_fit.power_law.xmin}, D={best_fit.power_law.D:.4f}")

# Bootstrap GoF using discrete Clauset et al. methodology (works with v1.5 and v2)
def power_law_discrete_cdf(x, alpha, xmin):
    """Discrete power law CDF: P(X <= x)"""
    if x < xmin:
        return 0.0
    # Sum of x^(-alpha) for all integers from xmin to x, normalized
    zeta_xmin = sum([k**(-alpha) for k in range(int(xmin), int(x)+1)])
    zeta_total = sum([k**(-alpha) for k in range(int(xmin), 1000)])  # Approximate tail
    return zeta_xmin / zeta_total if zeta_total > 0 else 0.0

def discrete_ks_distance(data, cdf_func):
    """Compute KS distance for discrete data"""
    data = np.sort(data)
    n = len(data)
    empirical_cdf = np.arange(1, n + 1) / n
    theoretical_cdf = np.array([cdf_func(x) for x in data])
    return np.max(np.abs(empirical_cdf - theoretical_cdf))

n_boot = 2500
observed_D = best_fit.power_law.D
alpha = best_fit.power_law.alpha
xmin = best_fit.power_law.xmin
count_ge = 0

print(f"Running {n_boot} bootstrap iterations (discrete method)...")

for j in range(n_boot):
    # Generate synthetic power law data discretely
    # Use inverse transform sampling from uniform [0,1]
    uniform_samples = np.random.uniform(0, 1, 114)

    # For discrete power law: sample from CDF inverse
    # Simplified: sample proportionally to P(k) ∝ k^(-α)
    max_k = 100  # reasonable upper bound
    probs = np.array([k**(-alpha) for k in range(int(xmin), max_k)])
    probs = probs / probs.sum()
    synthetic = np.random.choice(range(int(xmin), max_k), size=114, p=probs)

    # Fit power law to synthetic data
    try:
        syn_fit = powerlaw.Fit(synthetic, xmin=xmin, discrete=True, verbose=False)
        if syn_fit.power_law.D >= observed_D:
            count_ge += 1
    except:
        pass  # Skip if fit fails

p_gof = count_ge / n_boot
print(f"GoF p-value: {p_gof:.4f} ({count_ge}/{n_boot})")

# Distribution comparisons on best reconstruction
print(f"\nDistribution comparisons (best reconstruction):")
for alt in ['lognormal', 'exponential', 'stretched_exponential', 'truncated_power_law']:
    R, p = best_fit.distribution_compare('power_law', alt)
    print(f"  Power law vs {alt}: R={R:.4f}, p={p:.4f}")
