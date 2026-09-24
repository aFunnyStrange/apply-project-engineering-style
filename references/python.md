# Python Conventions

For multi-platform host applications, apply [multi-platform-aggregation.md](multi-platform-aggregation.md)
to the export/handler direction, lightweight shared capabilities and platform-owned settings. The
single-service examples here do not require handlers to import an aggregate that already exports them,
or require unrelated platform configuration to be moved into root settings.

## Contents

- Compatibility and typing
- Contracts and dependency injection
- Pydantic v2
- Async I/O
- Structure and entrypoints
- Documentation and logging
- Configuration and tests

## Compatibility and typing

- Target the Python version declared by the project. For new compatible code, avoid syntax newer than the
  supported runtime.
- Write unions with `Union[A, B]` and nullable values with `Optional[T]`. Do not use PEP 604 `A | B` syntax.
- Add explicit parameter and return annotations to public functions, methods, protocols, and important internal
  boundaries.
- Use precise aliases for JSON objects, task payloads, identifiers, and callback signatures. Keep `Any` at
  unavoidable framework or third-party boundaries instead of letting it spread through services.
- Use `TypedDict` for stable mapping shapes, Pydantic models for validated boundaries, and dataclasses or domain
  classes for behavior-rich internal data where appropriate.
- Use `TYPE_CHECKING` for annotation-only dependencies when avoiding runtime imports or cycles; do not
  replace known types with `Any`. For Python 3.8, use `List`, `Dict`, `Tuple`, `Optional` and `Union`.
- Prefer explicit `Optional` handling and early returns over unchecked attribute access or broad casts.

Example:

```python
"""Define the task storage contract used by the scheduler."""

from typing import List, Optional, Protocol


class TaskStorageProtocol(Protocol):
    """Describe durable task operations required by the scheduler."""

    async def claim_tasks(self, stage: str, limit: int) -> List[int]:
        """Claim eligible task identifiers."""
        ...

    async def mark_completed(self, task_id: int, artifact_url: Optional[str]) -> None:
        """Persist a completed task result."""
        ...
```

## Contracts and dependency injection

- Prefer concrete types for known clients and responses, using `TYPE_CHECKING` for annotation-only imports
  when appropriate. Use `Protocol` or a callable type for a real replaceable seam; do not invent an interface
  for every function, storage call or transport.
- Use `ABC` plus `@abstractmethod` when explicit inheritance, shared behavior, or lifecycle enforcement is part
  of the design. Raise `NotImplementedError` from abstract method bodies when a concrete body is required.
- Do not create both a Protocol and an ABC for the same boundary without a concrete reason.
- Inject actual connections, pools or clients through constructors or explicit parameters. In an embedded
  package the host normally constructs them; a package-owned runtime may construct defaults for standalone
  use. Do not add a factory/provider wrapper unless it adds real lifecycle or replacement behavior. Close
  owned resources only; injected objects take precedence over configuration-based construction.
- Give each crawler/spider a one-way dependency on common downloader and repository contracts. Do not chain
  platform spiders through each other.
- Publish stable callable APIs in root `export.py` for concrete service, crawler, and worker applications. Let
  handlers, direct tests, and the top-level crawler/worker `manager` use those exports instead of importing
  internal modules ad hoc.
- For a reusable Python framework or library, publish the stable surface through the named package's
  `__init__.py`, a deliberate `api.py`, or typed public modules. Do not add a root `export.py` or `manager.py`
  unless the repository also contains that concrete application runtime.
- Keep `export.py` free of HTTP framework objects and server startup. Re-export operations directly; wrap
  only when performing real adaptation
  without duplicating business logic, and accept injectable dependencies where direct unit tests need doubles.

## Pydantic v2

- Use Pydantic v2 APIs and imports. Do not add v1 `validator`, `root_validator`, nested model `class Config`,
  `parse_obj`, or `.dict()` patterns.
- Use `ConfigDict`, `field_validator`, `model_validator`, `model_validate`, and `model_dump`.
- Use `Field` constraints for ports, limits, timeouts, identifiers, and other validated configuration.
- Use `SecretStr` or an equivalent secret type for credentials. Reveal a secret only at the adapter call that
  requires it.
