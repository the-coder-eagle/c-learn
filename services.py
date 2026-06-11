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
    """Get the project root, handling PyInstaller _MEIPASS.

    For writable files (progress.json), use the directory containing the exe
    or the current working directory — NEVER write to _MEIPASS (it's temporary).
    """
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS)  # Read-only: used for content, tools, etc.
    return Path(__file__).parent


def _writable_dir() -> Path:
    """Get a persistent writable directory for user data.

    In PyInstaller builds, this is the directory containing the exe.
    In dev mode, this is the project root.
    """
    import __main__
    if getattr(sys, 'frozen', False):
        # Running as packaged exe — store data next to the exe
        return Path(sys.executable).parent
    # Running from source — store in project root
    return Path(__file__).parent

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
    """Get the content directory, respecting CLEARN_CONTENT_DIR env var."""
    custom = os.environ.get("CLEARN_CONTENT_DIR", "").strip()
    if custom:
        return Path(custom)
    return _base_dir() / "content"

# ── Configuration ────────────────────────────────────────────────────
# Load .env file if present (python-dotenv is optional)
try:
    from dotenv import load_dotenv
    _env_path = _base_dir() / ".env"
    if _env_path.exists():
        load_dotenv(_env_path)
except ImportError:
    pass  # python-dotenv not installed — use os.environ directly

# All config values with sensible defaults
CONFIG = {
    "compile_timeout": int(os.environ.get("CLEARN_COMPILE_TIMEOUT", "15")),
    "run_timeout": int(os.environ.get("CLEARN_RUN_TIMEOUT", "5")),
    "free_run_timeout": int(os.environ.get("CLEARN_FREE_RUN_TIMEOUT", "10")),
    "max_stdout": int(os.environ.get("CLEARN_MAX_STDOUT", "10000")),
    "max_stderr": int(os.environ.get("CLEARN_MAX_STDERR", "5000")),
    "strict_free_play": os.environ.get("CLEARN_STRICT_FREE_PLAY", "") == "1",
}
_PER_CASE_TIMEOUT = CONFIG["run_timeout"]

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
    r"\bsystem\s*\(", r"\bpopen\s*\(", r"\bexec[lvpe]*\s*\(", r"\bfork\s*\(",
    r"\bCreateProcess\b", r"\bWinExec\b", r"\bShellExecute\b",
    r"\bsocket\s*\(", r"\bconnect\s*\(",
    r"\b__asm\b", r"\b__asm__\b",
    r"#include\s*<winsock",
    r"#include\s*<winsock2",
    r"\bsyscall\s*\(",    # raw syscall — bypasses all wrappers
    r"\b__builtin_",      # compiler builtins that can escape sandbox
]

