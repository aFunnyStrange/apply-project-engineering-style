# Capability Evolution and Workflow Outcomes

Apply these rules to the capability currently being changed. They do not make every remote dependency optional,
change authoritative account storage, enable a rollout, or authorize account deletion.

## Baseline and enhancement contracts

Establish the smallest existing supported input and working baseline first. Keep enhancement fields distinct
from baseline required fields. Do not fabricate an absent identifier from a different field simply to pass validation.

Evaluate an enhancement in this order: enabled configuration, supported capability/version, request-local
prerequisites, circuit state, then external invocation. Disabled code must perform no enhancement I/O and must
not reject an old record for missing enhancement-only fields. Keep its actual implementation available for later
activation; a production switch is not replaced by a success-only mock.

| Observation | Behavior for a designated optional enhancement |
| --- | --- |
| Disabled or unsupported | Skip; retain baseline behavior |
| Local record lacks optional fields | Skip for that record; do not mark the whole platform broken |
| Transient network/HTTP failure | Use the documented fallback, report bounded diagnostic context |
| Explicit authoritative business denial | Preserve the denial; do not relabel it as an availability failure |
| Confirmed response contract mismatch | Apply configured disable/circuit policy at its documented scope |
| Skipped check | Represent unchecked/unavailable separately from a successful authoritative check |

Define circuit scope (request, process, deployment), reset/recovery path and alert ownership. A process variable
is not a distributed global switch. Choose recovery behavior from the current capability contract; do not
inherit a disable-until-restart policy from another integration.
Avoid broad substring matches that can mistake ordinary response content for a contract error.
Version ranges must compare parsed numeric components when their meaning is a range; do not use a `7.*` prefix
when the contract means major version >= 7, or lexical ordering that puts 10 before 7.

## Protocol versus business orchestration

Platform adapters own request serialization, version/identity profiles, signing, transport and response semantics.
Build one coherent request context so URL, timestamp, body, headers and device identity agree across signing and sending.
Services compose stable capabilities into business stages. Factor shared stages where their contracts match;
separate genuinely different use cases without creating a Cartesian product of versions, features and task types.
Keep configuration and dispatch decisions discoverable. Debug entrypoints call the same exported implementation.

## Typed outcomes before retry and state changes

Distinguish normal content, upstream busy, temporary account restriction, verified ban, insufficient quota,
transport failure, protocol failure and unknown settlement. A generic text response or busy message alone does
not prove an account is banned. Do not delete an account, overwrite uncertain accounting or release a business
reservation on the basis of a generic parser exception.

Reuse the existing retry/rotation owner. Keep a stable logical request identity and a distinct attempt identity;
preserve existing ID conventions and storage limits. Persist a failed attempt before rotating when the workflow
requires an attempt ledger; stop rotation if that handoff fails. Bound retries and exclude already used resources
within a run. Honor cancellation and avoid nested retry loops that multiply attempts. Do not replay a submitted
non-idempotent generation solely because the result is unknown; reconcile its existing operation first.

## Stream completion and business completion

Connection closure, an SSE complete event, business task completion, artifact durability and settlement are
different facts. Use authoritative task/media state and continuation information to decide whether to poll again.
Keep reservations while work is still pending. Settle once against confirmed final output, preserving unknown
state for reconciliation when evidence is insufficient. Do not bill the requested type/count when the actual
returned outcome differs. Apply only the pricing and storage rules specified by the current project.

Keep one owner for logging/alert emission across parser, service and route layers. Preserve attempt/stage/cause
context without emitting the same alert again at every boundary. Historical logs may inform a regression fixture,
but redact identifiers and never copy live account records into a Skill.

## Focused behavioral checks

Cover an old baseline record, disabled enhancement with zero calls, complete enhancement success, local missing
fields, transient fallback, authoritative denial, contract failure and declared recovery. For streaming/retry
changes also cover pending continuation, final settlement once, cancellation, attempt persistence failure and
no duplicate alert. Run only cases relevant to the changed behavior; do not add an unrelated test framework.
