---
title: "第一个C程序 — Hello World 详解"
slug: "hello-world"
level: 1
order: 1
tags: ["入门", "printf", "main函数", "编译"]
---

# 第一个C程序 — Hello World 详解

欢迎来到 C 语言的世界！我们从最经典的程序开始。

## 你的第一行代码

```c
#include <stdio.h>

int main() {
    printf("Hello, World!\n");
    return 0;
}
```

**逐行解析：**

| 行 | 代码 | 含义 |
|----|------|------|
| 1 | `#include <stdio.h>` | 告诉编译器："我要使用标准输入输出库" |
| 2 | （空行） | 让代码更易读（不影响程序） |
| 3 | `int main() {` | 程序入口——每个C程序从这里开始执行 |
| 4 | `    printf(...)` | 向屏幕输出文字 |
| 5 | `    return 0;` | 告诉操作系统"程序正常结束" |
| 6 | `}` | main 函数的结束 |

## 每个部分详解

### `#include <stdio.h>`
- `#include` 是**预处理指令**（以 `#` 开头）
- `stdio.h` 是**头文件**，包含了 `printf` 等输入输出函数的声明
- `< >` 表示在系统目录中查找这个文件
- **如果不写这行，printf 就无法使用！**

### `int main() { }`
- `main` 是**函数名**——每个C程序必须有一个 main 函数
- `int` 是**返回值类型**——main 返回一个整数给操作系统
- `()` 是参数列表（目前为空）
- `{ }` 是函数体——所有要执行的代码写在里面

### `printf("Hello, World!\n");`
- `printf` = **print formatted**（格式化打印）
- `"Hello, World!\n"` 是要输出的**字符串**
- `\n` 是**换行符**（不可见，但让光标移到下一行）
- **分号 `;`** 是每条语句的结束标志——千万不能忘！

### `return 0;`
- `return` 结束函数并返回一个值
- `0` 表示"程序正常退出"
- 返回非零值通常表示"出错了"

## 常见错误 🔴

| 错误代码 | 编译器提示 | 怎么修 |
|---------|-----------|--------|
| 忘记 `;` | `expected ';'` | 在语句末尾加上分号 |
| 忘记 `"` | `missing terminating "` | 字符串必须用双引号包裹 |
| 忘记 `}` | `expected '}'` | 数一数花括号是否配对 |
| 拼写错误 | `'prinf' undeclared` | 检查函数名拼写（printf 不是 prinf） |
| 忘记 `#include` | `'printf' undeclared` | 加上 `#include <stdio.h>` |

## 🧪 动手试试

修改下面的代码，看看输出有什么变化：

1. **改文字**：把 `Hello, World!` 改成你的名字
2. **加一行**：在 `return 0;` 前再加一个 `printf` 输出你喜欢的句子
3. **试试去掉 \n**：看看没换行是什么效果

```c
#include <stdio.h>

int main() {
    printf("Hello, C Learn!\n");
    printf("I'm learning C programming.\n");
    return 0;
}
```

## 编译过程（了解即可）

```
源代码 (main.c)  →  编译器 (gcc/tcc)  →  可执行文件 (a.exe)
     ↑                                        ↑
   你写的文字                              计算机能运行的二进制
```

当你点击"Run"按钮时，平台自动完成：**编译 → 运行 → 显示结果**。

## 要点速查

- ✅ 每个 C 程序必须有 `main()` 函数
- ✅ `#include <stdio.h>` 引入标准库
- ✅ `printf()` 输出文字到屏幕
- ✅ `\n` 表示换行
- ✅ 每条语句以 `;` 结尾
- ✅ `return 0;` 表示程序正常结束

**下一步**：学习 [变量与数据类型](/learn/variables) —— 如何存储和操作数据。
