---
title: "栈与队列 — 基础数据结构"
slug: "stack-and-queue"
level: 4
order: 4
tags: ["栈", "队列", "数组", "链表", "数据结构"]
---

# 栈与队列

**栈**和**队列**是最常用的线性数据结构，区别在于元素的进出顺序。

## 栈 (Stack) — 后进先出 (LIFO)

像一摞盘子：最后放上去的，最先取下来。

### 数组实现

```c
#include <stdio.h>
#define MAX 100

typedef struct {
    int data[MAX];
    int top;
} Stack;

void init(Stack *s) { s->top = -1; }
int is_empty(Stack *s) { return s->top == -1; }
int is_full(Stack *s) { return s->top == MAX - 1; }

void push(Stack *s, int val) {
    if (!is_full(s)) s->data[++s->top] = val;
}

int pop(Stack *s) {
    if (!is_empty(s)) return s->data[s->top--];
    return -1;
}

int peek(Stack *s) {
    if (!is_empty(s)) return s->data[s->top];
    return -1;
}

int main() {
    Stack s; init(&s);
    push(&s, 10); push(&s, 20); push(&s, 30);
    printf("%d\n", pop(&s));  // 30
    printf("%d\n", pop(&s));  // 20
    printf("%d\n", peek(&s)); // 10
    return 0;
}
```

## 队列 (Queue) — 先进先出 (FIFO)

像排队买票：先来的先服务。

### 链表实现

```c
#include <stdio.h>
#include <stdlib.h>

typedef struct QNode {
    int data;
    struct QNode *next;
} QNode;

typedef struct {
    QNode *front;
    QNode *rear;
} Queue;

void init(Queue *q) { q->front = q->rear = NULL; }
int is_empty(Queue *q) { return q->front == NULL; }

void enqueue(Queue *q, int val) {
    QNode *node = malloc(sizeof(QNode));
    node->data = val; node->next = NULL;
    if (q->rear == NULL) {
        q->front = q->rear = node;
    } else {
        q->rear->next = node;
        q->rear = node;
    }
}

int dequeue(Queue *q) {
    if (is_empty(q)) return -1;
    QNode *tmp = q->front;
    int val = tmp->data;
    q->front = q->front->next;
    if (q->front == NULL) q->rear = NULL;
    free(tmp);
    return val;
}

int main() {
    Queue q; init(&q);
    enqueue(&q, 1); enqueue(&q, 2); enqueue(&q, 3);
    printf("%d\n", dequeue(&q));  // 1
    printf("%d\n", dequeue(&q));  // 2
    printf("%d\n", dequeue(&q));  // 3
    return 0;
}
```

## 对比总结

| 特性 | 栈 (Stack) | 队列 (Queue) |
|------|-----------|-------------|
| 原则 | LIFO | FIFO |
| 操作 | push/pop/peek | enqueue/dequeue |
| 应用 | 函数调用、撤销、括号匹配 | BFS、消息队列、打印队列 |
| 实现 | 数组 O(1) | 数组（循环队列）/链表 O(1) |

## 要点总结

- 栈：后进先出，push/pop 都在同一端
- 队列：先进先出，enqueue 在尾部，dequeue 在头部
- 数组实现栈需要维护 top 指针
- 链表实现队列需要维护 front 和 rear 指针
