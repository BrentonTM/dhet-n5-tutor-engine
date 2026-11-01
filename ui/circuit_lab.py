"""Interactive, browser-based 3D circuit workbench for Industrial Electronics."""

import streamlit.components.v1 as components

from ui.diagram_engine import _three_scripts


def render_circuit_lab(height=790):
    """Render a self-contained breadboard and Arduino circuit construction lab."""
    components.html(_TEMPLATE.replace("__THREE__", _three_scripts()), height=height, scrolling=False)


_TEMPLATE = r"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<style>
*{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#07121d;color:#e8f0f7;font:13px/1.4 Inter,"Segoe UI",system-ui,sans-serif}
#app{height:100%;display:flex;flex-direction:column;border:1px solid #244052;border-radius:14px;overflow:hidden;background:#091824}
#toolbar{display:flex;align-items:center;gap:8px;padding:9px 11px;background:#0d2130;border-bottom:1px solid #234153;flex-wrap:wrap}
#brand{font-weight:800;color:#5ee2ec;margin-right:auto;letter-spacing:.02em}button{font:inherit;color:#eaf3f8;background:#122c3c;border:1px solid #31556a;border-radius:8px;padding:7px 10px;cursor:pointer}button:hover{border-color:#54d7e2;background:#17384a}button.primary{background:#087f8c;border-color:#1ab6c1;font-weight:750}button.danger{border-color:#81494c;color:#ffd3c9}
#layout{display:flex;flex:1;min-height:0}#palette{width:154px;flex:0 0 154px;padding:10px;overflow:auto;border-right:1px solid #234153;background:#0a1a27}#palette h4{margin:0 0 7px;color:#a9c2d1;font-size:11px;text-transform:uppercase;letter-spacing:.1em}#palette button{display:block;width:100%;margin:6px 0;text-align:left;background:#102738}#stage{position:relative;flex:1;min-width:0;min-height:0;cursor:grab}#stage.dragging{cursor:grabbing}#stage canvas{display:block;width:100%;height:100%;touch-action:none}
#overlay{position:absolute;left:10px;top:10px;padding:7px 9px;border-radius:8px;background:rgba(7,18,29,.84);border:1px solid #29485a;color:#c4d5df;font-size:11px;pointer-events:none}#hint{position:absolute;left:10px;right:10px;bottom:10px;min-height:30px;padding:7px 10px;background:rgba(7,18,29,.91);border-left:3px solid #ff9e42;border-radius:7px;color:#d9e7ef;font-size:11px;pointer-events:none}
#status{padding:8px 11px;background:#0c1d2a;border-top:1px solid #234153;color:#aec5d2;font-size:11px;min-height:32px}#status b{color:#5ee2ec}.legend{color:#8aa5b5;font-size:10px;margin-top:10px;line-height:1.5}
@media(max-width:620px){#palette{width:112px;flex-basis:112px;padding:6px}#palette button{padding:6px 5px;font-size:10px}#toolbar{gap:5px;padding:6px}#toolbar button{font-size:10px;padding:6px}#brand{font-size:11px}}
</style>__THREE__</head>
<body><div id="app">
 <div id="toolbar"><span id="brand">IE N5 · 3D CIRCUIT WORKBENCH</span><button id="run" class="primary">▶ Start simulation</button><button id="clearWires">Clear wires</button><button id="reset" class="danger">Reset parts</button></div>
 <div id="layout"><aside id="palette"><h4>Place component</h4>
   <button data-part="led">🔴 LED</button><button data-part="resistor">〰 Resistor</button><button data-part="pushbutton">◉ Pushbutton</button><button data-part="capacitor">▮ Capacitor</button><button data-part="potentiometer">◉ Potentiometer</button><button data-part="transistor">▣ NPN transistor</button>
   <div class="legend"><b>Build and inspect:</b><br>Choose a part to add it. Drag its body onto a breadboard column; double-click to turn it. Click a pin, component lead or hole, then click another one to add a wire. Drag empty board space to orbit; scroll to zoom.<br><br>Holes in the same numbered column, on the same side of the centre trench, share a node. The guided demo checks a D13 → resistor → LED → GND path; it does not yet solve component voltages or run Arduino code.</div>
 </aside><div id="stage"><div id="overlay">Drag blank space to orbit · scroll to zoom · drag parts to place</div><div id="hint">Try: place a resistor and LED across the centre gap. Connect Arduino D13 → resistor → LED → GND, then start the guided simulation.</div></div></div>
 <div id="status"><b>Ready.</b> Add a part, place it across the breadboard centre trench, and wire its leads. This guided demo is not a full SPICE or Arduino-code simulator.</div>
</div>
<script>
(function(){
var tries=0,engineWait=setInterval(function(){if(typeof THREE!=='undefined'){clearInterval(engineWait);start()}else if(++tries>240){clearInterval(engineWait);document.getElementById('status').innerHTML='<b>3D engine unavailable.</b> Check your connection, then reload the workbench.'}},50);
function start(){
var stage=document.getElementById('stage'), status=document.getElementById('status'), hint=document.getElementById('hint');
var scene=new THREE.Scene();scene.background=new THREE.Color('#07121d');
var camera=new THREE.PerspectiveCamera(42,1,.1,120), target=new THREE.Vector3(.25,.15,0), radius=18, yaw=.06, pitch=.58;
function placeCamera(){camera.position.set(target.x+radius*Math.sin(yaw)*Math.cos(pitch),target.y+radius*Math.sin(pitch),target.z+radius*Math.cos(yaw)*Math.cos(pitch));camera.lookAt(target)}placeCamera();
var renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,1.6));renderer.setSize(stage.clientWidth,stage.clientHeight);renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;stage.appendChild(renderer.domElement);
scene.add(new THREE.HemisphereLight(0xe8f7ff,0x1c2936,1.7));var keyLight=new THREE.DirectionalLight(0xffffff,2.2);keyLight.position.set(-5,12,8);keyLight.castShadow=true;scene.add(keyLight);var fill=new THREE.PointLight(0x29d3e2,1.1,35);fill.position.set(4,6,-5);scene.add(fill);
var floor=new THREE.Mesh(new THREE.PlaneGeometry(60,60),new THREE.MeshStandardMaterial({color:'#0b1a27',roughness:.9}));floor.rotation.x=-Math.PI/2;floor.position.y=-.18;floor.receiveShadow=true;scene.add(floor);
var raycaster=new THREE.Raycaster(), pointer=new THREE.Vector2(), clickable=[], holes=[], parts=[], wires=[], selectedEndpoint=null, dragPart=null, dragging=false, rotating=false, dragMoved=false, dragStartX=0, dragStartY=0, lastX=0,lastY=0, simRunning=false, simTimer=null, tick=false, serial=0;
var boardX=-1, boardY=.08, holeSpacing=.29, minCol=1,maxCol=29;
function mat(color,metalness,roughness,extra){return new THREE.MeshStandardMaterial(Object.assign({color:color,metalness:metalness||0,roughness:roughness===undefined ? .55 : roughness},extra||{}))}
function box(parent,name,size,pos,color,material){var m=new THREE.Mesh(new THREE.BoxGeometry(size[0],size[1],size[2]),material||mat(color));m.name=name;m.position.set(pos[0],pos[1],pos[2]);m.castShadow=true;m.receiveShadow=true;parent.add(m);return m}
function label(text,pos,color){var c=document.createElement('canvas'),ctx=c.getContext('2d');c.width=512;c.height=128;ctx.clearRect(0,0,c.width,c.height);ctx.font='bold 50px Segoe UI, sans-serif';ctx.fillStyle=color||'#16364b';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(text,256,64);var tex=new THREE.CanvasTexture(c), sprite=new THREE.Sprite(new THREE.SpriteMaterial({map:tex,transparent:true,depthWrite:false}));sprite.position.set(pos[0],pos[1],pos[2]);sprite.scale.set(2.1,.53,1);scene.add(sprite);return sprite}
function makeBoard(){
 var bb=box(scene,'Breadboard',[9.5,.32,5.25],[boardX,0,0],'#e5e9e9',mat('#e3e8e8',0,.72));
 box(scene,'Breadboard centre trench',[9.52,.03,.28],[boardX,.17,0],'#bbc2c5',mat('#bec6c8',0,.85));
 var railTop=box(scene,'Positive rail',[9.1,.025,.035],[boardX,.18,-2.05],'#dc4b56');var railBottom=box(scene,'Negative rail',[9.1,.025,.035],[boardX,.18,2.05],'#368ec7');
 label('BREADBOARD · CONNECTED GROUPS OF FIVE',[-1,.7,-2.6],'#80a4b4');
 function addHole(x,z,node,labelText){var h=new THREE.Mesh(new THREE.CylinderGeometry(.052,.052,.035,10),mat('#263642',.15,.4));h.rotation.x=0;h.position.set(x,.195,z);h.userData={kind:'node',node:node,label:labelText};scene.add(h);clickable.push(h);holes.push(h);}
 for(var col=minCol;col<=maxCol;col++){
   var x=boardX+(col-15)*holeSpacing;
   for(var row=0;row<5;row++){var za=-1.05+row*.34,zb=.37+row*.34;addHole(x,za,'A'+col,'Breadboard node A'+col);addHole(x,zb,'B'+col,'Breadboard node B'+col)}
   addHole(x,-2.05,'RAIL+','Positive rail');addHole(x,2.05,'RAIL-','Negative rail');
 }
 label('+',[-5.55,.24,-2.05],'#d94750');label('−',[-5.55,.24,2.05],'#3586bc');
}
function makeArduino(){
 var g=new THREE.Group();g.position.set(5.35,.15,0);scene.add(g);
 var pcb=box(g,'Arduino Uno R3 board',[3.35,.28,5.25],[0,0,0],'#1673aa',mat('#1377ae',.25,.48));
 box(g,'Microcontroller',[1.05,.18,1.05],[-.15,.22,.2],'#101a24',mat('#121920',.3,.45));
 box(g,'USB socket',[1.15,.38,.62],[0,.31,-2.64],'#b8c4c9',mat('#aab8c0',.72,.3));
 box(g,'Power jack',[.62,.44,.7],[-1.43,.34,2.23],'#20252b',mat('#20252b',.35,.45));
 label('ARDUINO UNO R3',[5.35,.78,.1],'#d8f1ff');
 function pin(x,z,name,node,color){var p=new THREE.Mesh(new THREE.CylinderGeometry(.09,.09,.22,12),mat(color||'#f0c86a',.5,.35));p.position.set(x,.36,z);p.userData={kind:'pin',node:node,label:name};g.add(p);clickable.push(p);label(name,[5.35+x,.73,z], '#c5e8f2');}
 pin(1.62,-1.85,'D13','D13','#f1ca6b');pin(-1.62,1.72,'5V','5V','#e76c61');pin(-1.62,2.05,'GND','GND','#69a9e0');pin(-1.62,1.38,'GND 2','GND','#69a9e0');
 for(var i=0;i<14;i++){var z=-1.85+i*.24;var d=new THREE.Mesh(new THREE.CylinderGeometry(.055,.055,.12,8),mat('#d7b45d',.35,.45));d.position.set(1.62,.26,z);g.add(d)}
 for(var j=0;j<10;j++){var z2=-1.25+j*.24;var d2=new THREE.Mesh(new THREE.CylinderGeometry(.055,.055,.12,8),mat('#d7b45d',.35,.45));d2.position.set(-1.62,.26,z2);g.add(d2)}
}
makeBoard();makeArduino();
function nodeAt(x,z){if(Math.abs(z)>1.72)return z<0?'RAIL+':'RAIL-';var col=Math.max(minCol,Math.min(maxCol,Math.round((x-boardX)/holeSpacing+15)));return (z<0?'A':'B')+col}
function terminalWorld(part,index){var p=part.userData.terminals[index];var v=new THREE.Vector3(p[0],p[1],p[2]);part.localToWorld(v);return v}
function addPinVisual(part,p){var pin=new THREE.Mesh(new THREE.CylinderGeometry(.045,.045,.38,8),mat('#b9c3c8',.45,.36));pin.position.set(p[0],p[1],p[2]);part.add(pin)}
function buildPart(type){serial++;var g=new THREE.Group(), baseX=boardX-3.5+((parts.length%6)*1.25), baseZ=(Math.floor(parts.length/6)%2?1.2:-1.2);g.position.set(baseX,.15,baseZ);g.userData={kind:'part',partType:type,serial:serial,pressed:false};var body,labelText;
 if(type==='led'){
   body=new THREE.Mesh(new THREE.SphereGeometry(.25,20,14),mat('#e94b4b',.08,.25,{emissive:'#300505',emissiveIntensity:.22}));body.position.set(0,.62,0);g.add(body);body.userData={kind:'body',owner:g};
   var cap=new THREE.Mesh(new THREE.CylinderGeometry(.21,.18,.15,20),mat('#9d2028',.2,.3));cap.position.set(0,.42,0);g.add(cap);cap.userData={kind:'body',owner:g};
   labelText='LED';g.userData.terminals=[[0,.29,-.62],[0,.29,.62]];
 }else if(type==='resistor'){
   body=box(g,'Resistor body',[.33,.3,.62],[0,.45,0],'#c68c50',mat('#c68c50',.12,.45));body.userData={kind:'body',owner:g};
   for(var b=0;b<3;b++){var band=box(g,'Resistor band',[.35,.31,.055],[0,.45,-.18+b*.18],b===1?'#65442a':'#e7d2aa');band.userData={kind:'body',owner:g}}
   labelText='RESISTOR';g.userData.terminals=[[0,.3,-.68],[0,.3,.68]];
 }else if(type==='pushbutton'){
   body=box(g,'Pushbutton',[.78,.32,.78],[0,.49,0],'#202a32',mat('#202a32',.3,.34));body.userData={kind:'body',owner:g};
   var cap=box(g,'Button cap',[.45,.22,.45],[0,.75,0],'#d64c4c');cap.userData={kind:'body',owner:g};
   labelText='PUSH BUTTON';g.userData.terminals=[[0,.28,-.65],[0,.28,.65]];
 }else if(type==='capacitor'){
   body=new THREE.Mesh(new THREE.CylinderGeometry(.28,.28,.58,20),mat('#278da0',.25,.35));body.position.set(0,.57,0);g.add(body);body.userData={kind:'body',owner:g};
   labelText='CAPACITOR';g.userData.terminals=[[0,.28,-.62],[0,.28,.62]];
 }else if(type==='potentiometer'){
   body=new THREE.Mesh(new THREE.CylinderGeometry(.38,.38,.23,24),mat('#273c4b',.2,.44));body.position.set(0,.55,0);g.add(body);body.userData={kind:'body',owner:g};
   var knob=new THREE.Mesh(new THREE.CylinderGeometry(.18,.18,.25,20),mat('#84bac2',.25,.3));knob.position.set(0,.78,0);g.add(knob);knob.userData={kind:'body',owner:g};
   labelText='POT';g.userData.terminals=[[-.35,.28,-.58],[0,.28,.62],[.35,.28,-.58]];
 }else{
   body=box(g,'NPN transistor',[.7,.46,.25],[0,.58,0],'#242b32',mat('#242b32',.3,.4));body.userData={kind:'body',owner:g};
   labelText='NPN';g.userData.terminals=[[-.25,.28,.5],[0,.28,.5],[.25,.28,.5]];
 }
 clickable.push(body);
 g.userData.label=labelText;
 g.userData.terminals.forEach(function(p,i){addPinVisual(g,p);var t=new THREE.Mesh(new THREE.SphereGeometry(.09,12,10),mat('#f4c56a',.38,.3));t.position.set(p[0],p[1],p[2]);t.userData={kind:'terminal',owner:g,index:i};g.add(t);clickable.push(t)});
 var lbl=label(labelText,[baseX,.92,baseZ],type==='led'?'#ff9797':'#c7e8ef');g.userData.labelSprite=lbl;parts.push(g);return g;
}
document.querySelectorAll('[data-part]').forEach(function(btn){btn.addEventListener('click',function(){var p=buildPart(btn.dataset.part);status.innerHTML='<b>'+p.userData.label+' placed.</b> Drag it onto a breadboard column, then wire its terminals.'})});
function endpointFor(obj){var d=obj.userData;if(d.kind==='terminal'){var part=d.owner,w=terminalWorld(part,d.index);return{node:nodeAt(w.x,w.z),pos:w.clone(),label:part.userData.label+' lead '+(d.index+1)}}return{node:d.node,pos:obj.getWorldPosition(new THREE.Vector3()),label:d.label}}
function drawWire(a,b){var start=a.pos.clone(),end=b.pos.clone(),height=Math.max(start.y,end.y)+.65;var points=[start,new THREE.Vector3(start.x,height,start.z),new THREE.Vector3(end.x,height,end.z),end];var curve=new THREE.CatmullRomCurve3(points);var color=(a.node==='GND'||a.node==='RAIL-'||b.node==='GND'||b.node==='RAIL-')?'#5ab3e3':(wires.length%2?'#eb5c58':'#edb644');var mesh=new THREE.Mesh(new THREE.TubeGeometry(curve,24,.045,7,false),mat(color,.2,.32,{emissive:color,emissiveIntensity:.12}));mesh.userData={kind:'wire'};scene.add(mesh);wires.push({mesh:mesh,a:a,b:b});}
function handleEndpoint(obj){var ep=endpointFor(obj);if(!selectedEndpoint){selectedEndpoint=ep;obj.material&&obj.material.emissive&&obj.material.emissive.set('#d48922');status.innerHTML='<b>Wire start:</b> '+ep.label+' ('+ep.node+'). Click the destination terminal.';return}if(selectedEndpoint.node===ep.node){status.innerHTML='<b>Same breadboard node.</b> Choose a different terminal or hole.';selectedEndpoint=null;return}drawWire(selectedEndpoint,ep);status.innerHTML='<b>Wire added.</b> '+selectedEndpoint.node+' ↔ '+ep.node+'.';selectedEndpoint=null;updateSimulation();}
function getHit(event){var r=renderer.domElement.getBoundingClientRect();pointer.x=((event.clientX-r.left)/r.width)*2-1;pointer.y=-((event.clientY-r.top)/r.height)*2+1;raycaster.setFromCamera(pointer,camera);return raycaster.intersectObjects(clickable,true)}
function intersectPlane(event){var r=renderer.domElement.getBoundingClientRect();pointer.x=((event.clientX-r.left)/r.width)*2-1;pointer.y=-((event.clientY-r.top)/r.height)*2+1;raycaster.setFromCamera(pointer,camera);var plane=new THREE.Plane(new THREE.Vector3(0,1,0),-.15),p=new THREE.Vector3();return raycaster.ray.intersectPlane(plane,p)?p:null}
renderer.domElement.addEventListener('pointerdown',function(e){lastX=e.clientX;lastY=e.clientY;var hits=getHit(e),hit=hits.find(function(h){return h.object.userData.kind});if(hit){var d=hit.object.userData;if(d.kind==='terminal'||d.kind==='node'||d.kind==='pin'){handleEndpoint(hit.object);return}if(d.kind==='body'&&d.owner){dragPart=d.owner;dragging=true;dragMoved=false;dragStartX=e.clientX;dragStartY=e.clientY;stage.classList.add('dragging');renderer.domElement.setPointerCapture(e.pointerId);return}}
 rotating=true;renderer.domElement.setPointerCapture(e.pointerId);});
renderer.domElement.addEventListener('pointermove',function(e){if(dragging&&dragPart){if(Math.hypot(e.clientX-dragStartX,e.clientY-dragStartY)>4)dragMoved=true;var p=intersectPlane(e);if(p){var col=Math.round((p.x-boardX)/holeSpacing+15);dragPart.position.x=boardX+(Math.max(2,Math.min(28,col))-15)*holeSpacing;dragPart.position.z=0;dragPart.userData.labelSprite.position.set(dragPart.position.x,1.0,0);updateSimulation()}return}if(rotating){var dx=e.clientX-lastX,dy=e.clientY-lastY;yaw-=dx*.008;pitch=Math.max(.18,Math.min(1.18,pitch+dy*.006));placeCamera()}lastX=e.clientX;lastY=e.clientY;});
renderer.domElement.addEventListener('pointerup',function(){if(dragPart&&!dragMoved&&dragPart.userData.partType==='pushbutton'){dragPart.userData.pressed=!dragPart.userData.pressed;status.innerHTML='<b>Pushbutton '+(dragPart.userData.pressed?'closed':'open')+'.</b> Click it again to change its state.';updateSimulation()}dragging=false;dragPart=null;rotating=false;stage.classList.remove('dragging')});
renderer.domElement.addEventListener('pointercancel',function(){dragging=false;dragPart=null;rotating=false;stage.classList.remove('dragging')});
renderer.domElement.addEventListener('wheel',function(e){e.preventDefault();radius=Math.max(10,Math.min(27,radius+e.deltaY*.012));placeCamera()},{passive:false});
renderer.domElement.addEventListener('dblclick',function(e){var hit=getHit(e).find(function(h){return h.object.userData.kind==='body'});if(hit&&hit.object.userData.owner){hit.object.userData.owner.rotation.y+=Math.PI/2;status.innerHTML='<b>Part rotated.</b> Double-click the body again to rotate it another 90°.';updateSimulation()}});
function reachablePath(){var adj={};function link(a,b,type){(adj[a]||(adj[a]=[])).push({to:b,type:type});(adj[b]||(adj[b]=[])).push({to:a,type:type})}wires.forEach(function(w){link(w.a.node,w.b.node,'wire')});parts.forEach(function(p){var ts=p.userData.terminals||[];for(var i=0;i<ts.length-1;i++){var a=terminalWorld(p,i),b=terminalWorld(p,i+1),type=p.userData.partType;if(type==='pushbutton'&&!p.userData.pressed)continue;link(nodeAt(a.x,a.z),nodeAt(b.x,b.z),type)}});
 var q=[{n:'D13',led:false,res:false}],seen={};while(q.length){var cur=q.shift(),key=cur.n+'|'+cur.led+'|'+cur.res;if(seen[key])continue;seen[key]=1;if(cur.n==='GND'&&cur.led&&cur.res)return true;(adj[cur.n]||[]).forEach(function(edge){q.push({n:edge.to,led:cur.led||edge.type==='led',res:cur.res||edge.type==='resistor'})})}return false}
function updateSimulation(){var complete=reachablePath();parts.forEach(function(p){if(p.userData.partType==='led'){var isOn=simRunning&&tick&&complete;p.children.forEach(function(ch){if(ch.material&&ch.material.emissive){ch.material.emissive.set(isOn?'#ff1f20':'#300505');ch.material.emissiveIntensity=isOn?1.8:.22}})}});if(simRunning){status.innerHTML=complete?'<b>Simulation running.</b> D13 output is pulsing; the LED lights when the output is HIGH.':'<b>Simulation running.</b> No complete D13 → resistor → LED → GND path detected yet.'}else if(complete){status.innerHTML='<b>Path detected.</b> Start simulation to pulse D13 and light the LED.'}}
document.getElementById('run').addEventListener('click',function(){simRunning=!simRunning;this.textContent=simRunning?'■ Stop simulation':'▶ Start simulation';if(simTimer)clearInterval(simTimer);if(simRunning){tick=false;simTimer=setInterval(function(){tick=!tick;updateSimulation()},650)}else{tick=false;updateSimulation()} });
document.getElementById('clearWires').addEventListener('click',function(){wires.forEach(function(w){scene.remove(w.mesh);w.mesh.geometry.dispose();w.mesh.material.dispose()});wires=[];selectedEndpoint=null;updateSimulation();status.innerHTML='<b>Wires cleared.</b> Click one terminal, then another to reconnect.'});
document.getElementById('reset').addEventListener('click',function(){simRunning=false;tick=false;if(simTimer)clearInterval(simTimer);simTimer=null;document.getElementById('run').textContent='▶ Start simulation';parts.forEach(function(p){scene.remove(p);if(p.userData.labelSprite)scene.remove(p.userData.labelSprite);p.traverse(function(o){var i=clickable.indexOf(o);if(i>=0)clickable.splice(i,1);if(o.geometry)o.geometry.dispose();if(o.material){if(Array.isArray(o.material))o.material.forEach(function(m){m.dispose()});else o.material.dispose()}})});parts=[];document.getElementById('clearWires').click();status.innerHTML='<b>Workbench reset.</b> Add components from the palette to begin.'});
function resize(){var w=stage.clientWidth,h=stage.clientHeight;if(!w||!h)return;camera.aspect=w/h;camera.updateProjectionMatrix();renderer.setSize(w,h)}new ResizeObserver(resize).observe(stage);
function animate(){requestAnimationFrame(animate);renderer.render(scene,camera)}animate();
}
})();
</script></body></html>"""

