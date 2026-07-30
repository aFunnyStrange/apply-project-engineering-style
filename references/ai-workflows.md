# AI Workflow Architecture

## Contents

- Activation and framework choice
- Portable core and surface adapters
- Layer and call model
- Graph and manager ownership
- Public exports and runtime construction
- State, checkpoints, and durable facts
- Async execution and dependency contracts
- Models, tools, retrieval, and artifacts
- Testing and operational checks

## Activation and framework choice

Apply this reference to LangGraph and equivalent agent, multi-agent, RAG, LLM orchestration, or durable AI
workflow runtimes. Keep the rules framework-neutral; map framework terms to these responsibilities instead of
letting a framework dictate the whole project structure.

Use a graph or durable workflow when the use case needs branching, cycles, parallel steps, human interruption,
streaming, checkpoint recovery, or explicit multi-step state. Keep a simple model or tool call in an ordinary
service when a graph would only wrap one linear function.

Keep the project root limited to configuration/tool metadata, README files, and thin entrypoints. Put graph
state, nodes, routing, prompts, services, repositories, provider adapters, tests, and scripts inside the named
package. Read [project-layout.md](project-layout.md) for the complete allowlist.

## Portable core and surface adapters

Keep reusable workflow semantics independent from the product surface that invokes them:

```text
framework-neutral goal/task/evidence contracts
  -> domain services and workflow application API
    -> optional durable graph/runtime adapter
      -> Codex Skill, editor rule, MCP, HTTP API, or CLI adapter
```

- Put goal decomposition, evidence models, domain state transitions, and reusable capability contracts in the
  portable core.
- Treat a Codex Skill or editor rule as a thin behavioral adapter that selects and constrains the core; do not
  make prose instructions the only implementation of deterministic domain logic.
- Expose the same stable application API through MCP, HTTP, CLI, or another surface only when that surface is
  actually required. Keep authentication and transport policy in the adapter.
- Use LangGraph or another workflow runtime when branching, persistence, interruption, or resumable state
  justifies it. The runtime is an orchestration adapter around the domain, not the whole domain model.
- Keep task, goal, evidence, artifact, and result contracts serializable and free of framework-specific live
  objects so another surface can reuse them.
- Test the portable core directly, then test each adapter's mapping separately.

## Layer and call model

Use this construction order for an AI-enabled service:

```text
platform/infra
  -> repo
    -> domain services and tool contracts
      -> workflow/graph
        -> export.py
          -> handlers
            -> routers
```

Use this runtime call direction:

```text
router
  -> handler
    -> exported async API
      -> workflow/graph
        -> nodes
          -> domain services, model/tool/retrieval contracts
            -> repositories
              -> infrastructure/platform adapters
```

For a pure AI worker, keep `manager` as the top-level process entry:

```text
manager
  -> exported async API
    -> workflow/graph
      -> nodes
        -> domain services and tool contracts
          -> repositories
            -> infrastructure/platform adapters
```

Treat the arrows above as call direction. Keep imports and dependency construction one-way so lower layers do
not import the graph, export surface, manager, handlers, or routers.

Use these role boundaries:

| Role | Owns | Must not own |
| --- | --- | --- |
| Domain service | Business rules, use cases, durable state transitions | Graph routing or framework state |
| Model/tool/retrieval contract | One replaceable capability required by a consumer | Provider selection or hidden client construction |
| Node/step | Adapt graph state to one service or capability call and return a small state update | Direct route handling or unrelated infrastructure |
| Workflow/graph | One run's steps, branches, joins, interrupts, retries, and resumable control flow | Business source-of-truth storage or process-wide job polling |
| Graph state | Small serializable execution context and intermediate references for one run | Credentials, large artifacts, or authoritative business records |
| Checkpointer | Recoverable snapshots and progress for graph execution | Account, task, billing, or session truth |
| `export.py` | Stable async functions and graph/factory exports | HTTP startup, manager loops, or duplicated workflow logic |
| `manager` | Task claiming and bounded concurrency across multiple workflow runs | Internal node routing or another executor wrapper |

## Graph and manager ownership

Let one graph instance describe the internal lifecycle of one business run. Let a worker `manager` decide which
durable jobs may run and how many graph runs may execute concurrently.

- Do not add an executor above or below `manager` that merely repeats its concurrency responsibility.
- Do not make `manager` choose individual graph nodes or duplicate graph edges in procedural code.
- Do not make graph nodes scan the global task table independently.
- Let `manager` pass a durable task identifier and explicitly constructed dependencies to the exported API.
- Let the graph load required facts through services or repositories and persist business transitions through
  those same boundaries.
- When the service invokes a graph directly for one request, omit `manager`; the service runtime already owns
  that request. Add a manager only for a real background-worker process.
- Bound fan-out inside a graph independently from the manager's graph-run concurrency so their product cannot
  overload external services.

## Public exports and runtime construction

Keep framework construction discoverable and directly testable:

```python
"""Expose the AI workflow without starting its transport runtime."""

from typing import Optional


def build_graph(dependencies: "WorkflowDependencies") -> "CompiledGraph":
    """Build one compiled graph from explicit dependencies."""
    ...


async def run_workflow(
    request: "WorkflowRequest",
    dependencies: "WorkflowDependencies",
    thread_id: Optional[str] = None,
) -> "WorkflowResult":
    """Execute one workflow run through the stable package API."""
    ...
```

