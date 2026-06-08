---
title: "实战项目 — 命令行计算器"
slug: "mini-calculator"
level: 3
order: 4
tags: ["项目", "计算器", "综合", "函数", "switch"]
---

# 实战项目 — 命令行计算器

把学到的知识组合起来，做一个真正可用的计算器程序。

## 功能需求

- ✅ 支持 `+` `-` `*` `/` 四种运算
- ✅ 支持连续计算（用上一次的结果继续算）
- ✅ 输入 `q` 退出
- ✅ 输入 `c` 清零
- ✅ 除零保护

## 完整代码

```c
#include <stdio.h>

double add(double a, double b) { return a + b; }
double sub(double a, double b) { return a - b; }
double mul(double a, double b) { return a * b; }
double divide(double a, double b) {
    if (b == 0) {
        printf("Error: Division by zero!\n");
        return 0;
    }
    return a / b;
}

void show_menu() {
    printf("\n=== Calculator ===\n");
    printf("Current: %.2f\n");
    printf("Options: + - * /  (c=clear, q=quit)\n");
    printf("Enter operator: ");
}

int main() {
    double result = 0;
    char op;

    printf("=== Command Line Calculator ===\n");
    printf("Enter first number: ");
    scanf("%lf", &result);
    getchar();  // 吃掉换行符

    while (1) {
        printf("\nCurrent: %.2f\n", result);
        printf("Op (+ - * / c q): ");
        scanf("%c", &op);
        getchar();

        if (op == 'q') break;
        if (op == 'c') { result = 0; continue; }

        double num;
        printf("Number: ");
        scanf("%lf", &num);
        getchar();

        switch (op) {
            case '+': result = add(result, num); break;
            case '-': result = sub(result, num); break;
            case '*': result = mul(result, num); break;
            case '/': result = divide(result, num); break;
            default:  printf("Unknown operator: %c\n", op);
        }
    }

    printf("Final result: %.2f\nGoodbye!\n", result);
    return 0;
}
```

## 运行示例

```
=== Command Line Calculator ===
Enter first number: 100

Current: 100.00
Op (+ - * / c q): +
Number: 50

Current: 150.00
Op (+ - * / c q): *
Number: 3

Current: 450.00
Op (+ - * / c q): /
Number: 9

Current: 50.00
Op (+ - * / c q): q
Final result: 50.00
Goodbye!
```

## 代码结构分析

```
main()
  ├── 读取初始值
  ├── 循环 {
  │     ├── 显示当前值
  │     ├── 读取操作符
  │     ├── 判断退出/清零
  │     ├── 读取操作数
  │     └── switch 分发到对应函数
  │   }
  └── 打印结果

add()  sub()  mul()  divide()
 ↑      ↑      ↑       ↑
 └──────┴──────┴───────┘
      各司其职的纯函数
```

## 扩展挑战

学有余力？试试添加这些功能：

1. **幂运算** `^`：用循环实现 `pow(base, exp)`
2. **取余** `%`：整数取余运算
3. **历史记录**：用数组保存最近 10 次计算结果
4. **括号表达式**：解析 `(2+3)*4` 这种输入
5. **单位转换**：`cm to inch`、`kg to lb`

## 你学到了什么

| 知识点 | 在项目中的体现 |
|--------|--------------|
| 函数定义与调用 | `add/sub/mul/divide` |
| 循环 | `while(1)` 主循环 |
| switch-case | 根据操作符分发 |
| scanf/printf | 用户输入输出 |
| if 条件判断 | 除零检查、退出判断 |
| 变量修改 | result 不断更新 |
