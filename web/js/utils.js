// ============================================================
// C Learn — utils.js (v4.1 modular)
// Shared helpers: DOM, API, render, format, theme, achievements
// ============================================================
const $=s=>document.querySelector(s),$$=s=>document.querySelectorAll(s);
const API="http://127.0.0.1:8765";
const DEFAULT_CODE='#include <stdio.h>\n\nint main() {\n    printf("Hello!\\n");\n    return 0;\n}\n';
const MAX_HISTORY=10;

// ── HTML / text helpers ──────────────────────────
function esc(s){return(s||"").replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}
function fmtTime(ts){const d=Math.floor((Date.now()-ts)/6e4);if(d<1)return'刚刚';if(d<60)return d+'分钟前';if(d<1440)return Math.floor(d/60)+'小时前';return Math.floor(d/1440)+'天前'}

// ── UI helpers ────────────────────────────────────
function dot(cls,txt){const d=$("#run-dot");d.textContent=txt;d.className=cls+' on';setTimeout(()=>d.classList.remove('on'),3500)}
function toast(msg,cls="ok"){const old=document.querySelector('.toast');if(old){old.style.opacity="0";setTimeout(()=>old.remove(),300)}const t=document.createElement("div");t.className="toast "+cls;t.textContent=msg;document.body.appendChild(t);setTimeout(()=>{t.style.opacity="0";setTimeout(()=>t.remove(),300)},3000)}
function setBtnLoading(btn,loading){if(loading){btn.classList.add('loading');btn.disabled=true}else{btn.classList.remove('loading');btn.disabled=false}}
function out(h){const ta=$("#term-out");ta.value=h;ta.scrollTop=ta.scrollHeight;window._inputStart=ta.value.length}
function outAppend(t){const ta=$("#term-out");ta.value+=t;ta.scrollTop=ta.scrollHeight;if(window._isRunning)window._inputStart=ta.value.length}
function outHTML(h){$("#judge-body").innerHTML=h;$("#judge-body").style.display='';$("#term-out").style.display='none'}
function showTerm(){$("#term-out").style.display='';$("#judge-body").style.display='none'}
function clr(){showTerm();out('')}

// ── API ───────────────────────────────────────────
async function api(path,opts={}){
  try{const r=await fetch(API+path,{headers:{"Content-Type":"application/json"},...opts});return r.json()}
  catch(e){console.error('API error:',path,e);return{error:e.message}}
}

// ── Markdown render ───────────────────────────────
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

// ── Code formatter ────────────────────────────────
function formatCode(code){
  const lines=code.split('\n');
  let out=[],indent=0;
  for(let line of lines){
    let trimmed=line.trim();
    if(!trimmed){out.push('');continue}
    if(/^else\b/.test(trimmed)&&!trimmed.endsWith('{')){indent=Math.max(0,indent-1)}
    if(trimmed.startsWith('}')||trimmed.startsWith(']')){indent=Math.max(0,indent-1)}
    out.push('    '.repeat(indent)+trimmed);
    if(trimmed.endsWith('{')||trimmed.endsWith('[')||trimmed.endsWith('(')){indent++}
    if(/^else\s*\{/.test(trimmed)){indent=Math.max(0,indent-1);out[out.length-1]='    '.repeat(indent)+trimmed;indent++}
    if(/^(case\s+|default\s*:)/.test(trimmed)){indent=Math.max(0,indent-1);out[out.length-1]='    '.repeat(indent)+trimmed;indent++}
  }
  return out.join('\n');
}

// ── Theme ─────────────────────────────────────────
function setGlobalSize(sz){
  window._globalSize=sz;document.documentElement.style.setProperty('--global-size',sz+'px');
  $("#font-lbl").textContent=sz+'px';localStorage.setItem('c-gs',sz);
}
function setCodeSize(sz){
  window._codeSize=sz;document.documentElement.style.setProperty('--editor-size',sz+'px');
  $("#code-lbl").textContent=sz;$("#code-lbl2").textContent=sz+'px';
  localStorage.setItem('c-cs',sz);
}
window.setAccent=function(a){
  window._accent=a;document.body.classList.remove('theme-purple','theme-cyan','theme-amber','theme-rose');
  if(a!=='default')document.body.classList.add('theme-'+a);
  $$("#topbar .theme-dot").forEach(d=>d.classList.toggle("on",(a==='default'&&d.id==='td-d')||d.id==='td-'+a[0]));
  localStorage.setItem('c-ac',a);
};
function applyLightMode(on){
  if(on){document.body.classList.add('light');$("#btn-light").textContent='🌙'}
  else{document.body.classList.remove('light');$("#btn-light").textContent='☀️'}
  localStorage.setItem('c-lt',on?'1':'0');
}
function initSystemTheme(){
  if(localStorage.getItem('c-lt')===null){
    const prefersDark=window.matchMedia('(prefers-color-scheme: dark)').matches;
    if(!prefersDark)applyLightMode(true);
  }
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change',e=>{
    if(localStorage.getItem('c-lt')===null)applyLightMode(!e.matches);
  });
}

