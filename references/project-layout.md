# Clean Project Root Layout

## Contents

- Root-directory rule
- Cross-language rule
- Python root files
- Python application layout decision
- Python library and framework roots
- Package ownership
- Python service layout
- Python worker layout
- LangGraph and AI layout
- Exceptions and migration

## Root-directory rule

Keep the project root as a small allowlist containing only:

1. project configuration and tool metadata;
2. user-facing README files;
3. thin executable, configuration, and export entrypoints;
4. ecosystem-standard source, package, test, documentation, example, and migration directories.

Put all implementation details inside the deliberately selected owned package, source tree, layer directory,
crate, module, or workspace location. Put tests and other project resources in the ecosystem's conventional
owned directories.
Do not leave business modules, clients, repositories, services, handlers, routers, graph nodes, prompts,
utility modules, test logic, migrations, or ad hoc debug programs as arbitrary loose files in the root.

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
- `.env` is optional: when used, keep it ignored and never commit secrets.
- `.env.example` documents the redacted variable contract when environment configuration is used.
- `settings.py` is the authoritative editable application configuration surface. Keep reusable validation
  models and parsing helpers in an owned module, but do not reduce the root file to a forwarding-only shim.
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

## Python application layout decision

Distinguish three boundaries before moving files:

1. the application directory used as the working and deployment root;
2. the Python import namespaces used by source code;
3. the built distribution installed or published for execution.

Use a named implementation package when the code is intended to be imported as one namespace, coexist with
other packages, or behave like a reusable library. Use explicit layer packages directly under the application
directory when the user or repository defines that directory as the deployment unit and a wrapper namespace
would add no ownership or compatibility value.

A flat application can use:

```text
project/
├── .env
├── .env.example
├── pyproject.toml
├── settings.py
├── export.py
├── manager.py
├── config/
├── domain/
├── platforms/
├── infrastructure/
├── repositories/
├── services/
├── runtime/
└── tests/
```

Do not mix both layouts accidentally or leave an empty wrapper containing only imports and caches. In a flat
Python layout, avoid a root import package whose name shadows the standard library. A dependency list in
`pyproject.toml` does not prove packaging: declare a build backend, configure module/package discovery and
exclusions, build from a clean temporary copy, inspect artifact members, and import the public surface from the
built artifact.

## Python library and framework roots

A reusable Python library or framework is not automatically an application project. Its root normally contains
packaging/tool metadata, documentation, CI configuration, and its named package:

```text
project/
├── README.md
├── pyproject.toml
├── lockfile
├── .gitignore
├── package_name/
└── tests/
```

Expose the supported API through `package_name/__init__.py`, `package_name/api.py`, or deliberate typed public
modules. Keep optional command entrypoints under the package and declare them in `pyproject.toml`. Do not create
root `settings.py`, `export.py`, `server.py`, or `manager.py` merely to imitate an application built on the
framework. Generated application projects may use those files when their concrete runtimes require them.

Treat package generators and templates as maintained source under the package or an ecosystem-standard asset
location. Tests should generate into temporary directories; generated demos, logs, build output, and editable
install metadata do not belong in the repository root.

## Python package ownership

For the named-package model, move Python implementation into the named package:

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

Create only the directories the project needs. The rule is about explicit ownership, not forcing every layer
or a wrapper namespace into every project or language. Apply the same dependency rules to flat layer packages.

- Put reusable and business implementation in the package.
- Put unit, integration, and total/system tests under the package's `tests/` or the ecosystem-standard root
  `tests/` tree. Follow the existing tool and repository contract; do not scatter test modules across the root.
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

## Small-service operational entrypoints

For independently deployed services, root start/stop/clean scripts and a thin request smoke or demo client
are intentional entrypoints. Keep them with their service; substantial implementation and test suites still
belong in owned directories. See [service-delivery.md](service-delivery.md). A Python smoke client does not
turn a non-Python service into a Python application requiring settings/export files.

For a source-imported package, an explicit public API and encapsulated implementation do not require a new
`pyproject.toml`. Distribution build checks apply when distribution is part of the delivery contract.
Document meaningful nested packages as subsystems, including their own state and resource ownership; see
[embedded-workflows.md](embedded-workflows.md).
