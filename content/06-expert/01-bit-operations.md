---
title: "位运算 — 底层操作的艺术"
slug: "bit-operations"
level: 6
order: 3
tags: ["位运算", "位掩码", "权限", "底层"]
---

# 位运算 — 底层操作的艺术

C 语言提供了 6 种位运算符，让你像 CPU 一样操作单个 bit。

## 运算符一览

| 运算符 | 名称 | 示例 | 结果（二进制） |
|--------|------|------|---------------|
| `&` | 按位与 | `0b1100 & 0b1010` | `0b1000` |
| `\|` | 按位或 | `0b1100 \| 0b1010` | `0b1110` |
| `^` | 按位异或 | `0b1100 ^ 0b1010` | `0b0110` |
| `~` | 按位取反 | `~0b0000` | `0b1111` |
| `<<` | 左移 | `1 << 3` | `8` |
| `>>` | 右移 | `8 >> 2` | `2` |

## 常见技巧

```c
#include <stdio.h>

int main() {
    int x = 42;

    // 判断奇偶
    printf("%d is %s\n", x, (x & 1) ? "odd" : "even");

    // 第 k 位是否为 1
    int k = 3;
    printf("bit %d is %s\n", k, (x >> k) & 1 ? "1" : "0");

    // 设置第 k 位为 1
    x = x | (1 << k);       // set bit

    // 清零第 k 位
    x = x & ~(1 << k);      // clear bit

    // 翻转第 k 位
    x = x ^ (1 << k);       // toggle bit

    // 判断是否是 2 的幂
    int n = 64;
    printf("%d is %s power of 2\n", n,
           (n > 0 && (n & (n - 1)) == 0) ? "a" : "not a");

    return 0;
}
```

## 权限掩码实战

```c
#include <stdio.h>

// 定义权限位
#define PERM_READ   0x01  // 0001
#define PERM_WRITE  0x02  // 0010
#define PERM_EXEC   0x04  // 0100
#define PERM_DELETE 0x08  // 1000

void show_perms(int perm) {
    printf("r:%s w:%s x:%s d:%s\n",
        (perm & PERM_READ)  ? "Y" : "N",
        (perm & PERM_WRITE) ? "Y" : "N",
        (perm & PERM_EXEC)  ? "Y" : "N",
        (perm & PERM_DELETE)? "Y" : "N");
}

int main() {
    int user_perm = 0;

    // 授予读和写
    user_perm |= PERM_READ | PERM_WRITE;
    show_perms(user_perm);  // r:Y w:Y x:N d:N

    // 添加执行权限
    user_perm |= PERM_EXEC;
    show_perms(user_perm);  // r:Y w:Y x:Y d:N

    // 移除写权限
    user_perm &= ~PERM_WRITE;
    show_perms(user_perm);  // r:Y w:N x:Y d:N

    return 0;
}
```

## 位运算的典型应用

- **权限系统**：用一个 int 存储多个布尔标志
- **状态压缩**：8 个 bool → 1 个 char
- **哈希/加密**：位混淆
- **图形/嵌入式**：像素操作、寄存器读写
- **算法优化**：用位运算替代乘除法（`x << 3` 替代 `x * 8`）

## 要点总结

- `&` (与) 用于清零和检测位
- `|` (或) 用于设置位
- `^` (异或) 用于翻转位
- `<<` / `>>` 用于移位
- 用 `1 << k` 生成只有第 k 位为 1 的掩码
- 位掩码是 C 语言的经典模式，理解它让你写出更底层的代码
