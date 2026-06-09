<p align="center">
  <img src="https://img.shields.io/badge/version-v11-blue?style=flat-square" alt="version">
  <img src="https://img.shields.io/badge/tests-40%20passed-brightgreen?style=flat-square" alt="tests">
  <img src="https://img.shields.io/badge/license-MIT-yellow?style=flat-square" alt="license">
  <img src="https://img.shields.io/badge/platform-Windows%2010%2B-lightgrey?style=flat-square" alt="platform">
</p>

<h1 align="center">🎓 C Learn</h1>
<h3 align="center">C 语言初学者 · 即学即写平台</h3>
<p align="center"><em>没有安装，没有配置，没有门槛。双击运行，开始写 C。</em></p>

---

## ✨ 为什么选择 C Learn？

学习 C 语言的经典困境：**环境配置劝退** — 装编译器、配 IDE、搞懂命令行，还没写一行代码就放弃了。

C Learn 把这一切简化为一个 **22MB 的单文件**。下载 → 双击 → 开始写代码。


## 🎯 核心特性

<table>
<tr>
<td width="50%">

### ⚡ 毫秒级编译反馈
内置 **TCC (TinyCC)** 编译器，编译速度比 GCC 快 10-50 倍。写完代码按 `Ctrl+Enter`，结果瞬间呈现——就像解释型语言一样流畅。

</td>
<td width="50%">

### 🎨 实时语法高亮
8 种 Token 类型独立配色：关键字紫色、类型黄色、字符串绿色、注释灰色……暗色/亮色双主题 + 5 种强调色可选，保护眼睛。

</td>
</tr>
<tr>
<td width="50%">

### 📖 36 课系统化课程
从 `printf("Hello World")` 到链表、指针、文件 I/O——16 级难度递进，每课都有可修改运行的代码示例。

</td>
<td width="50%">

### 💻 144 道在线判题
22 个分类覆盖所有 C 语言知识点。每道题都有测试用例，提交即时判题——AC / WA / CE 结果一目了然。

</td>
</tr>
<tr>
<td width="50%">

### 🔍 代码可视化模拟器
逐行执行代码，观察内存变量表的实时变化。指针解引用、数组遍历、函数调用栈——抽象概念变得可见。

</td>
<td width="50%">

### 🚀 零配置，单文件
22MB exe，双击即用。不需要安装编译器、不需要配置环境变量、不需要任何编程基础。

</td>
</tr>
</table>


## 📸 界面预览

```
┌──────────────────────────────────────────────────────────┐
│  ☰  C 语言学习 即学即写  |  📖学习  💻练习  🔍可视化  │  ← 顶栏
│                         | 已学 5 课 ▓▓░░░░   ●●●●●  ☀️  │
├────────┬───────────────┴─────────────────────────────────┤
│ 课程   │  📝 C 语言简介                                 │
│        │                                                │
│ ▼ 一、 │  C 语言是一门通用的、面向过程的……              │
│   基础  │                                                │
│   2/5  │  ```c                                           │
│ ○ 简介 │  #include <stdio.h>                             │
│ ✓ 变量 │  int main() {                                   │
│ ○ 运算 │      printf("你好，世界！\n");                  │
│ ○ 输入 │      return 0;                                  │
│ ○ 错误 │  }                                              │
│        │  ```                                            │
│ ▼ 二、 │  ← 上一课          下一课：变量与类型 →        │
│   控制  │                                                │
│   0/3  │                                                │
│        │                                                │
├────────┴─────────────────────────────────────────────────┤
│  main.c                         代码字体 − 14px +       │
│                                      🕐历史 🔍变量      │
│  1 │ #include <stdio.h>  ← 行号 + 语法高亮              │
│  2 │                                                    │
│  3 │ int main() {                                       │
│  4 │     printf("hi");                                  │
│  5 │     return 0;                                      │
│  6 │ }                                                  │
│──────────────────────────────────────────────────────────│
│  📥 输入 [                    ]                           │
│──────────────────────────────────────────────────────────│
│  输出                       运行结果 | 判题               │
│  ┌──────────────────────────────────────────────────┐   │
│  │ 运行成功 — 3ms                                    │   │
│  │ hi                                                │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
```


## 🚀 快速开始

### 用户（直接使用）

1. 下载 `dist/C-Learn.exe`（22MB）
2. 双击运行
3. 开始写 C 代码！

> **系统要求**: Windows 10/11，Edge WebView2 运行时（Windows 10+ 自带）

