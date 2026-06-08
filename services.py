"""
Sync services for the C Learn desktop app.

Wraps TCC compilation and exercise judging in synchronous functions
suitable for a tkinter GUI (runs in background thread).
"""
import os
import sys
import re
import subprocess
import tempfile
import time
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ── Path resolution (dev + PyInstaller) ──────────────────────────
def _base_dir() -> Path:
    """Get the project root, handling PyInstaller _MEIPASS."""
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS)
    return Path(__file__).parent  # services.py is at project root

def _tcc_exe() -> Optional[str]:
    """Find TCC executable."""
    candidates = [
        _base_dir() / "tools" / "tcc" / "tcc.exe",
        _base_dir() / "tools" / "tcc" / "tcc",
    ]
    for p in candidates:
        if p.exists():
            return str(p)
    # Try PATH
    import shutil
    for name in ["tcc", "tcc.exe"]:
        if shutil.which(name):
            return name
    return None

def _content_dir() -> Path:
    return _base_dir() / "content"

# ── Compile result ────────────────────────────────────────────────

@dataclass
class CompileResult:
    success: bool
    stdout: str = ""
    stderr: str = ""
    compile_error: str = ""
    exit_code: int = -1
    wall_time_ms: int = 0
    error_lines: list = field(default_factory=list)

# ── Judge result ──────────────────────────────────────────────────

@dataclass
class TestCaseResult:
    case_index: int
    passed: bool
    input: str
    expected: str
    actual: str
    error: str = ""
    wall_time_ms: int = 0

@dataclass
class JudgeResult:
    status: str  # "accepted" | "wrong_answer" | "compile_error" | "runtime_error" | "timeout"
    passed_count: int
    total_count: int
    test_results: list = field(default_factory=list)
    compile_error: str = ""
    wall_time_ms: int = 0

# ── Security scanner ──────────────────────────────────────────────

# Strict scan for exercise submission — blocks dangerous syscalls
_FORBIDDEN_STRICT = [
    "system(", "popen(", "exec(", "fork(", "CreateProcess",
    "WinExec", "ShellExecute", "socket(", "connect(",
    "__asm", "__asm__", "#include <winsock",
]

# Relaxed scan for free play — only blocks truly destructive ops
# NOTE: fopen/remove/fwrite are NOT blocked — they're needed for file I/O exercises
_FORBIDDEN_RELAXED = [
    "system(", "CreateProcess", "WinExec", "ShellExecute",
    "__asm", "__asm__",
]

# Windows: suppress console window for subprocess calls
_CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0
_STARTUP_INFO = None
if os.name == "nt":
    _STARTUP_INFO = subprocess.STARTUPINFO()
    _STARTUP_INFO.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    _STARTUP_INFO.wShowWindow = subprocess.SW_HIDE

def _subprocess_kwargs(**extra):
    """Return kwargs for subprocess.run that completely suppress console windows."""
    kw = {}
    if os.name == "nt":
        kw["creationflags"] = _CREATE_NO_WINDOW
        if _STARTUP_INFO is not None:
            kw["startupinfo"] = _STARTUP_INFO
    kw.update(extra)
    return kw

def _scan_source(source: str, strict: bool = False) -> tuple[bool, str]:
    """Security scan. strict=True for exercise submission, False for free play."""
    lower = source.lower()
    keywords = _FORBIDDEN_STRICT if strict else _FORBIDDEN_RELAXED
    blocks = []
    for kw in keywords:
        if kw.lower() in lower:
            blocks.append(kw)
    if blocks:
        return False, f"Code blocked: {', '.join(blocks[:3])} not allowed in this context."
    return True, ""

# ── Compilation ───────────────────────────────────────────────────

_PER_CASE_TIMEOUT = 5  # seconds per test case

