/**
 * FRIDAY Multimodal Voice Assistant
 * Author: Ayushmaan Shukla
 * Roll / Enrollment No.: 202510101240164
 * Department: Computer Science & Engineering (AI & ML)
 * Institution: Shri Ramswaroop Memorial University
 * Notice: This project is strictly for academic evaluation.
 *         Unauthorized reproduction or submission is a violation of academic integrity.
 */
/* ==============================================================================
   F.R.I.D.A.Y. Interactive 3D Holographic Viewer Engine (Three.js)
   ============================================================================== */

let scene, camera, renderer, controls;
let currentModelGroup = null;
let gridHelper, axesHelper, particleRing;
let isWireframe = false;
let isAutoRotating = true;
let showGrid = true;
let polyCount = 0;
let vertexCount = 0;
let meshList = [];
let selectedMesh = null;

// Initial camera state
const INITIAL_CAMERA_POS = { x: 0, y: 3, z: 6 };

function init() {
  const container = document.getElementById("canvas-container");
  const width = container.clientWidth || window.innerWidth;
  const height = container.clientHeight || window.innerHeight;

  // Scene
  scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0x050811, 0.05);

  // Camera
  camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 1000);
  camera.position.set(INITIAL_CAMERA_POS.x, INITIAL_CAMERA_POS.y, INITIAL_CAMERA_POS.z);

  // Renderer
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(width, height);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.2;
  container.appendChild(renderer.domElement);

  // Controls
  controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.06;
  controls.maxDistance = 25;
  controls.minDistance = 1.2;
  controls.autoRotate = isAutoRotating;
  controls.autoRotateSpeed = 1.2;

  // Holographic Lighting
  const ambientLight = new THREE.AmbientLight(0x00f0ff, 0.4);
  scene.add(ambientLight);

  const keyLight = new THREE.DirectionalLight(0x00f0ff, 1.2);
  keyLight.position.set(5, 8, 5);
  scene.add(keyLight);

  const fillLight = new THREE.DirectionalLight(0x0070f3, 0.8);
  fillLight.position.set(-5, -3, -5);
  scene.add(fillLight);

  const corePointLight = new THREE.PointLight(0x00f0ff, 2.0, 12);
  corePointLight.position.set(0, 0, 0);
  scene.add(corePointLight);

  // Spatial Grid Helper (Cyan Holographic Grid)
  gridHelper = new THREE.GridHelper(16, 24, 0x00f0ff, 0x0c2548);
  gridHelper.position.y = -1.5;
  scene.add(gridHelper);

  // Coordinate Axes
  axesHelper = new THREE.AxesHelper(2);
  axesHelper.position.set(-3.5, -1.4, -3.5);
  scene.add(axesHelper);

  // Decorative Holographic Particle Ring
  createParticleHUD();

  // Load Initial Procedural Model: Arc Reactor Core
  loadProceduralModel("reactor");

  // Window Resize Listener
  window.addEventListener("resize", onWindowResize);

  // Drag and Drop File Listener
  setupDragAndDrop();

  // Streamlit postMessage Event Bridge
  window.addEventListener("message", handleParentMessage);

  // Start Animation Loop
  animate();
}

// Particle HUD Ring
function createParticleHUD() {
  const particleCount = 200;
  const geometry = new THREE.BufferGeometry();
  const positions = new Float32Array(particleCount * 3);
  const radius = 3.6;

  for (let i = 0; i < particleCount; i++) {
    const angle = (i / particleCount) * Math.PI * 2;
    positions[i * 3] = Math.cos(angle) * radius;
    positions[i * 3 + 1] = -1.48;
    positions[i * 3 + 2] = Math.sin(angle) * radius;
  }

  geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  const material = new THREE.PointsMaterial({
    color: 0x00f0ff,
    size: 0.06,
    transparent: true,
    opacity: 0.7
  });

  particleRing = new THREE.Points(geometry, material);
  scene.add(particleRing);
}

