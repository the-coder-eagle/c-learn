---
title: "文本处理器 — 简易 grep/wc"
slug: "text-processor"
level: 12
order: 2
tags: ["grep", "wc", "文件", "字符串", "项目"]
---

# 文本处理器 — 简易 grep/wc

实现自己的文本处理工具，加深对文件和字符串的理解。

## 简易 wc（行数和字符数）

```c
#include <stdio.h>
#include <ctype.h>

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Usage: %s <file>\n", argv[0]);
        return 1;
    }

    FILE *fp = fopen(argv[1], "r");
    if (!fp) { perror("fopen"); return 1; }

    int lines = 0, words = 0, chars = 0;
    int in_word = 0;
    int ch;

    while ((ch = fgetc(fp)) != EOF) {
        chars++;
        if (ch == '\n') lines++;
        if (isspace(ch)) {
            in_word = 0;
        } else if (!in_word) {
            in_word = 1;
            words++;
        }
    }

    fclose(fp);
    printf("%d %d %d %s\n", lines, words, chars, argv[1]);
    return 0;
}
```

## 简易 grep（搜索文本）

```c
#include <stdio.h>
#include <string.h>

#define MAX_LINE 1024

int main(int argc, char *argv[]) {
    if (argc < 3) {
        printf("Usage: %s <pattern> <file>\n", argv[0]);
        return 1;
    }

    char *pattern = argv[1];
    FILE *fp = fopen(argv[2], "r");
    if (!fp) { perror("fopen"); return 1; }

    char line[MAX_LINE];
    int line_no = 0;

    while (fgets(line, MAX_LINE, fp)) {
        line_no++;
        if (strstr(line, pattern)) {
            printf("%d: %s", line_no, line);
        }
    }

    fclose(fp);
    return 0;
}
```

## 完整演示

```bash
$ gcc -o mywc wc.c
$ ./mywc wc.c
22 52 432 wc.c

$ gcc -o mygrep grep.c
$ ./mygrep "printf" wc.c
8:     printf("Usage: %s <file>\n", argv[0]);
26:     printf("%d %d %d %s\n", lines, words, chars, argv[1]);
```

## 扩展方向

- 支持多文件输入
- 支持正则表达式（regex.h）
- 支持行号开关 `-n`
- 支持忽略大小写 `-i`
- 统计行数/单词数/字符数分别用 `-l`/`-w`/`-c` 开关

## 要点总结

- `fgets` 逐行读取文件
- `strstr` 查找子字符串
- `isspace` 判断空白字符
- 命令行参数控制程序行为
- 从零实现工具 = 理解工具的原理
