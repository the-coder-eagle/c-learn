# C Learn — 开发日志

## 2026-06-11 — v4.0 全局 Debug + 优化 + UI 修复 + 内容极大扩展 + 打包

### 课程内容极大扩展 (v4.0 核心)
- **36 个课程模块全部重写**，从原来的 90KB 扩展到 **1.4MB（~15×）**
- 每个模块 10-29KB，面向**零基础初学者**
- 每个文件结构统一：
  - 🌟 生活化比喻引入（储物柜、厨房家电、快递地址等）
  - 📖 概念详解（是什么、为什么、何时用）
  - 📊 ASCII 图解（内存布局、编译流程、缓冲区、递归树）
  - 💻 4-6 个逐行注释的代码示例（简单→复杂）
  - ⚠️ 3-5 个常见错误（错误 vs 正确代码对比表格）
  - 💡 分层练习建议（初级/中级/进阶）
  - 📝 要点速查清单 + 小测验
  - 🔗 相关主题链接
- 9 个后台 Agent 并行写作，覆盖全部 16 个级别

### 后端 Bug 修复 (6 个) ...

### 本次总修复: 11 bugs + 7 优化 + 打包

### 后端 Bug 修复 (6 个)
- **P0**: `simulator.py` `step_back()` 不恢复变量值 — 新增 `_restore_stack()` + `_stack_data` 序列化
- **P0**: `simulator.py` `_eval_func_call` else 分支在 if 为真时仍执行 — 新增 `_eval_skip_else` 标志
- **P1**: `simulator.py` `_eval_expr` 不支持一元负号 (`-a`) — 添加 unary minus 处理
- **P2**: `server.py` 类型标注 `_simulator: CSimulator = None` → `Optional[CSimulator]`
- **P3**: `simulator.py` `_handle_func_call` 内冗余 import — 删除
- **P1**: 5 道习题 ID 重复 (basic-02/03, loop-01, ptr-01/02) — 改为唯一 ID

### 前端 Bug 修复 (5 个)
- **P1**: `app.js` 编译器错误行号越界 → `lines[ln-1]` undefined 崩溃 — 添加边界检查
- **P2**: `app.js` `r._example` 死代码 — 改用 `_vizSource` 变量追踪
- **P2**: `app.js` 重复点击已激活模式按钮触发完整 UI 重建 — 添加早返
- **P3**: `app.js` Toast 堆叠 — 新 toast 前移除旧 toast
- **P3**: `index.html` 图标按钮缺少 `aria-label` — 添加无障碍标注

### 优化 (7 项)
- 内存: 历史快照排除 `lines/variables` (5000步省 ~13MB)
- I/O: `InteractiveRunner._reader` 1字节→256字节块读 (系统调用减 256×)
- 前端: `formatCode()` 处理 else/else-if 行
- 前端: `debouncedHighlight` 合并自动保存逻辑
- 文档: `ANALYSIS.md` 更新为当前 Web 架构
- 打包: spec 添加 dotenv hidden import
- 数据: 习题 ID 去重

### 打包
- `pyinstaller C-Learn.spec --clean --noconfirm` → `dist/C-Learn.exe` (22MB)
- TCC 编译器 + Flask + PyWebView + 全部内容一次性打包

### 测试
- **61 tests, 100% pass, 2.6s** (无回归)

### 评估
- 架构: B+/A- | 安全: A- | 代码质量: B+ | 测试: A | 性能: B+
- 144 习题 + 36 课程模块 | 20 个 API 端点 | 9 个可视化示例

### 核心文件变更
- `simulator.py`: +45 行 (step_back 恢复/_stack_data/_restore_stack/else skip/unary minus)
- `server.py`: +2 行 (Optional 类型)
- `services.py`: ~5 行 (块读取优化)
- `web/app.js`: +20 行 (边界检查/_vizSource/早返/toast/formatCode)
- `web/index.html`: +3 行 (aria-label)
- `ANALYSIS.md`: 完全重写 (反映 Web 架构)
- `C-Learn.spec`: +1 行 (dotenv hidden import)
- 5 个 YAML 习题文件: ID 去重
- `devlog.md`: 更新

---

## 2026-06-09 — v3.3.0 模拟引擎补全 + 8 项功能优化

### 模拟引擎 v3 (do-while + break/continue + switch/case)
- **do-while**: 先执行循环体，`} while (cond);` 检查条件后跳回
- **break**: 跳出最内层循环或 switch 块
- **continue**: 跳过当前迭代剩余部分，跳回条件检查
- **switch/case**: 表达式求值 + case 匹配 + fall-through 穿透 + break 退出
- **default**: 无匹配 case 时进入默认分支
- 新增 3 个示例: 例7-do-while、例8-break/continue、例9-switch/case

