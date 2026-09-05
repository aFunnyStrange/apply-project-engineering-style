# Small Service Delivery

Prefer an independently usable service directory when the service is deployed separately. Keep its operational
scripts at that directory's root and let them operate from their own location. A thin root `test.py` or `demo.py`
may contain an editable request example and assertions; substantial suites and reusable client logic belong in
owned test/source directories. This is a supported layout, not a reason to migrate every project to shell scripts.

Separate source debugging from runtime distribution: use dependency source when a bug requires tracing or patches,
then deliver owned implementation, pinned dependencies, required assets and traceable patches. Do not ship a whole
framework checkout merely because the initial demo lived there. A patched dependency remains part of the delivery
contract and cannot silently become an unpatched public release.

Define the lifecycle surface:

- start: validate prerequisites/assets, build only when inputs or required outputs changed, start and track the
  owned process, report bounded readiness; never use a partial cache as a valid build;
- foreground run, if present: execute existing artifacts directly for debugging or a process manager;
- stop: verify process and project identity, stop with bounded escalation, support repeated invocation;
- clean: stop the owned service if needed, remove an explicit project-local output list, preserve inputs and
  business state, and avoid shared caches or paths outside the service;
- smoke: configurable endpoint, timeout, real request/response contract, assertions and nonzero failure exit.

Do not use `.gitignore` as a packaging or cleanup policy. Verify the actual archive/distribution from a clean
copy and distinguish online source bootstrap from offline delivery. Check the target OS/runtime/native backend
when those define compatibility; health alone does not prove a complete business call works.

For unidbg-specific reproduction and assets, use `develop-unidbg-service` only if active and available; this reference is sufficient
for generic service delivery and does not require that Skill to be installed.
