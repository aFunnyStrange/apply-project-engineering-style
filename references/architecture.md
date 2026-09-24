# Architecture and Runtime Boundaries

For multi-platform host applications, apply [multi-platform-aggregation.md](multi-platform-aggregation.md)
to the export/handler direction, lightweight shared capabilities and platform-owned settings. The
single-service examples here do not require handlers to import an aggregate that already exports them,
or require unrelated platform configuration to be moved into root settings.

## Contents

- Clean project root
- Layer model
- Dependency rules
- Server, scheduler, and worker separation
- Storage ownership
- State and reliability
- Scope and migration discipline

## Layer model

Keep the root limited to configuration/tool metadata, README files, thin entrypoints, and the deliberately
selected owned source or layer directories. Read [project-layout.md](project-layout.md) before choosing a named
implementation package or a flat application layout.

Use the following roles as vocabulary, not a directory checklist. Start with a direct readable flow and split
only when a boundary adds concrete ownership, testing or maintenance value. For embedded platform packages,
use [lightweight-platform-packages.md](lightweight-platform-packages.md); the full chains below are optional.

| Layer | Owns | Must not own |
| --- | --- | --- |
| `platform` / `platforms` | Stable project-owned semantics over unstable third-party APIs, versions, exceptions, wire formats, crypto/codecs, and OS capabilities | Business workflows, persistence policy, or leaking vendor types upward |
| `infra` / `infrastructure` | Resource construction and lifecycle such as database pools, cache/MQ clients, filesystem access, and process logging | Business decisions or presenting raw client methods as domain semantics |
| `repo` / `repositories` | Persistence semantics, queries, durable state transitions, mapping storage data to domain data | HTTP responses or crawler orchestration |
| `service` / `services` | Use cases, business validation, domain orchestration, transaction boundaries | Route registration, graph-framework state, or direct environment parsing |
| `workflow` / `graph` | One AI or durable workflow run's steps, branches, interrupts, and resumable control flow | Durable business truth, global task polling, or direct transport handling |
| `handlers` | Adapt transport input/output to service calls when a dedicated handler layer is useful | Persistence queries or reusable business rules |
| `routers` / `routes` | Register endpoints, middleware, and transport wiring | Business workflows or client construction |
| `export.py` / package exports | Publish the stable callable surface of a service, crawler, or worker package and support direct functional tests | HTTP runtime ownership, scheduling, or duplicated business logic |
| `manager` | Act as the top-level crawler/worker entry and directly own scheduling and concurrency | Reusable crawler logic or another redundant executor layer |
| `domain` / `models` | Stable entities, value objects, state enums, and contracts | Framework startup and external client details |
| composition root | Load configuration, initialize resources, inject dependencies, start processes | Reusable business logic |

When a Python service actually needs all these layers, one possible construction order is:

```text
platform/infra -> repo -> service -> export.py -> handlers -> routers
```

The corresponding full call chain is illustrative; omit forwarding-only layers:

```text
router -> handler -> exported API -> service -> repository contract -> infrastructure adapter
```

Allow direct functional tests to stop above the transport layer:

```text
exported API -> service -> repository contract or injected test double
```

For a pure crawler or worker package, use this construction shape:

```text
platform/infra -> repo -> service/crawler -> export.py
```

Make `manager` the separate top-level process entry:

```text
manager -> exported package API -> service/crawler -> repository -> infra/platform
```

Let `manager` implement task scheduling and concurrency itself. It may use internal async tasks, semaphores, or a
bounded queue, but do not introduce a second "concurrency executor" layer that only duplicates the manager.
Nothing should call the manager as a reusable library; reuse the exported package API instead.

Keep `export.py` independent of `server.py`, routers and HTTP framework objects. In the single-service
shape it is also independent of handlers; an aggregate may export handler callables only when handlers never
import that aggregate. Re-export or wrap
stable service callables without copying their business logic. Accept explicit dependencies or factories so
tests can inject doubles without starting the service.

Keep lower layers unaware of upper layers. Keep framework objects at transport boundaries. Return domain or
application results from services and exports rather than HTTP responses.

## Dependency rules

- Define contracts where they are consumed. Let adapters satisfy those contracts.
- For embedded clients, accept the host's existing connection, pool or client directly; infrastructure need
  not be duplicated inside each package. A package runtime creates resources only for modes that need owned
  defaults, reuses explicit injected objects and closes only what it owns. Do not instantiate Redis, database,
  HTTP or object-storage clients inside each operation. Preserve thread-safety and event-loop constraints.
- Keep external I/O boundaries asynchronous in long-lived, concurrent, request-serving, or streaming
  runtimes, and expose replaceable capabilities through contracts. A bounded one-shot tool may remain
  synchronous when an event loop provides no lifecycle or concurrency value. Select concrete HTTP, database,
  queue, and object-storage clients only in the composition root.
- Keep platform wrappers reusable and business-neutral. Normalize vendor request/response types, version
  differences, flags, error categories, and wire details at this boundary. Do not use `platform` as a generic
  home for unrelated helpers or concrete resource ownership.
