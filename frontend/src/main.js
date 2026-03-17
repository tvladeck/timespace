import "maplibre-gl/dist/maplibre-gl.css";
import { createMap, loadAllData } from "./map.js";
import { addAllLayers } from "./layers.js";
import { setupAnimation } from "./animation.js";
import { setupUI } from "./ui.js";

async function init() {
  const map = createMap();

  map.on("load", async () => {
    const data = await loadAllData();
    addAllLayers(map, data);
    const animator = setupAnimation(map, data);
    setupUI(map, animator);
  });
}

init();
