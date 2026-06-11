"""
C Learn — 全局自动化测试
测试所有核心功能：编译、判题、内容加载、进度存储、API 端点
运行: python test_all.py
"""
import sys
import os
import json
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from services import (
    compile_and_run, compile_only, run_binary, judge,
    load_modules, load_exercises, load_progress, save_progress,
    CompileResult, JudgeResult, _scan_source,
)


class TestCompileAndRun(unittest.TestCase):
    """编译 + 运行 核心功能测试"""

    def test_basic_hello_world(self):
        """最基本的 Hello World 编译运行"""
        r = compile_and_run(
            '#include <stdio.h>\nint main() { printf("Hello World\\n"); return 0; }')
        self.assertTrue(r.success)
        self.assertIn("Hello World", r.stdout)
        self.assertEqual(r.exit_code, 0)
        self.assertGreater(r.wall_time_ms, 0)

    def test_empty_code(self):
        """空代码 — 编译失败"""
        r = compile_and_run("")
        self.assertFalse(r.success)

    def test_syntax_error(self):
        """语法错误 — 给出错误信息和行号"""
        r = compile_and_run('#include <stdio.h>\nint main() { printf("hi")\n }')
        self.assertFalse(r.success)
        self.assertTrue(r.compile_error or r.stderr)
        self.assertGreater(len(r.error_lines), 0)

    def test_multiline_output(self):
        """多行输出正确捕获"""
        code = '#include <stdio.h>\nint main() {\n  for(int i=1;i<=5;i++) printf("%d\\n",i);\n  return 0;\n}'
        r = compile_and_run(code)
        self.assertTrue(r.success)
        lines = r.stdout.strip().split('\n')
        self.assertEqual(len(lines), 5)

    def test_no_console_window(self):
        """确认编译和运行不弹窗（通过在非 GUI 环境测试）"""
        # 这个测试在 CI/无桌面环境运行 — 如果弹窗会挂起
        r = compile_and_run(
            '#include <stdio.h>\nint main() { return 0; }')
        self.assertTrue(r.success)


class TestJudge(unittest.TestCase):
    """判题功能测试"""

    def test_accepted_simple(self):
        """简单一次通过"""
        cases = [{"input": "", "expected_output": "hello"}]
        r = judge('#include <stdio.h>\nint main() { printf("hello"); return 0; }', cases)
        self.assertEqual(r.status, "accepted")
        self.assertEqual(r.passed_count, 1)
        self.assertEqual(r.total_count, 1)

    def test_wrong_answer(self):
        """答案错误"""
        cases = [{"input": "", "expected_output": "hello"}]
        r = judge('#include <stdio.h>\nint main() { printf("world"); return 0; }', cases)
        self.assertEqual(r.status, "wrong_answer")
        self.assertEqual(r.passed_count, 0)

    def test_compile_error(self):
        """提交代码编译错误"""
        cases = [{"input": "", "expected_output": "x"}]
        r = judge('#include <stdio.h>\nint main() { printf("x")\n }', cases)
        self.assertEqual(r.status, "compile_error")
        self.assertTrue(r.compile_error)

    def test_multiple_cases(self):
        """多测试点"""
        cases = [
            {"input": "1 2", "expected_output": "3"},
            {"input": "10 20", "expected_output": "30"},
            {"input": "-5 8", "expected_output": "3"},
        ]
        code = '#include <stdio.h>\nint main() { int a,b; scanf("%d%d",&a,&b); printf("%d",a+b); return 0; }'
        r = judge(code, cases)
        self.assertEqual(r.status, "accepted")
        self.assertEqual(r.passed_count, 3)

    def test_partial_pass(self):
        """部分通过"""
        cases = [
            {"input": "", "expected_output": "A"},
            {"input": "", "expected_output": "B"},
        ]
        code = '#include <stdio.h>\nint main() { printf("A"); return 0; }'
        r = judge(code, cases)
        self.assertEqual(r.passed_count, 1)
        self.assertEqual(r.status, "wrong_answer")


class TestSecurity(unittest.TestCase):
    """安全扫描"""

    def test_normal_code_allowed(self):
        ok, msg = _scan_source('#include <stdio.h>\nint main() { return 0; }', strict=True)
        self.assertTrue(ok)

    def test_system_blocked(self):
        """system() 在严格模式下被拦截"""
        ok, _ = _scan_source('system("rm -rf /")', strict=True)
        self.assertFalse(ok)

    def test_file_io_allowed_in_learn(self):
        """自由练习允许文件操作"""
        ok, _ = _scan_source('FILE *f = fopen("test.txt","w");', strict=False)
        self.assertTrue(ok)

    def test_fork_blocked(self):
        ok, _ = _scan_source("fork()", strict=True)
        self.assertFalse(ok)


