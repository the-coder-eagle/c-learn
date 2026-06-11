"""
C Code Simulator — 教学用逐行执行引擎
支持子集: int, int*, 数组, 函数调用, printf, &, *, 赋值, 算术,
         if/else, while, for, do-while, break, continue, switch/case (v3)
不调用编译器，纯 Python 模拟。正确性优先于完整性。
"""
import re
from dataclasses import dataclass, field
from typing import Any, Optional


# ── 内置示例 ──────────────────────────────────────────
EXAMPLES = {
    "pointer_basics": {
        "title": "例1 - 指针基础",
        "code": """#include <stdio.h>

int main() {
    int a = 5;
    int b = 10;
    int *p = &a;

    printf("a = %d\\n", a);
    *p = 20;
    printf("a = %d\\n", a);

    p = &b;
    printf("*p = %d\\n", *p);
    return 0;
}""",
    },
    "function_pointer": {
        "title": "例2 - 函数传指针",
        "code": """#include <stdio.h>

void swap(int *x, int *y) {
    int temp = *x;
    *x = *y;
    *y = temp;
}

int main() {
    int a = 5;
    int b = 10;

    printf("before: a=%d b=%d\\n", a, b);
    swap(&a, &b);
    printf("after:  a=%d b=%d\\n", a, b);
    return 0;
}""",
    },
    "array_pointer": {
        "title": "例3 - 数组与指针",
        "code": """#include <stdio.h>

int main() {
    int arr[3] = {10, 20, 30};
    int *p = arr;

    printf("arr[0] = %d\\n", arr[0]);
    printf("*p = %d\\n", *p);

    p = p + 1;
    printf("*p = %d\\n", *p);

    *p = 99;
    printf("arr[1] = %d\\n", arr[1]);
    return 0;
}""",
    },
    "if_else": {
        "title": "例4 - if/else 条件判断",
        "code": """#include <stdio.h>

int main() {
    int a = 5;

    if (a > 3) {
        printf("a > 3\\n");
    } else {
        printf("a <= 3\\n");
    }

    a = 2;
    if (a > 3) {
        printf("big\\n");
    } else {
        printf("small\\n");
    }
    return 0;
}""",
    },
    "while_loop": {
        "title": "例5 - while 循环",
        "code": """#include <stdio.h>

int main() {
    int i = 0;

    while (i < 3) {
        printf("i = %d\\n", i);
        i = i + 1;
    }
    return 0;
}""",
    },
    "for_loop": {
        "title": "例6 - for 循环",
        "code": """#include <stdio.h>

int main() {
    int sum = 0;

    for (int i = 1; i <= 3; i = i + 1) {
        sum = sum + i;
    }
    printf("sum = %d\\n", sum);
    return 0;
}""",
    },
    "do_while": {
        "title": "例7 - do-while 循环",
        "code": """#include <stdio.h>

int main() {
    int i = 5;

    do {
        printf("i = %d\\n", i);
        i = i + 1;
    } while (i < 3);
    return 0;
}""",
    },
    "break_continue": {
        "title": "例8 - break 与 continue",
        "code": """#include <stdio.h>

int main() {
    int i = 0;

    while (i < 10) {
        i = i + 1;
        if (i == 3) {
            continue;
        }
        if (i == 5) {
            break;
        }
        printf("%d\\n", i);
    }
    return 0;
}""",
    },
    "switch_case": {
        "title": "例9 - switch/case",
        "code": """#include <stdio.h>

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
}""",
    },
}


# ── 内部数据结构 ──────────────────────────────────────

@dataclass
class Variable:
    name: str
    type: str          # "int", "int*", "int[3]"
    value: Any         # int or str (地址字符串)
    address: str       # "0x100" 格式
    size: int = 4
    elements: Optional[list] = None  # 数组元素列表
    points_to: Optional[str] = None  # 指向的变量名


@dataclass
class StackFrame:
    name: str          # 函数名
    variables: dict = field(default_factory=dict)  # name -> Variable
    return_line: int = 0


