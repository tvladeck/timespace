import maplibregl from "maplibre-gl";

const NYC_CENTER = [-73.935, 40.73];

export function createMap() {
  const map = new maplibregl.Map({
    container: "map",
    style: {
      version: 8,
      glyphs:
        "https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf",
      sources: {},
      layers: [
        {
          id: "background",
          type: "background",
          paint: {
            "background-color": "#0a1628",
          },
        },
      ],
    },
    center: NYC_CENTER,
    zoom: 10.5,
    maxBounds: [
      [-74.8, 40.2],
      [-73.2, 41.2],
    ],
    attributionControl: false,
  });

  map.addControl(new maplibregl.NavigationControl(), "top-right");

  return map;
}

async function fetchJSON(path) {
  const base = import.meta.env.BASE_URL || "/";
  const res = await fetch(base + path.replace(/^\//, ""));
  return res.json();
}

export async function loadAllData() {
  const [
    hexgridGeo,
    hexgridDist,
    subwayRoutesGeo,
    subwayRoutesDist,
    subwayStationsGeo,
    subwayStationsDist,
    labelsGeo,
    labelsDist,
  ] = await Promise.all([
    fetchJSON("/data/hexgrid_geo.geojson"),
    fetchJSON("/data/hexgrid_distorted.geojson"),
    fetchJSON("/data/subway_routes_geo.geojson"),
    fetchJSON("/data/subway_routes_distorted.geojson"),
    fetchJSON("/data/subway_stations_geo.geojson"),
    fetchJSON("/data/subway_stations_distorted.geojson"),
    fetchJSON("/data/labels_geo.geojson"),
    fetchJSON("/data/labels_distorted.geojson"),
  ]);

  return {
    hexgrid: { geo: hexgridGeo, distorted: hexgridDist },
    subwayRoutes: { geo: subwayRoutesGeo, distorted: subwayRoutesDist },
    subwayStations: { geo: subwayStationsGeo, distorted: subwayStationsDist },
    labels: { geo: labelsGeo, distorted: labelsDist },
  };
}
