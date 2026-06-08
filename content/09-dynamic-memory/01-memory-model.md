---
title: "C 内存模型全景"
slug: "memory-model"
level: 9
order: 1
tags: ["内存模型", "text", "data", "bss", "heap", "stack"]
---

# C 内存模型全景

理解 C 程序在内存中的布局是成为高级 C 程序员的关键一步。

## 五大内存段

```
  高地址
┌──────────┐
│   Stack   │ ← 局部变量、函数参数、返回地址
│   (栈)    │   向下增长 (↓)
├──────────┤
│           │
│  空闲区域  │
│           │
├──────────┤
│   Heap    │ ← malloc/free 管理
│   (堆)    │   向上增长 (↑)
├──────────┤
│   BSS     │ ← 未初始化全局/静态变量
├──────────┤
│   Data    │ ← 已初始化全局/静态变量
├──────────┤
│   Text    │ ← 机器代码 + 只读数据
└──────────┘
  低地址
```

## 各段详解

### Text 段（代码段）
- 存放编译后的机器指令
- **只读**，防止程序修改自身
- 字符串常量也可能放这里（取决于编译器）

### Data 段（数据段）
```c
int global_init = 42;      // Data 段 — 已初始化
static int count = 0;      // Data 段 — 显式初始化为 0
char msg[] = "hello";      // Data 段 — 可修改的数组
```

### BSS 段
```c
int global_uninit;         // BSS 段 — 未初始化
static int counter;        // BSS 段
// BSS 段在程序启动时自动清零，不占磁盘空间
```

### Heap（堆）
```c
int *p = malloc(100);      // 堆
int *q = calloc(10, 4);    // 堆（清零）
// 需要 free，否则内存泄漏
```

### Stack（栈）
```c
void func(int a) {         // a → 栈
    int x = 10;            // x → 栈
    char buf[256];         // buf → 栈
}  // 函数返回后，以上全部释放
```

## sizeof 验证各段大小

```c
#include <stdio.h>
#include <stdlib.h>

int main() {
    int stack_var;
    int *heap_var = malloc(sizeof(int));

    printf("Stack addr: %p\n", &stack_var);
    printf("Heap addr:  %p\n", heap_var);
    printf("Code addr:  %p\n", main);

    printf("Size of int: %zu\n", sizeof(int));
    printf("Size of int*: %zu\n", sizeof(int*));

    free(heap_var);
    return 0;
}
```

## 要点总结

- Text/Data/BSS → 编译时确定大小
- Stack → 自动管理，速度快但空间有限
- Heap → 手动管理，灵活但容易出错
- 理解内存模型 = 理解 "变量在哪、何时创建、何时销毁"
