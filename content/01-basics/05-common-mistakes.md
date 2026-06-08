---
title: "新手避坑指南 — 10 个最常见的错误"
slug: "common-mistakes"
level: 1
order: 5
tags: ["错误", "调试", "新手", "排错"]
---

# 新手避坑指南 — 10 个最常见的错误

每个 C 程序员都踩过这些坑。提前知道，少走弯路。

## 1. 忘记分号 `;`

```c
int x = 5    // ❌
printf("%d", x)    // ❌

int x = 5;   // ✅
printf("%d", x);   // ✅
```

C 语言中每条语句必须以 `;` 结束。忘了就编译报错 `expected ';'`。

## 2. `=` 和 `==` 搞混

```c
int x = 5;
if (x = 10)     // ❌ 这是赋值！条件永远为真！
if (x == 10)    // ✅ 这才是比较
```

**口诀**：一个等号是赋值，两个等号是比较。

## 3. scanf 忘记 `&`

```c
int age;
scanf("%d", age);    // ❌ 程序崩溃或结果错误
scanf("%d", &age);   // ✅ 必须加 & 取地址
```

例外：字符串 `char str[50]; scanf("%s", str);` 不需要 `&`。

## 4. 整数除法截断

```c
float result = 5 / 2;    // result = 2.0 不是 2.5！
float result = 5.0 / 2;  // ✅ result = 2.5
```

两个整数相除结果还是整数。至少让一个是浮点数。

## 5. 数组越界

```c
int arr[5] = {1, 2, 3, 4, 5};
arr[5] = 6;    // ❌ 最大索引是 4！
arr[10] = 10;  // ❌ 写到了别人的内存！
```

数组索引从 0 开始，`arr[5]` 的合法索引是 0~4。

## 6. 字符串比较不能用 `==`

```c
char name[] = "Tom";
if (name == "Tom")           // ❌ 比较的是地址！
if (strcmp(name, "Tom") == 0) // ✅ 用 strcmp
```

需要 `#include <string.h>`。

## 7. 忘记初始化变量

```c
int x;          // x 的值是随机的！
printf("%d", x); // 可能输出任何数字

int x = 0;      // ✅ 始终初始化
```

## 8. 循环条件写错导致死循环

```c
int i = 0;
while (i < 10) {
    printf("%d ", i);
    // 忘记 i++; ← 死循环！
}

// 或者分号坑：
while (i < 10); {   // ← 分号让循环体为空！
    printf("hi");
}
```

## 9. 忘记 `#include`

```c
// 忘记 #include <stdio.h>
int main() {
    printf("hi");   // ❌ printf undeclared
}
```

用了哪个库的函数，就要 include 对应的头文件。

## 10. 花括号不配对

```c
int main() {
    if (x > 0) {
        printf("positive\n");
    // 忘记关闭 if 的花括号！
    return 0;
}  // ❌ 编译器报错：expected '}'
```

**技巧**：写 `{` 时立即写 `}`，再往中间填代码。

## 排错流程

当你看到编译错误时，按这个顺序检查：

1. **读错误信息**：编译器通常告诉你是哪一行出了什么问题
2. **检查分号**：每条语句末尾都有 `;` 吗？
3. **检查括号配对**：`{ }` `( )` `" "` 都成对吗？
4. **检查拼写**：变量名和函数名拼对了吗？
5. **检查 include**：用到的函数都 include 了吗？
6. **检查类型匹配**：`printf` 的 `%d` 对应 int，`%f` 对应 float

## 常见编译错误速查

| 编译器信息 | 通常原因 |
|-----------|---------|
| `expected ';'` | 忘记分号 |
| `undeclared` | 拼写错误或忘记 include |
| `expected '}'` | 花括号不配对 |
| `lvalue required` | 赋值左边不是变量 |
| `implicit declaration` | 函数未声明 |
