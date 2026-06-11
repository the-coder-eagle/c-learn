// ============================================================
// C Learn — editor.js (v4.1 modular)
// Code editor: syntax highlight, history, autocomplete, run/submit
// ============================================================

// ── Syntax highlighting ──────────────────────────
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
    if(line[i]==='"'||line[i]==="'"){
      const q=line[i];let j=i+1;
      while(j<line.length&&line[j]!==q){if(line[j]==='\\')j++;j++}
      tokens.push({s:i,e:Math.min(j+1,line.length),c:'hl-str'});i=j+1;continue;
    }
    if(line[i]==='#'&&(i===0||/^\s*$/.test(line.slice(0,i)))){tokens.push({s:i,e:line.length,c:'hl-pp'});break}
    if(line[i]==='/'&&line[i+1]==='/'){tokens.push({s:i,e:line.length,c:'hl-cmt'});break}
    if(/\d/.test(line[i])&&(i===0||!/[a-zA-Z_]/.test(line[i-1]))){
      let j=i;while(j<line.length&&/[0-9a-fA-FxX.]/.test(line[j]))j++;
      tokens.push({s:i,e:j,c:'hl-num'});i=j;continue;
    }
    if(/[a-zA-Z_]/.test(line[i])){
      let j=i;while(j<line.length&&/[a-zA-Z0-9_]/.test(line[j]))j++;
      const w=line.slice(i,j);
      if(C_KEYWORDS.has(w))tokens.push({s:i,e:j,c:'hl-kw'});
      else if(C_TYPES.has(w))tokens.push({s:i,e:j,c:'hl-type'});
      else if(line.slice(j).trimStart().startsWith('('))tokens.push({s:i,e:j,c:'hl-fn'});
      i=j;continue;
    }
    if('+-*/%=<>!&|^~?:.'.includes(line[i])){tokens.push({s:i,e:i+1,c:'hl-op'});i++;continue}
    i++;
  }
  return tokens;
}

function highlight(){
  const ta=$("#code-input"),hl=$("#hl-code");
  const lines=ta.value.split('\n');let html='';
  for(let i=0;i<lines.length;i++){
    const tokens=tokenizeLine(lines[i]);
    if(!tokens.length){html+=esc(lines[i])+'\n';continue}
    let last=0,lineHtml='';
    for(const t of tokens){
      if(t.s>last)lineHtml+=esc(lines[i].slice(last,t.s));
      lineHtml+='<span class="'+t.c+'">'+esc(lines[i].slice(t.s,t.e))+'</span>';
      last=t.e;
    }
    if(last<lines[i].length)lineHtml+=esc(lines[i].slice(last));
    html+=lineHtml+'\n';
  }
  hl.innerHTML=html;
}

function updateGutter(){
  const n=$("#code-input").value.split('\n').length;
  $("#gutter").innerHTML=Array.from({length:n},(_,i)=>i+1).join('\n');
}

function syncEditorScroll(){
  const pre=$("#highlight-layer");
  pre.scrollTop=$("#code-input").scrollTop;
  pre.scrollLeft=$("#code-input").scrollLeft;
}

let _hlTimer=null;
function debouncedHighlight(){
  updateGutter();
  if(_hlTimer)clearTimeout(_hlTimer);
  _hlTimer=setTimeout(()=>{highlight();if(window._onHighlight)window._onHighlight()},50);
}

window.getCode=function(){return $("#code-input").value}
window.setCode=function(c){$("#code-input").value=c;updateGutter();highlight()}