class TestContentLoading(unittest.TestCase):
    """课程和习题加载"""

    def test_modules_load(self):
        mods = load_modules()
        self.assertGreater(len(mods), 0)
        self.assertTrue(all(hasattr(m, 'slug') for m in mods))
        self.assertTrue(all(hasattr(m, 'title') for m in mods))

    def test_exercises_load(self):
        exs = load_exercises()
        self.assertGreater(len(exs), 0)
        self.assertTrue(all(hasattr(e, 'id') for e in exs))
        self.assertTrue(all(hasattr(e, 'difficulty') for e in exs))
        self.assertTrue(all(hasattr(e, 'test_cases') for e in exs))

    def test_exercise_has_test_cases(self):
        """每个习题至少有一个测试点"""
        for ex in load_exercises():
            self.assertGreater(len(ex.test_cases), 0,
                               f"Exercise {ex.id} has no test cases")

    def test_module_levels_valid(self):
        """模块 level 在有效范围"""
        for m in load_modules():
            self.assertGreaterEqual(m.level, 1)
            self.assertLessEqual(m.level, 30)


class TestProgress(unittest.TestCase):
    """进度存储"""

    def setUp(self):
        self._test_slug = "__test_progress__"
        save_progress(self._test_slug, "passed", "print('test')")

    def test_save_and_load(self):
        p = load_progress()
        self.assertIn(self._test_slug, p)
        self.assertEqual(p[self._test_slug]["status"], "passed")
        self.assertEqual(p[self._test_slug]["last_code"], "print('test')")

    def test_overwrite(self):
        save_progress(self._test_slug, "failed", "bad code")
        p = load_progress()
        self.assertEqual(p[self._test_slug]["status"], "failed")

    def tearDown(self):
        # Clean up test entry
        p = load_progress()
        p.pop(self._test_slug, None)
        import json as _json
        with open(Path(__file__).parent / "progress.json", "w") as f:
            _json.dump(p, f, ensure_ascii=False, indent=2)


class TestCompileOnly(unittest.TestCase):
    """compile_only + run_binary"""

    def test_compile_and_run_separate(self):
        ok, binary, err = compile_only(
            '#include <stdio.h>\nint main() { printf("42"); return 0; }')
        self.assertTrue(ok, f"Compile failed: {err}")
        self.assertTrue(os.path.exists(binary))

        r = run_binary(binary)
        self.assertTrue(r.success)
        self.assertIn("42", r.stdout)

        # Clean up
        import shutil
        shutil.rmtree(Path(binary).parent, ignore_errors=True)

    def test_compile_error_separate(self):
        ok, _, err = compile_only(
            '#include <stdio.h>\nint main() { printf("x")\n }')
        self.assertFalse(ok)
        self.assertTrue(err)


