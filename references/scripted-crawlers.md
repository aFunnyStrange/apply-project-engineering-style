# Script Workflow Code Style

Use for small script entrypoints that compose existing API functions. This reference concerns code organization,
not database design, persistence, retry policy, account eligibility or any particular vendor behavior.

## Keep reusable functions and demos separate

Preserve useful endpoint demos. Add business functions that call the existing request builders, parsers and
public algorithms; do not duplicate protocol assembly in a new manager or replace simple demos with a task
framework. A demo is an editable caller of the reusable functions, not their implementation owner.

Keep browser automation, login orchestration and an independently deployed algorithm service in separate owned
packages when their lifecycles differ. Share explicit inputs or public APIs, not hidden imports of another
application's runtime or configuration. Do not add future transport/service integrations before requested.

## Make call sites readable

Build a request in a named variable, send it, then parse the response where that is the actual flow. Prefer
visible steps over nested lambdas or forwarding callbacks that make debugger stepping confusing. Keep callbacks
when the real framework requires them or construction must wait for a selected execution context. A named
builder plus explicit arguments is appropriate in that case; do not prebuild with stale context merely to
avoid a callback. Do not remove useful asynchronous contracts for cosmetic consistency.

Put one endpoint in a module, or a flat endpoint package when substantial. Keep its method, full URL, headers,
query and body visible together. Apply the same organization to calculated parameters: one independently
portable algorithm package with flat local files and a clear public `__init__.py`. Follow
[client-components.md](client-components.md) for the full contract.

## Expose a readable runtime execution API

Lightweight style does not mean exposing every low-level step to every caller. Encapsulate repeated execution
mechanics in an owned runtime: session/client reuse, execution context, transport invocation, parser invocation,
error propagation, logging context and cleanup where the project actually needs them. Expose a small named
execution function or a runtime object when retained resources justify it. The caller should show the business
sequence without rebuilding this machinery for each step.

Keep the implementation flat and the call chain short: a `runtime.py` can contain the real implementation;
a runtime package is useful only when it has several substantial responsibilities. Do not mandate a class,
context manager, executor/provider hierarchy or separate file for each operation. A public re-export is enough
when no contract adaptation is required.

A readable call shape might be:

```python
request = build_item_request(item_id, cookies)
result = await runtime.execute(request, parser=parse_item)
```

This is illustrative, not a new required interface. Reuse the project's existing equivalent. Named arguments
and named builders/parsers keep behavior inspectable without nested lambdas. Expose runtime execution through
the package's existing public entry, while retaining builders, algorithms and parsers for independent use and
debugging. Avoid parallel implementations of the same request path.

Keep execution encapsulation separate from scheduling: the runtime executes supplied work and owns its declared
resources; the manager decides when, how often and which stages to run. Do not hide timer loops, workflow
selection, new configuration sources or repeated resource construction behind an innocently named execute call.
The public contract should make inputs, return value, ownership and errors clear, and allow caller-supplied
resources without reconstructing or closing them.

## Distinguish runtime responsibilities by ownership

Inspect actual call paths before applying a common name or folder pattern. Useful roles can coexist without
becoming mandatory layers:

- Component runtime: assemble low-level capabilities and own their resource lifetime. Depend directly on
  component implementations, not on the package's aggregate export or upper business modules.
- Business runtime: compose components into the context required by a business operation. Keep business
  choices here rather than adding them to a generic downloader or browser helper.
- Script runtime: manage process startup, logging and shutdown. It should not construct protocol parameters
  or choose the workflow's scheduling policy.

A package public entry may export both the components and their assembled runtime. It must not connect to
external systems, launch applications or create resources during import. Optional heavyweight dependencies
can load at the capability's use boundary; do not use lazy imports to conceal dependency cycles.

Prefer two useful levels of access when both have real callers: a tool accepts an existing resource, and a
convenience entry opens its own resource, calls that same tool, and closes it. The convenience entry is a
substantive lifecycle wrapper, not redundant forwarding. Borrowed resources stay open; owned resources close
on success, exception and cancellation. Keep settings reads in the composition entry rather than in the pure
tool. A data-only transform does not need to become async just because callers perform I/O.

Choose runtime lifetime from the actual sequence of operations. Reuse a context across related calls when
continuity is required; do not rebuild it per request just because a helper is named `open_runtime`. Conversely,
do not share mutable contexts that require isolation. Retain the project's actual lifetime contract rather
than making every convenience entry permanent or every operation one-shot.

A business function should expose business inputs, injected resources and necessary outputs. It need not
expose each internal component or wrap them in a second generic object. Select a function, context manager
or small object based on real retained state and cleanup, not naming symmetry. Existing low-level encapsulation
is valuable when it leaves the upper call site short and the execution path easy to trace.

## Extract conventions from evidence, not filenames

Before generalizing a project's style, trace a public entry through one builder, algorithm, transport/runtime,
parser and business caller. Compare the standalone demo with the long-lived caller, including ownership and
cleanup. Distinguish a working boundary from incidental duplication or an older implementation that still
needs improvement. Do not prescribe every observed helper, callback or runtime construction pattern.

In particular, a file called `runtime.py` is not automatically the same abstraction in every package; an
`export.py` is not a requirement to duplicate `__init__.py`; and existing nested calls do not justify a
forwarding layer. State the transferable responsibility and verify it through imports and actual callers.

## Keep entrypoints and configuration small

A script `manager.py` can consist of an editable workflow selector and one main function with direct branches
calling existing functions. Do not add a CLI parser, registry, executor layer or strategy classes merely to
replace a few branches. Extract a helper only when it owns meaningful behavior or materially improves readability.

Keep each editable value in one clear owner. Application settings hold application choices; platform profiles
hold their actual integration configuration. Avoid duplicate root constants and unnecessary configuration
loaders. A local account list of dictionaries in its own file may be sufficient when requested; do not turn it
into a generic account framework or duplicate shared headers per account. Add modes only for existing supported
use cases, not hypothetical future replacements of an algorithm or service.

## Separate worker execution from manager scheduling

Workers expose one round of business execution. The manager owns repeated invocation, scan timing, concurrency
and dependency-aware shutdown. Do not place a timer/resubmission loop inside a worker merely to support an
aggregate entrypoint. Preserve standalone worker entrypoints as ordinary callers of the same functions.

Keep task ownership and cleanup visible in the manager. Reuse owned clients across repeated calls where their
contracts allow it; do not reconstruct resources simply because a new round started. A small scheduling helper
is justified if it performs real coordination, but a wrapper that only renames and forwards calls is not.

## Organize logs without hiding progress

Keep manager scheduling messages and each worker's detailed messages in separate files when requested. Reuse
that worker's file across rounds. Keep useful collection progress visible in the terminal; verbose rendering
logs can remain file-only according to the user's preference. Include enough stage/item context to identify
failures and results without logging credentials.

For concurrent workers in one process, use context-aware routing or an equivalent explicit logger boundary.
Do not repeatedly replace global logging configuration from individual async tasks. Logging helpers should own
formatting, routing and handler cleanup, not scheduling or business policy.

## Verify the style change

Check both structure and a readable call path. For independent algorithms, copy a package outside the parent
project and test its import and known vectors. For orchestration and logging, use substituted workers to check
call ownership, cancellation and log separation without running live collection. Keep old compatibility modules
only when required by actual callers; remove them when the user explicitly requests a clean migration.
