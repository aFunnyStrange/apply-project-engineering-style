---
name: apply-project-engineering-style
description: Apply the user's engineering conventions when implementing, refactoring, or reviewing applications, services, crawlers, workers, AI workflows, reusable libraries, and Skills. Covers multi-platform aggregation, project boundaries, direct debugging, configuration ownership, async runtime and state ownership, optional capability compatibility, and verifiable delivery across languages.
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

## Accept new rules and correct flawed defaults

During every coding task using this Skill, accept explicit user additions, corrections and refinements as
part of the current task contract, including rules introduced after implementation has begun. Apply a clear
instruction within its authorized scope without requiring the user to edit this Skill first or reconfirm an
already resolved preference. Preserve unrelated requirements and the precedence above.

Do not preserve a bug or an unsuitable design merely because it follows a Skill example. When project
facts, a reproducer or test results show that a default is wrong for the task, explain the evidence briefly,
make the smallest justified correction within the authorized scope, and verify the affected behavior.
Correct obsolete tests when the intended contract changes; do not weaken checks merely to hide a failure.
Ask only when an unresolved choice materially affects scope or compatibility, not simply because a Skill
default differs from a clear user instruction.

Distinguish a task-specific override from a reusable Skill improvement. Record the former in the appropriate
project documentation when useful; do not automatically make it a universal rule or modify the installed Skill
during ordinary project work. When the user asks to improve the Skill, generalize only the supported lesson,
update conflicting guidance and validate the result. Report any material departure and its reason concisely.

## Prefer direct, readable implementation

First distinguish a client package from a highly encapsulated concurrent server. Server applications may
benefit from `handlers -> services -> repositories -> infra`; API clients and protocol subpackages
should organize around complete request objects in `api/`, signing and parsing. Concurrency alone does not
make a client a server or require that stack.

Use the fewest boundaries that express real protocol, business-state and resource ownership. A layer is a
responsibility, not a required directory, class or function call. Do not add a forwarding method, factory,
handler, adapter, service or repository merely to complete an architecture diagram. Prefer a direct call or
re-export when arguments, results, policy and lifecycle are unchanged. Keep wrappers that perform actual
compatibility mapping, validation, state transitions or resource management.

For small API packages and embedded platform workflows, read
[lightweight-platform-packages.md](references/lightweight-platform-packages.md). This reference takes precedence
over the full-layer examples below for that scope. This style means visible request assembly and short call
chains. Preserve package-relative imports, explicit inputs and existing resource ownership.

For request/API, parser or protocol algorithm work, also read
[client-components.md](references/client-components.md). Keep full URL, method, headers, query and body
inspectable in the endpoint. Parameter encapsulation means independently callable computed business fields,
not scattering ordinary request dictionaries into distant modules. Export request builders, algorithms and
pure parsers explicitly; keep vendor-neutral primitives and transport in `platforms`. If a host framework provides Request,
construct that native type directly in `api/`; keep spider files focused on business orchestration. Use only fictional
examples in this Skill; never encode a reference project's identity, paths or proprietary protocol defaults.

## Default to minimally invasive integration

In an existing project, preserve the host's architecture and public entrypoints. A highly encapsulated server
may retain `handlers -> services -> repositories -> infra`. A lightweight client used by that server should
normally remain an owned package exposing its APIs and, when useful, a runtime for shared connections and
lifecycle. Change only the required integration seams. A request to add or improve one client does not
implicitly authorize reorganizing the host. Undertake a large architectural refactor only when explicitly
requested; otherwise fix concrete local issues without expanding the assignment.

## Reuse host infrastructure; keep standalone configuration usable

For embedded clients, prefer accepting the host's actual connection, pool or client object. Do not create a
second infrastructure stack or wrap every borrowed object in a provider solely for dependency injection.
The host owns construction and shutdown of borrowed resources. A package runtime may create and close its
own resources for standalone execution, but explicit injected objects take precedence and must not trigger
construction or closure of an unused fallback. Respect connection thread-safety and event-loop ownership.

Keep package `settings.py` complete and discoverable for package-owned configuration. Shared settings may
explicitly alias or map the host's configuration: this is useful configuration reuse, not a prohibited
forwarding-only business wrapper. Keep platform defaults local and document override precedence. If standalone
execution without the host is required, apply host mapping at the integration entry or an explicitly selected
profile; do not make ordinary package imports require the host or silently fall back after a configuration
error. Reuse an injected resource as-is rather than reconstructing it from forwarded settings.

## Follow the implementation workflow

1. Inspect the target tree, entrypoints, configuration, tests, and adjacent modules before editing.
2. Identify the existing business facts, state owner, external systems, process boundaries, and dependency
   direction.
3. For a new subsystem or structural refactor, establish a baseline of current behavior, entrypoints,
   configuration ownership, state, outputs, import paths, and deployment paths. Then sketch the intended
   layers, data flow, filesystem layout, import model, and distribution boundary before writing code.
