# ADR-005: Use Filesystem-Only Repository Context Inspection

## Status

Accepted

## Context

Milestone 1 needs deterministic repository context while preserving a strict read-only security boundary. The OpenSpec revision clarified that even commands often considered read-only, such as `git status`, `git ls-files`, `find`, `rg`, or `grep`, introduce platform, policy, audit, shell, environment, timeout, output, and tool-availability concerns.

This is a stable architectural boundary because future contributors may otherwise implement repository discovery through Git, search commands, package managers, language servers, or other external tools. That would quietly introduce a command-governance slice into Milestone 1 and weaken the separation between repository context and later sandbox/security policy work.

## Decision

Milestone 1 Repository Context Service must inspect repositories only through workspace-confined direct filesystem APIs or libraries.

Repository context inspection may perform deterministic traversal, metadata reads, bounded file reads, binary detection, UTF-8 decoding, content hashing, path normalization, ignore-policy evaluation, and symlink boundary checks.

Repository context inspection must not execute shell commands, subprocesses, Git commands, search commands, package-manager commands, test commands, language servers, external tools, or network calls. It must not install dependencies, write repository files, create branches, create commits, create PRs, read or write memory, or modify DeerFlow core.

Command-backed search or tool-backed repository inspection may be introduced only by a future OpenSpec or ADR that defines command intent, allowlists, environment policy, timeout/output bounds, audit behavior, and deterministic fallback semantics.

## Alternatives Considered

- Use Git commands for deterministic file discovery: rejected because Git behavior, ignore semantics, repository state, and platform output would become hidden contract inputs.
- Use `rg`, `grep`, or `find` for convenience: rejected because command availability, shell quoting, environment exposure, output caps, and failure modes would require command-governance design.
- Allow read-only commands as automatically safe: rejected because read-only execution still has policy, audit, and determinism implications.
- Build a full sandbox command layer in Milestone 1: rejected because Milestone 1 is the Repository Context Foundation Slice, not a command-governance milestone.

## Consequences

Positive consequences:

- Keeps Milestone 1 deterministic and portable across implementations.
- Prevents accidental expansion into command governance or sandbox execution.
- Makes side-effect absence easier to test with fixtures.
- Preserves RFC-004-style policy decisions for later milestones.

Negative consequences / trade-offs:

- The first implementation must implement traversal and text search directly.
- It cannot rely on optimized external search tools.
- Future Git-aware or command-backed behavior requires explicit design work before adoption.

