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

    def test_static_css(self):
        """验证前端 HTML 包含完整 CSS"""
        r = self.client.get("/")
        html = r.get_data(as_text=True)
        self.assertIn("font-family", html)
        self.assertIn("var(--accent)", html)


if __name__ == "__main__":
    print("=" * 60)
    print("C Learn — 全局自动化测试")
    print(f"时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Run tests
    unittest.main(verbosity=2)
