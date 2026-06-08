---
title: "文件操作基础"
slug: "file-io-intro"
level: 8
order: 1
tags: ["文件", "FILE", "fopen", "fclose", "fprintf", "fscanf"]
---

# 文件操作基础

程序运行时的数据在内存中，断电就没了。文件让数据持久保存。

## 打开与关闭

```c
#include <stdio.h>

int main() {
    FILE *fp = fopen("test.txt", "w");  // "w" = 写模式（覆盖）

    if (fp == NULL) {
        printf("无法打开文件!\n");
        return 1;
    }

    fclose(fp);  // 记得关闭！
    return 0;
}
```

### 文件模式

| 模式 | 含义 |
|------|------|
| `"r"` | 只读，文件必须存在 |
| `"w"` | 只写，覆盖已有文件 |
| `"a"` | 追加，在末尾写入 |
| `"r+"` | 读写，文件必须存在 |
| `"w+"` | 读写，覆盖已有文件 |
| `"rb"` `"wb"` | 二进制模式 |

## 写文件

```c
#include <stdio.h>

int main() {
    FILE *fp = fopen("scores.txt", "w");

    fprintf(fp, "Name: %s, Score: %d\n", "Alice", 95);
    fputs("Another line\n", fp);

    fclose(fp);
    return 0;
}
```

## 读文件

```c
#include <stdio.h>

int main() {
    FILE *fp = fopen("scores.txt", "r");
    if (!fp) return 1;

    char line[200];
    // 逐行读取
    while (fgets(line, sizeof(line), fp)) {
        printf("%s", line);
    }

    fclose(fp);
    return 0;
}
```

## 格式化读写

```c
// 写入
int score = 95;
fprintf(fp, "%d\n", score);

// 读取
int score;
fscanf(fp, "%d", &score);
```

⚠️ 永远检查 `fopen` 的返回值 — 文件可能不存在、权限不够、磁盘满。
