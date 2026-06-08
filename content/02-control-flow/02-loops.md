---
title: "循环 — for/while 重复执行"
slug: "loops"
level: 2
order: 2
tags: ["for", "while", "do-while", "循环", "迭代"]
---

# 循环 — for/while 重复执行

循环让一段代码反复执行。C 提供了三种循环结构。

## while — 当条件成立时循环

```c
while (条件) {
    // 条件为真时一直执行
}
```

```c
int i = 0;
while (i < 5) {
    printf("i = %d\n", i);
    i++;   // 别忘了改变条件，否则死循环！
}
```

### while 适用场景：不知道循环次数

```c
// 读取用户输入直到输入 0
int num;
printf("Enter numbers (0 to stop): ");
scanf("%d", &num);
while (num != 0) {
    printf("You entered: %d\n", num);
    scanf("%d", &num);
}
```

## for — 最常用的循环

```c
for (初始化; 条件; 更新) {
    // 循环体
}
```

```c
// 打印 0 到 4
for (int i = 0; i < 5; i++) {
    printf("i = %d\n", i);
}
```

**执行顺序**：
1. 初始化（只执行一次）
2. 检查条件 → 不满足则退出
3. 执行循环体
4. 执行更新
5. 回到步骤 2

### for 的灵活用法

```c
// 倒计数
for (int i = 10; i >= 1; i--) {
    printf("%d ", i);
}  // 10 9 8 7 6 5 4 3 2 1

// 步长 2
for (int i = 0; i <= 10; i += 2) {
    printf("%d ", i);
}  // 0 2 4 6 8 10

// 多个变量
for (int i = 0, j = 10; i < j; i++, j--) {
    printf("%d %d\n", i, j);
}
```

## do-while — 至少执行一次

```c
do {
    // 先执行一次，再检查条件
} while (条件);
```

```c
// 至少问一次用户输入
int answer;
do {
    printf("Guess a number (1-10): ");
    scanf("%d", &answer);
} while (answer != 7);
printf("Correct!\n");
```

## 三种循环对比

| 特性 | `for` | `while` | `do-while` |
|------|-------|---------|------------|
| 最少执行次数 | 0 | 0 | **1** |
| 适用场景 | 已知次数 | 未知次数 | 至少做一次 |
| 计数器 | 内置 | 手动 | 手动 |

## break 与 continue

```c
// break：立即退出循环
for (int i = 0; i < 10; i++) {
    if (i == 5) break;     // i=5 时退出
    printf("%d ", i);
}  // 输出: 0 1 2 3 4

// continue：跳过本次循环的剩余部分
for (int i = 0; i < 10; i++) {
    if (i % 2 == 0) continue;  // 跳过偶数
    printf("%d ", i);
}  // 输出: 1 3 5 7 9
```

## 嵌套循环

```c
// 打印乘法表
for (int i = 1; i <= 9; i++) {
    for (int j = 1; j <= i; j++) {
        printf("%d×%d=%-2d ", j, i, i * j);
    }
    printf("\n");
}
```

## 常见错误

| 错误 | 后果 | 修正 |
|------|------|------|
| `while(i<5);` | 分号导致空循环，死循环 | 去掉分号 |
| 忘记更新条件变量 | 死循环 | 循环体内改变条件 |
| `for(;;)` | 死循环（条件为空=永远真） | 明确条件或使用 break |
| 循环变量作用域 | `for(int i=0;...)` 的 i 在循环外不可见 | 在 for 前声明 |

## 练习：打印三角形

```c
#include <stdio.h>

int main() {
    int n = 5;
    for (int i = 1; i <= n; i++) {
        // 打印空格
        for (int j = 1; j <= n - i; j++)
            printf(" ");
        // 打印星号
        for (int k = 1; k <= 2 * i - 1; k++)
            printf("*");
        printf("\n");
    }
    return 0;
}
```

## 要点速查

- `for` — 已知循环次数
- `while` — 未知循环次数
- `do-while` — 至少一次
- `break` — 退出循环
- `continue` — 跳过本次，继续下次
- 嵌套循环：外层一次，内层一轮
