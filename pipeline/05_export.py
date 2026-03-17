"""Step 5: Export geographic and distorted GeoJSON files.

Works directly on GeoJSON coordinate structures to guarantee
identical structure between geo and distorted versions (required
for the frontend morph animation).
"""
import json
import copy
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import mapping
from config import OLD_SHAPEFILES_DIR, INTERMEDIATE_DIR, OUTPUT_DIR, SIMPLIFY_TOLERANCE, BOROUGH_COLORS, SUBWAY_COLORS
import importlib
_distort = importlib.import_module("04_distort")
TPSDistorter = _distort.TPSDistorter


def load_distorter():
    """Load the TPS distorter."""
    points = pd.read_csv(INTERMEDIATE_DIR / "embedded_points.csv", index_col=0)
    geo = points[["geo_x", "geo_y"]].values
    mds = points[["mds_x", "mds_y"]].values
    return TPSDistorter(geo, mds, regularization=0.1)


def load_shapefile(path, simplify_tolerance=SIMPLIFY_TOLERANCE):
    """Load a shapefile, reproject to WGS84, and optionally simplify."""
    gdf = gpd.read_file(path)
    gdf = gdf.to_crs(epsg=4326)
    if simplify_tolerance:
        gdf["geometry"] = gdf["geometry"].simplify(simplify_tolerance, preserve_topology=True)
    return gdf


def densify_coords(coords, max_segment_deg=0.001):
    """Densify a coordinate ring by adding intermediate vertices.

    For each edge longer than max_segment_deg, subdivide it into
    segments of at most max_segment_deg. This ensures the TPS distortion
    varies smoothly along each edge, preventing self-intersections.

    0.002 degrees ≈ 220m — enough to keep TPS displacement smooth.
    """
    if not isinstance(coords, list) or len(coords) < 2:
        return coords

    # Check if this is a leaf coordinate
    if isinstance(coords[0], (int, float)):
        return coords  # It's a single coordinate, not a ring

    # Check if this is a ring of coordinates
    if isinstance(coords[0], list) and isinstance(coords[0][0], (int, float)):
        # This is a ring — densify it
        result = [coords[0]]
        for i in range(len(coords) - 1):
            p1 = coords[i]
            p2 = coords[i + 1]
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            dist = (dx ** 2 + dy ** 2) ** 0.5
            if dist > max_segment_deg:
                n_segments = int(np.ceil(dist / max_segment_deg))
                for j in range(1, n_segments):
                    t = j / n_segments
                    result.append([p1[0] + t * dx, p1[1] + t * dy])
            result.append(p2)
        return result

    # Otherwise recurse into nested structure
    return [densify_coords(c, max_segment_deg) for c in coords]


def gdf_to_geojson(gdf, properties_fn=None, densify=True):
    """Convert a GeoDataFrame to a GeoJSON dict with optional edge densification."""
    features = []
    for _, row in gdf.iterrows():
        if row.geometry is None or row.geometry.is_empty:
            continue
        props = properties_fn(row) if properties_fn else {}
        geom_dict = mapping(row.geometry)
        coords = _tuples_to_lists(geom_dict["coordinates"])
        if densify:
            coords = densify_coords(coords)
        geom_dict["coordinates"] = coords
        features.append({
            "type": "Feature",
            "properties": props,
            "geometry": geom_dict,
        })
    return {"type": "FeatureCollection", "features": features}


def collect_leaf_coords(obj):
    """Recursively collect all leaf [lng, lat, ...] coordinate arrays
    from a GeoJSON coordinate structure. Returns a flat list of [lng, lat] pairs
    and a function to write them back.
    """
    coords = []
    positions = []  # (obj_ref, index) for writing back

    def _collect(node, path):
        if isinstance(node, (list, tuple)):
            if len(node) >= 2 and isinstance(node[0], (int, float)):
                # This is a coordinate pair [lng, lat, ...]
                coords.append([node[0], node[1]])
                positions.append((path,))
            else:
                for i, child in enumerate(node):
                    _collect(child, path + [i])

    _collect(obj, [])
    return np.array(coords) if coords else np.empty((0, 2)), positions


