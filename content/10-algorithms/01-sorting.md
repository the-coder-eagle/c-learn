---
title: "排序算法 — 从冒泡到快排"
slug: "sorting-algorithms"
level: 10
order: 1
tags: ["排序", "冒泡排序", "快速排序", "复杂度"]
---

# 排序算法 — 从冒泡到快排

排序是最基础的算法，理解不同排序算法的思想是算法入门的关键。

## 冒泡排序

最简单的排序 — 每轮把最大的"冒"到最后。

```c
void bubble_sort(int arr[], int n) {
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - 1 - i; j++) {
            if (arr[j] > arr[j + 1]) {
                int t = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = t;
            }
        }
    }
}
```

时间复杂度：O(n²)，稳定

## 快速排序

分治法 — 选 pivot，小的放左边，大的放右边，递归。

```c
void quick_sort(int arr[], int low, int high) {
    if (low >= high) return;

    int pivot = arr[high];
    int i = low - 1;

    for (int j = low; j < high; j++) {
        if (arr[j] < pivot) {
            i++;
            int t = arr[i]; arr[i] = arr[j]; arr[j] = t;
        }
    }
    int t = arr[i + 1]; arr[i + 1] = arr[high]; arr[high] = t;
    int pi = i + 1;

    quick_sort(arr, low, pi - 1);
    quick_sort(arr, pi + 1, high);
}
```

时间复杂度：O(n log n) 平均，O(n²) 最坏

## 算法对比

| 算法 | 最优 | 平均 | 最坏 | 空间 | 稳定 |
|------|------|------|------|------|------|
| 冒泡 | O(n) | O(n²) | O(n²) | O(1) | ✅ |
| 选择 | O(n²) | O(n²) | O(n²) | O(1) | ❌ |
| 插入 | O(n) | O(n²) | O(n²) | O(1) | ✅ |
| 快排 | O(n log n) | O(n log n) | O(n²) | O(log n) | ❌ |
| 归并 | O(n log n) | O(n log n) | O(n log n) | O(n) | ✅ |

## 完整演示

```c
#include <stdio.h>

void print_arr(int arr[], int n) {
    for (int i = 0; i < n; i++) printf("%d ", arr[i]);
    printf("\n");
}

int main() {
    int arr[] = {64, 34, 25, 12, 22, 11, 90};
    int n = 7;

    printf("Before: "); print_arr(arr, n);
    bubble_sort(arr, n);
    printf("After:  "); print_arr(arr, n);
    return 0;
}
```

## 要点总结

- 冒泡排序最简单，适合小数据（n < 100）
- 快速排序是最常用的通用排序算法
- 选择排序适合"找第 k 大/小"的场景
- C 标准库的 qsort 不需要手写排序