### 代码美化 (Ctrl+S)
- `formatCode()`: 自动缩进对齐、大括号智能缩进、case 标签处理

### 代码自动补全 (输入 2+ 字符触发)
- 12 种 C 语言模板: printf, scanf, for, while, if, if-else, switch, do-while, main, include, struct, malloc
- Tab 选择补全项，方向键导航，Esc 关闭

### 快捷键面板 (Ctrl+K)
- 8 个常用快捷键速查表，覆盖所有操作

### 成就系统
- 9 种成就: 初次运行、首战告捷、小试牛刀(10题)、渐入佳境(50题)、百题斩(100题)、挑战者(5困难)、连续三天、一周坚持、基础毕业
- 解锁时 toast 通知 + 欢迎页徽章展示

### 每日一题
- 基于日期哈希的每日推荐题目，欢迎页顶部卡片展示

### 进度导出/导入
- 导出: 下载 progress JSON 文件
- 导入: 上传 JSON 恢复进度

### 测试
- **61 tests, 100% pass** (新增 5 个: TestSimulator +5)
- test_static_js_file 覆盖新函数断言

### 核心文件变更
- `simulator.py`: +200 行 (do-while/break/continue/switch + 3 示例)
- `web/app.js`: +200 行 (格式化/补全/快捷面板/成就/每日一题/导出导入)
- `web/style.css`: +60 行 (新组件样式)
- `web/index.html`: +25 行 (新按钮 + 面板 + 下拉)
- `test_all.py`: +50 行 (switch/break/continue/do-while 测试)
- `README.md`, `devlog.md`: 更新

---

## 2026-06-09 — v3.2.0 全面评估修正

### 模拟引擎升级 (if/else + while + for)
- **控制流支持**: `simulator.py` 新增 if/else 条件分支、while 循环、for 循环
- **大括号配对**: 解析时建立 `_brace_map`，支持 `{` 与同行语法元素
- **条件求值**: `_eval_condition()` 支持 `>`, `<`, `>=`, `<=`, `==`, `!=`
- **循环追踪**: `_loop_stack` 管理嵌套循环，正确跳回条件检查
- 新增 3 个示例: 例4-if/else、例5-while、例6-for

### 安全扫描增强
- 正则词边界保护: `systematic` 不再误触发 `system(` 拦截
- 新增拦截: `syscall()`, `__builtin_*`, `winsock2`
- 严格模式支持: `CLEARN_STRICT_FREE_PLAY=1` 环境变量

### 配置系统
- **`.env.example`**: 8 项可配置设置（端口、超时、输出限制、路径）
- `CONFIG` 字典统一管理所有配置，可选 `python-dotenv` 支持
- 错误提示新增英文 fallback（`CLEARN_LANG` / `LANG` 检测）

### Bug 修复
- **临时文件泄漏**: `compile_only()` 重构为 try/finally 模式，失败路径自动清理
- **指针算术 bug**: `_handle_assign` 中 `return` 缩进错误导致普通变量赋值被跳过
- **for 循环死循环**: `_loop_stack` 弹出时机修正，条件为假时才弹出
- **静态 HTML 测试**: 适配 `?v=11` 版本参数

### 前端优化
- 语法高亮添加 50ms 防抖，大文件粘贴不卡顿
- 可视化面板新增 3 个控制流示例按钮

### 测试
- **56 tests, 100% pass** (新增 16 个: TestSimulator +7, TestSecurityRegex +5, TestConfig +1, TestVizExamplesAPI +3)

### 核心文件变更
- `simulator.py`: +350 行 (控制流引擎)
- `services.py`: +80 行 (配置 + 安全 + 英文错误提示 + 修复)
- `test_all.py`: +120 行 (新测试组)
- `web/app.js`: +20 行 (防抖 + 新示例)
- `web/index.html`: +3 行 (新示例按钮)
- `.env.example`: 新建

---

## 2026-06-09 — v3.1.0 历史/判题修复 + 菜单方向修正

### Bug 修复
- **历史按钮**: 菜单从 `bottom:100%`（向上弹出）改为 `top:100%`（向下弹出），修复被 `overflow:hidden` 裁切的问题
- **判题标签**: 输出面板"运行结果"/"判题"标签页添加点击切换逻辑，点击可在终端输出和判题结果间切换
- **判题结果**: 提交后自动切换到"判题"标签（原来错误高亮"运行结果"）

---

## 2026-06-09 — v3.0.0 交互式终端 + 统一 I/O

