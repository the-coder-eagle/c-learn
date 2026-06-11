// ============================================================
// C Learn — app.js (v4.1 modular orchestrator)
// Mode switching, sidebar, onboarding, shortcuts, startup
// Depends on: utils.js → editor.js → course.js → viz.js
// ============================================================

// ── Global state ──────────────────────────────────
window._mode="learn";
window._curMod=null;window._curEx=null;
window._globalSize=14;window._codeSize=14;
window._modules=[];window._exercises=[];window._progress={};
window._sidebarCollapsed=false;window._isRunning=false;
window._exCurrentFilter="all";window._exSearchTerm="";

// ── Sidebar toggle ────────────────────────────────
function toggleSidebar(){
  window._sidebarCollapsed=!window._sidebarCollapsed;
  var sb=$("#sidebar"),g1=$("#grip1"),btn=$("#btn-sidebar");
  if(window._sidebarCollapsed){sb.classList.add('collapsed');g1.classList.add('collapsed');btn.textContent='☰'}
  else{sb.classList.remove('collapsed');g1.classList.remove('collapsed');btn.textContent='✕';sb.style.width=(parseInt(localStorage.getItem('c-sidebar'))||220)+'px';sb.style.flex='none'}
  localStorage.setItem('c-sidebar-collapsed',window._sidebarCollapsed?'1':'0');
}
$("#btn-sidebar").onclick=toggleSidebar;
document.addEventListener("keydown",e=>{if((e.ctrlKey||e.metaKey)&&e.key==="b"){e.preventDefault();toggleSidebar()}});

// ── Drag system ───────────────────────────────────
(function(){
  var sw=parseInt(localStorage.getItem('c-sidebar'))||220;
  var rw=parseInt(localStorage.getItem('c-right'))||400;
  $("#sidebar").style.cssText='width:'+sw+'px;flex:none';
  $("#center").style.cssText='flex:1;min-width:200px';
  $("#right").style.cssText='width:'+rw+'px;flex:none;min-width:320px';
  if(localStorage.getItem('c-sidebar-collapsed')==='1'){window._sidebarCollapsed=true;$("#sidebar").classList.add('collapsed');$("#grip1").classList.add('collapsed');$("#btn-sidebar").textContent='☰'}
  var outH=parseInt(localStorage.getItem('c-out-h'))||200;
  if(outH!==200){$("#output-pane").style.height=outH+'px';$("#output-pane").style.flex='none'}

  var drag=null;
  document.addEventListener('mousedown',function(e){
    var grip=e.target.closest('.grip,.grip-v');
    if(!grip||grip.classList.contains('collapsed'))return;
    if(grip.id==='grip1'&&window._sidebarCollapsed)return;
    e.preventDefault();
    var isV=grip.classList.contains('grip-v');
    var left=document.getElementById(grip.dataset.left)||grip.previousElementSibling;
    var right=document.getElementById(grip.dataset.right)||grip.nextElementSibling;
    if(!left||!right)return;
    var prop=isV?'height':'width';
    drag={grip:grip,left:left,right:right,startPos:isV?e.clientY:e.clientX,startLeft:left.getBoundingClientRect()[prop],isV:isV,prop:prop};
    grip.classList.add('on');document.body.style.cursor=isV?'row-resize':'col-resize';document.body.style.userSelect='none';
  });
  document.addEventListener('mousemove',function(e){
    if(!drag)return;
    var delta=(drag.isV?e.clientY:e.clientX)-drag.startPos;
    drag.left.style[drag.prop]=Math.max(drag.isV?60:100,drag.startLeft+delta)+'px';
    drag.left.style.flex='none';drag.right.style.flex='1';
  });
  document.addEventListener('mouseup',function(){
    if(!drag)return;
    drag.grip.classList.remove('on');document.body.style.cursor='';document.body.style.userSelect='';
    var key=drag.grip.id==='grip1'?'c-sidebar':drag.grip.id==='grip2'?'c-center':drag.grip.id==='grip-out'?'c-out-h':'';
    if(key)localStorage.setItem(key,parseInt(drag.left.style[drag.prop]));
    if(drag.grip.id==='grip2')localStorage.setItem('c-right',parseInt(drag.right.style[drag.prop]||drag.right.getBoundingClientRect()[drag.prop]));
    drag=null;
  });
})();

// ── Font size controls ────────────────────────────
$("#font-up").onclick=()=>setGlobalSize(Math.min(20,(window._globalSize||14)+1));
$("#font-dn").onclick=()=>setGlobalSize(Math.max(10,(window._globalSize||14)-1));
$("#code-up").onclick=()=>setCodeSize(Math.min(22,(window._codeSize||14)+1));
$("#code-dn").onclick=()=>setCodeSize(Math.max(10,(window._codeSize||14)-1));
$("#code-up2").onclick=()=>setCodeSize(Math.min(22,(window._codeSize||14)+1));
$("#code-dn2").onclick=()=>setCodeSize(Math.max(10,(window._codeSize||14)-1));

