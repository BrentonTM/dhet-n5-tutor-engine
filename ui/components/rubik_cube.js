// An inline CCv2 component: no CDN, WebGL, network or third-party engine.
export const FACES = Object.freeze({
  F: {name: "Front", color: "#2fce85", axis: 2, side: 1},
  R: {name: "Right", color: "#ff626b", axis: 0, side: 1},
  U: {name: "Top", color: "#f3f5ff", axis: 1, side: 1},
  B: {name: "Back", color: "#5d9aff", axis: 2, side: -1},
  L: {name: "Left", color: "#ffa74f", axis: 0, side: -1},
  D: {name: "Bottom", color: "#ffd15a", axis: 1, side: -1},
});

export function solvedCube() {
  const stickers = [];
  for (const [face, definition] of Object.entries(FACES)) {
    const other = [0, 1, 2].filter(axis => axis !== definition.axis);
    for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) {
      const p = [0, 0, 0], n = [0, 0, 0];
      p[definition.axis] = definition.side;
      p[other[0]] = a; p[other[1]] = b;
      n[definition.axis] = definition.side;
      stickers.push({id: `${face}:${a}:${b}`, color: face, p, n});
    }
  }
  return stickers;
}

function quarterVector(vector, axis, direction) {
  const [x, y, z] = vector;
  if (axis === 0) return [x, -direction * z, direction * y];
  if (axis === 1) return [direction * z, y, -direction * x];
  return [-direction * y, direction * x, z];
}