### 开发者（参与贡献）

```bash
# 1. 克隆仓库
git clone https://github.com/zysh6666/c-learning-platform.git
cd c-learning-platform

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动开发服务器
python main.py

# 4. 运行测试
python test_all.py   # 40 tests
```

### 打包为 exe

```bash
pyinstaller C-Learn.spec --noconfirm
# 输出: dist/C-Learn.exe
```


## 🏗️ 架构设计

```
┌─────────────────────────────────────────┐
│          pywebview 桌面窗口              │
│         (Edge WebView2 运行时)           │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │    Flask HTTP Server               │ │
│  │    (127.0.0.1:8765)                │ │
│  │                                     │ │
│  │  /api/run        编译运行 C 代码    │ │
│  │  /api/submit     提交判题          │ │
│  │  /api/modules    课程内容          │ │
│  │  /api/exercises  习题列表          │ │
│  │  /api/progress   学习进度          │ │
│  │  /api/sim/*      代码可视化        │ │
│  └──────────┬──────────────────────────┘ │
│             │                             │
│  ┌──────────▼──────────────────────────┐ │
│  │   纯前端 (HTML/CSS/JS · 零框架)     │ │
│  │   • 三栏可拖拽布局                   │ │
│  │   • 实时语法高亮                     │ │
│  │   • Markdown 渲染 (含表格)           │ │
│  │   • 新手分步引导                     │ │
│  │   • localStorage 进度持久化          │ │
│  └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
          │
          ▼
┌────────────────────┐
│   services.py       │
│   • TCC 编译运行    │
│   • 判题引擎        │
│   • 内容加载        │
│   • 进度持久化      │
│   simulator.py      │
│   • 逐行模拟执行    │
│   • 内存变量追踪    │
│   • 指针解引用演示  │
└────────────────────┘
```


## 📁 项目结构

```
c-learning-platform/
├── main.py               # 入口：启动 Flask + pywebview 桌面窗口
├── server.py             # Flask API（12 个端点）
├── services.py           # TCC 编译、判题、课程加载、进度存储
├── simulator.py          # C 代码逐行模拟执行器（纯 Python）
├── test_all.py           # 40 个自动化测试 (unittest)
├── requirements.txt      # Python 依赖
├── C-Learn.spec          # PyInstaller 打包配置
│
├── web/                  # 🌐 前端 (零框架，纯原生)
│   ├── index.html        #   页面结构 (130 行)
│   ├── style.css         #   样式表：暗色/亮色 + 语法高亮配色 (340 行)
│   └── app.js            #   全部逻辑：编辑器/API/可视化/引导 (530 行)
│
├── content/              # 📚 教学内容
│   ├── 01-basics/        #   基础入门 (5 课)
│   ├── 02-control-flow/  #   控制流程 (3 课)
│   ├── 03-functions/     #   函数 (4 课)
│   ├── 03-memory/        #   内存理解 (2 课)
│   ├── ... 16 个模块共 36 课
│   └── exercises/        #   144 道练习题 (22 分类 YAML)
│
├── tools/tcc/            # 🔧 TCC 编译器
│   ├── tcc.exe
│   ├── libtcc.dll
│   ├── include/          #   C 标准头文件
│   └── lib/              #   静态库
│
├── dist/                 # 📦 打包输出
│   └── C-Learn.exe       #   22MB 独立可执行文件
│
├── README.md             # 📖 项目文档
└── devlog.md             # 📝 开发日志
```


## 🧪 测试

```bash
python test_all.py
```

**40 个测试，7 个测试组，100% 通过率：**

| 测试组 | 数量 | 覆盖内容 |
|--------|------|---------|
| `TestCompileAndRun` | 5 | Hello World、空代码、语法错误、多行输出 |
| `TestCompileOnly` | 2 | 分离编译 + 独立运行 |
| `TestJudge` | 5 | AC/WA/CE、多测试点、部分通过 |
| `TestSecurity` | 4 | system/fork 拦截、自由练习放行 |
| `TestContentLoading` | 4 | 课程加载、习题加载、数据完整性 |
| `TestProgress` | 2 | 进度保存/加载/覆盖 |
| `TestServerAPI` | 12 | HTTP 端点全覆盖 + 静态文件 |
| `TestSimulator` | 6 | 初始化、变量创建、指针解引用、回退 |


## 🎨 主题配色