// ── Code history ──────────────────────────────────
function _historyKey(){
  if(window._curEx)return'c-code-hist-'+window._curEx.id;
  if(window._mode==='free')return'c-code-hist-free';
  if(window._curMod)return'c-code-hist-mod-'+window._curMod.slug;
  return'c-code-hist-general';
}
window.saveCodeHistory=function(code){
  if(!code.trim())return;
  try{
    const key=_historyKey();
    let hist=JSON.parse(localStorage.getItem(key)||'[]');
    if(hist.length>0&&hist[0].code===code)return;
    hist.unshift({code:code.slice(0,2000),time:Date.now()});
    if(hist.length>MAX_HISTORY)hist=hist.slice(0,MAX_HISTORY);
    localStorage.setItem(key,JSON.stringify(hist));
  }catch(e){}
}
function loadCodeHistory(key){try{return JSON.parse(localStorage.getItem(key||_historyKey())||'[]')}catch(e){return[]}}
function showHistoryMenu(){
  const menu=$("#history-menu"),hist=loadCodeHistory();
  const label=window._curEx?window._curEx.title:(window._mode==='free'?'自由写':(window._curMod?window._curMod.title:'通用'));
  if(!hist.length){menu.innerHTML='<div class="h-empty">'+label+' — 暂无历史</div>'}
  else{menu.innerHTML='<div class="h-label">📋 '+label+' ('+hist.length+'条)</div>'+hist.map((h,i)=>'<div class="h-item" data-i="'+i+'"><span class="h-code">'+esc(h.code.slice(0,100))+'</span><span class="h-time">'+fmtTime(h.time)+'</span></div>').join('')}
  menu.classList.add('on');
  $$("#history-menu .h-item").forEach(el=>el.onclick=()=>{const i=parseInt(el.dataset.i);window.setCode(hist[i].code);menu.classList.remove('on');toast('代码已恢复')});
}
$("#btn-history").onclick=(e)=>{e.stopPropagation();const m=$("#history-menu");if(m.classList.contains('on'))m.classList.remove('on');else showHistoryMenu();};
document.addEventListener('click',e=>{if(!e.target.closest('.history-wrap'))$("#history-menu").classList.remove('on')});

// ── Variable inspector ────────────────────────────
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
$("#btn-inspect").onclick=()=>{const v=inspectVars(window.getCode());showVarPanel(v);toast(v.length?'检测到 '+v.length+' 个变量':"未检测到变量",v.length?"ok":"warn")};
$("#var-close").onclick=()=>$("#var-panel").classList.remove('on');

// ── Interactive run ───────────────────────────────
let pollTimer=null;
window._inputStart=0;

function stopInteractive(){
  if(pollTimer){clearInterval(pollTimer);pollTimer=null;}
  api("/api/interactive/kill",{method:"POST"});
  window._isRunning=false;
  $("#btn-run").textContent="▶ 运行";$("#btn-run").classList.remove('stopping');
  $("#stdin-bar").classList.remove('running');
  const ta=$("#term-out");ta.readOnly=true;ta.classList.remove('running');
  window._inputStart=0;
}

$("#term-out").addEventListener('keydown',function(e){
  if(!window._isRunning)return;
  const ta=this;
  if(e.key==='Home'||e.key==='End'||e.key==='ArrowUp'||e.key==='ArrowDown'||e.key==='ArrowLeft'||e.key==='ArrowRight'||e.ctrlKey||e.metaKey||e.altKey){
    if((e.key==='ArrowLeft'||e.key==='ArrowUp'||e.key==='Backspace')&&ta.selectionStart<=window._inputStart){e.preventDefault()}return;
  }
  if(e.key==='Enter'){
    e.preventDefault();
    if(ta.selectionStart<window._inputStart){ta.selectionStart=ta.selectionEnd=ta.value.length;return}
    const input=ta.value.slice(window._inputStart);
    if(!input.trim())return;
    api("/api/interactive/input",{method:"POST",body:JSON.stringify({text:input})});
    ta.value+='\n';window._inputStart=ta.value.length;ta.scrollTop=ta.scrollHeight;return;
  }
  if(ta.selectionStart<window._inputStart){ta.selectionStart=ta.selectionEnd=ta.value.length}
});
["mouseup","click"].forEach(ev=>$("#term-out").addEventListener(ev,function(){
  if(!window._isRunning)return;
  if(this.selectionStart<window._inputStart){this.selectionStart=this.selectionEnd=this.value.length}
}));

