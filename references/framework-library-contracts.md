# Framework and Library Compatibility Contracts

## Contents

- Decide the public contract first
- Isolate vendor and version differences
- Preserve optional dependency boundaries
- Keep accelerated and fallback backends equivalent
- Own asynchronous lifecycle explicitly
- Treat persistence and acknowledgement as semantics
- Test compatibility as a matrix
- Make generated examples executable evidence

## Decide the public contract first

For a reusable framework or library, define the consumer-facing contract before selecting an implementation.
Use the package's normal public surface, such as `package/__init__.py`, a deliberate `api.py`, or typed public
modules. Do not require a root `export.py`, `manager.py`, or application configuration file merely because an
application built with the library would have those entrypoints.

Keep public request, response, queue, stream, error, flag, and configuration types owned by the framework.
Vendor objects may appear inside one adapter, but must not leak into scheduler, service, plugin, or user-facing
contracts. When an old vendor type has already become public, preserve a bounded compatibility conversion and
document its removal policy instead of spreading it further.

Treat generated projects, templates, import paths, settings names, hook signatures, and extension callbacks as
public contracts when users depend on them. A refactor is incomplete until generated projects still import,
type-check, and execute through supported entrypoints.

## Isolate vendor and version differences

Put a changing third-party client behind a framework-owned adapter selected at the composition boundary.
Normalize these differences inside the adapter:

- synchronous versus asynchronous methods;
- renamed methods, enums, flags, and keyword arguments;
- response, stream, and WebSocket lifecycle;
- transport exceptions and timeout behavior;
- supported interpreter, ABI, and dependency-version ranges.

Translate retryable vendor failures into a framework-owned error while preserving the original exception as
its cause. Do not turn programming errors such as invalid arguments or unsupported options into network
retries.

Select stable capabilities during construction when possible. Do not repeat version checks, optional-import
checks, or mode branches in a hot request or scheduling loop unless the capability can genuinely change during
that object's lifetime. Optimize this only after defining equivalent semantics; removing one branch rarely
matters more than network I/O, serialization, or backpressure.

Keep concrete infra clients one-shot: connect, perform their native operation, and close. Put bounded retry,
cancellation policy, and resource replacement above infra. When concurrent callers observe the same failed
client generation, serialize replacement so one caller creates the next generation and the others reuse it.
Do not automatically replay an arbitrary transaction or non-idempotent operation.

## Preserve optional dependency boundaries

An optional database, queue, native extension, or transport extra must not become a default import-time
dependency. Keep its concrete import inside the adapter or feature module and fail with an actionable install
message only when the feature is selected.

Runtime isolation must not make the public API invisible to IDEs and type checkers. For lazy public exports:

- declare the real symbols under `TYPE_CHECKING` or in a checked stub;
- keep runtime export registries and typed exports synchronized;
- test that every runtime-exported name has a typed counterpart;
- keep `__all__`, documentation, and generated imports aligned.

Use optional-dependency extras to express supported feature bundles. Test both the core install without extras
and each important selected extra; a package import smoke test alone does not prove feature isolation.

## Keep accelerated and fallback backends equivalent

Native acceleration is an implementation choice, not a second protocol. Select the backend once per stable
runtime or component and expose a framework-owned capability. A pure-language fallback must match the native
backend for:

- accepted inputs and returned types;
- byte encoding, hashing, framing, indices, and serialization;
- exceptions and boundary validation;
- persistent data and cross-process interoperability.

Do not mix backends across distributed nodes when they generate different hashes, queue keys, fingerprints, or
serialized bytes. Faster local behavior is invalid if it creates distributed false negatives or makes persisted
state unreadable. If parity cannot be proven, retain one compatible implementation or introduce an explicitly
versioned data protocol with a migration plan.

Contract-test every backend with the same vectors. Include empty, nested, repeated, malformed, compressed, and
boundary-sized values where relevant. Test a core-only environment and an accelerated environment separately.

## Own asynchronous lifecycle explicitly