### 交互式运行引擎
- **InteractiveRunner 类**: `subprocess.Popen` + 二进制管道替代批量 `subprocess.run`
- **零缓冲 printf**: 编译时注入 `__wrap.c`，`-Dprintf=__flush_printf` 预处理器宏替换 + `WriteFile`/`FlushFileBuffers` 直写管道
- **逐字节读取**: `pipe.read(1)` 替代 `read(256)` 解决 Windows 管道阻塞问题
- 新增 API: `/api/interactive/start` `/poll` `/input` `/kill`

### 统一终端 (CLion 风格)
- 输出区改为 `<textarea>` — 输出和输入在同一区域
- 光标锁定：仅允许在程序输出末尾输入，保护已有输出
- Enter 发送输入，80ms 轮询实时显示输出
- 运行时按钮变为 "⏹ 停止"（红色），可随时终止

### Bug 修复
- 标题重复：`openModule()` 去掉 markdown 正文 `# 标题`
- 文字复制：CSS `user-select: text` 显式开启
- 停止按钮：去掉 `setBtnLoading`（不再 disabled）
- 学习进度：`_writable_dir()` 存储到 exe 目录，不再丢失
- 课程树进度：模块阅览自动标记，章节显示 N/M
- 练习题计数：过滤模块 slug，只统计练习 ID
- 缓存：`@app.after_request` + no-cache 头 + `?v=11`

### 核心文件变更
- `services.py`: +120 行 (InteractiveRunner + _writable_dir)
- `server.py`: +60 行 (interactive API + module progress)
- `web/app.js`: +100 行 (交互式运行 + 统一终端 + 进度)
- `web/style.css`: 终端 textarea 样式
- `web/index.html`: textarea 终端替换 div


## 2026-06-09 13:00 — v11 前端重构 + 语法高亮 + 新手引导

### 前端架构统一
- **彻底消除内联代码**: index.html 现为纯 HTML 结构 (130 行)，CSS/JS 完全独立
- **style.css** (340 行): 完整样式 + 语法高亮 Token 配色 (暗色/亮色双主题)
- **app.js** (530 行): 全部逻辑，零外部依赖
- 删除旧 v9/v10 重复代码，统一为单一来源

### 新功能

**1. C 语言语法高亮**
- 实时 tokenize: 关键字(int/for/return…)紫色、类型(int/char…)黄色、字符串绿色、注释灰色、数字橙色、预处理指令蓝色
- 透明 textarea + 底层 `<pre>` 叠加方案，支持暗色/亮色主题
- 每次输入自动重绘，100 行以内无延迟
- 新增 CSS 变量: `--hl-keyword` `--hl-type` `--hl-string` `--hl-comment` `--hl-number` `--hl-preproc` `--hl-func` `--hl-op`

**2. 新手引导 (Onboarding)**
- 首次启动 600ms 后自动弹出 4 步引导卡片
- Step 0: 欢迎 + 统计概览 (课时数/练习题数/完成率)
- Step 1: 左侧课程与练习说明
- Step 2: 右侧编辑器快捷键提示 (Ctrl+Enter/Tab/Ctrl+B)
- Step 3: 可视化模式介绍
- 完成后写入 `localStorage c-onboarded`，不再弹出
- 顶部新增 ❓ 帮助按钮，可随时重新打开引导

**3. 学习进度仪表盘**
- 欢迎页新增模块进度条 (16 个模块各有完成百分比)
- 新增"困难题已过"统计卡片
- 模块完成率绿色/蓝色双色进度条

### 其他改进
- 可视化模式新增"📝 自写代码"按钮，从编辑器加载代码到可视化
- 输出面板新增清空按钮
- 编辑器布局改为 pre+textarea 叠加结构 (`.editor-inner`)
- stdin 输入栏增加图标

### 测试更新
- `test_static_css` → `test_static_html`: 验证外部 CSS/JS 引用
- 测试新增对 `hl-kw`/`tokenizeLine`/`showOnboarding` 的断言
- **40 tests, 100% pass**

### README 更新
- 架构图反映实际 Web 前端 + Flask 后端方案
- 项目结构更新为新文件布局

---

## 2026-06-09 11:00 — v9 架构优化 + 新功能

### 架构重构：前端三文件分离
```
web/index.html  → 942 行单文件 (旧)
web/index.html  → 130 行纯 HTML 结构 (新)
web/style.css   → 300 行独立样式表 (新)
web/app.js      → 430 行独立逻辑 (新)
```
- HTML: 仅含页面结构 + `<link>` / `<script>` 引用
- CSS: 全部样式独立，新增 search/history/system-theme 规则
- JS: 全部逻辑独立，新增 3 项功能
- Flask static_folder 已配置，`/style.css` `/app.js` 直接可用

### 新功能 (P1/P2)

**1. 练习搜索过滤**
- 侧栏练习列表顶部新增搜索框
- 支持按标题和标签过滤
- 搜索词保留，切换难度筛选不丢失