// Procedural 3D Holographic Models
function loadProceduralModel(type) {
  if (currentModelGroup) {
    scene.remove(currentModelGroup);
    disposeGroup(currentModelGroup);
  }

  currentModelGroup = new THREE.Group();
  currentModelGroup.name = `Procedural Assembly (${type})`;

  const cyanHoloMaterial = new THREE.MeshStandardMaterial({
    color: 0x0c2847,
    emissive: 0x00f0ff,
    emissiveIntensity: 0.35,
    roughness: 0.3,
    metalness: 0.85,
    wireframe: isWireframe
  });

  const glowingCoreMaterial = new THREE.MeshBasicMaterial({
    color: 0x00f0ff,
    wireframe: isWireframe
  });

  const accentMaterial = new THREE.MeshStandardMaterial({
    color: 0x003d73,
    emissive: 0x0070f3,
    emissiveIntensity: 0.5,
    roughness: 0.2,
    metalness: 0.9,
    wireframe: isWireframe
  });

  if (type === "satellite") {
    // 1. Central Satellite Chassis
    const busGeo = new THREE.BoxGeometry(1.2, 1.2, 1.8);
    const busMesh = new THREE.Mesh(busGeo, cyanHoloMaterial);
    busMesh.name = "Satellite Core Bus";
    currentModelGroup.add(busMesh);

    // 2. Solar Panels
    const wingGeo = new THREE.BoxGeometry(2.4, 0.05, 0.9);
    const leftWing = new THREE.Mesh(wingGeo, accentMaterial);
    leftWing.position.set(-1.9, 0, 0);
    leftWing.name = "Port Solar Array";
    currentModelGroup.add(leftWing);

    const rightWing = new THREE.Mesh(wingGeo, accentMaterial);
    rightWing.position.set(1.9, 0, 0);
    rightWing.name = "Starboard Solar Array";
    currentModelGroup.add(rightWing);

    // 3. Dish Antenna
    const dishGeo = new THREE.SphereGeometry(0.7, 16, 8, 0, Math.PI * 2, 0, Math.PI * 0.4);
    const dishMesh = new THREE.Mesh(dishGeo, cyanHoloMaterial);
    dishMesh.rotation.x = Math.PI;
    dishMesh.position.set(0, 0, 1.2);
    dishMesh.name = "High-Gain Parabolic Reflector";
    currentModelGroup.add(dishMesh);

  } else if (type === "torus") {
    // Quantum Torus Assembly
    const torus1Geo = new THREE.TorusGeometry(1.6, 0.2, 16, 64);
    const ring1 = new THREE.Mesh(torus1Geo, cyanHoloMaterial);
    ring1.name = "Outer Containment Ring";
    currentModelGroup.add(ring1);

    const torus2Geo = new THREE.TorusGeometry(1.0, 0.15, 16, 48);
    const ring2 = new THREE.Mesh(torus2Geo, accentMaterial);
    ring2.rotation.x = Math.PI / 3;
    ring2.name = "Internal Field Stabilizer";
    currentModelGroup.add(ring2);

    const coreGeo = new THREE.IcosahedronGeometry(0.5, 2);
    const core = new THREE.Mesh(coreGeo, glowingCoreMaterial);
    core.name = "Zero-Point Singularity";
    currentModelGroup.add(core);

  } else if (type === "cube") {
    // Tesseract Cybernetic Cage
    const outerGeo = new THREE.BoxGeometry(2.0, 2.0, 2.0);
    const outerMesh = new THREE.Mesh(outerGeo, new THREE.MeshStandardMaterial({
      color: 0x00f0ff,
      wireframe: true,
      emissive: 0x00f0ff,
      emissiveIntensity: 0.6
    }));
    outerMesh.name = "Outer Hypercube Frame";
    currentModelGroup.add(outerMesh);

    const innerGeo = new THREE.OctahedronGeometry(1.0, 1);
    const innerMesh = new THREE.Mesh(innerGeo, accentMaterial);
    innerMesh.name = "Inner Crystalline Matrix";
    currentModelGroup.add(innerMesh);

  } else {
    // Default: Arc Reactor Assembly
    // Outer torus ring
    const ringGeo = new THREE.TorusGeometry(1.5, 0.28, 16, 50);
    const ringMesh = new THREE.Mesh(ringGeo, cyanHoloMaterial);
    ringMesh.name = "Primary Toroidal Housing";
    currentModelGroup.add(ringMesh);

    // Glowing core cylinder
    const coreGeo = new THREE.CylinderGeometry(0.8, 0.8, 0.4, 32);
    const coreMesh = new THREE.Mesh(coreGeo, glowingCoreMaterial);
    coreMesh.rotation.x = Math.PI / 2;
    coreMesh.name = "Palladium-Core Emitter";
    currentModelGroup.add(coreMesh);

    // 10 Radial Magnetic Induction Coils
    const coilCount = 10;
    for (let i = 0; i < coilCount; i++) {
      const angle = (i / coilCount) * Math.PI * 2;
      const coilGeo = new THREE.BoxGeometry(0.24, 0.35, 0.5);
      const coilMesh = new THREE.Mesh(coilGeo, accentMaterial);
      coilMesh.position.x = Math.cos(angle) * 1.5;
      coilMesh.position.y = Math.sin(angle) * 1.5;
      coilMesh.rotation.z = angle;
      coilMesh.name = `Induction Solenoid ${i + 1}`;
      currentModelGroup.add(coilMesh);
    }
  }

  scene.add(currentModelGroup);
  updateModelTelemetry(currentModelGroup.name);
}

