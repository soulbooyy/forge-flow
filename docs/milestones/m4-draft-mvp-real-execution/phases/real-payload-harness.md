# Real Payload Harness Closure — 2026-07-22

## Scope

This batch connects one registered fixture snapshot and transformer to the
independent real-mutation authority. It does not invoke the GitHub provider.

## Registered controls

The fixture target ID, repository-relative target path, fixed input digest, and
fixed output digest reside in one private registry. The source-minting seam
accepts bytes only if their digest matches the registered snapshot. The
transformer replaces exactly one subtraction operator in a return expression,
then requires the resulting digest to match its fixed registered output.

The output is minted only as the existing non-serializable ephemeral mutation
payload. It is not a contract, log field, artifact, or durable object; the
adapter destroys it on every exit path.

## Verification and review

Unit tests prove exact transformer behavior and rejection of unregistered
source. A separate controlled, read-only temporary checkout at the registered
base SHA supplied the actual target bytes to the harness in memory; input and
output digest revalidation passed and the checkout was deleted immediately.
No source content, payload content, or path was retained in the evidence.

Independent review found no P1 issue and recommended deduplicating target
constants. The fixture registry was added, regression-tested, and used by the
payload, orchestration, and CLI provider seams.