export function turnCube(stickers, face, turns = 1) {
  const definition = FACES[face];
  if (!definition || ![1, -1].includes(turns)) throw new Error("Use one legal quarter turn.");
  // Clockwise is seen while looking straight at the selected outside face.
  const direction = -definition.side * turns;
  return stickers.map(sticker => sticker.p[definition.axis] === definition.side
    ? {...sticker, p: quarterVector(sticker.p, definition.axis, direction),
       n: quarterVector(sticker.n, definition.axis, direction)}
    : {...sticker, p: [...sticker.p], n: [...sticker.n]});
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

function safePuzzle(value) {
  const history = Array.isArray(value?.history) ? value.history.filter(move =>
    move && Object.hasOwn(FACES, move.face) && [1, -1].includes(move.turns)).slice(0, 3000) : [];
  return {
    history,
    selected: Object.hasOwn(FACES, value?.selected) ? value.selected : "F",
    yaw: Number.isFinite(value?.yaw) ? value.yaw : -.55,
    pitch: Number.isFinite(value?.pitch) ? Math.max(-1.35, Math.min(1.35, value.pitch)) : .45,
    revision: Number.isFinite(value?.revision) ? value.revision : 0,
  };
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
      mount.puzzle = incoming; mount.cube = cubeFromHistory(incoming.history); mount.draw();
    }
    return mount.cleanup;
  }

  target.innerHTML = `
    <style>
      *{box-sizing:border-box}.rubik{color:var(--st-text-color,#edf2ff);font-family:var(--st-font,system-ui,sans-serif);width:100%;max-width:850px;margin:auto}
      .rubik h3{font-size:1.2rem;margin:0}.rubik p{line-height:1.5;font-size:.92rem;margin:.5rem 0}.rubik .muted{opacity:.78}
      .rubik .topline{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}.rubik .badge{font-size:.82rem;border:1px solid #416879;border-radius:20px;padding:6px 11px}
      .rubik .viewer{position:relative;background:linear-gradient(145deg,#101e32,#080e1c);border:1px solid #29435a;border-radius:20px;margin:12px 0;overflow:hidden}
      .rubik canvas{display:block;width:100%;height:300px;touch-action:none;cursor:grab;outline-offset:-4px;border-radius:20px}.rubik canvas:active{cursor:grabbing}.rubik canvas:focus-visible{outline:3px solid #27cdb9}
      .rubik .view-label{position:absolute;left:12px;bottom:10px;color:#b5c9dd;font-size:.75rem;pointer-events:none;background:#0b1429dc;border-radius:14px;padding:5px 9px}
      .rubik button{min-height:46px;border:1px solid var(--st-border-color,#34465e);border-radius:12px;background:var(--st-secondary-background-color,#17243a);color:inherit;padding:10px 12px;font:inherit;font-size:.88rem;cursor:pointer;line-height:1.25}
      .rubik button:hover{filter:brightness(1.13)}.rubik button:focus-visible{outline:3px solid #27cdb9;outline-offset:2px}.rubik button:disabled{opacity:.45;cursor:default}
      .rubik button[aria-pressed=true]{border:2px solid #27cdb9;background:#15675f;color:#fff;padding:9px 11px}
      .rubik .faces{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:7px}.rubik .faces button{display:flex;gap:6px;align-items:center;justify-content:center;padding-left:6px;padding-right:6px}.rubik .dot{width:10px;height:10px;flex:0 0 10px;border-radius:50%}
      .rubik .row{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0}.rubik .row>*{flex:1}.rubik .primary{background:#20c8b3;color:#072027;border-color:#20c8b3;font-weight:650}
      .rubik .mini{display:grid;grid-template-columns:repeat(3,28px);gap:3px}.rubik .tile{display:grid;place-items:center;width:28px;height:28px;border-radius:4px;color:#08101a;font-size:.7rem;font-weight:800}
      .rubik .face-preview{display:flex;align-items:center;gap:14px;margin:12px 0;padding:12px;border:1px solid var(--st-border-color,#34465e);border-radius:14px}.rubik .face-preview p{margin:0}
      .rubik .notice{padding:10px 12px;background:var(--st-secondary-background-color,#17243a);border-radius:12px;min-height:46px}.rubik .small{font-size:.8rem}
      .rubik .view-buttons{display:flex;gap:6px;flex-wrap:wrap}.rubik .view-buttons button{flex:1;font-size:.8rem}
      @media(max-width:540px){.rubik .faces{grid-template-columns:repeat(3,minmax(0,1fr))}.rubik canvas{height:270px}.rubik .row .wide{flex-basis:100%}.rubik .view-buttons button{min-width:45px}.rubik .view-buttons .view-reset{flex-basis:100%}}
      @media(prefers-reduced-motion:reduce){.rubik *{scroll-behavior:auto}}
    </style>
    <section class="rubik" aria-label="Interactive Rubik cube">
      <div class="topline"><h3>Rubik cube</h3><span class="badge" data-status></span></div>
      <p class="muted">Choose a face, then turn it. Drag the cube to look around.</p>
      <div class="viewer"><canvas tabindex="0" role="img" aria-label="Three dimensional Rubik cube. Drag to rotate the view; use the face buttons below to turn a layer."></canvas><span class="view-label">Drag = look around · buttons = turn a face</span></div>
      <div class="view-buttons" aria-label="View controls">
        <button type="button" data-view="left" aria-label="Look left">← View</button><button type="button" data-view="right" aria-label="Look right">View →</button>
        <button type="button" data-view="up" aria-label="Look above">↑ View</button><button type="button" data-view="down" aria-label="Look below">↓ View</button>
        <button type="button" class="view-reset" data-view="reset">Reset view</button>
      </div>
      <p><strong>1. Choose a face</strong></p>
      <div class="faces" aria-label="Choose a cube face">${Object.entries(FACES).map(([key, face]) => `<button type="button" data-face="${key}" aria-pressed="false" aria-label="Select ${face.name.toLowerCase()} face"><span class="dot" style="background:${face.color}"></span>${face.name}</button>`).join("")}</div>
      <div class="face-preview"><div class="mini" aria-hidden="true"></div><p class="small" data-selected></p></div>
      <p><strong>2. Turn the selected face</strong></p>
      <div class="row"><button type="button" class="primary" data-turn="1" aria-label="Turn selected face clockwise">↻ Clockwise</button><button type="button" data-turn="-1" aria-label="Turn selected face counterclockwise">↺ Anticlockwise</button></div>
      <div class="row"><button type="button" data-action="scramble">Scramble</button><button type="button" data-action="undo">Undo</button><button type="button" data-action="guide">Guide one step</button><button type="button" data-action="reset">Start solved</button></div>
      <p class="notice" data-notice role="status" aria-live="polite"></p>
      <p class="muted small">Clockwise is viewed straight at the selected face. “Guide one step” reverses your recorded moves, one at a time. It is a way back, not a shortest-solution solver. With the cube focused: arrow keys change the view; F/R/U/B/L/D turn a face; Shift turns it back.</p>
    </section>`;

  const canvas = target.querySelector("canvas"), ctx = canvas.getContext("2d");
  const puzzle = safePuzzle(data?.puzzle);
  mount = {puzzle, cube:cubeFromHistory(puzzle.history), publish:setStateValue, dragging:null, message:"Try a turn, or scramble to start a puzzle."};
  mounts.set(parentElement, mount);

  function commit(message) {
    mount.message = message;
    mount.puzzle.revision += 1;
    draw();
    mount.publish("puzzle", structuredClone(mount.puzzle));
  }
  function doTurn(face, turns) {
    if (mount.puzzle.history.length >= 3000) {
      mount.message = "This session has 3,000 recorded moves. Undo or start solved to continue."; draw(); return;
    }
    mount.puzzle.selected = face;
    mount.cube = turnCube(mount.cube, face, turns);
    mount.puzzle.history.push({face, turns});
    commit(`${FACES[face].name} turned ${turns === 1 ? "clockwise" : "anticlockwise"}.`);
  }
  function undo(guide) {
    const last = mount.puzzle.history.pop();
    if (!last) return;
    mount.cube = turnCube(mount.cube, last.face, -last.turns);
    mount.puzzle.selected = last.face;
    commit(`${guide ? "Guide" : "Undo"}: ${FACES[last.face].name} ${last.turns === 1 ? "anticlockwise" : "clockwise"}. ${mount.puzzle.history.length} recorded moves left to retrace.`);
  }
  function view(direction) {
    if (direction === "reset") {mount.puzzle.yaw = -.55; mount.puzzle.pitch = .45;}
    if (direction === "left") mount.puzzle.yaw -= .35;
    if (direction === "right") mount.puzzle.yaw += .35;
    if (direction === "up") mount.puzzle.pitch += .25;
    if (direction === "down") mount.puzzle.pitch -= .25;
    mount.puzzle.pitch = Math.max(-1.35, Math.min(1.35, mount.puzzle.pitch));
    commit("View changed. The puzzle's layers have not moved.");
  }
  target.querySelectorAll("[data-face]").forEach(button => button.onclick = () => {
    mount.puzzle.selected = button.dataset.face;
    commit(`${FACES[mount.puzzle.selected].name} selected. Choose a turn direction.`);
  });
  target.querySelectorAll("[data-turn]").forEach(button => button.onclick = () => doTurn(mount.puzzle.selected, Number(button.dataset.turn)));
  target.querySelectorAll("[data-view]").forEach(button => button.onclick = () => view(button.dataset.view));
  target.querySelectorAll("[data-action]").forEach(button => button.onclick = () => {
    if (button.dataset.action === "undo") undo(false);
    if (button.dataset.action === "guide") undo(true);
    if (button.dataset.action === "scramble") {
      mount.puzzle.history = scrambleMoves(); mount.cube = cubeFromHistory(mount.puzzle.history);
      commit("Scrambled with 20 legal quarter turns. Choose a face to begin, or use Guide one step.");
    }
    if (button.dataset.action === "reset") {
      mount.puzzle.history = []; mount.cube = solvedCube(); commit("A fresh solved cube. Try a face turn.");
    }
  });

  canvas.onpointerdown = event => {
    mount.dragging = {id:event.pointerId, x:event.clientX, y:event.clientY};
    canvas.setPointerCapture(event.pointerId); canvas.focus({preventScroll:true});
  };
  canvas.onpointermove = event => {
    const start = mount.dragging;
    if (!start || start.id !== event.pointerId) return;
    mount.puzzle.yaw += (event.clientX - start.x) * .009;
    mount.puzzle.pitch = Math.max(-1.35, Math.min(1.35, mount.puzzle.pitch + (event.clientY - start.y) * .009));
    mount.dragging = {id:event.pointerId,x:event.clientX,y:event.clientY}; draw();
  };
  function endDrag(event) {
    if (!mount.dragging || mount.dragging.id !== event.pointerId) return;
    mount.dragging = null;
    if (canvas.hasPointerCapture(event.pointerId)) canvas.releasePointerCapture(event.pointerId);
    commit("View changed. Choose a face button to turn a layer.");
  }
  canvas.onpointerup = endDrag; canvas.onpointercancel = endDrag;
  canvas.onkeydown = event => {
    const direction = {ArrowLeft:"left",ArrowRight:"right",ArrowUp:"up",ArrowDown:"down"}[event.key];
    const face = event.key.toUpperCase();
    if (direction) {event.preventDefault(); view(direction);}
    else if (Object.hasOwn(FACES, face) && !event.ctrlKey && !event.metaKey && !event.altKey) {
      event.preventDefault(); doTurn(face, event.shiftKey ? -1 : 1);
    }
  };

  function rotate(point) {
    const [x,y,z] = point, cy = Math.cos(mount.puzzle.yaw), sy = Math.sin(mount.puzzle.yaw);
    const cp = Math.cos(mount.puzzle.pitch), sp = Math.sin(mount.puzzle.pitch);
    const xx = x*cy+z*sy, zz = -x*sy+z*cy;
    return [xx,y*cp-zz*sp,y*sp+zz*cp];
  }
  function draw() {
    if (!ctx) return;
    const rect = canvas.getBoundingClientRect(), width = Math.max(240,rect.width), height = rect.height || 300;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.round(width*dpr); canvas.height = Math.round(height*dpr);
    ctx.setTransform(dpr,0,0,dpr,0,0); ctx.clearRect(0,0,width,height);
    const corners = [];
    for (const x of [-1.52,1.52]) for (const y of [-1.52,1.52]) for (const z of [-1.52,1.52]) {
      const v = rotate([x,y,z]), depth = 7/(7-v[2]);
      corners.push([v[0]*depth,v[1]*depth]);
    }
    const minX = Math.min(...corners.map(p=>p[0])), maxX = Math.max(...corners.map(p=>p[0]));
    const minY = Math.min(...corners.map(p=>p[1])), maxY = Math.max(...corners.map(p=>p[1]));
    const scale = Math.min((width-40)/(maxX-minX),(height-60)/(maxY-minY));
    const originX = width/2-(minX+maxX)*scale/2, originY = (height-20)/2+(minY+maxY)*scale/2;
    function project(point) {const v = rotate(point), depth = 7/(7-v[2]); return [originX+v[0]*scale*depth,originY-v[1]*scale*depth,v[2]];}
    const polygons = [];
    for (const sticker of mount.cube) {
      // Perspective visibility: outward normal must face the camera at z=7.
      if (rotate(sticker.n)[2] <= 1.52 / 7) continue;
      const normalAxis = sticker.n.findIndex(value => value !== 0), axes = [0,1,2].filter(axis => axis !== normalAxis);
      const center = sticker.p.map((value,axis) => axis === normalAxis ? value*1.52 : value);
      const points = [[-.455,-.455],[.455,-.455],[.455,.455],[-.455,.455]].map(offset => {
        const point = [...center]; point[axes[0]] += offset[0]; point[axes[1]] += offset[1]; return project(point);
      });
      polygons.push({sticker,points,center:project(center),depth:points.reduce((sum,p)=>sum+p[2],0)/4});
    }
    polygons.sort((a,b)=>a.depth-b.depth);
    for (const polygon of polygons) {
      ctx.beginPath(); polygon.points.forEach((p,i)=>i ? ctx.lineTo(p[0],p[1]) : ctx.moveTo(p[0],p[1])); ctx.closePath();
      ctx.fillStyle = FACES[polygon.sticker.color].color; ctx.fill(); ctx.strokeStyle = "#0c1522"; ctx.lineWidth = 3; ctx.stroke();
      if (polygon.sticker.id.endsWith(":0:0")) {
        ctx.fillStyle = "#101c2b"; ctx.font = "bold 15px system-ui"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
        ctx.fillText(polygon.sticker.color,polygon.center[0],polygon.center[1]);
      }
    }
    const solved = isSolvedCube(mount.cube);
    target.querySelector("[data-status]").textContent = `${solved ? "Solved" : "Keep exploring"} · ${mount.puzzle.history.length} moves`;
    const face = FACES[mount.puzzle.selected];
    target.querySelectorAll("[data-face]").forEach(button => button.setAttribute("aria-pressed",String(button.dataset.face === mount.puzzle.selected)));
    target.querySelector("[data-selected]").textContent = `${face.name} (${mount.puzzle.selected}) face, viewed straight on. The small grid shows its current stickers.`;
    const selected = mount.cube.filter(sticker=>sticker.n[face.axis] === face.side);
    // Face-local right/up directions as viewed from outside.
    const right = {F:[1,0,0],B:[-1,0,0],R:[0,0,-1],L:[0,0,1],U:[1,0,0],D:[1,0,0]}[mount.puzzle.selected];
    const up = {F:[0,1,0],B:[0,1,0],R:[0,1,0],L:[0,1,0],U:[0,0,-1],D:[0,0,1]}[mount.puzzle.selected];
    const dot = (a,b)=>a.reduce((sum,value,index)=>sum+value*b[index],0);
    selected.sort((a,b)=>dot(b.p,up)-dot(a.p,up) || dot(a.p,right)-dot(b.p,right));
    target.querySelector(".mini").innerHTML = selected.map(sticker=>`<span class="tile" style="background:${FACES[sticker.color].color}">${sticker.color}</span>`).join("");
    target.querySelector("[data-notice]").textContent = solved && mount.puzzle.history.length ? "Solved! " + mount.message : mount.message;
    target.querySelector("[data-action=undo]").disabled = !mount.puzzle.history.length;
    target.querySelector("[data-action=guide]").disabled = !mount.puzzle.history.length;
    canvas.setAttribute("aria-label",`Three dimensional Rubik cube. ${solved ? "Solved" : "Unsolved"}. ${face.name} face selected. ${mount.puzzle.history.length} recorded moves. Drag or arrow keys change the view; face buttons turn layers.`);
  }
  mount.draw = draw;
  const resize = new ResizeObserver(draw); resize.observe(canvas);
  mount.cleanup = () => {resize.disconnect(); mounts.delete(parentElement);};
  draw();
  return mount.cleanup;
}
