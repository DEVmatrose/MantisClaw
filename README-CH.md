# MantisClaw — 自主代理循环框架 (Autonomous Agent Loop Framework)

> **语言:** [English](README.md) | [Deutsch](README-DE.md) | 中文

<p align="center">
  <img src="docs/mantisclaw-overview.png" alt="MantisClaw Overview" width="700">
</p>

**版本:** 0.1.0  
**状态:** 开发中 (IN DEVELOPMENT)  
**GitHub:** [DEVmatrose/MantisClaw](https://github.com/DEVmatrose/MantisClaw)  
**作者:** [@ogerly](https://github.com/ogerly) · [DEVmatrose](https://github.com/DEVmatrose)  
**所属系列:** [Mantis-Familie](https://github.com/DEVmatrose)  
**许可证:** MIT

## 什么是 MantisClaw?

MantisClaw 是一个具有**涌现身份 (Emergent Identity)** 的**独立**代理循环框架。

### 核心理念：涌现之魂 (Emergent Soul)

```
soul(t) = f(base, agenda.resolve(account, social, decentral), working_context)
```

灵魂**从未被刻意编写** — 它在每一个 Tick（时钟周期）被**计算**出来。一个正在编程的代理与一个正在交易的代理是不同的，但它们都共享同一个 `identity/base.md`。

-----

## 架构

```
MantisClaw/
│
├── .agent.json                 ← AAMS 引导程序 (Bootstrap)
├── AGENTS.md                   ← 工具桥接 (Tool-Bridge)
├── READ-AGENT.md               ← 代理合约 (Agent Contract)
│
├── core/                       ← 大脑 (L3) — 纯循环
│   ├── runtime.py              ← 心跳循环 (60秒, 空闲检测)
│   ├── planner.py              ← 思考 (工具注入 + JSONL 提示词日志)
│   ├── executor.py             ← 行动 (模糊动作匹配)
│   ├── observer.py             ← 观察 + 健康追踪
│   ├── reflect.py              ← 反思 (RFL) — 自我修正
│   ├── context.py              ← JIT 上下文加载 (3阶段)
│   ├── skill_executor.py       ← 技能编排 (L5)
│   ├── llm.py                  ← LLM 后端 (L0)
│   ├── session.py              ← AAMS 会话管理
│   ├── workpaper.py            ← 工作底稿管理
│   ├── ltm.py                  ← 长期记忆
│   └── registry/               ← 工具注册表 (L4)
│       ├── __init__.py         ← ToolRegistry + 工具类
│       ├── registry.py         ← 白名单, 安全级别, 模糊解析
│       └── tools/              ← 工具实现
│           ├── filesystem.py   ← 文件操作 (读、写、列出目录、空间状态)
│           ├── memory.py       ← 记忆查询, 日志记录
│           └── analysis.py     ← 分析, 总结 (LLM 驱动)
│
├── identity/                   ← 涌现身份 (L1)
│   ├── base.md.example         ← 常量：名称、伦理、密钥
│   ├── agenda.md.example       ← 根节点：活动议程
│   ├── account.md.example      ← 平台访问权限
│   ├── social.md.example       ← CRM 状态：联系人
│   ├── decentral.md.example    ← 信任图谱：节点
│   └── hook.md.example         ← 触发器定义
│
├── WORKSPACE/                  ← AAMS 身体 (L2)
│   └── WORKING/                ← 构建记忆
│       ├── WHITEPAPER/         ← 架构真相 (Architecture Truth)
│       ├── WORKPAPER/          ← 会话工作
│       ├── MEMORY/             ← 长期记忆 (ltm-index.md)
│       ├── DIARY/              ← 决策上下文
│       ├── GUIDELINES/         ← 程序化记忆 (Procedural Memory)
│       ├── SCIENCE/            ← 知识验证
│       ├── LOGS/               ← 审计追踪 (prompt_log.jsonl)
│       ├── PROJECT/            ← 项目定义 (project.yaml)
│       └── TOOLS/              ← 技能 (编排配方)
│           └── skills/         ← Markdown+YAML 工作流
│
└── config/                     ← 配置
```

-----

## AAMS — 身体

[AAMS](https://github.com/DEVmatrose/AAMS) (自主代理清单规范) 是一个**独立于框架的**代理工作标准。AAMS 不是 MantisClaw 的一部分 — 它是一个外部的通用标准。

MantisClaw 使用 AAMS 作为**结构化身体** (`WORKSPACE/WORKING/`)。整个 WORKING 结构使得处理复杂任务（如编程、规划或组织）变得井然有序。

**AAMS 结构提供的内容：**

  - **Workpapers** — 会话工作，每次会话一个文件
  - **Whitepapers** — 稳定的架构真相
  - **LTM** — 长期记忆 (ltm-index.md + 可选的 ChromaDB)
  - **Diary** — 决策上下文 (按月分类的文件)
  - **Guidelines** — 程序化记忆 (可学习的工作方式)
  - **SCIENCE** — 知识验证 (外部研究，假设)
  - **Skills** — `TOOLS/skills/` 中的编排配方
  - **Logs** — 审计追踪 (prompt\_log.jsonl, 运行时指标)
  - **Project** — 包含里程碑和状态的项目定义

AAMS 标准: [github.com/DEVmatrose/AAMS](https://github.com/DEVmatrose/AAMS)

-----

## 循环 (The Loop)

```python
async def tick():
    # L1 — 计算涌现身份
    soul_t = compute_soul(base, agenda, accounts, social, decentral)
    
    # L4 — 加载上下文 (JIT 3阶段)
    registry.execute("load_context_always", {})          # ~3k Tokens
    registry.execute("load_context_agenda", {agenda})    # ~8k Tokens
    
    # L3 — 思考
    hooks = load("identity/hook.md")
    guidelines = registry.execute("read_guidelines", {task_type})
    plan = planner(soul_t, hooks, memory, guidelines)
    
    # L3 — 行动 (工具或技能)
    if plan.type == "skill":
        results = skill_executor.execute(plan.skill, context)
    else:
        results = registry.execute(plan.tool, plan.params)
    
    # L3 — 观察
    assessment = observer(results, diary, guidelines)
    
    # L3 — 反思 (RFL)
    if assessment.needs_revision:
        reflection = reflect(assessment, results, plan)
        plan = planner.revise(soul_t, reflection)
        results = executor(plan)  # 第二次尝试
    
    # L2 — 程序化记忆 + LTM
    observer.extract_lessons(results)  # → GUIDELINES/
    ltm_update(results, assessment)
```

### 分层模型

```
L0  LLM 后端                → core/llm.py
L1  身份 (Identity)         → identity/ (soul(t) 计算)
L2  AAMS Body (身体)        → WORKING/ (被动，仅通过工具访问)
L3  运行时 / 循环            → core/ (planner, executor, observer, reflect)
L4  工具注册表              → core/registry/ (白名单，包括身体访问)
L5  技能 + 语音 (Skills+Voice)  → TOOLS/skills/ + voice.py (语音优先助手)
L6  安全 (Security)             → 横向功能 (每个工具的安全级别)
```

> 在 **Mantis-OS** 中，还会增加 L7 (网络/MantisNostr)。

> **核心规则：** L3 (循环) 永远不直接接触 L2 (身体)。任何对 WORKING/ 的访问都必须通过 L4 中注册的工具进行。

-----

## 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/DEVmatrose/MantisClaw
cd MantisClaw

# 2. Python 虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\Activate.ps1  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置
cp config/.env.example .env
# 编辑 .env:
#   - LLM_BACKEND=lmstudio (默认) 或 ollama
#   - 可选：云端密钥 (OPENAI_API_KEY, ANTHROPIC_API_KEY)

# 5. 设置身份
cp identity/base.md.example identity/base.md
cp identity/agenda.md.example identity/agenda.md
# 可选：account.md, social.md, decentral.md, hook.md
```

### 启动 LLM 后端

MantisClaw 遵循 **本地优先 (local-first)** — 在启动代理之前必须运行本地 LLM：

```bash
# 选项 A: LM Studio (默认，推荐)
# → 打开 LM Studio, 加载模型, 在 localhost:1234 启动服务器

# 选项 B: Ollama
ollama serve                    # localhost:11434
ollama run qwen3-coder          # 或其他模型
```

### 启动代理循环 (无头模式)

```bash
python -m core.runtime
```

运行时循环将在终端中运行并记录每个 Tick：

```
12:00:00 [mantisclaw.runtime] INFO: MantisClaw starting...
12:00:00 [mantisclaw.runtime] INFO: Health: HEALTHY
12:00:00 [mantisclaw.runtime] INFO: Heartbeat: 60s
12:01:00 [mantisclaw.runtime] INFO: === TICK 1 ===
12:01:00 [mantisclaw.runtime] DEBUG: Soul computed. Agent: MantisClaw
12:01:00 [mantisclaw.runtime] INFO: Plan: ... (2 steps)
```

使用 `Ctrl+C` 停止。系统会自动在 `WORKSPACE/WORKING/WORKPAPER/` 中创建工作底稿。

### 启动控制面板 (Web-UI)

```bash
uvicorn dashboard.app:app --reload --port 8080
```

打开 **http://localhost:8080** — 控制面板显示：

```
┌──────────────┬──────────────────────────────────┬───────────────┐
│  助手         │                                  │ R1 项目       │
│  MantisClaw  │        与代理聊天                 │ R2 工作底稿    │
│  语音聊天     │        (SSE 流式传输)             │ R3 WORKING    │
│  事件流       │                                  │ R4 聊天历史    │
├──────────────┴──────────────────────────────────┴───────────────┤
│ 🟢 [后端 ▼] [模型 ▼] │ 身份 │ 运行时 │ 工具 │ 语音            │
└─────────────────────────────────────────────────────────────────┘
```

  - **左侧 (助手):** Mantis 语音助手 — 语音聊天记录 (VAD + TTS/STT + 动作分类器), 事件流 (运行时 Tick, 错误, 警告)
  - **中间:** 带有 SSE 流式传输（逐个 Token）的聊天界面
  - **右侧 (项目上下文):** R1 项目概览 (里程碑, 状态, 标签), R2 活跃工作底稿 (预览), R3 WORKING 树 (可导航的 AAMS 结构), R4 聊天历史
  - **底栏控件:** 后端/模型切换器, 身份检查器, 运行时模态框, 工具模态框, 提示词检查器, 语音切换
  - **顶栏:** 项目选择器下拉菜单 (切换活跃项目上下文)

-----

## 独立性 (Standalone)

| 维度 | MantisClaw |
|--------|------------|
| AAMS | ✅ 使用 AAMS 作为身体 (外部标准) |
| 运行时 | ✅ 自有的心跳循环 |
| 身份 | ✅ 所有文件存储在本地 `identity/` |
| LLM 后端 | ✅ LM Studio (默认) / Ollama / 可选云端 |
| 控制面板 | ✅ 运行在 localhost:8080 的 Web-UI (FastAPI + SSE + 实时 Tick 提要) |
| 空闲检测 | ✅ 相同计划在重复 3 次后将被跳过 |
| 提示词日志 | ✅ 基于 JSONL，可通过控制面板查看 |
| 部署 | ✅ 单个仓库，可独立运行 |

**代码与 Mantis-OS 中的 MantisClaw 完全一致** — 仅集成方式有所不同。

-----

## 运行时效率

自主循环在每个 Tick 都会消耗 LLM Token。如果没有对策，可能会产生“跑步机”效应 — 相同的计划被无限重复，每一步都产生错误，且 `analyze` 工具对不存在的路径生成冗长的解释。

### 应对措施 (已实现)

| 问题 | 解决方案 |
|---------|--------|
| **10秒心跳过于激进** | 将心跳提高到 60秒 (`config/default.yaml`) |
| **循环中出现相同计划** | 空闲检测：对计划签名进行哈希处理，连续 3 个相同计划后跳过执行 |
| **Tick 之间缺乏记忆** | 将最后 3 个 Tick 的总结注入 Planner 上下文，并注明“请勿重复！” |
| **LLM 虚构文件路径** | `_validate_path()` 剥离幻觉前缀 (`WORKSPACE/`, `./WORKSPACE/WORKING/`)，工具描述提供正确的示例路径 |
| **LLM 混用 WORKSPACE/ 和 WORKING/** | `workspace_status` 输出带 `WORKING/` 前缀的路径，Planner 规则：“严禁使用 WORKSPACE/ 作为前缀” |
| **LLM 忽略回答格式** | 明确的格式指令 + `禁止 (VERBOTEN):` 模块 (禁用 XML 标签) + `_parse_plan()` 优雅捕获 `<原因>` 标签 |
| **LLM 回复过长 (2000+ Tokens)** | Planner 最多 500 Tokens, Analyze 最多 300 Tokens, Summarize 最多 200 Tokens |
| **Analyze 无休止解释错误** | Token 限制 + 修正路径 → 减少错误 → 减少解释 |

### 监控

  - **提示词日志:** 每次 Planner 调用都以 JSONL 格式保存在 `WORKSPACE/WORKING/LOGS/prompt_log.jsonl`
  - **提示词检查器:** 控制面板弹窗显示最后的 LLM 提示词 (System/User/Response)
  - **实时 Tick 提要:** 控制面板显示最后 8 个 Tick，包括成功率、目标和异常
  - **空闲指示器:** 当代理处于闲置状态时，控制面板显示 “💤 IDLE: X 个相同计划”

-----

## 集成到 Mantis-OS

MantisClaw 可以独立运行 — 也可以作为 **Mantis-OS** (自主代理操作系统) 的一部分运行：

```
Mantis-OS (完整的代理节点)
  ├── MantisClaw (大脑 + 身份 + AAMS 身体)   ← 即本仓库
  └── MantisNostr (网格网络)
```

链接: [https://github.com/DEVmatrose/Mantis-OS](https://github.com/DEVmatrose/Mantis-OS)

-----

## 文档

### 白皮书 (Whitepapers)

| 白皮书 | 内容 |
|---|---|
| [WH-CORE](https://www.google.com/search?q=WORKSPACE/WORKING/WHITEPAPER/CORE.md) | 运行时与循环 — 大脑 |
| [WH-IDENTITY](https://www.google.com/search?q=WORKSPACE/WORKING/WHITEPAPER/IDENTITY.md) | 涌现身份 — soul(t) |
| [WH-WORKING](https://www.google.com/search?q=WORKSPACE/WORKING/WHITEPAPER/WORKING.md) | AAMS Body — 身体 |
| [WH-TOOLS](https://www.google.com/search?q=WORKSPACE/WORKING/WHITEPAPER/TOOLS.md) | 工具注册表, 技能与身体接口 |

查看 `WORKSPACE/WORKING/WORKPAPER/` 获取当前的会话工作内容。

-----

## 许可证

MIT