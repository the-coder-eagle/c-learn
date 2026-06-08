# C Learn — C 语言学习平台

专为初学者设计的 C 语言学习桌面应用。即学即写，学写结合。

## 特性

- **36 课 + 144 题** — 从 Hello World 到指针、结构体、算法
- **即学即写** — 左侧课程，右侧编辑器，Ctrl+Enter 运行
- **代码可视化** — 逐行执行模拟，内存变量表，指针解引用演示
- **TCC 编译** — 毫秒级 C 代码编译，结果即时显示
- **单 exe** — 22MB，双击运行，无需安装任何环境

## 快速开始

### 运行（用户）

双击 `dist/C-Learn.exe`

### 开发

```bash
pip install flask pywebview pyyaml pygments
python main.py
```

### 测试

```bash
python test_all.py   # 32 tests
```

## 项目结构

```
main.py          # 入口：启动 Flask + pywebview 桌面窗口
server.py        # Flask API（课程/习题/编译/判题/模拟器）
services.py      # TCC 编译、判题、内容加载、进度存储
simulator.py     # C 代码逐行模拟执行器（教学可视化）
test_all.py      # 32 个自动化测试
web/index.html   # 完整前端（纯 HTML/CSS/JS，零依赖）
content/         # 36 课 Markdown + 144 题 YAML
tools/tcc/       # TCC 编译器
```

## 技术栈

| 层 | 技术 |
|---|---|
| 桌面壳 | pywebview (Edge WebView2) |
| 后端 | Python Flask |
| 前端 | 原生 HTML/CSS/JS（零框架） |
| 编译器 | TCC (TinyCC) |
| 打包 | PyInstaller |

## 打包

```bash
pyinstaller C-Learn.spec --noconfirm
# 输出: dist/C-Learn.exe
```
