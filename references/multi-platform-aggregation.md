# Multi-platform Aggregation

Use this reference when one application hosts independently maintained platform integrations and shared
business capabilities. Apply only to the selected platforms and shared seams; it is not authorization to
rewrite other teams' integrations. These guidelines refine the single-service layout in the other references.

## Choose ownership before directories

Inspect the whole host application's entrypoints, imports, configuration, storage, workers and documentation
before moving the selected integration. Identify who owns protocol facts, business decisions, resource
lifetimes and public compatibility. A platform directory may be a protocol client, a self-contained workflow
or a companion service; its current name alone does not establish its intended responsibility.

For a protocol-only package, keep vendor requests, uploads, parsing, explicit session input and normalized
input/output results inside the package. Keep account selection, business retries, billing, persistence and
public response mapping in the host's platform-specific service. Inject transport/proxy providers and borrowed
resources; the protocol package must not import the host runtime or discover production credentials.

If the user instead chooses an embedded workflow package, it may own platform-specific retries through
injected capabilities. Do not impose both models at once. When the boundary changes, move the implementation
and update callers, examples and documentation together; a callback wrapper alone does not separate ownership.

Within a shared layer, group multiple files for a platform under one platform folder rather than growing
parallel platform-prefixed files. Preserve established protocol packages. Extract a companion service only
when its lifecycle, state and operational responsibilities justify it; a scripts directory is for entrypoints,
not a hiding place for a substantive service. Avoid maintaining duplicate protocol implementations after a move.

## Prefer an embedded workflow when it keeps ownership clearer

A valid lightweight shape is `router -> platform/export.py -> platform business -> platform protocol`, with
`worker -> platform update_callback(row)` for submitted work. The platform business package may own account
rotation, billing and persistence using injected pools and host response callbacks. Its protocol subpackage
owns only upstream input/output. Do not retain host handlers/services/infra/adapters that merely relay calls.
Keep existing shared response implementations at the host boundary and pass them in when the package needs
classification or formatting. This does not remove platform decisions needed before settlement.

A generic retry engine is optional. Share it only when real callers share attempt semantics; platform account
rotation and an already-submitted task's polling are different operations. Do not infer retry or billing from
public response status alone. Read [lightweight-platform-packages.md](lightweight-platform-packages.md).

## Separate reusable capabilities from application entrypoints

When multiple consumers actually need new common capabilities, expose them through a lightweight public surface, such as
`capabilities`. It must not import platform handlers, application startup, concrete connections or all vendor
SDKs. Internal framework modules may import implementation modules directly to avoid reverse dependencies;
platform consumers and documentation should use the public surface consistently.

If needed, a root `export.py` that aggregates full business entrypoints has a different role. It is optional
when routers already call package exports. Two possible aggregate shapes are:

- A single service's handlers call a service export; the export does not import those handlers.
- A multi-platform host's routers and root exports both call platform handler entrypoints; handlers do not
  import that aggregate export. Shared capabilities remain independently importable.

Choose one direction for each surface. Do not create `export -> handler -> export`, including cycles hidden
behind response-model imports. Neither export style should initialize production connections on import.
The aggregate can offer the same parameter construction and complete workflow used by routers for IDE
execution. A protocol demo should exercise protocol operations; a business demo should enter the actual
business workflow. State which it tests, and remove duplicate business orchestration from demos.

Host infrastructure can pass its existing connection or pool objects directly into platform packages; they
need not each implement infra. Package settings may explicitly map common host settings while retaining
complete platform-owned defaults for direct execution. Injected objects are reused, not reconstructed, and
only their owner closes them. Keep standalone profiles independent of mandatory host imports when required.

Root settings own service-wide defaults and lifecycle configuration. Platform configuration lives in an owned
platform module, for example `config/<platform>/settings.py`. The root need not collect every platform's
credentials, version policy and counters. Shared configuration must not become a platform-specific dumping
ground, and an individual platform runtime must not secretly own a service-wide feature.

## Preserve protocol facts; adapt legacy contracts at the boundary