def _tuples_to_lists(obj):
    """Recursively convert all tuples to lists in a nested structure."""
    if isinstance(obj, tuple):
        return [_tuples_to_lists(x) for x in obj]
    elif isinstance(obj, list):
        return [_tuples_to_lists(x) for x in obj]
    return obj


def distort_geojson(geojson, distorter):
    """Create a distorted copy of a GeoJSON dict by transforming all coordinates.

    For polygons that become self-intersecting, adaptively blends toward
    geographic coordinates until valid.
    """
    from shapely.geometry import shape as shapely_shape

    result = copy.deepcopy(geojson)
    n_blended = 0

    for feature in result["features"]:
        geom = feature["geometry"]
        geom["coordinates"] = _tuples_to_lists(geom["coordinates"])
        coords_array, positions = collect_leaf_coords(geom["coordinates"])

        if len(coords_array) == 0:
            continue

        transformed = distorter.transform_points(coords_array)
        _write_back(geom["coordinates"], transformed, 0)

        # For polygons, check validity and blend if needed
        if geom["type"] in ("Polygon", "MultiPolygon"):
            s = shapely_shape(geom)
            if not s.is_valid:
                # Find max distortion that stays valid
                for blend in [0.95, 0.9, 0.85, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]:
                    blended = coords_array + blend * (transformed - coords_array)
                    _write_back(geom["coordinates"], blended, 0)
                    if shapely_shape(geom).is_valid:
                        break
                else:
                    _write_back(geom["coordinates"], coords_array, 0)
                n_blended += 1

    if n_blended:
        print(f"    ({n_blended} features adaptively blended)")

    return result


def _write_back(node, transformed, idx):
    """Recursively write transformed coordinates back into a GeoJSON coordinate structure."""
    if isinstance(node, (list, tuple)):
        if len(node) >= 2 and isinstance(node[0], (int, float)):
            # Leaf coordinate — replace values (node must be a list, not tuple)
            node[0] = float(transformed[idx, 0])
            node[1] = float(transformed[idx, 1])
            return idx + 1
        else:
            for child in node:
                idx = _write_back(child, transformed, idx)
            return idx
    return idx


