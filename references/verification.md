# Verification Checklist

For multi-platform host applications, apply [multi-platform-aggregation.md](multi-platform-aggregation.md)
to the export/handler direction, lightweight shared capabilities and platform-owned settings. The
single-service examples here do not require handlers to import an aggregate that already exports them,
or require unrelated platform configuration to be moved into root settings.

## Contents

- Scope
- Architecture
- Frameworks and libraries
- AI workflows
- State and recovery
- Test levels
- Python
- Other languages
- Observability and security
- Final review

## Scope

- Confirm that every changed file is required by the current request.
- Preserve unrelated user changes and historical/debug artifacts.
- Verify public APIs, deployment paths, configuration names, log paths, and data compatibility.
- Re-read the user's request after implementation to catch omissions hidden by a successful test run.
- For Skill projects, confirm that the English root `README.md` and Chinese `readme-chinese.md` remain
  semantically aligned and explain purpose and quick usage, while `SKILL.md` retains Agent execution
  instructions.

## Architecture

- Confirm the project root contains only configuration/tool metadata, README files, and required thin
  entrypoints.
- For Python, verify discoverable configuration and callable package/application exports. Do not require a
  redundant root aggregate; optional server/manager entrypoints must match actual runtimes.
- For embedded clients, verify injected objects prevent fallback construction, borrowed resources remain
  open after package shutdown, and owned resources close correctly. Check host config mappings and supported
  standalone execution independently; no import should initialize a production connection.
- For other languages, confirm Python filenames were not copied mechanically and implementation follows the
  ecosystem's normal source, package, crate, module, workspace, and test layout.
- Confirm business modules, graph nodes, prompts, tests, migrations, and maintained scripts live inside the
  language's normal owned source/package structure unless an explicit repository/tool contract requires
  otherwise.
- Confirm the selected Python application layout is intentional: either one named implementation namespace or
  flat owned layer packages under the application directory. Reject accidental mixtures and empty wrappers.
- Confirm `.env` is ignored, `.env.example` is redacted and committed, and environment reads are centralized
  behind `settings.py`.
- Check imports and calls, not only folder names.
- Confirm that routers and handlers do not query storage directly.
- Confirm that a Python service exposes stable functionality through `export.py`; check the chosen
  single-service or aggregate direction and ensure handlers never import an aggregate that exports them.
- Confirm that `export.py` can be imported and exercised without starting the server or importing HTTP runtime
  state.
- Run or import the documented root entrypoint from the documented working directory and confirm it does not
  mutate `sys.path` or depend on an undocumented CLI bootstrap.
- Confirm that services do not construct concrete clients or read environment variables.
- Confirm that repositories do not return HTTP/framework response objects.
- Confirm that lower layers do not import upper layers.
- Confirm that concrete dependencies are assembled in one discoverable composition root.
- Confirm `platform` or `platforms` translates unstable third-party APIs and wire semantics into stable
  project-owned contracts rather than serving as a generic miscellaneous or resource-ownership directory.
- Confirm long-lived concurrent runtimes use appropriate asynchronous I/O or bounded blocking adapters, and
  concrete transports are replaceable. A bounded one-shot smoke tool may remain synchronous.
- Confirm that clients, pools, and sessions are reused and that unavoidable synchronous I/O is isolated from
  the async runtime.
- Remove speculative abstractions that have no current consumer, alternate implementation, or testing value.

## Frameworks and libraries

When the changed project is a reusable framework or library:

- Confirm the package-level public API imports without creating application runtime state.
- Confirm vendor-specific types, flags, exceptions, and version branches remain inside adapters.
- Confirm optional extras are not imported by the core package and missing features fail with actionable
  installation guidance only when selected.
- Confirm runtime lazy exports, typed exports/stubs, `__all__`, documentation, and generated imports agree.
- Run shared contract vectors against native/accelerated and fallback backends; reject backends whose hashes,
  bytes, framing, persistent state, or exceptions differ without an explicit versioned protocol.
- Run scheduler and background-task lifecycle tests on every declared interpreter/runtime version. Cover normal
  completion, cancellation, interrupt-driven shutdown, restart, and a producer that can enqueue after a queue
  becomes temporarily empty.
