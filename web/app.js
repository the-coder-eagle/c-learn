// ============================================================
// C Learn v11 — 语法高亮 + 新手引导 + 进度仪表盘
// 纯本地 JS · 零外部依赖
// ============================================================
const $=s=>document.querySelector(s),$$=s=>document.querySelectorAll(s);
const API="http://127.0.0.1:8765";
let mode="learn",curMod=null,curEx=null,globalSize=14,codeSize=14;
let modules=[],exercises=[],progress={};
let sidebarCollapsed=false,isRunning=false,exCurrentFilter="all",exSearchTerm="";
const DEFAULT_CODE='#include <stdio.h>\n\nint main() {\n    printf("Hello!\\n");\n    return 0;\n}\n';

// ═══════════════════ EDITOR ═══════════════════
const codeInput=$("#code-input"),gutter=$("#gutter"),hlCode=$("#hl-code");
codeInput.value=DEFAULT_CODE;

function updateGutter(){
  const n=codeInput.value.split('\n').length;
  gutter.innerHTML=Array.from({length:n},(_,i)=>i+1).join('\n');
}

// ── Syntax Highlighting ──────────────────────
const C_KEYWORDS=new Set([
  'auto','break','case','const','continue','default','do','else','enum',
  'extern','for','goto','if','register','return','signed','sizeof','static',
  'struct','switch','typedef','union','unsigned','volatile','while'
]);
const C_TYPES=new Set([
  'int','char','float','double','void','short','long','size_t','FILE',
  'uint8_t','int8_t','uint16_t','int16_t','uint32_t','int32_t','uint64_t','int64_t'
]);

function tokenizeLine(line){
  const tokens=[];
  let i=0;
  while(i<line.length){
    // String literals
    if(line[i]==='"'||line[i]==="'"){
      const q=line[i];let j=i+1;
      while(j<line.length&&line[j]!==q){
        if(line[j]==='\\')j++;
        j++;
      }
      tokens.push({s:i,e:Math.min(j+1,line.length),c:'hl-str'});
      i=j+1;continue;
    }
    // Preprocessor
    if(line[i]==='#'&&(i===0||/^\s*$/.test(line.slice(0,i)))){
      tokens.push({s:i,e:line.length,c:'hl-pp'});
      break;
    }
    // Single-line comment
    if(line[i]==='/'&&line[i+1]==='/'){
      tokens.push({s:i,e:line.length,c:'hl-cmt'});
      break;
    }
    // Numbers
    if(/\d/.test(line[i])&&(i===0||!/[a-zA-Z_]/.test(line[i-1]))){
      let j=i;
      while(j<line.length&&/[0-9a-fA-FxX.]/.test(line[j]))j++;
      tokens.push({s:i,e:j,c:'hl-num'});
      i=j;continue;
    }
    // Identifiers
    if(/[a-zA-Z_]/.test(line[i])){
      let j=i;
      while(j<line.length&&/[a-zA-Z0-9_]/.test(line[j]))j++;
      const w=line.slice(i,j);
      if(C_KEYWORDS.has(w))tokens.push({s:i,e:j,c:'hl-kw'});
      else if(C_TYPES.has(w))tokens.push({s:i,e:j,c:'hl-type'});
      else if(line.slice(j).trimStart().startsWith('('))tokens.push({s:i,e:j,c:'hl-fn'});
      i=j;continue;
    }
    // Operators
    if('+-*/%=<>!&|^~?:.'.includes(line[i])){
      tokens.push({s:i,e:i+1,c:'hl-op'});
      i++;continue;
    }
    i++;
  }
  return tokens;
}

function highlight(){
  const lines=codeInput.value.split('\n');
  let html='';
  for(let i=0;i<lines.length;i++){
    const tokens=tokenizeLine(lines[i]);
    if(!tokens.length){html+=esc(lines[i])+'\n';continue;}
    let last=0,lineHtml='';
    for(const t of tokens){
      if(t.s>last)lineHtml+=esc(lines[i].slice(last,t.s));
      lineHtml+='<span class="'+t.c+'">'+esc(lines[i].slice(t.s,t.e))+'</span>';
      last=t.e;
    }
    if(last<lines[i].length)lineHtml+=esc(lines[i].slice(last));
    html+=lineHtml+'\n';
  }
  hlCode.innerHTML=html;
}

function syncEditorScroll(){
  const pre=$("#highlight-layer");
  pre.scrollTop=codeInput.scrollTop;
  pre.scrollLeft=codeInput.scrollLeft;
}

codeInput.addEventListener('scroll',syncEditorScroll);
codeInput.addEventListener('input',()=>{updateGutter();highlight()});
codeInput.addEventListener('keydown',e=>{
  if(e.key==='Tab'){e.preventDefault();const s=codeInput.selectionStart;codeInput.value=codeInput.value.slice(0,s)+'    '+codeInput.value.slice(s);codeInput.selectionStart=codeInput.selectionEnd=s+4;highlight();updateGutter()}
});
updateGutter();highlight();

// stdin scanf detection (visual hint only)
codeInput.addEventListener('input',function(){
  var v=codeInput.value;
  var has=/scanf/.test(v)||/gets/.test(v)||/fgets/.test(v)||/getchar/.test(v);
  if(has&&!isRunning)codeInput.style.borderBottom='2px solid var(--amber)';
  else codeInput.style.borderBottom='';
});

function getCode(){return codeInput.value}
function setCode(c){codeInput.value=c;updateGutter();highlight()}