def compile_and_run(source_code: str, stdin: str = "", timeout: int = 10) -> CompileResult:
    """
    Compile C code with TCC and run it. Returns CompileResult.
    Runs synchronously — call from a background thread to keep UI responsive.
    """
    safe, msg = _scan_source(source_code, strict=False)  # relaxed for free play
    if not safe:
        return CompileResult(success=False, compile_error=msg)

    tcc = _tcc_exe()
    if not tcc:
        return CompileResult(
            success=False,
            compile_error=(
                "TCC compiler not found.\n\n"
                "Expected at: tools/tcc/tcc.exe\n"
                "Download: https://download.savannah.gnu.org/releases/tinycc/"
            ),
        )

    t0 = time.time()
    tmpdir = tempfile.mkdtemp(prefix="clearn_")
    ext = ".exe" if os.name == "nt" else ".out"
    binary = str(Path(tmpdir) / f"a{ext}")
    try:
        src = Path(tmpdir) / "main.c"
        src.write_text(source_code, encoding="utf-8")

        # Step 1: Compile only (no -run, so no console flash)
        compile_proc = subprocess.run(
            [tcc, "-std=c11", "-o", binary, str(src)],
            capture_output=True,
            timeout=15,
            text=True,
            **_subprocess_kwargs(),
        )

        raw_stderr = compile_proc.stderr[:5000] if compile_proc.stderr else ""
        clean_stderr = re.sub(
            r'[A-Z]:[^\s]*?/main\.c:\d+: ',
            '',
            raw_stderr
        ).strip()

        if compile_proc.returncode != 0:
            elapsed_ms = int((time.time() - t0) * 1000)
            return CompileResult(
                success=False,
                compile_error=_translate_error(clean_stderr or "Compilation failed"),
                exit_code=compile_proc.returncode,
                wall_time_ms=elapsed_ms,
                error_lines=_parse_error_lines(raw_stderr),
            )

        # Step 2: Run the compiled binary (no console window)
        run_proc = subprocess.run(
            [binary],
            input=stdin,
            capture_output=True,
            timeout=timeout,
            text=True,
            **_subprocess_kwargs(),
        )
        elapsed_ms = int((time.time() - t0) * 1000)
        stdout = run_proc.stdout[:10000] if run_proc.stdout else ""
        stderr_out = run_proc.stderr[:5000] if run_proc.stderr else ""

        error_lines = _parse_error_lines(stderr_out) if run_proc.returncode != 0 else []

        return CompileResult(
            success=(run_proc.returncode == 0),
            stdout=stdout,
            stderr=stderr_out,
            compile_error="",
            exit_code=run_proc.returncode or 0,
            wall_time_ms=elapsed_ms,
            error_lines=error_lines,
        )
    except subprocess.TimeoutExpired:
        return CompileResult(
            success=False,
            stderr=f"Execution timed out after {timeout}s",
            exit_code=-1,
            wall_time_ms=timeout * 1000,
        )
    except FileNotFoundError:
        return CompileResult(success=False, compile_error="TCC compiler not found")
    except Exception as e:
        return CompileResult(success=False, compile_error=f"Error: {str(e)}")
    finally:
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)


def compile_only(source_code: str) -> tuple[bool, str, str]:
    """
    Compile to a temp binary. Returns (success, binary_path, error_message).
    """
    safe, msg = _scan_source(source_code, strict=True)  # strict for submission
    if not safe:
        return False, "", msg

    tcc = _tcc_exe()
    if not tcc:
        return False, "", "TCC compiler not found"

    tmpdir = tempfile.mkdtemp(prefix="clearn_")
    ext = ".exe" if os.name == "nt" else ".out"
    binary = str(Path(tmpdir) / f"a{ext}")
    src = Path(tmpdir) / "main.c"
    src.write_text(source_code, encoding="utf-8")

    try:
        proc = subprocess.run(
            [tcc, "-std=c11", "-o", binary, str(src)],
            capture_output=True,
            timeout=15,
            text=True,
            **_subprocess_kwargs(),
        )
        if proc.returncode != 0:
            raw = proc.stderr[:5000] if proc.stderr else ""
            clean = re.sub(r'[A-Z]:[^\s]*?/main\.c:\d+: ', '', raw).strip()
            # Clean up on failure
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)
            return False, "", _translate_error(clean or f"Compilation failed")
        return True, binary, ""
    except subprocess.TimeoutExpired:
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)
        return False, "", "Compilation timed out"
    except Exception as e:
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)
        return False, "", str(e)