class CSimulator:
    """C 代码逐行模拟执行器 — 支持变量、指针、控制流"""

    def __init__(self, code: str):
        self._raw = code
        self._lines = []          # [(line_num, text, type, data_dict?), ...]
        self._ip = 0              # instruction pointer (index into _lines)
        self._stack: list[StackFrame] = []
        self._next_addr = 0x100   # 虚拟地址分配器
        self._output = ""         # printf 累积输出
        self._history: list[dict] = []  # 每步的状态快照（用于回退）
        self._finished = False
        self._hints: list[str] = []
        self._brace_map: dict[int, int] = {}  # 大括号配对 { → }
        self._loop_stack: list[dict] = []     # 嵌套循环追踪
        self._else_skip = False             # if 为真时跳过 else
        self._switch_value = None           # switch 表达式值
        self._case_matched = False          # 是否已匹配到 case
        self._switch_active = False         # 是否在 switch 块内
        self._func_map: dict[str, int] = {} # 函数名 → 起始行索引
        self._return_stack: list[int] = []  # 返回地址栈
        self._parse()

    # ── 解析辅助 ──────────────────────────────────────
    def _add_line(self, raw, stripped, stype, data=None):
        """向 _lines 添加一条解析后的行。用 raw 的长度统一标记。"""
        n = len(self._raw.split('\n'))
        self._lines.append((n, raw, stype, data or {}))

    def _parse_brace_line(self, stripped: str, brace_stack: list) -> bool:
        """处理大括号和 else 行。返回 True 表示已处理，调用者应 continue。"""
        line_idx = len(self._lines)

        # Standalone braces
        if stripped == '{':
            self._add_line('', stripped, "brace_open")
            brace_stack.append(line_idx)
            return True
        if stripped == '}':
            self._add_line('', stripped, "brace_close")
            if brace_stack:
                open_idx = brace_stack.pop()
                self._brace_map[open_idx] = line_idx
                self._brace_map[line_idx] = open_idx
            return True

        # } else / } else {
        m = re.match(r'\}\s*else\s*(\{?)\s*$', stripped)
        if m:
            has_brace = m.group(1) == '{'
            self._add_line('', stripped, "brace_close")
            if brace_stack:
                open_idx = brace_stack.pop()
                self._brace_map[open_idx] = line_idx
                self._brace_map[line_idx] = open_idx
            self._add_line('', stripped, "else_kw")
            if has_brace:
                idx = len(self._lines)
                self._add_line('', stripped, "brace_open")
                brace_stack.append(idx)
            return True

        # Standalone else / else {
        if stripped in ('else', 'else {'):
            self._add_line('', stripped, "else_kw")
            if stripped == 'else {':
                idx = len(self._lines)
                self._add_line('', stripped, "brace_open")
                brace_stack.append(idx)
            return True
        return False

    def _parse_control_flow(self, stripped: str, brace_stack: list) -> bool:
        """处理 if/while/for/do-while/switch/break/continue/case。返回 True 表示已处理。"""
        line_idx = len(self._lines)

        # if (cond) / if (cond) {
        m = re.match(r'if\s*\((.+)\)\s*(\{?)\s*$', stripped)
        if m:
            cond, brace = m.group(1).strip(), m.group(2)
            self._add_line('', stripped, "if_start", {"condition": cond})
            if brace == '{':
                idx = len(self._lines)
                self._add_line('', stripped, "brace_open")
                brace_stack.append(idx)
            return True

        # while (cond) / while (cond) {
        m = re.match(r'while\s*\((.+)\)\s*(\{?)\s*$', stripped)
        if m:
            cond, brace = m.group(1).strip(), m.group(2)
            self._add_line('', stripped, "while_start", {"condition": cond})
            if brace == '{':
                idx = len(self._lines)
                self._add_line('', stripped, "brace_open")
                brace_stack.append(idx)
            return True

        # for (init; cond; incr) / for (init; cond; incr) {
        m = re.match(r'for\s*\((.+);\s*(.+);\s*(.+)\)\s*(\{?)\s*$', stripped)
        if m:
            init, cond, incr, brace = m.groups()
            self._add_line('', stripped, "for_start",
                          {"init": init.strip(), "cond": cond.strip(), "incr": incr.strip()})
            if brace == '{':
                idx = len(self._lines)
                self._add_line('', stripped, "brace_open")
                brace_stack.append(idx)
            return True

        # do / do {
        if re.match(r'do\s*\{?\s*$', stripped):
            self._add_line('', stripped, "do_start")
            if stripped.endswith('{'):
                idx = len(self._lines)
                self._add_line('', stripped, "brace_open")
                brace_stack.append(idx)
            return True

        # } while (cond);
        m = re.match(r'\}\s*while\s*\((.+)\)\s*;\s*$', stripped)
        if m:
            cond = m.group(1).strip()
            self._add_line('', stripped, "brace_close")
            if brace_stack:
                open_idx = brace_stack.pop()
                self._brace_map[open_idx] = line_idx
                self._brace_map[line_idx] = open_idx
            self._add_line('', stripped, "while_check", {"condition": cond})
            return True

        # switch (expr) / switch (expr) {
        m = re.match(r'switch\s*\((.+)\)\s*\{?\s*$', stripped)
        if m:
            self._add_line('', stripped, "switch_start", {"expr": m.group(1).strip()})
            if stripped.endswith('{'):
                idx = len(self._lines)
                self._add_line('', stripped, "brace_open")
                brace_stack.append(idx)
            return True

        # break;
        if re.match(r'break\s*;\s*$', stripped):
            self._add_line('', stripped, "break_kw")
            return True

        # continue;
        if re.match(r'continue\s*;\s*$', stripped):
            self._add_line('', stripped, "continue_kw")
            return True

        # case N:
        m = re.match(r'case\s+(.+)\s*:\s*$', stripped)
        if m:
            self._add_line('', stripped, "case_label", {"value": m.group(1).strip()})
            return True

        # default:
        if re.match(r'default\s*:\s*$', stripped):
            self._add_line('', stripped, "default_label")
            return True
        return False

    # ── 解析 ──────────────────────────────────────────
    def _parse(self):
        """将代码分解为可执行的行列表，同时建立大括号配对映射。"""
        raw_lines = self._raw.split('\n')
        self._lines = []
        brace_stack = []

        for raw in raw_lines:
            stripped = raw.strip()
            if not stripped:
                self._add_line(raw, stripped, "empty")
                continue
            if stripped.startswith('#') or stripped.startswith('//'):
                self._add_line(raw, stripped, "skip")
                continue

            # 函数定义
            fm = re.match(r'(void|int)\s+(\w+)\s*\(([^)]*)\)\s*\{?\s*$', stripped)
            if fm:
                _, name, params = fm.groups()
                self._func_map[name] = len(self._lines)
                self._add_line(raw, stripped, "func_def", {"name": name, "params": params})
                continue

            # 大括号 / else
            if self._parse_brace_line(stripped, brace_stack):
                continue

            # 控制流
            if self._parse_control_flow(stripped, brace_stack):
                continue

            # 普通语句
            if stripped.endswith(';'):
                stmt_type = self._classify_stmt(stripped, None)
                self._add_line(raw, stripped, stmt_type, {"func": None})
            else:
                self._add_line(raw, stripped, "unknown")

    def _classify_stmt(self, stmt: str, func: Optional[str]) -> str:
        """分类语句类型"""
        s = stmt.strip().rstrip(';')
        if s.startswith('int ') and '=' in s:
            return "var_decl_init"
        if s.startswith('int '):
            return "var_decl"
        if s.startswith('printf('):
            return "printf"
        if s.startswith('return'):
            return "return"
        if '= &' in s or (s.startswith('int *') and '= &' in s):
            return "addr_assign"
        if '*p' in s.lower() or (s.startswith('*') and '=' in s):
            return "deref_assign"
        if '=' in s:
            return "assign"
        if re.match(r'\w+\(', s):
            return "func_call"
        return "stmt"

    # ── 地址分配 ──────────────────────────────────────
    def _alloc_addr(self) -> str:
        addr = f"0x{self._next_addr:03X}"
        self._next_addr += 4
        return addr

    def _alloc_array(self, count: int) -> list[str]:
        addrs = []
        for _ in range(count):
            addrs.append(f"0x{self._next_addr:03X}")
            self._next_addr += 4
        return addrs

    # ── 当前栈帧 ──────────────────────────────────────
    @property
    def _frame(self) -> StackFrame:
        return self._stack[-1] if self._stack else None

    # ── 变量查找（向上搜索调用栈） ─────────────────────
    def _find_var(self, name: str) -> Optional[Variable]:
        for frame in reversed(self._stack):
            if name in frame.variables:
                return frame.variables[name]
        return None

    def _set_var(self, name: str, value: Any, note: str = ""):
        """在当前栈帧设置变量值"""
        v = self._find_var(name)
        if v:
            v.value = value
            if v.type == "int*":
                self._update_points_to(v)

    def _update_points_to(self, ptr: Variable):
        """更新指针的 points_to 信息（含数组元素地址匹配）"""
        if not isinstance(ptr.value, str) or not ptr.value.startswith("0x"):
            ptr.points_to = None
            return
        for frame in reversed(self._stack):
            for var in frame.variables.values():
                if var.address == ptr.value and var.name != ptr.name:
                    ptr.points_to = var.name
                    return
                # Check array element addresses
                if var.elements:
                    for el in var.elements:
                        if el.get("addr") == ptr.value:
                            ptr.points_to = var.name
                            return
        ptr.points_to = None

    # ── 条件求值 ──────────────────────────────────────
    def _eval_condition(self, cond: str) -> bool:
        """Evaluate C boolean expressions. v4.1: supports &&, ||, !, comparisons.

        Precedence: ! > comparisons (>, <, >=, <=, ==, !=) > && > ||
        """
        cond = cond.strip()
        if not cond:
            return False

        # Strip outer parentheses
        while cond.startswith('(') and cond.endswith(')'):
            # Check if the closing paren matches the opening one
            depth = 0
            matched = True
            for i, ch in enumerate(cond):
                if ch == '(':
                    depth += 1
                elif ch == ')':
                    depth -= 1
                if depth == 0 and i < len(cond) - 1:
                    matched = False
                    break
            if matched:
                cond = cond[1:-1].strip()
            else:
                break

        # Unary NOT: !expr
        if cond.startswith('!'):
            return not self._eval_condition(cond[1:].strip())

        # Logical OR: a || b  (lowest precedence)
        depth = 0
        for i, ch in enumerate(cond):
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
            elif depth == 0 and i + 1 < len(cond) and cond[i:i+2] == '||':
                left = cond[:i].strip()
                right = cond[i+2:].strip()
                return self._eval_condition(left) or self._eval_condition(right)

        # Logical AND: a && b
        depth = 0
        for i, ch in enumerate(cond):
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
            elif depth == 0 and i + 1 < len(cond) and cond[i:i+2] == '&&':
                left = cond[:i].strip()
                right = cond[i+2:].strip()
                return self._eval_condition(left) and self._eval_condition(right)

        # Comparisons
        for op in ['>=', '<=', '!=', '==', '>', '<']:
            if op in cond:
                left, right = cond.split(op, 1)
                l_val = self._eval_expr(left.strip())
                r_val = self._eval_expr(right.strip())
                if op == '>':
                    return l_val > r_val
                if op == '<':
                    return l_val < r_val
                if op == '>=':
                    return l_val >= r_val
                if op == '<=':
                    return l_val <= r_val
                if op == '==':
                    return l_val == r_val
                if op == '!=':
                    return l_val != r_val

        # Single value: truthy if != 0
        val = self._eval_expr(cond)
        return val != 0

    # ── 执行一步 ──────────────────────────────────────
    def step(self) -> dict:
        """执行当前行，前进一行或跳转，返回状态"""
        if self._finished:
            return self._get_state()

        # 保存快照（用于回退）— skip lines/variables to save memory
        self._history.append(self._get_state(for_history=True))

        if self._ip >= len(self._lines):
            self._finished = True
            return self._get_state()

        _, raw, stmt_type, *extra = self._lines[self._ip]
        data = extra[0] if extra else {}
        current_func = data.get("func")

        self._hints = []
        jump_to = None  # set by handlers to override _ip increment

        try:
            if stmt_type == "func_def":
                self._handle_func_def(data)
            elif stmt_type == "var_decl":
                self._handle_var_decl(raw, current_func)
            elif stmt_type == "var_decl_init":
                self._handle_var_decl_init(raw, current_func)
            elif stmt_type == "assign":
                self._handle_assign(raw)
            elif stmt_type == "addr_assign":
                self._handle_addr_assign(raw)
            elif stmt_type == "deref_assign":
                self._handle_deref_assign(raw)
            elif stmt_type == "printf":
                self._handle_printf(raw)
            elif stmt_type == "func_call":
                jump_to = self._handle_func_call(raw)
            elif stmt_type == "return":
                jump_to = self._handle_return(raw)
            elif stmt_type == "if_start":
                jump_to = self._handle_if(data)
            elif stmt_type == "else_kw":
                jump_to = self._handle_else()
            elif stmt_type == "while_start":
                jump_to = self._handle_while(data)
            elif stmt_type == "for_start":
                jump_to = self._handle_for(data)
            elif stmt_type == "do_start":
                self._handle_do(data)
            elif stmt_type == "while_check":
                jump_to = self._handle_while_check(data)
            elif stmt_type == "break_kw":
                jump_to = self._handle_break()
            elif stmt_type == "continue_kw":
                jump_to = self._handle_continue()
            elif stmt_type == "switch_start":
                self._handle_switch(data)
            elif stmt_type == "case_label":
                jump_to = self._handle_case(data)
            elif stmt_type == "default_label":
                self._handle_default()
            elif stmt_type == "brace_close":
                jump_to = self._handle_brace_close(current_func)
            # skip, empty, brace_open, unknown — 前进但不执行
        except Exception as e:
            self._hints.append(f"⚠ 执行错误: {e}")

        if jump_to is not None:
            self._ip = jump_to
        else:
            self._ip += 1
        return self._get_state()

    def step_back(self) -> dict:
        """回退一步"""
        if self._history:
            prev = self._history.pop()
            self._ip = prev["_ip"]
            self._next_addr = prev["_next_addr"]
            self._output = prev["_output"]
            self._finished = prev["_finished"]
            self._hints = []
            # Restore loop stack
            self._loop_stack = list(prev.get("_loop_stack", []))
            self._else_skip = prev.get("_else_skip", False)
            self._switch_active = prev.get("_switch_active", False)
            self._switch_value = prev.get("_switch_value")
            self._case_matched = prev.get("_case_matched", False)
            self._return_stack = list(prev.get("_return_stack", []))
            # Restore stack frames and variables (v4 fix)
            if "_stack_data" in prev:
                self._restore_stack(prev["_stack_data"])
        return self._get_state()

    def reset(self):
        """重置到初始状态"""
        self._ip = 0
        self._stack = []
        self._next_addr = 0x100
        self._output = ""
        self._history = []
        self._finished = False
        self._hints = []
        self._loop_stack = []
        self._else_skip = False
        self._switch_value = None
        self._case_matched = False
        self._switch_active = False
        self._return_stack = []

    def _restore_stack(self, stack_data: list):
        """从序列化数据重建栈帧（用于 step_back 回退）"""
        self._stack = []
        for fd in stack_data:
            frame = StackFrame(name=fd["name"], return_line=fd.get("return_line", 0))
            for vname, vdata in fd.get("variables", {}).items():
                var = Variable(
                    name=vdata["name"], type=vdata["type"],
                    value=vdata["value"], address=vdata["address"],
                    size=vdata.get("size", 4), elements=vdata.get("elements"),
                    points_to=vdata.get("points_to"),
                )
                frame.variables[vname] = var
            self._stack.append(frame)

    def run_all(self) -> dict:
        """运行到结束"""
        max_steps = 5000  # safety limit
        steps = 0
        while not self._finished and steps < max_steps:
            self.step()
            steps += 1
        if steps >= max_steps:
            self._hints.append("⚠ 达到最大步数限制 (5000)，可能死循环")
            self._finished = True
        return self._get_state()

    # ── 控制流处理器 ──────────────────────────────────
    def _find_brace_open_after(self, start: int) -> Optional[int]:
        """Find the next brace_open after start, return its index or None."""
        for i in range(start, len(self._lines)):
            _, _, st, *_ = self._lines[i]
            if st == "brace_open":
                return i
        return None

    def _skip_block(self, from_ip: int) -> int:
        """Skip past a block by counting brace depth. Returns the index after the
        matching brace_close, or from_ip+1 if no block found."""
        depth = 0
        for i in range(from_ip, len(self._lines)):
            _, _, st, *_ = self._lines[i]
            if st == "brace_open":
                depth += 1
            elif st == "brace_close":
                depth -= 1
                if depth == 0:
                    return i
        return from_ip + 1  # fallback

    def _handle_if(self, data: dict) -> Optional[int]:
        """if (condition) — evaluate and jump accordingly."""
        cond = data.get("condition", "0")
        result = self._eval_condition(cond)
        self._hints.append(
            f"if ({cond}) → {'真' if result else '假'}，"
            f"{'执行 then 分支' if result else '跳过 then 分支'}"
        )

        # Find the body's brace_open (either next line or synthesized from same-line {)
        body_open = self._find_brace_open_after(self._ip + 1)

        if result:
            # Condition true: execute body, skip else (if any) later
            self._else_skip = True
            return None  # advance to body

        # Condition false: skip the if body
        if body_open is not None:
            close_ip = self._brace_map.get(body_open)
            if close_ip is not None:
                # Check if there's an else_kw after the if body's closing }
                for j in range(close_ip + 1, min(close_ip + 4, len(self._lines))):
                    _, _, st, *_ = self._lines[j]
                    if st == "else_kw":
                        self._else_skip = False  # we're entering else
                        return j  # jump directly to else_kw
                # No else: skip past the closing }
                return close_ip
        else:
            # Single-statement if (no braces): skip exactly one statement
            for i in range(self._ip + 1, len(self._lines)):
                _, _, st, *_ = self._lines[i]
                if st not in ("skip", "empty"):
                    return i + 1  # skip past the single body statement
        return None

    def _handle_else(self) -> Optional[int]:
        """else — skip body if if-was-true, or enter if if-was-false."""
        if getattr(self, '_else_skip', False):
            # If was true — skip the else body entirely
            self._else_skip = False
            self._hints.append("else 分支 — 跳过（if 条件为真）")
            # Skip past else body by depth-counting from current position
            body_open = self._find_brace_open_after(self._ip + 1)
            if body_open is not None:
                close_ip = self._brace_map.get(body_open)
                if close_ip is not None:
                    return close_ip
            return self._skip_block(self._ip + 1)
        else:
            # If was false — enter else body normally
            self._hints.append("else 分支 — 进入（if 条件为假）")
            return None

    def _handle_while(self, data: dict) -> Optional[int]:
        """while (condition) — evaluate and loop."""
        cond = data.get("condition", "0")
        result = self._eval_condition(cond)
        self._hints.append(
            f"while ({cond}) → {'真' if result else '假'}"
        )

        body_open = self._find_brace_open_after(self._ip + 1)

        if not result:
            # Condition false: exit loop — pop from loop_stack and skip body
            popped = None
            for i in range(len(self._loop_stack) - 1, -1, -1):
                if self._loop_stack[i]["start_ip"] == self._ip:
                    popped = self._loop_stack.pop(i)
                    break
            if popped:
                self._hints.append(f"  {popped['type']} 条件为假，退出循环")
            if body_open is not None and body_open in self._brace_map:
                return self._brace_map[body_open]
            return None

        # Condition true: record loop entry for jump-back
        # Check if this IP is already tracked (re-entering after loop-back)
        already_tracked = any(e.get("start_ip") == self._ip for e in self._loop_stack)
        if not already_tracked:
            self._loop_stack.append({
                "start_ip": self._ip,
                "type": "while",
            })
            self._hints.append(f"  进入循环体 (第 {len(self._loop_stack)} 层嵌套)")
        return None  # continue to body

    def _handle_for(self, data: dict) -> Optional[int]:
        """for (init; cond; incr) — initialize, check, loop."""
        init = data.get("init", "")
        cond = data.get("cond", "1")
        incr = data.get("incr", "")

        # Check if this is first entry (not a loop-back jump)
        already_tracked = any(e.get("start_ip") == self._ip for e in self._loop_stack)

        if not already_tracked:
            # Execute init: e.g. "int i = 1" or "i = 0"
            if init:
                self._hints.append(f"for 初始化: {init}")
                self._execute_inline_stmt(init)

        # Evaluate condition
        result = self._eval_condition(cond)
        self._hints.append(
            f"for (; {cond}; {incr}) → 条件 {'真' if result else '假'}"
        )

        body_open = self._find_brace_open_after(self._ip + 1)

        if not result:
            # Condition false: exit loop — pop from loop_stack and skip body
            for idx in range(len(self._loop_stack) - 1, -1, -1):
                if self._loop_stack[idx]["start_ip"] == self._ip:
                    popped = self._loop_stack.pop(idx)
                    self._hints.append(f"  {popped['type']} 条件为假，退出循环")
                    break
            if body_open is not None and body_open in self._brace_map:
                return self._brace_map[body_open]
            return None

        # Condition true: record loop entry
        if not already_tracked:
            self._loop_stack.append({
                "start_ip": self._ip,
                "type": "for",
                "incr": incr,
            })
            self._hints.append(f"  进入循环体 (第 {len(self._loop_stack)} 层嵌套)")
        return None  # continue to body

    # ── do-while / break / continue / switch ──────────
    def _handle_do(self, data: dict) -> None:
        """do { — always enter body first, condition checked later."""
        self._hints.append("do-while: 先执行循环体，再检查条件")
        # Record the do position for later break/continue
        self._loop_stack.append({
            "start_ip": self._ip,
            "type": "do_while",
        })

    def _handle_while_check(self, data: dict) -> Optional[int]:
        """} while (cond); — evaluate condition, jump back to do if true."""
        cond = data.get("condition", "0")
        result = self._eval_condition(cond)
        self._hints.append(
            f"while ({cond}) → {'真' if result else '假'}"
        )
        if result:
            # Find the matching do_start and jump back
            if self._loop_stack:
                loop = self._loop_stack[-1]
                if loop["type"] == "do_while":
                    self._hints.append("  条件为真，跳回 do 循环体")
                    return loop["start_ip"] + 1  # +1 to skip do_start itself
        else:
            # Exit loop
            if self._loop_stack:
                for idx in range(len(self._loop_stack) - 1, -1, -1):
                    if self._loop_stack[idx]["type"] == "do_while":
                        self._loop_stack.pop(idx)
                        self._hints.append("  条件为假，退出 do-while 循环")
                        break
        return None

    def _handle_break(self) -> Optional[int]:
        """break; — exit the innermost loop or switch."""
        if self._switch_active:
            self._hints.append("break — 跳出 switch")
            # Find the switch_start by scanning backwards
            for i in range(self._ip - 1, -1, -1):
                _, _, st, *_ = self._lines[i]
                if st == "switch_start":
                    body_open = self._find_brace_open_after(i + 1)
                    if body_open is not None and body_open in self._brace_map:
                        self._switch_active = False
                        self._case_matched = False
                        self._switch_value = None
                        return self._brace_map[body_open]  # jump to closing }
                    break
            return None

        if self._loop_stack:
            loop = self._loop_stack.pop()
            self._hints.append(f"break — 跳出 {loop['type']} 循环")
            loop_start = loop["start_ip"]
            body_open = self._find_brace_open_after(loop_start + 1)
            if loop["type"] == "do_while":
                body_open = self._find_brace_open_after(loop_start + 1)
            if body_open is not None and body_open in self._brace_map:
                return self._brace_map[body_open] + 1  # +1 to skip the closing }
        self._hints.append("break — 无循环可跳出")
        return None

    def _handle_continue(self) -> Optional[int]:
        """continue; — skip rest of current iteration."""
        if self._loop_stack:
            loop = self._loop_stack[-1]
            loop_type = loop["type"]
            self._hints.append(f"continue — 跳到 {loop_type} 下一轮迭代")

            if loop_type == "for":
                incr = loop.get("incr", "")
                if incr:
                    self._execute_inline_stmt(incr)
                return loop["start_ip"]  # jump back to for condition

            if loop_type == "while":
                return loop["start_ip"]  # jump back to while condition

            if loop_type == "do_while":
                # Jump to the while_check (end of do-while body)
                body_open = self._find_brace_open_after(loop["start_ip"] + 1)
                if body_open is not None and body_open in self._brace_map:
                    close_ip = self._brace_map[body_open]
                    # while_check is at close_ip + 1
                    return close_ip + 1
        self._hints.append("continue — 无循环可跳过")
        return None

    def _handle_switch(self, data: dict) -> None:
        """switch (expr) — evaluate expression and set up case matching."""
        expr = data.get("expr", "0")
        val = self._eval_expr(expr)
        self._switch_value = val
        self._case_matched = False
        self._switch_active = True
        self._hints.append(f"switch ({expr}) → 值为 {val}，开始匹配 case")

    def _handle_case(self, data: dict) -> Optional[int]:
        """case N: — check if matches switch value. Skip body if not matched."""
        case_val_str = data.get("value", "0")
        case_val = self._eval_expr(case_val_str)

        # If we're already executing a matched case (fall-through), continue
        if self._case_matched:
            self._hints.append(f"case {case_val}: 穿透执行")
            return None

        # Check if this case matches
        if case_val == self._switch_value:
            self._case_matched = True
            self._hints.append(f"case {case_val}: ✓ 匹配！")
            return None  # enter body

        # Not matched — skip to next case/default or closing }
        self._hints.append(f"case {case_val}: ✗ 跳过")
        depth = 0
        for i in range(self._ip + 1, len(self._lines)):
            _, _, st, *_ = self._lines[i]
            if st == "brace_open":
                depth += 1
            elif st == "brace_close":
                if depth == 0:
                    return i  # end of switch
                depth -= 1
            elif st in ("case_label", "default_label") and depth == 0:
                return i  # jump to next case/default
        return None

    def _handle_default(self) -> None:
        """default: — always matches if no case has matched yet."""
        if not self._case_matched:
            self._case_matched = True
            self._hints.append("default: 无匹配 case，进入默认分支")
        else:
            self._hints.append("default: 穿透执行（已有匹配 case）")

    def _execute_inline_stmt(self, stmt: str):
        """Execute a simple inline statement like 'int i = 0' or 'i = i + 1'.

        Used for for-loop init/incr clauses.
        """
        s = stmt.strip().rstrip(';')
        if not s:
            return

        # Variable declaration with init: "int i = 0"
        decl_match = re.match(r'int\s+(\w+)\s*=\s*(.+)$', s)
        if decl_match:
            name, expr = decl_match.groups()
            val = self._eval_expr(expr.strip())
            addr = self._alloc_addr()
            var = Variable(name=name, type="int", value=val, address=addr)
            if self._frame:
                self._frame.variables[name] = var
            self._hints.append(f"  声明 {name} = {val}，地址 {addr}")
            return

        # Assignment: "i = i + 1" or "sum = sum + i"
        assign_match = re.match(r'(\w+)\s*=\s*(.+)$', s)
        if assign_match:
            name, expr = assign_match.groups()
            val = self._eval_expr(expr.strip())
            v = self._find_var(name)
            old_val = v.value if v else None
            if v:
                v.value = val
            self._hints.append(
                f"  {name} = {val}"
                + (f"（之前: {old_val}）" if old_val is not None and old_val != val else "")
            )

    # ── 语句处理器 ────────────────────────────────────
    def _handle_func_def(self, data: dict):
        """进入函数定义"""
        name = data["name"]
        frame = StackFrame(name=name)
        self._stack.append(frame)
        self._hints.append(f"进入函数 {name}()，创建新的栈帧")

    def _handle_var_decl(self, raw: str, func: Optional[str]):
        """int x; 或 int arr[N];"""
        s = raw.strip().rstrip(';')
        # 数组声明
        arr_match = re.match(r'int\s+(\w+)\[(\d+)\]\s*$', s)
        if arr_match:
            name, count = arr_match.groups()
            count = int(count)
            addrs = self._alloc_array(count)
            var = Variable(
                name=name, type=f"int[{count}]", value="",
                address=addrs[0], size=4*count,
                elements=[{"index": i, "addr": addrs[i], "value": 0}
                         for i in range(count)])
            self._frame.variables[name] = var
            self._hints.append(
                f"声明数组 {name}[{count}]，分配 {count}×4={count*4} 字节，起始地址 {addrs[0]}")
            return
        # 普通变量声明
        m = re.match(r'int\s+(\*?)\s*(\w+)\s*$', s)
        if m:
            ptr, name = m.groups()
            addr = self._alloc_addr()
            var_type = "int*" if ptr else "int"
            var = Variable(name=name, type=var_type, value="?" if var_type == "int*" else 0, address=addr)
            self._frame.variables[name] = var
            self._hints.append(f"声明变量 {name}，类型 {var_type}，地址 {addr}")

    def _handle_var_decl_init(self, raw: str, func: Optional[str]):
        """int x = 5; 或 int *p = &a; 或 int arr[3] = {1,2,3}; 或 int a=1, b=2;"""
        s = raw.strip().rstrip(';')

        # 数组初始化
        arr_match = re.match(r'int\s+(\w+)\[(\d+)\]\s*=\s*\{([^}]+)\}', s)
        if arr_match:
            name, count, vals_str = arr_match.groups()
            count = int(count)
            vals = [int(v.strip()) for v in vals_str.split(',')]
            addrs = self._alloc_array(count)
            var = Variable(
                name=name, type=f"int[{count}]", value="",
                address=addrs[0], size=4*count,
                elements=[{"index": i, "addr": addrs[i],
                          "value": vals[i] if i < len(vals) else 0}
                         for i in range(count)])
            self._frame.variables[name] = var
            self._hints.append(
                f"声明数组 {name}[{count}] = {{{vals_str}}}，起始地址 {addrs[0]}")
            return

        # 指针初始化: int *p = &a;
        ptr_match = re.match(r'int\s+\*\s*(\w+)\s*=\s*&(\w+)\s*$', s)
        if ptr_match:
            ptr_name, target = ptr_match.groups()
            addr = self._alloc_addr()
            target_var = self._find_var(target)
            if target_var:
                var = Variable(name=ptr_name, type="int*", value=target_var.address,
                               address=addr, points_to=target)
                self._frame.variables[ptr_name] = var
                self._hints.append(
                    f"声明指针 {ptr_name}，&{target} 取出地址 {target_var.address}，{ptr_name} 存储该地址，指向 {target}")
            return

        # 指针初始化: int *p = arr;
        ptr_arr = re.match(r'int\s+\*\s*(\w+)\s*=\s*(\w+)\s*$', s)
        if ptr_arr:
            ptr_name, target = ptr_arr.groups()
            target_var = self._find_var(target)
            if target_var and '[' in target_var.type:
                addr = self._alloc_addr()
                var = Variable(name=ptr_name, type="int*", value=target_var.address,
                               address=addr, points_to=target)
                self._frame.variables[ptr_name] = var
                self._hints.append(
                    f"声明指针 {ptr_name}，数组名 {target} 代表首地址 {target_var.address}，{ptr_name} 指向数组首元素")
            return

        # 逗号声明: int a = 1, b = 2; (v4.1)
        if s.startswith('int ') and ',' in s:
            rest = s[4:].strip()  # remove "int "
            # Split by comma, but not inside expressions
            declarations = []
            depth = 0
            current = ''
            for ch in rest:
                if ch == '(':
                    depth += 1
                elif ch == ')':
                    depth -= 1
                if ch == ',' and depth == 0:
                    declarations.append(current.strip())
                    current = ''
                else:
                    current += ch
            if current.strip():
                declarations.append(current.strip())
            hints_parts = []
            for decl in declarations:
                eq = decl.find('=')
                if eq >= 0:
                    name = decl[:eq].strip().rstrip('*').strip()
                    expr = decl[eq+1:].strip()
                    val = self._eval_expr(expr)
                else:
                    name = decl.strip()
                    val = 0
                addr = self._alloc_addr()
                var_type = "int*" if '*' in decl else "int"
                var = Variable(name=name, type=var_type, value=val, address=addr)
                self._frame.variables[name] = var
                hints_parts.append(f"{name} = {val}")
            self._hints.append(f"声明变量: {', '.join(hints_parts)}")
            return

        # 普通变量初始化: int x = 5;
        m = re.match(r'int\s+(\w+)\s*=\s*(.+)$', s)
        if m:
            name, expr = m.groups()
            val = self._eval_expr(expr.strip())
            addr = self._alloc_addr()
            var = Variable(name=name, type="int", value=val, address=addr)
            self._frame.variables[name] = var
            self._hints.append(f"声明变量 {name} = {val}，地址 {addr}")

    def _handle_assign(self, raw: str):
        """x = expr; 或 arr[i] = expr; 或 p = p + 1;"""
        s = raw.strip().rstrip(';')
        # 数组元素赋值: arr[i] = expr
        arr_match = re.match(r'(\w+)\[(\d+)\]\s*=\s*(.+)$', s)
        if arr_match:
            name, idx_str, expr = arr_match.groups()
            idx = self._eval_expr(idx_str)
            val = self._eval_expr(expr)
            var = self._find_var(name)
            if var and var.elements:
                var.elements[idx]["value"] = val
                self._hints.append(f"数组 {name}[{idx}] = {val}")
            return

        # 指针算术: p = p + 1 (only for int* type)
        ptr_arith = re.match(r'(\w+)\s*=\s*(\w+)\s*\+\s*(\d+)\s*$', s)
        if ptr_arith:
            target, ptr_name, offset = ptr_arith.groups()
            ptr_var = self._find_var(ptr_name)
            offset = int(offset)
            if ptr_var and ptr_var.type == "int*":
                old_addr = int(ptr_var.value, 16) if isinstance(
                    ptr_var.value, str) else ptr_var.value
                new_addr = f"0x{old_addr + offset * 4:03X}"
                ptr_var.value = new_addr
                self._update_points_to(ptr_var)
                self._hints.append(
                    f"指针 {ptr_name} + {offset}，地址从 0x{old_addr:03X} 移到 {new_addr}（+{offset*4} 字节）")
                return

        # 普通赋值
        m = re.match(r'(\w+)\s*=\s*(.+)$', s)
        if m:
            name, expr = m.groups()
            val = self._eval_expr(expr.strip())
            old_val = None
            v = self._find_var(name)
            if v:
                old_val = v.value
                v.value = val
            self._hints.append(f"{name} = {val}" + (f"（之前: {old_val}）" if old_val is not None and old_val != val else ""))

    def _handle_addr_assign(self, raw: str):
        """int *p = &a; 或 p = &a;"""
        s = raw.strip().rstrip(';').replace('int *', '').replace('int*', '').strip()
        m = re.match(r'(\w+)\s*=\s*&(\w+)\s*$', s)
        if m:
            ptr_name, target = m.groups()
            target_var = self._find_var(target)
            ptr_var = self._find_var(ptr_name)
            if target_var and ptr_var:
                ptr_var.value = target_var.address
                ptr_var.points_to = target
                self._hints.append(
                    f"&{target} 取出地址 {target_var.address}，{ptr_name} 存储该地址，现在 {ptr_name} 指向 {target}")

    def _handle_deref_assign(self, raw: str):
        """*p = value; — 支持数组元素写入"""
        s = raw.strip().rstrip(';')
        m = re.match(r'\*\s*(\w+)\s*=\s*(.+)$', s)
        if m:
            ptr_name, expr = m.groups()
            val = self._eval_expr(expr.strip())
            ptr_var = self._find_var(ptr_name)
            if ptr_var and ptr_var.points_to:
                target = self._find_var(ptr_var.points_to)
                if target:
                    # If target is an array, write to the element at pointer offset
                    if target.elements and isinstance(ptr_var.value, str) and ptr_var.value.startswith("0x"):
                        base = int(target.address, 16)
                        cur = int(ptr_var.value, 16)
                        offset = (cur - base) // 4
                        if 0 <= offset < len(target.elements):
                            old_val = target.elements[offset]["value"]
                            target.elements[offset]["value"] = val
                            self._hints.append(
                                f"*{ptr_name} 解引用 → 修改 {target.name}[{offset}]：{old_val} → {val}")
                            return
                    old_val = target.value
                    target.value = val
                    self._hints.append(
                        f"*{ptr_name} 解引用 → 修改 {target.name} 的值：{old_val} → {val}")
                else:
                    self._hints.append(f"*{ptr_name} = {val}（解引用写入）")
            else:
                self._hints.append(f"*{ptr_name} = {val}")

    def _handle_printf(self, raw: str):
        """提取 printf 参数并模拟输出"""
        s = raw.strip()
        m = re.match(r'printf\("(.+)"\s*(?:,\s*(.+))?\)\s*;', s)
        if m:
            fmt, args_str = m.groups()
            args = []
            if args_str:
                args = [a.strip() for a in args_str.split(',')]
            result = fmt
            for i, arg in enumerate(args):
                val = self._eval_expr(arg)
                if '%d' in result:
                    result = result.replace('%d', str(val), 1)
                elif '%s' in result:
                    result = result.replace('%s', str(val), 1)
            result = result.replace('\\n', '\n')
            self._output += result
            self._hints.append(f"printf 输出: {result.strip()}")

    def _handle_func_call(self, raw: str) -> Optional[int]:
        """f(&a, &b); — 实际执行函数调用"""
        s = raw.strip().rstrip(';')
        m = re.match(r'(\w+)\s*\(([^)]*)\)', s)
        if not m:
            return None
        func_name, args_str = m.groups()
        if func_name in ('return', 'printf', 'scanf', 'main'):
            return None  # built-in or already handled

        # Find the function definition
        if func_name not in self._func_map:
            self._hints.append(f"⚠ 函数 {func_name}() 未定义")
            return None

        # Parse arguments from the call
        raw_args = [a.strip() for a in args_str.split(',') if a.strip()]
        arg_vars = []
        for arg in raw_args:
            is_ref = arg.startswith('&')
            var_name = arg.lstrip('&')
            v = self._find_var(var_name)
            if v:
                arg_vars.append({'name': var_name, 'var': v, 'is_ref': is_ref})
            else:
                # Literal number argument
                try:
                    lit_val = int(var_name)
                    # Create a temporary pseudo-variable
                    lit_var = Variable(name=var_name, type="int", value=lit_val, address="0x000")
                    arg_vars.append({'name': var_name, 'var': lit_var, 'is_ref': False})
                except ValueError:
                    pass  # ignore unresolvable args

        # Find the function definition's parameter names
        func_start = self._func_map[func_name]
        _, func_raw, _, func_data = self._lines[func_start]
        params_str = func_data.get("params", "")
        param_names = [p.strip().split()[-1].lstrip('*') for p in params_str.split(',') if p.strip()]

        # Create new frame for the function
        frame = StackFrame(name=func_name)
        self._stack.append(frame)
        self._hints.append(f"调用 {func_name}()，创建栈帧 — 参数传递：")

        # Map arguments to parameters
        for i, pname in enumerate(param_names):
            if i < len(arg_vars):
                av = arg_vars[i]
                if av['is_ref']:
                    # &var → create pointer parameter holding var's address
                    addr = self._alloc_addr()
                    ptr_var = Variable(
                        name=pname, type="int*",
                        value=av['var'].address,
                        address=addr,
                        points_to=av['name'])
                    frame.variables[pname] = ptr_var
                    self._hints.append(
                        f"  {pname} ← &{av['name']} (地址 {av['var'].address})")
                else:
                    # Pass by value
                    addr = self._alloc_addr()
                    val_var = Variable(
                        name=pname, type=av['var'].type,
                        value=av['var'].value,
                        address=addr)
                    frame.variables[pname] = val_var
                    self._hints.append(
                        f"  {pname} ← {av['name']} (值: {av['var'].value})")

        # Save return address (line AFTER this call) and jump to function body
        self._return_stack.append(self._ip + 1)  # return here after function completes
        # Find first executable line in function body (after func_def, past brace_open)
        for i in range(func_start + 1, len(self._lines)):
            _, _, st, *_ = self._lines[i]
            if st not in ("skip", "empty", "brace_open", "func_def"):
                return i  # jump to first body line
        return None  # empty function body

    def _handle_return(self, raw: str) -> Optional[int]:
        """return 语句 — 弹出栈帧，跳回调用点"""
        s = raw.strip().rstrip(';')
        return_val = None
        m = re.match(r'return\s+(.+)$', s)
        if m:
            return_val = self._eval_expr(m.group(1))
            self._hints.append(f"返回 {return_val}")

        # Pop the function frame
        if self._stack:
            frame = self._stack.pop()
            self._hints.append(f"退出 {frame.name}()，栈帧弹出")

        # Jump back to caller
        if self._return_stack:
            ret_addr = self._return_stack.pop()
            return ret_addr  # jump back to call site (+1 will advance past call)

        # For main() return, just advance
        self._hints.append("程序结束")
        return None

    def _handle_brace_close(self, func: Optional[str]) -> Optional[int]:
        """} — 可能结束函数、循环或条件块"""
        # Check if this closes a loop (while/for only — do-while jumps in while_check)
        if self._loop_stack:
            loop_info = self._loop_stack[-1]
            loop_type = loop_info["type"]
            # do-while is handled by _handle_while_check, NOT here
            if loop_type != "do_while":
                loop_start = loop_info["start_ip"]
                loop_body_open = self._find_brace_open_after(loop_start + 1)
                if loop_body_open is not None and loop_body_open in self._brace_map:
                    if self._brace_map[loop_body_open] == self._ip:
                        if loop_type == "for":
                            incr = loop_info.get("incr", "")
                            if incr:
                                self._hints.append(f"for 递增: {incr}")
                                self._execute_inline_stmt(incr)
                        self._hints.append(
                            f"{loop_type} 循环体结束，跳回条件检查"
                        )
                        return loop_start

        # Check if this closes a switch block (v4.1: use brace_map, no hard limit)
        if self._switch_active:
            if self._ip in self._brace_map:
                open_idx = self._brace_map[self._ip]  # matching {
                # switch_start is immediately before the opening brace
                for check in (open_idx - 1, open_idx - 2):
                    if check >= 0 and self._lines[check][2] == "switch_start":
                        self._switch_active = False
                        self._case_matched = False
                        self._switch_value = None
                        self._hints.append("switch 块结束")
                        break

        # Check if this closes a function (explicit or implicit return)
        if self._stack:
            frame = self._stack[-1]
            # Check if this } closes the current function's scope
            # For explicit return, the frame was already popped by _handle_return
            # For void functions, the } is the implicit return
            if self._return_stack and frame.name != "main":
                # Verify this } is not inside a loop by checking brace matching
                is_fn_end = True
                if self._loop_stack:
                    loop = self._loop_stack[-1]
                    body_open = self._find_brace_open_after(loop["start_ip"] + 1)
                    if body_open is not None and body_open in self._brace_map:
                        if self._brace_map[body_open] == self._ip:
                            is_fn_end = False  # this } closes a loop, not the function

                if is_fn_end:
                    popped_frame = self._stack.pop()
                    self._hints.append(f"退出函数 {popped_frame.name}()，栈帧弹出")
                    ret_addr = self._return_stack.pop()
                    return ret_addr  # jump back to caller

        return None  # normal advance

    # ── 表达式求值 ────────────────────────────────────
    def _eval_expr(self, expr: str) -> int:
        """求值简单表达式"""
        expr = expr.strip()
        # 一元负号: -expr (v4 fix)
        if expr.startswith('-') and len(expr) > 1 and expr[1] != ' ':
            # Only handle unary minus (not subtraction "a - b")
            rest = expr[1:].strip()
            if re.match(r'^[a-zA-Z_(\d]', rest):
                inner_val = self._eval_expr(rest)
                return -inner_val if isinstance(inner_val, int) else -int(inner_val)
        # 解引用: *p
        deref = re.match(r'\*\s*(\w+)$', expr)
        if deref:
            ptr_name = deref.group(1)
            ptr = self._find_var(ptr_name)
            if ptr and ptr.points_to:
                target = self._find_var(ptr.points_to)
                if target:
                    # If target is an array, find the element at pointer's offset
                    if target.elements and isinstance(ptr.value, str) and ptr.value.startswith("0x"):
                        base = int(target.address, 16)
                        cur = int(ptr.value, 16)
                        offset = (cur - base) // 4
                        if 0 <= offset < len(target.elements):
                            return target.elements[offset]["value"]
                    return target.value if isinstance(target.value, int) else 0
            return 0
        # 取地址: &x
        addr = re.match(r'&\s*(\w+)$', expr)
        if addr:
            var = self._find_var(addr.group(1))
            if var:
                return int(var.address, 16) if isinstance(var.address, str) else var.address
        # 数组元素: arr[i]
        arr_match = re.match(r'(\w+)\[(\d+)\]', expr)
        if arr_match:
            name, idx_str = arr_match.groups()
            idx = self._eval_expr(idx_str)
            var = self._find_var(name)
            if var and var.elements and 0 <= idx < len(var.elements):
                return var.elements[idx]["value"]
        # 变量
        if re.match(r'^[a-zA-Z_]\w*$', expr):
            var = self._find_var(expr)
            if var:
                if isinstance(var.value, int):
                    return var.value
                if isinstance(var.value, str) and var.value.startswith("0x"):
                    return int(var.value, 16)
        # 数字
        try:
            return int(expr)
        except ValueError:
            pass
        # 简单算术: a + b 或 a - b 或 a + 1 等
        arith = re.match(r'(\w+)\s*([+\-])\s*(\w+|\d+)$', expr)
        if arith:
            name, op, val = arith.groups()
            base = self._eval_expr(name)
            operand = self._eval_expr(val)
            return base + operand if op == '+' else base - operand

        # 函数调用: add(3, 4) → inline execute and return result
        fc_match = re.match(r'(\w+)\(([^)]*)\)$', expr)
        if fc_match and fc_match.group(1) in self._func_map:
            return self._eval_func_call(fc_match.group(1), fc_match.group(2))
        return 0

    def _eval_func_call(self, func_name: str, args_str: str) -> int:
        """Inline execute a function call and return its value.
        Saves/restores state so step-by-step execution is not affected."""
        # Save current execution state
        saved_ip = self._ip
        saved_stack = list(self._stack)
        saved_return = list(self._return_stack)
        saved_loop = list(self._loop_stack)
        saved_next_addr = self._next_addr

        # Find function definition
        func_start = self._func_map[func_name]
        _, func_raw, _, func_data = self._lines[func_start]
        params_str = func_data.get("params", "")
        param_names = [p.strip().split()[-1].lstrip('*') for p in params_str.split(',') if p.strip()]

        # Create frame and map arguments
        frame = StackFrame(name=func_name)
        self._stack.append(frame)

        raw_args = [a.strip() for a in args_str.split(',') if a.strip()]
        for i, pname in enumerate(param_names):
            if i < len(raw_args):
                arg = raw_args[i]
                val = self._eval_expr(arg)
                addr = self._alloc_addr()
                v = Variable(name=pname, type="int", value=val, address=addr)
                frame.variables[pname] = v

        # Execute function body line by line until return or end
        result = 0
        body_ip = func_start + 1
        brace_depth = 1  # assume function has implicit opening brace
        _eval_skip_else = False  # flag: if was true → skip else body
        # Skip past explicit brace_open if present
        if body_ip < len(self._lines):
            _, _, st, *_ = self._lines[body_ip]
            if st == "brace_open":
                body_ip += 1

        while body_ip < len(self._lines):
            _, raw, st, *extra = self._lines[body_ip]
            data = extra[0] if extra else {}

            if st == "func_def":
                break  # hit another function → end
            if st == "brace_open":
                brace_depth += 1
            elif st == "brace_close":
                brace_depth -= 1
                if brace_depth <= 0:
                    break  # end of function body
            elif st == "return":
                s = raw.strip().rstrip(';')
                m = re.match(r'return\s+(.+)$', s)
                if m:
                    result = self._eval_expr(m.group(1))
                break
            elif st == "if_start":
                # Minimal if handling for inline execution
                cond = data.get("condition", "0")
                cond_result = self._eval_condition(cond)
                if cond_result:
                    # If true: execute body, then skip else (v4 fix)
                    _eval_skip_else = True
                else:
                    # Skip if body (find matching brace_close)
                    skip_depth = 0
                    for skip_ip in range(body_ip + 1, len(self._lines)):
                        _, _, sk_st, *_ = self._lines[skip_ip]
                        if sk_st == "brace_open":
                            skip_depth += 1
                        elif sk_st == "brace_close":
                            skip_depth -= 1
                            if skip_depth == 0:
                                body_ip = skip_ip  # jump to closing }
                                break
            elif st == "else_kw" and _eval_skip_else:
                # If was true — skip the else body (v4 fix)
                skip_depth = 0
                for skip_ip in range(body_ip + 1, len(self._lines)):
                    _, _, sk_st, *_ = self._lines[skip_ip]
                    if sk_st == "brace_open":
                        skip_depth += 1
                    elif sk_st == "brace_close":
                        skip_depth -= 1
                        if skip_depth == 0:
                            body_ip = skip_ip  # jump to closing }
                            break
                _eval_skip_else = False
            if st in ("var_decl_init", "var_decl", "assign", "deref_assign",
                      "addr_assign", "printf", "if_start", "else_kw"):
                # Execute simple statements inline
                if st == "var_decl_init":
                    s = raw.strip().rstrip(';')
                    dm = re.match(r'int\s+(\w+)\s*=\s*(.+)$', s)
                    if dm:
                        name, expr = dm.groups()
                        val = self._eval_expr(expr.strip())
                        addr = self._alloc_addr()
                        v = Variable(name=name, type="int", value=val, address=addr)
                        frame.variables[name] = v
                elif st == "var_decl":
                    s = raw.strip().rstrip(';')
                    dm = re.match(r'int\s+(\w+)\s*$', s)
                    if dm:
                        name = dm.group(1)
                        addr = self._alloc_addr()
                        frame.variables[name] = Variable(name=name, type="int", value=0, address=addr)
                elif st == "assign":
                    s = raw.strip().rstrip(';')
                    am = re.match(r'(\w+)\s*=\s*(.+)$', s)
                    if am:
                        name, expr = am.groups()
                        v = self._find_var(name)
                        if v:
                            v.value = self._eval_expr(expr.strip())
            body_ip += 1

        # Restore state
        self._ip = saved_ip
        self._stack = saved_stack
        self._return_stack = saved_return
        self._loop_stack = saved_loop
        self._next_addr = saved_next_addr
        return result

    # ── 状态查询 ──────────────────────────────────────
    def _get_state(self, for_history: bool = False) -> dict:
        """返回当前完整状态。

        for_history=True: strip lines/variables from the snapshot to save
        memory (history only needs _stack_data for step_back restoration).
        """
        variables = []
        lines = []

        if not for_history:
            for frame in self._stack:
                for name, var in frame.variables.items():
                    entry = {
                        "name": name,
                        "type": var.type,
                        "value": self._fmt_val(var),
                        "address": var.address,
                        "frame": frame.name,
                    }
                    if var.type == "int*" and var.points_to:
                        pts = self._find_var(var.points_to)
                        if pts:
                            entry["points_to"] = f"{pts.value} ({var.points_to})"
                    if var.elements:
                        entry["elements"] = var.elements
                    variables.append(entry)

            for i, (_, raw, stype, *_) in enumerate(self._lines):
                if stype not in ("empty", "skip", "brace_open", "brace_close", "unknown"):
                    lines.append({"num": i + 1, "text": raw, "active": i == self._ip})

        # 当前行号
        current_line = 0
        if self._ip < len(self._lines):
            current_line = self._ip + 1

        # Serialize stack frames for step_back restoration (v4 fix)
        stack_data = []
        for frame in self._stack:
            frame_vars = {}
            for name, var in frame.variables.items():
                frame_vars[name] = {
                    "name": var.name, "type": var.type,
                    "value": var.value, "address": var.address,
                    "size": var.size, "elements": var.elements,
                    "points_to": var.points_to,
                }
            stack_data.append({
                "name": frame.name, "return_line": frame.return_line,
                "variables": frame_vars,
            })

        return {
            "current_line": current_line,
            "lines": lines,
            "variables": variables,
            "stack_frames": [f.name for f in self._stack],
            "output": self._output,
            "hints": self._hints,
            "finished": self._finished,
            "_ip": self._ip,
            "_next_addr": self._next_addr,
            "_output": self._output,
            "_finished": self._finished,
            "_loop_stack": list(self._loop_stack),
            "_else_skip": self._else_skip,
            "_switch_active": self._switch_active,
            "_switch_value": self._switch_value,
            "_case_matched": self._case_matched,
            "_return_stack": list(self._return_stack),
            "_stack_data": stack_data,
        }

    @staticmethod
    def _fmt_val(var: Variable) -> str:
        if isinstance(var.value, int):
            return str(var.value)
        return str(var.value)

    @property
    def has_next(self) -> bool:
        return not self._finished and self._ip < len(self._lines)

    @property
    def has_prev(self) -> bool:
        return len(self._history) > 0
