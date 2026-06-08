---
title: "结构体基础 — 创建自己的数据类型"
slug: "structs-intro"
level: 7
order: 1
tags: ["struct", "结构体", "typedef", "自定义类型"]
---

# 结构体基础 — 创建自己的数据类型

结构体让你把**多个相关的数据打包在一起**，创建自己的复合类型。

## 为什么需要结构体？

```c
// 没有结构体：数据分散
char name1[50]; int age1; float score1;
char name2[50]; int age2; float score2;
// 要传 3 个参数，容易搞混

// 有结构体：数据组织在一起
struct Student { char name[50]; int age; float score; };
struct Student s1, s2;
// 一个变量包含所有信息
```

## 定义与使用

```c
#include <stdio.h>
#include <string.h>

// 定义结构体类型
struct Student {
    char name[50];
    int age;
    float score;
};

int main() {
    // 声明变量
    struct Student s1;

    // 赋值（用 . 访问成员）
    strcpy(s1.name, "Alice");
    s1.age = 20;
    s1.score = 92.5;

    // 打印
    printf("Name: %s\n", s1.name);
    printf("Age: %d\n", s1.age);
    printf("Score: %.1f\n", s1.score);
    return 0;
}
```

## 初始化方式

```c
// 方式1：按顺序初始化
struct Student s1 = {"Bob", 22, 88.0};

// 方式2：指定成员初始化（C99）
struct Student s2 = {.name = "Carol", .score = 95.0, .age = 19};

// 方式3：先声明再逐个赋值
struct Student s3;
strcpy(s3.name, "Dave");
s3.age = 21;
s3.score = 76.5;
```

## typedef — 简化类型名

```c
// 不用 typedef：每次都要写 struct
struct Point { int x; int y; };
struct Point p1, p2;

// 用 typedef：简化
typedef struct {
    int x;
    int y;
} Point;

Point p1, p2;  // 简洁！
p1.x = 10; p1.y = 20;
```

## 结构体数组

```c
typedef struct {
    char name[50];
    int age;
    float score;
} Student;

Student class[3] = {
    {"Alice", 20, 92.5},
    {"Bob", 22, 88.0},
    {"Carol", 19, 95.0},
};

// 遍历
for (int i = 0; i < 3; i++) {
    printf("%s: %.1f\n", class[i].name, class[i].score);
}
```

## 结构体与函数

```c
// 传值（复制整个结构体）
void print_student(Student s) {
    printf("%s (%d) : %.1f\n", s.name, s.age, s.score);
}

// 传指针（高效，可修改）
void birthday(Student *s) {
    s->age += 1;  // -> 等价于 (*s).age
}

int main() {
    Student s = {"Alice", 20, 92.5};
    print_student(s);    // Alice (20) : 92.5
    birthday(&s);
    print_student(s);    // Alice (21) : 92.5
    return 0;
}
```

### `->` vs `.`

| 语法 | 使用场景 | 含义 |
|------|---------|------|
| `s.age` | s 是结构体变量 | 访问成员 |
| `p->age` | p 是结构体指针 | 等价于 `(*p).age` |

## 嵌套结构体

```c
typedef struct {
    int day, month, year;
} Date;

typedef struct {
    char name[50];
    Date birthday;    // 结构体嵌套
    float score;
} Student;

Student s = {"Alice", {15, 6, 2005}, 92.5};
printf("Born: %d/%d/%d\n", s.birthday.day, s.birthday.month, s.birthday.year);
```

## 练习：学生管理系统雏形

```c
#include <stdio.h>
#include <string.h>

#define MAX 100

typedef struct {
    char name[50];
    int age;
    float score;
} Student;

void print_all(Student arr[], int n) {
    printf("\n--- Student List ---\n");
    for (int i = 0; i < n; i++)
        printf("%d. %s, %d, %.1f\n",
               i+1, arr[i].name, arr[i].age, arr[i].score);
}

float average_score(Student arr[], int n) {
    float sum = 0;
    for (int i = 0; i < n; i++) sum += arr[i].score;
    return sum / n;
}

int main() {
    Student students[MAX];
    int n = 0;

    // 添加学生
    students[n++] = (Student){"Alice", 20, 92.5};
    students[n++] = (Student){"Bob", 22, 88.0};
    students[n++] = (Student){"Carol", 19, 95.0};

    print_all(students, n);
    printf("Average: %.1f\n", average_score(students, n));
    return 0;
}
```

## 要点速查

- `struct` 定义复合数据类型
- `.` 访问成员，`->` 通过指针访问成员
- `typedef` 简化类型名
- 结构体可以嵌套、可以组成数组
- 传指针比传值更高效
