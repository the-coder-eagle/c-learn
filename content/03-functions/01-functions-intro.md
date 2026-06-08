---
title: "函数基础 — 组织你的代码"
slug: "functions-intro"
level: 3
order: 1
tags: ["函数", "参数", "返回值", "void", "模块化"]
---

# 函数基础 — 组织你的代码

函数是把一段代码**打包**成一个可重复使用的单元。你已经用过 `main()` 和 `printf()`——现在自己写。

## 为什么需要函数？

```c
// 没有函数：重复代码
int a = 5, b = 3;
int max1;
if (a > b) max1 = a; else max1 = b;

int c = 10, d = 7;
int max2;
if (c > d) max2 = c; else max2 = d;

// 有函数：写一次，到处用
int max(int x, int y) {
    return (x > y) ? x : y;
}
int max1 = max(5, 3);
int max2 = max(10, 7);
```

## 函数的结构

```c
返回类型 函数名(参数列表) {
    // 函数体
    return 返回值;
}
```

一个完整示例：

```c
#include <stdio.h>

// 函数定义
int add(int a, int b) {
    int result = a + b;
    return result;
}

int main() {
    int sum = add(3, 5);    // 调用函数
    printf("3 + 5 = %d\n", sum);  // 8
    return 0;
}
```

## 术语辨析

| 术语 | 含义 | 示例 |
|------|------|------|
| **形参** (parameter) | 函数定义中的变量 | `int add(int a, int b)` 中的 a 和 b |
| **实参** (argument) | 调用时传入的具体值 | `add(3, 5)` 中的 3 和 5 |
| **返回值** | 函数计算出的结果 | `return result` |
| **调用** | 执行函数 | `add(3, 5)` |

## 返回类型

```c
int get_age() { return 25; }     // 返回 int
float get_pi() { return 3.14f; } // 返回 float
char get_grade() { return 'A'; } // 返回 char

// void：不返回任何值
void say_hello() {
    printf("Hello!\n");
    // 没有 return 语句（或 return; 直接退出）
}
```

## 多参数函数

```c
// 三个参数：计算平均分
float average(float a, float b, float c) {
    return (a + b + c) / 3.0;
}

int main() {
    float avg = average(85.5, 92.0, 78.5);
    printf("Average: %.1f\n", avg);  // 85.3
    return 0;
}
```

## 函数声明（原型）vs 定义

```c
#include <stdio.h>

// 函数声明（原型）—— 告诉编译器"有这个函数"
int multiply(int a, int b);

int main() {
    printf("%d\n", multiply(6, 7));  // 42
    return 0;
}

// 函数定义 —— 函数的实际代码
int multiply(int a, int b) {
    return a * b;
}
```

**为什么需要声明？** C 编译器从上到下读取代码。如果函数定义在调用之后，就需要提前声明。

## 传值调用（重要！）

C 语言中，函数参数是**传值**的——函数拿到的是变量的**副本**，修改副本不影响原变量。

```c
void add_one(int x) {
    x = x + 1;          // 修改的是局部副本！
    printf("Inside: %d\n", x);
}

int main() {
    int n = 5;
    add_one(n);
    printf("Outside: %d\n", n);  // 还是 5！没有变！
    return 0;
}
```

**要修改外部变量，需要指针（后面学）。**

## 常见错误

```c
// ❌ 忘记声明
int main() {
    foo();  // 编译器不知道 foo 是什么
}

// ❌ 返回类型不匹配
int get_value() {
    return "hello";  // 返回字符串但声明为 int
}

// ❌ 忘记 return
int get_number() {
    int x = 5;
    // 忘记 return x;
}  // 未定义行为！
```

## 练习：实用函数

```c
#include <stdio.h>

// 判断素数
int is_prime(int n) {
    if (n < 2) return 0;
    for (int i = 2; i * i <= n; i++) {
        if (n % i == 0) return 0;
    }
    return 1;
}

// 计算阶乘
int factorial(int n) {
    int result = 1;
    for (int i = 1; i <= n; i++)
        result *= i;
    return result;
}

int main() {
    printf("Primes: ");
    for (int i = 2; i <= 20; i++)
        if (is_prime(i)) printf("%d ", i);
    printf("\n");

    printf("5! = %d\n", factorial(5));  // 120
    return 0;
}
```

## 要点速查

- 函数 = 输入（参数）→ 处理（函数体）→ 输出（返回值）
- `void` 表示无返回值
- 形参是定义时的变量，实参是调用时传入的值
- C 是传值调用，函数内修改参数不影响外部
- 定义在调用之前，或者提前声明