- Confirm stream ownership closes resources on success, callback failure, interceptor replacement,
  cancellation, and shutdown, with bounded concurrency and buffering.
- Confirm acknowledgement occurs only after the represented downstream handoff succeeds and partitioned-log
  commits do not pass unfinished earlier offsets.
- Generate every supported project/demo mode into a temporary directory, import its public entrypoints, and run
  at least one representative flow through the same API path users call.
- Test the declared compatibility matrix: interpreter versions, supported vendor versions, core-only install,
  important extras, claimed runtime topologies, and clean wheel/source-distribution installs.

Read [framework-library-contracts.md](framework-library-contracts.md) for the full contract.

## AI workflows

When the project uses LangGraph or another AI workflow runtime:

- Confirm the graph orchestrates one run while a worker manager, when present, owns task claiming and
  concurrency across runs.
- Confirm nodes call injected services or model/tool/retrieval contracts instead of constructing infrastructure.
- Confirm handlers and managers enter through `export.py`, and graph construction does not start the server or
  perform external I/O at import time.
- Confirm every Python AI application retains root `export.py`, even when `langgraph.json` can reference an
  internal graph module.
- Confirm async handlers use async graph invocation, streaming, providers, tools, repositories, and
  checkpointers without blocking the event loop.
- Confirm live clients and secrets are passed through runtime context or injected dependencies, not graph state.
- Confirm graph state and checkpoints contain execution context rather than authoritative task, account,
  session, billing, or business status.
- Confirm large prompts, documents, captures, and model/tool results are stored as durable artifacts with
  bounded references in state.
- Confirm graph-run concurrency and node fan-out concurrency are independently bounded.
- Confirm retries and checkpoint resume cannot repeat non-idempotent side effects without protection.
- Confirm structured model/tool output is validated and invalid output follows an explicit failure path.
- Confirm unit tests cover isolated nodes or decisions, integration tests cover one graph path with a fresh
  checkpointer, and the total/system test reaches the final durable business result.

## State and recovery

- Identify the durable source of truth for every business state.
- Ensure queues contain lightweight identifiers or references rather than large response bodies.
- Verify atomic claim or ownership behavior under concurrent schedulers.
- Verify that a crash before completion leaves work discoverable.
- Verify that stale locks expire or can be safely reset.
- Verify that one failed task does not starve later tasks.
- Verify partition filters on every scan and status update.
- Verify idempotent completion, unique constraints, and duplicate delivery behavior.
- Verify pending-versus-retry priority and retry bounds.
- Exercise replay or repair paths when parsers or derived data can evolve.

When account locking is requested:

- Confirm that the documented authoritative store owns account/session facts; do not assume a relational
  migration was required. Verify its retention, backup and loss semantics.
- Confirm that workers only request and use accounts through the account manager contract.
- Confirm that lock acquisition, token-safe release, expiry, optional renewal, cooldown, and risk state remain
  inside the account coordination layer.
- Confirm that rate and timing policies come from current user/project configuration and were not copied from a
  reference project.

## Test levels

Require at least one representative test at each of these three levels for projects governed by this Skill:

1. Unit test: exercise one isolated flow and prove it can run through. Replace unrelated infrastructure and
   collaborators with fakes, stubs, in-memory adapters, or direct module calls.
2. Integration test: exercise one narrow business scenario across the components and infrastructure that
   actually collaborate for that scenario. Keep the target specific, such as task submission creating one
   durable row or one worker stage persisting one artifact.
3. Total/system test: exercise the complete business flow from the real outer entry to the final durable state,
   including the major process or transport boundaries that define the product.

Do not use "integration test" as a catch-all name for a complete end-to-end system test. Keep fixtures,
configuration, expected state, and cleanup independent for each level. For a code change, add or update the
lowest level that proves the behavior, then run the affected higher levels.

For discovery-and-collection workflows, also apply
[collection-workflows.md](collection-workflows.md): verify complete discovery coverage, resource-scoped bounded
fan-out, per-item failure isolation, observation-versus-unique counts, and the explicit persistence decision.

## Python

