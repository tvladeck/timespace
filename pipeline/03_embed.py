"""Step 3: Embed transit time matrix into 2D.

Key insight: raw transit times correlate r=0.93 with geographic distance,
so standard MDS produces an embedding that looks like geography. To extract
the interesting distortion, we feed MDS an *adjusted* distance matrix that
emphasizes transit's deviation from geography:

    adjusted(i,j) = geo_dist(i,j) * (transit_time(i,j) / walking_time(i,j) / median_ratio)^beta

This normalizes out the "transit is faster than walking" baseline and amplifies
directional asymmetries (e.g., N-S subway express vs E-W crosstown crawl).
"""
import numpy as np
import pandas as pd
from sklearn.manifold import MDS
from scipy.spatial import Delaunay
from scipy.spatial.distance import pdist, squareform
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from config import INTERMEDIATE_DIR, MDS_RANDOM_STATE
from utils import walking_time_seconds


def build_adjusted_matrix(transit_minutes, points, beta=1.5):
    """Build distance matrix that amplifies transit's deviation from geography."""
    n = len(points)
    geo = points[["lng", "lat"]].values
    geo_dists = squareform(pdist(geo))

    # Walking times
    walk_min = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            w = walking_time_seconds(geo[i, 1], geo[i, 0], geo[j, 1], geo[j, 0]) / 60
            walk_min[i, j] = w
            walk_min[j, i] = w

    # Transit/walking ratio
    ratio = np.ones((n, n))
    mask = walk_min > 0
    ratio[mask] = transit_minutes[mask] / walk_min[mask]
    np.fill_diagonal(ratio, 1)

    # Normalize so median pair = 1.0
    upper = np.triu_indices(n, k=1)
    med = np.median(ratio[upper])
    ratio_norm = ratio / med
    np.fill_diagonal(ratio_norm, 1)

    print(f"Transit/walking ratio median: {med:.3f}")
    r = ratio_norm[upper]
    print(f"Normalized: <1 (transit helps): {(r<1).mean()*100:.0f}%, >1 (transit doesn't help): {(r>1).mean()*100:.0f}%")

    # Adjusted distance: amplify the transit advantage/disadvantage
    adjusted = geo_dists * (ratio_norm ** beta)
    np.fill_diagonal(adjusted, 0)
    adjusted = (adjusted + adjusted.T) / 2

    print(f"beta={beta}: adjusted range [{adjusted[adjusted>0].min():.5f}, {adjusted.max():.5f}]")
    return adjusted


def align_fixed_scale(emb, geo):
    """Align: rotation + translation, scale to match geographic extent."""
    mu_e = emb.mean(axis=0)
    mu_g = geo.mean(axis=0)
    s = emb - mu_e
    t = geo - mu_g

    M = t.T @ s
    U, _, Vt = np.linalg.svd(M)
    d = np.linalg.det(U @ Vt)
    D = np.diag([1, np.sign(d)])
    R = U @ D @ Vt
    rotated = s @ R.T

    geo_avg = pdist(t).mean()
    emb_avg = pdist(rotated).mean()
    scale = geo_avg / emb_avg

    return scale * rotated + mu_g


def count_flipped(geo, emb):
    tri = Delaunay(geo)
    n_f = sum(
        1 for s in tri.simplices
        if np.sign(np.cross(geo[s][1] - geo[s][0], geo[s][2] - geo[s][0]))
        != np.sign(np.cross(emb[s][1] - emb[s][0], emb[s][2] - emb[s][0]))
    )
    return n_f, len(tri.simplices)