$("#btn-run").onclick=async()=>{
  const code=window.getCode();if(!code.trim())return;
  if(window._isRunning){stopInteractive();showTerm();outAppend('\n--- 程序已停止 ---\n');return}
  window._isRunning=true;$("#btn-run").textContent="⏹ 停止";$("#btn-run").classList.add('stopping');
  window.saveCodeHistory(code);showTerm();out('');
  const ta=$("#term-out");ta.readOnly=false;ta.classList.add('running');ta.focus();
  window._inputStart=0;dot('','');
  $$("#output-pane .otab").forEach(b=>b.classList.toggle("on",b.dataset.tab==="out"));

  const startRes=await api("/api/interactive/start",{method:"POST",body:JSON.stringify({code})});
  if(startRes.status==="compile_error"){
    const errText=startRes.error||"编译失败";
    const lines=errText.split('\n').map(l=>/main\.c:(\d+)/.test(l)?'<span class="erlink" data-line="'+RegExp.$1+'">'+esc(l)+'</span>':esc(l)).join('\n');
    outHTML('<div style="color:var(--red);font-weight:700;margin-bottom:4px">编译错误</div>\n'+lines+'\n<div class="hint">点击蓝色行号跳转到错误位置</div>');
    dot('no','编译失败');
    $$(".erlink").forEach(el=>el.onclick=()=>{
      const ln=parseInt(el.dataset.line),lines_=$("#code-input").value.split('\n');
      if(ln<1||ln>lines_.length)return;
      let pos=0;for(let i=0;i<ln-1;i++)pos+=lines_[i].length+1;
      $("#code-input").focus();$("#code-input").setSelectionRange(pos,pos+lines_[ln-1].length);
    });
    stopInteractive();return;
  }
  if(startRes.status==="error"||startRes.error){out(esc(startRes.error||"启动失败"));stopInteractive();return}

  pollTimer=setInterval(async()=>{
    const res=await api("/api/interactive/poll");if(!res)return;
    for(const line of res.lines){outAppend(line.text)}
    if(!res.running){
      clearInterval(pollTimer);pollTimer=null;
      window._isRunning=false;$("#btn-run").textContent="▶ 运行";$("#btn-run").classList.remove('stopping');
      ta.readOnly=true;ta.classList.remove('running');window._inputStart=0;
      if(res.exit_code===0){
        dot('ok','运行成功');const v=inspectVars(code);if(v.length)showVarPanel(v);
        if(!window._curEx){toast("运行成功！");if(!localStorage.getItem('c-ach-first_run')){localStorage.setItem('c-ach-first_run','1');setTimeout(checkAchievements,500)}}
        recordDailyActivity();
      }else{outAppend('\n[退出码 '+res.exit_code+']\n');dot('no','退出码 '+res.exit_code)}
    }
  },80);
};

// ── Submit ────────────────────────────────────────
$("#btn-submit").onclick=async()=>{
  if(!window._curEx||window._isRunning)return;const code=window.getCode();if(!code.trim())return;
  window._isRunning=true;setBtnLoading($("#btn-submit"),true);window.saveCodeHistory(code);
  showTerm();out('判题中...');
  $$("#output-pane .otab").forEach(b=>b.classList.toggle("on",b.dataset.tab==="judge"));
  try{
    const r=await api("/api/submit",{method:"POST",body:JSON.stringify({code,exercise_id:window._curEx.id})});
    let h="";
    if(r.status==="accepted"){h+='<div class="ok-big">🎉 完全正确！</div><div style="text-align:center;color:var(--text3);margin-bottom:8px">'+r.total_count+'/'+r.total_count+' 测试通过 · '+r.wall_time_ms+'ms</div>';dot('ok','全部通过');toast("全部通过！");if(!localStorage.getItem('c-ach-first_ac')){localStorage.setItem('c-ach-first_ac','1');setTimeout(checkAchievements,500)}recordDailyActivity();}
    else if(r.status==="compile_error"){h+='<div class="no-big">编译错误</div><div style="text-align:center;color:var(--red)">'+esc(r.compile_error||"")+'</div>';dot('no','编译失败');toast("编译没通过","warn")}
    else{h+='<div class="no-big">通过 '+r.passed_count+'/'+r.total_count+'</div><div style="text-align:center;color:var(--text2);margin-bottom:8px">别灰心，改完再试！</div>';dot('no','部分通过');toast(r.passed_count+'/'+r.total_count+' 通过',"warn")}
    if(r.test_results)for(const tc of r.test_results){
      if(tc.passed)h+='<div class="case-ok">✓ 测试 '+tc.case+'</div>';
      else{h+='<div class="case-no">✗ 测试 '+tc.case+'</div>';if(tc.error)h+='<div class="s">  '+esc(tc.error)+'</div>';if(tc.actual)h+='<div class="s">  你的输出：'+esc(tc.actual)+'</div>';if(tc.expected)h+='<div class="s">  预期输出：'+esc(tc.expected)+'</div>'}
    }
    outHTML(h);if(window._refreshAfterSubmit)await window._refreshAfterSubmit();
  }catch(e){outHTML('<span style="color:var(--red)">请求失败：'+esc(e.message)+'</span>')}
  finally{window._isRunning=false;setBtnLoading($("#btn-submit"),false)}
};

