"""Bundled feature-anchored tour overlay, rendered in the app's own document."""

import json
from pathlib import Path
import streamlit as st

_VENDOR = Path(__file__).parent / "vendor" / "driver"
_STYLE = (_VENDOR / "driver.css").read_text(encoding="utf-8") + """
.trentox-tour.driver-popover{background:#132034;color:#edf5fb;border:1px solid #35505f;border-radius:16px;
font-family:system-ui,sans-serif;max-width:min(360px,calc(100vw - 24px));max-height:calc(100vh - 28px);overflow:auto;}
.trentox-tour .driver-popover-title{font-size:18px;line-height:1.35;padding-right:24px;}
.trentox-tour .driver-popover-description{font-size:13px;line-height:1.65;color:#d2deeb;}
.trentox-tour .tour-tip{border-left:2px solid #6ee7dd;padding-left:10px;margin-top:12px;}
.trentox-tour .driver-popover-close-btn{color:#d2deeb;}
.trentox-tour .driver-popover-footer{flex-wrap:wrap;gap:10px;}
.trentox-tour .driver-popover-progress-text{color:#9fb3c8;font-size:11px;}
.trentox-tour .driver-popover-footer-buttons{display:flex;gap:7px;}
.trentox-tour .driver-popover-footer button{background:#20354b;color:#eef6fb;text-shadow:none;border:1px solid #405c73;
border-radius:9px;padding:9px 12px;min-height:38px;font-size:12px;}
.trentox-tour .driver-popover-footer button:last-child{background:#6ee7dd;color:#082e31;border-color:#6ee7dd;}
.trentox-tour button:disabled{opacity:.4;cursor:default;}
.trentox-tour button:focus-visible,.trentox-tour select:focus-visible{outline:2px solid #6ee7dd;outline-offset:3px;}
.trentox-tour .tour-jump{display:block;margin:12px 0 6px;font-size:11px;color:#b7c8d9;}
.trentox-tour select{display:block;width:100%;margin-top:5px;background:#0b1626;color:#edf5fb;border:1px solid #405c73;
padding:8px;border-radius:8px;font-size:12px;}
@media(prefers-reduced-motion:reduce){.driver-overlay,.driver-popover{animation:none!important;transition:none!important;}}
"""

