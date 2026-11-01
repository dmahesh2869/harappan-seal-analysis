"""
Cross-site bundle agreement test.

Question: does the same offering stand carry the same attribute values
(neck, halter, ...) at different sites?

Statistic: among pairs of seals with the SAME stand but from DIFFERENT sites,
the fraction that share the same attribute value ("cross-site match rate").

Null: shuffle stand labels among seals within each site. This keeps each
site's stand mix and attribute habits intact, so a local carving tradition
alone cannot produce a high match rate; only stand-linked attribute
consistency across sites can.

Input: appendix7.1.txt (ID SITE EYE EAR HEAD HORN NECK HALTER TAIL LEG HOOF PIZZLE STAND)
"""

import numpy as np

SEED = 28031969
N_PERM = 2000
ATTRS = ['EYE', 'EAR', 'HEAD', 'HORN', 'NECK', 'HALTER', 'TAIL', 'LEG', 'HOOF', 'PIZZLE']
COLS = ['ID', 'SITE'] + ATTRS + ['STAND']
MISSING = {'n/a', 'blank'}


def load(path='appendix7.1.txt'):
    rows = []
    with open(path, 'r', encoding='utf-8') as f:
        next(f)
        for line in f:
            parts = line.split()
            if len(parts) == len(COLS):
                rows.append(dict(zip(COLS, parts)))
    return rows


def test_attribute(rows, attr, rng):
    """Return observed stats and permutation p-value for one attribute."""
    sub = [r for r in rows if r['STAND'] not in MISSING and r[attr] not in MISSING]
    site = np.array([r['SITE'] for r in sub])
    stand = np.array([r['STAND'] for r in sub])
    val = np.array([r[attr] for r in sub])

    site_c = np.unique(site, return_inverse=True)[1]
    val_c = np.unique(val, return_inverse=True)[1]
    stand_c = np.unique(stand, return_inverse=True)[1]
    ns, nv, nst = site_c.max() + 1, val_c.max() + 1, stand_c.max() + 1

    def rate(st):
        # Same-stand cross-site pairs = sum over stands of (N^2 - sum_site n^2)
        sv = np.bincount((st * ns + site_c) * nv + val_c, minlength=nst * ns * nv).reshape(nst, ns, nv)
        per_val = sv.sum(axis=1)
        matches = (per_val ** 2).sum() - (sv ** 2).sum()
        per_site = sv.sum(axis=2)
        n = (per_site.sum(axis=1) ** 2).sum() - (per_site ** 2).sum()
        return (matches / n if n else np.nan), n // 2

    obs, n_pairs = rate(stand_c)
    # Baseline: cross-site pairs with DIFFERENT stands
    match = val[:, None] == val[None, :]
    diff_site = site[:, None] != site[None, :]
    diff_stand = (stand[:, None] != stand[None, :]) & diff_site
    baseline = (match & diff_stand).sum() / diff_stand.sum()

    base_order = np.argsort(site_c, kind='stable')
    site_sorted = site_c[base_order]
    null = np.empty(N_PERM)
    for i in range(N_PERM):
        # Within-site shuffle: sort by (site, random key)
        order = np.lexsort((rng.random(len(site_c)), site_c))
        perm = np.empty_like(stand_c)
        perm[base_order] = stand_c[order]
        null[i], _ = rate(perm)

    p = (np.sum(null >= obs) + 1) / (N_PERM + 1)
    return {
        'attr': attr, 'n': len(sub), 'pairs': n_pairs,
        'obs': obs, 'baseline': baseline,
        'null_mean': np.nanmean(null), 'p': p,
    }


def per_stand(rows, attr, min_per_site=2, top=8):
    """Cross-site match rate for the most widely attested stands."""
    out = []
    stands = sorted({r['STAND'] for r in rows if r['STAND'] not in MISSING})
    for st in stands:
        sub = [r for r in rows if r['STAND'] == st and r[attr] not in MISSING]
        by_site = {}
        for r in sub:
            by_site.setdefault(r['SITE'], []).append(r[attr])
        by_site = {s: v for s, v in by_site.items() if len(v) >= min_per_site}
        if len(by_site) < 2:
            continue
        m = t = 0
        sites = list(by_site)
        for i in range(len(sites)):
            for j in range(i + 1, len(sites)):
                for a in by_site[sites[i]]:
                    for b in by_site[sites[j]]:
                        t += 1
                        m += a == b
        out.append((st, len(sites), sum(len(v) for v in by_site.values()), m / t))
    out.sort(key=lambda x: -x[2])
    return out[:top]


def main():
    rng = np.random.default_rng(SEED)
    rows = load()
    print(f"Seals parsed: {len(rows)}; random seed {SEED}; {N_PERM} permutations\n")

    print("CROSS-SITE MATCH RATE: same stand, different sites")
    print("(null = stands shuffled within each site)\n")
    print(f"{'Attr':8s}{'n':>5s}{'pairs':>8s}{'same-stand':>12s}{'diff-stand':>12s}{'null mean':>11s}{'p':>9s}")
    results = [test_attribute(rows, a, rng) for a in ATTRS]
    for r in results:
        print(f"{r['attr']:8s}{r['n']:5d}{r['pairs']:8d}{r['obs']:12.3f}{r['baseline']:12.3f}"
              f"{r['null_mean']:11.3f}{r['p']:9.4f}")

    sig = [r['attr'] for r in results if r['p'] < 0.05 / len(ATTRS)]
    print(f"\nSignificant after Bonferroni (alpha = {0.05/len(ATTRS):.4f}): {sig if sig else 'none'}")

    print("\nPER-STAND DETAIL (stands at 2+ sites, >=2 seals per site) for NECK and HALTER")
    for attr in ('NECK', 'HALTER'):
        print(f"\n{attr}: stand, sites, seals, cross-site match rate")
        for st, ns, n, m in per_stand(rows, attr):
            print(f"  stand {st:>4s}  {ns} sites  {n:3d} seals  match={m:.3f}")


if __name__ == '__main__':
    main()
