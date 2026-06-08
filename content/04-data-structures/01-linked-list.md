---
title: "链表 — 动态数据结构基础"
slug: "linked-list"
level: 4
order: 3
tags: ["链表", "struct", "指针", "数据结构"]
---

# 链表 — 动态数据结构基础

数组大小固定，插入删除需要移动元素。**链表**解决了这个问题：每个节点独立分配，通过指针连接。

## 单向链表节点

```c
struct Node {
    int data;
    struct Node *next;  // 指向下一个节点
};
```

## 创建和遍历

```c
#include <stdio.h>
#include <stdlib.h>

struct Node {
    int data;
    struct Node *next;
};

// 创建新节点
struct Node* create_node(int data) {
    struct Node *node = malloc(sizeof(struct Node));
    node->data = data;
    node->next = NULL;
    return node;
}

// 遍历打印
void print_list(struct Node *head) {
    struct Node *cur = head;
    while (cur != NULL) {
        printf("%d -> ", cur->data);
        cur = cur->next;
    }
    printf("NULL\n");
}

int main() {
    // 创建：1 → 2 → 3
    struct Node *head = create_node(1);
    head->next = create_node(2);
    head->next->next = create_node(3);

    print_list(head);  // 1 -> 2 -> 3 -> NULL

    // 释放链表
    struct Node *cur = head;
    while (cur != NULL) {
        struct Node *tmp = cur;
        cur = cur->next;
        free(tmp);
    }
    return 0;
}
```

## 插入操作

### 在头部插入（O(1)）

```c
struct Node* insert_head(struct Node *head, int data) {
    struct Node *new_node = create_node(data);
    new_node->next = head;
    return new_node;  // 新节点成为新的 head
}
```

### 在尾部插入（O(n)）

```c
struct Node* insert_tail(struct Node *head, int data) {
    struct Node *new_node = create_node(data);
    if (head == NULL) return new_node;

    struct Node *cur = head;
    while (cur->next != NULL) cur = cur->next;
    cur->next = new_node;
    return head;
}
```

## 删除操作

```c
// 删除第一个值为 target 的节点
struct Node* delete_node(struct Node *head, int target) {
    if (head == NULL) return NULL;

    // 删除头节点
    if (head->data == target) {
        struct Node *new_head = head->next;
        free(head);
        return new_head;
    }

    // 查找要删除的节点
    struct Node *cur = head;
    while (cur->next != NULL && cur->next->data != target) {
        cur = cur->next;
    }

    if (cur->next != NULL) {
        struct Node *tmp = cur->next;
        cur->next = cur->next->next;
        free(tmp);
    }
    return head;
}
```

## 要点总结

- 链表节点 = 数据 + 指向下一个节点的指针
- 插入删除 O(1)（已知位置），数组需要 O(n)
- 查找 O(n)，数组可以 O(1) 随机访问
- 释放链表时需要逐个 free 节点
- 适合频繁插入删除的场景