// ── Theme ─────────────────────────────────────────
$("#btn-light").onclick=()=>applyLightMode(!document.body.classList.contains('light'));

// ── Mode switching ────────────────────────────────
$$("#topbar .modes button").forEach(b=>b.onclick=()=>{
  if(b.classList.contains("on"))return;
  $$("#topbar .modes button").forEach(x=>x.classList.remove("on"));
  b.classList.add("on");window._mode=b.dataset.mode;
  if(window._mode==="visualize"){window._curMod=null;window._curEx=null;$("#viz-code").textContent=EXAMPLES_CODE.pointer_basics;showVizPanel();vizLoadCode(EXAMPLES_CODE.pointer_basics);return}
  window._hideVizPanel();clr();dot('','');
  $("#btn-submit").style.display=(window._mode==="practice")?"":"none";
  $("#btn-reset").style.display=(window._mode==="practice")?"":"none";
  if(window._mode==="free"){window._showFreeMode();return}
  if(window._mode==="learn"){window._curMod=null;window._curEx=null;buildCourseTree();showWelcome()}
  else{window._curMod=null;window._curEx=null;buildExerciseList();showWelcome()}
});

// ── Onboarding ────────────────────────────────────
let obStep=0;const obTotal=4;

function showOnboarding(){
  if(localStorage.getItem('c-onboarded'))return;
  obStep=0;$("#onboard-overlay").classList.add('on');renderObStep();
}
function hideOnboarding(){$("#onboard-overlay").classList.remove('on');localStorage.setItem('c-onboarded','1')}
function renderObStep(){
  for(let i=0;i<obTotal;i++)$("#ob-step-"+i).style.display=i===obStep?'':'none';
  $("#ob-prev").style.visibility=obStep===0?'hidden':'';
  $("#ob-next").style.display=obStep===obTotal-1?'none':'';$("#ob-done").style.display=obStep===obTotal-1?'':'none';
  let dots='';for(let i=0;i<obTotal;i++)dots+='<span class="dot'+(i===obStep?' on':'')+'"></span>';$("#ob-dots").innerHTML=dots;
  if(obStep===0){
    const d=window._exercises.filter(e=>e.status==="passed").length,t=window._exercises.length,p=Math.round(d/t*100)||0;
    $("#ob-stats").innerHTML='<div class="os"><div class="n">'+window._modules.length+'</div><div class="l">课时</div></div><div class="os"><div class="n">'+t+'</div><div class="l">练习题</div></div><div class="os"><div class="n">'+p+'%</div><div class="l">完成率</div></div>';
  }
}
$("#ob-prev").onclick=()=>{if(obStep>0){obStep--;renderObStep()}};
$("#ob-next").onclick=()=>{if(obStep<obTotal-1){obStep++;renderObStep()}};
$("#ob-done").onclick=()=>hideOnboarding();
$("#btn-help").onclick=()=>{obStep=0;renderObStep();$("#onboard-overlay").classList.add('on')};

// ── Shortcut panel ────────────────────────────────
function toggleShortcuts(){$("#shortcut-overlay").classList.toggle('on')}
$("#shortcut-close").onclick=toggleShortcuts;
$("#shortcut-overlay").addEventListener('click',function(e){if(e.target===this)toggleShortcuts()});

// ── Keyboard shortcuts ────────────────────────────
document.addEventListener("keydown",e=>{
  if((e.ctrlKey||e.metaKey)&&e.key==="Enter"){e.preventDefault();if(!window._isRunning)(window._mode==="practice"&&window._curEx?$("#btn-submit"):$("#btn-run")).click()}
  if((e.ctrlKey||e.metaKey)&&e.key==="k"){e.preventDefault();toggleShortcuts()}
  if((e.ctrlKey||e.metaKey)&&e.key==="s"){e.preventDefault();$("#btn-fmt").click()}
  if(e.key==="Escape"){if($("#shortcut-overlay").classList.contains('on'))toggleShortcuts()}
});

// ── Restore preferences ───────────────────────────
const gs=parseInt(localStorage.getItem('c-gs'));if(gs)setGlobalSize(gs);
const cs=parseInt(localStorage.getItem('c-cs'));if(cs)setCodeSize(cs);
const ac=localStorage.getItem('c-ac');if(ac)window.setAccent(ac);
initSystemTheme();
if(localStorage.getItem('c-lt')==='1')applyLightMode(true);

// ── Startup ───────────────────────────────────────
(async()=>{
  await _loadData();
  buildCourseTree();
  showWelcome();
  setTimeout(showOnboarding,600);
  setTimeout(checkAchievements,1200);
})();
