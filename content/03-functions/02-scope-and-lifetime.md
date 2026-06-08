---
title: "作用域与生命周期"
slug: "scope-and-lifetime"
level: 3
order: 2
tags: ["作用域", "局部变量", "全局变量", "static", "生命周期"]
---

# 作用域与生命周期

变量的"可见范围"叫作用域，"存活时间"叫生命周期。

## 局部变量

在 `{}` 内部声明的变量，只在这个块内可见。

```c
#include <stdio.h>

void foo() {
    int x = 42;    // 局部变量，foo 之外不可见
    printf("x = %d\n", x);
}

int main() {
    foo();
    // printf("%d", x);  // ❌ 编译错误：x 不在作用域内
    return 0;
}
```

## 全局变量

在所有函数外部声明，整个文件可见。

```c
#include <stdio.h>

int counter = 0;   // 全局变量

void increment() {
    counter++;
}

int main() {
    increment();
    increment();
    printf("counter = %d\n", counter);  // 2
    return 0;
}
```

⚠️ 谨慎使用全局变量：任何函数都能修改，调试困难。

## static 变量

函数内的 `static` 变量在多次调用间保持值。

```c
#include <stdio.h>

void count() {
    static int n = 0;   // 只初始化一次
    n++;
    printf("called %d times\n", n);
}

int main() {
    count();  // called 1 times
    count();  // called 2 times
    count();  // called 3 times
    return 0;
}
```

- 局部变量：每次调用重新创建
- static 局部变量：程序运行期间一直存在
- 全局变量：整个程序生命周期
