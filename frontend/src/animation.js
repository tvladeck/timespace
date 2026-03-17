/**
 * Cross-fade animation between geographic and timespace views.
 *
 * Instead of morphing coordinates (which requires expensive setData calls),
 * both geo and distorted layers are pre-loaded and we just animate opacity.
 * This is GPU-accelerated via MapLibre's WebGL renderer — smooth 60fps.
 */

const ANIMATION_DURATION = 1500;

function easeInOutCubic(t) {
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

export function setupAnimation(map, data) {
  let currentT = 0; // 0 = geographic, 1 = distorted
  let targetT = 0;
  let animationStart = null;
  let startT = 0;

  const MAX_HEX_OPACITY = 0.4;
  const MAX_LINE_OPACITY = 0.8;
  const MAX_LABEL_OPACITY = 0.7;

  function setOpacities(t) {
    const geo = 1 - t;
    const dist = t;

    // Hex fills
    map.setPaintProperty("hex-fills-geo", "fill-opacity", geo * MAX_HEX_OPACITY);
    map.setPaintProperty("hex-fills-geo", "fill-outline-color",
      `rgba(255, 255, 255, ${geo * 0.15})`);
    map.setPaintProperty("hex-fills-dist", "fill-opacity", dist * MAX_HEX_OPACITY);
    map.setPaintProperty("hex-fills-dist", "fill-outline-color",
      `rgba(255, 255, 255, ${dist * 0.15})`);

    // Subway lines
    map.setPaintProperty("subway-lines-geo", "line-opacity", geo * MAX_LINE_OPACITY);
    map.setPaintProperty("subway-lines-dist", "line-opacity", dist * MAX_LINE_OPACITY);

    // Subway stations
    map.setPaintProperty("subway-dots-geo", "circle-opacity", geo * 0.8);
    map.setPaintProperty("subway-dots-geo", "circle-stroke-opacity", geo * 0.8);
    map.setPaintProperty("subway-dots-dist", "circle-opacity", dist * 0.8);
    map.setPaintProperty("subway-dots-dist", "circle-stroke-opacity", dist * 0.8);

    // Labels
    map.setPaintProperty("labels-geo", "text-color",
      `rgba(255, 255, 255, ${geo * MAX_LABEL_OPACITY})`);
    map.setPaintProperty("labels-dist", "text-color",
      `rgba(255, 255, 255, ${dist * MAX_LABEL_OPACITY})`);
  }

  function animate(timestamp) {
    if (!animationStart) animationStart = timestamp;
    const elapsed = timestamp - animationStart;
    const progress = Math.min(elapsed / ANIMATION_DURATION, 1);
    const easedProgress = easeInOutCubic(progress);

    currentT = startT + (targetT - startT) * easedProgress;
    setOpacities(currentT);

    if (progress < 1) {
      requestAnimationFrame(animate);
    } else {
      currentT = targetT;
      animationStart = null;
    }
  }

  return {
    toggle() {
      targetT = currentT < 0.5 ? 1 : 0;
      startT = currentT;
      animationStart = null;
      requestAnimationFrame(animate);
      return targetT === 1;
    },
    isTimespace() {
      return currentT > 0.5;
    },
  };
}
