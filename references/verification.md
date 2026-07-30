# Verification Checklist

## Contents

- Scope
- Architecture
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
- For Python, confirm required thin `settings.py` and `export.py` entries, plus optional `server.py` or
  `manager.py` entries, match the actual runtimes.
- For other languages, confirm Python filenames were not copied mechanically and implementation follows the
  ecosystem's normal source, package, crate, module, workspace, and test layout.
- Confirm business modules, graph nodes, prompts, tests, migrations, and maintained scripts live inside the
  language's normal owned source/package structure unless an explicit repository/tool contract requires
  otherwise.
- Confirm `.env` is ignored, `.env.example` is redacted and committed, and environment reads are centralized
  behind `settings.py`.
- Check imports and calls, not only folder names.
- Confirm that routers and handlers do not query storage directly.
- Confirm that a Python service exposes stable functionality through `export.py` and that handlers use that
  public surface.
- Confirm that `export.py` can be imported and exercised without starting the server or importing HTTP runtime
  state.
- Confirm that services do not construct concrete clients or read environment variables.
- Confirm that repositories do not return HTTP/framework response objects.
- Confirm that lower layers do not import upper layers.
- Confirm that concrete dependencies are assembled in one discoverable composition root.
- Confirm that every external I/O boundary is asynchronous and that concrete transport clients can be replaced
  without changing business logic.
- Confirm that clients, pools, and sessions are reused and that unavoidable synchronous I/O is isolated from
  the async runtime.
- Remove speculative abstractions that have no current consumer, alternate implementation, or testing value.

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

- Confirm that MySQL/Postgres, not Redis, owns real account and session facts.
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
- Confirm unit tests can reach Python functionality through `export.py` or a direct unit import without starting
  the server.
- Run the affected unit, narrow integration, and total/system tests.

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
- Report exactly which checks ran and which could not run.
- Describe any intentional exception to the conventions and the project evidence that required it.