// ── Reset ─────────────────────────────────────────
$("#btn-reset").onclick=async()=>{
  if(!window._curEx)return;const d=await api('/api/exercise/'+window._curEx.id);
  window.setCode(d.template_code||"");clr();dot('','');toast("代码已重置");
};

// ── Output tabs ───────────────────────────────────
$$("#output-pane .otab[data-tab]").forEach(b=>b.onclick=()=>{
  if(b.dataset.tab==="out")showTerm();else{$("#term-out").style.display='none';$("#judge-body").style.display=''}
  $$("#output-pane .otab[data-tab]").forEach(x=>x.classList.toggle("on",x===b));
});
$("#tab-clear").onclick=()=>{clr();dot('','')};

// ── Autocomplete ──────────────────────────────────
const AC_PATTERNS=[
  {key:'pr',text:'printf("");',desc:'printf 输出',sel:[8,8]},
  {key:'sc',text:'scanf("%d", &x);',desc:'scanf 输入',sel:[7,10]},
  {key:'for',text:'for (int i = 0; i < N; i++) {\n    \n}',desc:'for 循环',sel:[26,26]},
  {key:'while',text:'while (1) {\n    \n}',desc:'while 循环',sel:[9,10]},
  {key:'if',text:'if (1) {\n    \n}',desc:'if 条件',sel:[6,7]},
  {key:'ife',text:'if (1) {\n    \n} else {\n    \n}',desc:'if-else',sel:[6,7]},
  {key:'switch',text:'switch (x) {\n    case 1:\n        \n        break;\n    default:\n        \n}',desc:'switch',sel:[34,34]},
  {key:'do',text:'do {\n    \n} while (1);',desc:'do-while',sel:[6,6]},
  {key:'main',text:'int main() {\n    \n    return 0;\n}',desc:'main 函数',sel:[16,16]},
  {key:'inc',text:'#include <stdio.h>\n',desc:'include',sel:[0,19]},
  {key:'struct',text:'struct name {\n    int field;\n};',desc:'结构体',sel:[13,17]},
  {key:'malloc',text:'(int*)malloc(N * sizeof(int));',desc:'malloc',sel:[0,33]},
];
let acVisible=false,acIdx=0;

function showAutocomplete(word){
  const matches=AC_PATTERNS.filter(p=>p.key.startsWith(word.toLowerCase()));
  if(!matches.length){$("#ac-drop").classList.remove('on');acVisible=false;return}
  acIdx=0;
  const h=matches.map((m,i)=>'<div class="ac-item'+(i===0?' cur':'')+'" data-i="'+i+'"><b>'+esc(m.key)+'</b><span>'+esc(m.desc)+'</span><small>'+esc(m.text.slice(0,50))+'</small></div>').join('');
  $("#ac-drop").innerHTML=h;$("#ac-drop").classList.add('on');acVisible=true;
  const ta=$("#code-input"),rect=ta.getBoundingClientRect();
  const lineHeight=parseFloat(getComputedStyle(ta).lineHeight)||20;
  const cursorTop=ta.selectionStart?ta.value.slice(0,ta.selectionStart).split('\n').length:1;
  const top=rect.top+(cursorTop-1)*lineHeight+lineHeight+4;
  $("#ac-drop").style.top=Math.min(top,window.innerHeight-220)+'px';
  $("#ac-drop").style.left=Math.min(rect.left+20,window.innerWidth-380)+'px';
  $$("#ac-drop .ac-item").forEach(el=>el.onclick=()=>{const i=parseInt(el.dataset.i);applyAutocomplete(matches[i])});
}