_CONTROLLER = r"""
const guideInstances = new WeakMap();
function visible(el) {if(!el)return false;const r=el.getBoundingClientRect();return r.width>0&&r.height>0&&getComputedStyle(el).visibility!=='hidden';}
function findTarget(step) {
  const nodes=(selector)=>Array.from(document.querySelectorAll(selector)).filter(visible);
  if(step.kind==='testid')return nodes('[data-testid="'+step.target+'"]')[0];
  if(step.kind==='key')return nodes('.st-key-'+CSS.escape(step.target))[0];
  if(step.kind==='key_prefix')return nodes('[class*="st-key-"]').find(el=>Array.from(el.classList).some(c=>c.startsWith('st-key-'+step.target)));
  if(step.kind==='button')return nodes('button').find(el=>el.textContent.trim()===step.target);
  if(step.kind==='expander')return nodes('summary').find(el=>el.textContent.includes(step.target))?.closest('details');
  const label=nodes('label,[data-testid="stWidgetLabel"]').find(el=>el.textContent.trim()===step.target);
  return label?.closest('[data-testid="stSelectbox"],[data-testid="stSlider"],[data-testid="stTextInput"],[data-testid="stFileUploader"]')||label;
}
function esc(value){return String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
export default function({parentElement,data,setTriggerValue}) {
  let s=guideInstances.get(parentElement);
  if(!s){s={version:0,driver:null,disposed:false,token:null};guideInstances.set(parentElement,s);}
  const cleanup=()=>{s.disposed=true;s.version++;s.driver?.destroy();if(s.escape)document.removeEventListener('keydown',s.escape,true);guideInstances.delete(parentElement);};
  if(s.token===data.token)return cleanup;
  s.token=data.token;s.version++;s.changing=false;s.driver?.destroy();const version=s.version;
  if(!document.getElementById('trentox-tour-styles')){const style=document.createElement('style');style.id='trentox-tour-styles';style.textContent=TOUR_CSS;document.head.appendChild(style);}
  const send=(kind,target)=>{if(s.changing||s.disposed)return;s.changing=true;s.driver?.destroy();
    setTriggerValue('action',{id:crypto.randomUUID(),step:data.step.id,kind,target});};
  if(s.escape)document.removeEventListener('keydown',s.escape,true);
  s.escape=event=>{if(event.key==='Escape'){event.preventDefault();send('stop');}};
  document.addEventListener('keydown',s.escape,true);
  if(data.step.id==='voice'){
    const summary=Array.from(document.querySelectorAll('summary')).find(el=>el.textContent.includes('ElevenLabs voice'));
    if(summary&&!summary.closest('details')?.open)summary.click();
  }
  if(data.step.sidebar){const side=document.querySelector('[data-testid="stSidebar"]');
    if(!visible(side)||side.getBoundingClientRect().right<=0){
      const open=document.querySelector('[data-testid="stSidebarCollapsedControl"] button')||document.querySelector('button[aria-label="Expand sidebar"]');open?.click();}}
  const started=performance.now();
  const draw=()=>{
    if(s.disposed||version!==s.version)return;
    const target=findTarget(data.step);
    if(!target&&performance.now()-started<8000){requestAnimationFrame(draw);return;}
    const description='<p>'+esc(data.step.body)+'</p><p class="tour-tip">'+esc(data.step.tip)+'</p>'+
      (!target?'<p>The specific control is not visible in this view. You can use Next to continue or replay this step from the feature list.</p>':'');
    s.driver=makeTour({animate:!matchMedia('(prefers-reduced-motion: reduce)').matches,overlayOpacity:0.42,
      overlayClickBehavior:'none',allowClose:true,allowKeyboardControl:false,stagePadding:8,stageRadius:12,
      allowedElements:'[data-baseweb="popover"]',showProgress:true,progressText:'Step '+data.number+' of '+data.total,
      popoverClass:'trentox-tour',showButtons:['close'],onCloseClick:()=>send('stop'),onDestroyStarted:()=>send('stop'),
      onPopoverRender:(popover)=>{
        const label=document.createElement('label');label.className='tour-jump';label.textContent='Jump to a feature';
        const select=document.createElement('select');select.setAttribute('aria-label','Jump to a guide feature');
        for(const item of data.items){const option=document.createElement('option');option.value=item.id;option.textContent=item.title;option.selected=item.id===data.step.id;select.appendChild(option);}
        select.onchange=()=>send('jump',select.value);label.appendChild(select);popover.description.appendChild(label);
        popover.footer.style.display='flex';popover.footerButtons.replaceChildren();
        for(const [kind,text,disabled] of [['back','Back',data.number===1],['stop','Skip guide',false],['next',data.number===data.total?'Finish guide':'Next',false]]){
          const button=document.createElement('button');button.type='button';button.textContent=text;button.disabled=disabled;
          button.onclick=()=>send(kind);popover.footerButtons.appendChild(button);}
        popover.wrapper.setAttribute('aria-label','App guide: '+data.step.title);
      }});
    s.driver.highlight({element:target,popover:{title:esc(data.step.title),description,side:data.step.sidebar?'right':'bottom',align:'center'}});
  };
  requestAnimationFrame(draw);
  return cleanup;
}
"""

_JS = "const vendorScope = {};\n(function(){\n" + (_VENDOR / "driver.js.iife.js").read_text(encoding="utf-8") + (
    "\n}).call(vendorScope);\nconst makeTour = vendorScope.driver.js.driver;\nconst TOUR_CSS = "
    + json.dumps(_STYLE) + ";\n" + _CONTROLLER
)
_TOUR = st.components.v2.component("trentox_feature_guide", html="<span aria-hidden='true'></span>", js=_JS)


def render_overlay(data):
    return _TOUR(data=data, key="first_use_feature_overlay", on_action_change=lambda: None, height=0)
