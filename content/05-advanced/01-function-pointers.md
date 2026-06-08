---
title: "函数指针 — 把函数当参数传递"
slug: "function-pointers"
level: 5
order: 3
tags: ["函数指针", "回调", "qsort", "高阶函数"]
---

# 函数指针 — 把函数当参数传递

**函数指针**可以指向函数，从而实现回调（callback）、策略模式等高级技巧。

## 基本语法

```c
// 声明一个函数指针：
// 返回类型 (*指针名)(参数类型列表)
int (*func_ptr)(int, int);

// 指向一个函数：
int add(int a, int b) { return a + b; }
func_ptr = &add;   // 或 func_ptr = add;
int result = func_ptr(3, 5);  // 8
```

## 作为参数传递（回调函数）

```c
#include <stdio.h>

// 对数组每个元素应用一个操作
void for_each(int *arr, int n, void (*fn)(int*)) {
    for (int i = 0; i < n; i++) {
        fn(&arr[i]);
    }
}

void double_it(int *x) { *x *= 2; }
void print_int(int *x) { printf("%d ", *x); }

int main() {
    int arr[] = {1, 2, 3, 4, 5};
    int n = 5;

    for_each(arr, n, double_it);
    for_each(arr, n, print_int);  // 2 4 6 8 10
    return 0;
}
```

## qsort — 标准库中的函数指针

```c
#include <stdio.h>
#include <stdlib.h>

int compare_int(const void *a, const void *b) {
    return *(int*)a - *(int*)b;  // 升序
}

int compare_desc(const void *a, const void *b) {
    return *(int*)b - *(int*)a;  // 降序
}

int main() {
    int arr[] = {5, 2, 9, 1, 7};
    int n = 5;

    qsort(arr, n, sizeof(int), compare_int);
    for (int i = 0; i < n; i++) printf("%d ", arr[i]);
    // 输出: 1 2 5 7 9
    return 0;
}
```

## 函数指针数组

```c
int add(int a, int b) { return a + b; }
int sub(int a, int b) { return a - b; }
int mul(int a, int b) { return a * b; }

int main() {
    // 函数指针数组 — 像菜单一样选择操作
    int (*ops[])(int, int) = {add, sub, mul};

    printf("2+3=%d\n", ops[0](2, 3));  // 5
    printf("2-3=%d\n", ops[1](2, 3));  // -1
    printf("2*3=%d\n", ops[2](2, 3));  // 6
    return 0;
}
```

## 要点总结

- 声明格式：`返回类型 (*指针名)(参数类型)`
- 函数名本身就是函数地址
- 常用场景：qsort、事件回调、策略模式
- typedef 简化：`typedef int (*BinOp)(int, int);`
