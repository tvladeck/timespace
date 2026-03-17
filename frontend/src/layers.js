/**
 * Add all map layers — both geographic and distorted versions.
 * Animation works by cross-fading opacity between the two sets.
 */
export function addAllLayers(map, data) {
  // Sources — both geo and distorted loaded upfront
  map.addSource("hexgrid-geo", { type: "geojson", data: data.hexgrid.geo });
  map.addSource("hexgrid-dist", { type: "geojson", data: data.hexgrid.distorted });

  map.addSource("subway-routes-geo", { type: "geojson", data: data.subwayRoutes.geo });
  map.addSource("subway-routes-dist", { type: "geojson", data: data.subwayRoutes.distorted });

  map.addSource("subway-stations-geo", { type: "geojson", data: data.subwayStations.geo });
  map.addSource("subway-stations-dist", { type: "geojson", data: data.subwayStations.distorted });

  map.addSource("labels-geo", { type: "geojson", data: data.labels.geo });
  map.addSource("labels-dist", { type: "geojson", data: data.labels.distorted });

  // === Geographic layers (visible by default) ===

  map.addLayer({
    id: "hex-fills-geo",
    type: "fill",
    source: "hexgrid-geo",
    paint: {
      "fill-color": ["get", "color"],
      "fill-opacity": 0.4,
      "fill-outline-color": "rgba(255, 255, 255, 0.15)",
    },
  });

  map.addLayer({
    id: "subway-lines-geo",
    type: "line",
    source: "subway-routes-geo",
    paint: {
      "line-color": ["get", "color"],
      "line-width": 2,
      "line-opacity": 0.8,
    },
  });

  map.addLayer({
    id: "subway-dots-geo",
    type: "circle",
    source: "subway-stations-geo",
    paint: {
      "circle-radius": ["interpolate", ["linear"], ["zoom"], 9, 1, 12, 3, 14, 5],
      "circle-color": "#ffffff",
      "circle-stroke-color": ["get", "color"],
      "circle-stroke-width": ["interpolate", ["linear"], ["zoom"], 9, 0.5, 12, 1.5],
      "circle-opacity": 0.8,
      "circle-stroke-opacity": 0.8,
    },
  });

  map.addLayer({
    id: "labels-geo",
    type: "symbol",
    source: "labels-geo",
    layout: {
      "text-field": ["get", "name"],
      "text-size": ["interpolate", ["linear"], ["zoom"], 10, 8, 13, 12],
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

  // === Distorted layers (hidden by default) ===

  map.addLayer({
    id: "hex-fills-dist",
    type: "fill",
    source: "hexgrid-dist",
    paint: {
      "fill-color": ["get", "color"],
      "fill-opacity": 0,
      "fill-outline-color": "rgba(255, 255, 255, 0.0)",
    },
  });

  map.addLayer({
    id: "subway-lines-dist",
    type: "line",
    source: "subway-routes-dist",
    paint: {
      "line-color": ["get", "color"],
      "line-width": 2,
      "line-opacity": 0,
    },
  });

  map.addLayer({
    id: "subway-dots-dist",
    type: "circle",
    source: "subway-stations-dist",
    paint: {
      "circle-radius": ["interpolate", ["linear"], ["zoom"], 9, 1, 12, 3, 14, 5],
      "circle-color": "#ffffff",
      "circle-stroke-color": ["get", "color"],
      "circle-stroke-width": ["interpolate", ["linear"], ["zoom"], 9, 0.5, 12, 1.5],
      "circle-opacity": 0,
      "circle-stroke-opacity": 0,
    },
  });

  map.addLayer({
    id: "labels-dist",
    type: "symbol",
    source: "labels-dist",
    layout: {
      "text-field": ["get", "name"],
      "text-size": ["interpolate", ["linear"], ["zoom"], 10, 8, 13, 12],
      "text-font": ["Open Sans Regular", "Arial Unicode MS Regular"],
      "text-anchor": "center",
      "text-allow-overlap": false,
      "text-optional": true,
    },
    paint: {
      "text-color": "rgba(255, 255, 255, 0.0)",
      "text-halo-color": "rgba(10, 22, 40, 0.8)",
      "text-halo-width": 1.5,
    },
    minzoom: 11,
  });

  // Hover highlight (on both)
  map.addLayer({
    id: "hex-highlight",
    type: "fill",
    source: "hexgrid-geo",
    paint: { "fill-color": "#ffffff", "fill-opacity": 0 },
    filter: ["==", "nta", ""],
  });
}
