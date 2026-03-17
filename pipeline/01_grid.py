"""Step 1: Generate control points.

Phase 1 mode: Extract 139 points from existing distance matrix.
Phase 2 mode: Generate denser grid from NTA centroids + subway stations.
"""
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
from config import OLD_DATA_DIR, OLD_SHAPEFILES_DIR, INTERMEDIATE_DIR, RAW_DIR


DEDUP_DISTANCE_M = 200  # Deduplicate points within this distance


def load_nylnglat():
    """Load the master neighborhood lat/lng file."""
    df = pd.read_csv(OLD_DATA_DIR / "nylnglat.csv", index_col=0)
    df.index = df.index.astype(int)
    return df


def load_distance_matrix():
    """Load the existing distance matrix CSV."""
    dm = pd.read_csv(OLD_DATA_DIR / "distance.matrix.139.csv", index_col=0)
    meta_cols = ["neighborhood", "lat", "lng"]
    neighborhood_cols = [c for c in dm.columns if c not in meta_cols]
    return dm, neighborhood_cols


def extract_control_points_phase1():
    """Phase 1: Extract control points from existing distance matrix."""
    nylnglat = load_nylnglat()
    dm, neighborhood_cols = load_distance_matrix()

    n_cols = len(neighborhood_cols)
    print(f"Distance matrix has {len(dm)} rows and {n_cols} distance columns")

    matrix_values = dm[neighborhood_cols].values[:n_cols, :]
    control_points = nylnglat.iloc[:n_cols].copy().reset_index(drop=True)

    print(f"Extracted {len(control_points)} control points")

    INTERMEDIATE_DIR.mkdir(parents=True, exist_ok=True)
    control_points.to_csv(INTERMEDIATE_DIR / "control_points.csv", index=True)
    np.save(INTERMEDIATE_DIR / "raw_distance_matrix.npy", matrix_values)

    return control_points, matrix_values


def generate_control_points_phase2():
    """Phase 2: Generate denser control points from NTA centroids + subway stations.

    Combines:
    1. All NTA neighborhood centroids (195 points)
    2. Subway station locations (~490 points)
    3. Deduplicates within 200m
    """
    print("Generating Phase 2 control points...\n")

    # 1. NTA centroids
    nta = gpd.read_file(OLD_SHAPEFILES_DIR / "nynta_15c" / "nynta.shp")
    nta = nta.to_crs(epsg=4326)
    # Use representative_point instead of centroid for accuracy
    nta_points = nta.copy()
    nta_points["geometry"] = nta_points.geometry.representative_point()
    nta_gdf = gpd.GeoDataFrame({
        "name": nta_points["NTAName"],
        "borough": nta_points["BoroName"],
        "source": "nta_centroid",
        "geometry": nta_points.geometry,
    }, crs="EPSG:4326")
    print(f"NTA centroids: {len(nta_gdf)} points")

    # 2. Subway stations
    stations = gpd.read_file(OLD_SHAPEFILES_DIR / "NYC_Subways" / "subway_stations.shp")
    stations = stations.to_crs(epsg=4326)
    # Filter to open stations only
    stations = stations[stations["CLOSED"].isna() | (stations["CLOSED"] == "")].copy()
    stations_gdf = gpd.GeoDataFrame({
        "name": stations["NAME"],
        "borough": stations["BOROUGH"],
        "source": "subway_station",
        "geometry": stations.geometry,
    }, crs="EPSG:4326")
    print(f"Subway stations: {len(stations_gdf)} points")

    # 3. Combine
    combined = pd.concat([nta_gdf, stations_gdf], ignore_index=True)
    print(f"Combined: {len(combined)} points")

    # 4. Deduplicate within 200m
    # Project to UTM zone 18N (NYC) for metric distance calculation
    combined_utm = combined.to_crs(epsg=32618)
    keep = [True] * len(combined_utm)
    coords = np.array([(g.x, g.y) for g in combined_utm.geometry])

    # Prioritize NTA centroids over subway stations
    nta_mask = combined["source"] == "nta_centroid"
    # Sort so NTA centroids come first (they get priority)
    order = np.argsort(~nta_mask.values)  # False (0) first → NTA first

    for i in range(len(order)):
        if not keep[order[i]]:
            continue
        for j in range(i + 1, len(order)):
            if not keep[order[j]]:
                continue
            dist = np.linalg.norm(coords[order[i]] - coords[order[j]])
            if dist < DEDUP_DISTANCE_M:
                keep[order[j]] = False

    deduped = combined[keep].reset_index(drop=True)
    print(f"After deduplication ({DEDUP_DISTANCE_M}m): {len(deduped)} points")

    # Extract lat/lng
    deduped["lng"] = deduped.geometry.x
    deduped["lat"] = deduped.geometry.y

    # Report
    print(f"\nBy borough:")
    print(deduped["borough"].value_counts().to_string())
    print(f"\nBy source:")
    print(deduped["source"].value_counts().to_string())

    # Save as CSV (matching Phase 1 format)
    output = pd.DataFrame({
        "BoroName": deduped["borough"],
        "NTAName": deduped["name"],
        "lng": deduped["lng"],
        "lat": deduped["lat"],
        "source": deduped["source"],
    })

    INTERMEDIATE_DIR.mkdir(parents=True, exist_ok=True)
    output.to_csv(INTERMEDIATE_DIR / "control_points.csv", index=True)
    print(f"\nSaved {len(output)} control points to {INTERMEDIATE_DIR / 'control_points.csv'}")

    return output


if __name__ == "__main__":
    import sys
    phase = int(sys.argv[1]) if len(sys.argv) > 1 else 2

    if phase == 1:
        extract_control_points_phase1()
    else:
        generate_control_points_phase2()
