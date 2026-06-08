---
title: "函数练习 — 把代码变成积木"
slug: "function-practice"
level: 3
order: 3
tags: ["函数", "练习", "模块化", "实战"]
---

# 函数练习 — 把代码变成积木

好的程序员把复杂问题分解成小函数。这里有 6 个练习，由浅入深。

## 1. 判断回文数 ★

写一个函数判断一个整数是否是回文数（正着读反着读一样）。

```c
int is_palindrome(int n) {
    int original = n, reversed = 0;
    while (n > 0) {
        reversed = reversed * 10 + n % 10;
        n /= 10;
    }
    return original == reversed;
}
// 121 → 1 (true)
// 123 → 0 (false)
```

## 2. 计算 BMI ★

```c
// BMI = 体重(kg) / 身高(m)²
float calc_bmi(float weight, float height) {
    return weight / (height * height);
}

const char* bmi_category(float bmi) {
    if (bmi < 18.5) return "Underweight";
    if (bmi < 25.0) return "Normal";
    if (bmi < 30.0) return "Overweight";
    return "Obese";
}
```

## 3. 数字转字符串（简易版）★★

把一个整数转换为汉字拼音（0-9）。用函数指针数组实现。

```c
const char* number_to_chinese(int n) {
    const char* words[] = {
        "ling", "yi", "er", "san",
        "si", "wu", "liu", "qi", "ba", "jiu"
    };
    if (n >= 0 && n <= 9) return words[n];
    return "unknown";
}
```

## 4. 简单加密 ★★

凯撒密码：每个字母向后移动固定位数。

```c
char caesar_encrypt(char ch, int shift) {
    if (ch >= 'a' && ch <= 'z')
        return 'a' + (ch - 'a' + shift) % 26;
    if (ch >= 'A' && ch <= 'Z')
        return 'A' + (ch - 'A' + shift) % 26;
    return ch;  // 非字母不变
}

void encrypt_string(const char* input, char* output, int shift) {
    int i = 0;
    while (input[i]) {
        output[i] = caesar_encrypt(input[i], shift);
        i++;
    }
    output[i] = '\0';
}
// "abc" shift=3 → "def"
// "xyz" shift=3 → "abc"
```

## 5. 简易计算器 ★★

用函数实现加减乘除，用函数指针选择操作。

```c
#include <stdio.h>

double add(double a, double b) { return a + b; }
double sub(double a, double b) { return a - b; }
double mul(double a, double b) { return a * b; }
double divide(double a, double b) {
    return b != 0 ? a / b : 0;
}

int main() {
    double (*ops[4])(double, double) = {add, sub, mul, divide};
    char symbols[] = {'+', '-', '*', '/'};

    double a, b; int op;
    printf("Enter a b op (0:+ 1:- 2:* 3:/): ");
    scanf("%lf %lf %d", &a, &b, &op);

    if (op >= 0 && op <= 3)
        printf("%.2f %c %.2f = %.2f\n", a, symbols[op], b, ops[op](a, b));
    return 0;
}
```

## 6. 递归：汉诺塔 ★★★

```c
#include <stdio.h>

void hanoi(int n, char from, char to, char aux) {
    if (n == 1) {
        printf("Move disk 1 from %c to %c\n", from, to);
        return;
    }
    hanoi(n - 1, from, aux, to);
    printf("Move disk %d from %c to %c\n", n, from, to);
    hanoi(n - 1, aux, to, from);
}

int main() {
    hanoi(3, 'A', 'C', 'B');
    return 0;
}
// 输出:
// Move disk 1 from A to C
// Move disk 2 from A to B
// Move disk 1 from C to B
// Move disk 3 from A to C
// Move disk 1 from B to A
// Move disk 2 from B to C
// Move disk 1 from A to C
```

## 设计好函数的 3 个原则

1. **单一职责**：一个函数只做一件事
2. **好名字**：函数名应该描述它做什么（`calc_bmi` 而不是 `f1`）
3. **短小精悍**：超过 30 行就该考虑拆分了