- Run the bundled convention checker on changed paths.
- Run the configured formatter/linter and type checker.
- Confirm Pydantic v2 APIs and constrained fields.
- Confirm `Union`/`Optional` typing rather than PEP 604 syntax.
- Confirm module, class, function, and method docstrings.
- Confirm Protocol/ABC choices match the intended runtime relationship.
- Confirm async code does not call blocking I/O directly.
- Confirm pure computation was not made async without an awaited dependency.
- Confirm client lifecycle, cancellation, and bounded concurrency.
- Confirm root `settings.py` owns concrete editable application configuration, root `.env` is excluded from
  distribution when used, and secrets are revealed only at the concrete adapter boundary.
- Confirm unit tests can reach Python functionality through `export.py` or a direct unit import without starting
  the server.
- Run the affected unit, narrow integration, and total/system tests.
- When `pyproject.toml` declares a distributable application, build wheel/source artifacts from a clean
  temporary copy, inspect member lists for accidental secrets, caches, logs, runtime outputs, and tests when
  excluded, then import the public entrypoints from the built artifact. Do not treat `.gitignore` as package
  configuration.

## Other languages

- Rust: use normal crate/module tests rather than adding a Python-style export layer; run formatting, checks,
  unit tests, narrow integration tests, and the system test under repository constraints.
- JavaScript/TypeScript: run syntax/type checks, linting, build verification, and all affected test levels.
- Java: run the configured formatter/static analysis and all affected build/test levels.
- Go: run `gofmt`, `go vet`, all affected test levels, and configured linters.
- For generated artifacts, rerun the generator and verify reproducibility instead of editing output by hand.

## Observability and security

- Log error returns as well as thrown exceptions.
- Preserve the original source location and traceback/cause chain.
- Include task, stage, platform, and resource identifiers needed to correlate the flow.
- Avoid duplicate context in both bound fields and message text.
- Log successful persistence using identifiers when it is operationally valuable; avoid logging routine large
  responses.
- Bound and redact failure payload samples.
- Confirm credentials, cookies, session tokens, authorization headers, proxy passwords, and private payloads are
  absent from logs and fixtures.

## Final review

- Run `git diff --check` when inside a Git worktree.
- Inspect the complete diff for accidental edits, dead code, temporary debug output, and inconsistent names.
- Compare the final tree and entrypoints with the user's stated structural goal; do not report a refactor as
  successful solely because tests passed.
- Report exactly which checks ran and which could not run.
- Describe any intentional exception to the conventions and the project evidence that required it.

## Capability and standalone-delivery changes

For optional capability changes, apply [capability-evolution.md](capability-evolution.md), including zero calls
when disabled, old-input compatibility, documented fallback, business denial and circuit scope/recovery.
For independent services, apply [service-delivery.md](service-delivery.md), including cached startup, ownership,
clean/rebuild, preserved assets and a smoke request beyond health. Treat documented root operational scripts
and a thin smoke client as valid entrypoints in the architecture checks above.

For embedded package migrations, also apply [embedded-workflows.md](embedded-workflows.md): verify disabled
routing has no new I/O, durable identifiers survive renames, failed final storage does not regenerate work,
pending capacity prevents duplicate replenishment, and debug defaults cannot alter production policy.


For multi-platform changes, also apply [multi-platform-aggregation.md](multi-platform-aggregation.md): verify
common imports do not load platform runtimes, adapters alone own transition fields, shared refresh has a
lifecycle owner in each process, and public status changes preserve platform retry and settlement decisions.


## Client request, algorithm and parser boundaries

For client refactors, apply [client-components.md](client-components.md). Inspect the complete request before
I/O, verify field/signature consistency and public exports, and parse captured responses without a client.
Do not accept a directory-only split, opaque request tuples, static dictionary relays or network-bound
parsers as evidence of readability. Verify vendor-neutral crypto with independent vectors and retain the
actual stream, request-context and resource-ownership contracts.

When a host framework supplies Request, verify API builders return that native type and the normal
scheduler/callback path accepts it directly. Check that spider files contain business orchestration while
endpoint dictionaries, algorithms and pure parsers live in separately importable modules.