4. Identify transport, orchestration, persistence and platform responsibilities; separate code only where
   ownership, change patterns or testing justify it. Adjacent responsibilities may share a module.
5. Pass dependencies explicitly at the consuming boundary. Add a protocol or factory only for a real
   substitution or lifecycle need; concrete types and ordinary functions are often sufficient.
6. Implement the smallest coherent change; preserve deployment paths, public APIs, data, and operational
   behavior unless the request explicitly changes them.
7. For a reusable framework or library, identify its declared interpreter, dependency-version, optional-extra,
   generated-project, and runtime-mode compatibility matrix before changing a public contract.
8. Validate syntax, formatting, types, focused behavior, failure paths, built/installed artifacts when relevant,
   the requested structural outcome, and the final diff. Passing tests does not prove that a reorganization met
   its maintainability or layout goal.

## Preserve baseline workflows and lightweight delivery

Keep the existing baseline usable when adding a capability explicitly designated optional. Check enablement
before validating enhancement-only fields or doing external I/O; model unavailable, skipped, business-denied,
and incompatible outcomes separately. Use a known supported fallback only within that capability's contract.
Keep version/request differences in platform adapters and business paths in cohesive workflows; do not grow
one workflow per flag combination or turn a working small service into a framework.

Read [capability-evolution.md](references/capability-evolution.md) when adding optional remote services,
feature flags, versioned request profiles, account rotation, streaming completion, or retry/settlement behavior.

For independently deployed small services, preserve root `start.sh`, `stop.sh`, `clean.sh`, an optional foreground
run script, and a thin `test.py`/`demo.py` when they are the intended operational surface. Scripts belong to the
service they manage, not an unrelated parent. Keep reusable implementation and substantial test suites in owned
source/test directories. A Python smoke client for a Java service does not require Python application scaffolding.
Read [service-delivery.md](references/service-delivery.md) for this delivery shape.

## Keep the project root clean

Treat the project root as an allowlist for configuration/tool metadata, `README.md`/`readme-chinese.md`, thin
entrypoints, and ecosystem-standard source/test/documentation directories. Put business and framework
implementation, graph nodes, prompts, migrations, maintained scripts, and tests inside deliberately selected
owned packages, source trees, conventional test trees, crates, modules, or workspace locations; do not leave
them as arbitrary loose root files.

For Python application projects, keep configuration and stable callable APIs easy to find, normally through
`settings.py` and `export.py`. An existing host may call embedded package exports directly; do not add a root
aggregate or debug entry merely to forward those calls. Add `server.py` only for a server runtime and `manager.py` only for a crawler or worker
runtime. When environment-based configuration is used, keep `.env` ignored and commit a redacted
`.env.example`; do not introduce it into code-configured packages. LangGraph and other Python AI projects
still need a usable callable surface; a framework manifest alone does not provide one.

Treat the named implementation package as a default, not a mandatory wrapper. First distinguish the application
directory, Python import namespaces, and built distribution. When the user or repository defines the application
directory itself as the deployment unit, explicitly owned layer packages may live directly beneath it. Do not
add an otherwise redundant wrapper package for visual conformity. Conversely, `pyproject.toml` alone does not
make a project distributable: when distribution is required, configure discovery, build from a clean copy,
inspect the artifact, and import it. A source-imported package with an encapsulated public API does not require
a new distribution manifest.

For a reusable Python library or framework, use its package-level public surface, such as `package/__init__.py`
or a deliberate `api.py`. Do not add application-only root `settings.py`, `export.py`, `server.py`, or
`manager.py` files unless the repository also ships that concrete runtime.

Do not copy the Python filenames into Rust, JavaScript/TypeScript, Java, Go, or another language. Use each
ecosystem's native build metadata, public-library surface, source tree, binary/application entrypoint, and test
layout while preserving the same clean-root principle.

Read [project-layout.md](references/project-layout.md) before creating, reorganizing, or reviewing a project
root.

## Enforce the cross-language core

- For a Python service, expose a callable business entry. A router may call a platform package export
  directly. Add handlers, services, repositories and adapters only when they own substantive behavior. The
  full layered chain is an option for complex services, not a mandatory call path. Preserve acyclic imports.
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
- Give `platform` or `platforms` one precise role: convert unstable third-party APIs, versions, exceptions,
  wire formats, and operating-system behavior into stable project-owned semantics. Do not use it as a synonym
  for infrastructure or as a miscellaneous directory. In a flat Python layout, avoid a root package name that
  shadows the standard library.
- Put dependency construction in one composition root. Avoid hidden client construction inside business logic.
- Keep changing vendor clients behind framework-owned platform contracts. Normalize version differences and
  transport exceptions in the adapter, preserve original causes, and do not retry programming errors.
- Keep optional drivers and native extensions out of default import paths. Preserve IDE completion with checked
  typed lazy exports or stubs, and test that runtime and typed public surfaces stay synchronized.