// ═══════════════════ FONT SIZE ═══════════════════
function setGlobalSize(sz){
  globalSize=sz;document.documentElement.style.setProperty('--global-size',sz+'px');
  $("#font-lbl").textContent=sz+'px';localStorage.setItem('c-gs',sz);
}
$("#font-up").onclick=()=>setGlobalSize(Math.min(20,globalSize+1));
$("#font-dn").onclick=()=>setGlobalSize(Math.max(10,globalSize-1));
function setCodeSize(sz){
  codeSize=sz;document.documentElement.style.setProperty('--editor-size',sz+'px');
  $("#code-lbl").textContent=sz+'px';$("#code-lbl2").textContent=sz+'px';
  localStorage.setItem('c-cs',sz);
}
$("#code-up").onclick=()=>setCodeSize(Math.min(22,codeSize+1));
$("#code-dn").onclick=()=>setCodeSize(Math.max(10,codeSize-1));
$("#code-up2").onclick=()=>setCodeSize(Math.min(22,codeSize+1));
$("#code-dn2").onclick=()=>setCodeSize(Math.max(10,codeSize-1));

// ═══════════════════ THEME ═══════════════════
let accent='default';
window.setAccent=function(a){
  accent=a;document.body.classList.remove('theme-purple','theme-cyan','theme-amber','theme-rose');
  if(a!=='default')document.body.classList.add('theme-'+a);
  $$("#topbar .theme-dot").forEach(d=>d.classList.toggle("on",(a==='default'&&d.id==='td-d')||d.id==='td-'+a[0]));
  localStorage.setItem('c-ac',a);
};
function applyLightMode(on){
  if(on){document.body.classList.add('light');$("#btn-light").textContent='🌙'}
  else{document.body.classList.remove('light');$("#btn-light").textContent='☀️'}
  localStorage.setItem('c-lt',on?'1':'0');
}
$("#btn-light").onclick=()=>applyLightMode(!document.body.classList.contains('light'));

function initSystemTheme(){
  if(localStorage.getItem('c-lt')===null){
    const prefersDark=window.matchMedia('(prefers-color-scheme: dark)').matches;
    if(!prefersDark)applyLightMode(true);
  }
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change',e=>{
    if(localStorage.getItem('c-lt')===null)applyLightMode(!e.matches);
  });
}

// ═══════════════════ SIDEBAR ═══════════════════
function toggleSidebar(){
  sidebarCollapsed=!sidebarCollapsed;
  var sb=$("#sidebar"),g1=$("#grip1"),btn=$("#btn-sidebar");
  if(sidebarCollapsed){sb.classList.add('collapsed');g1.classList.add('collapsed');btn.textContent='☰'}
  else{sb.classList.remove('collapsed');g1.classList.remove('collapsed');btn.textContent='✕';sb.style.width=(parseInt(localStorage.getItem('c-sidebar'))||220)+'px';sb.style.flex='none'}
  localStorage.setItem('c-sidebar-collapsed',sidebarCollapsed?'1':'0');
}
$("#btn-sidebar").onclick=toggleSidebar;
document.addEventListener("keydown",e=>{if((e.ctrlKey||e.metaKey)&&e.key==="b"){e.preventDefault();toggleSidebar()}});

