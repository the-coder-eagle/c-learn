---
title: "字符串输入输出"
slug: "string-io"
level: 6
order: 2
tags: ["字符串", "scanf", "gets", "fgets", "缓冲区"]
---

# 字符串输入输出

## scanf 系列

```c
#include <stdio.h>

int main() {
    char name[50];
    printf("What's your name? ");
    scanf("%s", name);     // ⚠️ 遇到空格就停止！
    printf("Hello, %s\n", name);
    return 0;
}
```

输入 `John Doe` → 输出 `John`（空格后的部分丢失）。

## 读取整行：fgets

```c
#include <stdio.h>
#include <string.h>

int main() {
    char line[200];
    printf("Enter a line: ");
    fgets(line, sizeof(line), stdin);

    // 去掉末尾的换行符
    line[strcspn(line, "\n")] = '\0';

    printf("You typed: %s\n", line);
    return 0;
}
```

- `fgets(buf, size, stdin)` — 安全读取一行，最多读 size-1 个字符
- `strcspn` — 查找换行符位置

## gets 的危险

```c
// ❌ 永远不要用 gets！
// gets(buffer);  // 没有长度限制，经典缓冲区溢出漏洞
```

早在 C11 标准中 `gets` 已被移除。只用 `fgets`。

## 格式化输出

```c
#include <stdio.h>

int main() {
    char s[] = "hello";
    printf("|%s|\n", s);       // |hello|
    printf("|%10s|\n", s);     // |     hello|  (右对齐，宽度 10)
    printf("|%-10s|\n", s);    // |hello     |  (左对齐)
    printf("|%.3s|\n", s);     // |hel|         (最多 3 字符)
    return 0;
}
```
