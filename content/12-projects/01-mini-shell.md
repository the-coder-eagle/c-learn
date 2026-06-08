---
title: "Mini Shell — 构建简易命令行解释器"
slug: "mini-shell"
level: 12
order: 1
tags: ["shell", "fork", "exec", "项目"]
---

# Mini Shell — 构建简易命令行解释器

把学到的知识整合起来，构建一个能运行命令的简化版 shell。

## 核心概念

Unix shell 的工作原理：
1. 读取用户输入 → 2. 解析命令 → 3. fork 子进程 → 4. exec 执行 → 5. wait 等待

## 完整实现

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>

#define MAX_CMD 256
#define MAX_ARGS 64

int main() {
    char cmd[MAX_CMD];

    while (1) {
        printf("csh> ");
        fflush(stdout);

        if (fgets(cmd, MAX_CMD, stdin) == NULL) break;
        cmd[strcspn(cmd, "\n")] = '\0';  // 去换行

        if (strcmp(cmd, "exit") == 0) break;
        if (strlen(cmd) == 0) continue;

        // 解析命令和参数
        char *args[MAX_ARGS];
        int argc = 0;
        char *token = strtok(cmd, " ");
        while (token && argc < MAX_ARGS - 1) {
            args[argc++] = token;
            token = strtok(NULL, " ");
        }
        args[argc] = NULL;

        // fork + exec
        pid_t pid = fork();
        if (pid == 0) {
            // 子进程
            execvp(args[0], args);
            perror("execvp");
            exit(1);
        } else if (pid > 0) {
            // 父进程
            wait(NULL);
        } else {
            perror("fork");
        }
    }

    printf("Goodbye!\n");
    return 0;
}
```

## 运行示例

```bash
$ gcc -o csh mini-shell.c
$ ./csh
csh> ls
Makefile  csh  mini-shell.c
csh> echo Hello World
Hello World
csh> pwd
/home/user/projects
csh> exit
Goodbye!
```

## 代码解读

| 函数 | 作用 |
|------|------|
| `fgets` | 读取用户输入 |
| `strtok` | 分割命令和参数 |
| `fork()` | 创建子进程 |
| `execvp()` | 在子进程中执行命令 |
| `wait()` | 父进程等待子进程结束 |

## 改进方向

- 支持 `cd` 内置命令（使用 `chdir()`）
- 支持管道 `|`（pipe + dup2）
- 支持重定向 `>` `<`（open + dup2）
- 支持后台运行 `&`

## 要点总结

- fork 创建子进程，exec 替换进程映像
- 父进程 wait 等待子进程退出
- 这是 Linux 操作系统编程的入口
- 慢慢扩展功能，理解 Unix 哲学
