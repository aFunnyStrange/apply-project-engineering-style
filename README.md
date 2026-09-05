# Project Engineering Style

> Status: **active**. Approved on 2026-07-30; continue improving it from verified real-project evidence.

`apply-project-engineering-style` packages recurring architecture, code organization, runtime boundaries, and
testing conventions into a Codex Skill so they do not need to be repeated in every development prompt.

## Use cases

Use this Skill when:

- creating or refactoring backend services, crawlers, workers, and asynchronous task pipelines;
- developing LangGraph, agent, multi-agent, RAG, LLM orchestration, or other AI workflows;
- maintaining Python, Rust, JavaScript/TypeScript, Java, Go, or mixed-language projects;
- evolving reusable frameworks/libraries across interpreter and vendor dependency versions;
- designing boundaries among databases, Redis, message queues, object storage, and task state;
- requiring layered, testable, IDE-friendly, replayable, and diagnosable code;
- creating or maintaining Codex Skills that should follow the same engineering conventions.

## Quick start

```text
Use $apply-project-engineering-style to implement this requirement.
```

The Skill follows the current request and repository conventions first. It applies personal engineering
conventions only where the project is silent and does not expand the refactoring scope merely because the
Skill is enabled.

## Core conventions

- Keep the project root limited to configuration/tool metadata, README files, thin entrypoints, and
  ecosystem-standard source/test/documentation directories. Put implementation and maintained files in their
  owned package, source, or conventional test tree instead of leaving loose root files.
- Distinguish the application directory, import namespaces, and built distribution before reorganizing Python.
  Use a named package by default, but allow explicitly owned flat layer packages when a wrapper adds no value.
- Treat `pyproject.toml` as build configuration, not proof of packaging; build from a clean copy, inspect the
  artifact, and import its public surface.
- Treat the clean-root rule as cross-language, but use native layouts rather than copying Python filenames.
- Use root `export.py`/`manager.py` for concrete Python application runtimes; reusable frameworks and libraries
  expose their stable API from the named package instead.
- For Python applications, keep root `settings.py` and `export.py`; add `server.py` only for a server runtime
  and `manager.py` only for a crawler/worker runtime.
- Keep `.env` local and ignored, and commit a redacted `.env.example`.
- Keep root `settings.py` as the real editable application configuration surface rather than a forwarding shim.
- Keep `export.py` for LangGraph and other Python AI applications; framework manifests do not replace it.
- Layer services as `platform/infra -> repo -> service -> export.py -> handlers -> routers`.
- Use `platform`/`platforms` specifically to stabilize third-party APIs, versions, exceptions, and wire
  semantics; keep resource construction and lifecycle in infrastructure.
- Expose directly testable Python application service, crawler, and worker functionality through `export.py`;
  expose reusable framework/library functionality through its named package API.
- Let the top-level worker or crawler `manager` own scheduling and concurrency directly.
- In AI projects, let the graph orchestrate one task internally; let the worker `manager` claim work and run
  multiple graphs concurrently without reimplementing node scheduling.
- Keep goal, task, evidence, and domain contracts portable; make Codex Skills, editor rules, MCP, API, CLI, and
  optional LangGraph runtimes thin adapters around the same exported core.
- Keep execution context in graph state/checkpoints; keep task, account, session, and business facts in a
  relational database.
- Store business truth in a relational database. Use Redis/MQ primarily for transient coordination and small
  task references.
- When account locking is required, keep real accounts and sessions in MySQL/PostgreSQL and use Redis only for
  TTL locks, cooldowns, risk state, and rate limits. Workers request accounts from an account manager.
- Put large responses, images, and capture artifacts in object storage rather than Redis.
- Use asynchronous I/O for long-lived or concurrent runtimes while keeping transports replaceable; allow a
  bounded one-shot tool to stay synchronous when an event loop adds no lifecycle or concurrency value.
- Isolate vendor-version changes, optional dependencies, native acceleration, fallback parity, background-task
  ownership, streaming closure, and scheduler acknowledgement behind tested framework-owned contracts.
- For Python, use Pydantic v2, `Union`/`Optional`, `Protocol`-based duck typing, and `asyncio`.
- Preserve unit, narrow business integration, and complete business/system test levels.
- For discovery-and-collection flows, cover every discovered item with resource-scoped bounded concurrency,
  retain source observations, deduplicate final records across the run, and add persistence only when required.

## Install for Codex

Link the complete `apply-project-engineering-style/` source directory into the user Skill directory. The link
must resolve to a directory whose top level directly contains `SKILL.md`; do not install by copying the source.

Windows PowerShell:

```powershell
$skillsRoot = Join-Path $HOME ".agents\skills"
$source = (Resolve-Path "<repository-root>\apply-project-engineering-style").Path
$link = Join-Path $skillsRoot "apply-project-engineering-style"
New-Item -ItemType Directory -Force -Path $skillsRoot | Out-Null
if (Test-Path -LiteralPath $link) { throw "Destination already exists: $link" }
New-Item -ItemType Junction -Path $link -Target $source | Out-Null
```

macOS:

```bash
skills_root="$HOME/.agents/skills"
source_dir="$(cd "<repository-root>/apply-project-engineering-style" && pwd)"
link_path="$skills_root/apply-project-engineering-style"
mkdir -p "$skills_root"
if [ -e "$link_path" ] || [ -L "$link_path" ]; then echo "Destination already exists: $link_path" >&2; exit 1; fi
ln -s "$source_dir" "$link_path"
```

Codex normally detects Skill changes automatically; restart it if the Skill does not appear. Invoke it as
`$apply-project-engineering-style`. For cross-agent reuse, CC Switch v3.13 or newer can use
`~/.agents/skills` as shared source storage: open **Skills**, scan/import the local Skill if needed, enable the
target agents, and sync. Review agent-specific tools and permissions after import.

## Files

- `SKILL.md`: core instructions used by Codex.
- `references/project-layout.md`: cross-language clean-root rule and Python service, worker, and AI layouts.
- `references/architecture.md`: layering, task state, server/worker, and storage boundaries.
- `references/collection-workflows.md`: complete discovery, bounded fan-out, resource pools, run-level
  deduplication, and explicit persistence decisions.
- `references/framework-library-contracts.md`: public package APIs, adapters, optional/native backends,
  scheduler lifecycle, persistence, compatibility matrices, and generated-project verification.
- `references/account-management.md`: optional account repositories, Redis TTL coordination, and account-manager
  conventions.
- `references/ai-workflows.md`: layering, state, async, export, and testing conventions for LangGraph and similar
  workflows.
- `references/python.md`: Python-specific conventions.
- `references/language-mapping.md`: mapping the conventions to Rust and other languages.
- `references/verification.md`: post-implementation verification checklist.
- `scripts/check_python_conventions.py`: checks Python docstrings, annotations, and Pydantic v2 conventions.

## Capability evolution and service delivery

The workflow covers optional-capability compatibility, early feature gates, scoped fallback/circuit
behavior, coherent request profiles, retry attempt ownership and stream-versus-business completion rules.
It explicitly supports independently deployed services with root start/stop/clean scripts and a thin smoke client.
These rules preserve baseline behavior and keep small deployments convenient without expanding unrelated work.

See `references/capability-evolution.md` and `references/service-delivery.md` for conditional guidance. The existing Python conventions and checker remain available.
