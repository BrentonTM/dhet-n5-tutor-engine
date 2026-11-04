// Inline CCv2 cube. Integer sticker coordinates are the source of truth.
export const FACES = Object.freeze({
  F: {name: "Front", color: "#2fce85", axis: 2, side: 1},
  R: {name: "Right", color: "#ff626b", axis: 0, side: 1},
  U: {name: "Top", color: "#f3f5ff", axis: 1, side: 1},
  B: {name: "Back", color: "#5d9aff", axis: 2, side: -1},
  L: {name: "Left", color: "#ffa74f", axis: 0, side: -1},
  D: {name: "Bottom", color: "#ffd15a", axis: 1, side: -1},
});

export const MOVES = Object.freeze({
  ...Object.fromEntries(Object.entries(FACES).map(([key, face]) =>
    [key, {...face, direction: -face.side}])),
  M: {name: "Middle column", axis: 0, side: 0, direction: 1},
  E: {name: "Middle row", axis: 1, side: 0, direction: 1},
  S: {name: "Middle depth", axis: 2, side: 0, direction: -1},
});

export function solvedCube() {
  const stickers = [];
  for (const [face, definition] of Object.entries(FACES)) {
    const other = [0, 1, 2].filter(axis => axis !== definition.axis);
    for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) {
      const p = [0, 0, 0], n = [0, 0, 0];
      p[definition.axis] = definition.side;
      p[other[0]] = a;
      p[other[1]] = b;
      n[definition.axis] = definition.side;
      stickers.push({id: `${face}:${a}:${b}`, color: face, p, n});
    }
  }
  return stickers;
}

function quarterVector(vector, axis, direction) {
  const [x, y, z] = vector;
  const result = axis === 0 ? [x, -direction * z, direction * y]
    : axis === 1 ? [direction * z, y, -direction * x]
    : [-direction * y, direction * x, z];
  return result.map(value => value || 0);
}

export function turnCube(stickers, face, turns = 1) {
  const definition = MOVES[face];
  if (!definition || ![1, -1, 2, -2].includes(turns)) {
    throw new Error("Use a quarter turn or half turn of a cube layer.");
  }
  const direction = definition.direction * Math.sign(turns);
  return stickers.map(sticker => {
    let p = [...sticker.p], n = [...sticker.n];
    if (p[definition.axis] === definition.side) {
      for (let step = 0; step < Math.abs(turns); step++) {
        p = quarterVector(p, definition.axis, direction);
        n = quarterVector(n, definition.axis, direction);
      }
    }
    return {...sticker, p, n};
  });
}

export function cubeFromHistory(history) {
  let cube = solvedCube();
  for (const move of history) cube = turnCube(cube, move.face, move.turns);
  return cube;
}

export function isSolvedCube(stickers) {
  return Object.values(FACES).every(face => {
    const colors = stickers.filter(s => s.n[face.axis] === face.side).map(s => s.color);
    return colors.length === 9 && colors.every(color => color === colors[0]);
  });
}

export function scrambleMoves(random = Math.random, count = 20) {
  const faces = Object.keys(FACES), moves = [];
  for (let i = 0; i < count; i++) {
    const choices = faces.filter(face => face !== moves.at(-1)?.face);
    const face = choices[Math.min(choices.length - 1, Math.floor(random() * choices.length))];
    moves.push({face, turns: random() < .5 ? 1 : -1});
  }
  return moves;
}

// Match the finger's screen direction to a physical layer's projected motion.
export function moveForSwipe(sticker, delta, project) {
  const length = Math.hypot(...delta);
  if (!length) return null;
  const center = sticker.p.map((value, axis) => value + sticker.n[axis] * .5);
  const origin = project(center);
  let best = null;
  for (let axis = 0; axis < 3; axis++) {
    if (sticker.n[axis]) continue;
    const [x, y, z] = center;
    const velocity = [[0, -z, y], [z, 0, -x], [-y, x, 0]][axis];
    const next = project(center.map((value, index) => value + velocity[index] * .1));
    const dx = next[0] - origin[0], dy = next[1] - origin[1];
    const distance = Math.hypot(dx, dy);
    if (distance < .0001) continue;
    const alignment = (dx * delta[0] + dy * delta[1]) / (distance * length);
    if (best && best.alignment >= Math.abs(alignment)) continue;
    const [face, definition] = Object.entries(MOVES).find(([, move]) =>
      move.axis === axis && move.side === sticker.p[axis]);
    best = {face, turns: Math.sign(alignment) * definition.direction,
            alignment: Math.abs(alignment)};
  }
  return best && best.alignment >= .65 ? {face: best.face, turns: best.turns} : null;
}

