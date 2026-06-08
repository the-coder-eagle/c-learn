---
title: "数组基础 — 批量管理数据"
slug: "arrays-intro"
level: 4
order: 1
tags: ["数组", "索引", "遍历", "初始化"]
---

# 数组基础 — 批量管理数据

如果需要存储 100 个学生的成绩，声明 100 个变量 `s1, s2, s3...`？数组用一个名字管理整批数据。

## 声明与初始化

```c
// 声明：类型 名字[大小]
int scores[5];                        // 5 个 int

// 声明 + 初始化
int nums[5] = {10, 20, 30, 40, 50};  // 全部指定
int zeros[5] = {0};                   // 全部初始化为 0
int partial[5] = {1, 2};             // {1, 2, 0, 0, 0}

// 让编译器数大小
int arr[] = {1, 2, 3, 4, 5};         // 自动推断大小为 5
```

## 访问元素（索引从 0 开始）

```c
int arr[5] = {10, 20, 30, 40, 50};

arr[0]  // 第一个元素 = 10
arr[1]  // 第二个元素 = 20
arr[4]  // 最后一个元素 = 50
// arr[5] // ❌ 越界！
```

## 遍历数组

```c
int scores[5] = {85, 92, 78, 95, 88};

// 方式1：for 循环（最常用）
for (int i = 0; i < 5; i++) {
    printf("Student %d: %d\n", i + 1, scores[i]);
}

// 方式2：计算大小（不硬编码数字 5）
int n = sizeof(scores) / sizeof(scores[0]);
for (int i = 0; i < n; i++) {
    printf("%d ", scores[i]);
}
```

## 常见操作

```c
#include <stdio.h>

int main() {
    int arr[5] = {3, 1, 4, 1, 5};
    int n = 5;

    // 求和
    int sum = 0;
    for (int i = 0; i < n; i++) sum += arr[i];
    printf("Sum: %d\n", sum);  // 14

    // 找最大值
    int max = arr[0];
    for (int i = 1; i < n; i++)
        if (arr[i] > max) max = arr[i];
    printf("Max: %d\n", max);  // 5

    // 查找
    int target = 4, found = -1;
    for (int i = 0; i < n; i++) {
        if (arr[i] == target) { found = i; break; }
    }
    printf("Found 4 at index: %d\n", found);  // 2

    return 0;
}
```

## 数组与循环的经典配合

```c
// 反转数组
int arr[] = {1, 2, 3, 4, 5};
int n = 5;
for (int i = 0; i < n / 2; i++) {
    int t = arr[i];
    arr[i] = arr[n - 1 - i];
    arr[n - 1 - i] = t;
}
// 结果: {5, 4, 3, 2, 1}

// 冒泡排序
for (int i = 0; i < n - 1; i++) {
    for (int j = 0; j < n - 1 - i; j++) {
        if (arr[j] > arr[j + 1]) {
            int t = arr[j]; arr[j] = arr[j + 1]; arr[j + 1] = t;
        }
    }
}
```

## ⚠️ 数组的重要限制

- **大小固定**：声明后不能改变
- **不能整体赋值**：`arr2 = arr1;` 不行，要逐个元素复制
- **不能直接比较**：`if (arr1 == arr2)` 比较的是地址
- **越界不报错**：C 不检查数组越界，这是最危险的 bug 来源
- **索引从 0 开始**：`arr[n]` 的合法范围是 `0` 到 `n-1`
- **数组名是指针**：`arr` 等价于 `&arr[0]`

## 练习

```c
#include <stdio.h>

int main() {
    // 1. 计算平均分
    int scores[] = {88, 92, 76, 85, 95, 80, 78, 91};
    int n = sizeof(scores) / sizeof(scores[0]);

    int sum = 0;
    for (int i = 0; i < n; i++) sum += scores[i];
    printf("Average: %.1f\n", (float)sum / n);

    // 2. 统计及格人数
    int pass = 0;
    for (int i = 0; i < n; i++)
        if (scores[i] >= 60) pass++;
    printf("Passed: %d/%d\n", pass, n);

    return 0;
}
```

## 要点速查

- `类型 名字[大小]` 声明数组
- 索引从 0 开始，到 大小-1 结束
- `sizeof(arr)/sizeof(arr[0])` 计算元素个数
- 用 for 循环遍历数组
- 数组越界是静默 bug——C 不帮你检查