// Model Telemetry & Hierarchy Parsing
function updateModelTelemetry(modelName) {
  polyCount = 0;
  vertexCount = 0;
  meshList = [];

  if (!currentModelGroup) return;

  currentModelGroup.traverse((child) => {
    if (child.isMesh && child.geometry) {
      meshList.push(child);
      const geo = child.geometry;
      if (geo.index) {
        polyCount += geo.index.count / 3;
      } else if (geo.attributes.position) {
        polyCount += geo.attributes.position.count / 3;
      }
      if (geo.attributes.position) {
        vertexCount += geo.attributes.position.count;
      }
    }
  });

  polyCount = Math.round(polyCount);

  // Update HUD text
  const nameEl = document.getElementById("hud-model-name");
  if (nameEl) nameEl.innerText = modelName || "Holographic Projection";

  const polyEl = document.getElementById("hud-poly-count");
  if (polyEl) polyEl.innerText = polyCount.toLocaleString();

  const meshEl = document.getElementById("hud-mesh-count");
  if (meshEl) meshEl.innerText = meshList.length;

  populateHierarchyPanel();
}

function populateHierarchyPanel() {
  const listEl = document.getElementById("hierarchy-list");
  if (!listEl) return;
  listEl.innerHTML = "";

  meshList.forEach((mesh, index) => {
    const li = document.createElement("li");
    li.className = "hierarchy-item";
    li.innerHTML = `<span>${mesh.name || `Component_${index + 1}`}</span><span style="color:#00f0ff">#${index+1}</span>`;
    li.onclick = () => selectMeshComponent(mesh, li);
    listEl.appendChild(li);
  });
}

