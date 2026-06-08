---
title: "文件系统操作 — stat、目录遍历"
slug: "file-systems"
level: 11
order: 2
tags: ["stat", "目录", "文件系统", "seek"]
---

# 文件系统操作 — stat、目录遍历

除了读写文件内容，C 还可以获取文件元信息和遍历目录。

## stat — 获取文件信息

```c
#include <stdio.h>
#include <sys/stat.h>

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Usage: %s <filename>\n", argv[0]);
        return 1;
    }

    struct stat st;
    if (stat(argv[1], &st) != 0) {
        perror("stat");
        return 1;
    }

    printf("File: %s\n", argv[1]);
    printf("Size: %lld bytes\n", (long long)st.st_size);
    printf("Mode: %o\n", st.st_mode);
    printf("Is regular file? %s\n", S_ISREG(st.st_mode) ? "yes" : "no");
    printf("Is directory?    %s\n", S_ISDIR(st.st_mode) ? "yes" : "no");
    return 0;
}
```

## fseek 与 ftell — 随机访问

```c
#include <stdio.h>

int main() {
    FILE *fp = fopen("test.txt", "w+");
    fprintf(fp, "ABCDEFGHIJ");

    // 跳到文件末尾
    fseek(fp, 0, SEEK_END);
    long size = ftell(fp);
    printf("File size: %ld bytes\n", size);

    // 跳到第 3 个字节
    fseek(fp, 3, SEEK_SET);
    char ch = fgetc(fp);
    printf("Byte at offset 3: %c\n", ch);  // D

    fclose(fp);
    return 0;
}
```

## 目录遍历（POSIX）

```c
#include <stdio.h>
#include <dirent.h>

int main() {
    DIR *dir = opendir(".");
    if (dir == NULL) {
        perror("opendir");
        return 1;
    }

    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL) {
        printf("%s  ", entry->d_name);
        if (entry->d_type == DT_DIR) printf("[DIR]");
        printf("\n");
    }

    closedir(dir);
    return 0;
}
```

## 临时文件

```c
#include <stdio.h>

int main() {
    // tmpfile 自动创建、自动删除
    FILE *tmp = tmpfile();
    fprintf(tmp, "temporary data\n");
    rewind(tmp);
    char buf[100];
    fgets(buf, sizeof(buf), tmp);
    printf("Read: %s", buf);
    // 文件夹闭或程序退出时自动删除
    fclose(tmp);
    return 0;
}
```

## 要点总结

- `stat()` 获取文件大小、权限、类型
- `fseek()` + `ftell()` 实现文件随机访问
- `opendir()` / `readdir()` 遍历目录（POSIX）
- `tmpfile()` 创建自动清理的临时文件
