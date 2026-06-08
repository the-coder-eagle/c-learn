---
title: "内存管理常见陷阱"
slug: "memory-pitfalls"
level: 9
order: 2
tags: ["悬空指针", "内存泄漏", "双重释放", "缓冲区溢出"]
---

# 内存管理常见陷阱

动态内存是 C 语言最强大的功能，也是最危险的。以下是必须避开的坑。

## 陷阱 1：忘记 free（内存泄漏）

```c
void leak() {
    int *p = malloc(1000);
    // 忘记 free(p) — 这 1000 字节永远回不去了
}  // p 指针变量销毁了，但堆上的内存还在
```

**检测工具**：Valgrind（Linux）、Address Sanitizer

## 陷阱 2：悬空指针（Use-After-Free）

```c
int *p = malloc(sizeof(int));
*p = 42;
free(p);
// p 现在是"悬空指针" — 指向已释放的内存
printf("%d\n", *p);  // 未定义行为！
```

**修复**：free 后立即设为 NULL

```c
free(p);
p = NULL;  // 之后再访问 p 至少会崩溃而非悄悄出错
```

## 陷阱 3：双重释放

```c
int *p = malloc(100);
free(p);
free(p);  // 崩溃！p 指向的内存已经不属于你了
```

## 陷阱 4：缓冲区溢出

```c
char buf[10];
strcpy(buf, "this string is way too long");  // 写穿了 buf！
// 覆盖了栈上的其他数据 — 安全漏洞！
```

**修复**：使用安全版本

```c
strncpy(buf, src, sizeof(buf) - 1);
buf[sizeof(buf) - 1] = '\0';  // 确保结尾有 0
```

## 陷阱 5：返回局部变量地址

```c
int* bad() {
    int x = 42;
    return &x;  // x 在函数返回时就消失了！
}
```

## 陷阱 6：realloc 失败导致泄漏

```c
int *p = malloc(10);
int *new_p = realloc(p, 100);
if (new_p == NULL) {
    // realloc 失败！p 仍然有效，但 new_p 是 NULL
    // 如果直接 p = realloc(p, ...) — 泄漏！
}
// 正确做法：
int *tmp = realloc(p, 100);
if (tmp) p = tmp;
else free(p);  // 处理失败情况
```

## 点石成金的原则

1. 🌟 **每次 malloc 都要有对应的 free**
2. 🌟 **free 后立即设为 NULL**
3. 🌟 **检查 malloc/calloc/realloc 返回值是否为 NULL**
4. 🌟 **使用安全函数（strncpy, snprintf）代替不安全版本**
5. 🌟 **不要返回局部变量的地址**
