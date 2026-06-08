---
title: "栈与堆 — 内存布局"
slug: "stack-vs-heap"
level: 3
order: 4
tags: ["栈", "堆", "内存布局", "作用域"]
---

# 栈与堆 — C 程序的内存布局

理解 C 程序的内存布局是写出安全、高效代码的基础。

## 内存分段

```
高地址 ┌─────────────┐
      │    栈 (Stack) │ ← 局部变量、函数调用帧
      │    ↓↓↓        │    自动管理，FILO
      ├─────────────┤
      │              │
      │   空闲区域    │
      │              │
      ├─────────────┤
      │   堆 (Heap)   │ ← malloc 分配
      │    ↑↑↑        │    手动管理
      ├─────────────┤
      │  BSS 段       │ ← 未初始化的全局/静态变量 (初始为 0)
      ├─────────────┤
      │  Data 段      │ ← 已初始化的全局/静态变量
      ├─────────────┤
      │  Text 段      │ ← 程序代码（只读）
低地址 └─────────────┘
```

## 栈 vs 堆 对比

| 特性 | 栈 (Stack) | 堆 (Heap) |
|------|-----------|----------|
| 分配方式 | 自动 | 手动 (malloc/free) |
| 速度 | 极快（移动指针） | 较慢（查找空闲块） |
| 大小 | 有限（1-8 MB） | 受系统内存限制 |
| 生命周期 | 函数返回即释放 | 直到 free 才释放 |
| 碎片 | 无 | 可能产生碎片 |

## 代码演示

```c
#include <stdio.h>
#include <stdlib.h>

int global_x = 10;      // Data 段
static int static_y;     // BSS 段（初始为 0）

void demo() {
    int stack_var = 42;             // 栈
    int *heap_var = malloc(100);    // 堆（100 字节）

    printf("Stack var address: %p\n", &stack_var);
    printf("Heap var address:  %p\n", heap_var);
    printf("Global var addr:   %p\n", &global_x);

    free(heap_var);  // 释放堆内存
}

int main() {
    demo();
    // stack_var 已在 demo 返回时自动释放
    // global_x 在程序退出时释放
    return 0;
}
```

## 典型错误：返回局部变量地址

```c
// 错误示例 — 不要这样做！
int* bad_function() {
    int x = 42;
    return &x;  // x 在函数返回后失效！
}

// 正确做法：使用堆
int* good_function() {
    int *p = malloc(sizeof(int));
    *p = 42;
    return p;  // 调用者负责 free
}
```

## 要点总结

- 局部变量在栈上，自动释放
- malloc 在堆上，必须手动 free
- 不要返回指向局部变量的指针
- 全局/静态变量在 Data/BSS 段，程序运行期间一直存在
