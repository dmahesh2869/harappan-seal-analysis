#!/usr/bin/env python3
"""
Diachronic Growth Analysis: Stand Types Increase Across 3A→3B→3C
Shows preferential attachment dynamics in fragmented supply chain
"""

def main():
    # Data from diachronic analysis
    periods = ['3A', '3B', '3C']
    num_stands = [3, 27, 42]
    total_seals = [4, 45, 93]
    alpha = [2.0820, 3.1241, 2.3253]
    gof_pvalue = [0.8490, 0.9850, 0.6690]
    
    print("=" * 80)
    print("DIACHRONIC GROWTH ANALYSIS: Market Evolution in Indus Seals")
    print("=" * 80)
    print()
    
    print("KEY FINDING: Stand Type Proliferation with Persistent Power Law")
    print("-" * 80)
    print()
    
    print("Period Progression:")
    print()
    for i, period in enumerate(periods):
        print(f"  {period}: {num_stands[i]:2d} distinct stands, {total_seals[i]:3d} total seals")
    
    print()
    
    # Growth rates
    growth_3a_to_3b = (num_stands[1] - num_stands[0]) / num_stands[0] * 100
    growth_3b_to_3c = (num_stands[2] - num_stands[1]) / num_stands[1] * 100
    total_growth = (num_stands[2] - num_stands[0]) / num_stands[0] * 100
    
    print("Growth Rates:")
    print(f"  3A → 3B: {growth_3a_to_3b:+.0f}% (3 → 27 stands)")
    print(f"  3B → 3C: {growth_3b_to_3c:+.0f}% (27 → 42 stands)")
    print(f"  Total:   {total_growth:+.0f}% (3 → 42 stands, 14x increase)")
    print()
    print()
    
    print("=" * 80)
    print("POWER LAW PERSISTENCE")
    print("=" * 80)
    print()
    
    for i, period in enumerate(periods):
        status = "✓ PASS" if gof_pvalue[i] > 0.05 else "✗ FAIL"
        print(f"  {period}: α = {alpha[i]:.4f}, p = {gof_pvalue[i]:.4f} {status}")
    
    print()
    print("All three periods consistent with power law (p > 0.05)")
    print("→ Power law persists despite 14x growth in stand types")
    print()
    print()
    
    print("=" * 80)
    print("INTERPRETATION: Preferential Attachment Dynamics")
    print("=" * 80)
    print()
    
    print("OBSERVATION 1: Explosive Growth Phase (3A → 3B)")
    print("-" * 80)
    print(f"  • 800% increase in stand types (3 → 27)")
    print(f"  • Total seals: 4 → 45 (1,025% increase)")
    print(f"  • Interpretation: Market rapidly developing, new workshop types emerging")
    print(f"  • Network dynamics: Explosive entry of new competitors")
    print()
    
    print("OBSERVATION 2: Stabilizing Growth Phase (3B → 3C)")
    print("-" * 80)
    print(f"  • 56% increase in stand types (27 → 42)")
    print(f"  • Total seals: 45 → 93 (107% increase)")
    print(f"  • Interpretation: Market maturing, growth rate declining")
    print(f"  • Network dynamics: Consolidation, market settling into equilibrium")
    print()
    
    print("OBSERVATION 3: Power Law Exponent Evolution")
    print("-" * 80)
    print(f"  • 3A: α = 2.08 (limited data, high inequality)")
    print(f"  • 3B: α = 3.12 (PEAK inequality - steepest rank/frequency decline)")
    print(f"  • 3C: α = 2.33 (moderate inequality - flattening out)")
    print()
    print("  Interpretation:")
    print("  - 3B shows STRONGEST preferential attachment (high α means top stands dominate)")
    print("  - 3C shows WEAKENING preferential attachment (new entrants gaining share)")
    print("  - Pattern: Growth phase creates 'winner-take-most', then more equitable")
    print()
    print()
    
    print("=" * 80)
    print("ALIGNMENT WITH FRAGMENTED SUPPLY CHAIN HYPOTHESIS")
    print("=" * 80)
    print()
    
    print("Why this growth pattern supports independent workshops + market hubs:")
    print()
    print("1. EXPLOSIVE GROWTH (3A→3B) shows ORGANIC MARKET EMERGENCE")
    print("   ✓ If centrally planned: would show gradual increase or no change")
    print("   ✓ Organic market: rapid emergence of competing stand types")
    print()
    
    print("2. PREFERENTIAL ATTACHMENT (α rising to 3.12 in 3B) shows HUB FORMATION")
    print("   ✓ Top stands (like Stand 16) become dominant through network effects")
    print("   ✓ Independent workshops adopt same stands → network externalities")
    print("   ✓ Small number of stands get adopted at multiple sites")
    print()
    
    print("3. POWER LAW PERSISTENCE shows SELF-ORGANIZING SYSTEM")
    print("   ✓ Across 14x growth, power law doesn't break")
    print("   ✓ Network maintains scale-free property (signature of self-organization)")
    print("   ✓ No central authority needed to maintain distribution")
    print()
    
    print("4. DECLINING ALPHA (3.12→2.33) shows MARKET OPENING")
    print("   ✓ As market matures, inequality decreases")
    print("   ✓ New entrants can compete with established stands")
    print("   ✓ Suggests competitive market, not monopoly")
    print()
    print()
    
    print("=" * 80)
    print("SUMMARY FOR PAPER")
    print("=" * 80)
    print()
    
    print("ONE-LINER FINDINGS:")
    print()
    print("1. STAND 16 PERSISTENCE:")
    print("   Stand 16 appears in both 3B (4 seals) and 3C (4 seals),")
    print("   suggesting a stable, widely-adopted offering type across periods.")
    print()
    
    print("2. POWER LAW ACROSS PERIODS:")
    print("   All three periods exhibit power law distributions (p > 0.05),")
    print("   indicating self-organizing market dynamics independent of period.")
    print()
    
    print("3. DIACHRONIC GROWTH WITH PREFERENTIAL ATTACHMENT:")
    print("   Stand types increase 14-fold (3→42) across periods,")
    print("   with power law exponent peaking in 3B (α=3.12),")
    print("   consistent with preferential attachment in fragmented networks.")
    print()
    
    print("=" * 80)
    print()


if __name__ == '__main__':
    main()
