/**
 * Add all map layers with geographic data as initial state.
 */
export function addAllLayers(map, data) {
  // Sources
  map.addSource("hexgrid", {
    type: "geojson",
    data: data.hexgrid.geo,
  });

  map.addSource("subway-routes", {
    type: "geojson",
    data: data.subwayRoutes.geo,
  });

  map.addSource("subway-stations", {
    type: "geojson",
    data: data.subwayStations.geo,
  });

  map.addSource("labels", {
    type: "geojson",
    data: data.labels.geo,
  });

  // Layer 1: Hex grid fills
  map.addLayer({
    id: "hex-fills",
    type: "fill",
    source: "hexgrid",
    paint: {
      "fill-color": ["get", "color"],
      "fill-opacity": 0.4,
      "fill-outline-color": "rgba(255, 255, 255, 0.15)",
    },
  });

  // Layer 2: Subway routes
  map.addLayer({
    id: "subway-lines",
    type: "line",
    source: "subway-routes",
    paint: {
      "line-color": ["get", "color"],
      "line-width": 2,
      "line-opacity": 0.8,
    },
  });

  // Layer 3: Subway stations
  map.addLayer({
    id: "subway-dots",
    type: "circle",
    source: "subway-stations",
    paint: {
      "circle-radius": [
        "interpolate",
        ["linear"],
        ["zoom"],
        9, 1,
        12, 3,
        14, 5,
      ],
      "circle-color": "#ffffff",
      "circle-stroke-color": ["get", "color"],
      "circle-stroke-width": [
        "interpolate",
        ["linear"],
        ["zoom"],
        9, 0.5,
        12, 1.5,
      ],
      "circle-opacity": [
        "interpolate",
        ["linear"],
        ["zoom"],
        9, 0.3,
        11, 0.8,
      ],
    },
  });

  // Layer 4: Hex hover highlight
  map.addLayer({
    id: "hex-highlight",
    type: "fill",
    source: "hexgrid",
    paint: {
      "fill-color": "#ffffff",
      "fill-opacity": 0,
    },
    filter: ["==", "nta", ""],
  });

  // Layer 5: Labels
  map.addLayer({
    id: "labels-nta",
    type: "symbol",
    source: "labels",
    layout: {
      "text-field": ["get", "name"],
      "text-size": [
        "interpolate",
        ["linear"],
        ["zoom"],
        10, 8,
        13, 12,
      ],
      "text-font": ["Open Sans Regular", "Arial Unicode MS Regular"],
      "text-anchor": "center",
      "text-allow-overlap": false,
      "text-optional": true,
    },
    paint: {
      "text-color": "rgba(255, 255, 255, 0.7)",
      "text-halo-color": "rgba(10, 22, 40, 0.8)",
      "text-halo-width": 1.5,
    },
    minzoom: 11,
  });
}
