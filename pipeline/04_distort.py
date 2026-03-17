"""Step 4: TPS distortion without boundary anchors.

Uses thin-plate spline interpolation with moderate regularization.
No boundary anchors (they suppress edge distortion).
Self-intersections handled per-polygon in export via adaptive blending.
"""
import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from config import INTERMEDIATE_DIR


class TPSDistorter:
    def __init__(self, geo_coords, emb_coords, regularization=0.1):
        self.geo_raw = np.asarray(geo_coords, dtype=np.float64)
        self.emb = np.asarray(emb_coords, dtype=np.float64)
        self.n_points = len(geo_coords)
        self.reg = regularization

        # Normalize for numerical stability
        self.geo_min = self.geo_raw.min(axis=0)
        self.geo_range = self.geo_raw.max(axis=0) - self.geo_min
        self.geo = (self.geo_raw - self.geo_min) / self.geo_range

        self.weights_x, self.affine_x = self._solve_tps(self.emb[:, 0])
        self.weights_y, self.affine_y = self._solve_tps(self.emb[:, 1])
        print(f"TPS: {self.n_points} pts, reg={regularization}")

    def _tps_kernel(self, r):
        result = np.zeros_like(r)
        mask = r > 0
        result[mask] = r[mask] ** 2 * np.log(r[mask])
        return result

    def _solve_tps(self, target):
        n = self.n_points
        dists = cdist(self.geo, self.geo)
        K = self._tps_kernel(dists) + self.reg * np.eye(n)
        P = np.column_stack([np.ones(n), self.geo])
        L = np.zeros((n + 3, n + 3))
        L[:n, :n] = K
        L[:n, n:] = P
        L[n:, :n] = P.T
        rhs = np.zeros(n + 3)
        rhs[:n] = target
        params = np.linalg.solve(L, rhs)
        return params[:n], params[n:]

    def _normalize(self, coords):
        return (coords - self.geo_min) / self.geo_range

    def transform_points(self, coords):
        coords = np.asarray(coords, dtype=np.float64)
        if coords.ndim == 1:
            coords = coords.reshape(1, 2)
        normed = self._normalize(coords)
        dists = cdist(normed, self.geo)
        U = self._tps_kernel(dists)
        x_out = self.affine_x[0] + self.affine_x[1] * normed[:, 0] + self.affine_x[2] * normed[:, 1] + U @ self.weights_x
        y_out = self.affine_y[0] + self.affine_y[1] * normed[:, 0] + self.affine_y[2] * normed[:, 1] + U @ self.weights_y
        return np.column_stack([x_out, y_out])


# Aliases
DelaunayDistorter = TPSDistorter
GridDistorter = TPSDistorter

def add_boundary_anchors(geo, emb, **kwargs):
    return geo, emb


def build_distorter():
    points = pd.read_csv(INTERMEDIATE_DIR / "embedded_points.csv", index_col=0)
    geo = points[["geo_x", "geo_y"]].values
    emb = points[["mds_x", "mds_y"]].values
    distorter = TPSDistorter(geo, emb, regularization=0.1)

    recon = distorter.transform_points(geo)
    err = np.sqrt(((recon - emb) ** 2).sum(axis=1))
    print(f"Control point error: mean={err.mean():.4f}, max={err.max():.4f}")

    # Report Manhattan shape
    bc = "BoroName" if "BoroName" in points.columns else "borough"
    man = points[bc] == "Manhattan"
    g, e = geo[man], recon[man]
    gw = g[:, 0].max() - g[:, 0].min()
    gh = g[:, 1].max() - g[:, 1].min()
    ew = e[:, 0].max() - e[:, 0].min()
    eh = e[:, 1].max() - e[:, 1].min()
    print(f"Manhattan: W={ew/gw:.2f}x H={eh/gh:.2f}x")

    return distorter


if __name__ == "__main__":
    build_distorter()