function selectMeshComponent(mesh, element) {
  // Reset previous
  if (selectedMesh && selectedMesh.material && selectedMesh._origMaterial) {
    selectedMesh.material = selectedMesh._origMaterial;
  }

  document.querySelectorAll(".hierarchy-item").forEach(el => el.classList.remove("selected"));
  if (element) element.classList.add("selected");

  selectedMesh = mesh;
  if (!mesh._origMaterial) {
    mesh._origMaterial = mesh.material;
  }

  // Highlight selection with cyan pulse material
  mesh.material = new THREE.MeshStandardMaterial({
    color: 0x00f0ff,
    emissive: 0x00f0ff,
    emissiveIntensity: 0.9,
    wireframe: true
  });

  // Display object info
  const detailsEl = document.getElementById("selected-details");
  if (detailsEl) {
    detailsEl.innerHTML = `
      <div class="meta-row"><span class="meta-label">Selected:</span><span class="meta-val">${mesh.name}</span></div>
      <div class="meta-row"><span class="meta-label">Geometry:</span><span class="meta-val">${mesh.geometry.type}</span></div>
      <div class="meta-row"><span class="meta-label">Vertices:</span><span class="meta-val">${mesh.geometry.attributes.position ? mesh.geometry.attributes.position.count : 0}</span></div>
    `;
  }
}

// GLTF / GLB File Loader
function loadGLTFFile(file) {
  const reader = new FileReader();
  reader.onload = function(e) {
    const contents = e.target.result;
    const loader = new THREE.GLTFLoader();

    loader.parse(contents, "", function(gltf) {
      if (currentModelGroup) {
        scene.remove(currentModelGroup);
        disposeGroup(currentModelGroup);
      }

      currentModelGroup = gltf.scene;
      currentModelGroup.name = file.name || "Custom GLTF Asset";

      // Compute bounding box and center model
      const box = new THREE.Box3().setFromObject(currentModelGroup);
      const center = box.getCenter(new THREE.Vector3());
      const size = box.getSize(new THREE.Vector3());
      const maxDim = Math.max(size.x, size.y, size.z) || 1.0;
      const scale = 3.0 / maxDim;

      currentModelGroup.scale.set(scale, scale, scale);
      currentModelGroup.position.x = -center.x * scale;
      currentModelGroup.position.y = -center.y * scale;
      currentModelGroup.position.z = -center.z * scale;

      scene.add(currentModelGroup);
      applyWireframeState(isWireframe);
      updateModelTelemetry(file.name);
      resetView();
    }, function(err) {
      console.error("GLTF Parse Error:", err);
      alert("Error parsing 3D model asset: " + err.message);
    });
  };
  reader.readAsArrayBuffer(file);
}

// Setup Drag & Drop
function setupDragAndDrop() {
  const container = document.getElementById("canvas-container");
  const overlay = document.getElementById("drop-overlay");

  window.addEventListener("dragover", (e) => {
    e.preventDefault();
    if (overlay) overlay.classList.add("active");
  });

  window.addEventListener("dragleave", (e) => {
    if (e.relatedTarget === null && overlay) {
      overlay.classList.remove("active");
    }
  });

  window.addEventListener("drop", (e) => {
    e.preventDefault();
    if (overlay) overlay.classList.remove("active");
    if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      if (file.name.endsWith(".glb") || file.name.endsWith(".gltf")) {
        loadGLTFFile(file);
      } else {
        alert("Please drop a valid .glb or .gltf 3D file.");
      }
    }
  });
}

// Wireframe Toggle
function toggleWireframe() {
  setWireframe(!isWireframe);
}

function setWireframe(state) {
  isWireframe = state;
  applyWireframeState(isWireframe);
  const btn = document.getElementById("btn-wireframe");
  if (btn) btn.classList.toggle("active", isWireframe);
}

function applyWireframeState(wireframe) {
  if (!currentModelGroup) return;
  currentModelGroup.traverse((child) => {
    if (child.isMesh && child.material) {
      if (Array.isArray(child.material)) {
        child.material.forEach(m => m.wireframe = wireframe);
      } else {
        child.material.wireframe = wireframe;
      }
    }
  });
}

// Camera Controls
function resetView() {
  camera.position.set(INITIAL_CAMERA_POS.x, INITIAL_CAMERA_POS.y, INITIAL_CAMERA_POS.z);
  controls.target.set(0, 0, 0);
  controls.reset();
}

