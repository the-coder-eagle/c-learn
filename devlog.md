# C Learn — 开发日志

## 2026-06-09 00:30 — v7 离线化 + GitHub 准备

### 修复
- **行号横向排列** — gutter 添加 `white-space:pre`
- **拖拽条失效** — grip 加宽到 8px，`initLayout` 延迟到 DOM 渲染完成后执行
- **CDN 依赖移除** — 所有外部 JS 依赖清零，CodeMirror 改为纯 textarea + gutter 实现
- **编译导入修复** — Compartment 从 `@codemirror/state` 独立导入

### 项目就绪
- `.gitignore` — 排除 build/dist/__pycache__/progress.json
- `README.md` — 项目说明、快速开始、结构、技术栈
- 源文件: 11 个（全部在根目录）
- 测试: 32 个，100% 通过
- exe: 22MB，零网络依赖

---

## 2026-06-09 — v6 可视化教学引擎

### 新增：C 代码逐行执行 + 内存可视化

**simulator.py** (350行) — 纯 Python C 语言模拟执行器
- 支持语法子集: int, int*, 数组, 函数调用, printf, &, *, 赋值, 算术
- 逐行解析 + 分类（var_decl, assign, deref, printf, func_call 等 12 种语句类型）
- 虚拟内存模型: 地址从 0x100 递增分配，栈帧管理
- 每步生成教学提示（自然语言解释当前行做了什么）
- 支持 step/back/reset/run_all
- 3 个内置示例: 指针基础 / 函数传指针 / 数组与指针

**server.py** — 8 个新 API 端点
- `/api/sim/load` — 加载代码
- `/api/sim/step` — 前进一步
- `/api/sim/back` — 回退一步
- `/api/sim/reset` — 重置
- `/api/sim/run` — 运行到底
- `/api/sim/state` — 获取当前状态
- `/api/sim/example/<name>` — 加载内置示例
- `/api/sim/examples` — 列出示例

**前端可视化面板**
- 顶部模式新增 `🔍 可视化` 标签
- 左侧: 代码编辑器（当前行高亮）
- 右侧: 内存表格（变量名 | 类型 | 值 | 地址 | 指向 | 栈帧）
- 底部: 教学提示区 + printf 输出 + 控制按钮
- 3 个内置示例一键加载

### 项目结构 (10 个源文件)
```
main.py server.py services.py simulator.py test_all.py
C-Learn.spec devlog.md ANALYSIS.md
web/index.html (45KB 单文件前端)
```

### Bug 修复
- **亮暗切换一次生效**：CodeMirror 使用 Compartment 动态切换 oneDark ↔ cmLightTheme
- **第二根拖拽条修复**：重写 makeResizable，使用 window 级事件监听，grip z-index 提升到 20
- **三栏宽度精确计算**：全部使用 `flex:none` + 显式 px，避免 flex 布局干扰拖拽

### 代码清理
- 删除 `desktop/` 残留文件（~2000 行旧 customtkinter 代码）
- 项目仅保留 8 个源文件

### 项目结构
```
main.py server.py services.py test_all.py
C-Learn.spec devlog.md ANALYSIS.md
web/index.html (37KB 单文件前端)
content/ (36课 + 144题)
tools/tcc/ (编译器)
```

---

## 2026-06-08 23:50 — v4 变量检查器 + 全局字体 + 三栏拖拽修复

### 新增
- **全局字体调节**：顶部 `−` `+` 调节所有界面文字大小（10~20px），偏好自动保存
- **代码字体独立调节**：编辑器工具栏单独调节代码字体（10~24px）
- **三栏拖拽修复**：改用 JS 精确计算宽度，两根分隔条均可正常拖拽，宽度持久化
- **变量检查器**：点击 `🔍 变量` 自动解析代码中的变量声明（类型+名称），运行成功后自动展示
- **运行指示器**：编辑器右上角浮层即时反馈运行状态（绿色=成功/红色=失败）

### UI 优化
- 全局使用 em 单位，字体缩放时所有元素等比变化
- 三栏初始宽度智能分配（侧栏 240px / 中间 30% / 右侧自适应）
- 窗口缩放时自动重新计算右侧宽度
- 章节卡片间距收紧，信息密度更合理

