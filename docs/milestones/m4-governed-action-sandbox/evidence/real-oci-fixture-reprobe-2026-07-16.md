# M4 Controlled OCI Fixture Re-probe Evidence — 2026-07-16

## Purpose

This is the single controlled re-probe that reconciles the earlier OCI probe's
missing-workspace condition. It uses the same registered image and exact
allowlisted command, but supplies a temporary fixture checkout verified before
container start as base revision
`97c8220cd713ebf61124ac2de2f3eadc6e4dc222`.

It does not invoke the ForgeFlow service or persist a PolicyDecisionRecord or
ExecutionAttempt. It records a controlled fixture-runtime fact, not a new
governed execution terminal. It creates no GitHub mutation.

## Preconditions and controls

| Item | Observed result |
| --- | --- |
| Fixture repository | `soulbooyy/forgeflow-m4-fixture` (private; authenticated read only) |
| Verified checkout revision | `97c8220cd713ebf61124ac2de2f3eadc6e4dc222` |
| Worktree state before run | clean |
| Image digest | `sha256:81b691e3b5d43b2f4e717eaeef63437705addd115aee32917efd5d7387807f28` |
| Command identity | `fixture-test-runner-v1` |
| Workspace mount | temporary verified checkout mounted read-only at `/workspace` |
| Network | disabled |
| Root filesystem | read-only |
| Runtime UID/GID | `100:100` |
| Credentials and environment | none injected into the container |
| Other host or artifact mounts | none |
| Timeout / output limit | 120 seconds / 65536 bytes |

The temporary checkout was removed immediately after the run. No raw command
output, source payload, credential, or workspace path is retained here.

## Result

| Field | Observed value |
| --- | --- |
| Run timestamp (UTC) | `2026-07-16T06:22:02Z` |
| Container exit code | `1` |
| Timed out | `false` |
| Elapsed time | `1455 ms` |
| Captured output bytes | `513` |
| Within registered output limit | `true` |
| Output SHA-256 | `60338d75df15e058d1496d11de354903d15f30b45250ab92b132994956711f43` |
| Temporary workspace cleanup | completed |

## Reconciled semantics

The non-zero result is an **expected fixture negative-test failure**. A
transient, read-only semantic check of the same registered base revision
established both that `calculator.add` uses subtraction and that the fixture
test asserts an addition result of `5`. The registered Issue is correspondingly
"Fix calculator addition bug." The re-probe therefore validates the failure
path of the exact allowlisted command against the fixed pre-fix fixture.

This result is a command-execution and fixture-behavior fact. It is not
`sandbox_unavailable`, `policy_blocked`, or a governed `command_failed` fact:
no ForgeFlow PolicyDecisionRecord or ExecutionAttempt was created for this
manual controlled probe. The earlier probe remains separately classified as a
missing-workspace alignment failure in
[the original probe evidence](real-oci-fixture-run-2026-07-16.md).

## Closure effect

No further OCI re-probe is needed to classify `exit=1`; the controlled negative
fixture path is reconciled. Canonical M4 implementation and deterministic
contract/policy acceptance remain complete. Full external M4 end-to-end closure
is still not claimed: the registered positive path would require its separate
governed evaluation and, if it reaches mutation, the fixture reset/audit
procedure. No such external mutation is authorized or performed by this
record.