def run_binary(binary_path: str, stdin: str = "", timeout: int = _PER_CASE_TIMEOUT) -> CompileResult:
    """Run a pre-compiled binary with stdin."""
    t0 = time.time()
    try:
        proc = subprocess.run(
            [binary_path],
            input=stdin,
            capture_output=True,
            timeout=timeout,
            text=True,
            **_subprocess_kwargs(),
        )
        elapsed_ms = int((time.time() - t0) * 1000)
        return CompileResult(
            success=(proc.returncode == 0),
            stdout=proc.stdout[:10000] if proc.stdout else "",
            stderr=proc.stderr[:5000] if proc.stderr else "",
            exit_code=proc.returncode or 0,
            wall_time_ms=elapsed_ms,
        )
    except subprocess.TimeoutExpired:
        return CompileResult(
            success=False,
            stderr=f"Execution timed out after {timeout}s",
            exit_code=-1,
            wall_time_ms=timeout * 1000,
        )
    except Exception as e:
        return CompileResult(success=False, stderr=f"Error: {str(e)}", exit_code=-1)


# ── Judge (compile once, run N test cases) ─────────────────────────

def judge(source_code: str, test_cases: list[dict], timeout: int = _PER_CASE_TIMEOUT) -> JudgeResult:
    """
    Compile once, run against all test cases. Returns structured JudgeResult.
    """
    if not test_cases:
        return JudgeResult(status="accepted", passed_count=0, total_count=0)

    t_start = time.time()

    # Compile
    ok, binary, err = compile_only(source_code)
    if not ok:
        hint = ""
        if "undeclared" in err.lower():
            hint = "\n\nHint: Check for typos in variable names or missing #include directives."
        elif "expected" in err.lower() and (";" in err or "}" in err):
            hint = "\n\nHint: Check for missing semicolons (;) or braces ({})."
        elif "main" in err.lower():
            hint = "\n\nHint: Every C program needs an 'int main() { ... }' function."
        return JudgeResult(
            status="compile_error",
            passed_count=0,
            total_count=len(test_cases),
            compile_error=err + (hint if hint else ""),
            wall_time_ms=int((time.time() - t_start) * 1000),
        )

    # Sort cases — simple first
    sorted_cases = sorted(
        enumerate(test_cases),
        key=lambda x: len(str(x[1].get("input", "")))
    )

    results = []
    passed = 0
    has_timeout = False
    first_failure_seen = False

    for original_idx, tc in sorted_cases:
        if first_failure_seen:
            # Still record remaining cases as skipped for transparency
            results.append(TestCaseResult(
                case_index=original_idx,
                passed=False,
                input=tc.get("input", ""),
                expected=tc.get("expected_output", "").strip(),
                actual="",
                error="Skipped (previous case failed)",
            ))
            continue

        inp = tc.get("input", "")
        expected = tc.get("expected_output", "").strip()

        run_result = run_binary(binary, inp, timeout=timeout)

        if run_result.stderr and "timed out" in run_result.stderr.lower():
            has_timeout = True
            results.append(TestCaseResult(
                case_index=original_idx, passed=False,
                input=inp, expected=expected, actual="",
                error=f"Time Limit Exceeded ({timeout}s)",
                wall_time_ms=run_result.wall_time_ms,
            ))
            first_failure_seen = True
            continue

        if run_result.exit_code != 0:
            err_detail = run_result.stderr[:300] if run_result.stderr else f"Exit code {run_result.exit_code}"
            results.append(TestCaseResult(
                case_index=original_idx, passed=False,
                input=inp, expected=expected,
                actual=run_result.stdout.strip()[:500],
                error=f"Runtime Error: {err_detail}",
                wall_time_ms=run_result.wall_time_ms,
            ))
            first_failure_seen = True
            continue

        actual = run_result.stdout.strip()
        actual_norm = '\n'.join(line.rstrip() for line in actual.split('\n'))
        expected_norm = '\n'.join(line.rstrip() for line in expected.split('\n'))
        is_pass = (actual_norm == expected_norm)

        if is_pass:
            passed += 1
        else:
            first_failure_seen = True

        results.append(TestCaseResult(
            case_index=original_idx,
            passed=is_pass,
            input=inp,
            expected=expected,
            actual=actual,
            wall_time_ms=run_result.wall_time_ms,
        ))

    # Clean up
    try:
        import shutil
        shutil.rmtree(Path(binary).parent, ignore_errors=True)
    except Exception:
        pass

    # Overall status
    if has_timeout and passed == 0:
        overall = "timeout"
    elif passed == len(test_cases):
        overall = "accepted"
    else:
        overall = "wrong_answer"

    # Build frontend-safe results (show expected only for first failure)
    frontend_results = []
    first_failure_shown = False
    for r in results:
        item = {
            "case": r.case_index + 1,
            "passed": r.passed,
            "input": r.input,
            "wall_time_ms": r.wall_time_ms,
        }
        if r.error:
            item["error"] = r.error
        if r.passed:
            item["actual"] = r.actual[:200] if r.actual else ""
        else:
            item["actual"] = r.actual[:500] if r.actual else "(no output)"
            if not first_failure_shown:
                item["expected"] = r.expected[:500]
                first_failure_shown = True
        frontend_results.append(item)

    return JudgeResult(
        status=overall,
        passed_count=passed,
        total_count=len(test_cases),
        test_results=frontend_results,
        wall_time_ms=int((time.time() - t_start) * 1000),
    )


