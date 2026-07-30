# Clean Project Root Layout

## Contents

- Root-directory rule
- Cross-language rule
- Python root files
- Package ownership
- Python service layout
- Python worker layout
- LangGraph and AI layout
- Exceptions and migration

## Root-directory rule

Keep the project root as a small allowlist containing only:

1. project configuration and tool metadata;
2. user-facing README files;
3. thin executable, configuration, and export entrypoints.

Put all implementation details inside the language's normal named package, source tree, crate, module, or
workspace location. Do not leave business modules, clients, repositories, services, handlers, routers, graph
nodes, prompts, utility modules, test logic, migrations, or ad hoc debug programs loose in the root.

## Cross-language rule

The clean-root rule is universal; concrete filenames are language-specific.

- Python uses the root entry/configuration files defined below.
- Rust normally keeps code and binary entries under `src/` or workspace crates and exposes reusable APIs
  through `lib.rs`.
- JavaScript/TypeScript normally keeps code under `src/` and uses the package's configured module/bin entry.
- Java normally keeps code under `src/main/java` and uses the build framework's application entry.
- Go normally keeps application entries under `cmd/<app>/` and reusable code under `internal/` or `pkg/`;
  a small root `main.go` is acceptable only when it is the idiomatic thin entry for that project.

Do not create `settings.py`, `export.py`, `server.py`, or `manager.py` in a non-Python project. Preserve the
intent with native manifests, public modules/packages/crates, and application entrypoints.

Tests, migrations, generated sources, and operational scripts follow the ecosystem's established source or
workspace layout. They still must not become arbitrary loose root files.

## Python root files

For Python projects, use only the entries that the project actually needs:

```text
project/
├── README.md
├── readme-chinese.md
├── pyproject.toml
├── lockfile
├── .gitignore
├── .env
├── .env.example
├── settings.py
├── export.py
├── server.py
├── manager.py
├── langgraph.json
├── Dockerfile
├── compose.yaml
└── package_name/
```

Interpret the entries as follows:

- `README.md` and `readme-chinese.md` are user documentation.
- `pyproject.toml`, lockfiles, formatter/linter/type-checker configuration, container definitions, CI metadata,
  and framework manifests are project/tool configuration.
- `.env` is a local runtime file. Keep it ignored and never commit secrets.
- `.env.example` is the committed, redacted variable contract.
- `settings.py` is the thin root configuration entry. Keep validated settings models and parsing details inside
  the package; re-export or construct them here.
- `export.py` is required for Python application projects, including services, crawlers, workers, LangGraph,
  agent, RAG, and other AI workflows. It exposes a stable directly testable API and may provide the permitted
  `__main__` or CLI debug surface.
- `server.py` exists only when the project has a server process. Keep it to settings loading, dependency
  construction, logging setup, application creation, and runtime start.
- `manager.py` exists only when the project has a crawler/worker process. Keep it as the executable bootstrap
  for the one package manager that owns scheduling and concurrency; do not add another executor layer.
- `langgraph.json` or an equivalent framework manifest is configuration, not implementation.

Do not create empty placeholder entrypoints. Omit `server.py`, `manager.py`, `langgraph.json`, container files,
or other optional entries when that runtime does not exist.

## Python package ownership

Move Python implementation into the named package:

```text
package_name/
├── domain/
├── platform/
├── infra/
├── repo/
├── service/
├── workflow/
├── app/
│   ├── handlers/
│   └── routers/
├── config/
├── runtime/
├── prompts/
├── tests/
├── migrations/
└── scripts/
```

Create only the directories the project needs. The rule is about ownership, not forcing every layer into every
project or language.

- Put reusable and business implementation in the package.
- Put unit, integration, and total/system tests under the package's `tests/` unless an existing tool or
  repository contract requires another location.
- Put migration code and revisions under the package; keep only a required root tool configuration such as
  `alembic.ini`.
- Put maintained operational scripts under the package. Temporary one-off debugging files must not accumulate
  in the root.
- Put runtime logs, captures, outputs, caches, and generated artifacts in configured external or ignored
  directories, not as loose root files.

## Python service layout

```text
project/
├── README.md
├── readme-chinese.md
├── pyproject.toml
├── .env
├── .env.example
├── settings.py
├── export.py
├── server.py
└── package_name/
    ├── config/
    ├── platform/
    ├── infra/
    ├── repo/
    ├── service/
    ├── app/handlers/
    ├── app/routers/
    └── tests/
```

Call direction:

```text
server.py
  -> package composition/application factory
  -> routers
  -> handlers
  -> root export.py stable API
  -> package services
  -> repositories
  -> infrastructure/platform
```

`export.py` must remain importable without starting `server.py`.

## Python worker layout

```text
project/
├── README.md
├── readme-chinese.md
├── pyproject.toml
├── .env
├── .env.example
├── settings.py
├── export.py
├── manager.py
└── package_name/
    ├── config/
    ├── platform/
    ├── infra/
    ├── repo/
    ├── service/
    ├── runtime/manager.py
    └── tests/
```

The root `manager.py` is only the executable bootstrap. The package manager is the highest scheduling and
concurrency owner. The bootstrap is not a second executor and must not duplicate scheduling logic.

## LangGraph and AI layout

LangGraph and other Python AI projects use the same clean root:

```text
project/
├── README.md
├── readme-chinese.md
├── pyproject.toml
├── .env
├── .env.example
├── settings.py
├── export.py
├── server.py          # only for an API/service runtime
├── manager.py         # only for a background worker runtime
├── langgraph.json     # only when required by the framework
└── package_name/
    ├── config/
    ├── domain/
    ├── platform/
    ├── infra/
    ├── repo/
    ├── service/
    ├── workflow/
    │   ├── state.py
    │   ├── nodes/
    │   ├── routing.py
    │   └── graph.py
    ├── prompts/
    ├── runtime/
    └── tests/
```

Do not omit `export.py` merely because `langgraph.json` can point directly to a package graph. Export
`build_graph`, `run_workflow`, and, when required by the framework, a graph object or factory from the root
`export.py`. Keep graph compilation import-safe and free of network/database connections.

A pure AI library may have only `export.py`. An AI API adds `server.py`. An AI background processor adds
`manager.py`. A combined deployment may have both, while preserving server/worker separation.

## Exceptions and migration

Follow an explicit user requirement or established language/repository/tool contract when it requires a
root-level file or directory that is not in the default allowlist. Keep the exception minimal and document why
the ecosystem or tool cannot use its normal source/package location.

For an existing project, do not move files solely for appearance during an unrelated narrow fix. Apply the
clean-root migration when the user requests it or when the current task already owns the relevant structure,
then preserve import paths, launch commands, packaging, deployment, and data compatibility.