5 种强调色，一键切换。暗色/亮色模式自动跟随系统，也可手动切换。

| 主题 | 强调色 | 预览 |
|------|--------|------|
| 🟦 默认蓝 | `#6C8CFF` | 沉稳、专业 |
| 🟪 紫 | `#A78BFA` | 柔和、创意 |
| 🟦 青 | `#22D3EE` | 清新、现代 |
| 🟨 琥珀 | `#FBBF24` | 温暖、醒目 |
| 🌹 玫瑰 | `#FB7185` | 活泼、热情 |

暗色主题基于 [Catppuccin](https://github.com/catppuccin/catppuccin) 配色理念，亮色主题采用低对比度柔光设计。


## ⌨️ 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl + Enter` | 运行代码 / 提交判题 |
| `Ctrl + B` | 切换侧栏显示 |
| `Tab` | 插入 4 空格缩进 |
| `Ctrl + +/-` | 界面/代码字号调节 |


## 🔒 安全说明

C Learn 是 **本地桌面应用**，代码在用户本机直接执行。前端包含基础的代码安全扫描（拦截 `system()`、`CreateProcess` 等危险调用），但不构成完整沙箱。

- ✅ 适合个人学习和本地使用
- ⚠️ 不适合直接作为公开在线判题系统部署
- 💡 如需 SaaS 化部署，建议配合 Docker 沙箱或 seccomp 限制


## 📊 内容体系

### 课程（36 课 · 16 级）

| 级别 | 模块 | 课时 |
|------|------|------|
| 1 | 一、基础入门 | Hello World, 变量, 运算符, 输入输出, 常见错误 |
| 2 | 二、控制流程 | if-else, 循环, 综合练习 |
| 3 | 三、函数 | 函数入门, 作用域与生命周期, 练习, 迷你计算器 |
| 4 | 四、内存理解 | malloc/free, 栈 vs 堆 |
| 5 | 五、数组 | 数组入门, 二维数组 |
| 6 | 六、数据结构 | 链表, 栈与队列 |
| 7 | 七、指针 | 基本解引用 |
| 8 | 八、进阶 | 函数指针, 高级指针 |
| 9 | 九、字符串 | 字符串入门, 字符串 I/O |
| 10 | 十、专家 | 位运算 |
| 11 | 十一、结构体 | 结构体入门, 结构体与指针 |
| 12 | 十二、文件 I/O | 文件读写, 二进制与错误处理 |
| 13 | 十三、动态内存 | 内存模型, 常见陷阱 |
| 14 | 十四、算法 | 排序, 查找 |
| 15 | 十五、系统 | 命令行参数, 文件系统 |
| 16 | 十六、项目 | 迷你 Shell, 文本处理器 |

### 练习题（144 题 · 22 分类）

```
basics · loops · functions · arrays · strings · pointers
structs · memory · linkedlist · stack-queue · trees
algorithms · sort-search · recursion · dynamic-programming
math · bit-manipulation · file-io · enums-unions
preprocessor · expert · data-structures
```


## 🛠️ 技术栈

| 层 | 技术 | 说明 |
|----|------|------|
| 桌面壳 | **pywebview** | 调用系统 Edge WebView2，比 Electron 轻 10 倍 |
| 后端 | **Flask** | 轻量 Python Web 框架，12 个 API 端点 |
| 前端 | **原生三件套** | HTML/CSS/JS，零 npm 依赖，零打包构建 |
| 编译器 | **TCC** | TinyCC，编译比 GCC 快 10-50 倍 |
| 打包 | **PyInstaller** | Python → 单文件 exe |


## 🗺️ 路线图

- [x] v1-v8: 核心平台（编译、判题、课程、进度）
- [x] v9: 前端模块化 + 搜索 + 代码历史 + 系统主题
- [x] v10: UI 人因工程升级（按钮尺寸、抓取区、可访问性）
- [x] v11: 语法高亮 + 新手引导 + 进度仪表盘
- [ ] v12: 代码自动补全
- [ ] v13: 学习路径推荐（"每日一题"）
- [ ] v14: 移动端适配（PWA）
- [ ] v15: Docker 沙箱 + SaaS 部署


## 🤝 贡献

欢迎提 Issue 和 PR！这是一个个人教育项目，旨在降低 C 语言学习门槛。

## 📄 许可

MIT License

---

<p align="center">
  <sub>Made with ❤️ by <a href="https://github.com/zysh6666">zysh6666</a></sub>
</p>
