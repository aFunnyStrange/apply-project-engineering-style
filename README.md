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

## Lightweight API and platform packages

Distinguish clients from highly encapsulated concurrent servers: the latter can retain a full layered stack.
For clients, prefer complete request objects in `api/` and short call chains. Layers describe responsibilities, not a
mandatory handler/service/repository stack. Keep protocol input/output separate from platform business state;
remove forwarding-only wrappers, inject existing host capabilities, and let the worker own polling cadence.
See [the lightweight package guide](references/lightweight-platform-packages.md) for the current pattern.

In existing projects, integrate with minimal intrusion: retain the host server structure, expose client APIs
and any necessary runtime from an owned package, and change only required seams. Large architectural
reorganization requires an explicit request.

Embedded clients normally borrow the host's connection/pool/client objects directly. A standalone runtime
creates only its own defaults and closes only owned resources. Package settings retain complete local
configuration and may explicitly map shared host configuration; this is legitimate reuse, not redundant
business forwarding. Injected resources take precedence over constructing new ones.

## Core conventions

- Keep the project root limited to configuration/tool metadata, README files, thin entrypoints, and
  ecosystem-standard source/test/documentation directories. Put implementation and maintained files in their
  owned package, source, or conventional test tree instead of leaving loose root files.
- Distinguish the application directory, import namespaces, and built distribution before reorganizing Python.
  Use a named package by default, but allow explicitly owned flat layer packages when a wrapper adds no value.
- When distribution is required, treat `pyproject.toml` as build configuration, not proof of packaging; build from a clean copy, inspect the
  artifact, and import its public surface.
- Treat the clean-root rule as cross-language, but use native layouts rather than copying Python filenames.
- Use root `export.py`/`manager.py` for concrete Python application runtimes; reusable frameworks and libraries
  expose their stable API from the named package instead.
- For Python applications, normally use `settings.py` and `export.py`; an existing host may reuse package
  exports without another root aggregate. Add `server.py` only for a server runtime
  and `manager.py` only for a crawler/worker runtime.
- Use `.env` and a redacted `.env.example` when environment configuration is part of the application contract;
  do not add them to explicitly code-configured packages.
- Keep root `settings.py` as the real editable application configuration surface rather than a forwarding shim.
- Keep `export.py` for LangGraph and other Python AI applications; framework manifests do not replace it.
- Use the single-service layering example, or the acyclic aggregation alternative for multi-platform hosts;
  keep shared capabilities independent of handler exports.
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
- When account locking is required, separate authoritative facts from TTL coordination, preserve the chosen
  store, and document durability and retention. Workers request accounts from an account manager.
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

## Embedded workflow integration

The [embedded workflow reference](references/embedded-workflows.md) covers source packages without unnecessary
build scaffolding, injected connections and refresh callbacks, stable persisted identifiers during renames,
stage-specific retry and asynchronous continuation, atomic capacity replenishment, separate production/debug
policy, and architecture documentation for nested packages. It introduces no platform-specific thresholds,
provider configuration, storage migration or rollout authorization.


## Multi-platform applications

The [aggregation guide](references/multi-platform-aggregation.md) covers shared capabilities versus aggregate
entrypoints, protocol-only packages versus host orchestration, platform-owned settings and runtimes, temporary
response adapters, shared retry mechanics with platform decisions, service-owned configuration snapshots,
and lightweight model/matcher adoption. Apply it only to the selected integrations and shared boundaries;
platform billing, account policies and exact response states remain project-specific. Verify historical
responses read-only and distinguish local template changes from live configuration deployment.


## Rules can evolve during implementation

You can add or correct rules while coding is underway; there is no need to edit the Skill first. Clear user
instructions take precedence over its defaults within the task's authorized scope. A demonstrated bug or
unsuitable default should be corrected and verified, not preserved for stylistic compliance. Project-specific
exceptions stay local; reusable changes are written back to the Skill when you request a Skill update.


## Inspectable client components

Keep complete URLs, methods, headers, query and body visible in endpoint request builders. Encapsulate
computed business fields independently from vendor-neutral standard primitives and transport; keep parsers
callable with offline responses. Export these capabilities explicitly. Static dictionaries do not need a
separate parameter layer. See [client components](references/client-components.md) for a complete fictional
example and verification criteria; the Skill contains no project-specific reference names or machine paths.

For framework-based crawlers, reuse native Request objects. Keep explicit endpoint fields in separate API
modules and algorithms/parsers outside spiders; spiders retain business sequencing and callback wiring.
