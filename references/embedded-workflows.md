# Embedded Packages and Existing Workflow Integration

Use this reference when a reusable package joins an existing application, a resource pool supports requests,
or submission and completion run in different processes. Apply only the relevant sections. These rules do
not prescribe a database, lock policy, resource quota, provider, or rollout default for unrelated projects.

## Contents

- Package and configuration boundaries
- Trace the existing contract before migration
- Resource eligibility and historical state
- Retry, persistence and process handoff
- Capacity maintenance and alerts
- Debug clients and nested architecture
- Verification scenarios

## Package and configuration boundaries

Distinguish an importable source package, a deployed application and an installable distribution. Encapsulated
implementation with an explicit public module is sufficient for a source package; add build metadata only
when installation/distribution is required. A nested package can have its own domain, services, adapters,
state and API without becoming a separate service. Identify any shared sibling dependencies rather than
claiming the nested directory can be copied independently.

The composition root owns external configuration and constructs clients/pools. Reusable operations accept
borrowed connections and typed provider callbacks. State whether each resource is borrowed or owned; close
only owned resources. Share clients within the appropriate event loop/process, and avoid creating asynchronous
pools in temporary synchronous-request event loops. Imports must not create production connections.

Inject a refresh capability when a package must replace an external resource mid-operation; do not force
callers to restart a submitted operation merely to supply a replacement. Keep provider credentials and
supplier-selection logic outside the package. Normalize legacy input shapes once at the boundary, and use
one canonical representation internally. Distinguish unknown values from explicit choices such as direct
connection; never silently treat missing configuration as permission for a fallback.

Honor the project's configuration mechanism. Code defaults are valid for an embedded package; environment
loading belongs only where that contract exists. Document units, allowed ranges, trigger conditions and
scope beside operational settings. Production policy and small debug overrides may use the same API without
sharing mutable global defaults. Do not promote demonstration thresholds to production defaults or make
production import a demo module.

## Trace the existing contract before migration

Follow the real path from router through orchestration, provider, storage, worker and result query. Record:

- eligibility for the new implementation, including input capabilities and output requirements;
- request ID generation, prompt transformations and external correlation IDs;
- response shape, task states, tables/columns, object paths and serialization boundaries;
- persisted continuation context and the worker that reads it;
- initialization, shutdown and fallback ownership.

A package rename does not imply a data migration. Preserve existing key prefixes, persisted implementation
markers and object paths when they remain compatibility contracts. Document intentional naming differences.
Do not rename historical markers merely to make them match the new source directory.

When a migration switch is requested, evaluate it before importing/initializing new runtime dependencies or
doing new I/O. Route unsupported capabilities to the established path according to the user's contract.
Do not infer permission to fall back to another account/provider after execution has begun. Define rollback
for both new requests and already submitted work; turning off new routing must not strand existing jobs.

## Resource eligibility and historical state

Separate raw record lookup from selection for a new operation. Records may remain queryable while invalid,
out of quota, temporarily occupied, or missing required capabilities. Do not delete or permanently invalidate
a record solely to exclude it from one request. An explicitly selected identifier must use the same store and
eligibility policy unless the operation explicitly requires diagnostic/raw access.

Deduplicate by the established natural identity, atomically at the store. Importing an old record must not
reset counters, invalidation or diagnostic flags on an existing record. Preserve unknown optional fields as
unknown; do not fabricate credentials or silently classify incomplete records as usable. Validate before
writing where practical, and make interrupted imports replayable without destructive overwrite.

Keep immutable provenance separate from current execution state. For example, retain a creation-time endpoint
snapshot while tracking whether reuse has been disabled. Specify the exact failure class and scope that
changes this state; a transport issue must not automatically mean the account itself is invalid.

If leases are part of the contract, bound selection/acquisition and cleanup separately, renew with owner
checks, and cancel or fence stale owners. Empty or busy inventory should produce a defined outcome, not wait
indefinitely for a producer. Window counters need explicit timezone, increment semantics and expiration;
usage accepted by a provider is not necessarily the same event as successful final persistence.

Inventory every key family: owner, type, identity/partition format, fields, TTL, cleanup and loss semantics.
Distinguish expiring coordination/counters from intentionally retained sessions and job history. Evaluate
commands against the deployed server version separately from client-library API compatibility. Multi-key
scripts do not imply cluster compatibility; disclose scanning/blocking costs at the intended pool scale.

## Retry, persistence and process handoff

