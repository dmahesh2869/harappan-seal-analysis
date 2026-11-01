"""
Clauset et al. (2009) Section 6: Test whether the exponential distribution
can be ruled out via its own GoF bootstrap using discrete methodology.

Uses the last (Total) column of seal.db.txt as input, with the same
exponential fit / KS / bootstrap logic as exponential_gof.py.
"""
import powerlaw
import numpy as np
import warnings

from analyze_seal import parse_seal_db, SEED

np.random.seed(SEED)


def discrete_ks_distance(data, cdf_func):
    """Max absolute difference between empirical and theoretical CDF."""
    data = np.sort(data)
    n = len(data)
    empirical_cdf = np.arange(1, n + 1) / n
    theoretical_cdf = np.array([cdf_func(x) for x in data])
    return np.max(np.abs(empirical_cdf - theoretical_cdf))


def exponential_cdf(x, xmin, lambda_param):
    """CDF of shifted exponential: P(X <= x) for X ~ Exp(lambda) + xmin"""
    if x < xmin:
        return 0.0
    return 1.0 - np.exp(-lambda_param * (x - xmin))


_, totals = parse_seal_db()
data = [t for t in totals if t > 0]

print(f"Data: {len(data)} types, {sum(data)} total seals")
print(f"Sorted (desc): {sorted(data, reverse=True)}")
print(f"Random seed: {SEED}")

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    fit = powerlaw.Fit(data, discrete=True, verbose=False)
print(f"Power law fit: alpha={fit.power_law.alpha:.4f}, xmin={fit.power_law.xmin}, D={fit.power_law.D:.4f}")

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    R, p = fit.distribution_compare('power_law', 'exponential')
print(f"PL vs Exponential LR: R={R:.4f}, p={p:.4f}")

print(f"\n{'='*60}")
print("Clauset et al. competing distribution GoF test (discrete)")
print(f"{'='*60}")

xmin = fit.power_law.xmin
data_above = np.array([x for x in data if x >= xmin])
n_above = len(data_above)
print(f"Data above xmin={xmin}: {n_above} points")

# MLE for shifted exponential: lambda = 1/mean(x - xmin)
mean_shifted = np.mean(data_above - xmin)
if mean_shifted == 0:
    mean_shifted = 0.5
exp_lambda = 1.0 / mean_shifted

exp_D_obs = discrete_ks_distance(data_above,
                                 lambda x: exponential_cdf(x, xmin, exp_lambda))
print(f"Exponential MLE: lambda={exp_lambda:.4f}, scale={1/exp_lambda:.4f}")
print(f"Exponential KS D (observed): {exp_D_obs:.4f}")

n_boot = 2500
count_ge = 0
print(f"Running {n_boot} bootstrap iterations...")

for _ in range(n_boot):
    syn = np.random.exponential(1.0 / exp_lambda, n_above)
    syn = np.round(syn + xmin).astype(int)
    syn = syn[syn >= xmin]

    if len(syn) < 5:
        continue

    syn_mean = np.mean(syn - xmin)
    if syn_mean == 0:
        syn_mean = 0.5
    syn_lambda = 1.0 / syn_mean

    syn_D = discrete_ks_distance(syn, lambda x: exponential_cdf(x, xmin, syn_lambda))
    if syn_D >= exp_D_obs:
        count_ge += 1

p_gof_exp = count_ge / n_boot
print(f"\nExponential GoF p-value: {p_gof_exp:.4f} ({count_ge}/{n_boot})")
if p_gof_exp < 0.1:
    print("=> EXPONENTIAL RULED OUT as a plausible model (p < 0.1)")
else:
    print("=> Exponential NOT ruled out (p >= 0.1)")
    print("   (Data is also consistent with an exponential distribution)")
