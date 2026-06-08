---
title: "高级指针 — 二级指针与指针数组"
slug: "advanced-pointers"
level: 5
order: 4
tags: ["二级指针", "指针数组", "动态二维数组", "高级指针"]
---

# 高级指针 — 二级指针与指针数组

掌握了基础指针后，来看更复杂的用法：二级指针、指针数组和动态二维数组。

## 二级指针

**二级指针**是指向指针的指针。常用于函数中修改指针本身。

```c
#include <stdio.h>
#include <stdlib.h>

// 在函数中分配内存并修改外部的指针
void allocate(int **p, int n) {
    *p = malloc(n * sizeof(int));
}

int main() {
    int *arr = NULL;
    allocate(&arr, 5);  // &arr 是 int** 类型
    for (int i = 0; i < 5; i++) arr[i] = i;
    free(arr);
    return 0;
}
```

## 指针数组 vs 数组指针

```c
int *ptr_arr[10];    // 指针数组：10 个 int* 元素
int (*arr_ptr)[10];  // 数组指针：指向 int[10] 的指针
```

### 指针数组常见用途：命令行参数

```c
int main(int argc, char *argv[]) {  // char* 数组
    for (int i = 0; i < argc; i++) {
        printf("argv[%d] = %s\n", i, argv[i]);
    }
    return 0;
}
```

## 动态二维数组

```c
#include <stdio.h>
#include <stdlib.h>

int main() {
    int rows = 3, cols = 4;

    // 分配行指针数组
    int **matrix = malloc(rows * sizeof(int*));
    for (int i = 0; i < rows; i++) {
        matrix[i] = malloc(cols * sizeof(int));
    }

    // 赋值
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            matrix[i][j] = i * cols + j;
            printf("%2d ", matrix[i][j]);
        }
        printf("\n");
    }

    // 释放（逆序）
    for (int i = 0; i < rows; i++) free(matrix[i]);
    free(matrix);
    return 0;
}
```

## 函数返回指针

```c
// 返回堆上的数组
int* create_range(int n) {
    int *arr = malloc(n * sizeof(int));
    for (int i = 0; i < n; i++) arr[i] = i + 1;
    return arr;  // 调用者负责 free
}

int main() {
    int *nums = create_range(10);
    for (int i = 0; i < 10; i++) printf("%d ", nums[i]);
    free(nums);
    return 0;
}
```

## 要点总结

- `int **p` 是指向 int* 的指针
- 二级指针用于在函数中修改指针本身
- 指针数组 `int *arr[N]` — N 个指针
- 动态二维数组需要两层 malloc
- 释放时逆序 free（先释放行，再释放行指针数组）