def export_layer(name, gdf, distorter, properties_fn=None):
    """Export a layer as paired geographic + distorted GeoJSON files."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Create geographic GeoJSON
    geo_geojson = gdf_to_geojson(gdf, properties_fn)

    # Count vertices
    n_features = len(geo_geojson["features"])
    total_coords = sum(
        len(collect_leaf_coords(f["geometry"]["coordinates"])[0])
        for f in geo_geojson["features"]
    )
    print(f"  {name}: {n_features} features, {total_coords} vertices")

    # Create distorted GeoJSON (preserves exact structure)
    dist_geojson = distort_geojson(geo_geojson, distorter)

    # Verify structure match
    for i in range(n_features):
        g_str = json.dumps(geo_geojson["features"][i]["geometry"]["coordinates"])
        d_str = json.dumps(dist_geojson["features"][i]["geometry"]["coordinates"])
        assert g_str.count("[") == d_str.count("["), \
            f"Structure mismatch in feature {i} of {name}"

    # Write files
    geo_path = OUTPUT_DIR / f"{name}_geo.geojson"
    dist_path = OUTPUT_DIR / f"{name}_distorted.geojson"

    with open(geo_path, "w") as f:
        json.dump(geo_geojson, f)
    with open(dist_path, "w") as f:
        json.dump(dist_geojson, f)

    geo_size = geo_path.stat().st_size / 1024
    dist_size = dist_path.stat().st_size / 1024
    print(f"    -> {geo_path.name} ({geo_size:.0f} KB), {dist_path.name} ({dist_size:.0f} KB)")


def export_all():
    """Export all layers."""
    distorter = load_distorter()

    # 1. Boroughs
    print("Exporting boroughs...")
    boroughs = load_shapefile(OLD_SHAPEFILES_DIR / "nybb" / "nybb.shp")
    export_layer("boroughs", boroughs, distorter, lambda row: {
        "name": row["BoroName"],
        "color": BOROUGH_COLORS.get(row["BoroName"], "#888888"),
    })

    # 2. NTA neighborhoods
    print("Exporting NTA neighborhoods...")
    nta = load_shapefile(OLD_SHAPEFILES_DIR / "nynta_15c" / "nynta.shp")
    nta_filtered = nta[~nta["NTAName"].str.contains("park-cemetery-etc|Airport", case=False, na=False)].copy()
    export_layer("nta", nta_filtered, distorter, lambda row: {
        "name": row["NTAName"],
        "borough": row["BoroName"],
        "code": row["NTACode"],
        "color": BOROUGH_COLORS.get(row["BoroName"], "#888888"),
    })

    # 3. Subway routes
    print("Exporting subway routes...")
    routes = load_shapefile(
        OLD_SHAPEFILES_DIR / "NYC_Subways" / "subway_routes.shp",
        simplify_tolerance=SIMPLIFY_TOLERANCE,
    )
    routes = routes[routes["CLOSED"].isna() | (routes["CLOSED"] == "")].copy()
    export_layer("subway_routes", routes, distorter, lambda row: {
        "name": row.get("NAME", ""),
        "route": row.get("ROUTE", ""),
        "color": SUBWAY_COLORS.get(str(row.get("ROUTE", "")), row.get("COLOR", "#808183")),
    })

    # 4. Subway stations
    print("Exporting subway stations...")
    stations = load_shapefile(
        OLD_SHAPEFILES_DIR / "NYC_Subways" / "subway_stations.shp",
        simplify_tolerance=None,
    )
    stations = stations[stations["CLOSED"].isna() | (stations["CLOSED"] == "")].copy()
    export_layer("subway_stations", stations, distorter, lambda row: {
        "name": row.get("NAME", ""),
        "routes": row.get("ROUTES", ""),
        "borough": row.get("BOROUGH", ""),
        "color": SUBWAY_COLORS.get(
            str(row.get("ROUTES", "")).split("-")[0].strip() if row.get("ROUTES") else "",
            "#808183",
        ),
    })

    # 5. Labels (NTA centroids)
    print("Exporting labels...")
    nta_for_labels = nta_filtered.copy()
    nta_for_labels["geometry"] = nta_for_labels.geometry.representative_point()
    export_layer("labels", nta_for_labels, distorter, lambda row: {
        "name": row["NTAName"],
        "borough": row["BoroName"],
    })

    # 6. Control points
    print("Exporting control points...")
    cp = pd.read_csv(INTERMEDIATE_DIR / "embedded_points.csv", index_col=0)
    boro_col = "BoroName" if "BoroName" in cp.columns else "borough"
    name_col = "NTAName" if "NTAName" in cp.columns else "name"
    geo_features = []
    dist_features = []
    for _, row in cp.iterrows():
        props = {"name": row.get(name_col, ""), "borough": row.get(boro_col, "")}
        geo_features.append({
            "type": "Feature",
            "properties": props,
            "geometry": {"type": "Point", "coordinates": [row["geo_x"], row["geo_y"]]},
        })
        dist_features.append({
            "type": "Feature",
            "properties": props,
            "geometry": {"type": "Point", "coordinates": [row["mds_x"], row["mds_y"]]},
        })

    for suffix, features in [("geo", geo_features), ("distorted", dist_features)]:
        path = OUTPUT_DIR / f"control_points_{suffix}.geojson"
        with open(path, "w") as f:
            json.dump({"type": "FeatureCollection", "features": features}, f)
    print(f"    -> control_points_geo.geojson, control_points_distorted.geojson")

    print(f"\nDone! All files in {OUTPUT_DIR}")


if __name__ == "__main__":
    export_all()