- Put API request/response models near the application boundary and crawler models near the crawler boundary
  when their contracts differ. Do not reuse one oversized model across unrelated layers.
- Keep internal domain models independent from FastAPI request objects.
- Keep an explicitly code-configured package independent of environment loading; inject external connections
  and callbacks instead. For environment-based applications, use `pydantic-settings` when appropriate or load
  `os.getenv` values explicitly into a Pydantic v2 model. Preserve precedence:
  process environment, then `.env`, then code defaults.

Example:

```python
"""Define validated worker settings."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, SecretStr


class WorkerSettings(BaseModel):
    """Store validated worker runtime settings."""

    model_config = ConfigDict(extra="forbid")

    redis_url: SecretStr
    task_month: str
    concurrency: int = Field(default=4, ge=1, le=100)
    proxy: Optional[SecretStr] = None
```

## Async I/O

- Use `asyncio` for long-lived, concurrent, request-serving, or streaming runtime entrypoints and their network,
  database, queue, filesystem, subprocess, and crawler I/O boundaries.
- Permit a bounded one-shot migration, verifier, converter, or developer tool to remain synchronous when it has
  no concurrency, cancellation, streaming, shared event-loop, or async-caller requirement. Record the reason
  when this differs from the surrounding application runtime; do not convert a real application boundary to
  synchronous code for convenience.
- Use the established async HTTP/downloader client directly when its concrete type is known. Define a
  `Protocol` only for a meaningful replaceable contract. The Skill does not mandate one HTTP library or a
  new transport abstraction for every client package.
- Reuse async HTTP sessions and connection pools. Do not create a new client for each request.
- Offload unavoidable synchronous SDK or filesystem work with an adapter supported by the declared runtime.
  `asyncio.to_thread` requires Python 3.9+ unless the project explicitly supplies or accepts an exception.
  Syntax checks alone do not validate standard-library availability or dependency interpreter requirements.
- Keep CPU-only parsing, normalization, validation, and value transformations synchronous when they do not
  await anything. Do not add meaningless `async def` declarations to pure functions.
- Do not hold an async lock across unrelated slow work. Scope locks to the resource or platform behavior they
  protect.
- Use bounded queues and bounded concurrency. Never create unbounded task lists from a production-sized scan.
- Handle `asyncio.CancelledError` separately and re-raise it.
- Close sessions, pools, and clients in an explicit lifecycle method or async context manager.
- Avoid infinite account or task scans. Complete one bounded traversal and return a clear failure or retry
  result.

## Structure and entrypoints

Keep the project root limited to configuration/tool metadata, README files, thin application entrypoints, and
the deliberately selected owned source directories. A named implementation package is the default, but flat
layer packages are valid when the project directory itself is the explicit application and deployment unit.
Read [project-layout.md](project-layout.md) before choosing either model. A named-package application may use:

```text
project/
├── settings.py          thin configuration entry
├── export.py            stable API and optional direct tests
├── server.py            optional thin server entry
├── manager.py           optional thin worker entry
└── package_name/
    ├── platforms/ or platform/
    ├── infra/
    ├── repo/
    ├── service/
    ├── workflow/ or graph/
    ├── app/models/
    ├── app/handlers/
    ├── app/routers/
    ├── crawler/models/
    ├── crawler/spiders/
    └── tests/
```

- Read [project-layout.md](project-layout.md) for the complete root allowlist.
- Do not create a redundant wrapper namespace merely to imitate the named-package diagram. In a flat layout,
  keep every layer explicitly owned and avoid top-level package names that shadow the standard library.
- Use a stable callable surface, normally package/application `export.py`. An existing host can call package
  exports directly without a redundant root aggregate; reusable libraries may use their named package API.
- Keep service entrypoints such as `server.py` thin.
- Let single-service handlers call the stable `export.py` API; when an aggregate exports handlers, those
  handlers call platform services directly and import common types from a separate public capability surface.
  Keep the chosen business entrypoint directly testable with injected
  repositories or fakes so unit functionality does not require starting FastAPI or another server.
