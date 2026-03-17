/**
 * UI interactions: toggle button, hover/click, about modal.
 */

const BOROUGH_COLORS = {
  Manhattan: "#d4a574",
  Brooklyn: "#5b9b8a",
  Queens: "#8b7eb8",
  Bronx: "#c47c6c",
  "Staten Island": "#7a8fa6",
};

export function setupUI(map, animator) {
  setupToggle(animator);
  setupHover(map);
  setupAboutModal();
}

function setupToggle(animator) {
  const btn = document.getElementById("toggle-btn");
  const label = document.getElementById("toggle-label");

  btn.addEventListener("click", () => {
    const isTimespace = animator.toggle();
    label.textContent = isTimespace ? "Show Geographic" : "Show Timespace";
    btn.classList.toggle("active", isTimespace);
  });

  // Keyboard shortcut: space bar
  document.addEventListener("keydown", (e) => {
    if (e.code === "Space" && e.target === document.body) {
      e.preventDefault();
      btn.click();
    }
  });
}

function setupHover(map) {
  const infoPanel = document.getElementById("info-panel");
  const infoContent = document.getElementById("info-content");
  let hoveredName = null;

  map.on("mousemove", "hex-fills-geo", (e) => {
    if (e.features.length === 0) return;
    const feature = e.features[0];
    const name = feature.properties.nta;
    const borough = feature.properties.borough;

    if (!name || name === hoveredName) return;
    hoveredName = name;

    // Highlight all hexes in the same NTA
    map.setFilter("hex-highlight", ["==", "nta", name]);
    map.setPaintProperty("hex-highlight", "fill-opacity", 0.15);
    map.getCanvas().style.cursor = "pointer";

    const color = BOROUGH_COLORS[borough] || "#888";
    infoContent.innerHTML = `
      <h3>${name}</h3>
      <span class="borough-badge" style="background: ${color}">${borough}</span>
    `;
    infoPanel.classList.remove("hidden");
  });

  map.on("mouseleave", "hex-fills-geo", () => {
    hoveredName = null;
    map.setFilter("hex-highlight", ["==", "nta", ""]);
    map.setPaintProperty("hex-highlight", "fill-opacity", 0);
    map.getCanvas().style.cursor = "";
    infoPanel.classList.add("hidden");
  });

  // Subway station hover
  map.on("mouseenter", "subway-dots", (e) => {
    if (e.features.length === 0) return;
    const f = e.features[0];
    map.getCanvas().style.cursor = "pointer";
    infoContent.innerHTML = `
      <h3>${f.properties.name}</h3>
      <p>Routes: ${f.properties.routes || "N/A"}</p>
    `;
    infoPanel.classList.remove("hidden");
  });

  map.on("mouseleave", "subway-dots", () => {
    map.getCanvas().style.cursor = "";
    infoPanel.classList.add("hidden");
  });
}

function setupAboutModal() {
  const modal = document.getElementById("about-modal");
  const openBtn = document.getElementById("about-btn");
  const closeBtn = document.getElementById("about-close");
  const backdrop = document.getElementById("about-backdrop");

  function open() {
    modal.classList.remove("hidden");
  }
  function close() {
    modal.classList.add("hidden");
  }

  openBtn.addEventListener("click", open);
  closeBtn.addEventListener("click", close);
  backdrop.addEventListener("click", close);
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") close();
  });
}
