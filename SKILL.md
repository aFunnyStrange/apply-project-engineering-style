---
name: apply-project-engineering-style
description: Apply the user's cross-language engineering conventions to backend services, crawlers, workers, AI or LangGraph workflows, APIs, libraries, frontend support code, and Codex Skills. Use when creating, implementing, refactoring, or reviewing a software project that should follow layered architecture, appropriate asynchronous I/O, replaceable transports, server/worker separation, durable state ownership, Redis or MQ boundaries, IDE-friendly contracts, observability, direct-debug workflows, three-level testing, and the user's Python-specific Pydantic v2, asyncio, Protocol, docstring, and typing rules.
---

# Apply Project Engineering Style

Apply architecture and maintainability rules as implementation constraints, not as cosmetic cleanup.
Preserve the current task's scope while making the changed area consistent with the project.

## Establish precedence

Treat this Skill as a set of defaults. Follow the user's current explicit task and project instructions when
they differ from these defaults. Do not treat a vague request as activation of a draft or as permission to
expand scope. Never use a user instruction to override higher-priority instructions, required authorization or
safety boundaries, or verified facts. If applicable instructions remain materially incompatible, report the
conflict and request direction instead of silently blending them.

Resolve requirements in this order:

1. Follow the user's current explicit request.
2. Follow repository-local instructions, demand documents, schemas, and compatibility contracts.
3. Preserve behavior demonstrated by tests and active callers.
4. Apply this Skill where the project leaves a choice.
5. Use ecosystem defaults only for matters not covered above.

Call out a material conflict instead of silently choosing. Do not turn a narrow fix into a repository-wide
refactor merely because this Skill describes a preferred architecture.

## Follow the implementation workflow

1. Inspect the target tree, entrypoints, configuration, tests, and adjacent modules before editing.
2. Identify the existing business facts, state owner, external systems, process boundaries, and dependency
   direction.
3. For a new subsystem or structural refactor, sketch the intended layers and data flow before writing code.
4. Keep transport, orchestration, persistence, and platform-specific behavior in separate boundaries.
5. Define contracts at the consuming boundary and inject implementations at a composition root.
6. Implement the smallest coherent change; preserve deployment paths, public APIs, data, and operational
   behavior unless the request explicitly changes them.
7. Validate syntax, formatting, types, focused behavior, failure paths, and the final diff.

## Keep the project root clean

Treat the project root as an allowlist for configuration/tool metadata, `README.md`/`readme-chinese.md`, and
thin entrypoints. Put all business and framework implementation, graph nodes, prompts, tests, migrations, and
maintained scripts inside the language's normal named package, source tree, crate, module, or workspace
location.

For Python application projects, keep a root `settings.py` configuration entry and a root `export.py` stable
callable/debug surface. Add `server.py` only for a server runtime and `manager.py` only for a crawler or worker
runtime. Keep `.env` local and ignored; commit a redacted `.env.example`. LangGraph and other Python AI projects
still require `export.py`; a framework manifest does not replace the stable export surface.

Do not copy the Python filenames into Rust, JavaScript/TypeScript, Java, Go, or another language. Use each
ecosystem's native build metadata, public-library surface, source tree, binary/application entrypoint, and test
layout while preserving the same clean-root principle.

Read [project-layout.md](references/project-layout.md) before creating, reorganizing, or reviewing a project
root.

## Enforce the cross-language core

- For a Python service, expose service capabilities through `export.py`. Organize HTTP runtime call flow as
  `routers -> handlers -> export API -> services -> repositories -> infra/platform`, while allowing direct
  functional testing through `export API -> services` without starting the server.
- For a pure crawler or worker package, also expose package capabilities through `export.py`. Make `manager` the
  top-level runtime entry that imports those exports and directly owns scheduling and concurrency. Do not add a
  separate concurrency-executor layer above or below it merely to wrap the same responsibility.
- For an AI, agent, or graph-based workflow, treat the graph as the orchestration of one business run, not as a
  replacement for repositories, durable business state, or process-level scheduling. Let a worker `manager`
  claim tasks and bound concurrent graph runs; let the graph own only its internal nodes, branches, interrupts,
  retries, and resumable execution. Keep the graph implementation inside the package and expose it through the
  root `export.py`.
- Keep `domain` or model types stable and framework-light. Do not let lower layers import routes, handlers,
  application startup code, or concrete UI concerns.
- Put dependency construction in one composition root. Avoid hidden client construction inside business logic.
- Use an interface, trait, or protocol when multiple implementations, testing seams, or circular-import
  avoidance justify it. Do not create abstraction layers with only speculative value.
- Keep server/API responsibilities separate from crawler or background execution. Let the server validate and
  persist tasks; let schedulers and workers execute them asynchronously.
