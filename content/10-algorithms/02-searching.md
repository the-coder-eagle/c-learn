---
title: "查找算法 — 二分查找与更多"
slug: "searching-algorithms"
level: 10
order: 2
tags: ["二分查找", "线性查找", "哈希", "复杂度"]
---

# 查找算法 — 二分查找与更多

查找是计算机科学中最常见的操作之一。

## 线性查找（O(n)）

```c
int linear_search(int arr[], int n, int target) {
    for (int i = 0; i < n; i++) {
        if (arr[i] == target) return i;
    }
    return -1;  // 未找到
}
```

适合任意数组，不需要排序。

## 二分查找（O(log n)）

要求：数组**已排序**。

```c
int binary_search(int arr[], int n, int target) {
    int left = 0, right = n - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;  // 防溢出
        if (arr[mid] == target) return mid;
        if (arr[mid] < target) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
```

### 二分查找变体

```c
// 查找第一个等于 target 的位置
int lower_bound(int arr[], int n, int target) {
    int left = 0, right = n;
    while (left < right) {
        int mid = left + (right - left) / 2;
        if (arr[mid] >= target) right = mid;
        else left = mid + 1;
    }
    return left;
}
```

## 完整演示

```c
#include <stdio.h>

int main() {
    // 二分查找需要有序数组
    int arr[] = {1, 3, 5, 7, 9, 11, 13, 15};
    int n = 8;
    int x = 7;

    int idx = binary_search(arr, n, x);
    if (idx != -1)
        printf("Found %d at index %d\n", x, idx);
    else
        printf("%d not found\n", x);

    return 0;
}
```

## 算法对比

| 算法 | 时间复杂度 | 前提条件 | 适用场景 |
|------|-----------|---------|---------|
| 线性查找 | O(n) | 无 | 小数据或无序 |
| 二分查找 | O(log n) | 有序 | 有序数组 |
| 哈希查找 | O(1) | 哈希表 | 大量查询 |

## 要点总结

- 二分查找 O(log n) — 比线性查找 O(n) 快得多
- 前提是数据有序（需要先排序）
- `mid = left + (right - left) / 2` 防止整数溢出
- 标准库 `bsearch()` 可用于二分查找
- n=10⁶ 时：线性查找 ~10⁶ 次，二分查找 ~20 次