**2. 代码历史记录**
- 编辑器工具栏新增 🕐 历史按钮
- 运行/提交时自动保存代码快照 (最多 10 条)
- 点击历史项一键恢复代码
- 数据存储于 localStorage `c-code-hist`

**3. 系统主题自动跟随**
- 首次启动时检测 `prefers-color-scheme`
- 用户手动切换后以用户选择为准，不再自动跟随
- CSS 新增 `@media (prefers-color-scheme: light)` 规则
- `auto-theme` 类预留用于未来"跟随系统"选项

### 其他修复
- 欢迎页 emoji 修复: `?` → `🎓`
- 完全正确提示添加 🎉 庆祝图标
- 提示文本添加 💡 图标
- 无匹配题目时显示"无匹配题目"提示

### 测试
- 新增 `TestSimulator` (6 tests): 初始状态、变量创建、指针解引用、重置、回退、示例加载
- 新增 `test_static_css_file` / `test_static_js_file`: 验证独立文件可访问
- **总计 40 tests, 100% pass**

### 基础设施
- 新增 `requirements.txt`: flask, pywebview, pyinstaller, pyyaml, pygments

---

## 2026-06-09 10:30 — v8 人因工程 UI 全面升级

### 用户反馈
- 按钮/按键太小，难以点击
- 两条侧栏分隔条不能自由拖动（抓取区太窄 8px）
- UI 设计不符合人因工程标准

### P0 — 按钮尺寸统一升级
- **工具栏按钮** `btn-run`/`btn-sub`: padding 4→6px/12→18px, min-height 28→32px
- **字体调节按钮** `sz-btn`: 20×20 → 26×26px
- **顶栏模式切换**: font-size 11→12px, padding 4→5px/10→14px, min-height 28px
- **输出区 tab**: font-size 9→10px, padding 2→3px/8→10px
- **练习筛选按钮**: font-size 9→10px, padding 3→5px, min-height 26px
- **侧栏课程/习题项**: padding 6→8px, min-height 32px
- **顶栏高度**: 40→44px，容纳更大的按钮

### P0 — 拖拽系统重设计
- **Grip 点击区**: 视觉 12px + `::before` 伪元素扩展到 20px 点击区
- **三栏最小宽度保护**: 侧栏 120px, 内容 200px, 右侧 320px
- **窗口缩放比例保持**: resize 事件按比例重新分配三栏宽度
- **新增竖直拖拽条** `grip-v`: 编辑器区和输出区之间可上下拖拽调整高度
- **输出区高度持久化**: 保存到 localStorage `c-out-h`

### P1 — 侧栏折叠
- 顶栏新增 ☰ 按钮，点击折叠/展开侧栏
- 折叠时侧栏宽度→0，左 grip 隐藏
- 右侧两栏自动扩展填满空间
- 快捷键: `Ctrl+B`
- 折叠状态持久化到 localStorage `c-sidebar-collapsed`

### P1 — 字号体系
```
--fs-xs:10px → 辅助文字、标签、进度
--fs-sm:11px → 侧栏项目、工具栏按钮
--fs-md:13px → 正文级交互元素
--fs-lg:15px → 小标题
--fs-xl:18px → 大标题
```
所有 UI 文字统一使用 `var(--fs-*)` 变量，不再硬编码 px

### P1 — 顶栏重新布局
- Logo + 模式切换 → 分隔线 → 界面字体 → 分隔线 → 代码字体 → 分隔线 → 进度 → 主题色 → 亮暗
- 使用 `.sep` 分隔线和 `.ctrl-group` 分组美化
- 代码字体在顶栏和编辑器工具栏同步调节
- 所有主题色圆点添加 `title` tooltip 提示

### P2 — 细节打磨
- **focus-visible**: 所有按钮/输入框添加 2px accent 色 outline
- **transition**: 所有交互元素统一 `0.18s ease` 过渡
- **Loading 状态**: 运行/提交按钮 API 调用期间禁用 + 半透明
- **Toast**: 持续时间 2.5→3s, 底部间距 20→24px
- **Tooltip**: 所有功能性按钮添加 `title` 属性
- **欢迎页**: 统计卡片 hover 高亮, 步骤字号提升
- **滚动条**: 5px 宽, hover 时颜色加深
- **可视化按钮**: 添加图标和 title

### 测试
- 22/23 测试类通过 (TestServerAPI 需 Flask — 网络不可用)
- 核心测试: compile(5), judge(5), content(4), security(4), progress(2), compile_only(2) 全部 PASS

### 打包
- `C-Learn.spec` 无需修改 (web 目录已在 datas 中)
- 构建命令: `pyinstaller C-Learn.spec`

---

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