function rotateModel(axis, degrees) {
  if (!currentModelGroup) return;
  const radians = (degrees * Math.PI) / 180;
  if (axis === "x") currentModelGroup.rotation.x += radians;
  else if (axis === "y") currentModelGroup.rotation.y += radians;
  else if (axis === "z") currentModelGroup.rotation.z += radians;
}

function zoomCamera(factor) {
  camera.position.multiplyScalar(factor);
}

function toggleAutoRotate() {
  isAutoRotating = !isAutoRotating;
  controls.autoRotate = isAutoRotating;
  const btn = document.getElementById("btn-autorotate");
  if (btn) btn.classList.toggle("active", isAutoRotating);
}

function toggleGrid() {
  showGrid = !showGrid;
  gridHelper.visible = showGrid;
  const btn = document.getElementById("btn-grid");
  if (btn) btn.classList.toggle("active", showGrid);
}

function toggleHierarchyPanel() {
  const panel = document.getElementById("hierarchy-panel");
  if (panel) panel.classList.toggle("collapsed");
}

// Memory Cleanup
function disposeGroup(group) {
  group.traverse((child) => {
    if (child.isMesh) {
      if (child.geometry) child.geometry.dispose();
      if (child.material) {
        if (Array.isArray(child.material)) {
          child.material.forEach(m => m.dispose());
        } else {
          child.material.dispose();
        }
      }
    }
  });
}

// Window Resize
function onWindowResize() {
  const container = document.getElementById("canvas-container");
  const width = container.clientWidth;
  const height = container.clientHeight;
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  renderer.setSize(width, height);
}

// Natural Language / Action Dispatcher
function executeViewerAction(action) {
  if (!action || !action.action) return;
  const act = action.action.toLowerCase();
  const params = action.params || {};

  switch (act) {
    case "rotate":
      rotateModel(params.axis || "y", params.degrees || 45);
      break;
    case "zoom":
      zoomCamera(params.factor || 0.8);
      break;
    case "wireframe":
      if (params.enabled !== undefined) setWireframe(params.enabled);
      else toggleWireframe();
      break;
    case "reset":
      resetView();
      break;
    case "auto_rotate":
      if (params.enabled !== undefined) {
        isAutoRotating = params.enabled;
        controls.autoRotate = isAutoRotating;
      } else {
        toggleAutoRotate();
      }
      break;
    case "grid":
      if (params.enabled !== undefined) {
        showGrid = params.enabled;
        gridHelper.visible = showGrid;
      } else {
        toggleGrid();
      }
      break;
    case "procedural":
      loadProceduralModel(params.type || "reactor");
      break;
    case "hierarchy":
      const panel = document.getElementById("hierarchy-panel");
      if (panel) panel.classList.remove("collapsed");
      break;
    default:
      console.log("Unrecognized 3D viewer action:", act);
  }
}

// Streamlit PostMessage Handler
function handleParentMessage(event) {
  if (event.data && event.data.type === "FRIDAY_3D_ACTION") {
    if (Array.isArray(event.data.actions)) {
      event.data.actions.forEach(executeViewerAction);
    } else if (event.data.action) {
      executeViewerAction(event.data.action);
    }
  }
}

// Render Loop
function animate() {
  requestAnimationFrame(animate);

  controls.update();

  // Subtle HUD particle rotation
  if (particleRing) {
    particleRing.rotation.y += 0.002;
  }

  renderer.render(scene, camera);
}

// Expose API globally
window.fridayViewer = {
  executeAction: executeViewerAction,
  loadProceduralModel: loadProceduralModel,
  setWireframe: setWireframe,
  toggleWireframe: toggleWireframe,
  toggleAutoRotate: toggleAutoRotate,
  toggleGrid: toggleGrid,
  resetView: resetView,
  rotateModel: rotateModel,
  zoomCamera: zoomCamera,
  toggleHierarchyPanel: toggleHierarchyPanel
};

window.onload = init;