# ── Error message translation ─────────────────────────────────────

def _translate_error(raw: str) -> str:
    """Make compiler errors student-friendly with Chinese hints."""
    msg = raw.strip()
    if not msg:
        return "Unknown compilation error"

    # Add Chinese-friendly hints
    hints = []
    lower = msg.lower()
    if 'undeclared' in lower or 'undefined' in lower:
        hints.append("提示：变量或函数未声明。检查拼写错误或是否缺少 #include。")
    if 'expected' in lower and (';' in msg or '}' in msg or '{' in msg):
        hints.append("提示：缺少分号(;)或花括号({})。")
    if 'implicit' in lower:
        hints.append("提示：函数使用前需要先声明或定义。")
    if "unknown type name" in lower:
        hints.append("提示：未知类型名。检查是否拼写正确，或是否包含了对应的头文件。")
    if "assignment" in lower and "cast" in lower:
        hints.append("提示：类型不匹配。赋值时左右两边类型需要兼容。")

    if hints:
        return msg + "\n\n" + "\n".join(hints)
    return msg


def _parse_error_lines(raw_stderr: str) -> list[dict]:
    """Parse stderr for line/column error markers."""
    results = []
    # Match: path:line:column: message  or  path:line: message
    pattern = re.compile(r'main\.c:(\d+):(\d+)?:?\s*(.*)')
    for line in raw_stderr.split('\n'):
        m = pattern.search(line)
        if m:
            results.append({
                "line": int(m.group(1)),
                "column": int(m.group(2)) if m.group(2) else 0,
                "message": m.group(3).strip()[:200],
            })
    return results


# ── Course content loading ────────────────────────────────────────

import yaml

@dataclass
class CourseModule:
    title: str
    slug: str
    level: int
    order: int
    description: str = ""
    content_md: str = ""
    tags: list = field(default_factory=list)

