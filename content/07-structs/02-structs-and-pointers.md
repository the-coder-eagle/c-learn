---
title: "结构体与指针"
slug: "structs-and-pointers"
level: 7
order: 2
tags: ["结构体", "指针", "箭头运算符", "链表节点"]
---

# 结构体与指针

结构体和指针结合是 C 语言的强大特性，也是链表、树等数据结构的基石。

## 指向结构体的指针

```c
#include <stdio.h>

typedef struct {
    int x;
    int y;
} Point;

int main() {
    Point p = {10, 20};
    Point *ptr = &p;

    // 两种访问方式等价
    printf("(*ptr).x = %d\n", (*ptr).x);  // 10
    printf("ptr->x  = %d\n", ptr->x);     // 10 (推荐)
    return 0;
}
```

`ptr->member` 是 `(*ptr).member` 的语法糖，更清晰。

## 结构体传参

```c
#include <stdio.h>
#include <stdlib.h>

typedef struct { int x, y; } Point;

// 传值：复制整个结构体（慢）
void move_by_value(Point p, int dx, int dy) {
    p.x += dx;  // 只修改副本，不影响原值！
    p.y += dy;
}

// 传指针：只传 8 字节地址（快）
void move_by_pointer(Point *p, int dx, int dy) {
    p->x += dx;  // 直接修改原值
    p->y += dy;
}

int main() {
    Point p1 = {0, 0};
    move_by_value(p1, 5, 5);
    printf("by value: (%d, %d)\n", p1.x, p1.y);    // (0, 0) 没变！

    move_by_pointer(&p1, 5, 5);
    printf("by ptr:   (%d, %d)\n", p1.x, p1.y);     // (5, 5)
    return 0;
}
```

**原则**：除非结构体很小（≤ 8 字节），否则传指针。

## 自引用结构体（链表节点）

```c
typedef struct Node {
    int data;
    struct Node *next;  // 指向同类型的指针
} Node;
```

这就是链表的基本单元——每个节点指向下一个同类节点。
