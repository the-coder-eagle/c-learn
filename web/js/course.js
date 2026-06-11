// ============================================================
// C Learn — course.js (v4.1 modular)
// Course tree, exercise list, welcome dashboard, navigation
// ============================================================

const LV={"1":"一、基础入门","2":"二、控制流程","3":"三、函数","4":"四、内存理解","5":"五、数组","6":"六、数据结构","7":"七、指针","8":"八、进阶","9":"九、字符串","10":"十、专家","11":"十一、结构体","12":"十二、文件 I/O","13":"十三、动态内存","14":"十四、算法","15":"十五、系统","16":"十六、项目"};

// ── Data loading ──────────────────────────────────
async function _loadData(){
  const[mods,exs,prog]=await Promise.all([api("/api/modules"),api("/api/exercises"),api("/api/progress")]);
  window._modules=mods||[];window._exercises=exs||[];
  window._progress={};if(prog&&prog.details)for(const[k,v]of Object.entries(prog.details))window._progress[k]=v.status;
  const done=prog?prog.solved||0:0,total=prog?prog.total||144:144;
  $("#done-n").textContent=done;$("#mini-f").style.width=(total?(done/total*100):0)+"%";
}
window._loadDataAndRefresh=async function(){
  await _loadData();
  if(window._mode==='learn'){buildCourseTree();showWelcome()}
  else{buildExerciseList(window._exCurrentFilter||'all');showWelcome()}
};
window._refreshAfterSubmit=async function(){
  await _loadData();
  if(window._exCurrentFilter)buildExerciseList(window._exCurrentFilter);
};

// ── Course tree ───────────────────────────────────
function buildCourseTree(){
  $("#side-title").textContent="课程";$("#side-num").textContent=window._modules.length+" 课时";
  const ctr=$("#side-inner");ctr.innerHTML="";
  const groups={};for(const m of window._modules)(groups[m.level]||=[]).push(m);
  for(const lv of Object.keys(groups).sort((a,b)=>a-b)){
    const mods=groups[lv].sort((a,b)=>a.order-b.order);
    const done=mods.filter(m=>window._progress[m.slug]==="passed").length,total=mods.length;
    const card=document.createElement("div");card.className="chapter";
    const head=document.createElement("div");head.className="ch-head";
    head.innerHTML='<span><span class="arr">▼</span> '+(LV[lv]||"Level "+lv)+'</span><span class="prog'+(done===total&&total>0?' done':'')+'">'+done+'/'+total+'</span>';
    const body=document.createElement("div");let fold=false;
    head.onclick=()=>{fold=!fold;head.classList.toggle("fold",fold);body.style.display=fold?"none":""};
    card.appendChild(head);card.appendChild(body);
    for(const m of mods){
      const isDone=window._progress[m.slug]==="passed",isCur=window._curMod&&window._curMod.slug===m.slug;
      const d=document.createElement("div");d.className="lesson"+(isCur?" cur":"");
      d.innerHTML='<span class="ico'+(isDone?' done':'')+'">'+(isDone?'✓':(isCur?'▸':'○'))+'</span>'+m.title;
      d.onclick=()=>openModule(m);body.appendChild(d);
    }
    ctr.appendChild(card);
  }
}