- Keep concrete infra clients one-shot. Put bounded retry, cancellation policy, and replaceable resource
  generations above infra; collapse concurrent replacement of the same failed generation and never replay an
  arbitrary non-idempotent transaction automatically.
- Use an interface, trait, or protocol when multiple implementations, testing seams, or circular-import
  avoidance justify it. Do not create abstraction layers with only speculative value.
- For bounded discovery-and-collection flows, process every discovered item unless the contract explicitly
  defines sampling. Fan out independent I/O behind a limit scoped to the constrained resource, isolate ordinary
  item failures, propagate cancellation, and deduplicate final records across the complete run while retaining
  source observations needed for diagnosis.
- Keep server/API responsibilities separate from crawler or background execution. Let the server validate and
  persist tasks; let schedulers and workers execute them asynchronously.
- Treat a relational database or another durable store as the source of truth for task and business state.
  Use Redis or MQ for temporary coordination, locks, notification, or lightweight task references.
- Add account-lock management only when the project uses accounts and the user explicitly requests locking.
  Prefer durable account storage and TTL coordination as separate concerns, but preserve an explicitly
  established authoritative store; do not introduce a database migration to enforce this default. Document
  persistence, retention and loss semantics, and hide lock mechanics behind an account manager.
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
- Use the project's async transport in concurrent code. Pass the concrete client directly when its type is
  stable; introduce a transport interface only when replacement or a meaningful testing seam requires it.
- Reuse clients, pools, and sessions. Offload unavoidable synchronous I/O using the language's supported
  blocking adapter instead of blocking the async runtime.
- Give every background task a retained owner and shutdown path. Do not treat an empty queue as quiescence while
  callbacks, listeners, streams, or other active producers can still enqueue work.
- Make root `settings.py` the discoverable configuration surface for a Python application. Explicit aliases
  or mappings to host-owned shared settings are valid; avoid redundant copies and unrelated indirection.
  Reusable validation may live in an owned module, while concrete application defaults
  and profiles remain discoverable at the root. In multi-platform hosts, root settings own shared service
  configuration; platform-owned settings remain in their own discoverable modules. Respect the chosen code-only or environment-based configuration
  contract. In environment-based applications, keep secrets in ignored local configuration and preserve
  documented precedence. Never log credentials, cookies, tokens, or full sensitive payloads.
- Log failures, abnormal parsing, external I/O, and state transitions with stable context. Avoid noisy success
  logs and duplicate context already attached by the logger.
- Prefer directly debuggable Python files with editable parameters or external sample paths. A pure
  `export.py` may remain re-exports only. Do not add CLI parsing, DebugSettings or a debug runtime without
  a concrete need; follow an explicit no-CLI requirement.
- Treat `export.py` as a Python convention. In Rust and other languages, expose testable functionality through
  the ecosystem's normal public module, crate, package, or library surface.
- Maintain three test levels: unit tests for one isolated executable flow, integration tests for one narrow
  business scenario across its collaborating components, and a total/system test for the complete business
  flow. Do not mislabel the total test as an integration test.
- Do not invent persistence or local artifacts merely because a workflow produced data. Distinguish discovery
  metadata, normalized observations, deduplicated results, and durable artifacts. Add storage only when the
  business, replay, audit, or diagnostic contract requires it, and verify generated output is excluded from
  distributions when it is not part of the product.
- When developing a Skill, add an English root `README.md` and a Chinese `readme-chinese.md` for users. Keep the
  two versions semantically aligned and summarize purpose, applicable tasks, quick invocation, major
  capabilities, and resource layout. Keep Agent-only procedures and detailed execution rules in `SKILL.md`;
  do not force users to read `SKILL.md` to understand what the Skill does.

Read [architecture.md](references/architecture.md) for any backend, crawler, API, worker, queue, database, or
multi-process design.

Read [multi-platform-aggregation.md](references/multi-platform-aggregation.md) when one service hosts multiple
platform integrations, shared response/retry capabilities, platform runtimes, compatibility adapters or
service-wide rule refresh. In this scope, its ownership and export alternatives refine the single-service
examples below; do not require handlers to import a root export that already exports those handlers.

Read [embedded-workflows.md](references/embedded-workflows.md) when integrating a reusable package into an
existing service, migrating traffic between implementations, replenishing a session/resource pool, handing
submitted work to a polling worker, or documenting nested package architecture.

Read [collection-workflows.md](references/collection-workflows.md) when a workflow discovers multiple items,
fans out external I/O, aggregates overlapping results, rotates constrained resources, or needs an explicit
decision about persistence.

Read [framework-library-contracts.md](references/framework-library-contracts.md) when developing or reviewing a
reusable framework/library, public extension surface, generated project template, vendor-version adapter,
optional/native backend, scheduler lifecycle, streaming API, or compatibility matrix.

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
