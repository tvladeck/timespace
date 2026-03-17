"""Shared utilities for the timespace pipeline."""
import numpy as np


def haversine_km(lat1, lon1, lat2, lon2):
    """Haversine distance in kilometers between two lat/lng points."""
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return R * 2 * np.arcsin(np.sqrt(a))


def walking_time_seconds(lat1, lon1, lat2, lon2, speed_kmh=5.0, grid_factor=1.4):
    """Estimated walking time in seconds between two points."""
    dist = haversine_km(lat1, lon1, lat2, lon2) * grid_factor
    return dist / speed_kmh * 3600


def procrustes_align(source, target, allow_reflection=True):
    """Align source points to target via Procrustes (rotation, scaling, translation).

    Both inputs are (N, 2) arrays. Returns transformed source.
    Tries both with and without reflection, picks the one with lower residual.
    """
    results = []
    for reflect in ([False, True] if allow_reflection else [False]):
        mu_s = source.mean(axis=0)
        mu_t = target.mean(axis=0)
        s = source - mu_s
        t = target - mu_t

        M = t.T @ s
        U, _, Vt = np.linalg.svd(M)

        if reflect:
            # Allow reflection
            R = U @ Vt
        else:
            # Prevent reflection
            d = np.linalg.det(U @ Vt)
            D = np.diag([1, np.sign(d)])
            R = U @ D @ Vt

        scale = np.trace(t.T @ (s @ R.T)) / np.trace(s.T @ s)
        transformed = scale * (s @ R.T) + mu_t
        residual = np.sum((transformed - target) ** 2)
        results.append((residual, transformed))

    # Return the one with lower residual
    results.sort(key=lambda x: x[0])
    return results[0][1]