A protocol client should describe actual supported inputs and outputs, including text, media and mixed or
unknown output when the provider supports them. Do not infer a vendor request version from an output that
has not happened yet. Host policy maps legacy request labels to explicit version/options and translates the
result back to the public contract. Do not invent unsupported upstream wire formats for future extensibility.
Where the project uses typed results, expected unsupported capabilities can return an explicit unsupported
result; preserve genuine technical failures and never silently discard supplied input.

Keep canonical results free of transition-only copies. An application adapter owns legacy field names,
envelopes and temporary dual writes. Keep artifacts and useful diagnostics when projecting errors, refusals
or wrong output types. Initial and polling responses should use the same declared schema when required.
Use extensible Pydantic models when the contract requires unknown fields to survive, while still validating
required fields and enums. Constructing a response model validates/serializes data; it does not classify,
retry or bill a request by itself.

Share classification over explicit parsed facts, optionally with an injected parser. Lightweight scripts and
routers may use just the response type or a rule matcher without adopting an entire runtime. Do not turn
sample status names, refusal precedence or text-mismatch behavior into universal platform policy. Confirm the
current contract and test conflicts between evidence, usable artifacts, technical errors and pending work.
A local request ID alone does not prove asynchronous work was accepted. Text output alone cannot reliably
reveal semantic refusal; match only the evidence the contract recognizes and keep unknown distinct from a
confirmed refusal. Do not grow a phrase catalog merely to compensate for missing protocol evidence.

## Share retry mechanics, retain platform decisions

Keep response classification, retry action and billing settlement as distinct typed decisions. A generic
executor can bound attempts/deadlines and call injected operations, selection/rotation and cleanup functions.
The platform service decides which stage and evidence permit another attempt, which account is eligible,
and how accepted remote work is resumed. Do not mechanically retry every failed/unknown public status.

Changing public fields or adding states must not accidentally change account rotation, quota consumption,
submission replay or polling behavior. Check these paths explicitly, including exhaustion and final storage
failure. Billing, quota windows, daily resets and permanent invalidation remain platform policy; shared
mechanics must not embed one platform's counters or convert uncertain outcomes into permanent account loss.

## Service-owned configuration snapshots

For shared hot-reloadable tables, define the source of truth at startup and during runtime separately. Local
bootstrap, full local-template replacement and remote-authoritative configuration are different contracts.
If startup replacement is requested, validate all templates first, remove deleted managed entries, and avoid
deleting unrelated keys. Keep backups outside the discovery glob. Namespace keys by the actual application
and feature; platform overrides should have explicit merge/disable semantics.

Let service startup own discovery, initial loading and refresh shutdown. Readers obtain a validated in-memory
snapshot, without per-request remote I/O when snapshot refresh is the chosen contract. Validate a candidate
batch before atomic publication, retain the last valid snapshot on refresh failure, and define cold-start
failure behavior. Each worker/process needs its own initialization/refresh strategy; an ordinary imported
getter does not create a background timer or share another process's memory. Keep refresh cadence configurable;
do not copy a one-hour interval from an example as a universal requirement.

## Verification and colleague-facing documentation

Use read-only, platform-scoped historical samples to validate parser and response changes when authorized.
Inspect actual table fields and archive shapes, separate missing old data from parser regressions, and cover
recent responses plus older formats relevant to the change. Include positive and negative evidence and
wrong/mixed modalities. Avoid preserving prompts, sessions or archive credentials in regression fixtures.
Replay should not resubmit generation, charge accounts or rewrite production history unless explicitly asked.

Verify the changed boundary with import checks, focused classification/adapter tests and the affected real
workflow tests. Check disabled routing, submitted-task continuation and retry/settlement invariants where
applicable. After moves, audit actual tracked and ignored files, log paths, imports and startup/demo commands;
`.gitignore` neither untracks existing files nor controls package contents.

The root README should explain ownership, public imports and the shortest adoption path. Dedicated guides
should show minimal model-only and matcher-only use, optional full classification/retry integration, and
links to real maintained call sites. Keep platform billing and provider details in platform guides. Document
current APIs rather than inventing migration advice for consumers that never used the draft. Report which
code/templates changed separately from whether live configuration was updated or a service restarted.