@dataclass
class ExerciseData:
    id: str
    title: str
    difficulty: str
    tags: list
    description_md: str
    template_code: str
    test_cases: list
    hints: list
    solution_code: str

# Cache
_modules_cache: Optional[list[CourseModule]] = None
_exercises_cache: Optional[list[ExerciseData]] = None

LEVEL_MAP = {
    "01-basics": 1, "02-control-flow": 2, "03-functions": 3,
    "03-memory": 4, "04-arrays": 5, "04-data-structures": 6,
    "05-pointers": 7, "05-advanced": 8, "06-strings": 9,
    "06-expert": 10, "07-structs": 11, "08-file-io": 12,
    "09-dynamic-memory": 13, "10-algorithms": 14, "11-systems": 15,
    "12-projects": 16,
}


def load_modules() -> list[CourseModule]:
    global _modules_cache
    if _modules_cache is not None:
        return _modules_cache

    modules = []
    content = _content_dir()
    if not content.exists():
        _modules_cache = modules
        return modules

    for dir_name in sorted(os.listdir(content)):
        dir_path = content / dir_name
        if not dir_path.is_dir() or dir_name == "exercises":
            continue

        level = LEVEL_MAP.get(dir_name, 1)

        for fname in sorted(os.listdir(dir_path)):
            if not fname.endswith(".md"):
                continue
            text = (dir_path / fname).read_text(encoding="utf-8")
            meta, body = _parse_frontmatter(text)
            modules.append(CourseModule(
                title=meta.get("title", fname.replace(".md", "")),
                slug=fname.replace(".md", ""),
                level=meta.get("level", level),
                order=meta.get("order", 0),
                description=meta.get("description", ""),
                content_md=body,
                tags=meta.get("tags", []),
            ))

    modules = sorted(modules, key=lambda m: (m.level, m.order))
    _modules_cache = modules
    return modules


def load_exercises() -> list[ExerciseData]:
    global _exercises_cache
    if _exercises_cache is not None:
        return _exercises_cache

    exercises = []
    ex_root = _content_dir() / "exercises"
    if not ex_root.exists():
        _exercises_cache = exercises
        return exercises

    for dir_name in sorted(os.listdir(ex_root)):
        dir_path = ex_root / dir_name
        if not dir_path.is_dir():
            continue
        for fname in sorted(os.listdir(dir_path)):
            if not fname.endswith((".yml", ".yaml")):
                continue
            text = (dir_path / fname).read_text(encoding="utf-8")
            data = yaml.safe_load(text)
            if not data:
                continue
            exercises.append(ExerciseData(
                id=data.get("id", fname.replace(".yml", "")),
                title=data.get("title", fname),
                difficulty=data.get("difficulty", "easy"),
                tags=data.get("tags", []),
                description_md=data.get("description_md", ""),
                template_code=data.get("template_code", ""),
                test_cases=data.get("test_cases", []),
                hints=data.get("hints", []),
                solution_code=data.get("solution_code", ""),
            ))

    _exercises_cache = exercises
    return exercises


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    meta = yaml.safe_load(parts[1]) or {}
    return meta, parts[2].strip()


# ── Progress persistence (local JSON) ─────────────────────────────

import json as _json

_PROGRESS_FILE = _base_dir() / "progress.json"

def load_progress() -> dict:
    """Load exercise progress from local JSON."""
    if _PROGRESS_FILE.exists():
        try:
            with open(_PROGRESS_FILE, "r", encoding="utf-8") as f:
                return _json.load(f)
        except Exception:
            pass
    return {}

def save_progress(slug: str, status: str, code: str):
    """Save exercise progress (passed/failed) to local JSON."""
    data = load_progress()
    data[slug] = {
        "status": status,
        "last_code": code,
        "timestamp": time.time(),
    }
    with open(_PROGRESS_FILE, "w", encoding="utf-8") as f:
        _json.dump(data, f, ensure_ascii=False, indent=2)
