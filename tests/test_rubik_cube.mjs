import assert from "node:assert/strict";
import {readFile} from "node:fs/promises";

const code = await readFile(new URL("../ui/components/rubik_cube.js", import.meta.url), "utf8");
const {FACES,solvedCube,turnCube,cubeFromHistory,isSolvedCube,scrambleMoves} = await import(`data:text/javascript;base64,${Buffer.from(code).toString("base64")}`);
const canonical = cube => cube.map(s=>`${s.id}:${s.p.join(",")}:${s.n.join(",")}`).sort();
const original = solvedCube();
assert.equal(original.length,54);
assert.equal(isSolvedCube(original),true);
for (const face of Object.keys(FACES)) {
  assert.deepEqual(canonical(turnCube(turnCube(original,face,1),face,-1)),canonical(original),`${face} inverse`);
  let cube = original;
  for (let i=0;i<4;i++) cube = turnCube(cube,face);
  assert.deepEqual(canonical(cube),canonical(original),`${face} four turns`);
  const once = turnCube(original,face);
  assert.equal(isSolvedCube(once),false,`${face} moves adjacent stickers`);
  assert.equal(once.filter((s,i)=>s.p.join()!==original[i].p.join() || s.n.join()!==original[i].n.join()).length,20,`${face} moves twenty stickers, leaving the center`);
}
// Two turns of opposite faces commute; adjacent face turns generally do not.
for (const [a,b] of [["F","B"],["L","R"],["U","D"]]) {
  assert.deepEqual(canonical(turnCube(turnCube(original,a),b)),canonical(turnCube(turnCube(original,b),a)));
}
assert.notDeepEqual(canonical(turnCube(turnCube(original,"F"),"R")),canonical(turnCube(turnCube(original,"R"),"F")));
// Right clockwise sends a top-right sticker to the back-right face.
const known = turnCube(original,"R").find(s=>s.id==="U:1:0");
assert.deepEqual(known.n,[0,0,-1]);
assert.deepEqual(known.p,[1,0,-1]);
let seed=275;
const random=()=>((seed=(seed*1664525+1013904223)>>>0)/4294967296);
for (let round=0;round<20;round++) {
  const moves=scrambleMoves(random,100);
  const cube=cubeFromHistory(moves);
  assert.equal(cube.length,54);
  assert.equal(new Set(cube.map(s=>s.id)).size,54);
  assert.equal(new Set(cube.map(s=>s.p.join()+":"+s.n.join())).size,54);
  for (const face of Object.keys(FACES)) assert.equal(cube.filter(s=>s.color===face).length,9);
  for (const sticker of cube) {
    assert.ok(sticker.p.every(v=>[-1,0,1].includes(v)));
    assert.equal(sticker.n.reduce((n,v)=>n+Math.abs(v),0),1);
    assert.equal(sticker.p.find((_,axis)=>sticker.n[axis]!==0),sticker.n.find(v=>v!==0));
  }
  const retrace=moves.slice().reverse().map(move=>({face:move.face,turns:-move.turns}));
  assert.deepEqual(canonical(cubeFromHistory([...moves,...retrace])),canonical(original));
}
assert.throws(()=>turnCube(original,"X"));
assert.throws(()=>turnCube(original,"F",2));
assert.deepEqual(canonical(original),canonical(solvedCube()),"Turns must not mutate source state");
console.log("Rubik cube: six-face inverses/four-turn identities, direction, commutation, 2,000 legal scramble turns and complete retraces pass.");
