# M4 Real OCI Fixture Run Evidence — 2026-07-16

## Scope and authorization

This record captures the single real OCI fixture run explicitly authorized on
2026-07-16. It is an execution-environment probe only. It did not invoke the
ForgeFlow service, create a GitHub mutation, inject a credential, or retain
raw container output.

## Registered identity checks

| Item | Observed value | Result |
| --- | --- | --- |
| Image reference | `ghcr.io/soulbooyy/forgeflow-m4-fixture-runner@sha256:81b691e3b5d43b2f4e717eaeef63437705addd115aee32917efd5d7387807f28` | exact registered digest |
| Local image ID | `sha256:81b691e3b5d43b2f4e717eaeef63437705addd115aee32917efd5d7387807f28` | exact registered digest |
| Image working directory | `/workspace` | matches registered command working directory |
| Image runtime user | `fixture` | run forced to registered UID `100:100` |
| Registered command identity | `fixture-test-runner-v1` | selected exactly once |

The fixture registration pins base revision
`97c8220cd713ebf61124ac2de2f3eadc6e4dc222`. No independent local fixture
checkout was present at runtime, so this run cannot independently attest that
the filesystem embedded in the registered image corresponds to that revision.
It must therefore not be treated as the full base-revision-pinned M4 external
evaluation.

## Runtime controls

The container was started once with these effective controls:

- immutable registered image digest;
- no network (`--network none`);
- read-only container root filesystem;
- runtime UID/GID `100:100`;
- working directory `/workspace`;
- an isolated writable `/tmp` tmpfs only;
- no environment-variable injection, credential injection, artifact-store
  mount, or host workspace mount;
- `120` second supervising timeout; and
- transient stdout/stderr capture, bounded against the registered `65536` byte
  maximum and then discarded.

## Result

| Field | Observed value |
| --- | --- |
| Run timestamp (UTC) | `2026-07-16T06:01:54Z` |
| Container exit code | `1` |
| Timed out | `false` |
| Elapsed time | `1547 ms` |
| Captured output bytes | `1008` |
| Within registered output limit | `true` |
| Output SHA-256 | `66473c1ba197e6ad99b861d98ad23c40a8902f85e4b59dbe36c6ed59b723ac4e` |

The run **failed**. Raw output is intentionally not included in this record.
The authorization covered exactly one real OCI run, so no retry, altered
runtime configuration, image pull, or GitHub operation was performed.

## Consequence

This evidence establishes that the locally available registered image can be
started under the stated isolation controls and that its selected fixture
command returned a non-zero result. It does not close M4 external evaluation
or milestone closure. A later, separately authorized investigation should use
an independently verified fixture checkout at the registered base revision and
preserve only redacted diagnostic evidence before any further real run.

## Reconciliation

### Final classification of exit code `1`

The exit code is **not established as an expected fixture/test failure**. Raw
output was deliberately discarded, so this record cannot identify a particular
unittest diagnostic. It is also not a result from the registered fixture
repository: the runner's controlled-build record states that its build context
intentionally contains no fixture-repository source, while this probe supplied
no temporary workspace mount. The result is therefore classified as a
**probe workspace-provisioning / fixture-image alignment failure**, not a
fixture-repository behavioral result.

The exact allowlisted command identity was invoked by Docker, which is a
command-execution fact. It was not invoked through ForgeFlow's evaluated
`ActionIntent` / `CommandIntent` / `PolicyDecisionRecord` tuple, so it creates
no governed `ExecutionAttempt` and must not be recorded as a M4
`command_failed` terminal fact.

### Facts kept separate

| Domain | Reconciled fact |
| --- | --- |
| Sandbox capability | The registered image started with the recorded digest, network, root-filesystem, UID, credential, and mount exclusions. The fixed-revision-workspace condition was not supplied or proven. |
| Command execution | Docker invoked the exact registered command once and it returned `1` within the output and time bounds. |
| Fixture behavior | Not evaluated: no independently verified checkout at `97c8220cd713ebf61124ac2de2f3eadc6e4dc222` was mounted. |
| Policy decision | Not evaluated: this was an environment probe, not a ForgeFlow policy evaluation. |

Accordingly, the result is neither `sandbox_unavailable` nor
`policy_blocked`, and it is not a governed `command_failed` fact. It also does
not establish a successful allowed execution path.

### Original-probe follow-up

The minimal correction was not a
policy, command, image, or architecture change: provide a temporary local
checkout whose Git object is verified to equal the registered base SHA, mount
only that checkout at `/workspace`, and run the same single command under the
same controls. The runner documentation specifies this workspace arrangement.

That correction was completed later on 2026-07-16 after GitHub CLI access was
made available. Its resulting expected fixture negative-test failure and
controls are recorded in [the controlled re-probe evidence](real-oci-fixture-reprobe-2026-07-16.md).
