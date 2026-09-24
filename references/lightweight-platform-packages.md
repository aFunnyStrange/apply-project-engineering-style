# Lightweight Platform Packages

Use for API clients and self-contained integrations embedded in a larger service. Prefer direct
functions and visible business steps over a general framework. These are supported shapes, not a required
migration of other platforms or a new universal folder template.

## Distinguish clients from servers first

Highly encapsulated concurrent servers can use `handlers -> services -> repositories -> infra` to organize
use cases, persistence and infrastructure. That server design remains valid. Client packages and protocol
subpackages organize around inspectable upstream requests. Concurrency or being embedded in a server does
not require that server's full layer chain; surrounding business code may own state independently.

## Integrate with minimal intrusion

When extending an existing host, keep its server structure and unrelated code intact. Encapsulate client
logic as a package with a small public API. A runtime may expose reusable connections, session resources and
shutdown when those capabilities are actually needed; it need not become a generic service framework.
Adapt the existing route or worker at the smallest necessary seam. Do not move host handlers, services,
repositories or infrastructure merely because the client uses a lighter structure. Large-scale host
reorganization requires an explicit refactoring request, not an inference from ordinary feature development.

## Separate protocol from business without adding relays

A small protocol client and an integration's protocol subpackage are the same level of abstraction. Keep
request construction, signing, upstream calls and parsing there. Explicit inputs carry session and version
options; outputs describe actual text, image, video or mixed results supported by the real protocol. Keep
legacy task labels, account selection/rotation, billing, persistence and public response compatibility in the
surrounding platform business code. Do not invent wire formats for hypothetical future input types.

A useful embedded shape is:

```text
host routers / worker
    -> vendor/export.py
        -> business/             # Platform state, retries, settlement and storage
        -> protocol/
            api/                # One endpoint per file or folder, plus export.py
            parser/             # Response parsing, independent of HTTP scheduling
            algorithms/         # Public vendor signing/device functions
                internal/       # Complex private algorithm implementation when needed
            platforms/          # Small standard crypto/transport helpers, when useful
```

Treat the tree as an example. Keep settings, exports and useful demos easy to find; group multiple related
business files by responsibility when a flat directory becomes hard to scan. Do not create empty folders or
one-file wrapper packages merely to match the picture. A platform with several files in a host layer should
have one folder there, rather than many parallel platform-prefixed files.

## Borrow host resources and share configuration explicitly

The host normally supplies infrastructure. Accept the actual SQL/Redis connection or pool, HTTP session or
storage client; do not introduce another infra directory or provider merely to forward its methods. Runtime
is a small optional owner of reusable resources, not an obligatory framework. Track borrowed versus owned
resources: package shutdown closes only its own, and explicit injection prevents fallback construction.
Reuse does not make a connection safe across threads or async loops; retain the real driver's constraints.

Keep package `settings.py` complete for its own configuration. For shared values, a direct alias/import or
small mapping to the host settings is useful and allowed. In a host-free standalone mode, use local settings
and put host mapping in the caller or an explicit profile. If independent execution is only promised inside
the repository, document that dependency rather than claiming portability. Do not silently catch broken host
configuration and connect to a different database. Keep one declared precedence: explicit injected resource
first; configuration selects construction only when no resource was supplied. A caller override can replace
local defaults; host-shared fields should have a documented source. No need for a generic config-merging engine.

## Make endpoint code inspectable

Read [client-components.md](client-components.md) for the full request/algorithm/parser contract and a
complete fictional example. Endpoint modules expose the method, literal full URL, headers, query, body and
calculated field inputs together. Do not introduce base-URL/path assembly, anonymous request tuples or
forwarding-only endpoint files. Ordinary dictionaries belong beside the request; computed business fields
belong in independently callable algorithms. Standard primitives and transport belong in vendor-neutral
platform capabilities. Parsers accept responses independently of network clients and have explicit exports.

Keep meaningful device/session/version facts and per-request encryption material paired with their
responses. A shared header group may be factored when genuinely reused, but endpoint-specific fields and
its application must remain visible. Use relative imports and the existing native Request type when useful.

## Remove abstraction that adds no behavior

If a method only imports and awaits a function with the same arguments, call that function directly or put
its substantive implementation on the owning object. Re-exporting a callable is sufficient for a public API.
Keep a wrapper when it converts a contract, enforces a real invariant, manages resources or maintains required
compatibility. Do not add runtime, provider, factory, repository or callback objects for naming symmetry.
A runtime is useful when it actually owns reusable connections, loop affinity or shutdown; those invariants
must survive simplification. Do not replace them with per-call clients or leaked background tasks.

Use concrete response/client types instead of `Any` when known. Use annotation-only imports and a small
callable contract for genuine injection seams. Do not add keyword-only separators or DebugSettings just as
ceremony; retain argument restrictions that serve an actual API contract. Match the deployed Python version.
Use Chinese comments/docstrings and human-facing errors for projects following this convention; keep field
names, protocol values and established external error identifiers intact.

Package-internal imports should be relative. Host code imports the package's public export; internal code
must not depend on host routers or on the host prefix merely to import its own sibling. Inject an existing
host response handler instead of importing the host's concrete model implementation into a reusable package.
Shared classification/serialization can coexist with platform billing and retry decisions; they own different
facts. Do not claim that wrapping data in a response class eliminates settlement decisions.

## Give scheduling and state one owner

When the host worker already controls scan cadence, each platform callback performs one polling attempt.
Do not add another next-poll cache, sleep loop or interval parameter inside that callback unless independently
required. Use the host's supplied poll limit in that mode; an image workflow that polls within one request can
retain its own limit. If standalone settings remain for another mode, document where they do and do not apply.

Account rotation belongs to the platform when eligibility, retry timing and submission evidence differ.
Preserve attempt identifiers, accepted-task continuation and settlement idempotency while simplifying calls.
Successful recovery may clear only the same operation's accounting-unknown marker, not unrelated risk states.
Shared SQL alone does not guarantee cross-process settlement: verify shared Redis DB/namespace, operation
identity and retained receipts where the implementation uses them. Timing, costs and schemas are project
contracts, not defaults to copy from a reference.

## Debug and verify the real flow

Algorithms and parsers may have small directly runnable mains with editable inputs or an external sample
path derived from `Path(__file__)`. No developer-machine paths, CLI framework or separate debug configuration
is needed for that purpose. Keep raw archives intact when normalizing display output. A protocol demo tests
upload/chat or parsing; use the actual server route for full host behavior rather than duplicating orchestration.
Keep owned tests and ignored demos/logs inside the platform package when that is the project convention.

Before and after refactoring, trace one request, one retry and one polling completion through real callers.
Verify account/resource release, persistence destination, public response compatibility and failure recovery.
Update imports, docs and ignore rules with moves; remove obsolete forwarding modules and stale entrypoints.
Do not modify shared implementations the user has frozen, unrelated platforms or live data for structural
cleanup. A shorter tree is useful only when the real call chain is easier to read and behavior is preserved.