- Export a graph object or factory from `export.py` when framework configuration needs a module path.
- Keep `export.py` at the project root for every Python AI application. Do not omit it merely because
  `langgraph.json` or another framework manifest can reference a package module directly.
- Keep import time free of network connections, database access, environment-dependent validation, and
  background tasks.
- Construct repositories, clients, model adapters, checkpointers, and stores in one composition root or
  injectable factory.
- Let handlers and worker managers call exported functions instead of importing internal graph or node modules.
- Permit framework development commands such as graph visualizers, framework servers, test runners, and
  debuggers. They are toolchain entrypoints, not custom application CLIs.
- Keep custom Python application CLI parsing in `export.py` only, unless the user explicitly requests a public
  CLI product surface. Preserve `python export.py` and IDE Console Debugger use.

## State, checkpoints, and durable facts

Separate execution memory from business truth:

| Data | Owner |
| --- | --- |
| Tasks, users, accounts, sessions, permissions, billing, business status | MySQL/Postgres or the project's durable business store |
| Graph position, intermediate values, interrupt/resume data, thread-local conversation context | Graph state and checkpointer |
| Cross-run AI memory or retrieval metadata | Explicit store/repository with documented lifetime and ownership |
| Locks, leases, cooldowns, counters, transient run status | Redis with explicit TTL and loss semantics |
| Prompts, documents, captures, images, audio, large model/tool results | Object/blob storage with references in graph state |
| Search embeddings or vector indexes | Derived index; retain durable source documents and version metadata elsewhere |

- Give every graph run a `thread_id` or equivalent execution identifier. Relate it to the durable task ID, but
  do not use it as the only proof that the business task exists or completed.
- Use an in-memory checkpointer only for tests and local development.
- Choose an async persistent checkpointer when production runs must resume after restart. Its records remain
  workflow infrastructure, even when stored in the same Postgres cluster as business tables.
- Use Redis-backed graph persistence only when its TTL, eviction, and loss behavior match the required recovery
  semantics. Redis loss must not erase business facts.
- Keep state small and serializable. Store artifact identifiers, hashes, versions, and bounded summaries rather
  than raw captures or unbounded conversation history.
- Apply retention and redaction to checkpoints because prompts, model responses, and tool results may contain
  sensitive data.

## Async execution and dependency contracts

- Make exported workflow calls asynchronous.
- Use async graph invocation and streaming APIs. Do not call a synchronous graph or blocking model client from
  an async server handler.
- Make every model, tool, retriever, checkpoint, store, database, HTTP, filesystem, queue, and subprocess
  boundary asynchronous.
- Keep deterministic routing, reducers, schema conversion, and CPU-light validation synchronous when they do
  not perform I/O.
- Define consumer-owned async Protocols for model inference, tools, retrieval, memory, and artifact storage.
  Inject provider adapters instead of importing a specific model or HTTP SDK into nodes.
- Pass stable dependencies through explicit runtime context or node construction. Do not place live clients,
  sessions, repositories, or secret objects in serializable graph state.
- Reuse model and HTTP clients. Apply timeouts, cancellation, bounded retries, rate limits, and concurrency at
  the adapter or capability boundary.
- Make side-effecting nodes idempotent. Persist an idempotency key or durable transition before an operation
  that could be replayed after interruption.
- Separate retryable transport/model failure, invalid model output, business rejection, and permanent tool
  failure. Do not retry every exception through one unbounded graph cycle.
- Require structured outputs at model boundaries when downstream code expects a schema. Validate them before
  updating graph state.

## Models, tools, retrieval, and artifacts

- Use Pydantic v2 models for external requests, responses, configuration, and validated model/tool outputs.
- Prefer `TypedDict` or dataclasses for compact graph state. Do not force Pydantic onto every internal state
  update when validation cost adds no boundary value.
- Follow the Python `Union` and `Optional` convention in graph state, node signatures, runtime context, and
  provider contracts.
- Keep prompts and model selection in a named capability or policy layer. Do not scatter provider/model names
  across nodes.
- Treat tools as narrow application capabilities. Validate arguments, enforce authorization at the tool
  boundary, and return bounded typed results.
- Assume retrieved documents and tool output are untrusted input. Do not allow their text to override system
  policy, authorization, or tool scope.
- Store prompt templates, schema versions, model profile, tool versions, and source references needed to
  reproduce or diagnose an AI result.
- Keep vector databases and embeddings replaceable behind retrieval contracts. Rebuild derived indexes from
  durable, versioned source material.

## Testing and operational checks

Maintain the same three test levels:

1. Unit: test one node, reducer, routing decision, service, prompt renderer, or provider adapter with
   deterministic fakes. Do not require a live model merely to prove control flow.
2. Integration: compile the workflow with a fresh test checkpointer and execute one narrow business path,
   branch, interrupt/resume sequence, or repository interaction.
3. Total/system: execute the real outer API, MCP, export, or worker entry through the graph to the final durable
   business result using controlled model/tool providers or an explicitly authorized live environment.

Also verify:

- async invocation and streaming do not block the event loop
- graph-run and node fan-out concurrency are both bounded
- cancellation closes streams and releases leases/resources
- checkpoint resume does not repeat non-idempotent side effects
- invalid structured model output follows an explicit error path
- business completion is persisted independently from graph completion
- large or sensitive values do not leak into state, checkpoints, logs, or traces
- provider, model, prompt, tool, and artifact versions are observable enough for diagnosis
- a graph can be constructed and exercised without starting routers, the server, or the worker manager