// ── Exercise list ─────────────────────────────────
function buildExerciseList(filter="all"){
  window._exCurrentFilter=filter;$("#side-title").textContent="练习";
  const done=window._exercises.filter(e=>e.status==="passed").length;
  $("#side-num").textContent='已过 '+done+'/'+window._exercises.length;
  const ctr=$("#side-inner");ctr.innerHTML="";

  const swrap=document.createElement("div");swrap.className="search-wrap";
  const sinp=document.createElement("input");sinp.type="text";sinp.placeholder="搜索题目...";sinp.value=window._exSearchTerm||"";
  sinp.addEventListener('input',()=>{window._exSearchTerm=sinp.value;buildExerciseList(window._exCurrentFilter)});
  swrap.appendChild(sinp);ctr.appendChild(swrap);

  const flt=document.createElement("div");flt.className="flt-row";
  [["all","全部"],["easy","简单"],["medium","中等"],["hard","困难"]].forEach(([v,label])=>{
    const b=document.createElement("button");b.textContent=label;if(v===filter)b.classList.add("on");
    b.onclick=()=>{window._exSearchTerm="";buildExerciseList(v)};flt.appendChild(b);
  });ctr.appendChild(flt);

  // v4.1: Tag filter chips
  const allTags=new Set();window._exercises.forEach(e=>(e.tags||[]).forEach(t=>allTags.add(t)));
  if(allTags.size>0){
    const tagRow=document.createElement("div");tagRow.className="flt-row";
    [...allTags].sort().slice(0,12).forEach(tag=>{
      const tb=document.createElement("button");tb.textContent=tag;tb.style.fontSize='9px';
      tb.onclick=()=>{window._exSearchTerm=tag;buildExerciseList(window._exCurrentFilter)};
      tagRow.appendChild(tb);
    });ctr.appendChild(tagRow);
  }

  let list=window._exercises;
  if(filter!=="all")list=list.filter(e=>e.difficulty===filter);
  if(window._exSearchTerm){
    const q=window._exSearchTerm.toLowerCase();
    list=list.filter(e=>e.title.toLowerCase().includes(q)||(e.tags||[]).some(t=>t.toLowerCase().includes(q)));
  }
  for(const ex of list){
    const st=ex.status,isCur=window._curEx&&window._curEx.id===ex.id;
    const d=document.createElement("div");d.className="ex-item"+(isCur?" cur":"");
    d.innerHTML='<span class="dot '+(ex.difficulty==='medium'?'med':ex.difficulty)+'">●</span> <span style="width:14px;font-size:9px;color:'+(st==='passed'?'var(--green)':st==='failed'?'var(--red)':'var(--text3)')+'">'+(st==='passed'?'✓':(st==='failed'?'✗':''))+'</span> '+ex.title;
    d.onclick=()=>openExercise(ex);ctr.appendChild(d);
  }
  if(list.length===0&&window._exercises.length>0){
    ctr.appendChild(Object.assign(document.createElement("div"),{className:'h-empty',textContent:'无匹配题目'}));
  }
}

// ── Welcome dashboard ─────────────────────────────
function showWelcome(){
  const doneEx=window._exercises.filter(e=>e.status==="passed").length,totalEx=window._exercises.length;
  const pct=Math.round(doneEx/totalEx*100)||0;
  let nl=null;for(const m of window._modules){if(window._progress[m.slug]!=="passed"){nl=m;break}}if(!nl&&window._modules.length)nl=window._modules[0];

  // Module progress rows
  const groups={};for(const m of window._modules)(groups[m.level]||=[]).push(m);
  let mpRows='';for(const lv of Object.keys(groups).sort((a,b)=>a-b)){
    const mods=groups[lv];const d=mods.filter(m=>window._progress[m.slug]==="passed").length;
    const p=mods.length?Math.round(d/mods.length*100):0;
    mpRows+='<div class="mp-row"><span class="mp-name">'+(LV[lv]||"Lv"+lv)+'</span><div class="mp-bar"><div class="mp-fill '+(p===100?'done':'prog')+'" style="width:'+p+'%"></div></div><span class="mp-n">'+d+'/'+mods.length+'</span></div>';
  }

  const daily=getDailyProblem();
  let dailyHTML='';
  if(daily){
    dailyHTML='<div class="daily-card" onclick="window._openExerciseById(\''+daily.id+'\')"><div class="daily-badge">📅 每日一题</div><div><b>'+daily.title+'</b></div><div style="font-size:var(--fs-xs);color:var(--text3)">难度: '+(daily.difficulty==='easy'?'简单':daily.difficulty==='medium'?'中等':'困难')+' · '+(daily.tags||[]).slice(0,3).join(', ')+'</div></div>';
  }

  const unlocked=JSON.parse(localStorage.getItem('c-ach')||'[]');
  let achHTML='';
  if(unlocked.length>0){
    const recent=ACHIEVEMENTS.filter(a=>unlocked.includes(a.id)).slice(-4);
    achHTML='<div class="ach-row">'+recent.map(a=>'<div class="ach-badge" title="'+a.desc+'">'+a.icon+'</div>').join('')+'</div>';
  }

  $("#center").innerHTML=
    '<div class="welcome"><div class="emoji">🎓</div><h1>欢迎学习 C 语言！</h1><div class="sub">即学即写 · 学写结合</div>'+dailyHTML+
    '<div class="stat-row"><div class="stat-card"><div class="val">'+doneEx+'</div><div class="lbl">已完成练习</div></div><div class="stat-card"><div class="val">'+pct+'%</div><div class="lbl">总体进度</div></div><div class="stat-card"><div class="val">'+window._exercises.filter(e=>e.difficulty==="hard"&&e.status==="passed").length+'</div><div class="lbl">困难题已过</div></div></div>'+
    achHTML+'<div class="module-progress"><h3>📊 模块进度</h3>'+mpRows+'</div>'+
    '<div class="step"><span class="n">1</span>左侧选择课程，阅读讲解</div><div class="step"><span class="n">2</span>右侧编辑器编写代码</div><div class="step"><span class="n">3</span>点击 <b>▶ 运行</b> 查看结果</div><div class="step"><span class="n">4</span>切换到 <b>练习</b> 或 <b>可视化</b> 模式</div>'+
    '<div style="display:flex;gap:10px;justify-content:center;margin-top:10px"><button class="btn-g" onclick="exportProgress()">📤 导出进度</button><button class="btn-g" onclick="importProgress()">📥 导入进度</button></div>'+
    (nl?'<button class="start-btn" id="start-btn">开始学习：'+nl.title+'</button>':'');
  $("#center").scrollTop=0;
  if(nl)$("#start-btn").onclick=()=>openModule(nl);
}

