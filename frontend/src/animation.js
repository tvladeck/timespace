/**
 * Morph animation between geographic and timespace views.
 *
 * Interpolates all coordinates: lerp(geo[i], distorted[i], t) with
 * ease-in-out over ~1.5 seconds.
 */

const ANIMATION_DURATION = 1500; // ms

function easeInOutCubic(t) {
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

/**
 * Deep-interpolate GeoJSON coordinates.
 * geo and distorted must have identical structure.
 */
function lerpCoords(geo, distorted, t) {
  if (typeof geo === "number") {
    return geo + (distorted - geo) * t;
  }
  return geo.map((g, i) => lerpCoords(g, distorted[i], t));
}

function interpolateGeoJSON(geoData, distortedData, t) {
  if (t <= 0) return geoData;
  if (t >= 1) return distortedData;

  const result = JSON.parse(JSON.stringify(geoData));
  for (let i = 0; i < result.features.length; i++) {
    const geoCoords = geoData.features[i].geometry.coordinates;
    const distCoords = distortedData.features[i].geometry.coordinates;
    result.features[i].geometry.coordinates = lerpCoords(
      geoCoords,
      distCoords,
      t
    );
  }
  return result;
}

export function setupAnimation(map, data) {
  let currentT = 0; // 0 = geographic, 1 = distorted
  let targetT = 0;
  let animating = false;
  let animationStart = null;
  let startT = 0;

  const sources = [
    { name: "hexgrid", data: data.hexgrid },
    { name: "subway-routes", data: data.subwayRoutes },
    { name: "subway-stations", data: data.subwayStations },
    { name: "labels", data: data.labels },
  ];

  function updateSources(t) {
    for (const source of sources) {
      const interpolated = interpolateGeoJSON(
        source.data.geo,
        source.data.distorted,
        t
      );
      map.getSource(source.name).setData(interpolated);
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
      return targetT === 1; // returns true if transitioning to timespace
    },
    isTimespace() {
      return currentT > 0.5;
    },
  };
}
