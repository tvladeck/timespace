"""Step 2: Compute transit time matrix.

Phase 1: Reuse existing 139-point matrix from old project.
Phase 2: Use r5py to compute many-to-many transit times for 600+ points.
"""
import numpy as np
import pandas as pd
import sys
from pathlib import Path
from config import INTERMEDIATE_DIR, RAW_DIR, WALKING_SPEED_KMH, MANHATTAN_GRID_FACTOR
from utils import walking_time_seconds


def compute_r5py_matrix(control_points):
    """Compute transit time matrix using r5py."""
    import datetime
    import geopandas as gpd
    from shapely.geometry import Point
    import r5py

    n = len(control_points)
    print(f"Computing {n}x{n} transit time matrix with r5py...")

    # Build GeoDataFrame for origins/destinations
    origins = gpd.GeoDataFrame(
        {
            "id": range(n),
            "geometry": [
                Point(row["lng"], row["lat"])
                for _, row in control_points.iterrows()
            ],
        },
        crs="EPSG:4326",
    )

    # Build transport network
    osm_file = str(RAW_DIR / "nyc.osm.pbf")
    gtfs_dir = RAW_DIR / "gtfs"
    gtfs_files = sorted(str(f) for f in gtfs_dir.glob("*.zip"))

    print(f"OSM file: {osm_file}")
    print(f"GTFS feeds: {len(gtfs_files)}")
    for f in gtfs_files:
        print(f"  {Path(f).name}")

    print("\nBuilding transport network (this takes a few minutes)...")
    transport_network = r5py.TransportNetwork(osm_file, gtfs_files)
    print("Network built.")

    # Compute travel time matrix
    # Wednesday March 18 2026 at 8am — typical weekday morning
    departure = datetime.datetime(2026, 3, 18, 8, 0, 0)

    print(f"\nComputing travel times (departure: {departure})...")
    print(f"  Modes: TRANSIT + WALK")
    print(f"  Departure window: 60 minutes (samples median)")
    print(f"  Max trip time: 120 minutes")

    result = r5py.TravelTimeMatrix(
        transport_network,
        origins=origins,
        destinations=origins,
        departure=departure,
        transport_modes=[r5py.TransportMode.TRANSIT, r5py.TransportMode.WALK],
        departure_time_window=datetime.timedelta(minutes=60),
        max_time=datetime.timedelta(minutes=120),
    )

    print(f"Result: {len(result)} rows")

    # Pivot to matrix
    matrix = result.pivot(index="from_id", columns="to_id", values="travel_time")
    matrix = matrix.values.astype(float)

    # Handle NaN (unreachable within max_time) — set to max_time
    nan_count = np.isnan(matrix).sum()
    if nan_count > 0:
        print(f"  {nan_count} unreachable pairs (setting to 120 min)")
        matrix = np.nan_to_num(matrix, nan=120.0)

    # Ensure diagonal is 0
    np.fill_diagonal(matrix, 0)

    # Symmetrize
    matrix = (matrix + matrix.T) / 2

    print(f"\nMatrix range: {matrix[matrix > 0].min():.1f} to {matrix.max():.1f} minutes")
    print(f"Mean: {matrix[matrix > 0].mean():.1f} minutes")

    return matrix


def compute_walking_matrix(points):
    """Compute pairwise walking time matrix in minutes."""
    n = len(points)
    lats = points["lat"].values
    lngs = points["lng"].values
    walk = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            wt = walking_time_seconds(
                lats[i], lngs[i], lats[j], lngs[j],
                speed_kmh=WALKING_SPEED_KMH,
                grid_factor=MANHATTAN_GRID_FACTOR,
            ) / 60.0  # convert to minutes
            walk[i, j] = wt
            walk[j, i] = wt
    return walk


def load_phase1_matrix():
    """Load the existing Phase 1 matrix (processed in previous runs)."""
    raw = np.load(INTERMEDIATE_DIR / "raw_distance_matrix.npy")
    return raw


def process_transit_times(phase=2):
    """Full transit time processing pipeline."""
    points = pd.read_csv(INTERMEDIATE_DIR / "control_points.csv", index_col=0)
    n = len(points)

    if phase == 1:
        # Phase 1: use existing matrix
        raw = load_phase1_matrix()
        # Fill lower triangle
        for i in range(n):
            for j in range(i):
                if raw[i, j] == 0 and raw[j, i] != 0:
                    raw[i, j] = raw[j, i]
                elif raw[j, i] == 0 and raw[i, j] != 0:
                    raw[j, i] = raw[i, j]
        transit_minutes = raw / 60.0
    else:
        # Phase 2: compute with r5py
        transit_minutes = compute_r5py_matrix(points)

    # Compute walking times
    print("\nComputing walking time matrix...")
    walk = compute_walking_matrix(points)
    print(f"Walking times range: {walk[walk > 0].min():.1f} to {walk.max():.1f} minutes")

    # Take min(transit, walking) per pair
    # For Phase 2, r5py already includes walking but let's ensure floor
    combined = np.where(
        (transit_minutes > 0) & (walk > 0),
        np.minimum(transit_minutes, walk),
        np.where(transit_minutes > 0, transit_minutes, walk),
    )
    np.fill_diagonal(combined, 0)

    # Symmetrize
    symmetric = (combined + combined.T) / 2
    np.fill_diagonal(symmetric, 0)

    print(f"\nFinal matrix: {n}x{n}")
    print(f"Range: {symmetric[symmetric > 0].min():.1f} to {symmetric.max():.1f} minutes")
    print(f"Mean: {symmetric[symmetric > 0].mean():.1f} minutes")

    # Save
    np.save(INTERMEDIATE_DIR / "transit_matrix_seconds.npy", symmetric * 60)
    np.save(INTERMEDIATE_DIR / "transit_matrix_minutes.npy", symmetric)
    print(f"Saved to {INTERMEDIATE_DIR}")

    return symmetric, points


if __name__ == "__main__":
    phase = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    matrix, points = process_transit_times(phase=phase)