Maintain one owner of request-level rotation. Track resources already tried within a logical request and keep
its stable request ID across attempts. Do not fake usage or permanent invalidity to prevent a local retry.
Specify both per-attempt bounds and the overall exhaustion/deadline behavior; nested retries can otherwise
multiply unexpectedly. Follow the user's replay policy when the remote outcome is uncertain, and disclose
possible duplicate remote effects if that policy permits another submission.

Define retry decisions per stage:

| Stage | Decision to establish |
| --- | --- |
| Selection or explicit submission rejection | Whether another eligible resource may be attempted |
| Submission with uncertain acceptance | How to reconcile existing remote work before any replay |
| Accepted asynchronous work | Which persisted context and worker continue it |
| Terminal polling failure | Whether it is terminal or permits an explicitly authorized new submission |
| Artifact/database write failure after acceptance | How to repair storage without regenerating remote work |

A continuation worker may need an accepted job's saved identity/context even when that identity is no longer
eligible for new submissions. Do not force read-only continuation through new-work quota or lease selection
unless that operation requires it. Do not hold a submission lock for the whole remote job lifetime by default.

Separate attempt diagnostics from the final task row. If the existing schema admits only one row per logical
request, an intermediate failed insert can block the final success. Use the existing attempt ledger when
required, or persist only the final outcome and keep attempt diagnostics separately. Preserve response and
query-ID contracts; verify stored context can be read by the existing worker and result endpoint.

## Capacity maintenance and alerts

When automatic replenishment is requested, use one API for scheduled and failure-triggered checks. Compute
eligible inventory with the same quota/capability/invalidity rules as selection, while deciding explicitly
whether temporarily leased resources count as stock. Include queued quantities and active remaining work
before calculating a deficit. Make check-and-enqueue atomic or otherwise idempotent under concurrent calls;
an uncertain enqueue timeout must not lead to an unconditional duplicate submission.

Separate the trigger threshold, desired stock and maximum addition per call. A per-call cap can intentionally
leave a deficit. Identify the actual maintenance triggers: failure-only checks do not guarantee replenishment
after successful consumption or during idle periods. Do not invent a timer/service merely because the API
could support one. Producers own creation budgets and recovery; requests need not wait for replenishment.

For requested invalidation alerts, use the host application's notifier through an injected capability.
Include stable resource/request identifiers and a diagnostic record locator, not credentials or full session
snapshots. Classify authoritative invalidation separately from ordinary request failure. Choose one alert
owner and isolate advisory alert/capacity errors from primary work when the business contract allows it.
Use bounded transport I/O and explicit task cleanup; cancellation must not leave unowned notification threads.

## Debug clients and nested architecture

Extract meaningful reusable operations into the package API; production and demo entrypoints should not
import each other. Keep scenario orchestration separate: a normal demo should exercise real selection and
usage policy, while a repeated-resource probe can deliberately bypass local selection under its stated test
contract. Make that difference visible; do not claim the probe proves production admission behavior.

Reuse protocol, storage and lifecycle implementations instead of preserving obsolete client emulation.
Retain intentional output differences, such as local test reports versus production object/database storage.
No debug entrypoint should silently enable production rollout, send notifications or refill at production
scale merely by importing another module.

Architecture documentation should explain both the outer service and substantial nested packages. For each,
show the public API and actual returned contract, internal layers, state owner/lifetime, protocol transports,
resource cleanup, shared dependencies and known gaps. Distinguish public summaries from internal detailed
reports, simulated process phases from real processes, and isolated tests from verified live behavior.

Service operational logs and protocol diagnostics may have different owners, retention and independent
switches. Correlation needs the affected resource identity as well as a batch/job ID. Recheck ignore rules
against the actual repository root after moving packages; source ownership, Git tracking and distribution
inclusion are separate decisions.

## Verification scenarios

Select the cases changed by the task rather than adding a generic checklist to every project:

- Disabled rollout creates no new clients; supported and unsupported requests preserve their respective paths.
- A historical incomplete record is retained but not accidentally admitted; duplicate import preserves state.
- Rotation tries each resource once, stores the intended final outcome, and terminates on exhaustion.
- Accepted asynchronous work continues after quota/eligibility changes and after routing rollback.
- Polling or final-storage failure does not silently create a second remote job.
- Concurrent replenishment counts queued/active work; small demo overrides leave production settings intact.
- Alert failure cannot prevent the specified rotation, and transient errors do not emit invalidation alerts.
- Owner-safe lease cancellation and borrowed-client cleanup do not affect another operation's resources.
- Tests replace external boundaries without changing production routing, serialization or state transitions.

Do not label mocked protocol success as a live deployment check. Keep syntax, type checking, runtime/library
compatibility, server-command compatibility and end-to-end verification as distinct claims.
