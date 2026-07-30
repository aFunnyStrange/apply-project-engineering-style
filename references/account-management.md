# Account Management

## Contents

- Activation rule
- Responsibility boundaries
- Durable and ephemeral data
- Lease lifecycle
- Rate and risk policies
- Worker contract
- Testing

## Activation rule

Add this subsystem only when both conditions hold:

1. The project depends on a reusable account or session pool.
2. The user explicitly requests account locking, leasing, cooldown, risk state, or rate limiting.

Do not introduce Redis account coordination for a single-account script or merely because another project has
it.

## Responsibility boundaries

Use three independent roles:

| Role | Responsibility |
| --- | --- |
| Account repository | Read and update real account/session facts in MySQL or Postgres |
| Redis account coordinator | Own TTL locks, lease tokens, cooldown, risk markers, and rate state |
| Account manager/service | Select accounts, coordinate leases, expose a worker-facing account API, and hide storage details |

Use this call direction:

```text
worker -> account manager -> account repository
                          -> Redis account coordinator
```

The worker requests an account, performs the business operation, and reports the outcome. It must not construct
Redis keys, acquire or release locks, update rate counters, calculate cooldowns, or know the lease token.

Keep account selection and locking out of generic task schedulers unless the scheduler itself is the explicit
account manager.

## Durable and ephemeral data

Store real facts in MySQL/Postgres:

- account identity and pool membership
- enabled/disabled state
- cookies, tokens, device/session identifiers, and refresh metadata
- account capabilities and persistent business metadata
- durable invalidation or manual disable reasons

Protect sensitive session fields using the project's secret-management and encryption requirements. Never put
credentials or full session payloads in Redis merely to simplify Worker access.

Store only ephemeral coordination state in Redis:

- ownership lock with TTL
- cooldown marker with TTL
- temporary risk marker with TTL
- request counters or rate-window state with expiry
- optional lease heartbeat/renewal state

Redis loss may temporarily reduce coordination quality, but it must not destroy the real account pool or its
session facts. A durable account disable or session replacement must be written to the relational database.

## Lease lifecycle

Implement acquisition as one Account Manager operation:

1. Read eligible accounts from the repository.
2. Exclude accounts with active cooldown or risk state.
3. Atomically acquire one Redis lock using a unique lease token and TTL.
4. Return only the account/session context needed by the Worker.
5. Release through the Account Manager after success, failure, or cancellation.

Use an async context manager or the language's equivalent so cleanup runs on exceptions:

```python
async with account_manager.lease() as account:
    if account is None:
        return retry_result
    await execute_business_request(account)
```

Enforce these lock rules:

- Acquire with an atomic create-if-absent plus TTL operation such as Redis `SET key token NX EX ttl`.
- Release only when the stored token matches the lease token. Use an atomic compare-and-delete script or
  equivalent; do not use an unsafe independent `GET` followed by `DEL`.
- Use a bounded acquisition timeout and honor cancellation. Do not wait forever when all accounts are busy.
- Renew the lease only when a task may validly exceed its TTL. Stop renewal before release and ensure a stale
  owner cannot release a newer lease.
- Scope keys by project, pool, and account identity.
- Treat expiry as crash recovery, not as the normal release path.

## Rate and risk policies

Require the current user or project to define:

- lock TTL and optional renewal interval
- maximum account acquisition wait
- request-rate window, quota, and burst behavior
- per-request delay and optional jitter
- cooldown duration and triggering outcomes
- risk duration and persistent-disable threshold
- selection policy when several accounts are eligible

Do not copy numeric values, request counts, delays, jitter, or cooldown durations from `lzh_tb` or another
reference project. If the user has not defined a rate policy, request the missing policy or leave rate limiting
disabled; do not invent operational numbers.

Let Workers report normalized outcomes such as success, retryable failure, authentication failure, or risk
signal. Let the Account Manager apply the configured cooldown/risk policy. Keep the policy out of individual
spiders and Workers.

## Worker contract

Expose a small interface that supports:

- acquire/lease an eligible account
- report the operation outcome
- optionally mark a durable account invalid through the Account Manager

Do not expose Redis clients, key builders, lease tokens, counters, or cooldown calculations to Workers.

Log pool, account identifier, lease result, and normalized outcome when useful. Never log cookies, tokens,
passwords, proxy credentials, raw session material, or the lock token.

## Testing

Add tests at all three levels:

1. Unit: use a fake repository and fake coordinator to verify selection, bounded waiting, cleanup, and outcome
   policy for one account flow.
2. Integration: use test MySQL/Postgres and Redis to verify TTL acquisition, contention, atomic token-safe
   release, expiry recovery, renewal, and configured rate/cooldown behavior.
3. Total/system: run at least two concurrent Workers against the full account flow and verify that only one owns
   an account at a time, real session data remains durable, and execution recovers after failure.

Include a test proving that changing user-supplied rate configuration changes behavior without code changes.