# Relaxed scan for free play — only blocks truly destructive ops
# NOTE: fopen/remove/fwrite are NOT blocked — they're needed for file I/O exercises
_FORBIDDEN_RELAXED = [
    r"\bsystem\s*\(", r"\bCreateProcess\b", r"\bWinExec\b", r"\bShellExecute\b",
    r"\b__asm\b", r"\b__asm__\b", r"\bsyscall\s*\(",
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
    """Security scan. strict=True for exercise submission, False for free play.

    Uses regex patterns for precise matching (word boundaries prevent false positives
    like 'systematic' triggering the 'system(' block).
    """
    lower = source.lower()
    patterns = _FORBIDDEN_STRICT if strict else _FORBIDDEN_RELAXED

    # Honor CLEARN_STRICT_FREE_PLAY env override
    if not strict and CONFIG.get("strict_free_play", False):
        patterns = _FORBIDDEN_STRICT

    blocks = []
    for pat in patterns:
        if re.search(pat, lower):
            # Extract a human-readable label from the pattern
            label = pat.replace(r"\b", "").replace(r"\s*\(", "(").replace(r"\s*<", " <")
            blocks.append(label)

    if blocks:
        return False, f"Code blocked: {', '.join(blocks[:3])} not allowed in this context."
    return True, ""

# ── Compilation ───────────────────────────────────────────────────

def compile_and_run(source_code: str, stdin: str = "", timeout: int = None) -> CompileResult:
    """
    Compile C code with TCC and run it. Returns CompileResult.
    Runs synchronously — call from a background thread to keep UI responsive.
    """
    safe, msg = _scan_source(source_code, strict=False)  # relaxed for free play
    if not safe:
        return CompileResult(success=False, compile_error=msg)

    if timeout is None:
        timeout = CONFIG["free_run_timeout"]

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

        raw_stderr = compile_proc.stderr[: CONFIG["max_stderr"]] if compile_proc.stderr else ""
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
        stdout = run_proc.stdout[: CONFIG["max_stdout"]] if run_proc.stdout else ""
        stderr_out = run_proc.stderr[: CONFIG["max_stderr"]] if run_proc.stderr else ""

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


def compile_only(source_code: str, strict: bool = True) -> tuple[bool, str, str]:
    """
    Compile to a temp binary. Returns (success, binary_path, error_message).

    The caller owns the tmpdir on success and MUST clean it up after running
    the binary. On failure, tmpdir is cleaned up before returning.
    """
    safe, msg = _scan_source(source_code, strict=strict)
    if not safe:
        return False, "", msg

    tcc = _tcc_exe()
    if not tcc:
        return False, "", "TCC compiler not found"

    tmpdir = tempfile.mkdtemp(prefix="clearn_")
    success = False
    try:
        ext = ".exe" if os.name == "nt" else ".out"
        binary = str(Path(tmpdir) / f"a{ext}")
        src = Path(tmpdir) / "main.c"
        src.write_text(source_code, encoding="utf-8")

        proc = subprocess.run(
            [tcc, "-std=c11", "-o", binary, str(src)],
            capture_output=True,
            timeout=CONFIG["compile_timeout"],
            text=True,
            **_subprocess_kwargs(),
        )
        if proc.returncode != 0:
            raw = proc.stderr[: CONFIG["max_stderr"]] if proc.stderr else ""
            clean = re.sub(r'[A-Z]:[^\s]*?/main\.c:\d+: ', '', raw).strip()
            return False, "", _translate_error(clean or "Compilation failed")

        success = True
        return True, binary, ""
    except subprocess.TimeoutExpired:
        return False, "", "Compilation timed out"
    except Exception as e:
        return False, "", f"Compilation error: {str(e)}"
    finally:
        if not success:
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)


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
            stdout=proc.stdout[: CONFIG["max_stdout"]] if proc.stdout else "",
            stderr=proc.stderr[: CONFIG["max_stderr"]] if proc.stderr else "",
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
    """Make compiler errors student-friendly with bilingual hints (ZH + EN fallback)."""
    msg = raw.strip()
    if not msg:
        return "Unknown compilation error"

    # Detect system language preference from environment
    _lang = os.environ.get("CLEARN_LANG", "")
    if not _lang:
        # Simple heuristic: check LANG env or default to bilingual
        _lang = os.environ.get("LANG", "zh")

    is_zh = _lang.startswith("zh") or _lang.startswith("zh_CN")

    # Build hints — always include English, add Chinese when appropriate
    hints = []
    lower = msg.lower()

    if 'undeclared' in lower or 'undefined' in lower:
        if is_zh:
            hints.append("提示：变量或函数未声明。检查拼写错误或是否缺少 #include。")
        hints.append("Hint: variable or function not declared. Check for typos or missing #include.")

    if 'expected' in lower and (';' in msg or '}' in msg or '{' in msg):
        if is_zh:
            hints.append("提示：缺少分号(;)或花括号({})。")
        hints.append("Hint: missing semicolon (;) or brace ({}).")

    if 'implicit' in lower:
        if is_zh:
            hints.append("提示：函数使用前需要先声明或定义。")
        hints.append("Hint: function must be declared or defined before use.")

    if "unknown type name" in lower:
        if is_zh:
            hints.append("提示：未知类型名。检查是否拼写正确，或是否包含了对应的头文件。")
        hints.append("Hint: unknown type name. Check spelling or missing #include.")

    if "assignment" in lower and "cast" in lower:
        if is_zh:
            hints.append("提示：类型不匹配。赋值时左右两边类型需要兼容。")
        hints.append("Hint: type mismatch. Both sides of assignment need compatible types.")

    if "undefined reference" in lower:
        if is_zh:
            hints.append("提示：未定义的引用。是否忘记链接库，或函数名拼写错误？")
        hints.append("Hint: undefined reference. Did you forget to link a library or misspell a function name?")

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


# ── Interactive Runner ──────────────────────────────────────────────

import threading as _threading

