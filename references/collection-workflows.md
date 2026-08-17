# Collection Workflow Boundaries

## Contents

- Separate discovery from acquisition
- Fan out with resource-scoped bounds
- Isolate resource-pool ownership
- Preserve observations and unique results
- Make persistence explicit
- Verify the complete flow

## Separate discovery from acquisition

Model discovery and acquisition as distinct protocol operations. A bootstrap, manifest, index, search, or
listing response may provide identifiers and session metadata without containing the final business records.
Parse the verified current schema first and retain older shapes only as explicit compatibility fallbacks.

Unless the product contract defines sampling, request every distinct item returned by one bounded discovery
operation. Do not silently rotate through one item per run. Use configured fallback identifiers only when
discovery yields none, not instead of valid discovered work. Remove unrelated legacy operations after proving
they are not required by the current protocol.

Represent each phase honestly in the run result:

- discovered identifiers;
- one acquisition result per attempted identifier, including failures;
- normalized observations associated with their source;
- deduplicated business records for downstream consumers;
- duplicate and failure counts.

## Fan out with resource-scoped bounds

Run independent external I/O concurrently, but scope the limit to the actual constrained resource such as a
session, credential, account, device, proxy, tenant, or upstream quota. A single global limit can conceal
unfairness or still let one resource exceed its permitted concurrency.

For a bounded list, use the language's gather/join primitive behind a bounded semaphore or equivalent. Preserve
discovery order in returned per-item results when the contract requires it. Propagate cancellation, isolate
ordinary per-item failures when partial completion is valid, and ensure one failed item does not prevent later
items from being attempted.

Do not create an unbounded task list from an unbounded scan. Page or stream discovery into bounded batches or a
bounded queue.

## Isolate resource-pool ownership

Hide the concrete source of accounts, devices, sessions, credentials, or other reusable execution resources
behind a repository contract. Let a pool service own eligibility, expiry, deterministic selection, refresh,
and rotation. Collection and protocol services consume stable resource capabilities; they must not know storage
keys, connection strings, or concrete client construction.

Keep machine-specific connection facts centralized in application settings. Preserve separately editable
fields when the operational contract requires them instead of collapsing them into a convenient but opaque
aggregate value. Construct concrete clients once in the composition root and reveal secrets only at that
adapter boundary.

## Preserve observations and unique results

The same business record may appear under several discovery items, pages, queries, partitions, or sources.
Deduplicate across the complete run using a stable domain identity, not only inside each individual response.

Retain source-level observations when they are needed for diagnosis or attribution, and expose unique run-level
records separately. Report observed, unique, duplicate, and failed counts so deduplication cannot be mistaken
for missing collection.

## Make persistence explicit

Do not add local files, database writes, screenshots, captures, or object-store artifacts solely because data
was produced. Returning the normalized and deduplicated run result is a valid final boundary. When persistence
is required, inject a repository or object-store contract and define identity, idempotency, retention, replay,
and failure semantics.

Keep discovery metadata distinct from acquired business records. Name, model, and log them separately.

Generated outputs, local secrets, logs, caches, and captures must not enter built distributions unless they are
intentional product assets. Version-control ignore rules are not packaging rules; configure artifact discovery
and inspect the actual built member list.

## Verify the complete flow

Cover these facts at the appropriate test levels:

1. the current discovery schema and every retained compatibility fallback;
2. every discovered item is attempted exactly once after stable identifier deduplication;
3. fallback work is used only when discovery is empty;
4. concurrency exceeds one when possible but never exceeds its per-resource bound;
5. one ordinary item failure does not cancel successful peers, while external cancellation propagates;
6. cross-source duplicates remain visible as observations and appear once in unique output;
7. resource repositories and pools remain replaceable and concrete clients stay in the composition root;
8. no persistence side effect occurs when persistence is outside the contract;
9. built artifacts exclude local configuration, tests when intended, caches, logs, and runtime outputs.
