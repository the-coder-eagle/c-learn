---
title: "变量与数据类型 — 存储你的数据"
slug: "variables-and-types"
level: 1
order: 2
tags: ["变量", "数据类型", "int", "float", "char", "声明"]
---

# 变量与数据类型 — 存储你的数据

变量是存储数据的"盒子"。每个盒子有**名字**（变量名）、**类型**（能装什么）和**值**（装了什么）。

## 基本数据类型

| 类型 | 关键字 | 占内存 | 范围 | 示例 |
|------|--------|--------|------|------|
| 整数 | `int` | 4 字节 | -21亿 ~ 21亿 | `int age = 18;` |
| 小数 | `float` | 4 字节 | ~7 位精度 | `float pi = 3.14f;` |
| 双精度 | `double` | 8 字节 | ~15 位精度 | `double e = 2.71828;` |
| 字符 | `char` | 1 字节 | -128 ~ 127 | `char grade = 'A';` |

## 声明与初始化

```c
#include <stdio.h>

int main() {
    // 方式1：先声明，再赋值
    int age;
    age = 25;

    // 方式2：声明的同时初始化（推荐）
    float score = 95.5;

    // 方式3：一次声明多个
    int x = 1, y = 2, z = 3;

    printf("Age: %d, Score: %.1f\n", age, score);
    printf("x=%d, y=%d, z=%d\n", x, y, z);
    return 0;
}
```

## printf 格式占位符

| 占位符 | 对应类型 | 含义 |
|--------|---------|------|
| `%d` | int | 十进制整数 |
| `%f` | float/double | 小数 |
| `%.2f` | float/double | 保留 2 位小数 |
| `%c` | char | 单个字符 |
| `%s` | char[] | 字符串 |
| `%x` | int | 十六进制 |

```c
int age = 20;
float height = 1.75;
char grade = 'A';

printf("I'm %d years old, %.2f m tall, grade %c\n", age, height, grade);
```

## 变量命名规则

- ✅ 字母、数字、下划线：`score`, `player1`, `max_value`
- ✅ 以字母或下划线开头（不能数字开头）
- ❌ C 关键字：`int`, `if`, `return` 等
- ❌ 区分大小写：`Score` ≠ `score`

```c
int score;      // ✅
int _count;     // ✅
int player2;    // ✅
int 2player;    // ❌ 不能以数字开头
int if;         // ❌ if 是关键字
```

## 变量的值可以改变

```c
int x = 10;
printf("x = %d\n", x);   // 10
x = 20;                   // 改变值
printf("x = %d\n", x);   // 20
x = x + 5;                // 加 5
printf("x = %d\n", x);   // 25
```

## 常见错误

| 错误 | 后果 | 修正 |
|------|------|------|
| `int x = 3.14;` | 小数截断为 3 | 用 `float x = 3.14f;` |
| `printf("%d", 3.14);` | 乱码 | 用 `%f` 匹配浮点 |
| 未初始化变量 | 随机值 | `int x = 0;` |

## 要点速查

- 变量 = 名字 + 类型 + 值
- `int` 整数，`float` 小数，`char` 字符
- `printf` 用 `%d/%f/%c` 输出变量
- 变量名区分大小写，不能数字开头
