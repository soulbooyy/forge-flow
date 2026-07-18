# Approval, Trace, and Durable Summary Specification

## ADDED Requirements

### Requirement: Metadata publication SHALL be immutable and payload-free

The capability SHALL publish only an eligible metadata candidate and bounded
lineage as an immutable metadata artifact; it SHALL NOT publish source, diff,
or patch content.

#### Scenario: Ineligible candidate cannot publish

- **GIVEN** blocked, failed, indeterminate, or absent eligibility
- **WHEN** publication is requested
- **THEN** no durable artifact reference or summary linkage is created

### Requirement: Approval SHALL be independently bound and expiring

ApprovalDecision SHALL bind its exact request lineage and expiry; changed inputs
or expiry SHALL make it unusable for later governance evaluation.

#### Scenario: Stale approval is unusable

- **GIVEN** an expired or lineage-mismatched decision
- **WHEN** it is consumed
- **THEN** the outcome is approval-required and no later action is authorized

### Requirement: Durable summary SHALL contain redacted references only

DurableRunSummary SHALL append bounded immutable references and stop facts only.

#### Scenario: Raw payload cannot enter summary

- **GIVEN** a source, diff, command output, credential, environment value, or path
- **WHEN** summary input is validated
- **THEN** it is rejected without a partial durable record