class TestServerAPI(unittest.TestCase):
    """Flask API 端点测试 (需要服务器运行)"""

    @classmethod
    def setUpClass(cls):
        from server import app, start_server
        cls._url = start_server(port=18765)
        time.sleep(0.3)
        cls.client = app.test_client()

    def test_health(self):
        r = self.client.get("/api/health")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["status"], "ok")

    def test_modules(self):
        r = self.client.get("/api/modules")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertIsInstance(data, list)
        if data:
            self.assertIn("slug", data[0])
            self.assertIn("title", data[0])

    def test_exercises(self):
        r = self.client.get("/api/exercises")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertIsInstance(data, list)
        if data:
            self.assertIn("id", data[0])
            self.assertIn("difficulty", data[0])

    def test_progress(self):
        r = self.client.get("/api/progress")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertIn("solved", data)
        self.assertIn("total", data)

    def test_run_api_success(self):
        r = self.client.post("/api/run",
                             json={"code": '#include <stdio.h>\nint main() { printf("api-test"); return 0; }'})
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertTrue(data["success"])
        self.assertIn("api-test", data["stdout"])

    def test_run_api_error(self):
        r = self.client.post("/api/run",
                             json={"code": '#include <stdio.h>\nint main() { printf("x")\n }'})
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertFalse(data["success"])
        self.assertTrue(data.get("compile_error") or data.get("stderr"))

    def test_submit_api(self):
        exs = load_exercises()
        if not exs:
            self.skipTest("No exercises available")
        ex = exs[0]
        r = self.client.post("/api/submit", json={
            "code": ex.solution_code or ex.template_code or "int main(){return 0;}",
            "exercise_id": ex.id,
        })
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertIn("status", data)
        self.assertIn("passed_count", data)

    def test_exercise_detail(self):
        exs = load_exercises()
        if not exs:
            self.skipTest("No exercises available")
        r = self.client.get(f"/api/exercise/{exs[0].id}")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertIn("title", data)
        self.assertIn("description_md", data)

    def test_index_html(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn("C 语言学习平台", r.get_data(as_text=True))

    def test_static_html(self):
        """前端 HTML 结构正确，引用外部 CSS/JS"""
        r = self.client.get("/")
        html = r.get_data(as_text=True)
        self.assertIn("C 语言学习平台", html)
        self.assertIn('<link rel="stylesheet" href="/style.css">', html)
        self.assertIn('src="/js/app.js', html)  # v4.1: modular JS

    def test_static_css_file(self):
        """style.css 独立文件可访问，包含主题变量和语法高亮配色"""
        r = self.client.get("/style.css")
        self.assertEqual(r.status_code, 200)
        css = r.get_data(as_text=True)
        self.assertIn("--accent", css)
        self.assertIn("--btn-h", css)
        self.assertIn("focus-visible", css)
        self.assertIn("hl-kw", css)  # syntax highlight token

    def test_static_js_files(self):
        """v4.1: 模块化 JS 文件全部可访问，核心函数分布在各个模块中"""
        files_checks = {
            "/js/utils.js": ["esc", "formatCode", "checkAchievements", "exportProgress", "md2html"],
            "/js/editor.js": ["tokenizeLine", "debouncedHighlight", "saveCodeHistory", "showAutocomplete", "_historyKey"],
            "/js/course.js": ["buildCourseTree", "openModule", "showWelcome", "_showFreeMode"],
            "/js/viz.js": ["showVizPanel", "vizLoadCode", "vizRefresh", "EXAMPLES_CODE"],
            "/js/app.js": ["toggleSidebar", "showOnboarding", "_mode", "toggleShortcuts"],
        }
        for path, expected in files_checks.items():
            r = self.client.get(path)
            self.assertEqual(r.status_code, 200, f"{path} should be accessible")
            js = r.get_data(as_text=True)
            for name in expected:
                self.assertIn(name, js, f"{name} should be in {path}")


class TestSimulator(unittest.TestCase):
    """v9: 模拟器功能测试 (基础 + v2 控制流)"""

    def setUp(self):
        from simulator import CSimulator
        self.sim = CSimulator("""#include <stdio.h>

int main() {
    int a = 5;
    int *p = &a;
    *p = 10;
    printf("%d", a);
    return 0;
}""")

    def test_init_state(self):
        """初始状态：未执行，无输出"""
        state = self.sim._get_state()
        self.assertEqual(state["output"], "")
        self.assertFalse(state["finished"])
        self.assertGreater(len(self.sim._lines), 0)  # 代码已解析

    def test_step_creates_variables(self):
        """逐步执行会创建变量"""
        # Step through function entry and variable declarations
        for _ in range(4):  # func_def, skip, var_decl_init x2, skip
            self.sim.step()
        state = self.sim._get_state()
        var_names = [v["name"] for v in state["variables"]]
        self.assertIn("a", var_names)

    def test_pointer_deref(self):
        """*p = 10 会修改 a 的值"""
        state = self.sim.run_all()
        self.assertIn("10", state["output"])
        self.assertTrue(state["finished"])

    def test_reset(self):
        """重置回到初始状态"""
        self.sim.run_all()
        self.sim.reset()
        state = self.sim._get_state()
        self.assertEqual(len(state["variables"]), 0)
        self.assertFalse(state["finished"])

    def test_step_back(self):
        """回退一步"""
        self.sim.step()  # func_def
        self.sim.step()  # skip (include)
        self.sim.step()  # var_decl_init: a=5
        before = self.sim._get_state()
        self.sim.step()  # another step
        after = self.sim._get_state()
        self.assertNotEqual(before["current_line"], after["current_line"])
        # step back
        back = self.sim.step_back()
        self.assertEqual(back["current_line"], before["current_line"])

    def test_example_loads(self):
        """内置示例可加载"""
        from simulator import EXAMPLES
        self.assertIn("pointer_basics", EXAMPLES)
        self.assertIn("function_pointer", EXAMPLES)
        self.assertIn("array_pointer", EXAMPLES)
        # v2: new control flow examples
        self.assertIn("if_else", EXAMPLES)
        self.assertIn("while_loop", EXAMPLES)
        self.assertIn("for_loop", EXAMPLES)
        from simulator import CSimulator
        for key in EXAMPLES:
            sim = CSimulator(EXAMPLES[key]["code"])
            state = sim._get_state()
            self.assertIsNotNone(state)

    # ── v2 控制流测试 ──────────────────────────────

    def test_if_else_true_branch(self):
        """if/else — 条件为真时执行 then 分支"""
        from simulator import CSimulator
        sim = CSimulator("""#include <stdio.h>
int main() {
    int a = 10;
    if (a > 5) {
        printf("big");
    } else {
        printf("small");
    }
    return 0;
}""")
        state = sim.run_all()
        self.assertIn("big", state["output"])
        self.assertNotIn("small", state["output"])

    def test_if_else_false_branch(self):
        """if/else — 条件为假时执行 else 分支"""
        from simulator import CSimulator
        sim = CSimulator("""#include <stdio.h>
int main() {
    int a = 3;
    if (a > 5) {
        printf("big");
    } else {
        printf("small");
    }
    return 0;
}""")
        state = sim.run_all()
        self.assertIn("small", state["output"])
        self.assertNotIn("big", state["output"])

    def test_while_loop(self):
        """while 循环正确迭代"""
        from simulator import CSimulator
        sim = CSimulator("""#include <stdio.h>
int main() {
    int i = 0;
    while (i < 3) {
        printf("%d", i);
        i = i + 1;
    }
    return 0;
}""")
        state = sim.run_all()
        self.assertIn("012", state["output"])

    def test_for_loop(self):
        """for 循环正确迭代并求和"""
        from simulator import CSimulator
        sim = CSimulator("""#include <stdio.h>
int main() {
    int sum = 0;
    for (int i = 1; i <= 3; i = i + 1) {
        sum = sum + i;
    }
    printf("%d", sum);
    return 0;
}""")
        state = sim.run_all()
        self.assertIn("6", state["output"])

    def test_nested_if(self):
        """嵌套 if — 内层条件判断正确"""
        from simulator import CSimulator
        sim = CSimulator("""#include <stdio.h>
int main() {
    int a = 10;
    if (a > 5) {
        if (a > 8) {
            printf("big");
        }
    }
    return 0;
}""")
        state = sim.run_all()
        self.assertIn("big", state["output"])

    def test_step_back_after_jump(self):
        """控制流跳转后 step_back 正确恢复"""
        from simulator import CSimulator
        sim = CSimulator("""#include <stdio.h>
int main() {
    int a = 3;
    if (a > 5) {
        printf("big");
    } else {
        printf("small");
    }
    return 0;
}""")
        for _ in range(6):
            sim.step()
        state_before = sim._get_state()
        sim.step()
        state_after = sim._get_state()
        self.assertNotEqual(state_before["current_line"], state_after["current_line"])
        back = sim.step_back()
        self.assertEqual(back["current_line"], state_before["current_line"])

    # ── v3 控制流测试 ──────────────────────────────

    def test_do_while_always_executes_once(self):
        """do-while 循环体至少执行一次（即使条件为假）"""
        from simulator import CSimulator
        sim = CSimulator("""#include <stdio.h>
int main() {
    int i = 5;
    do {
        printf("run");
        i = i + 1;
    } while (i < 3);
    return 0;
}""")
        state = sim.run_all()
        self.assertIn("run", state["output"])

    def test_break_exits_loop(self):
        """break 正确跳出 while 循环"""
        from simulator import CSimulator
        sim = CSimulator("""#include <stdio.h>
int main() {
    int i = 0;
    while (i < 10) {
        i = i + 1;
        if (i == 3) {
            break;
        }
        printf("%d", i);
    }
    return 0;
}""")
        state = sim.run_all()
        # Should print 1 and 2, then break before printing 3
        self.assertIn("1", state["output"])
        self.assertIn("2", state["output"])
        self.assertNotIn("3", state["output"])

    def test_continue_skips_iteration(self):
        """continue 跳过当前迭代"""
        from simulator import CSimulator
        sim = CSimulator("""#include <stdio.h>
int main() {
    int i = 0;
    while (i < 5) {
        i = i + 1;
        if (i == 3) {
            continue;
        }
        printf("%d", i);
    }
    return 0;
}""")
        state = sim.run_all()
        self.assertIn("1", state["output"])
        self.assertIn("2", state["output"])
        self.assertIn("4", state["output"])
        self.assertIn("5", state["output"])
        self.assertNotIn("3", state["output"])

    def test_switch_case_matching(self):
        """switch/case 正确匹配并执行对应分支"""
        from simulator import CSimulator
        sim = CSimulator("""#include <stdio.h>
int main() {
    int x = 2;
    switch (x) {
        case 1:
            printf("one");
            break;
        case 2:
            printf("two");
            break;
        case 3:
            printf("three");
            break;
        default:
            printf("other");
    }
    return 0;
}""")
        state = sim.run_all()
        self.assertIn("two", state["output"])
        self.assertNotIn("one", state["output"])
        self.assertNotIn("three", state["output"])

    def test_switch_default_fallback(self):
        """switch 无匹配时进入 default"""
        from simulator import CSimulator
        sim = CSimulator("""#include <stdio.h>
int main() {
    int x = 99;
    switch (x) {
        case 1:
            printf("one");
            break;
        default:
            printf("other");
    }
    return 0;
}""")
        state = sim.run_all()
        self.assertIn("other", state["output"])


class TestSecurityRegex(unittest.TestCase):
    """v2: 安全扫描器 — 正则词边界测试"""

    def test_word_boundary_systematic(self):
        """'systematic' 不应触发 system( 拦截（词边界保护）"""
        ok, _ = _scan_source('int systematic = 1;', strict=True)
        self.assertTrue(ok, "'systematic' should NOT be blocked by word boundary")

    def test_actual_system_call_blocked(self):
        """'system(\"rm\")' 应被拦截"""
        ok, msg = _scan_source('system("rm -rf /");', strict=True)
        self.assertFalse(ok)
        self.assertIn("system(", msg)

    def test_asm_keyword_blocked(self):
        """__asm 应被严格/宽松模式拦截"""
        ok, _ = _scan_source("__asm { mov eax, 1 }", strict=True)
        self.assertFalse(ok)
        ok2, _ = _scan_source("__asm { mov eax, 1 }", strict=False)
        self.assertFalse(ok2)

    def test_syscall_blocked(self):
        """syscall() 原始系统调用应被拦截"""
        ok, _ = _scan_source("syscall(59, ...);", strict=True)
        self.assertFalse(ok)

    def test_normal_code_still_works(self):
        """正常 C 代码在各种扫描模式下都能通过"""
        normal = '#include <stdio.h>\nint main() {\n    printf("assembly language is fun");\n    return 0;\n}'
        ok, _ = _scan_source(normal, strict=True)
        self.assertTrue(ok)
        ok2, _ = _scan_source(normal, strict=False)
        self.assertTrue(ok2)


class TestConfig(unittest.TestCase):
    """v2: 配置系统测试"""

    def test_config_defaults(self):
        """配置默认值存在且合理"""
        from services import CONFIG
        self.assertGreater(CONFIG["compile_timeout"], 0)
        self.assertGreater(CONFIG["run_timeout"], 0)
        self.assertGreater(CONFIG["free_run_timeout"], 0)
        self.assertGreater(CONFIG["max_stdout"], 0)
        self.assertGreater(CONFIG["max_stderr"], 0)
        self.assertFalse(CONFIG["strict_free_play"])  # default off


class TestVizExamplesAPI(unittest.TestCase):
    """v2: 可视化示例 API 测试"""

    @classmethod
    def setUpClass(cls):
        from server import app
        cls.client = app.test_client()

    def test_all_9_examples_listed(self):
        """9 个示例全部在列表中"""
        r = self.client.get("/api/sim/examples")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(len(data), 9)
        ids = [e["id"] for e in data]
        for expected in ["pointer_basics", "function_pointer", "array_pointer",
                         "if_else", "while_loop", "for_loop",
                         "do_while", "break_continue", "switch_case"]:
            self.assertIn(expected, ids, f"Example {expected} missing from list")

    def test_if_else_example_loads(self):
        """if/else 示例可加载"""
        r = self.client.get("/api/sim/example/if_else")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertIn("title", data)
        self.assertEqual(data["title"], "例4 - if/else 条件判断")

    def test_while_loop_example_loads(self):
        """while 循环示例可加载"""
        r = self.client.get("/api/sim/example/while_loop")
        self.assertEqual(r.status_code, 200)

    def test_for_loop_example_loads(self):
        """for 循环示例可加载"""
        r = self.client.get("/api/sim/example/for_loop")
        self.assertEqual(r.status_code, 200)


class TestSimulatorV4(unittest.TestCase):
    """v4.1: step_back 变量恢复 + 逻辑运算符回归测试"""

    def test_step_back_restores_variable_value(self):
        """step_back 正确恢复变量值（回归测试）"""
        from simulator import CSimulator
        sim = CSimulator("""#include <stdio.h>
int main() {
    int a = 5;
    a = 10;
    printf("%d", a);
    return 0;
}""")
        # Step to a=5 then a=10
        for _ in range(4):
            sim.step()
        state = sim._get_state()
        var_vals = {v["name"]: v["value"] for v in state["variables"]}
        self.assertEqual(var_vals.get("a"), "10", "a should be 10 after a=10")

        # Step back should restore a=5
        back = sim.step_back()
        var_vals_back = {v["name"]: v["value"] for v in back["variables"]}
        self.assertEqual(var_vals_back.get("a"), "5",
                         "step_back MUST restore a to 5 (was 10)")

    def test_step_back_multiple_steps(self):
        """连续多步回退正确"""
        from simulator import CSimulator
        sim = CSimulator("""#include <stdio.h>
int main() {
    int x = 1;
    x = 2;
    x = 3;
    printf("%d", x);
    return 0;
}""")
        for _ in range(6):
            sim.step()
        state = sim._get_state()
        self.assertEqual({v["name"]: v["value"] for v in state["variables"]}.get("x"), "3")
        # Back 3 times: should go to x=1
        for _ in range(3):
            sim.step_back()
        back = sim._get_state()
        self.assertEqual({v["name"]: v["value"] for v in back["variables"]}.get("x"), "1")

    def test_and_operator(self):
        """&& 逻辑与"""
        from simulator import CSimulator
        sim = CSimulator("""#include <stdio.h>
int main() {
    int a = 5;
    int b = 10;
    if (a > 0 && b > 5) {
        printf("both");
    }
    return 0;
}""")
        state = sim.run_all()
        self.assertIn("both", state["output"])

    def test_or_operator(self):
        """|| 逻辑或"""
        from simulator import CSimulator
        sim = CSimulator("""#include <stdio.h>
int main() {
    int a = 5;
    if (a > 10 || a < 10) {
        printf("either");
    }
    return 0;
}""")
        state = sim.run_all()
        self.assertIn("either", state["output"])

    def test_not_operator(self):
        """! 逻辑非"""
        from simulator import CSimulator
        sim = CSimulator("""#include <stdio.h>
int main() {
    int a = 5;
    if (!(a > 10)) {
        printf("not");
    }
    return 0;
}""")
        state = sim.run_all()
        self.assertIn("not", state["output"])

    def test_complex_condition(self):
        """复合条件: && + || + ()"""
        from simulator import CSimulator
        sim = CSimulator("""#include <stdio.h>
int main() {
    int a = 5;
    int b = 0;
    if ((a > 0 && b == 0) || a > 10) {
        printf("complex");
    }
    return 0;
}""")
        state = sim.run_all()
        self.assertIn("complex", state["output"])


class TestInteractiveRunner(unittest.TestCase):
    """v4.1: 交互式运行器基础测试"""

    def test_start_and_kill(self):
        """启动和终止交互式进程"""
        from services import InteractiveRunner
        runner = InteractiveRunner()
        result = runner.start('#include <stdio.h>\nint main() { printf("hi"); return 0; }')
        self.assertIn(result["status"], ["started", "compile_error"],
                      f"Expected started or compile_error, got {result['status']}")
        if result["status"] == "started":
            # Wait briefly for output
            import time
            time.sleep(0.3)
            poll = runner.poll()
            self.assertTrue(poll["running"] or poll["exit_code"] is not None)
            runner.kill()

    def test_compile_error(self):
        """交互式运行编译错误"""
        from services import InteractiveRunner
        runner = InteractiveRunner()
        result = runner.start('#include <stdio.h>\nint main() { printf("x")\n }')
        self.assertEqual(result["status"], "compile_error")
        self.assertTrue(result.get("error"))


if __name__ == "__main__":
    print("=" * 60)
    print("C Learn — 全局自动化测试")
    print(f"时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Run tests
    unittest.main(verbosity=2)
