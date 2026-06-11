# C Learn Desktop — 全局分析报告

> 分析时间: 2026-06-11 | 源文件: 8 个 | 测试: 61 个 | 习题: 144 道

---

## 一、当前架构

```
入口 main.py → PyWebView 桌面壳
                  │
                  └── server.py (Flask API，后台线程)
                       ├── services.py (TCC编译、判题、课程加载、进度存储)
                       └── simulator.py (C 代码逐行模拟执行)

Web 前端 → web/index.html (单页)
            ├── web/style.css (纯 CSS，零外部依赖)
            └── web/app.js (纯 vanilla JS，零外部依赖)

数据层 → content/ (36 个课程模块 .md + 144 道习题 .yml)
         progress.json (本地 JSON 进度文件)
```

## 二、文件清单

| 文件 | 行数 | 职责 |
|------|------|------|
| `main.py` | 49 | 桌面壳入口，启动 Flask + WebView |
| `server.py` | 298 | Flask API 路由 (20 个端点) |
| `services.py` | 909 | 编译、判题、安全扫描、内容加载、进度、交互式运行 |
| `simulator.py` | 1582 | C 代码模拟执行引擎 (指针/数组/循环/switch) |
| `test_all.py` | 713 | 61 个自动化测试 |
| `web/app.js` | 1153 | 前端全部逻辑 (编辑器/语法高亮/补全/模式切换) |
| `web/index.html` | 185 | HTML 结构 (单页应用) |
| `web/style.css` | 370 | 样式 (暗色/亮色主题 + 语法高亮配色) |

## 三、v4 (2026-06-11) 质量评估

### 架构: B+/A-
- Flask + Web 前端 + PyWebView 分层清晰，前后端完全分离
- API 设计符合 RESTful 风格
- 零外部 JS/CSS 依赖，纯本地运行
- `ANALYSIS.md` 保持与代码同步

### 安全: A-
- 双层安全扫描 (严格/宽松)，正则词边界保护
- 子进程使用 `CREATE_NO_WINDOW` 抑制控制台弹窗
- 编译超时、运行时超时、输出大小限制
- `.env` 配置文件支持 (python-dotenv)

### 代码质量: B+
- 良好的中文注释和文档
- 数据类使用得当，异常处理全面
- `simulator.py` `_parse()` 方法较长 (~180行) 可拆分
- `web/app.js` 单文件 1153 行可模块化

### 测试: A
- 61 个测试全部通过
- 覆盖: 编译(5) + 判题(5) + 安全(9) + 内容(4) + 进度(2) + API(11) + 模拟器(17) + 配置(1) + 可视化(4)
- 缺口: 缺少前端 JS 测试、InteractiveRunner 测试

### 性能: B+
- TCC 编译 <100ms
- 判题编译一次 + 多用例运行，早停策略
- 模拟器 5000 步限制 + 历史快照优化
- 前端 debounced highlight (50ms)

## 四、v4 修复记录

### 已修复 Bug (10 个)
| 来源 | 严重度 | 描述 |
|------|--------|------|
| 本次 | P0 | `step_back()` 不恢复变量值 |
| 本次 | P0 | `_eval_func_call` else 分支在 if 为真时泄漏 |
| 本次 | P1 | `_eval_expr` 不支持一元负号 |
| 本次 | P1 | 编译器错误行号越界导致 JS 崩溃 |
| 本次 | P1 | 5 道习题 ID 重复，无法通过 API 访问 |
| 本次 | P2 | `server.py` 类型标注错误 |
| 本次 | P2 | `r._example` 死代码 |
| 本次 | P2 | 模式按钮重复点击触发完整 UI 重建 |
| 本次 | P3 | 冗余 import |
| 本次 | P3 | Toast 堆叠 |

### 已实施优化 (6 项)
| 类别 | 描述 |
|------|------|
| 内存 | 历史快照跳过 lines/variables 序列化 (5000步省 ~13MB) |
| I/O | 管道读取 1字节→256字节块 (系统调用减 256×) |
| 前端 | `formatCode` 处理 else/else-if 行 |
| 前端 | aria-label 无障碍标注 |
| 文档 | `ANALYSIS.md` 更新反映 Web 架构 |
| 数据 | 习题 ID 去重 |

## 五、关键指标

| 指标 | 数值 |
|------|------|
| 源文件 | 8 个 |
| 代码行数 | Python ~2800 + JS ~1150 + CSS ~370 |
| 课程模块 | 36 个 (16 级) |
| 练习题 | 144 道 (简单 63 / 中等 66 / 困难 15) |
| API 端点 | 20 个 |
| 测试数 | 61 个 (100% pass, ~2.5s) |
