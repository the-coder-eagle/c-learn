---
title: "二进制文件与错误处理"
slug: "binary-and-error"
level: 8
order: 2
tags: ["文件", "二进制", "fread", "fwrite", "ferror", "errno"]
---

# 二进制文件与错误处理

## 二进制读写

文本模式会转换换行符（Windows 上 `\n` → `\r\n`）。二进制模式原样读写。

```c
#include <stdio.h>

typedef struct {
    int id;
    float score;
} Record;

int main() {
    // 写二进制
    Record records[] = {{1, 92.5}, {2, 88.0}, {3, 95.5}};
    FILE *fp = fopen("data.bin", "wb");
    fwrite(records, sizeof(Record), 3, fp);
    fclose(fp);

    // 读二进制
    Record read_back[3];
    fp = fopen("data.bin", "rb");
    fread(read_back, sizeof(Record), 3, fp);
    fclose(fp);

    for (int i = 0; i < 3; i++) {
        printf("ID: %d, Score: %.1f\n", read_back[i].id, read_back[i].score);
    }
    return 0;
}
```

- `fwrite(ptr, size, count, fp)` — 写入 count 个大小为 size 的元素
- `fread(ptr, size, count, fp)` — 读取，返回实际读到的元素数

## 随机访问

```c
#include <stdio.h>

int main() {
    FILE *fp = fopen("data.bin", "rb");

    // 跳到第 3 个记录（索引 2）
    fseek(fp, 2 * sizeof(Record), SEEK_SET);

    Record r;
    fread(&r, sizeof(Record), 1, fp);
    printf("Record 3: ID=%d, Score=%.1f\n", r.id, r.score);

    // 查看当前位置
    long pos = ftell(fp);
    printf("Current position: %ld\n", pos);

    rewind(fp);  // 回到开头
    fclose(fp);
    return 0;
}
```

- `SEEK_SET` — 从文件头算
- `SEEK_CUR` — 从当前位置算
- `SEEK_END` — 从文件尾算

## 错误处理

```c
#include <stdio.h>
#include <errno.h>
#include <string.h>

int main() {
    FILE *fp = fopen("nonexistent.txt", "r");
    if (!fp) {
        printf("Error: %s\n", strerror(errno));
        perror("fopen");  // 自动打印错误原因
        return 1;
    }

    // 读操作出错检测
    char buf[10];
    if (fgets(buf, sizeof(buf), fp) == NULL) {
        if (ferror(fp)) {
            printf("Read error!\n");
        } else if (feof(fp)) {
            printf("End of file reached.\n");
        }
    }

    // 清除错误状态
    clearerr(fp);
    fclose(fp);
    return 0;
}
```

- `ferror(fp)` — 检查流是否有错误
- `feof(fp)` — 检查是否到文件尾
- `clearerr(fp)` — 清除错误和 EOF 标志