---

## 2026-06-08 23:30 — v3 UX 增强

### 新增功能
- **可拖拽栏目**：侧栏/中间/右侧之间可拖拽分隔条调整宽度，宽度自动保存
- **字体调节**：编辑器工具栏 `−` `+` 按钮调节代码字体（10px~24px），偏好自动保存
- **5 种主题色**：顶部彩色圆点切换（默认蓝/紫/青/琥珀/玫瑰）
- **亮色/暗色切换**：☀️/🌙 按钮一键切换
- **运行状态指示器**：编辑器右上角浮层显示运行结果（绿=成功，红=失败），3 秒自动消失
- **用户偏好持久化**：字体大小、主题色、亮暗模式、栏目宽度全部保存到 localStorage

### UI 优化
- Run 按钮增加脉冲动画引导点击
- 主题色切换即时生效（CSS 变量）
- 拖拽手柄 hover 高亮
- 欢迎页新增第 4 步提示主题和字体调节

---

## 2026-06-08: 架构重构 — 从 customtkinter 到 Web 前端

### 重构原因

经过 6 轮 UI 迭代后，customtkinter 框架已无法满足产品需求：
- 无真正的布局引擎（flexbox/grid）
- 无法实现卡片化、动画、现代排版
- 主题切换需逐个 widget 手动更新
- 代码膨胀到 3000+ 行，维护困难

### 新架构

```
main.py            → pywebview 桌面窗口
server.py          → Flask API 服务器
services.py        → 编译/判题/内容/进度（复用）
web/index.html     → 完整 SPA（HTML + CSS + CodeMirror）
content/           → 课程 Markdown + 习题 YAML
tools/tcc/         → TCC 编译器
test_all.py        → 32 个自动化测试
```

**技术栈**: Flask + pywebview + CodeMirror 6 + 原生 JS/CSS
**运行**: `python main.py`
**测试**: `python test_all.py`（32 tests, 100% pass）
**打包**: `pyinstaller main.spec` → 单 exe

### 设计原则

目标用户：高考后学 C 的初学者
- 即学即写：左侧课程 → 中间阅读 → 右侧编码
- 学写结合：每课都有可直接运行的代码
- 温暖友好：暗色主题但不过于冰冷
- 鼓励导向：运行成功显示"太棒了！"，失败显示"别灰心"

### 已清理

- 删除 `desktop/` 下的旧 customtkinter UI 代码（~2000 行）
- 删除旧的 `build/`, `dist/`, `desktop.spec`
- `services.py` 移至项目根目录

### 测试覆盖

| 模块 | 测试数 | 覆盖内容 |
|------|--------|---------|
| compile_and_run | 5 | Hello World, 空代码, 语法错误, 多行输出, 无弹窗 |
| judge | 5 | 通过, 错误, 编译失败, 多测试点, 部分通过 |
| security | 4 | 正常代码, system拦截, 文件I/O允许, fork拦截 |
| content | 4 | 模块加载, 习题加载, 测试点完整性, level范围 |
| progress | 2 | 保存+读取, 覆盖更新 |
| compile_only | 2 | 分离编译运行, 编译错误 |
| server API | 10 | health, modules, exercises, progress, run, submit, detail, index, css |
| **总计** | **32** | **100% 通过** |

### 快捷键

| 快捷键 | 功能 |
|--------|------|
| Ctrl+Enter | 学习模式：运行代码 / 练习模式：提交判题 |

### 打包命令

```bash
pyinstaller --onefile --windowed --name "C-Learn" \
  --add-data "web;web" \
  --add-data "content;content" \
  --add-data "tools/tcc/tcc.exe;tools/tcc" \
  --add-data "tools/tcc/libtcc.dll;tools/tcc" \
  --add-data "tools/tcc/lib;tools/tcc/lib" \
  --add-data "tools/tcc/include;tools/tcc/include" \
  --hidden-import flask \
  --hidden-import webview \
  --hidden-import services \
  --hidden-import yaml \
  main.py
```