// ── Achievement system ────────────────────────────
const ACHIEVEMENTS=[
  {id:'first_run',name:'初次运行',desc:'第一次成功运行 C 代码',icon:'▶️',check:p=>p.firstRun},
  {id:'first_ac',name:'首战告捷',desc:'第一次提交通过判题',icon:'✅',check:p=>p.firstAC},
  {id:'solve_10',name:'小试牛刀',desc:'通过 10 道练习题',icon:'🔟',check:p=>(p.solved||0)>=10},
  {id:'solve_50',name:'渐入佳境',desc:'通过 50 道练习题',icon:'🔥',check:p=>(p.solved||0)>=50},
  {id:'solve_100',name:'百题斩',desc:'通过 100 道练习题',icon:'💯',check:p=>(p.solved||0)>=100},
  {id:'hard_5',name:'挑战者',desc:'通过 5 道困难题',icon:'💪',check:p=>(p.hardSolved||0)>=5},
  {id:'streak_3',name:'连续三天',desc:'连续 3 天写代码',icon:'📅',check:p=>(p.streak||0)>=3},
  {id:'streak_7',name:'一周坚持',desc:'连续 7 天写代码',icon:'🌟',check:p=>(p.streak||0)>=7},
  {id:'all_basics',name:'基础毕业',desc:'完成全部基础模块',icon:'🎓',check:p=>p.basicsDone},
];

function getAchievementStats(){
  const prog=window._progress||{};
  const exs=window._exercises||[];
  const exDone=exs.filter(e=>e.status==='passed');
  const hardSolved=exDone.filter(e=>e.difficulty==='hard').length;
  const solved=exDone.length;
  let streak=0;
  try{
    const hist=JSON.parse(localStorage.getItem('c-streak')||'[]');
    const today=new Date().toISOString().slice(0,10);
    for(let i=hist.length-1;i>=0;i--){
      if(hist[i]===today)continue;
      const d=new Date(hist[i]);const expected=new Date();
      expected.setDate(expected.getDate()-(hist.length-1-i));
      if(d.toISOString().slice(0,10)===expected.toISOString().slice(0,10))streak++;
      else break;
    }
    if(hist[hist.length-1]===today)streak++;
  }catch(e){}
  const basicsDone=!!prog['hello-world']&&!!prog['variables']&&!!prog['operators'];
  return{firstRun:localStorage.getItem('c-ach-first_run')==='1',firstAC:localStorage.getItem('c-ach-first_ac')==='1',solved,hardSolved,streak,basicsDone};
}

function checkAchievements(){
  const stats=getAchievementStats();
  const unlocked=JSON.parse(localStorage.getItem('c-ach')||'[]');
  let newAch=[];
  for(const ach of ACHIEVEMENTS){
    if(unlocked.includes(ach.id))continue;
    if(ach.check(stats)){unlocked.push(ach.id);newAch.push(ach)}
  }
  localStorage.setItem('c-ach',JSON.stringify(unlocked));
  for(const a of newAch){toast(a.icon+' '+a.name+'解锁！ '+a.desc,'ok')}
}

function recordDailyActivity(){
  try{
    const today=new Date().toISOString().slice(0,10);
    let hist=JSON.parse(localStorage.getItem('c-streak')||'[]');
    if(hist[hist.length-1]!==today){hist.push(today);if(hist.length>365)hist=hist.slice(-365);localStorage.setItem('c-streak',JSON.stringify(hist))}
  }catch(e){}
}

function getDailyProblem(){
  if(!window._exercises||!window._exercises.length)return null;
  const today=new Date().toISOString().slice(0,10);
  const stored=localStorage.getItem('c-daily');
  if(stored){
    try{const d=JSON.parse(stored);if(d.date===today)return window._exercises.find(e=>e.id===d.id)||null}catch(e){}
  }
  const hash=[...today].reduce((a,c)=>a+c.charCodeAt(0),0);
  const idx=hash%window._exercises.length;
  const ex=window._exercises[idx];
  localStorage.setItem('c-daily',JSON.stringify({date:today,id:ex.id}));
  return ex;
}

// ── Progress export / import ──────────────────────
window.exportProgress=async function(){
  try{
    const r=await api('/api/progress');
    const blob=new Blob([JSON.stringify(r,null,2)],{type:'application/json'});
    const url=URL.createObjectURL(blob);
    const a=document.createElement('a');a.href=url;a.download='c-learn-progress-'+new Date().toISOString().slice(0,10)+'.json';
    a.click();URL.revokeObjectURL(url);toast("进度已导出");
  }catch(e){toast("导出失败","err")}
};
window.importProgress=function(){
  const inp=document.createElement('input');inp.type='file';inp.accept='.json';
  inp.onchange=async function(){
    try{
      const text=await inp.files[0].text();const data=JSON.parse(text);
      if(!data.details){toast("无效的进度文件","err");return}
      let cnt=0;
      for(const[k,v]of Object.entries(data.details)){
        await api('/api/progress/module/'+k,{method:'POST',body:JSON.stringify({status:v.status,code:v.last_code||''})});cnt++;
      }
      if(window._loadDataAndRefresh)await window._loadDataAndRefresh();
      toast("已导入 "+cnt+" 条进度记录");
    }catch(e){toast("导入失败: "+e.message,"err")}
  };
  inp.click();
};
