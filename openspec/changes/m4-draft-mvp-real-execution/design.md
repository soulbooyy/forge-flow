# M4 Draft-MVP Real Execution Design

Phase 1 is pure: it defines a new mutation-scoped PDR type and an adapter
request that accepts only scalar, verified lineage references. It does not
import a v1 materialization/eligibility PDR type, payload handle, bytes, or a
simulation identity.

Phase 2 adds a concrete local Docker harness only after its local-run gate is
accepted. It mounts a separately verified fixture snapshot read-only, uses the
exact registered image/profile, has no network or credentials, uses an empty
environment and temporary output, and records bounded redacted facts only.

Phase 3 adds the sole GitHub adapter only after its fixture-mutation gate is
accepted. It receives an opaque runtime credential and can create at most one
branch, one commit, and one Draft PR for one idempotency key. Any ambiguity has
zero automatic retries. Phase 4 executes the acceptance matrix, then performs
the registered reset and keeps a redacted audit record.

Neither external gate is implied by completion of prior phases.
