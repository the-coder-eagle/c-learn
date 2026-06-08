---
title: "字符串基础 — 文字处理入门"
slug: "strings-intro"
level: 6
order: 1
tags: ["字符串", "char数组", "strlen", "strcpy", "strcmp"]
---

# 字符串基础 — 文字处理入门

C 语言没有专门的"字符串类型"。字符串就是**以 `\0` 结尾的字符数组**。

## 字符串的本质

```c
char str[] = "Hello";

// 内存中实际存储：
//   'H'  'e'  'l'  'l'  'o'  '\0'
//   [0]  [1]  [2]  [3]  [4]  [5]
```

`\0` (NULL 字符) 是字符串的**结束标记**——所有字符串函数都靠它判断字符串在哪结束。

## 声明字符串

```c
char s1[20] = "Hello";         // 数组（可修改）
char s2[] = "World";           // 自动计算大小（6 = 5字母 + \0）
char *s3 = "Hello";            // 指针指向字符串常量（不可修改！）

s1[0] = 'h';  // ✅ 数组可以修改
// s3[0] = 'h'; // ❌ 字符串常量不可修改（可能崩溃）
```

## 输入输出

```c
char name[50];

// scanf — 遇到空格就停
scanf("%s", name);   // 输入 "Zhang San" → name = "Zhang"

// fgets — 读取一行（包括空格）
fgets(name, sizeof(name), stdin);
// 输入 "Zhang San\n" → name = "Zhang San\n"
// 注意：fgets 保留末尾的 \n

// 去掉 fgets 的换行符
name[strcspn(name, "\n")] = '\0';
```

## 常用字符串函数 (`<string.h>`)

```c
#include <string.h>

// 长度
strlen("Hello");              // 5 (\0 不计入)

// 复制
char dest[20];
strcpy(dest, "Hello");        // dest = "Hello"
strncpy(dest, src, n);        // 安全版：最多复制 n 个字符

// 拼接
char buf[50] = "Hello ";
strcat(buf, "World");         // buf = "Hello World"

// 比较
strcmp("abc", "abc");         // 0  (相等)
strcmp("abc", "abd");         // -1 (abc < abd)
strcmp("xyz", "abc");         // >0 (xyz > abc)

// 查找
char *p = strstr("hello world", "world");  // 返回 "world" 的位置
char *q = strchr("hello", 'e');            // 返回 'e' 的位置
```

## ⚠️ strcmp 返回值

初学者最容易搞错的地方：

```c
if (strcmp(a, b) == 0)  // ✅ a 等于 b
if (strcmp(a, b))       // ❌ 非零 = 不相等，逻辑反了！
if (!strcmp(a, b))      // ✅ 也可以（但不如 == 0 清晰）
```

## 遍历字符串

```c
char str[] = "Hello";

// 方式1：用索引
for (int i = 0; str[i] != '\0'; i++) {
    printf("%c ", str[i]);
}

// 方式2：用指针
for (char *p = str; *p != '\0'; p++) {
    printf("%c ", *p);
}

// 方式3：简洁版
while (*str) {      // *str != '\0'
    printf("%c ", *str);
    str++;
}
```

## 字符判断函数 (`<ctype.h>`)

```c
#include <ctype.h>

isalpha('A');   // 是字母吗？ → 1
isdigit('5');   // 是数字吗？ → 1
isspace(' ');   // 是空白吗？ → 1
islower('a');   // 是小写吗？ → 1
isupper('Z');   // 是大写吗？ → 1
toupper('a');   // 转大写 → 'A'
tolower('Z');   // 转小写 → 'z'
```

## 练习：统计字符串

```c
#include <stdio.h>
#include <string.h>
#include <ctype.h>

int main() {
    char str[200];
    printf("Enter a string: ");
    fgets(str, sizeof(str), stdin);
    str[strcspn(str, "\n")] = '\0';

    int len = strlen(str);
    int letters = 0, digits = 0, spaces = 0;

    for (int i = 0; i < len; i++) {
        if (isalpha(str[i])) letters++;
        else if (isdigit(str[i])) digits++;
        else if (isspace(str[i])) spaces++;
    }

    printf("Length: %d\n", len);
    printf("Letters: %d\n", letters);
    printf("Digits: %d\n", digits);
    printf("Spaces: %d\n", spaces);
    return 0;
}
```

## 要点速查

- 字符串 = 以 `\0` 结尾的 char 数组
- `strlen` 返回长度（不含 `\0`）
- `strcmp` 比较，返回 0 表示相等
- `strcpy` 复制，`strcat` 拼接
- 用 `==` 比较字符串是错的
- `fgets` 保留 `\n`，记得去掉
