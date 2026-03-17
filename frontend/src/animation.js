/**
 * Morph animation between geographic and timespace views.
 *
 * Performance optimization: pre-extracts all coordinates into flat
 * Float64Arrays at load time. Each frame just lerps between two arrays
 * and writes back — no JSON cloning or tree walking.
 */

const ANIMATION_DURATION = 1500;

function easeInOutCubic(t) {
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

/**
 * Pre-extract all leaf coordinates from a GeoJSON into a flat array.
 * Returns { flat: Float64Array, offsets: [...] } where offsets track
 * how to write coordinates back into the GeoJSON structure.
 */
function extractCoords(geojson) {
  const coords = [];

  function walk(node) {
    if (Array.isArray(node)) {
      if (node.length >= 2 && typeof node[0] === "number") {
        coords.push(node[0], node[1]);
      } else {
        for (const child of node) walk(child);
      }
    }
  }

  for (const feature of geojson.features) {
    walk(feature.geometry.coordinates);
  }

  return new Float64Array(coords);
}

/**
 * Write interpolated coordinates back into the GeoJSON structure.
 */
function writeCoords(geojson, flat) {
  let idx = 0;

  function walk(node) {
    if (Array.isArray(node)) {
      if (node.length >= 2 && typeof node[0] === "number") {
        node[0] = flat[idx++];
        node[1] = flat[idx++];
      } else {
        for (const child of node) walk(child);
      }
    }
  }

  for (const feature of geojson.features) {
    walk(feature.geometry.coordinates);
  }
}

export function setupAnimation(map, data) {
  let currentT = 0;
  let targetT = 0;
  let animating = false;
  let animationStart = null;
  let startT = 0;

  // Pre-extract coordinate arrays for each source
  const sources = [];
  for (const [name, layerData] of Object.entries(data)) {
    const geoFlat = extractCoords(layerData.geo);
    const distFlat = extractCoords(layerData.distorted);

    // Verify same length
    if (geoFlat.length !== distFlat.length) {
      console.warn(`${name}: coordinate count mismatch (${geoFlat.length} vs ${distFlat.length}), skipping animation`);
      continue;
    }

    // Pre-allocate interpolation buffer and a mutable copy of the geo GeoJSON
    const interpFlat = new Float64Array(geoFlat.length);
    // Deep clone once for the mutable working copy
    const mutableGeoJSON = JSON.parse(JSON.stringify(layerData.geo));

    sources.push({
      name,
      geoFlat,
      distFlat,
      interpFlat,
      mutableGeoJSON,
    });
  }

  function updateSources(t) {
    for (const src of sources) {
      const { geoFlat, distFlat, interpFlat, mutableGeoJSON, name } = src;
      const n = geoFlat.length;

      // Fast lerp on flat arrays
      if (t <= 0) {
        interpFlat.set(geoFlat);
      } else if (t >= 1) {
        interpFlat.set(distFlat);
      } else {
        for (let i = 0; i < n; i++) {
          interpFlat[i] = geoFlat[i] + (distFlat[i] - geoFlat[i]) * t;
        }
      }

      // Write back into mutable GeoJSON
      writeCoords(mutableGeoJSON, interpFlat);

      // Update MapLibre source
      const source = map.getSource(name === "subwayRoutes" ? "subway-routes" :
                                    name === "subwayStations" ? "subway-stations" :
                                    name);
      if (source) {
        source.setData(mutableGeoJSON);
      }
    }
  }

  function animate(timestamp) {
    if (!animationStart) animationStart = timestamp;
    const elapsed = timestamp - animationStart;
    const progress = Math.min(elapsed / ANIMATION_DURATION, 1);
    const easedProgress = easeInOutCubic(progress);

    currentT = startT + (targetT - startT) * easedProgress;
    updateSources(currentT);

    if (progress < 1) {
      requestAnimationFrame(animate);
    } else {
      currentT = targetT;
      animating = false;
      animationStart = null;
    }
  }

  return {
    toggle() {
      targetT = currentT < 0.5 ? 1 : 0;
      startT = currentT;
      animating = true;
      animationStart = null;
      requestAnimationFrame(animate);
      return targetT === 1;
    },
    isTimespace() {
      return currentT > 0.5;
    },
  };
}