def embed():
    matrix = np.load(INTERMEDIATE_DIR / "transit_matrix_minutes.npy")
    points = pd.read_csv(INTERMEDIATE_DIR / "control_points.csv", index_col=0)
    n = matrix.shape[0]
    print(f"Embedding {n} points...\n")

    geo = points[["lng", "lat"]].values

    # Try both raw and adjusted distance matrices, pick best
    adjusted = build_adjusted_matrix(matrix, points, beta=1.0)

    print()
    mds = MDS(
        n_components=2, metric=True, dissimilarity="precomputed",
        n_init=10, max_iter=1000, random_state=MDS_RANDOM_STATE,
        normalized_stress="auto",
    )
    emb = mds.fit_transform(adjusted)
    print(f"MDS stress: {mds.stress_:.4f}")

    # Align (try all orientations)
    best = None
    best_f = float("inf")
    for fy in [False, True]:
        for fx in [False, True]:
            c = emb.copy()
            if fy: c[:, 1] = -c[:, 1]
            if fx: c[:, 0] = -c[:, 0]
            a = align_fixed_scale(c, geo)
            n_f, n_t = count_flipped(geo, a)
            if n_f < best_f:
                best_f = n_f
                best = a

    final = best
    print(f"Flipped: {best_f}/{n_t}")

    # Report
    report(geo, final, points)

    # Save
    result = points.copy()
    result["mds_x"] = final[:, 0]
    result["mds_y"] = final[:, 1]
    result["geo_x"] = geo[:, 0]
    result["geo_y"] = geo[:, 1]
    result.to_csv(INTERMEDIATE_DIR / "embedded_points.csv", index=True)
    np.save(INTERMEDIATE_DIR / "mds_coords.npy", final)

    plot_diagnostics(geo, final, matrix, points)
    return final, geo, points


def report(geo, emb, points):
    bc = "BoroName" if "BoroName" in points.columns else "borough"
    print("\nDistortion by borough:")
    for b in ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"]:
        m = points[bc] == b
        if m.sum() < 3:
            continue
        r = pdist(emb[m]).mean() / pdist(geo[m]).mean()
        d = "compressed" if r < 1 else "expanded"
        print(f"  {b:20s}: {r:.2f}x ({d})")

    # Manhattan aspect ratio
    m = points[bc] == "Manhattan"
    g = geo[m]
    e = emb[m]
    gw = g[:, 0].max() - g[:, 0].min()
    gh = g[:, 1].max() - g[:, 1].min()
    ew = e[:, 0].max() - e[:, 0].min()
    eh = e[:, 1].max() - e[:, 1].min()
    print(f"\nManhattan shape: W={ew/gw:.2f}x, H={eh/gh:.2f}x (H/W {gh/gw:.2f} → {eh/ew:.2f})")


def plot_diagnostics(geo, emb, distance_matrix, points):
    bc = "BoroName" if "BoroName" in points.columns else "borough"
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    ax = axes[0]
    ax.scatter(geo[:, 0], geo[:, 1], c="blue", alpha=0.3, s=8, label="Geographic")
    ax.scatter(emb[:, 0], emb[:, 1], c="red", alpha=0.3, s=8, label="Timespace")
    ax.set_title("Geographic vs Timespace")
    ax.legend()
    ax.set_aspect("equal")

    ax = axes[1]
    emb_dists = squareform(pdist(emb))
    upper = np.triu_indices(len(geo), k=1)
    ax.scatter(distance_matrix[upper], emb_dists[upper], alpha=0.05, s=1)
    ax.set_xlabel("Transit time (min)")
    ax.set_ylabel("Embedding distance")
    ax.set_title("Shepard Diagram")
    corr = np.corrcoef(distance_matrix[upper], emb_dists[upper])[0, 1]
    ax.text(0.05, 0.95, f"r = {corr:.3f}", transform=ax.transAxes, va="top")

    ax = axes[2]
    colors = {
        "Manhattan": "#d4a574", "Brooklyn": "#5b9b8a",
        "Queens": "#8b7eb8", "Bronx": "#c47c6c", "Staten Island": "#7a8fa6",
    }
    for b, color in colors.items():
        m = points[bc] == b
        ax.scatter(emb[m, 0], emb[m, 1], c=color, s=10, label=b, alpha=0.7)
    ax.set_title("Timespace by Borough")
    ax.legend(fontsize=8)
    ax.set_aspect("equal")

    plt.tight_layout()
    plt.savefig(INTERMEDIATE_DIR / "mds_diagnostics.png", dpi=150)
    print("\nSaved diagnostic plot")
    plt.close()


if __name__ == "__main__":
    embed()