class InteractiveRunner:
    """Runs a compiled C program interactively with streaming I/O.

    Uses subprocess.Popen with pipes so the frontend can stream output
    and send stdin input while the program is running (like a real terminal).
    """
    def __init__(self):
        self.process = None
        self.tmpdir = None
        self._output_lock = _threading.Lock()
        self._output_lines = []  # list of {"type":"stdout"|"stderr","text":str}
        self.running = False
        self.exit_code = None

    def start(self, source_code: str) -> dict:
        """Compile and launch the binary. Returns {status, error?}."""
        code = source_code

        # Security scan (relaxed for free play)
        safe, msg = _scan_source(code, strict=False)
        if not safe:
            return {"status": "compile_error", "error": msg}

        # ── Compile with OS-level printf ──
        # TCC's libc printf may buffer when stdout is a pipe, and overriding
        # printf at link time is unreliable. Instead we use a unique function
        # name (__flush_printf) and tell the preprocessor to replace every
        # printf call with it via -D. This guarantees our direct-write
        # implementation is used, with zero symbol conflicts.
        tcc = _tcc_exe()
        if not tcc:
            return {"status": "compile_error", "error": "TCC compiler not found"}

        tmpdir = tempfile.mkdtemp(prefix="clearn_")
        ext = ".exe" if os.name == "nt" else ".out"
        binary = str(Path(tmpdir) / f"a{ext}")

        # Wrapper: __flush_printf uses WriteFile + FlushFileBuffers to
        # write directly to the stdout pipe, bypassing all C stdio buffering.
        # Compiler -D flags redirect printf/puts to our implementations.
        wrapper_src = (
            '#include <stdio.h>\n'
            '#include <stdarg.h>\n'
            '#include <windows.h>\n'
            'int __flush_printf(const char *f,...) {\n'
            '    char b[8192];va_list a;va_start(a,f);\n'
            '    int r=vsnprintf(b,sizeof(b),f,a);va_end(a);\n'
            '    if(r>0) {\n'
            '        HANDLE h=GetStdHandle(STD_OUTPUT_HANDLE);\n'
            '        DWORD w;WriteFile(h,b,r,&w,NULL);\n'
            '        FlushFileBuffers(h);\n'
            '    }\n'
            '    return r;\n'
            '}\n'
            'int __flush_puts(const char *s) {\n'
            '    int r=__flush_printf("%s\\n",s);return r>=0?r:r;\n'
            '}\n'
        )
        wrapper_path = str(Path(tmpdir) / "__wrap.c")
        Path(wrapper_path).write_text(wrapper_src, encoding="utf-8")

        # Write user's source
        src_path = str(Path(tmpdir) / "main.c")
        Path(src_path).write_text(code, encoding="utf-8")

        # Compile: -D flags redirect printf→__flush_printf, puts→__flush_puts
        compile_proc = subprocess.run(
            [tcc, "-std=c11",
             "-Dprintf=__flush_printf", "-Dputs=__flush_puts",
             "-o", binary, wrapper_path, src_path],
            capture_output=True, timeout=15, text=True,
            **_subprocess_kwargs(),
        )
        if compile_proc.returncode != 0:
            raw = compile_proc.stderr[:5000] if compile_proc.stderr else ""
            clean = re.sub(r'[A-Z]:[^\s]*?/(__wrap|main)\.c:\d+: ', '', raw).strip()
            import shutil as _shutil
            _shutil.rmtree(tmpdir, ignore_errors=True)
            return {"status": "compile_error", "error": _translate_error(clean or "Compilation failed")}

        # Start the binary with pipes (binary mode — no extra buffering)
        try:
            self.process = subprocess.Popen(
                [binary],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                **_subprocess_kwargs(),
            )
            self.tmpdir = str(Path(binary).parent)
            self.running = True
            self.exit_code = None
            self._output_lines.clear()

            # Launch reader threads
            _threading.Thread(target=self._reader, args=(self.process.stdout, "stdout"), daemon=True).start()
            _threading.Thread(target=self._reader, args=(self.process.stderr, "stderr"), daemon=True).start()
            # Monitor thread for exit
            _threading.Thread(target=self._monitor, daemon=True).start()

            return {"status": "started"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _reader(self, pipe, pipe_type: str):
        """Read output from the subprocess pipe in chunks.

        Uses a blocking read loop — on Windows, PIPE reads return as soon
        as any data is available (unlike file reads). Using larger chunk
        sizes reduces system call overhead while maintaining responsiveness.
        """
        try:
            while True:
                chunk = pipe.read(256)  # 256-byte chunks — responsive + efficient
                if not chunk:  # EOF
                    break
                text = chunk.decode('utf-8', errors='replace')
                with self._output_lock:
                    self._output_lines.append({"type": pipe_type, "text": text})
        except (ValueError, OSError):
            pass  # Pipe closed

    def _monitor(self):
        """Wait for process exit, update state, and clean up."""
        try:
            self.process.wait()
        except Exception:
            pass
        self.exit_code = self.process.returncode
        self.running = False
        # Clean up temp dir
        if self.tmpdir:
            import shutil as _shutil
            _shutil.rmtree(self.tmpdir, ignore_errors=True)
            self.tmpdir = None

    def poll(self) -> dict:
        """Return new output since last poll, plus process status."""
        with self._output_lock:
            lines = self._output_lines[:]
            self._output_lines.clear()
        return {
            "running": self.running,
            "exit_code": self.exit_code,
            "lines": lines,
        }

    def send_input(self, text: str):
        """Write text + newline to the process's stdin (binary pipe)."""
        if self.process and self.running and self.process.stdin:
            try:
                data = (text + '\n').encode('utf-8')
                self.process.stdin.write(data)
                self.process.stdin.flush()
                return True
            except (OSError, ValueError):
                return False
        return False

    def kill(self):
        """Forcefully terminate the running process."""
        if self.process:
            try:
                self.process.kill()
            except Exception:
                pass
            self.running = False
        if self.tmpdir:
            import shutil as _shutil
            _shutil.rmtree(self.tmpdir, ignore_errors=True)
            self.tmpdir = None


# Global singleton (one desktop window = one session)
_runner: InteractiveRunner = None


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

_PROGRESS_FILE = _writable_dir() / "progress.json"

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
