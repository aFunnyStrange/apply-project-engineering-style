# Cross-Language Mapping

## Contents

- Universal mapping
- Rust
- JavaScript and TypeScript
- Java
- Go
- Mixed-language systems

## Universal mapping

Express the same design intent with each language's native mechanisms:

| Intent | Preferred mechanism |
| --- | --- |
| Stable business data | Domain types with minimal framework coupling |
| Consumer-owned capability contract | Protocol, trait, interface, or small function type |
| Concrete external integration | Infrastructure/platform adapter |
| Persistence semantics | Repository |
| Use-case orchestration | Service |
| Transport adaptation | Handler/controller |
| Route registration | Router |
| Dependency construction | Binary/main/application factory |
| Expected failure | Typed error/result with preserved cause |
| Runtime observation | Structured contextual logging |

Do not create a repository or service wrapper that only renames one function and adds no semantic boundary.
Do introduce the boundary when it isolates external systems, durable state transitions, business orchestration,
testing, or multiple implementations.

Keep every project root limited to configuration, build/tool metadata, README files, and ecosystem-native thin
entrypoints. Put implementation under the language's conventional package, source, crate, module, or workspace
tree. Do not leave business modules, tests, migrations, generated code, or maintained scripts as arbitrary
loose root files.

Use `export.py` only as the Python form of a stable callable surface. For other languages, use their normal
public module, crate, package, or library mechanism. At every language boundary, keep the public surface
importable or callable without starting the full server.

Do not mechanically create Python root files in another language:

| Language | Native structure |
| --- | --- |
| Rust | `Cargo.toml` at root; implementation and entries under `src/` or workspace crates; reusable surface through `lib.rs` |
| JavaScript/TypeScript | `package.json` and tool configs at root; implementation under `src/`; entry selected by package/build configuration |
| Java | Maven/Gradle metadata at root; implementation under `src/main/java`; tests under the build tool's standard tree |
| Go | `go.mod`/`go.sum` at root; application entries under `cmd/<app>/`; reusable code under `internal/` or `pkg/` |

Use a different native layout when the existing project or ecosystem standard is clearer, while preserving the
clean-root outcome.

Use each language's standard asynchronous runtime for external I/O. Keep HTTP, database, queue, filesystem,
subprocess, and external-service adapters replaceable behind native interfaces. Reuse clients and pools, honor
cancellation/timeouts, and bound concurrency. Keep pure computation synchronous when it has no asynchronous
work.

## Rust

- Split crates or modules by capability and responsibility when the workspace is large enough to benefit.
- Keep reusable platform capabilities and infrastructure crates free of HTTP route and business workflow code.
- Put stable entities and state contracts in a domain crate or module.
- Let repositories wrap Redis, SQL, object storage, and external persistence semantics.
- Let services own validation and use-case orchestration.
- Construct `Arc`-shared resources and concrete adapters in the binary or application-state composition root.
- Use traits when alternate implementations or test seams are real. Avoid trait proliferation for private,
  single-purpose helpers.
- Use `thiserror` for library/layer errors and preserve sources. Use `anyhow` primarily at binary/composition
  boundaries where heterogeneous startup failures must be propagated.
- Use Tokio-aware clients and never perform blocking SDK or filesystem work on the async executor.
- Keep HTTP and other I/O clients behind async traits or adapter types selected by the composition root.
- Keep Axum routers and handlers thin; do not put database calls directly in route registration.
- Expose reusable functionality through `lib.rs` and normal public modules. Do not create an `export.py`-style
  wrapper when Rust's module and crate test surfaces already provide direct access.
- Keep unit tests near the tested module when appropriate, integration tests under `tests/` or the workspace's
  established equivalent, and a separate system test for the complete business flow.
- Run `cargo fmt --all`, targeted tests, and `cargo check` using the repository's online/offline constraints.

## JavaScript and TypeScript

- Keep browser collection/runtime code, build/compiler code, backend services, and operational scripts in
  separate modules.
- Prefer TypeScript contracts for new typed projects. In maintained JavaScript, use clear module boundaries and
  JSDoc only where it improves IDE understanding without forcing a migration.
- Keep route/controller code thin and inject service or client dependencies through factories.
- Reuse HTTP agents, database pools, and browser sessions. Bound concurrency and explicitly close resources.
- Express I/O with promises/async functions and keep concrete clients behind injected modules or interfaces.
- Keep large captures and payloads out of Redis/MQ; send references to durable artifacts.
- Preserve original error stacks and contextual fields. Do not log secrets or full protected payloads.
- Validate syntax with the project's toolchain, such as `node --check`, TypeScript compilation, linting, and
  focused tests.
- Keep generated or VMP output separate from editable source; verify build reproducibility instead of manually
  editing generated payloads.

## Java

- Use interfaces at repository and external-capability seams when substitution or testing is needed.
- Keep controllers thin, services focused on use cases, repositories focused on persistence, and configuration
  in dependency-injection modules.
- Prefer immutable DTOs/value objects where practical and validate external input at the boundary.
- Use typed exception categories and retain original causes.
- Use the project's standard async runtime, bounded executors, and nonblocking clients; do not hide blocking
  calls in event-loop handlers.
- Follow the project's formatter, compiler level, static analysis, and test framework rather than importing a
  new framework merely to mirror another language.

## Go

- Define small interfaces near the consuming package.
- Keep transport handlers, services, repositories, and adapters in packages with one-way imports.
- Build dependencies in `main` or a dedicated composition package.
- Pass `context.Context` through I/O boundaries and honor cancellation and deadlines.
- Keep external clients behind small package interfaces and use bounded goroutines for concurrent I/O.
- Wrap errors with operational context while preserving `errors.Is` and `errors.As` behavior.
- Use bounded goroutines and queues. Do not launch one goroutine per unbounded database row.
- Run `gofmt`, `go vet`, focused tests, and the repository's configured linters.

## Mixed-language systems

- Put cross-process contracts in versioned schemas or stable JSON/protobuf models, not duplicated implicit
  assumptions.
- Keep Python ML/crawler components behind a queue, RPC, or library boundary that the server can replace.
- Let the server remain authoritative for identity and business state even when workers use another language.
- Normalize features and task payloads before crossing process boundaries; retain raw artifacts for audit and
  replay, but do not make downstream logic depend on unstable raw layouts.
- Document ownership of each schema, queue, state transition, and artifact.
