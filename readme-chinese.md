# Project Engineering Style

> 状态：**已激活**。于 2026-07-30 获得批准，后续根据真实工程证据继续完善。

`apply-project-engineering-style` 将个人长期使用的工程架构、代码组织、运行边界和测试方式固化为
Codex Skill，减少每次开发时重复描述相同约束。

## 适用场景

在以下任务中使用：

- 新建或重构后端服务、爬虫、Worker 和异步任务管道。
- 开发 LangGraph、Agent、Multi-Agent、RAG、LLM 编排和其他 AI 工作流。
- 维护 Python、Rust、JavaScript/TypeScript、Java、Go 或混合语言项目。
- 设计数据库、Redis、MQ、对象存储和任务状态之间的边界。
- 希望代码保持分层、可测试、IDE 友好、可回放和易于排查。
- 创建或维护需要相同工程习惯的 Codex Skill。

## 快速使用

在需求中指定：

```text
使用 $apply-project-engineering-style 实现当前需求。
```

Skill 会先遵循当前需求和项目本身的约定，再在项目没有明确规定的地方应用个人工程规范，不会因为
启用 Skill 就自动扩大重构范围。

## 核心约定

- 项目根目录只保留配置/工具元数据、README 和极薄的入口；实现代码、测试、迁移、Prompt、Graph
  节点和维护脚本全部放入对应语言的标准包或源码目录。
- 干净根目录是跨语言原则，但具体文件名遵循各语言生态，不能把 Python 入口机械复制到其他语言。
- Python 应用在根目录保留 `settings.py` 和 `export.py`；只有服务进程才添加 `server.py`，只有
  爬虫/Worker 进程才添加 `manager.py`。
- `.env` 只在本地根目录使用并加入忽略，仓库提交脱敏的 `.env.example`。
- LangGraph 和其他 Python AI 项目同样保留根级 `export.py`，框架清单不能替代稳定导出入口。
- 服务按 `platform/infra -> repo -> service -> export.py -> handlers -> routers` 分层。
- Python 服务、爬虫和 Worker 都通过 `export.py` 暴露可直接测试的功能。
- 纯爬虫或 Worker 由最高层 `manager` 直接负责调度和并发。
- AI 项目中 Graph 负责单次任务内部编排；Worker `manager` 只负责领取任务和并发运行多个 Graph，
  不重复实现节点调度。
- 目标、任务、证据和领域契约保持平台无关；Codex Skill、编辑器规则、MCP、API、CLI 以及可选的
  LangGraph Runtime 都只是同一导出核心的薄适配层。
- Graph State/checkpoint 只保存执行上下文，不能代替关系型数据库中的任务、账号、会话和业务事实。
- 关系型数据库保存业务事实状态；Redis/MQ 主要承担临时协调和轻量任务引用。
- 需要账号锁时，MySQL/Postgres 保存真实账号和会话，Redis 仅保存 TTL 锁、冷却、风控和限速状态；
  Worker 只向账号 Manager 申请账号。
- 大响应、图片和抓包等产物进入对象存储，不通过 Redis 传递完整内容。
- 长期运行或并发 Runtime 的外部 I/O 使用异步模型，并保持具体传输可替换；没有并发、取消或流式
  需求的一次性有界工具可以保持同步，避免为了形式统一引入事件循环。
- Python 使用 Pydantic v2、`Union`/`Optional`、Protocol 鸭子类型和 asyncio。
- 每个项目保留单元测试、细业务集成测试和完整业务总测试三个层次。

## 安装到 Codex

把完整的 `apply-project-engineering-style/` 源码目录链接到用户 Skill 目录。链接目标的顶层必须
直接包含 `SKILL.md`；不要通过复制源码安装。

Windows PowerShell：

```powershell
$skillsRoot = Join-Path $HOME ".agents\skills"
$source = (Resolve-Path "<仓库根目录>\apply-project-engineering-style").Path
$link = Join-Path $skillsRoot "apply-project-engineering-style"
New-Item -ItemType Directory -Force -Path $skillsRoot | Out-Null
if (Test-Path -LiteralPath $link) { throw "目标已存在：$link" }
New-Item -ItemType Junction -Path $link -Target $source | Out-Null
```

macOS：

```bash
skills_root="$HOME/.agents/skills"
source_dir="$(cd "<仓库根目录>/apply-project-engineering-style" && pwd)"
link_path="$skills_root/apply-project-engineering-style"
mkdir -p "$skills_root"
if [ -e "$link_path" ] || [ -L "$link_path" ]; then echo "目标已存在：$link_path" >&2; exit 1; fi
ln -s "$source_dir" "$link_path"
```

Codex 通常会自动识别 Skill 变化；没有显示时重启 Codex。使用
`$apply-project-engineering-style` 显式调用。需要跨 Agent 复用时，可在 CC Switch v3.13 或更高
版本中把 `~/.agents/skills` 设为共享来源，在 **Skills** 页面扫描/导入本地 Skill、启用目标 Agent
并同步。导入后检查目标 Agent 的工具和权限差异。

## 文件说明

- `SKILL.md`：Codex 使用的核心执行规则。
- `references/project-layout.md`：跨语言干净根目录原则，以及 Python 服务、Worker 和 AI 项目布局。
- `references/architecture.md`：分层、任务状态、Server/Worker 和存储边界。
- `references/account-management.md`：按需启用的账号仓库、Redis TTL 协调和账号 Manager 规范。
- `references/ai-workflows.md`：LangGraph 等 AI 工作流的分层、状态、异步、导出和测试规范。
- `references/python.md`：Python 专项规范。
- `references/language-mapping.md`：Rust 等其他语言的通用映射。
- `references/verification.md`：实施完成后的验证清单。
- `scripts/check_python_conventions.py`：Python docstring、类型注解和 Pydantic v2 规则检查。
