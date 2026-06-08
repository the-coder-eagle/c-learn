"""
C Code Simulator — 教学用逐行执行引擎
支持子集: int, int*, 数组, 函数调用, printf, &, *, 赋值, 算术
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
    """C 代码逐行模拟执行器"""

    def __init__(self, code: str):
        self._raw = code
        self._lines = []          # [(line_num, text, type), ...]
        self._ip = 0              # instruction pointer (index into _lines)
        self._stack: list[StackFrame] = []
        self._next_addr = 0x100   # 虚拟地址分配器
        self._output = ""         # printf 累积输出
        self._history: list[dict] = []  # 每步的状态快照（用于回退）
        self._finished = False
        self._hints: list[str] = []
        self._parse()

    # ── 解析 ──────────────────────────────────────────
    def _parse(self):
        """将代码分解为可执行的行列表"""
        raw_lines = self._raw.split('\n')
        self._lines = []
        in_function = False
        brace_depth = 0
        current_func = None

        for raw in raw_lines:
            stripped = raw.strip()
            if not stripped:
                self._lines.append((len(raw_lines), raw, "empty"))
                continue

            # 跳过 include 和注释
            if stripped.startswith('#') or stripped.startswith('//'):
                self._lines.append((len(raw_lines), raw, "skip"))
                continue

            # 函数定义头 (handles brace on same line like "int main() {")
            func_match = re.match(
                r'(void|int)\s+(\w+)\s*\(([^)]*)\)\s*\{?\s*$', stripped)
            if func_match and not in_function:
                ret_type, name, params = func_match.groups()
                self._lines.append((len(raw_lines), raw, "func_def",
                                    {"name": name, "params": params}))
                brace_depth += 1  # always increment for function entry
                in_function = True
                current_func = name
                continue

            # 大括号 (only count stand-alone braces)
            if stripped == '{':
                self._lines.append((len(raw_lines), raw, "brace_open"))
                continue
            if stripped == '}':
                self._lines.append((len(raw_lines), raw, "brace_close"))
                continue

            # 普通语句
            if stripped.endswith(';'):
                stmt_type = self._classify_stmt(stripped, current_func)
                self._lines.append(
                    (len(raw_lines), raw, stmt_type, {"func": current_func}))
            elif stripped.endswith('{'):
                brace_depth += 1
                self._lines.append((len(raw_lines), raw, "stmt_block"))
            else:
                self._lines.append((len(raw_lines), raw, "unknown"))

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
        if '= &' in s:
            return "addr_assign"
        if '*p' in s.lower() or s.startswith('*'):
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
            # 如果是指针，更新指向信息
            if v.type == "int*":
                self._update_points_to(v)

    def _update_points_to(self, ptr: Variable):
        """更新指针的 points_to 信息"""
        if not isinstance(ptr.value, str) or not ptr.value.startswith("0x"):
            ptr.points_to = None
            return
        # 在所有栈帧中查找地址匹配的变量
        for frame in reversed(self._stack):
            for var in frame.variables.values():
                if var.address == ptr.value and var.name != ptr.name:
                    ptr.points_to = var.name
                    return
        ptr.points_to = None

    # ── 执行一步 ──────────────────────────────────────
    def step(self) -> dict:
        """执行当前行，前进一行，返回状态"""
        if self._finished:
            return self._get_state()

        # 保存快照（用于回退）
        self._history.append(self._get_state())

        if self._ip >= len(self._lines):
            self._finished = True
            return self._get_state()

        _, raw, stmt_type, *extra = self._lines[self._ip]
        data = extra[0] if extra else {}
        current_func = data.get("func")

        self._hints = []

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
                self._handle_func_call(raw)
            elif stmt_type == "return":
                self._handle_return(raw)
            elif stmt_type == "brace_close":
                self._handle_brace_close(current_func)
            # skip, empty, brace_open, unknown — 前进但不执行
        except Exception as e:
            self._hints.append(f"⚠ 执行错误: {e}")

        self._ip += 1
        return self._get_state()

    def step_back(self) -> dict:
        """回退一步"""
        if self._history:
            prev = self._history.pop()
            # Restore state from snapshot
            self._ip = prev["_ip"]
            self._next_addr = prev["_next_addr"]
            self._output = prev["_output"]
            self._finished = prev["_finished"]
            self._hints = []
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

    def run_all(self) -> dict:
        """运行到结束"""
        while not self._finished:
            self.step()
        return self._get_state()

    # ── 语句处理器 ────────────────────────────────────
    def _handle_func_def(self, data: dict):
        """进入函数定义"""
        name = data["name"]
        params_str = data.get("params", "")
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
        """int x = 5; 或 int *p = &a; 或 int arr[3] = {1,2,3};"""
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

        # 指针算术: p = p + 1
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
        """*p = value;"""
        s = raw.strip().rstrip(';')
        m = re.match(r'\*\s*(\w+)\s*=\s*(.+)$', s)
        if m:
            ptr_name, expr = m.groups()
            val = self._eval_expr(expr.strip())
            ptr_var = self._find_var(ptr_name)
            if ptr_var and ptr_var.points_to:
                target = self._find_var(ptr_var.points_to)
                if target:
                    old_val = target.value
                    target.value = val
                    # 如果是数组元素，也更新
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
                # 替换 %d, %s 等
                if '%d' in result:
                    result = result.replace('%d', str(val), 1)
                elif '%s' in result:
                    result = result.replace('%s', str(val), 1)
                elif '\\n' in result:
                    result = result.replace('\\n', '\n')
            result = result.replace('\\n', '\n')
            self._output += result
            self._hints.append(f"printf 输出: {result.strip()}")

    def _handle_func_call(self, raw: str):
        """f(&a, &b); — 函数调用"""
        s = raw.strip().rstrip(';')
        m = re.match(r'(\w+)\s*\(([^)]*)\)', s)
        if m:
            func_name, args_str = m.groups()
            if func_name == 'return':
                return
            # 简单处理：为被调函数创建新栈帧，传递参数
            # 对于我们的子集，参数是 &var 形式
            arg_names = [a.strip().lstrip('&') for a in args_str.split(',') if a.strip()]
            self._hints.append(
                f"调用 {func_name}({', '.join(arg_names)})——参数传递：")

            for arg_name in arg_names:
                v = self._find_var(arg_name)
                if v:
                    self._hints.append(
                        f"  &{arg_name} → 传递地址 {v.address}（值: {v.value}）")

    def _handle_return(self, raw: str):
        """return 语句"""
        s = raw.strip().rstrip(';')
        m = re.match(r'return\s+(.+)$', s)
        if m:
            val = self._eval_expr(m.group(1))
            self._hints.append(f"返回 {val}")
        else:
            self._hints.append("函数返回")

    def _handle_brace_close(self, func: Optional[str]):
        """} — 可能是函数结束，弹出栈帧"""
        if func and self._stack and self._stack[-1].name == func:
            frame = self._stack.pop()
            self._hints.append(f"退出函数 {frame.name}()，栈帧弹出")

    # ── 表达式求值 ────────────────────────────────────
    def _eval_expr(self, expr: str) -> int:
        """求值简单表达式"""
        expr = expr.strip()
        # 解引用: *p
        deref = re.match(r'\*\s*(\w+)$', expr)
        if deref:
            ptr_name = deref.group(1)
            ptr = self._find_var(ptr_name)
            if ptr and ptr.points_to:
                target = self._find_var(ptr.points_to)
                if target:
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
        # 简单算术: a + b 或 a - b
        arith = re.match(r'(\w+)\s*([+\-])\s*(\d+)$', expr)
        if arith:
            name, op, val = arith.groups()
            base = self._eval_expr(name)
            return base + int(val) if op == '+' else base - int(val)
        return 0

    # ── 状态查询 ──────────────────────────────────────
    def _get_state(self) -> dict:
        """返回当前完整状态"""
        variables = []

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

        # 当前行号
        current_line = 0
        if self._ip < len(self._lines):
            current_line = self._ip + 1

        lines = []
        for i, (_, raw, stype, *_) in enumerate(self._lines):
            if stype not in ("empty", "skip", "brace_open", "brace_close", "unknown"):
                lines.append({"num": i + 1, "text": raw, "active": i == self._ip})

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
