"""
Bipartite Network Analysis: Sites ↔ Offering Stands (Guilds)
Comprehensive network analysis with multiple visualizations:

Outputs:
- bipartite_network.png: Full network graph (all 139 guilds + 17 sites)
- geographical_network.png: Geographic map with site locations and seal counts
- hub_guilds.png: Bar charts showing hub guild frequencies and reach
- hub_guild_geographic_overlay.png: Geographic overlay of top 8 hub guilds
- site_overlap_chord.png: Chord diagram showing site-to-site guild overlap

Methodology:
- Constructs bipartite network of sites ↔ offering stand types
- Identifies hub guilds (multi-site presence) suggesting standardized practices
- Computes site-to-site guild overlap as evidence of network coordination
- Generates quantitative and spatial visualizations
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from networkx.algorithms import bipartite
from matplotlib.patches import PathPatch
from matplotlib.path import Path
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# 1. PARSE SITES GUILD (CANONICAL CLEANED DATA)
# ============================================================================

def parse_sites_guild(filepath):
    """Parse sites_guild.txt and return a DataFrame with site-stand pairs."""
    data = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    current_stand = None
    in_stand_section = False
    
    for line in lines:
        line = line.rstrip('\n')
        
        # Look for STAND X (Total: Y) headers
        if line.startswith('STAND ') and '(Total:' in line:
            # Extract stand name
            parts = line.split('(Total:')
            if len(parts) == 2:
                current_stand = parts[0].replace('STAND ', '').strip()
                in_stand_section = True
            continue
        
        # Skip header lines and separators
        if 'Site' in line and 'Count' in line:
            continue
        if '---' in line:
            continue
        if '===' in line:
            in_stand_section = False
            continue
        
        # Parse data lines (Site \t Count format)
        if in_stand_section and current_stand and line.strip():
            parts = line.split()
            if len(parts) >= 2:
                # Handle multi-word site names
                try:
                    # Last part should be the count
                    count = int(parts[-1])
                    # Everything before count is the site name
                    site_name = ' '.join(parts[:-1])
                    
                    # Add individual seal records (one record per seal)
                    for _ in range(count):
                        data.append({
                            'Site_Name': site_name,
                            'Stand': current_stand
                        })
                except (ValueError, IndexError):
                    # Skip lines that don't parse correctly
                    continue
    
    df = pd.DataFrame(data)
    return df.reset_index(drop=True) if len(df) > 0 else df

# ============================================================================
# 2. BUILD CONNECTIVITY MATRICES
# ============================================================================

def build_site_stand_network(df):
    """
    Build bipartite network: Sites (left nodes) ↔ Stands/Guilds (right nodes)
    Returns:
    - B: bipartite graph (networkx)
    - site_to_stands: dict mapping site name to list of stands
    - stand_to_sites: dict mapping stand to list of sites
    """
    
    # Create bipartite graph
    B = nx.Graph()
    
    # Add nodes with bipartite attribute
    sites = df['Site_Name'].unique()
    stands = df['Stand'].unique()
    
    B.add_nodes_from(sites, bipartite=0)  # Left partition (sites)
    B.add_nodes_from(stands, bipartite=1)  # Right partition (stands/guilds)
    
    # Add edges
    for _, row in df.iterrows():
        B.add_edge(row['Site_Name'], row['Stand'])
    
    # Build lookup dicts
    site_to_stands = defaultdict(list)
    stand_to_sites = defaultdict(list)
    
    for _, row in df.iterrows():
        site_to_stands[row['Site_Name']].append(row['Stand'])
        stand_to_sites[row['Stand']].append(row['Site_Name'])
    
    # Remove duplicates and sort
    for key in site_to_stands:
        site_to_stands[key] = sorted(list(set(site_to_stands[key])))
    for key in stand_to_sites:
        stand_to_sites[key] = sorted(list(set(stand_to_sites[key])))
    
    return B, site_to_stands, stand_to_sites

# ============================================================================
# 3. NETWORK METRICS
# ============================================================================

def compute_metrics(B, site_to_stands, stand_to_sites):
    """Compute bipartite network metrics."""
    
    sites = {n for n, d in B.nodes(data=True) if d['bipartite'] == 0}
    stands = set(B) - sites
    
    # Degree (connectivity) for each site
    site_degrees = {}
    for site in sites:
        site_degrees[site] = len(site_to_stands[site])
    
    # Degree for each stand
    stand_degrees = {}
    for stand in stands:
        stand_degrees[stand] = len(stand_to_sites[stand])
    
    # Network density (bipartite)
    density = bipartite.density(B, sites)
    
    # Number of components
    n_components = nx.number_connected_components(B)
    
    return {
        'site_degrees': site_degrees,
        'stand_degrees': stand_degrees,
        'density': density,
        'n_components': n_components,
        'n_sites': len(sites),
        'n_stands': len(stands),
        'n_edges': B.number_of_edges()
    }

# ============================================================================
# 4. GEOGRAPHICAL DATA (INDUS VALLEY CIVILIZATION SITES)
# ============================================================================

def get_site_coordinates():
    """
    Approximate geographical coordinates for Harappan sites
    (Latitude, Longitude) - based on standard archaeological references
    """
    coords = {
        'Harappa': (30.6236, 72.8042),
        'Mohenjo-daro': (27.3347, 68.1374),
        'Dholavira': (23.8859, 70.2157),
        'Lothal': (22.5224, 72.2423),
        'Kalibangan': (29.1286, 74.3044),
        'Chanhu-daro': (24.8542, 68.5156),
        'Banawali': (29.0928, 77.3261),
        'Allahdino': (25.2128, 68.4108),
        'Balakot': (25.3678, 67.2308),
        'Nausharo': (27.5614, 68.4083),
        'Rakigarhi': (29.3206, 77.9061),  # Easternmost site (without 'h')
        'Farmana': (29.1867, 77.5511),
        'Nindowari': (25.3544, 67.3208),
        'Jhukar': (25.1667, 68.0833),
        'Kot Diji': (28.0578, 69.5083),
        'Lohumjodaro': (27.4033, 68.4719),
        'Pabumath': (25.9428, 68.9039),
        'Surkotada': (23.0542, 69.6625),
        'Bagasra': (22.1311, 70.1261),
    }
    return coords

# ============================================================================
# 5. VISUALIZATION 1: BIPARTITE GRAPH LAYOUT
# ============================================================================

def visualize_bipartite_network(B, site_to_stands, stand_to_sites):
    """Create a two-column bipartite layout visualization."""
    
    sites = {n for n, d in B.nodes(data=True) if d['bipartite'] == 0}
    stands = set(B) - sites
    
    # Create positions: sites on left, stands on right
    pos = {}
    
    # Sort sites by number of connections (for visual hierarchy)
    site_list = sorted(sites, key=lambda x: len(site_to_stands[x]), reverse=True)
    for i, site in enumerate(site_list):
        pos[site] = (0, -i * 0.5)
    
    # Sort stands by number of connections
    stand_list = sorted(stands, key=lambda x: len(stand_to_sites[x]), reverse=True)
    for i, stand in enumerate(stand_list):
        pos[stand] = (10, -i * 0.15)
    
    # Draw
    fig, ax = plt.subplots(figsize=(16, 20))
    
    # Draw edges with transparency (fewer opacity)
    nx.draw_networkx_edges(B, pos, ax=ax, alpha=0.1, width=0.5, edge_color='gray')
    
    # Draw site nodes (left, larger)
    nx.draw_networkx_nodes(B, pos, nodelist=sites, node_color='#FF6B6B', 
                          node_size=800, ax=ax, label='Sites')
    
    # Draw stand nodes (right, smaller, color by degree)
    stand_degrees = [len(stand_to_sites[s]) for s in stands]
    nodes = nx.draw_networkx_nodes(B, pos, nodelist=stands, 
                                   node_color=stand_degrees, 
                                   cmap='YlOrRd', node_size=300, ax=ax, 
                                   label='Stands/Guilds')
    
    # Draw labels
    nx.draw_networkx_labels(B, pos, labels={s: s for s in sites}, 
                           font_size=9, font_weight='bold', ax=ax)
    nx.draw_networkx_labels(B, pos, labels={s: s for s in stands}, 
                           font_size=7, ax=ax)
    
    ax.set_title('Bipartite Network: Harappan Sites ↔ Offering Stand Guilds', 
                fontsize=16, fontweight='bold')
    ax.legend(scatterpoints=1, loc='upper left', fontsize=12)
    ax.axis('off')
    
    # Add colorbar for stand degree
    sm = plt.cm.ScalarMappable(cmap='YlOrRd', 
                              norm=plt.Normalize(vmin=min(stand_degrees), 
                                               vmax=max(stand_degrees)))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, label='Number of Sites (Guild Reach)')
    
    plt.tight_layout()
    plt.savefig('bipartite_network.png', dpi=150, bbox_inches='tight')
    print("[OK] Bipartite network visualization saved to: bipartite_network.png")
    plt.close()

# ============================================================================
# 6. VISUALIZATION 2: GEOGRAPHICAL MAP WITH NETWORK OVERLAY
# ============================================================================

def visualize_geographical_network(df, site_to_stands, stand_to_sites):
    """Create geographical map with site locations and network connections.
    
    Features:
    - Sites sized by seal count
    - Sites colored by stand diversity
    - Smart label positioning to avoid overlaps
    - Slight nudging of overlapping sites for clarity
    """
    
    coords = get_site_coordinates()
    
    # Aggregate data by site
    site_seal_counts = df.groupby('Site_Name').size()
    site_stand_counts = {site: len(stands) for site, stands in site_to_stands.items()}
    
    # Detect overlapping sites (within 0.5 degrees)
    overlapping_pairs = []
    sites_list = list(coords.keys())
    for i, site1 in enumerate(sites_list):
        for site2 in sites_list[i+1:]:
            lat1, lon1 = coords[site1]
            lat2, lon2 = coords[site2]
            dist = np.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)
            
            if dist < 0.5:
                overlapping_pairs.append((site1, site2))
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 12))
    
    # Plot background (approximate Indus Valley region)
    ax.set_xlim(66, 79)
    ax.set_ylim(21, 33)
    
    # Add grid
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    
    # Draw sites as nodes, sized by number of seals
    for site, (lat, lon) in coords.items():
        if site in site_seal_counts:
            n_seals = site_seal_counts[site]
            n_stands = site_stand_counts[site]
            
            # Size proportional to log(seals) for better scaling
            # Boost size for major hubs (Mohenjo-daro and Harappa)
            base_size = 100 + 50 * np.log(n_seals)
            if site in ['Mohenjo-daro', 'Harappa']:
                size = base_size * 1.5  # Increase major hub sizes
            else:
                size = base_size
            
            # Color by stand diversity
            color_intensity = n_stands / max(site_stand_counts.values())
            
            # Put Mohenjo-daro in foreground (higher z-order)
            zorder = 5 if site == 'Mohenjo-daro' else (4 if site == 'Harappa' else 3)
            ax.scatter(lon, lat, s=size, alpha=0.7, 
                      c=[[color_intensity, 0.3, 1-color_intensity]], 
                      edgecolors='black', linewidth=2, zorder=zorder)
            
            # Determine label position based on map quadrant
            map_center_lon = 72.5
            map_center_lat = 27.0
            
            dx, dy = 0.4, 0.4  # Default offset
            ha, va = 'left', 'bottom'
            
            if lon < map_center_lon and lat > map_center_lat:
                # Upper left
                dx, dy = -0.4, 0.4
                ha, va = 'right', 'bottom'
            elif lon >= map_center_lon and lat > map_center_lat:
                # Upper right
                dx, dy = 0.4, 0.4
                ha, va = 'left', 'bottom'
            elif lon < map_center_lon and lat <= map_center_lat:
                # Lower left
                dx, dy = -0.4, -0.4
                ha, va = 'right', 'top'
            else:
                # Lower right
                dx, dy = 0.4, -0.4
                ha, va = 'left', 'top'
            
            # Extra nudging for overlapping pairs
            for pair in overlapping_pairs:
                if site == pair[0]:
                    if 'left' in ha:
                        dx -= 0.3
                    else:
                        dx += 0.3
                    if 'bottom' in va:
                        dy += 0.2
                    else:
                        dy -= 0.2
                elif site == pair[1]:
                    if 'left' in ha:
                        dx += 0.3
                    else:
                        dx -= 0.3
                    if 'bottom' in va:
                        dy -= 0.2
                    else:
                        dy += 0.2
            
            # Special nudging for Mohenjo-daro to avoid Nausharo overlap
            if site == 'Mohenjo-daro':
                dx -= 0.5  # Push left
                dy -= 0.3  # Push down
            
            # Special handling for Mohenjo-daro: force it in foreground
            text_zorder = 15 if site == 'Mohenjo-daro' else 5
            ax.text(lon + dx, lat + dy, f'{site}\n({n_seals}s, {n_stands}g)', 
                   fontsize=8, ha=ha, va=va, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.4),
                   zorder=text_zorder)
    
    ax.set_xlabel('Longitude (E)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Latitude (N)', fontsize=12, fontweight='bold')
    ax.set_title('Harappan Sites: Geographical Distribution\n' +
                '(Node size ∝ seals; Color: stand diversity; s=seals, g=guilds; Positions adjusted for clarity)', 
                fontsize=13, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('geographical_network.png', dpi=150, bbox_inches='tight')
    print("[OK] Geographical network map saved to: geographical_network.png")
    plt.close()

# ============================================================================
# 7. VISUALIZATION 3: HUB STANDS (GUILDS WITH MULTI-SITE PRESENCE)
# ============================================================================

def visualize_hub_guilds(stand_to_sites, site_seal_counts):
    """Identify and visualize guilds that appear at multiple sites."""
    
    # Filter stands that appear at multiple sites
    hub_stands = {stand: sites for stand, sites in stand_to_sites.items() 
                  if len(sites) >= 2}
    
    # Sort by geographic reach
    hub_stands_sorted = sorted(hub_stands.items(), 
                               key=lambda x: len(x[1]), reverse=True)
    
    print("\n" + "="*70)
    print("HUB GUILDS (Multi-site presence)")
    print("="*70)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
    
    # Plot 1: Hub stands by reach (with Stand type on y-axis)
    stands, reach = zip(*hub_stands_sorted[:30])  # Top 30
    reach = [len(h) for s, h in hub_stands_sorted[:30]]
    stand_labels = [f'Stand {s}' for s in stands]  # Explicit Stand labels
    
    ax1.barh(range(len(stands)), reach, color='steelblue', edgecolor='black')
    ax1.set_yticks(range(len(stands)))
    ax1.set_yticklabels(stand_labels, fontsize=8)
    ax1.set_xlabel('Number of Sites', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Stand Type', fontsize=12, fontweight='bold')
    ax1.set_title('Top Hub Guilds by Geographic Reach', fontsize=12, fontweight='bold')
    ax1.invert_yaxis()
    ax1.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, v in enumerate(reach):
        ax1.text(v + 0.05, i, str(v), va='center', fontsize=9)
    
    # Plot 2: Distribution of reach
    all_reach = [len(sites) for sites in stand_to_sites.values()]
    reach_counts = {}
    for r in all_reach:
        reach_counts[r] = reach_counts.get(r, 0) + 1
    
    reach_vals = sorted(reach_counts.keys())
    counts = [reach_counts[r] for r in reach_vals]
    
    ax2.bar(reach_vals, counts, color='coral', edgecolor='black', width=0.8)
    ax2.set_xlabel('Number of Sites per Guild', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Number of Guilds', fontsize=11, fontweight='bold')
    ax2.set_title('Guild Distribution by Geographic Reach', fontsize=12, fontweight='bold')
    ax2.set_xticks(reach_vals)
    ax2.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('hub_guilds.png', dpi=150, bbox_inches='tight')
    print("[OK] Hub guilds visualization saved to: hub_guilds.png")
    plt.close()
    
    # Print top hub guilds
    for stand, sites in hub_stands_sorted[:20]:
        print(f"Guild {stand:>5}: {len(sites)} sites - {', '.join(sites)}")

# ============================================================================
# 8. VISUALIZATION 4: HUB GUILD GEOGRAPHIC OVERLAY
# ============================================================================

def create_curved_connection(ax, coord1, coord2, color, alpha=0.7, linewidth=2.5):
    """Create a curved connection between two sites using Bezier curve."""
    y = [coord1[0], coord2[0]]
    x = [coord1[1], coord2[1]]
    
    # Calculate midpoint and perpendicular offset for curve
    mid_x, mid_y = (x[0] + x[1]) / 2, (y[0] + y[1]) / 2
    
    # Distance between points
    dist = np.sqrt((x[1] - x[0])**2 + (y[1] - y[0])**2)
    
    # Offset perpendicular to line for curve
    if dist > 0:
        offset = dist * 0.15
        perp_x = -(y[1] - y[0]) / dist * offset
        perp_y = (x[1] - x[0]) / dist * offset
    else:
        perp_x = perp_y = 0
    
    # Control point for Bezier curve
    control_x = mid_x + perp_x
    control_y = mid_y + perp_y
    
    # Draw cubic Bezier curve
    verts = [(x[0], y[0]), (control_x, control_y), (x[1], y[1])]
    codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3]
    path = Path(verts, codes)
    
    patch = PathPatch(path, facecolor='none', edgecolor=color, 
                     alpha=alpha, linewidth=linewidth)
    ax.add_patch(patch)

def get_top_hub_guilds(stand_to_sites, guild_freq, n_top=8):
    """Identify top guilds with multi-site presence, ranked by frequency."""
    top_guilds = []
    
    # Sort by frequency (descending)
    sorted_guilds = sorted(guild_freq.items(), key=lambda x: -x[1])
    
    for guild, freq in sorted_guilds:
        if len(stand_to_sites[guild]) > 1:  # Multi-site guilds only
            top_guilds.append(guild)
            if len(top_guilds) >= n_top:
                break
    
    return top_guilds

def visualize_hub_guild_overlay(stand_to_sites, guild_freq, df):
    """Create geographic overlay showing top 8 hub guilds with curved arcs."""
    
    coords = get_site_coordinates()
    site_seal_counts = df.groupby('Site_Name').size()
    
    # Color palette for guilds (highly saturated, distinct colors)
    colors = ['#E41A1C', '#377EB8', '#4DAF4A', '#FF7F00', '#984EA3', 
              '#A65628', '#F781BF', '#999999']
    
    # Get top hub guilds
    top_guilds = get_top_hub_guilds(stand_to_sites, guild_freq, n_top=8)
    
    fig, ax = plt.subplots(figsize=(16, 12))
    
    # Set geographic bounds
    ax.set_xlim(66, 79)
    ax.set_ylim(21, 33)
    ax.grid(True, alpha=0.2, linestyle='--')
    
    # Calculate map center for smart label positioning
    map_center_lon = 72.5  # (66 + 79) / 2
    map_center_lat = 27.0  # (21 + 33) / 2
    
    # Detect overlapping sites (within 0.5 degrees of each other)
    overlapping_pairs = []
    sites_list = list(coords.items())
    for i, (site1, (lat1, lon1)) in enumerate(sites_list):
        for site2, (lat2, lon2) in sites_list[i+1:]:
            dist = np.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)
            if dist < 0.5:  # Sites too close
                overlapping_pairs.append((site1, site2))
    
    # Plot all sites with smart label positioning
    for site_name, (lat, lon) in coords.items():
        n_seals = site_seal_counts.get(site_name, 0)
        if n_seals > 0:
            # Boost size for major hubs (Mohenjo-daro and Harappa)
            base_size = 100 + 50 * np.log(n_seals)
            if site_name in ['Mohenjo-daro', 'Harappa']:
                size = base_size * 1.5  # Increase major hub sizes
            else:
                size = base_size
            
            # Put Mohenjo-daro in foreground (higher z-order)
            zorder = 11 if site_name == 'Mohenjo-daro' else (10 if site_name == 'Harappa' else 9)
            ax.scatter(lon, lat, s=size, color='darkblue', zorder=zorder, edgecolors='black', linewidth=1.5)
            
            # Smart label positioning: offset depends on quadrant
            offset = 0.5
            dx, dy = 0.3, 0.3
            
            # Determine which quadrant the site is in relative to map center
            if lon < map_center_lon and lat > map_center_lat:
                # Upper left -> label to the left and up
                dx, dy = -offset, offset
                ha, va = 'right', 'bottom'
            elif lon >= map_center_lon and lat > map_center_lat:
                # Upper right -> label to the right and up
                dx, dy = offset, offset
                ha, va = 'left', 'bottom'
            elif lon < map_center_lon and lat <= map_center_lat:
                # Lower left -> label to the left and down
                dx, dy = -offset, -offset
                ha, va = 'right', 'top'
            else:
                # Lower right -> label to the right and down
                dx, dy = offset, -offset
                ha, va = 'left', 'top'
            
            # Extra nudging for known overlapping pairs
            for pair in overlapping_pairs:
                if site_name == pair[0]:
                    # Nudge first site of pair in opposite direction
                    if 'left' in ha:
                        dx -= 0.3
                    else:
                        dx += 0.3
                    if 'bottom' in va:
                        dy += 0.2
                    else:
                        dy -= 0.2
                elif site_name == pair[1]:
                    # Nudge second site of pair opposite way
                    if 'left' in ha:
                        dx += 0.3
                    else:
                        dx -= 0.3
                    if 'bottom' in va:
                        dy -= 0.2
                    else:
                        dy += 0.2
            
            ax.text(lon + dx, lat + dy, site_name, fontsize=9, fontweight='bold', 
                   zorder=11, ha=ha, va=va)
    
    # Draw connections for each top guild
    for idx, guild in enumerate(top_guilds):
        color = colors[idx % len(colors)]
        sites = sorted(list(stand_to_sites[guild]))
        freq = guild_freq[guild]
        
        # Draw connections between all pairs of sites with this guild
        for i in range(len(sites)):
            for j in range(i + 1, len(sites)):
                site1 = sites[i]
                site2 = sites[j]
                
                if site1 in coords and site2 in coords:
                    coord1 = coords[site1]
                    coord2 = coords[site2]
                    create_curved_connection(ax, coord1, coord2, color, alpha=0.6, linewidth=2.5)
    
    # Create legend
    legend_elements = []
    for idx, guild in enumerate(top_guilds):
        color = colors[idx % len(colors)]
        freq = guild_freq[guild]
        n_sites = len(stand_to_sites[guild])
        label = f"Stand {guild:3s} ({freq:2d} seals, {n_sites} sites)"
        legend_elements.append(Line2D([0], [0], color=color, linewidth=3.5, label=label))
    
    ax.legend(handles=legend_elements, loc='upper left', fontsize=11, 
              title='Hub Offering Stand Types (Multi-site Presence)', 
              title_fontsize=12, framealpha=0.95, edgecolor='black')
    
    ax.set_xlabel('Longitude (E)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Latitude (N)', fontsize=12, fontweight='bold')
    ax.set_title('Hub Guild Geographic Distribution: Multi-site Offering Stand Types\n' +
                 '(Curved arcs show offering stand types shared between sites)', 
                 fontsize=14, fontweight='bold', pad=15)
    
    # Add annotation
    ax.text(0.02, 0.02, 'Indus Valley Civilization\nOffering Stand Standardization',
            transform=ax.transAxes, fontsize=10, verticalalignment='bottom',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('hub_guild_geographic_overlay.png', dpi=300, bbox_inches='tight')
    print("[OK] Hub guild geographic overlay saved to: hub_guild_geographic_overlay.png")
    plt.close()
    
    # Print summary table
    print("\n" + "=" * 90)
    print("HUB GUILD SUMMARY: TOP OFFERING STAND TYPES WITH MULTI-SITE PRESENCE")
    print("=" * 90)
    print(f"\n{'Stand':<8} {'Seals':<8} {'Sites':<8} {'Geographic Reach (Sites)':<60}")
    print("-" * 90)
    
    for guild in top_guilds:
        freq = guild_freq[guild]
        sites = sorted(list(stand_to_sites[guild]))
        n_sites = len(sites)
        sites_str = ', '.join(sites[:5])
        if n_sites > 5:
            sites_str += f", ... ({n_sites - 5} more)"
        
        print(f"{guild:<8} {freq:<8} {n_sites:<8} {sites_str:<60}")
    
    print("-" * 90)
    print(f"\nInterpretation:")
    print(f"  These {len(top_guilds)} offering stand types appear across multiple sites")
    print(f"  Their presence suggests standardized production practices or integrated guild organization")
    print(f"  Geographic distribution may reflect trade, administrative coordination,")
    print(f"  shared craft standards, cultural prestige, or combinations thereof")
    print("=" * 90)

# ============================================================================
# 9. SUMMARY STATISTICS
# ============================================================================

def print_summary_statistics(df, metrics, site_to_stands, stand_to_sites):
    """Print comprehensive summary statistics."""
    
    print("\n" + "="*70)
    print("BIPARTITE NETWORK SUMMARY: SITES <-> OFFERING STANDS")
    print("="*70)
    
    print(f"\nNetwork Structure:")
    print(f"  Sites (nodes):           {metrics['n_sites']}")
    print(f"  Guilds/Stands (nodes):   {metrics['n_stands']}")
    print(f"  Site-Guild edges:        {metrics['n_edges']}")
    print(f"  Connected components:    {metrics['n_components']}")
    print(f"  Network density:         {metrics['density']:.4f}")
    
    print(f"\nSeal Counts:")
    print(f"  Total seals analyzed:    {len(df)}")
    print(f"  Seals with stand data:   {len(df)}")
    
    print(f"\nSite Connectivity (degree):")
    site_degrees = metrics['site_degrees']
    print(f"  Min guilds per site:     {min(site_degrees.values())}")
    print(f"  Max guilds per site:     {max(site_degrees.values())}")
    print(f"  Mean guilds per site:    {np.mean(list(site_degrees.values())):.2f}")
    
    print(f"\nGuild Reach (geographic distribution):")
    stand_degrees = metrics['stand_degrees']
    single_site = sum(1 for d in stand_degrees.values() if d == 1)
    multi_site = sum(1 for d in stand_degrees.values() if d > 1)
    print(f"  Single-site guilds:      {single_site}")
    print(f"  Multi-site guilds:       {multi_site}")
    print(f"  Min sites per guild:     {min(stand_degrees.values())}")
    print(f"  Max sites per guild:     {max(stand_degrees.values())}")
    print(f"  Mean sites per guild:    {np.mean(list(stand_degrees.values())):.2f}")
    
    print(f"\nTop Sites by Seal Count:")
    site_seals = df.groupby('Site_Name').size().sort_values(ascending=False)
    for site, count in site_seals.head(10).items():
        n_stands = len(site_to_stands[site])
        print(f"  {site:20s}  {count:3d} seals  {n_stands:3d} guilds")
    
    print(f"\nTop 10 Guilds by Multi-Site Presence:")
    hub_stands = sorted([(s, len(site_to_stands[s])) for s in stand_to_sites.keys()],
                       key=lambda x: x[1], reverse=True)[:10]
    for stand, n_sites in hub_stands:
        sites = stand_to_sites[stand]
        print(f"  Stand {stand:>5}  {n_sites} sites - {', '.join(sites)}")

# ============================================================================
# 7. VISUALIZATION 5: SITE OVERLAP CHORD DIAGRAM
# ============================================================================

def compute_site_overlap(site_to_stands):
    """
    Compute shared guild counts between all pairs of sites.
    Returns a dictionary: {(site1, site2): count of shared guilds}
    """
    sites = list(site_to_stands.keys())
    overlap = {}
    
    for i, site1 in enumerate(sites):
        for site2 in sites[i+1:]:
            guilds1 = set(site_to_stands[site1])
            guilds2 = set(site_to_stands[site2])
            shared = len(guilds1 & guilds2)
            if shared > 0:
                overlap[(site1, site2)] = shared
    
    return overlap

def visualize_site_overlap_chord(site_to_stands, df):
    """
    Create chord diagram showing site-to-site guild overlap.
    Chord thickness represents number of shared guilds between sites.
    Node size represents total seal count at each site.
    """
    from matplotlib.patches import Wedge
    from matplotlib.path import Path
    import matplotlib.patches as mpatches
    
    # Compute overlap
    overlap = compute_site_overlap(site_to_stands)
    sites = sorted(site_to_stands.keys())
    n_sites = len(sites)
    
    # Get seal counts per site for node sizing
    site_seal_counts = df.groupby('Site_Name').size()
    max_seals = site_seal_counts.max()
    min_seals = site_seal_counts.min()
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 14))
    
    # Arrange sites in circle
    angles = np.linspace(0, 2*np.pi, n_sites, endpoint=False)
    radius = 3.0
    positions = {site: (radius * np.cos(angle), radius * np.sin(angle)) 
                 for site, angle in zip(sites, angles)}
    
    # Color palette for sites
    colors_palette = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
                      '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B88B', '#A8D8EA',
                      '#AA96DA', '#FCBAD3', '#A2D5C6', '#FFD3B6', '#D4A5A5',
                      '#9B9DC4', '#FFAAA5']
    site_colors = {site: colors_palette[i % len(colors_palette)] 
                   for i, site in enumerate(sites)}
    
    # Draw site circles on perimeter (sized by seal count with threshold-based scaling)
    for site, (x, y) in positions.items():
        n_seals = site_seal_counts.get(site, 1)
        # Threshold-based radius sizing
        if n_seals > 100:
            circle_radius = 0.5    # Large hubs (Mohenjo-daro, Harappa)
        elif n_seals > 20:
            circle_radius = 0.2    # Medium sites (Kalibangan)
        else:
            circle_radius = 0.1    # Small sites (<10 seals)
        
        circle = plt.Circle((x, y), circle_radius, color=site_colors[site], 
                           ec='darkgray', linewidth=2, zorder=10)
        ax.add_patch(circle)
        
        # Add site label
        label_offset = 0.6
        lx, ly = x * (1 + label_offset/radius), y * (1 + label_offset/radius)
        ax.text(lx, ly, site, ha='center', va='center', fontsize=9, 
               fontweight='bold', zorder=11)
    
    # Draw chords for overlaps
    if overlap:
        max_overlap = max(overlap.values())
        for (site1, site2), count in overlap.items():
            x1, y1 = positions[site1]
            x2, y2 = positions[site2]
            
            # Bezier curve through center (chord-like appearance)
            # Thickness proportional to overlap count
            thickness = 0.5 + (count / max_overlap) * 3.5
            alpha = 0.55 + (count / max_overlap) * 0.45
            
            # Simple quadratic Bezier through midpoint
            t = np.linspace(0, 1, 100)
            # Control point at origin (center)
            cx, cy = 0, 0
            
            # Bezier curve formula
            px = (1-t)**2 * x1 + 2*(1-t)*t * cx + t**2 * x2
            py = (1-t)**2 * y1 + 2*(1-t)*t * cy + t**2 * y2
            
            ax.plot(px, py, color='#2C3E50', linewidth=thickness, 
                   alpha=alpha, zorder=1)
    
    # Set equal aspect and remove axes
    ax.set_aspect('equal')
    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)
    ax.axis('off')
    
    # Title and legend
    ax.set_title('Site-to-Site Guild Overlap\n(Chord thickness proportional to shared guilds)', 
                fontsize=14, fontweight='bold', pad=20)
    
    # Add legend with overlap statistics
    if overlap:
        legend_text = f"Total site pairs: {len(overlap)}\n"
        legend_text += f"Guilds shared (range): {min(overlap.values())}-{max(overlap.values())}"
        ax.text(-4.8, 4.5, legend_text, fontsize=10, 
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig('site_overlap_chord.png', dpi=150, bbox_inches='tight')
    print("[OK] Site overlap chord diagram saved to: site_overlap_chord.png")
    plt.close()
    
    # Print overlap statistics
    print(f"\nSite Overlap Statistics:")
    print(f"  Site pairs with shared guilds: {len(overlap)}")
    if overlap:
        print(f"  Shared guilds per pair (range): {min(overlap.values())}-{max(overlap.values())}")
        print(f"  Mean shared guilds per pair: {np.mean(list(overlap.values())):.1f}")
        
        # Show top pairs
        print(f"\n  Top site pairs by guild overlap:")
        top_pairs = sorted(overlap.items(), key=lambda x: x[1], reverse=True)[:10]
        for (site1, site2), count in top_pairs:
            print(f"    {site1:20s} ↔ {site2:20s}: {count:2d} guilds")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("Parsing sites_guild.txt (canonical cleaned data)...")
    df = parse_sites_guild('sites_guild.txt')
    
    print(f"Loaded {len(df)} seals with offering stand data")
    print(f"Unique sites: {df['Site_Name'].nunique()}")
    print(f"Unique stands: {df['Stand'].nunique()}")
    
    print("\nBuilding bipartite network...")
    B, site_to_stands, stand_to_sites = build_site_stand_network(df)
    
    print("Computing metrics...")
    metrics = compute_metrics(B, site_to_stands, stand_to_sites)
    
    print("Creating visualizations...")
    visualize_bipartite_network(B, site_to_stands, stand_to_sites)
    
    site_seal_counts = df.groupby('Site_Name').size()
    visualize_geographical_network(df, site_to_stands, stand_to_sites)
    visualize_hub_guilds(stand_to_sites, site_seal_counts)
    
    # Build guild frequency dictionary for overlay
    guild_freq = {}
    for _, row in df.iterrows():
        guild = row['Stand']
        guild_freq[guild] = guild_freq.get(guild, 0) + 1
    
    visualize_hub_guild_overlay(stand_to_sites, guild_freq, df)
    visualize_site_overlap_chord(site_to_stands, df)
    
    print_summary_statistics(df, metrics, site_to_stands, stand_to_sites)
    
    visualize_hub_guilds(stand_to_sites, site_seal_counts)
    
    print("Generating summary statistics...")
    print_summary_statistics(df, metrics, site_to_stands, stand_to_sites)
    
    print("\n" + "="*70)
    print("Analysis complete! Check the generated PNG files.")
    print("="*70)
