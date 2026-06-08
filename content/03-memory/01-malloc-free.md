---
title: "动态内存分配 — malloc 与 free"
slug: "malloc-free"
level: 3
order: 3
tags: ["malloc", "free", "堆内存", "指针"]
---

# 动态内存分配 — malloc 与 free

C 语言的变量通常分配在**栈**上，但栈空间有限（通常 1-8 MB）。当需要大块内存或运行时决定大小时，必须使用**堆内存**（heap）。

## 核心函数

| 函数 | 作用 | 头文件 |
|------|------|--------|
| `malloc(size)` | 分配 size 字节，不初始化 | `stdlib.h` |
| `calloc(n, size)` | 分配 n×size 字节，初始化为 0 | `stdlib.h` |
| `realloc(ptr, size)` | 调整已分配内存大小 | `stdlib.h` |
| `free(ptr)` | 释放 malloc/calloc/realloc 返回的内存 | `stdlib.h` |

## malloc 示例

```c
#include <stdio.h>
#include <stdlib.h>

int main() {
    int n = 5;
    // 分配 5 个 int 的空间
    int *arr = (int*)malloc(n * sizeof(int));

    if (arr == NULL) {
        printf("Memory allocation failed!\n");
        return 1;
    }

    // 使用分配的内存
    for (int i = 0; i < n; i++) {
        arr[i] = i * 10;
        printf("arr[%d] = %d\n", i, arr[i]);
    }

    // 必须释放！
    free(arr);
    return 0;
}
```

## calloc vs malloc

```c
// malloc: 未初始化（垃圾值）
int *a = malloc(5 * sizeof(int));

// calloc: 全部初始化为 0
int *b = calloc(5, sizeof(int));
```

## realloc 调整大小

```c
int *p = malloc(10 * sizeof(int));
// ... 发现不够，扩展到 20 个
p = realloc(p, 20 * sizeof(int));
```

## 常见错误

- **忘记 free** → 内存泄漏
- **free 后继续使用** → 悬空指针（use-after-free）
- **多次 free** → 未定义行为
- **free 栈变量** → 程序崩溃

## 要点总结

- `malloc` 分配不初始化的堆内存
- `calloc` 分配并清零
- `free` 释放 malloc/calloc/realloc 返回的指针
- 每次 malloc 必须对应一次 free
- 分配后检查 NULL（分配失败）