// ═══════════════════ DRAG SYSTEM ═══════════════════
(function(){
  var sw=parseInt(localStorage.getItem('c-sidebar'))||220;
  var rw=parseInt(localStorage.getItem('c-right'))||400;
  $("#sidebar").style.cssText='width:'+sw+'px;flex:none';
  $("#center").style.cssText='flex:1;min-width:200px';
  $("#right").style.cssText='width:'+rw+'px;flex:none;min-width:320px';
  if(localStorage.getItem('c-sidebar-collapsed')==='1'){sidebarCollapsed=true;$("#sidebar").classList.add('collapsed');$("#grip1").classList.add('collapsed');$("#btn-sidebar").textContent='☰'}
  var outH=parseInt(localStorage.getItem('c-out-h'))||200;
  if(outH!==200){$("#output-pane").style.height=outH+'px';$("#output-pane").style.flex='none'}

  var drag=null;
  document.addEventListener('mousedown',function(e){
    var grip=e.target.closest('.grip,.grip-v');
    if(!grip||grip.classList.contains('collapsed'))return;
    if(grip.id==='grip1'&&sidebarCollapsed)return;
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

// ═══════════════════ UI HELPERS ═══════════════════
function dot(cls,txt){const d=$("#run-dot");d.textContent=txt;d.className=cls+' on';setTimeout(()=>d.classList.remove('on'),3500)}
function toast(msg,cls="ok"){const t=document.createElement("div");t.className="toast "+cls;t.textContent=msg;document.body.appendChild(t);setTimeout(()=>{t.style.opacity="0";setTimeout(()=>t.remove(),300)},3000)}
function setBtnLoading(btn,loading){if(loading){btn.classList.add('loading');btn.disabled=true}else{btn.classList.remove('loading');btn.disabled=false}}
// Terminal helpers — unified output+input textarea
function out(h){const ta=$("#term-out");ta.value=h;ta.scrollTop=ta.scrollHeight;_inputStart=ta.value.length}
function outAppend(t){const ta=$("#term-out");ta.value+=t;ta.scrollTop=ta.scrollHeight;if(isRunning)_inputStart=ta.value.length}
function outHTML(h){$("#judge-body").innerHTML=h;$("#judge-body").style.display='';$("#term-out").style.display='none'}
function showTerm(){ $("#term-out").style.display='';$("#judge-body").style.display='none' }
function clr(){showTerm();out('')}
function esc(s){return(s||"").replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}

// ═══════════════════ CODE HISTORY ═══════════════════
const MAX_HISTORY=10;
function saveCodeHistory(code){
  if(!code.trim()||code===DEFAULT_CODE)return;
  try{
    let hist=JSON.parse(localStorage.getItem('c-code-hist')||'[]');
    if(hist.length>0&&hist[0].code===code)return;
    hist.unshift({code:code.slice(0,2000),time:Date.now()});
    if(hist.length>MAX_HISTORY)hist=hist.slice(0,MAX_HISTORY);
    localStorage.setItem('c-code-hist',JSON.stringify(hist));
  }catch(e){}
}
function loadCodeHistory(){
  try{return JSON.parse(localStorage.getItem('c-code-hist')||'[]')}catch(e){return[]}
}
function showHistoryMenu(){
  const menu=$("#history-menu"),hist=loadCodeHistory();
  if(!hist.length){menu.innerHTML='<div class="h-empty">暂无历史记录</div>'}
  else{menu.innerHTML=hist.map((h,i)=>'<div class="h-item" data-i="'+i+'" title="点击恢复此代码">'+esc(h.code.slice(0,80))+'...</div>').join('')}
  menu.classList.toggle('on');
  $$("#history-menu .h-item").forEach(el=>el.onclick=()=>{const i=parseInt(el.dataset.i);setCode(hist[i].code);menu.classList.remove('on');toast('代码已恢复')});
}
$("#btn-history").onclick=(e)=>{e.stopPropagation();showHistoryMenu();};
document.addEventListener('click',e=>{if(!e.target.closest('.history-wrap'))$("#history-menu").classList.remove('on')});

// ═══════════════════ API ═══════════════════
async function api(path,opts={}){
  try{const r=await fetch(API+path,{headers:{"Content-Type":"application/json"},...opts});return r.json()}
  catch(e){console.error('API error:',path,e);return{error:e.message}}
}
async function loadData(){
  const[mods,exs,prog]=await Promise.all([api("/api/modules"),api("/api/exercises"),api("/api/progress")]);
  modules=mods||[];exercises=exs||[];
  progress={};if(prog&&prog.details)for(const[k,v]of Object.entries(prog.details))progress[k]=v.status;
  const done=prog?prog.solved||0:0,total=prog?prog.total||144:144;
  $("#done-n").textContent=done;$("#mini-f").style.width=(total?(done/total*100):0)+"%";
}

// ═══════════════════ MARKDOWN ═══════════════════
function md2html(md){
  if(!md)return"";let h=md;
  h=h.replace(/```(\w*)\n([\s\S]*?)```/g,(_,lang,code)=>'<pre><code>'+esc(code.trim())+'</code></pre>');
  h=h.replace(/(\|[^\n]+\|\n)(\|[-:\s|]+\|\n)((?:\|[^\n]+\|\n?)+)/g,(_,head,sep,rows)=>{
    var hc=head.split('|').filter(c=>c.trim()).map(c=>'<th>'+c.trim()+'</th>').join('');
    var rb=rows.trim().split('\n').map(r=>'<tr>'+r.split('|').filter(c=>c.trim()).map(c=>'<td>'+c.trim()+'</td>').join('')+'</tr>').join('');
    return '<div class="table-wrap"><table><thead><tr>'+hc+'</tr></thead><tbody>'+rb+'</tbody></table></div>';
  });
  h=h.replace(/`([^`]+)`/g,'<code>$1</code>');h=h.replace(/\*\*([^*]+)\*\*/g,'<strong>$1</strong>');
  h=h.replace(/^### (.+)$/gm,'<h3>$1</h3>');h=h.replace(/^## (.+)$/gm,'<h2>$1</h2>');h=h.replace(/^# (.+)$/gm,'<h1>$1</h1>');
  h=h.replace(/^[-*] (.+)$/gm,'<li>$1</li>');h=h.replace(/(<li>.*<\/li>\n?)+/g,'<ul>$&</ul>');
  h=h.replace(/(<table>[\s\S]*?<\/table>)/g,'<div class="table-wrap">$1</div>');
  h=h.replace(/\n\n/g,'</p><p>');h='<p>'+h+'</p>';h=h.replace(/<p><\/p>/g,'');
  h=h.replace(/<p><(h|pre|ul|table|hr|div)/g,'<$1');h=h.replace(/<\/(h3|h2|h1|pre|ul|table|div)><\/p>/g,'</$1>');
  return h;
}

// ═══════════════════ COURSE TREE ═══════════════════
const LV={"1":"一、基础入门","2":"二、控制流程","3":"三、函数","4":"四、内存理解","5":"五、数组","6":"六、数据结构","7":"七、指针","8":"八、进阶","9":"九、字符串","10":"十、专家","11":"十一、结构体","12":"十二、文件 I/O","13":"十三、动态内存","14":"十四、算法","15":"十五、系统","16":"十六、项目"};

function buildCourseTree(){
  $("#side-title").textContent="课程";$("#side-num").textContent=modules.length+" 课时";
  const ctr=$("#side-inner");ctr.innerHTML="";
  const groups={};for(const m of modules)(groups[m.level]||=[]).push(m);
  for(const lv of Object.keys(groups).sort((a,b)=>a-b)){
    const mods=groups[lv].sort((a,b)=>a.order-b.order);
    const done=mods.filter(m=>progress[m.slug]==="passed").length,total=mods.length;
    const card=document.createElement("div");card.className="chapter";
    const head=document.createElement("div");head.className="ch-head";
    head.innerHTML='<span><span class="arr">▼</span> '+(LV[lv]||"Level "+lv)+'</span><span class="prog'+(done===total&&total>0?' done':'')+'">'+done+'/'+total+'</span>';
    const body=document.createElement("div");let fold=false;
    head.onclick=()=>{fold=!fold;head.classList.toggle("fold",fold);body.style.display=fold?"none":""};
    card.appendChild(head);card.appendChild(body);
    for(const m of mods){
      const isDone=progress[m.slug]==="passed",isCur=curMod&&curMod.slug===m.slug;
      const d=document.createElement("div");d.className="lesson"+(isCur?" cur":"");
      d.innerHTML='<span class="ico'+(isDone?' done':'')+'">'+(isDone?'✓':(isCur?'▸':'○'))+'</span>'+m.title;
      d.onclick=()=>openModule(m);body.appendChild(d);
    }
    ctr.appendChild(card);
  }
}

// ═══════════════════ EXERCISE LIST ═══════════════════
function buildExerciseList(filter="all"){
  exCurrentFilter=filter;$("#side-title").textContent="练习";
  const done=exercises.filter(e=>e.status==="passed").length;
  $("#side-num").textContent='已过 '+done+'/'+exercises.length;
  const ctr=$("#side-inner");ctr.innerHTML="";

  const swrap=document.createElement("div");swrap.className="search-wrap";
  const sinp=document.createElement("input");sinp.type="text";sinp.placeholder="搜索题目...";sinp.value=exSearchTerm;
  sinp.addEventListener('input',()=>{exSearchTerm=sinp.value;buildExerciseList(exCurrentFilter)});
  swrap.appendChild(sinp);ctr.appendChild(swrap);

  const flt=document.createElement("div");flt.className="flt-row";
  [["all","全部"],["easy","简单"],["medium","中等"],["hard","困难"]].forEach(([v,label])=>{
    const b=document.createElement("button");b.textContent=label;if(v===filter)b.classList.add("on");
    b.onclick=()=>{exSearchTerm="";buildExerciseList(v)};flt.appendChild(b);
  });ctr.appendChild(flt);

  let list=exercises;
  if(filter!=="all")list=list.filter(e=>e.difficulty===filter);
  if(exSearchTerm){
    const q=exSearchTerm.toLowerCase();
    list=list.filter(e=>e.title.toLowerCase().includes(q)||(e.tags||[]).some(t=>t.toLowerCase().includes(q)));
  }
  for(const ex of list){
    const st=ex.status,isCur=curEx&&curEx.id===ex.id;
    const d=document.createElement("div");d.className="ex-item"+(isCur?" cur":"");
    d.innerHTML='<span class="dot '+(ex.difficulty==='medium'?'med':ex.difficulty)+'">●</span> <span style="width:14px;font-size:9px;color:'+(st==='passed'?'var(--green)':st==='failed'?'var(--red)':'var(--text3)')+'">'+(st==='passed'?'✓':(st==='failed'?'✗':''))+'</span> '+ex.title;
    d.onclick=()=>openExercise(ex);ctr.appendChild(d);
  }
  if(list.length===0&&exercises.length>0){
    ctr.appendChild(Object.assign(document.createElement("div"),{className:'h-empty',textContent:'无匹配题目'}));
  }
}

// ═══════════════════ NAVIGATION ═══════════════════
function getAdjacent(){
  const flat=[],groups={};for(const m of modules)(groups[m.level]||=[]).push(m);
  for(const lv of Object.keys(groups).sort((a,b)=>a-b))for(const m of groups[lv].sort((a,b)=>a.order-b.order))flat.push(m);
  const i=flat.findIndex(m=>m.slug===curMod?.slug);
  return{prev:i>0?flat[i-1]:null,next:i<flat.length-1?flat[i+1]:null};
}

// ═══════════════════ WELCOME / DASHBOARD ═══════════════════
function showWelcome(){
  const doneEx=exercises.filter(e=>e.status==="passed").length,totalEx=exercises.length;
  const pct=Math.round(doneEx/totalEx*100)||0;
  let nl=null;for(const m of modules){if(progress[m.slug]!=="passed"){nl=m;break}}if(!nl&&modules.length)nl=modules[0];

  // Module progress
  const groups={};for(const m of modules)(groups[m.level]||=[]).push(m);
  let mpRows='';
  for(const lv of Object.keys(groups).sort((a,b)=>a-b)){
    const mods=groups[lv];
    const d=mods.filter(m=>progress[m.slug]==="passed").length;
    const p=mods.length?Math.round(d/mods.length*100):0;
    mpRows+='<div class="mp-row"><span class="mp-name">'+(LV[lv]||"Lv"+lv)+'</span><div class="mp-bar"><div class="mp-fill '+(p===100?'done':'prog')+'" style="width:'+p+'%"></div></div><span class="mp-n">'+d+'/'+mods.length+'</span></div>';
  }

  $("#center").innerHTML=
    '<div class="welcome"><div class="emoji">🎓</div><h1>欢迎学习 C 语言！</h1><div class="sub">即学即写 · 学写结合</div>'+
    '<div class="stat-row">'+
    '<div class="stat-card"><div class="val">'+doneEx+'</div><div class="lbl">已完成练习</div></div>'+
    '<div class="stat-card"><div class="val">'+pct+'%</div><div class="lbl">总体进度</div></div>'+
    '<div class="stat-card"><div class="val">'+exercises.filter(e=>e.difficulty==="hard"&&e.status==="passed").length+'</div><div class="lbl">困难题已过</div></div>'+
    '</div>'+
    '<div class="module-progress"><h3>📊 模块进度</h3>'+mpRows+'</div>'+
    '<div class="step"><span class="n">1</span>左侧选择课程，阅读讲解</div>'+
    '<div class="step"><span class="n">2</span>右侧编辑器编写代码</div>'+
    '<div class="step"><span class="n">3</span>点击 <b>▶ 运行</b> 查看结果</div>'+
    '<div class="step"><span class="n">4</span>切换到 <b>练习</b> 或 <b>可视化</b> 模式</div>'+
    (nl?'<button class="start-btn" id="start-btn">开始学习：'+nl.title+'</button>':'');
  $("#center").scrollTop=0;
  if(nl)$("#start-btn").onclick=()=>openModule(nl);
}

// ═══════════════════ OPEN MODULE ═══════════════════
function openModule(mod){
  curMod=mod;curEx=null;$("#var-panel").classList.remove('on');
  // Strip leading # heading from content to avoid duplicate title
  // (frontmatter title is already shown as <h1>)
  let content = mod.content_md || "*暂无内容*";
  content = content.replace(/^# .+\n?/, '').trim();
  $("#center").innerHTML='<h1>'+mod.title+'</h1>'+md2html(content);
  $("#center").scrollTop=0;
  const blocks=[...(mod.content_md||"").matchAll(/```c\n([\s\S]*?)```/g)];
  let code=DEFAULT_CODE;
  const mainBlock=blocks.find(b=>b[1].includes('int main'));
  if(mainBlock)code=mainBlock[1].trim();
  else if(blocks.length>0)code=blocks[0][1].trim();
  setCode(code);clr();dot('','');$("#btn-submit").style.display="none";$("#btn-reset").style.display="none";
  // Mark module as viewed for progress tracking
  api("/api/progress/module/"+mod.slug,{method:"POST"}).then(()=>{progress[mod.slug]="passed";buildCourseTree()});
  $$("#output-pane .otab").forEach(b=>{if(b.dataset.tab==="judge")b.style.display="none"});
  const nav=document.createElement("div");nav.className="lesson-nav";
  const{prev,next}=getAdjacent();
  nav.innerHTML='<button '+(prev?'':'disabled style="opacity:0.3"')+'>← '+(prev?prev.title:'没有了')+'</button><button class="primary">'+(next?'下一课：'+next.title+' →':'完成全部！')+'</button>';
  nav.children[0].onclick=()=>{if(prev)openModule(prev)};nav.children[1].onclick=()=>{if(next)openModule(next)};
  $("#center").appendChild(nav);buildCourseTree();
  setTimeout(()=>{const c=document.querySelector(".lesson.cur");if(c)c.scrollIntoView({block:"center",behavior:"smooth"})},100);
}

// ═══════════════════ OPEN EXERCISE ═══════════════════
async function openExercise(ex){
  curEx=ex;curMod=null;$("#var-panel").classList.remove('on');
  const d=await api('/api/exercise/'+ex.id);if(d.error)return;
  const dn=d.difficulty==="easy"?"简单":d.difficulty==="medium"?"中等":"困难";
  const sb=d.status==="passed"?'<span class="badge ok">✓ 已通过</span>':(d.status==="failed"?'<span class="badge no">✗ 未通过</span>':'');
  $("#center").innerHTML='<h1>'+d.title+'</h1><div style="display:flex;gap:6px;align-items:center;margin-bottom:14px;flex-wrap:wrap"><span class="badge '+(d.difficulty==='medium'?'medium':d.difficulty)+'">'+dn+'</span>'+sb+(d.tags||[]).map(t=>'<span style="padding:2px 8px;border-radius:4px;font-size:var(--fs-xs);background:var(--bg-hover);color:var(--text2)">'+t+'</span>').join('')+'</div>'+md2html(d.description_md||"")+(d.hints?.length?'<div style="margin-top:14px;padding:10px;background:var(--bg-hover);border-radius:8px;font-size:11px;color:var(--text2);line-height:1.7">💡 提示：'+d.hints.join(' | ')+'</div>':"");
  $("#center").scrollTop=0;
  setCode(d.template_code||"// 在这里写你的代码\n");clr();dot('','');
  $("#btn-submit").style.display="";$("#btn-reset").style.display="";
  $$("#output-pane .otab").forEach(b=>{if(b.dataset.tab==="judge")b.style.display=""});
  buildExerciseList(exCurrentFilter);
}

// ═══════════════════ VARIABLE INSPECTOR ═══════════════════
function inspectVars(code){
  const vars=[],re=/\b(int|float|double|char)\s+(\*?\s*\w+)\s*(=|;)/g;let m;
  while((m=re.exec(code))!==null){
    const type=m[1],name=m[2].replace(/\s+/g,''),init=m[3]==='=';
    if(!['main','if','for','while','return'].includes(name)&&name.length>0)vars.push({type,name,init});
  }
  const seen=new Set();return vars.filter(v=>{if(seen.has(v.name))return false;seen.add(v.name);return true});
}
function showVarPanel(vars){
  const el=$("#var-list");
  if(!vars.length){el.innerHTML='<span style="color:var(--text3)">未检测到变量</span>';return}
  el.innerHTML=vars.map(v=>'<div class="vi"><span class="vt">'+v.type+'</span><span class="vn">'+v.name+'</span>'+(v.init?'<span class="vv">= ...</span>':'')+'</div>').join('');
  $("#var-panel").classList.add('on');
}
$("#btn-inspect").onclick=()=>{const v=inspectVars(getCode());showVarPanel(v);toast(v.length?'检测到 '+v.length+' 个变量':"未检测到变量",v.length?"ok":"warn")};
$("#var-close").onclick=()=>$("#var-panel").classList.remove('on');

// ═══════════════════ INTERACTIVE RUN (UNIFIED TERMINAL) ═══════════════════
let pollTimer=null;
let _inputStart=0;  // cursor position: user can only type at or after this

function stopInteractive(){
  if(pollTimer){clearInterval(pollTimer);pollTimer=null;}
  api("/api/interactive/kill",{method:"POST"});
  isRunning=false;
  $("#btn-run").textContent="▶ 运行";
  $("#btn-run").classList.remove('stopping');
  $("#stdin-bar").classList.remove('running');
  // Make terminal read-only again
  const ta=$("#term-out");
  ta.readOnly=true;
  ta.classList.remove('running');
  _inputStart=0;
}

// Prevent editing old output — only allow typing at cursor >= _inputStart
$("#term-out").addEventListener('keydown',function(e){
  if(!isRunning)return;
  const ta=this;

  // Allow navigation keys
  if(e.key==='Home'||e.key==='End'||e.key==='ArrowUp'||e.key==='ArrowDown'||
     e.key==='ArrowLeft'||e.key==='ArrowRight'||e.ctrlKey||e.metaKey||e.altKey){
    // ArrowLeft/Up: if cursor would go before _inputStart, prevent
    if((e.key==='ArrowLeft'||e.key==='ArrowUp'||e.key==='Backspace')&&ta.selectionStart<=_inputStart){
      e.preventDefault();
    }
    return;
  }

  // Enter: capture input and send to process
  if(e.key==='Enter'){
    e.preventDefault();
    // Keep cursor at end
    if(ta.selectionStart<_inputStart){ta.selectionStart=ta.selectionEnd=ta.value.length;return}
    // Get input typed since last program output
    const input=ta.value.slice(_inputStart);
    if(!input.trim())return;
    // Send to stdin
    api("/api/interactive/input",{method:"POST",body:JSON.stringify({text:input})});
    // Advance input start past this line (+1 for the Enter newline)
    ta.value+='\n';
    _inputStart=ta.value.length;
    ta.scrollTop=ta.scrollHeight;
    return;
  }

  // Prevent typing before _inputStart
  if(ta.selectionStart<_inputStart){
    ta.selectionStart=ta.selectionEnd=ta.value.length;
  }
});

// Also lock cursor via click/mouseup
["mouseup","click"].forEach(ev=>$("#term-out").addEventListener(ev,function(){
  if(!isRunning)return;
  if(this.selectionStart<_inputStart){
    this.selectionStart=this.selectionEnd=this.value.length;
  }
}));

$("#btn-run").onclick=async()=>{
  const code=getCode();if(!code.trim())return;

  // If already running, stop it
  if(isRunning){stopInteractive();showTerm();outAppend('\n--- 程序已停止 ---\n');return}

  isRunning=true;$("#btn-run").textContent="⏹ 停止";$("#btn-run").classList.add('stopping');
  saveCodeHistory(code);
  showTerm();
  out('');  // Clear terminal
  const ta=$("#term-out");
  ta.readOnly=false;
  ta.classList.add('running');
  ta.focus();
  _inputStart=0;
  dot('','');
  $$("#output-pane .otab").forEach(b=>b.classList.toggle("on",b.dataset.tab==="out"));

  // Compile and start
  const startRes=await api("/api/interactive/start",{method:"POST",body:JSON.stringify({code})});

  if(startRes.status==="compile_error"){
    const errText=startRes.error||"编译失败";
    const lines=errText.split('\n').map(l=>/main\.c:(\d+)/.test(l)?'<span class="erlink" data-line="'+RegExp.$1+'">'+esc(l)+'</span>':esc(l)).join('\n');
    outHTML('<div style="color:var(--red);font-weight:700;margin-bottom:4px">编译错误</div>\n'+lines+'\n<div class="hint">点击蓝色行号跳转到错误位置</div>');
    dot('no','编译失败');
    $$(".erlink").forEach(el=>el.onclick=()=>{
      const ln=parseInt(el.dataset.line),lines=codeInput.value.split('\n');
      let pos=0;for(let i=0;i<ln-1;i++)pos+=lines[i].length+1;
      codeInput.focus();codeInput.setSelectionRange(pos,pos+lines[ln-1].length);
    });
    stopInteractive();return;
  }

  if(startRes.status==="error"||startRes.error){
    out(esc(startRes.error||"启动失败"));
    stopInteractive();return;
  }

  // Start polling for output
  pollTimer=setInterval(async()=>{
    const res=await api("/api/interactive/poll");
    if(!res)return;

    // Append new output
    for(const line of res.lines){
      outAppend(line.text);
    }

    if(!res.running){
      // Process exited
      clearInterval(pollTimer);pollTimer=null;
      isRunning=false;
      $("#btn-run").textContent="▶ 运行";
      $("#btn-run").classList.remove('stopping');
      ta.readOnly=true;
      ta.classList.remove('running');
      _inputStart=0;

      if(res.exit_code===0){
        dot('ok','运行成功');const v=inspectVars(code);if(v.length)showVarPanel(v);
        if(!curEx)toast("运行成功！");
      }else{
        outAppend('\n[退出码 '+res.exit_code+']\n');
        dot('no','退出码 '+res.exit_code);
      }
    }
  },80);
};

// ═══════════════════ SUBMIT ═══════════════════
$("#btn-submit").onclick=async()=>{
  if(!curEx||isRunning)return;const code=getCode();if(!code.trim())return;
  isRunning=true;setBtnLoading($("#btn-submit"),true);saveCodeHistory(code);
  showTerm();out('判题中...');
  $$("#output-pane .otab").forEach(b=>b.classList.toggle("on",b.dataset.tab==="out"));
  try{
    const r=await api("/api/submit",{method:"POST",body:JSON.stringify({code,exercise_id:curEx.id})});
    let h="";
    if(r.status==="accepted"){
      h+='<div class="ok-big">🎉 完全正确！</div><div style="text-align:center;color:var(--text3);margin-bottom:8px">'+r.total_count+'/'+r.total_count+' 测试通过 · '+r.wall_time_ms+'ms</div>';
      dot('ok','全部通过');toast("全部通过！");
    }else if(r.status==="compile_error"){
      h+='<div class="no-big">编译错误</div><div style="text-align:center;color:var(--red)">'+esc(r.compile_error||"")+'</div>';
      dot('no','编译失败');toast("编译没通过","warn");
    }else{
      h+='<div class="no-big">通过 '+r.passed_count+'/'+r.total_count+'</div><div style="text-align:center;color:var(--text2);margin-bottom:8px">别灰心，改完再试！</div>';
      dot('no','部分通过');toast(r.passed_count+'/'+r.total_count+' 通过',"warn");
    }
    if(r.test_results)for(const tc of r.test_results){
      if(tc.passed)h+='<div class="case-ok">✓ 测试 '+tc.case+'</div>';
      else{h+='<div class="case-no">✗ 测试 '+tc.case+'</div>';if(tc.error)h+='<div class="s">  '+esc(tc.error)+'</div>';if(tc.actual)h+='<div class="s">  你的输出：'+esc(tc.actual)+'</div>';if(tc.expected)h+='<div class="s">  预期输出：'+esc(tc.expected)+'</div>'}
    }
    outHTML(h);await loadData();buildExerciseList(exCurrentFilter);
  }catch(e){outHTML('<span style="color:var(--red)">请求失败：'+esc(e.message)+'</span>')}
  finally{isRunning=false;setBtnLoading($("#btn-submit"),false)}
};

// ═══════════════════ RESET ═══════════════════
$("#btn-reset").onclick=async()=>{
  if(!curEx)return;const d=await api('/api/exercise/'+curEx.id);
  setCode(d.template_code||"");clr();dot('','');toast("代码已重置");
};

// Clear output
$("#tab-clear").onclick=()=>{clr();dot('','')};

// ═══════════════════ VISUALIZATION ═══════════════════
const EXAMPLES_CODE={
  pointer_basics:'#include <stdio.h>\n\nint main() {\n    int a = 5;\n    int b = 10;\n    int *p = &a;\n\n    printf("a = %d\\n", a);\n    *p = 20;\n    printf("a = %d\\n", a);\n\n    p = &b;\n    printf("*p = %d\\n", *p);\n    return 0;\n}',
  function_pointer:'#include <stdio.h>\n\nvoid swap(int *x, int *y) {\n    int temp = *x;\n    *x = *y;\n    *y = temp;\n}\n\nint main() {\n    int a = 5;\n    int b = 10;\n\n    printf("before: a=%d b=%d\\n", a, b);\n    swap(&a, &b);\n    printf("after:  a=%d b=%d\\n", a, b);\n    return 0;\n}',
  array_pointer:'#include <stdio.h>\n\nint main() {\n    int arr[3] = {10, 20, 30};\n    int *p = arr;\n\n    printf("arr[0] = %d\\n", arr[0]);\n    printf("*p = %d\\n", *p);\n\n    p = p + 1;\n    printf("*p = %d\\n", *p);\n\n    *p = 99;\n    printf("arr[1] = %d\\n", arr[1]);\n    return 0;\n}',
};

function showVizPanel(){
  $("#sidebar").style.display="none";$("#center").style.display="none";$("#right").style.display="none";
  $$('.grip').forEach(g=>g.style.display='none');$$('.grip-v').forEach(g=>g.style.display='none');
  $("#viz-panel").classList.add('on');
}
function hideVizPanel(){
  $("#sidebar").style.display="";$("#center").style.display="";$("#right").style.display="";
  $$('.grip').forEach(g=>{if(!g.classList.contains('collapsed'))g.style.display=''});
  $$('.grip-v').forEach(g=>g.style.display='');
  $("#viz-panel").classList.remove('on');
}

async function vizLoadCode(code){
  const r=await api("/api/sim/load",{method:"POST",body:JSON.stringify({code})});
  if(r.error){toast(r.error,"err");return}
  vizRefresh(r);
}
async function vizStep(){const r=await api("/api/sim/step",{method:"POST"});vizRefresh(r)}
async function vizBack(){const r=await api("/api/sim/back",{method:"POST"});vizRefresh(r)}
async function vizReset(){const r=await api("/api/sim/reset",{method:"POST"});vizRefresh(r)}
async function vizRunAll(){const r=await api("/api/sim/run",{method:"POST"});vizRefresh(r)}

function vizRefresh(r){
  if(!r||r.error)return;
  const lines=(EXAMPLES_CODE[r._example]||$("#viz-code").textContent||"").split('\n');
  $("#viz-gutter").innerHTML=lines.map((_,i)=>'<span'+(i+1===r.current_line?' class="hl"':'')+'>'+(i+1)+'</span>').join('\n');
  $("#viz-code").innerHTML=lines.map((l,i)=>'<span'+(i+1===r.current_line?' class="hl"':'')+'>'+esc(l)+'</span>').join('\n');

  let mem='<table><tr style="color:var(--text3)"><th style="padding:4px 6px;text-align:left;border-bottom:1px solid var(--border)">变量</th><th style="padding:4px 6px;text-align:left;border-bottom:1px solid var(--border)">类型</th><th style="padding:4px 6px;text-align:left;border-bottom:1px solid var(--border)">值</th><th style="padding:4px 6px;text-align:left;border-bottom:1px solid var(--border)">地址</th><th style="padding:4px 6px;text-align:left;border-bottom:1px solid var(--border)">指向</th><th style="padding:4px 6px;text-align:left;border-bottom:1px solid var(--border)">帧</th></tr>';
  if(r.variables)for(const v of r.variables){
    const isPtr=v.type==='int*';
    mem+='<tr style="border-bottom:1px solid var(--border)"><td style="padding:3px 6px;color:var(--text)">'+v.name+'</td><td style="padding:3px 6px;color:var(--accent2)">'+v.type+'</td><td style="padding:3px 6px;color:'+(isPtr?'var(--amber)':'var(--green)')+'">'+v.value+'</td><td style="padding:3px 6px;color:var(--text3)">'+v.address+'</td><td style="padding:3px 6px;color:var(--accent)">'+(v.points_to||'-')+'</td><td style="padding:3px 6px;color:var(--text3);font-size:9px">'+(v.frame||'')+'</td></tr>';
    if(v.elements)for(const el of v.elements){
      mem+='<tr style="border-bottom:1px solid var(--border);background:var(--bg-hover)"><td style="padding:2px 6px 2px 16px;color:var(--text2)">'+v.name+'['+el.index+']</td><td style="padding:2px 6px;color:var(--text3)">int</td><td style="padding:2px 6px;color:var(--green)">'+el.value+'</td><td style="padding:2px 6px;color:var(--text3)">'+el.addr+'</td><td>-</td><td style="font-size:9px">'+(v.frame||'')+'</td></tr>';
    }
  }
  mem+='</table>';
  if(!r.variables||!r.variables.length)mem='<div style="color:var(--text3);padding:16px;text-align:center">暂无变量 — 点击 <b>下一步</b> 开始执行</div>';
  $("#viz-memory").innerHTML=mem;
  if(r.hints&&r.hints.length)$("#viz-hints").innerHTML=r.hints.map(h=>'<div>'+h+'</div>').join('');
  $("#viz-output").textContent=r.output||'(暂无输出)';
  $("#viz-next").style.display=r.finished?'none':'';
}

$("#viz-load").onclick=()=>vizLoadCode($("#viz-code").textContent||EXAMPLES_CODE.pointer_basics);
$("#viz-next").onclick=vizStep;$("#viz-prev").onclick=vizBack;$("#viz-reset").onclick=vizReset;$("#viz-runall").onclick=vizRunAll;
$("#viz-ex1").onclick=()=>{const c=EXAMPLES_CODE.pointer_basics;$("#viz-code").textContent=c;vizLoadCode(c)};
$("#viz-ex2").onclick=()=>{const c=EXAMPLES_CODE.function_pointer;$("#viz-code").textContent=c;vizLoadCode(c)};
$("#viz-ex3").onclick=()=>{const c=EXAMPLES_CODE.array_pointer;$("#viz-code").textContent=c;vizLoadCode(c)};
$("#viz-custom").onclick=()=>{const c=getCode();if(!c.trim()){toast("请先在编辑器中编写代码","warn");return}$("#viz-code").textContent=c;vizLoadCode(c);toast("已加载编辑器中的代码")};

// ═══════════════════ MODE SWITCH ═══════════════════
$$("#topbar .modes button").forEach(b=>b.onclick=()=>{
  $$("#topbar .modes button").forEach(x=>x.classList.remove("on"));
  b.classList.add("on");mode=b.dataset.mode;curMod=null;curEx=null;
  if(mode==="visualize"){$("#viz-code").textContent=EXAMPLES_CODE.pointer_basics;showVizPanel();vizLoadCode(EXAMPLES_CODE.pointer_basics);return}
  hideVizPanel();clr();dot('','');
  $("#btn-submit").style.display=mode==="practice"?"":"none";
  $("#btn-reset").style.display=mode==="practice"?"":"none";
  if(mode==="learn"){buildCourseTree();showWelcome()}else{buildExerciseList();showWelcome()}
});

// ═══════════════════ ONBOARDING ═══════════════════
let obStep=0;
const obTotal=4;

function showOnboarding(){
  if(localStorage.getItem('c-onboarded'))return;
  obStep=0;$("#onboard-overlay").classList.add('on');
  renderObStep();
}

function hideOnboarding(){
  $("#onboard-overlay").classList.remove('on');
  localStorage.setItem('c-onboarded','1');
}

function renderObStep(){
  for(let i=0;i<obTotal;i++)$("#ob-step-"+i).style.display=i===obStep?'':'none';
  $("#ob-prev").style.visibility=obStep===0?'hidden':'';
  $("#ob-next").style.display=obStep===obTotal-1?'none':'';
  $("#ob-done").style.display=obStep===obTotal-1?'':'none';

  // Dots
  let dots='';
  for(let i=0;i<obTotal;i++)dots+='<span class="dot'+(i===obStep?' on':'')+'"></span>';
  $("#ob-dots").innerHTML=dots;

  // First step: show stats
  if(obStep===0){
    const d=exercises.filter(e=>e.status==="passed").length;
    const t=exercises.length;
    const p=Math.round(d/t*100)||0;
    $("#ob-stats").innerHTML='<div class="os"><div class="n">'+modules.length+'</div><div class="l">课时</div></div><div class="os"><div class="n">'+t+'</div><div class="l">练习题</div></div><div class="os"><div class="n">'+p+'%</div><div class="l">完成率</div></div>';
  }
}

$("#ob-prev").onclick=()=>{if(obStep>0){obStep--;renderObStep()}};
$("#ob-next").onclick=()=>{if(obStep<obTotal-1){obStep++;renderObStep()}};
$("#ob-done").onclick=()=>hideOnboarding();
$("#btn-help").onclick=()=>{obStep=0;renderObStep();$("#onboard-overlay").classList.add('on')};

// ═══════════════════ SHORTCUTS ═══════════════════
document.addEventListener("keydown",e=>{
  if((e.ctrlKey||e.metaKey)&&e.key==="Enter"){
    e.preventDefault();
    if(!isRunning)(mode==="practice"&&curEx?$("#btn-submit"):$("#btn-run")).click();
  }
});

// ═══════════════════ RESTORE PREFERENCES ═══════════════════
const gs=parseInt(localStorage.getItem('c-gs'));if(gs)setGlobalSize(gs);
const cs=parseInt(localStorage.getItem('c-cs'));if(cs)setCodeSize(cs);
const ac=localStorage.getItem('c-ac');if(ac)setAccent(ac);
initSystemTheme();
if(localStorage.getItem('c-lt')==='1')applyLightMode(true);

// ═══════════════════ STARTUP ═══════════════════
(async()=>{
  await loadData();
  buildCourseTree();
  showWelcome();
  // Show onboarding after a short delay (only first visit)
  setTimeout(showOnboarding,600);
})();
