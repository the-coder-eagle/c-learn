---
title: "命令行参数 — argc 与 argv"
slug: "command-line-args"
level: 11
order: 1
tags: ["argc", "argv", "命令行", "getopt"]
---

# 命令行参数 — argc 与 argv

C 程序可以通过 `main` 的参数接收命令行输入。

## 基础用法

```c
#include <stdio.h>

int main(int argc, char *argv[]) {
    printf("参数个数: %d\n", argc);

    for (int i = 0; i < argc; i++) {
        printf("argv[%d] = %s\n", i, argv[i]);
    }
    return 0;
}
```

```bash
$ ./program hello world 42
参数个数: 4
argv[0] = ./program
argv[1] = hello
argv[2] = world
argv[3] = 42
```

## 参数解析

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Usage: %s <name> [count]\n", argv[0]);
        return 1;
    }

    char *name = argv[1];
    int count = (argc >= 3) ? atoi(argv[2]) : 1;

    for (int i = 0; i < count; i++) {
        printf("Hello, %s!\n", name);
    }
    return 0;
}
```

## 环境变量

```c
#include <stdio.h>
#include <stdlib.h>

int main() {
    char *home = getenv("HOME");
    char *path = getenv("PATH");

    if (home) printf("HOME = %s\n", home);
    if (path) printf("PATH = %s\n", path);

    // setenv 修改环境变量
    setenv("MY_VAR", "hello", 1);
    printf("MY_VAR = %s\n", getenv("MY_VAR"));
    return 0;
}
```

## 要点总结

- `argc` — 参数个数（含程序名）
- `argv` — 参数值数组（全部是字符串）
- `argv[0]` — 程序名
- `atoi()` 把字符串转整数
- `getenv()` / `setenv()` 读写环境变量