- Break circular imports with a small protocol/interface or by moving stable types into `domain`; do not solve
  them with runtime imports unless a framework forces that boundary.
- Keep exports explicit when a package is intended as a stable extension surface. Put service, crawler, and
  worker callable APIs in `export.py`; let handlers, direct tests, and `manager` use them instead of reaching
  into internal modules.
- When an AI workflow is present, let the graph coordinate calls to domain services and capability contracts.
  Do not move repository semantics or authoritative business transitions into framework-specific graph state.
- Prefer capability names over misleading deployment names. A module named `service` or `http_core` ages better
  than a name that assumes a gateway/backend split that may later change.
- Avoid generic `utils` modules for domain behavior. Place code with the capability or use case it serves.

## Server, scheduler, and worker separation

Use this default asynchronous flow for server-submitted crawlers and background jobs:

```text
API/server
  -> validate and normalize request
  -> create or update durable task facts
  -> return an identifier

manager
  -> scan eligible durable rows by stage and partition
  -> claim with temporary coordination protection
  -> schedule bounded concurrent calls through the exported package API
  -> load authoritative input by identifier
  -> execute the stage
  -> persist artifact references and state
  -> release or allow expiry of temporary coordination state
```

Apply these constraints:

- Keep the API useful for remote task submission and status access; do not make it own crawler execution.
- Run one manager per process or stage. Let it own both scheduling and bounded concurrency instead of making
  every task poll the database independently or adding a redundant executor layer.
- Use an external MQ when processes or hosts require delivery semantics. Use a bounded in-memory queue after a
  manager has claimed work inside one process.
- Put independent, repairable transformations such as parsing into their own stage when formats evolve or old
  artifacts must be replayed.
- Keep a service entrypoint thin: load settings, build dependencies, configure logging, and start the runtime.
  A crawler/worker manager additionally owns its scheduling and concurrency loop.

Allow a synchronous server-to-service call only when the user explicitly needs a synchronous request/response
operation and its latency and recovery semantics are acceptable.

## Storage ownership

Use each store for the job it can recover:

| Store | Appropriate data |
| --- | --- |
| Relational database | Business facts, task state, account/session facts, identity relationships, timestamps, partitions, artifact URLs, retry metadata |
| Redis | TTL locks, leases, rate-limit counters, account cooldown/risk state, ephemeral coordination/cache state, stream notification |
| MQ/Redis Streams | Lightweight work identifiers and delivery coordination when needed |
| Object storage | Large JSON responses, images, archives, captures, and other immutable artifacts |
| Local files | Development fixtures, bounded logs, and explicitly requested debug output |

Do not use Redis as the only record that a business stage completed. Do not push large response bodies or images
through Redis merely to connect two stages. Persist the artifact first, then pass a stable identifier or URL.

Do not infer that every produced value requires persistence. A returned normalized result may be the complete
business boundary. Adding a file, database write, or object-store artifact is new behavior that needs an
explicit business, replay, audit, or diagnostic purpose.

If a domain legitimately uses Redis as an authoritative short-lived store, document the TTL and loss semantics
and keep that decision separate from durable task facts.

## State and reliability

- Model the smallest explicit state machine that supports recovery. Prefer `pending`, `retry`, and `completed`
  for simple pipelines; add `running`, `failed`, or terminal variants only when their semantics are necessary.
- Store error summary, attempt count, and next eligibility when retries need control. Do not encode an unbounded
  retry loop in a worker.
- Schedule new `pending` work before `retry` work unless the business requirement says otherwise.
- Filter every scan and update by the relevant partition such as `task_month`; a new process must not
  accidentally claim an old partition.
- Claim work atomically where possible. Use a lease token, fencing value, or ownership check when stale workers
  could overwrite newer results.
- Make completion writes idempotent and protect natural uniqueness with database constraints.
- Preserve the durable `pending` or `retry` state if a process dies before completion. Temporary locks must
  expire or be safely reset.
- Ensure one failed item cannot prevent the scheduler from scanning later items. Use cursor-based scans or
  another starvation-resistant traversal.
- Provide a replay path that reads persisted source artifacts and writes versioned parse results or new
  downstream tasks.
- Version parsers or derived records when the same source may need reinterpretation.

## Scope and migration discipline

- Read actual schemas, indexes, row counts, foreign keys, and sample relationships before designing a migration.
- Do not collapse tables merely because fields overlap. Preserve one-to-many and one-to-one cardinality.
- Prefer additive migration and verified backfill before switching readers or writers.
- Keep historical tables or backups when the user relies on them for diagnosis. Remove them only under an
  explicit retention decision.
- Separate schema correction from application refactoring when either change is risky enough to validate alone.
- Preserve deployment paths, log paths, Docker entrypoints, and external API shapes unless the current request
  changes them.
- For a narrow maintenance request, fix the specified surface and avoid unrelated architecture cleanup.
