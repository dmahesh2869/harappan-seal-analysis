"""
Power law analysis of seal motif frequencies from seal.db.txt.
Uses the last column (Total) of each motif row as input, with the same
fitting / goodness-of-fit approach as analyze_seal_attributes.py.
"""

import powerlaw
import numpy as np
import matplotlib.pyplot as plt

SEED = 28031969
SKIP_LABELS = ('Total Seals', 'Seal Impressions')


def parse_seal_db(path='seal.db.txt'):
    """Return (labels, totals) from the last column of each motif row."""
    labels, totals = [], []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if '|' not in line:
                continue
            parts = [p.strip() for p in line.split('|')]
            label, last = parts[0], parts[-1]
            if label.startswith('Iconographic') or label in SKIP_LABELS:
                continue
            if not last.isdigit():
                continue
            labels.append(label)
            totals.append(int(last))
    return labels, totals


def analyze(frequencies):
    """Fit power law and run bootstrap goodness-of-fit test."""
    fit = powerlaw.Fit(frequencies, discrete=True)

    n_boot = 2500
    observed_D = fit.power_law.D
    n_data = len(frequencies)
    count_ge = 0
    for _ in range(n_boot):
        synthetic_data = fit.power_law.generate_random(n_data)
        synthetic_fit = powerlaw.Fit(synthetic_data, discrete=True, xmin=fit.power_law.xmin)
        if synthetic_fit.power_law.D >= observed_D:
            count_ge += 1
    p_value = count_ge / n_boot
    return fit, p_value


def plot(frequencies, alpha, p_value, out='seal_power_law.png'):
    freqs = np.array(sorted(frequencies, reverse=True))
    ranks = np.arange(1, len(freqs) + 1)
    fit_line = freqs[0] * (ranks ** (-1 / (alpha - 1)))

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(ranks, freqs, s=50, alpha=0.6, zorder=3)
    ax.plot(ranks, fit_line, 'r--', linewidth=2, label=f'α={alpha:.2f}')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Rank')
    ax.set_ylabel('Frequency')
    ax.set_title(f'seal.db.txt motif totals (p={p_value:.3f})')
    ax.grid(True, which='both', ls=':', alpha=0.4)
    ax.legend()
    plt.tight_layout()
    plt.savefig(out, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Plot saved to: {out}")


def main():
    # powerlaw draws from numpy's global RNG
    np.random.seed(SEED)
    labels, totals = parse_seal_db()
    # Zero-count rows cannot be fitted
    frequencies = [t for t in totals if t > 0]

    fit, p_value = analyze(frequencies)

    print("=" * 60)
    print("POWER LAW FIT: seal.db.txt (Total column)")
    print("=" * 60)
    print(f"Random seed:        {SEED}")
    print(f"Motif types:        {len(frequencies)}")
    print(f"Total seals:        {sum(frequencies)}")
    print(f"alpha:              {fit.power_law.alpha:.4f}")
    print(f"sigma (alpha err):  {fit.power_law.sigma:.4f}")
    print(f"xmin:               {fit.power_law.xmin}")
    print(f"KS distance D:      {fit.power_law.D:.4f}")
    print(f"GOF p-value:        {p_value:.4f} "
          f"({'plausible power law' if p_value >= 0.1 else 'power law rejected'})")

    for alt in ('lognormal', 'exponential', 'truncated_power_law'):
        R, p = fit.distribution_compare('power_law', alt)
        print(f"vs {alt:20s} R={R:8.4f}  p={p:.4f}")

    plot(frequencies, fit.power_law.alpha, p_value)


if __name__ == '__main__':
    main()