// ── Navigation ────────────────────────────────────
function getAdjacent(){
  const flat=[],groups={};for(const m of window._modules)(groups[m.level]||=[]).push(m);
  for(const lv of Object.keys(groups).sort((a,b)=>a-b))for(const m of groups[lv].sort((a,b)=>a.order-b.order))flat.push(m);
  const i=flat.findIndex(m=>m.slug===window._curMod?.slug);
  return{prev:i>0?flat[i-1]:null,next:i<flat.length-1?flat[i+1]:null};
}

function openModule(mod){
  window._curMod=mod;window._curEx=null;$("#var-panel").classList.remove('on');
  let content=mod.content_md||"*暂无内容*";
  content=content.replace(/^# .+\n?/,'').trim();
  $("#center").innerHTML='<h1>'+mod.title+'</h1>'+md2html(content);$("#center").scrollTop=0;
  const blocks=[...(mod.content_md||"").matchAll(/```c\n([\s\S]*?)```/g)];
  let code=DEFAULT_CODE;
  const mainBlock=blocks.find(b=>b[1].includes('int main'));
  if(mainBlock)code=mainBlock[1].trim();
  else if(blocks.length>0)code=blocks[0][1].trim();
  window.setCode(code);clr();dot('','');$("#btn-submit").style.display="none";$("#btn-reset").style.display="none";
  api("/api/progress/module/"+mod.slug,{method:"POST"}).then(()=>{window._progress[mod.slug]="passed";buildCourseTree()});
  $$("#output-pane .otab").forEach(b=>{if(b.dataset.tab==="judge")b.style.display="none"});
  const nav=document.createElement("div");nav.className="lesson-nav";
  const{prev,next}=getAdjacent();
  nav.innerHTML='<button '+(prev?'':'disabled style="opacity:0.3"')+'>← '+(prev?prev.title:'没有了')+'</button><button class="primary">'+(next?'下一课：'+next.title+' →':'完成全部！')+'</button>';
  nav.children[0].onclick=()=>{if(prev)openModule(prev)};nav.children[1].onclick=()=>{if(next)openModule(next)};
  $("#center").appendChild(nav);buildCourseTree();
  setTimeout(()=>{const c=document.querySelector(".lesson.cur");if(c)c.scrollIntoView({block:"center",behavior:"smooth"})},100);
}

async function openExercise(ex){
  window._curEx=ex;window._curMod=null;$("#var-panel").classList.remove('on');
  const d=await api('/api/exercise/'+ex.id);if(d.error)return;
  const dn=d.difficulty==="easy"?"简单":d.difficulty==="medium"?"中等":"困难";
  const sb=d.status==="passed"?'<span class="badge ok">✓ 已通过</span>':(d.status==="failed"?'<span class="badge no">✗ 未通过</span>':'');
  $("#center").innerHTML='<h1>'+d.title+'</h1><div style="display:flex;gap:6px;align-items:center;margin-bottom:14px;flex-wrap:wrap"><span class="badge '+(d.difficulty==='medium'?'medium':d.difficulty)+'">'+dn+'</span>'+sb+(d.tags||[]).map(t=>'<span style="padding:2px 8px;border-radius:4px;font-size:var(--fs-xs);background:var(--bg-hover);color:var(--text2)">'+t+'</span>').join('')+'</div>'+md2html(d.description_md||"")+(d.hints?.length?'<div style="margin-top:14px;padding:10px;background:var(--bg-hover);border-radius:8px;font-size:11px;color:var(--text2);line-height:1.7">💡 提示：'+d.hints.join(' | ')+'</div>':"");
  $("#center").scrollTop=0;
  window.setCode(d.template_code||"// 在这里写你的代码\n");clr();dot('','');
  $("#btn-submit").style.display="";$("#btn-reset").style.display="";
  $$("#output-pane .otab").forEach(b=>{if(b.dataset.tab==="judge")b.style.display=""});
  buildExerciseList(window._exCurrentFilter);
}

window._openExerciseById=function(exId){
  const ex=window._exercises.find(e=>e.id===exId);
  if(ex){
    window._mode='practice';
    $$("#topbar .modes button").forEach(x=>x.classList.remove('on'));
    document.querySelector('#topbar .modes button[data-mode="practice"]').classList.add('on');
    if(window._hideVizPanel)window._hideVizPanel();
    $("#btn-submit").style.display="";$("#btn-reset").style.display="";
    openExercise(ex);
  }
};

// ── Free write mode ───────────────────────────────
window._showFreeMode=function(){
  window._curMod=null;window._curEx=null;
  $("#side-title").textContent="自由写";$("#side-num").textContent="随心写";
  const ctr=$("#side-inner");ctr.innerHTML="";
  const card=document.createElement("div");card.className="chapter";
  card.innerHTML='<div style="padding:12px 14px;color:var(--text2);font-size:var(--fs-sm);line-height:1.8"><b>📝 自由编写</b><br>不受课程和习题限制<br><br><span style="color:var(--text3);font-size:var(--fs-xs)">💾 代码自动保存<br>🕐 独立历史记录<br>▶️ Ctrl+Enter 运行</span></div>';
  ctr.appendChild(card);
  const saved=localStorage.getItem('c-free-code');
  window.setCode(saved||DEFAULT_CODE);clr();dot('','');
  $("#btn-submit").style.display="none";$("#btn-reset").style.display="none";
  $$("#output-pane .otab").forEach(b=>{if(b.dataset.tab==="judge")b.style.display="none"});showTerm();
  const freeHistCount=loadCodeHistory('c-code-hist-free').length;
  $("#center").innerHTML='<div class="welcome"><div class="emoji">📝</div><h1>自由编写</h1><div class="sub">随心写 C 代码 · 自动保存 · 不受限制</div><div class="stat-row"><div class="stat-card" id="free-save-card"><div class="val" id="free-save-status">已保存</div><div class="lbl">每次运行自动保存到本地</div></div><div class="stat-card"><div class="val">'+freeHistCount+'</div><div class="lbl">历史记录</div></div></div><div class="step"><span class="n">💡</span>在这里可以自由编写任何 C 代码，不受课程和习题限制</div><div class="step"><span class="n">💾</span>代码自动保存到本地，刷新或重启不丢失</div><div class="step"><span class="n">🕐</span>每次运行自动记录到独立历史</div><div class="step"><span class="n">⌨️</span>输入 2 个字母触发代码补全，Tab 选择</div></div>';
  $("#center").scrollTop=0;
};

// Free mode autosave hook
let _freeSavePending=false;
window._onHighlight=function(){
  if(window._mode==='free'&&!_freeSavePending){
    _freeSavePending=true;
    setTimeout(()=>{localStorage.setItem('c-free-code',window.getCode());_freeSavePending=false;const el=$("#free-save-status");if(el)el.textContent='已保存 ✓'},1000);
  }
};