- Treat a relational database or another durable store as the source of truth for task and business state.
  Use Redis or MQ for temporary coordination, locks, notification, or lightweight task references.
- Add account-lock management only when the project uses accounts and the user explicitly requests locking.
  Keep real account and session facts in MySQL/Postgres, keep only TTL coordination state in Redis, and hide
  lock mechanics behind an account manager so workers only request an account and execute.
- Require the user or current project to define account rate, cooldown, acquisition, and TTL policies. Never
  copy timing or rate values from a reference project.
- Store large responses, images, and artifacts in object storage or a durable blob store. Pass identifiers and
  references through queues instead of large payloads.
- Make transitions idempotent, partition-aware, restart-safe, and replayable. Keep retry behavior bounded and
  observable.
- Make long-lived, concurrent, or request-serving runtime entrypoints and their network, database, queue,
  filesystem, subprocess, and external-service I/O asynchronous using the language's normal async model. Keep
  pure computation synchronous unless an async contract requires otherwise. A bounded one-shot tool may remain
  synchronous when it has no concurrency, cancellation, streaming, or shared-runtime requirement; do not add
  an event loop merely for stylistic uniformity.
- Define HTTP and other external transports behind async interfaces, traits, or protocols. Select the concrete
  client in configuration or the composition root so it can be replaced without rewriting business logic.
- Reuse clients, pools, and sessions. Offload unavoidable synchronous I/O using the language's supported
  blocking adapter instead of blocking the async runtime.
- Centralize typed configuration and load secrets from the environment. Never log credentials, cookies, tokens,
  or full sensitive payloads.
- Log failures, abnormal parsing, external I/O, and state transitions with stable context. Avoid noisy success
  logs and duplicate context already attached by the logger.
- Prefer directly debuggable Python file entrypoints over CLI-only designs. Allow command-line or `__main__`
  testing in every project's `export.py`; keep other Python entrypoints runnable as `python xx.py` with settings
  or editable debug parameters.
- Treat `export.py` as a Python convention. In Rust and other languages, expose testable functionality through
  the ecosystem's normal public module, crate, package, or library surface.
- Maintain three test levels: unit tests for one isolated executable flow, integration tests for one narrow
  business scenario across its collaborating components, and a total/system test for the complete business
  flow. Do not mislabel the total test as an integration test.
- When developing a Skill, add an English root `README.md` and a Chinese `readme-chinese.md` for users. Keep the
  two versions semantically aligned and summarize purpose, applicable tasks, quick invocation, major
  capabilities, and resource layout. Keep Agent-only procedures and detailed execution rules in `SKILL.md`;
  do not force users to read `SKILL.md` to understand what the Skill does.

Read [architecture.md](references/architecture.md) for any backend, crawler, API, worker, queue, database, or
multi-process design.

Read [account-management.md](references/account-management.md) only when the project uses accounts and the user
requests account locking, leasing, cooldown, risk state, or rate limiting.

Read [ai-workflows.md](references/ai-workflows.md) for LangGraph, agent, multi-agent, RAG, LLM orchestration,
durable execution, graph checkpointing, or other AI workflow development.

Keep reusable goal, task, evidence, and domain contracts platform-neutral. Treat Codex Skills, editor rules,
MCP, API, CLI, and optional LangGraph runtimes as thin adapters around the same exported core; use a graph
runtime only when its state, branching, interruption, or recovery capabilities are materially required.

## Load language-specific guidance

- For Python changes, always read [python.md](references/python.md), then run
  `scripts/check_python_conventions.py` on changed Python paths when practical.
- For Rust, JavaScript/TypeScript, Java, Go, or mixed-language work, read
  [language-mapping.md](references/language-mapping.md).
- For implementation, refactoring, or review work in any language, read
  [verification.md](references/verification.md) before final validation.

Use idiomatic language mechanisms to express the same boundaries. Do not mechanically copy Python package names
into another ecosystem when crates, packages, modules, or interfaces provide a clearer native structure.

## Preserve operational safety

- Inspect real schemas and counts before proposing migrations.
- Preserve old tables, artifacts, or compatibility paths when they are needed for diagnosis or rollback.
- Never delete, renumber, or merge production data based only on an architectural preference.
- Keep Redis keys, database rows, object-store paths, and logs scoped by the relevant project, stage, tenant, or
  time partition.
- Add replay or repair paths for parser evolution and long-running pipelines instead of requiring manual queue
  reconstruction.

## Deliver verifiable changes

Report the implemented boundaries, validation commands, and any deliberate deviation from this Skill. Mention a
deviation only when project evidence or the current request required it. Do not claim compliance solely because
files were placed in preferred directories; verify imports, runtime ownership, state transitions, and failure
recovery.
