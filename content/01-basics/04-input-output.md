---
title: "输入输出 — 让程序与用户对话"
slug: "input-output"
level: 1
order: 4
tags: ["printf", "scanf", "输入", "输出", "交互"]
---

# 输入输出 — 让程序与用户对话

前面我们只做了"输出"——程序单向告诉我们信息。现在让程序**读取用户输入**，实现真正的交互。

## printf 进阶

### 基本用法回顾

```c
printf("Hello\n");                   // 输出文字
printf("Age: %d\n", 25);            // 一个变量
printf("%d + %d = %d\n", 3, 5, 8); // 多个变量
```

### 格式化控制

```c
int n = 42;
float f = 3.14159;

printf("|%d|\n", n);        // |42|
printf("|%5d|\n", n);       // |   42|   (宽度 5，右对齐)
printf("|%-5d|\n", n);      // |42   |   (宽度 5，左对齐)
printf("|%05d|\n", n);      // |00042|   (宽度 5，前导零)

printf("|%f|\n", f);        // |3.141590|  (默认 6 位)
printf("|%.2f|\n", f);      // |3.14|      (保留 2 位)
printf("|%8.2f|\n", f);     // |    3.14|  (宽度 8，2 位)
```

## scanf — 读取用户输入

`scanf` 是 `printf` 的"反向"——从键盘读取数据存到变量里。

### ⚠️ 关键：必须用 `&` 取地址！

```c
int age;
scanf("%d", &age);    // ✅ 正确：&age 是 age 变量的地址
// scanf("%d", age);  // ❌ 错误：忘记 & 会导致程序崩溃！
```

### 读取不同类型

```c
int age;
float height;
char name[50];    // 字符串用字符数组

printf("Enter your age: ");
scanf("%d", &age);

printf("Enter your height (m): ");
scanf("%f", &height);

printf("Enter your name: ");
scanf("%s", name);   // 字符串不需要 &！

printf("\n--- Your Info ---\n");
printf("Name: %s\n", name);
printf("Age: %d\n", age);
printf("Height: %.2f m\n", height);
```

### scanf 格式占位符

| 占位符 | 读取类型 | 示例 |
|--------|---------|------|
| `%d` | 整数 | `scanf("%d", &x)` |
| `%f` | 浮点数 | `scanf("%f", &f)` |
| `%lf` | double | `scanf("%lf", &d)` |
| `%c` | 单个字符 | `scanf(" %c", &ch)` |
| `%s` | 字符串（无空格） | `scanf("%s", str)` |

### ⚠️ scanf 的坑

```c
// 坑1：%c 会读取上一次遗留的换行符
char ch;
scanf("%d", &num);    // 用户输入 42 然后回车
scanf("%c", &ch);     // ch 变成了换行符 '\n'！
// 解决：加一个空格
scanf(" %c", &ch);    // ✅ 跳过前导空白

// 坑2：%s 遇到空格就停止
char name[50];
scanf("%s", name);    // 输入 "Zhang San" → name 只得到 "Zhang"
// 解决：用 fgets (后面学)

// 坑3：不检查返回值
if (scanf("%d", &x) != 1) {
    printf("Invalid input!\n");   // 用户可能输入了字母
}
```

## 完整交互示例

```c
#include <stdio.h>

int main() {
    char name[50];
    int age;
    float score;

    printf("=== Student Info System ===\n\n");

    printf("Your name: ");
    scanf("%s", name);

    printf("Your age: ");
    scanf("%d", &age);

    printf("Your score: ");
    scanf("%f", &score);

    printf("\n========== Result ==========\n");
    printf("Name:  %s\n", name);
    printf("Age:   %d\n", age);
    printf("Score: %.1f\n", score);

    if (score >= 60) {
        printf("Status: PASS\n");
    } else {
        printf("Status: FAIL\n");
    }

    return 0;
}
```

## 要点速查

- `printf` 输出，`scanf` 输入
- `scanf` 的变量前要加 `&`（字符串除外）
- 格式占位符必须匹配变量类型
- `%c` 前加空格跳过空白字符
- `%s` 遇到空格就停——后面学 `fgets` 解决
- 始终检查 scanf 的返回值

**下一步**：[条件判断](/learn/if-else) — 让程序根据条件做出决策。
