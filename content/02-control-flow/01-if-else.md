---
title: "条件判断 — if/else 与 switch"
slug: "if-else"
level: 2
order: 1
tags: ["if", "else", "switch", "条件", "分支"]
---

# 条件判断 — if/else 与 switch

程序不只是从上到下顺序执行——它需要**根据不同情况做不同的事**。这就是条件判断。

## if 基础

```c
if (条件) {
    // 条件为真（非0）时执行
}
```

```c
int score = 85;

if (score >= 60) {
    printf("Pass!\n");
}
```

## if-else

```c
if (score >= 60) {
    printf("Pass!\n");
} else {
    printf("Fail!\n");
}
```

## if-else if-else 多分支

```c
if (score >= 90) {
    printf("Grade: A\n");
} else if (score >= 80) {
    printf("Grade: B\n");
} else if (score >= 70) {
    printf("Grade: C\n");
} else if (score >= 60) {
    printf("Grade: D\n");
} else {
    printf("Grade: F\n");
}
```

**执行逻辑**：从上到下检查，遇到第一个为真的条件就执行对应的代码块，然后**跳过**后面所有分支。

## 嵌套 if

```c
int age = 25;
int has_id = 1;

if (age >= 18) {
    if (has_id) {
        printf("You may enter.\n");
    } else {
        printf("Please show your ID.\n");
    }
} else {
    printf("Too young.\n");
}
```

## 三元运算符（简洁版 if-else）

```c
// 常规写法
int max;
if (a > b) {
    max = a;
} else {
    max = b;
}

// 三元运算符（一行搞定）
int max = (a > b) ? a : b;
```

格式：`条件 ? 为真时的值 : 为假时的值`

## switch-case（多值判断）

当需要判断一个变量**等于**多个不同值时，`switch` 比多个 `if-else` 更清晰：

```c
int day = 3;

switch (day) {
    case 1:
        printf("Monday\n");
        break;
    case 2:
        printf("Tuesday\n");
        break;
    case 3:
        printf("Wednesday\n");
        break;
    case 4:
        printf("Thursday\n");
        break;
    case 5:
        printf("Friday\n");
        break;
    case 6:
    case 7:
        printf("Weekend!\n");
        break;
    default:
        printf("Invalid day\n");
}
```

### ⚠️ switch 注意事项

| 要点 | 说明 |
|------|------|
| 必须有 `break` | 否则会"穿透"到下一个 case |
| `default` | 所有 case 都不匹配时执行（可选） |
| 只能判断整数 | int / char / enum，不能是 float 或字符串 |
| 多个 case 可合并 | `case 6: case 7:` 共享同一段代码 |

### 忘记 break 的后果

```c
int n = 1;
switch (n) {
    case 1: printf("one\n");    // 没有 break！
    case 2: printf("two\n");    // 也会执行！
    case 3: printf("three\n");  // 也会执行！
}
// 输出：one two three （全都执行了！）
```

## 常见错误

```c
// ❌ 错误1：分号导致空语句
if (x > 0);     // 分号让 if 变成了"什么都不做"
    printf("x is positive\n");  // 这行总是执行！

// ❌ 错误2：赋值代替比较
if (x = 5)      // 这是赋值！不是比较！
if (x == 5)     // 这才是比较

// ❌ 错误3：字符串直接比较
char name[] = "Tom";
if (name == "Tom")  // ❌ 比较的是地址，不是内容
if (strcmp(name, "Tom") == 0)  // ✅ 用 strcmp
```

## 练习：成绩等级转换

```c
#include <stdio.h>

int main() {
    int score;
    printf("Enter score (0-100): ");
    scanf("%d", &score);

    if (score >= 90)
        printf("A\n");
    else if (score >= 80)
        printf("B\n");
    else if (score >= 70)
        printf("C\n");
    else if (score >= 60)
        printf("D\n");
    else
        printf("F\n");

    return 0;
}
```

## 要点速查

- `if (条件) { }` — 条件成立时执行
- `else { }` — 条件不成立时执行
- `else if` — 多条件链式判断
- `switch` 适合判断一个变量的多个具体值
- `break` 在 switch 中阻止穿透
- 不要混淆 `=` 和 `==`