function safePuzzle(value) {
  const history = Array.isArray(value?.history) ? value.history.filter(move =>
    move && Object.hasOwn(MOVES, move.face) && [1, -1, 2, -2].includes(move.turns)).slice(0, 3000) : [];
  return {
    history,
    selected: Object.hasOwn(FACES, value?.selected) ? value.selected : "F",
    mode: value?.mode === "view" ? "view" : "turn",
    yaw: Number.isFinite(value?.yaw) ? value.yaw : -.55,
    pitch: Number.isFinite(value?.pitch) ? Math.max(-1.4, Math.min(1.4, value.pitch)) : .45,
    revision: Number.isFinite(value?.revision) ? value.revision : 0,
  };
}

function pointInPolygon(point, polygon) {
  let inside = false;
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const a = polygon[i], b = polygon[j];
    if ((a[1] > point[1]) !== (b[1] > point[1])
        && point[0] < (b[0] - a[0]) * (point[1] - a[1]) / (b[1] - a[1]) + a[0]) {
      inside = !inside;
    }
  }
  return inside;
}

const mounts = new WeakMap();

export default function render(component) {
  const {parentElement, data, setStateValue} = component;
  const target = parentElement.querySelector(".tx-rubik-root");
  if (!target) return;
  let mount = mounts.get(parentElement);
  if (mount) {
    mount.publish = setStateValue;
    const incoming = safePuzzle(data?.puzzle);
    if (incoming.revision > mount.puzzle.revision) {
      mount.cancelTurn();
      mount.puzzle = incoming;
      mount.cube = cubeFromHistory(incoming.history);
      mount.draw();
    }
    return mount.cleanup;
  }

  target.innerHTML = `
    <style>
      *{box-sizing:border-box}
      .rubik{color:var(--st-text-color,#edf2ff);font-family:var(--st-font,system-ui,sans-serif);width:100%;max-width:760px;margin:auto;container-type:inline-size}
      .rubik h3{font-size:1.2rem;margin:0}.rubik p{line-height:1.45;font-size:.9rem;margin:8px 0}
      .rubik .muted{color:#a9bacd}.rubik .topline{display:flex;align-items:center;justify-content:space-between;gap:8px;flex-wrap:wrap}
      .rubik .badge{font-size:.78rem;border:1px solid #416879;border-radius:20px;padding:6px 10px;white-space:nowrap}
      .rubik .viewer{position:relative;background:radial-gradient(ellipse at 50% 38%,#193249,#080e1c 75%);border:1px solid #29435a;border-radius:18px;overflow:hidden;margin:10px 0}
      .rubik canvas{display:block;width:100%;height:330px;touch-action:none;cursor:grab;border-radius:18px;outline-offset:-4px;user-select:none}
      .rubik canvas:active{cursor:grabbing}.rubik canvas:focus-visible{outline:3px solid #27cdb9}
      .rubik .view-label{position:absolute;bottom:8px;left:8px;right:8px;text-align:center;color:#bdd1e0;font-size:.72rem;pointer-events:none}
      .rubik button{min-height:48px;min-width:0;touch-action:manipulation;border:1px solid var(--st-border-color,#34465e);border-radius:12px;background:var(--st-secondary-background-color,#17243a);color:inherit;padding:9px 8px;font:inherit;font-size:.86rem;cursor:pointer;line-height:1.25}
      .rubik button:hover{filter:brightness(1.13)}.rubik button:focus-visible{outline:3px solid #27cdb9;outline-offset:2px}
      .rubik button:disabled{opacity:.45;cursor:default}.rubik button[aria-pressed=true]{border-color:#27cdb9;background:#14554f;box-shadow:inset 0 0 0 1px #27cdb9}
      .rubik .modes{display:grid;grid-template-columns:1fr 1fr;gap:8px}
      .rubik .faces{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:6px}
      .rubik .faces button{display:flex;gap:6px;align-items:center;justify-content:center}
      .rubik .dot{width:11px;height:11px;flex:0 0 11px;border-radius:50%}
      .rubik .turns{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin:10px 0}
      .rubik .turns button{font-weight:650}.rubik .turns button:last-child{background:#087f79;border-color:#24c7b7}
      .rubik .actions{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}
      .rubik .notice{min-height:38px;padding:8px 0;color:#b9d6dd;font-size:.82rem}
      .rubik details{border-top:1px solid #29384f;padding-top:10px;margin-top:4px}
      .rubik summary{cursor:pointer;min-height:36px;font-size:.85rem}
      .rubik .view-buttons{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:6px;margin:8px 0}
      .rubik .mini{display:grid;grid-template-columns:repeat(3,24px);gap:3px}
      .rubik .tile{display:grid;place-items:center;height:24px;border-radius:4px;color:#08101a;font-size:.65rem;font-weight:800}
      .rubik .face-preview{display:flex;align-items:center;gap:14px;margin:10px 0}.rubik .face-preview p{font-size:.8rem}
      @container(max-width:520px){
        .rubik canvas{height:280px}.rubik .faces{grid-template-columns:repeat(3,minmax(0,1fr))}
        .rubik .actions{grid-template-columns:1fr 1fr}.rubik .view-buttons{grid-template-columns:repeat(4,minmax(0,1fr))}
        .rubik .view-reset{grid-column:1/-1}.rubik .turns button{font-size:.82rem;padding:10px 4px}
      }
      @media(prefers-reduced-motion:reduce){.rubik *{scroll-behavior:auto}}
    </style>
    <section class="rubik" aria-label="Interactive Rubik cube">
      <div class="topline"><h3>Rubik cube</h3><span class="badge" data-status></span></div>
      <p class="muted">Swipe a row or column to turn it. Drag the background to look around.</p>
      <div class="modes" aria-label="Cube interaction">
        <button type="button" data-mode="turn" aria-pressed="true">Turn layers</button>
        <button type="button" data-mode="view" aria-pressed="false">Rotate view</button>
      </div>
      <div class="viewer">
        <canvas tabindex="0" role="img" aria-label="Interactive three dimensional Rubik cube"></canvas>
        <span class="view-label">Swipe a layer · two fingers rotate the view</span>
      </div>
      <div class="faces" aria-label="Choose a cube face">
        ${Object.entries(FACES).map(([key, face]) => `<button type="button" data-face="${key}" aria-pressed="false" aria-label="Select ${face.name.toLowerCase()} face"><span class="dot" style="background:${face.color}"></span>${face.name}</button>`).join("")}
      </div>
      <div class="turns" aria-label="Turn the selected face">
        <button type="button" data-turn="-1" aria-label="Turn selected face counterclockwise">↺ 90°</button>
        <button type="button" data-turn="2" aria-label="Turn selected face 180 degrees">180°</button>
        <button type="button" data-turn="1" aria-label="Turn selected face clockwise">↻ 90°</button>
      </div>
      <div class="actions">
        <button type="button" data-action="scramble">Scramble</button>
        <button type="button" data-action="undo">Undo</button>
        <button type="button" data-action="guide">Guide one step</button>
        <button type="button" data-action="reset">Start solved</button>
      </div>
      <p class="notice" data-notice role="status" aria-live="polite"></p>
      <details><summary>View controls &amp; help</summary>
        <div class="view-buttons" aria-label="View controls">
          <button type="button" data-view="left" aria-label="Look left">←</button>
          <button type="button" data-view="right" aria-label="Look right">→</button>
          <button type="button" data-view="up" aria-label="Look above">↑</button>
          <button type="button" data-view="down" aria-label="Look below">↓</button>
          <button type="button" class="view-reset" data-view="reset">Reset view</button>
        </div>
        <div class="face-preview"><div class="mini" aria-hidden="true"></div><p data-selected></p></div>
        <p class="muted">Tap a sticker or a face button to select a face. The 90° arrows turn it as viewed straight on. Swipe any of the three rows or columns, including the middle layer. Use Rotate view or two fingers to look around.</p>
        <p class="muted">Guide one step retraces your last recorded move. With the cube focused, arrow keys change the view. F/R/U/B/L/D and M/E/S turn layers, Shift reverses a turn, and Alt makes a half turn.</p>
      </details>
    </section>`;

  const canvas = target.querySelector("canvas");
  const ctx = canvas.getContext("2d");
  const puzzle = safePuzzle(data?.puzzle);
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  mount = {
    puzzle, cube: cubeFromHistory(puzzle.history), publish: setStateValue,
    pointers: new Map(), gesture: null, animation: null,
    frame: null, disposed: false, polygons: [], project: null,
    message: "Swipe a layer, or choose a face and tap a turn.",
  };
  mounts.set(parentElement, mount);

  function publish() {
    mount.puzzle.revision += 1;
    mount.publish("puzzle", structuredClone(mount.puzzle));
  }
  function commit(message) {
    mount.message = message;
    draw();
    publish();
  }
  function cancelTurn() {
    if (mount.frame !== null) cancelAnimationFrame(mount.frame);
    mount.frame = null;
    mount.animation = null;
  }
  mount.cancelTurn = cancelTurn;

  function doTurn(face, turns, retrace = false) {
    if (mount.animation) return;
    if (!retrace && mount.puzzle.history.length >= 3000) {
      mount.message = "Move limit reached. Undo or start solved to continue.";
      draw();
      return;
    }
    const definition = MOVES[face];
    if (Object.hasOwn(FACES, face)) mount.puzzle.selected = face;
    const finish = () => {
      mount.cube = turnCube(mount.cube, face, turns);
      if (retrace) mount.puzzle.history.pop();
      else mount.puzzle.history.push({face, turns});
      cancelTurn();
      const direction = Math.abs(turns) === 2 ? "180°" : turns === 1 ? "clockwise" : "anticlockwise";
      commit(`${retrace ? "Retraced" : "Turned"} ${definition.name.toLowerCase()} ${direction}.`);
    };
    if (reducedMotion.matches) {
      finish();
      return;
    }
    mount.animation = {axis: definition.axis, side: definition.side, angle: 0};
    const duration = Math.abs(turns) === 2 ? 320 : 230;
    let started = null;
    function frame(now) {
      if (mount.disposed) return;
      if (started === null) started = now;
      const progress = Math.min(1, (now - started) / duration);
      const eased = 1 - (1 - progress) ** 3;
      mount.animation.angle = definition.direction * turns * Math.PI / 2 * eased;
      draw();
      if (progress < 1) mount.frame = requestAnimationFrame(frame);
      else finish();
    }
    mount.frame = requestAnimationFrame(frame);
    draw();
  }

  function undo() {
    const last = mount.puzzle.history.at(-1);
    if (last) doTurn(last.face, -last.turns, true);
  }
  function view(direction) {
    if (direction === "reset") {mount.puzzle.yaw = -.55; mount.puzzle.pitch = .45;}
    if (direction === "left") mount.puzzle.yaw -= .35;
    if (direction === "right") mount.puzzle.yaw += .35;
    if (direction === "up") mount.puzzle.pitch += .25;
    if (direction === "down") mount.puzzle.pitch -= .25;
    mount.puzzle.pitch = Math.max(-1.4, Math.min(1.4, mount.puzzle.pitch));
    commit("View adjusted.");
  }

  target.querySelectorAll("[data-mode]").forEach(button => button.onclick = () => {
    mount.puzzle.mode = button.dataset.mode;
    commit(mount.puzzle.mode === "view" ? "Drag to rotate the view." : "Swipe a row or column to turn it.");
  });
  target.querySelectorAll("[data-face]").forEach(button => button.onclick = () => {
    mount.puzzle.selected = button.dataset.face;
    commit(`${FACES[mount.puzzle.selected].name} selected. Tap an arrow to turn it.`);
  });
  target.querySelectorAll("[data-turn]").forEach(button => button.onclick = () =>
    doTurn(mount.puzzle.selected, Number(button.dataset.turn)));
  target.querySelectorAll("[data-view]").forEach(button => button.onclick = () => view(button.dataset.view));
  target.querySelectorAll("[data-action]").forEach(button => button.onclick = () => {
    if (mount.animation) return;
    if (button.dataset.action === "undo" || button.dataset.action === "guide") undo();
    if (button.dataset.action === "scramble") {
      mount.puzzle.history = scrambleMoves();
      mount.cube = cubeFromHistory(mount.puzzle.history);
      commit("Scrambled with 20 legal turns.");
    }
    if (button.dataset.action === "reset") {
      mount.puzzle.history = [];
      mount.cube = solvedCube();
      commit("Solved cube ready.");
    }
  });

  function pointerPosition(event) {
    const rect = canvas.getBoundingClientRect();
    return [event.clientX - rect.left, event.clientY - rect.top];
  }
  function pointerCenter() {
    const points = [...mount.pointers.values()];
    return points.reduce((sum, point) => [sum[0] + point[0] / points.length,
      sum[1] + point[1] / points.length], [0, 0]);
  }
  function stickerAt(point) {
    for (let i = mount.polygons.length - 1; i >= 0; i--) {
      const polygon = mount.polygons[i];
      if (pointInPolygon(point, polygon.points)) return polygon.sticker || null;
    }
    return null;
  }
  canvas.onpointerdown = event => {
    if (event.button !== 0 || mount.animation) return;
    const point = pointerPosition(event);
    mount.pointers.set(event.pointerId, point);
    canvas.setPointerCapture(event.pointerId);
    canvas.focus({preventScroll: true});
    const center = pointerCenter();
    const sticker = mount.pointers.size === 1 ? stickerAt(point) : null;
    mount.gesture = {
      type: mount.puzzle.mode === "view" || !sticker || mount.pointers.size > 1 ? "view" : "turn",
      start: center, last: center, sticker, project: mount.project, moved: false,
    };
  };
  canvas.onpointermove = event => {
    if (!mount.pointers.has(event.pointerId) || !mount.gesture) return;
    mount.pointers.set(event.pointerId, pointerPosition(event));
    const gesture = mount.gesture, center = pointerCenter();
    if (Math.hypot(center[0] - gesture.start[0], center[1] - gesture.start[1]) > 12) {
      gesture.moved = true;
    }
    if (gesture.type === "view") {
      mount.puzzle.yaw += (center[0] - gesture.last[0]) * .008;
      mount.puzzle.pitch = Math.max(-1.4, Math.min(1.4,
        mount.puzzle.pitch + (center[1] - gesture.last[1]) * .008));
      draw();
    }
    gesture.last = center;
  };
  function endPointer(event, cancelled = false) {
    if (!mount.pointers.has(event.pointerId)) return;
    const gesture = mount.gesture;
    mount.pointers.delete(event.pointerId);
    mount.gesture = null;
    if (canvas.hasPointerCapture(event.pointerId)) canvas.releasePointerCapture(event.pointerId);
    // After a two-finger gesture, lift both fingers before starting another move.
    if (mount.pointers.size) {
      if (!cancelled && gesture?.type === "view" && gesture.moved) commit("View adjusted.");
      return;
    }
    if (!gesture || cancelled) return;
    if (gesture.type === "view") {
      if (gesture.moved) commit("View adjusted.");
      return;
    }
    const end = pointerPosition(event);
    const delta = [end[0] - gesture.start[0], end[1] - gesture.start[1]];
    if (Math.hypot(...delta) >= 18) {
      const move = moveForSwipe(gesture.sticker, delta, gesture.project);
      if (move) doTurn(move.face, move.turns);
    } else {
      const face = Object.entries(FACES).find(([, definition]) =>
        gesture.sticker.n[definition.axis] === definition.side)?.[0];
      if (face) {
        mount.puzzle.selected = face;
        commit(`${FACES[face].name} selected.`);
      }
    }
  }
  canvas.onpointerup = event => endPointer(event);
  canvas.onpointercancel = event => endPointer(event, true);
  canvas.onlostpointercapture = event => endPointer(event, true);
  canvas.onkeydown = event => {
    const direction = {ArrowLeft: "left", ArrowRight: "right", ArrowUp: "up", ArrowDown: "down"}[event.key];
    const face = event.key.toUpperCase();
    if (direction) {event.preventDefault(); view(direction);}
    else if (Object.hasOwn(MOVES, face) && !event.ctrlKey && !event.metaKey) {
      event.preventDefault();
      doTurn(face, (event.shiftKey ? -1 : 1) * (event.altKey ? 2 : 1));
    }
  };

  function rotate(point) {
    const [x, y, z] = point;
    const cy = Math.cos(mount.puzzle.yaw), sy = Math.sin(mount.puzzle.yaw);
    const cp = Math.cos(mount.puzzle.pitch), sp = Math.sin(mount.puzzle.pitch);
    const xx = x * cy + z * sy, zz = -x * sy + z * cy;
    return [xx, y * cp - zz * sp, y * sp + zz * cp];
  }
  function animateVector(vector, position) {
    const animation = mount.animation;
    if (!animation || position[animation.axis] !== animation.side) return vector;
    const [x, y, z] = vector;
    const c = Math.cos(animation.angle), s = Math.sin(animation.angle);
    if (animation.axis === 0) return [x, y * c - z * s, y * s + z * c];
    if (animation.axis === 1) return [x * c + z * s, y, -x * s + z * c];
    return [x * c - y * s, x * s + y * c, z];
  }

  function draw() {
    if (!ctx || mount.disposed) return;
    const rect = canvas.getBoundingClientRect(), width = rect.width, height = rect.height;
    if (width <= 0 || height <= 0) return;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const pixelWidth = Math.round(width * dpr), pixelHeight = Math.round(height * dpr);
    if (canvas.width !== pixelWidth || canvas.height !== pixelHeight) {
      canvas.width = pixelWidth;
      canvas.height = pixelHeight;
    }
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, width, height);
    const corners = [];
    for (const x of [-1.52, 1.52]) for (const y of [-1.52, 1.52]) for (const z of [-1.52, 1.52]) {
      const v = rotate([x, y, z]), depth = 7 / (7 - v[2]);
      corners.push([v[0] * depth, v[1] * depth]);
    }
    const minX = Math.min(...corners.map(p => p[0])), maxX = Math.max(...corners.map(p => p[0]));
    const minY = Math.min(...corners.map(p => p[1])), maxY = Math.max(...corners.map(p => p[1]));
    const scale = Math.min((width - 48) / (maxX - minX), (height - 46) / (maxY - minY)) * .91;
    const originX = width / 2 - (minX + maxX) * scale / 2;
    const originY = (height - 10) / 2 + (minY + maxY) * scale / 2;
    function project(point) {
      const v = rotate(point), depth = 7 / (7 - v[2]);
      return [originX + v[0] * scale * depth, originY - v[1] * scale * depth, v[2]];
    }
    mount.project = project;
    const polygons = [];
    function addPolygon(position, normal, extent, distance, sticker = null) {
      const axis = normal.findIndex(value => value !== 0);
      const axes = [0, 1, 2].filter(index => index !== axis);
      const center = position.map((value, index) => value + normal[index] * distance);
      const rotatedCenter = rotate(animateVector(center, position));
      const rotatedNormal = rotate(animateVector(normal, position));
      if (rotatedNormal[2] * 7 - rotatedNormal.reduce((sum, value, i) =>
        sum + value * rotatedCenter[i], 0) <= 0) return;
      const points = [[-extent, -extent], [extent, -extent], [extent, extent], [-extent, extent]].map(offset => {
        const point = [...center];
        point[axes[0]] += offset[0];
        point[axes[1]] += offset[1];
        return project(animateVector(point, position));
      });
      polygons.push({points, sticker, center: project(animateVector(center, position)),
        depth: points.reduce((sum, point) => sum + point[2], 0) / 4,
        light: rotatedNormal[2]});
    }
    for (const x of [-1, 0, 1]) for (const y of [-1, 0, 1]) for (const z of [-1, 0, 1]) {
      if (x === 0 && y === 0 && z === 0) continue;
      for (const face of Object.values(FACES)) {
        const normal = [0, 0, 0];
        normal[face.axis] = face.side;
        addPolygon([x, y, z], normal, .49, .49);
      }
    }
    for (const sticker of mount.cube) addPolygon(sticker.p, sticker.n, .435, .502, sticker);
    polygons.sort((a, b) => a.depth - b.depth);
    mount.polygons = polygons;
    for (const polygon of polygons) {
      ctx.beginPath();
      polygon.points.forEach((point, index) => index ? ctx.lineTo(point[0], point[1]) : ctx.moveTo(point[0], point[1]));
      ctx.closePath();
      ctx.fillStyle = polygon.sticker ? FACES[polygon.sticker.color].color : "#0b1019";
      ctx.fill();
      ctx.strokeStyle = polygon.sticker ? "#06101b" : "#1b2534";
      ctx.lineWidth = polygon.sticker ? 1.5 : .8;
      ctx.stroke();
      if (polygon.sticker) {
        ctx.fillStyle = `rgba(0, 8, 20, ${(1 - polygon.light) * .17})`;
        ctx.fill();
        if (polygon.sticker.id.endsWith(":0:0")) {
          ctx.fillStyle = "#101c2b";
          ctx.font = "bold 13px system-ui";
          ctx.textAlign = "center";
          ctx.textBaseline = "middle";
          ctx.fillText(polygon.sticker.color, polygon.center[0], polygon.center[1]);
        }
      }
    }
    const solved = isSolvedCube(mount.cube), selectedFace = FACES[mount.puzzle.selected];
    const moveLabel = `${mount.puzzle.history.length} ${mount.puzzle.history.length === 1 ? "move" : "moves"}`;
    target.querySelector("[data-status]").textContent = `${solved ? "Solved" : "Keep exploring"} · ${moveLabel}`;
    target.querySelectorAll("[data-mode]").forEach(button =>
      button.setAttribute("aria-pressed", String(button.dataset.mode === mount.puzzle.mode)));
    target.querySelector(".view-label").textContent = mount.puzzle.mode === "view"
      ? "Drag to look around · tap Turn layers to twist"
      : "Swipe a layer · two fingers rotate the view";
    target.querySelectorAll("[data-face]").forEach(button => {
      button.setAttribute("aria-pressed", String(button.dataset.face === mount.puzzle.selected));
      const face = FACES[button.dataset.face];
      const center = mount.cube.find(sticker => sticker.n[face.axis] === face.side
        && sticker.p.every((value, axis) => axis === face.axis || value === 0));
      if (center) button.querySelector(".dot").style.background = FACES[center.color].color;
    });
    target.querySelector("[data-selected]").textContent = `${selectedFace.name} (${mount.puzzle.selected}), viewed straight on.`;
    const selected = mount.cube.filter(sticker => sticker.n[selectedFace.axis] === selectedFace.side);
    const right = {F: [1, 0, 0], B: [-1, 0, 0], R: [0, 0, -1], L: [0, 0, 1], U: [1, 0, 0], D: [1, 0, 0]}[mount.puzzle.selected];
    const up = {F: [0, 1, 0], B: [0, 1, 0], R: [0, 1, 0], L: [0, 1, 0], U: [0, 0, -1], D: [0, 0, 1]}[mount.puzzle.selected];
    const dot = (a, b) => a.reduce((sum, value, index) => sum + value * b[index], 0);
    selected.sort((a, b) => dot(b.p, up) - dot(a.p, up) || dot(a.p, right) - dot(b.p, right));
    target.querySelector(".mini").innerHTML = selected.map(sticker =>
      `<span class="tile" style="background:${FACES[sticker.color].color}">${sticker.color}</span>`).join("");
    target.querySelector("[data-notice]").textContent = solved && mount.puzzle.history.length
      ? "Solved! " + mount.message : mount.message;
    target.querySelectorAll("[data-turn], [data-action]").forEach(button => {
      button.disabled = Boolean(mount.animation)
        || (["undo", "guide"].includes(button.dataset.action) && !mount.puzzle.history.length);
    });
    canvas.setAttribute("aria-label",
      `Three dimensional Rubik cube. ${solved ? "Solved" : "Unsolved"}. ${selectedFace.name} selected. ${moveLabel}. Swipe a layer to turn it, use two fingers to rotate the view, or use the face buttons.`);
  }

  mount.draw = draw;
  const resize = new ResizeObserver(draw);
  resize.observe(canvas);
  mount.cleanup = () => {
    mount.disposed = true;
    cancelTurn();
    resize.disconnect();
    mount.pointers.clear();
    mounts.delete(parentElement);
  };
  draw();
  return mount.cleanup;
}
