// ============================================================
// C Learn — viz.js (v4.1 modular)
// Code visualization panel: simulator interaction + examples
// ============================================================

const EXAMPLES_CODE={
  pointer_basics:'#include <stdio.h>\n\nint main() {\n    int a = 5;\n    int b = 10;\n    int *p = &a;\n\n    printf("a = %d\\n", a);\n    *p = 20;\n    printf("a = %d\\n", a);\n\n    p = &b;\n    printf("*p = %d\\n", *p);\n    return 0;\n}',
  function_pointer:'#include <stdio.h>\n\nvoid swap(int *x, int *y) {\n    int temp = *x;\n    *x = *y;\n    *y = temp;\n}\n\nint main() {\n    int a = 5;\n    int b = 10;\n\n    printf("before: a=%d b=%d\\n", a, b);\n    swap(&a, &b);\n    printf("after:  a=%d b=%d\\n", a, b);\n    return 0;\n}',
  array_pointer:'#include <stdio.h>\n\nint main() {\n    int arr[3] = {10, 20, 30};\n    int *p = arr;\n\n    printf("arr[0] = %d\\n", arr[0]);\n    printf("*p = %d\\n", *p);\n\n    p = p + 1;\n    printf("*p = %d\\n", *p);\n\n    *p = 99;\n    printf("arr[1] = %d\\n", arr[1]);\n    return 0;\n}',
  if_else:'#include <stdio.h>\n\nint main() {\n    int a = 5;\n\n    if (a > 3) {\n        printf("a > 3\\n");\n    } else {\n        printf("a <= 3\\n");\n    }\n\n    a = 2;\n    if (a > 3) {\n        printf("big\\n");\n    } else {\n        printf("small\\n");\n    }\n    return 0;\n}',
  while_loop:'#include <stdio.h>\n\nint main() {\n    int i = 0;\n\n    while (i < 3) {\n        printf("i = %d\\n", i);\n        i = i + 1;\n    }\n    return 0;\n}',
  for_loop:'#include <stdio.h>\n\nint main() {\n    int sum = 0;\n\n    for (int i = 1; i <= 3; i = i + 1) {\n        sum = sum + i;\n    }\n    printf("sum = %d\\n", sum);\n    return 0;\n}',
};

let _vizSource='';

function showVizPanel(){
  $("#sidebar").style.display="none";$("#center").style.display="none";$("#right").style.display="none";
  $$('.grip').forEach(g=>g.style.display='none');$$('.grip-v').forEach(g=>g.style.display='none');
  $("#viz-panel").classList.add('on');
}
window._hideVizPanel=function(){
  $("#sidebar").style.display="";$("#center").style.display="";$("#right").style.display="";
  $$('.grip').forEach(g=>{if(!g.classList.contains('collapsed'))g.style.display=''});
  $$('.grip-v').forEach(g=>g.style.display='');
  $("#viz-panel").classList.remove('on');
};

async function vizLoadCode(code){
  const r=await api("/api/sim/load",{method:"POST",body:JSON.stringify({code})});
  if(r.error){toast(r.error,"err");return}
  _vizSource=code;vizRefresh(r);
}
async function vizStep(){const r=await api("/api/sim/step",{method:"POST"});vizRefresh(r)}
async function vizBack(){const r=await api("/api/sim/back",{method:"POST"});vizRefresh(r)}
async function vizReset(){const r=await api("/api/sim/reset",{method:"POST"});vizRefresh(r)}
async function vizRunAll(){const r=await api("/api/sim/run",{method:"POST"});vizRefresh(r)}

function vizRefresh(r){
  if(!r||r.error)return;
  const lines=(_vizSource||$("#viz-code").textContent||"").split('\n');
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

// ── Viz button bindings ───────────────────────────
$("#viz-load").onclick=()=>vizLoadCode($("#viz-code").textContent||EXAMPLES_CODE.pointer_basics);
$("#viz-next").onclick=vizStep;$("#viz-prev").onclick=vizBack;$("#viz-reset").onclick=vizReset;$("#viz-runall").onclick=vizRunAll;

function _loadExample(key){
  const c=EXAMPLES_CODE[key];$("#viz-code").textContent=c;vizLoadCode(c);
}
$("#viz-ex1").onclick=()=>_loadExample('pointer_basics');
$("#viz-ex2").onclick=()=>_loadExample('function_pointer');
$("#viz-ex3").onclick=()=>_loadExample('array_pointer');
$("#viz-ex4").onclick=()=>_loadExample('if_else');
$("#viz-ex5").onclick=()=>_loadExample('while_loop');
$("#viz-ex6").onclick=()=>_loadExample('for_loop');
$("#viz-custom").onclick=()=>{const c=window.getCode();if(!c.trim()){toast("请先在编辑器中编写代码","warn");return}$("#viz-code").textContent=c;vizLoadCode(c);toast("已加载编辑器中的代码")};