- Make a pure crawler/worker `manager.py` the top-level scheduling and concurrency entry. Let it call
  `export.py`; do not add a separate concurrency-executor layer and do not design another caller above manager.
- Expose importable `main()` or application factory functions that can be called directly from an IDE debugger.
- Use `async def main()` plus `asyncio.run(main())` for directly executed Python runtimes.
- Make the documented runtime file the real entrypoint from the project root. Do not require callers to change
  directories, mutate `sys.path`, or invoke a CLI wrapper before normal execution.
- Keep `export.py` as pure re-exports when sufficient. Direct guarded demos are optional; respect no-CLI
  requirements and do not add command-line parsing solely to demonstrate exports.
- Do not add command-line interfaces elsewhere unless the user explicitly asks. Run other tools and entrypoints
  as `python xx.py`; adjust a settings file or deliberately editable Python parameters for Console Debugger
  workflows.
- Treat framework development commands such as test runners, graph development servers, migration tools, and
  debuggers as toolchain commands rather than custom application CLIs. For an application they do not replace
  `export.py`; for a reusable library they do not replace its importable package API.
- Keep temporary debugging entrypoints separate from reusable core logic.

## Documentation and logging

- Add a triple-double-quoted docstring to every module, class, function, and method.
- Describe purpose, inputs, outputs, and raised errors for nontrivial public interfaces. Keep obvious private
  helpers concise rather than filling them with generic boilerplate.
- Replace `print` with the project logger in maintained runtime code.
- Configure each standalone server or worker to log to the terminal and its expected file when the project
  requires persistent local logs.
- Attach stable context such as task ID, query ID, platform, stage, and environment once through logger context.
  Do not repeat the same identifiers in every message.
- Log database/object-store state changes and identifiers, request failures, abnormal parse results, account
  failures, and returned error branches.
- Avoid logging routine successful responses, full large payloads, credentials, cookies, proxy passwords, or
  tokens. Truncate bounded failure samples.
- Preserve meaningful traceback and original source location. Avoid wrappers that make every log appear to come
  from the logging helper.

## Configuration and tests

- Make `settings.py` a complete, discoverable configuration surface for its owned defaults. Reusable
  validation and parsing may live in owned modules. Explicitly aliasing or mapping host shared settings is
  valid for an embedded package; do not duplicate credentials or recreate an injected connection from them.
  Keep host-free standalone configuration usable when promised, with documented override precedence.
  Do not scatter environment reads through services, graphs, nodes, or spiders.
- If the application uses environment configuration, keep local `.env` ignored and commit a redacted
  `.env.example`. Code-configured embedded packages need neither file.
- For that environment-based contract, keep machine-local endpoints and secrets in `.env`; preserve process
  environment, then `.env`, then code
  default precedence. Preserve operator-required connection fields as separately validated values instead of
  collapsing them into a more opaque representation for implementation convenience.
- Validate configuration before starting long-lived processes.
- Preserve Docker paths, working directories, log locations, and launch behavior during refactors.
- Add unit tests that call `export.py` or a directly imported internal unit with protocol-compatible fakes.
  Make each test prove that one isolated flow can run through without starting the service.
- Add integration tests for one narrow business scenario at a time. Exercise the relevant collaborating
  services, repositories, adapters, and test infrastructure without expanding the case into the full product
  lifecycle.
- Add a total/system test that runs the complete business flow from its real entry through the final durable
  result. Keep it distinct from narrow integration tests.
- Cover task transitions, retry priority, partition filtering, restart recovery, bounded scheduling, parser
  edge cases, and cancellation at the appropriate test level.
- Run the repository's formatter, linter, type checker, and focused tests. Use the bundled checker for the
  personal rules not normally covered by standard tools:

```bash
python3 scripts/check_python_conventions.py path/to/changed_package
```

- For distributable applications, build from a clean temporary copy without local secrets or runtime outputs,
  inspect wheel/source-distribution members, and import the public configuration, export, and runtime surfaces
  from the built artifact. Source-tree imports do not prove package discovery is correct.