Every background task must have a discoverable owner, retained reference, completion cleanup, and shutdown
path. Create and register the task before a very fast coroutine can complete. Cancellation must be handled
separately and re-raised after local cleanup.

Do not infer runtime quiescence from an empty queue alone. A callback, WebSocket listener, stream consumer,
signal dispatcher, or other active task may still produce work. Define quiescence from both queue state and the
set of producers or in-flight tasks that can enqueue more work.

Use one idempotent shutdown coordinator. For graceful or interrupt-driven shutdown, order the phases explicitly:

1. stop accepting or claiming new work;
2. cancel and await owned producers/consumers as appropriate;
3. return or leave unacknowledged unfinished deliveries;
4. persist required session or scheduler state while transports are writable;
5. clean only framework-owned transient state when configured;
6. close sessions, pools, clients, and signal tasks.

Run the same lifecycle tests on every declared Python/runtime version. An import test cannot expose scheduler
quiescence races, orphan tasks, cancellation hangs, or version-specific event-loop behavior.

For live streams, make ownership transfer explicit. The consumer that receives a stream must close it, and the
framework must also close it on callback failure, interceptor replacement, cancellation, and shutdown. Bounds
must apply to concurrency and to buffered records or events.

## Treat persistence and acknowledgement as semantics

Persist the minimum complete state required to resume behavior, not merely the obvious queue item. For crawler
or worker requests this may include callback identity, metadata, session identity, cookie attributes, priority,
retry state, and routing information. Define a versioned codec and an explicit compatibility policy.

Redis and message queues are poor stores for unbounded payloads. Use compact binary storage directly when the
backend supports it; do not add Base64 without a transport need. Compress only when the result is smaller, and
bound both encoded size and decompression output to prevent memory exhaustion. Store large bodies and artifacts
elsewhere and queue references.

Acknowledge a delivery only after the downstream durable or replayable handoff it represents has succeeded.
For partitioned logs, never commit past an earlier unfinished offset. On cancellation, crash, or controlled
shutdown, preserve at-least-once recovery by returning leased work or leaving it uncommitted. Make duplicate
processing idempotent.

Treat persistence and transient cleanup as separate policies. Cleanup must be scoped to framework-owned keys,
queues, topics, consumer groups, containers, and volumes. A failure cleaning one backend must not silently skip
independent cleanup that is still safe.

## Test compatibility as a matrix

Derive the matrix from declared support rather than testing only the developer's current environment. Include
the dimensions that can alter behavior:

- minimum and current interpreter/runtime versions;
- minimum, representative, and newest supported vendor-client versions;
- core-only and optional-extra installations;
- in-memory, single-node, sentinel/replicated, and clustered modes when claimed;
- normal completion, interrupt-driven shutdown, cancellation, restart, and dependency failure;
- buffered HTTP, WebSocket, streaming/SSE, or equivalent long-lived transports when supported;
- source checkout, built artifact, and clean installed package.

Keep unit contract tests for adapters and lifecycle helpers, narrow integration tests for one real dependency,
and a total/system test that enters through the public API and reaches the final result. Record unsupported or
unexecuted cells rather than reporting the entire matrix as passed.

Release CI must build once, validate the exact artifacts, install the wheel and source distribution in clean
environments, and publish only those verified immutable artifacts. Keep release-version/tag checks and registry
publishing details in the release workflow or the package-publishing Skill.

## Make generated examples executable evidence

For a framework with project generators or demo templates, verify the generated output rather than only the
template functions. At minimum:

1. generate every supported mode into a temporary directory;
2. confirm the root remains clean and mode-specific files do not leak into other modes;
3. import the generated settings, public API, and runtime entrypoint;
4. run one representative request or message through the same public service/repository path users call;
5. retain bounded logs and a machine-readable result for release diagnostics;
6. clean only the temporary project-local infrastructure created by the test.

Keep local Docker or equivalent infrastructure independent from the application deployment image. Use it as a
replaceable development/test fixture with project-scoped names and explicit `up`, `status`, `down`, and
destructive reset behavior. Production applications should consume configured external endpoints unless the
current deployment contract explicitly co-locates infrastructure.