function applyAutocomplete(pat){
  const ta=$("#code-input"),pos=ta.selectionStart;
  let start=pos;while(start>0&&/[a-zA-Z_]/.test(ta.value[start-1]))start--;
  const before=ta.value.slice(0,start),after=ta.value.slice(pos);
  ta.value=before+pat.text+after;ta.focus();
  const cursorPos=start+pat.sel[0];ta.selectionStart=ta.selectionEnd=cursorPos;
  if(pat.sel.length===2&&pat.sel[0]!==pat.sel[1]){ta.selectionStart=start+pat.sel[0];ta.selectionEnd=start+pat.sel[1]}
  $("#ac-drop").classList.remove('on');acVisible=false;debouncedHighlight();
}

// ── Editor event bindings ─────────────────────────
$("#code-input").addEventListener('scroll',syncEditorScroll);
$("#code-input").addEventListener('input',function(){
  if(acVisible)return;
  const pos=$("#code-input").selectionStart;
  const char=$("#code-input").value[pos-1]||'';
  if(!/[a-zA-Z_]/.test(char)){$("#ac-drop").classList.remove('on');acVisible=false;return}
  let start=pos;while(start>0&&/[a-zA-Z_]/.test($("#code-input").value[start-1]))start--;
  const word=$("#code-input").value.slice(start,pos);
  if(word.length>=2)showAutocomplete(word);else{$("#ac-drop").classList.remove('on');acVisible=false}
});
$("#code-input").addEventListener('input',debouncedHighlight);
$("#code-input").addEventListener('keydown',e=>{
  if(acVisible){
    if(e.key==='Tab'||e.key==='Enter'){e.preventDefault();const cur=$("#ac-drop .ac-item.cur");if(cur)cur.click();return}
    if(e.key==='ArrowDown'){e.preventDefault();acIdx=Math.min(acIdx+1,$$("#ac-drop .ac-item").length-1);$$("#ac-drop .ac-item").forEach((el,i)=>el.classList.toggle('cur',i===acIdx));return}
    if(e.key==='ArrowUp'){e.preventDefault();acIdx=Math.max(0,acIdx-1);$$("#ac-drop .ac-item").forEach((el,i)=>el.classList.toggle('cur',i===acIdx));return}
    if(e.key==='Escape'){e.preventDefault();$("#ac-drop").classList.remove('on');acVisible=false;return}
    $("#ac-drop").classList.remove('on');acVisible=false;
  }
  if(e.key==='Tab'){e.preventDefault();const s=$("#code-input").selectionStart;$("#code-input").value=$("#code-input").value.slice(0,s)+'    '+$("#code-input").value.slice(s);$("#code-input").selectionStart=$("#code-input").selectionEnd=s+4;debouncedHighlight()}
});
$("#code-input").addEventListener('input',function(){
  var v=$("#code-input").value,has=/scanf/.test(v)||/gets/.test(v)||/fgets/.test(v)||/getchar/.test(v);
  if(has&&!window._isRunning)$("#code-input").style.borderBottom='2px solid var(--amber)';
  else $("#code-input").style.borderBottom='';
});

// ── Formatter button ──────────────────────────────
$("#btn-fmt").onclick=()=>{const code=window.getCode();if(!code.trim())return;window.setCode(formatCode(code));toast("代码已格式化")};

// ── Initialize editor ─────────────────────────────
$("#code-input").value=DEFAULT_CODE;
updateGutter();highlight();
