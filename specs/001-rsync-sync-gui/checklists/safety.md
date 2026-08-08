# Safety & Data-Integrity Checklist: Rsync Folder Sync GUI

**Purpose**: Validate that the spec's requirements around destructive operations (mirror mode,
deletion, cross-drive sync) are complete, unambiguous, and consistent enough to implement safely,
before `/speckit-implement` — this is the domain where constitution Principle II (Safety by
Default) makes an unclear requirement expensive to get wrong.
**Created**: 2026-08-08
**Feature**: [spec.md](../spec.md)

**Note**: Generated with default focus (no explicit user request given): highest-risk domain =
destructive-sync/data-integrity requirements. Depth: standard. Audience: reviewer, as a pre-
implementation gate.

## Requirement Completeness

- [ ] CHK001 Are the exact rsync-level consequences of "mirror mode" (which flags' effects it
      corresponds to — delete-on-destination, overwrite-on-conflict) fully enumerated anywhere in
      the spec, rather than left implicit in the term "mirror"? [Completeness, Spec §FR-005/FR-006]
- [ ] CHK002 Does the spec define what happens if the dry-run preview itself fails (e.g. rsync
      errors during the dry-run pass, before any real changes)? [Gap, Spec §FR-006]
- [ ] CHK003 Are requirements defined for what the user sees if the *set of changes* differs
      between the dry-run preview and the real run (e.g. the destination changed in between)?
      [Gap, Coverage]
- [ ] CHK004 Are requirements defined for whether a canceled sync (FR-013) can leave the
      destination in a partially-synced state, and if so, whether that's disclosed to the user?
      [Gap, Edge Case]
- [ ] CHK005 Is there a requirement covering what "confirmation" means precisely (e.g. a single
      click on a dialog vs. typing a phrase) for a destructive run, or is the confirmation
      mechanism left fully to implementation discretion? [Clarity, Spec §FR-006]

## Requirement Clarity

- [ ] CHK006 Is "destructive" (used in FR-005) defined precisely enough to distinguish it from
      ordinary overwrite-on-change (which FR-005's own wording implies is allowed even without
      mirror mode)? [Ambiguity, Spec §FR-005]
- [ ] CHK007 Is "clearly report" (FR-010, for an unavailable job folder) given any concrete,
      checkable criteria, or is it left to implementation judgment what counts as "clear"?
      [Clarity, Spec §FR-010]
- [ ] CHK008 Is "readable form" (FR-012, for surfaced errors) given any concrete criteria (e.g.
      no raw stack traces, must include the failed path), or is it purely subjective?
      [Clarity, Spec §FR-012]

## Requirement Consistency

- [ ] CHK009 Do FR-005 ("MUST NOT remove... unless mirror mode enabled") and the Edge Cases
      section's out-of-space/permission scenarios agree on what "destructive" excludes — i.e. is
      an interrupted/partial write due to disk-full ever classified as a mirror-mode-only risk, or
      could it also happen in a non-mirror sync and is that consequence addressed consistently?
      [Consistency, Spec §FR-005 vs Edge Cases]
- [ ] CHK010 Do User Story 3's acceptance scenarios and FR-006 agree on whether the dry-run
      preview is mandatory for *every* mirror-mode run, or only the first one for a given job (the
      spec text implies "every run" — is that stated as explicitly for FR-006 as it is in the
      User Story)? [Consistency, Spec §US3 vs FR-006]

## Acceptance Criteria Quality

- [ ] CHK011 Is SC-003 ("zero unconfirmed destructive deletions... every removal preceded by a
      preview the user explicitly approved") stated in a way that is objectively verifiable from
      the requirements alone (i.e. does FR-006 fully guarantee SC-003, or is there a requirements
      gap between the two)? [Measurability, Spec §SC-003 vs FR-006]
- [ ] CHK012 Can "the user can identify what went wrong from the app's own output alone" (SC-004)
      be objectively tested against the current error-surfacing requirements (FR-012), or does it
      depend on subjective judgment of what counts as "identifiable"? [Measurability, Spec §SC-004]

## Scenario Coverage

- [ ] CHK013 Are requirements defined for a mirror-mode sync where the preview shows *zero*
      changes (destination already matches source) — does confirmation still apply, or is a
      no-op run allowed to skip the confirm step? [Gap, Edge Case]
- [ ] CHK014 Are requirements defined for what happens if the user enables mirror mode on a job
      that already ran previously in non-mirror mode — is there any transition/warning
      requirement, or is toggling mirror mode assumed to need no special handling? [Gap]
- [ ] CHK015 Are recovery requirements defined for a destructive sync that fails partway through
      (after confirmation, mid-transfer) — does the spec say anything about the state the user is
      left in, beyond the generic error-surfacing requirement (FR-012)? [Gap, Recovery]

## Dependencies & Assumptions

- [ ] CHK016 Is the assumption that rsync is already installed on the user's system (spec
      Assumptions) paired with any requirement for what the app does if it is missing or an
      incompatible version — or is that failure mode entirely unaddressed? [Gap, Spec §Assumptions]
- [ ] CHK017 Is the assumption that "different hard drives" means only locally-mounted volumes
      (excluding network/cloud) reflected consistently in every requirement that mentions folder
      selection, or could a user still point the picker at a network-mounted path without the
      spec saying what should happen? [Consistency, Spec §Assumptions vs FR-002]

## Notes

- Highest-priority items for review before implementation: CHK001, CHK002, CHK009, CHK010, CHK011
  — these bear most directly on constitution Principle II (Safety by Default).
- Check items off as reviewed: `[x]`. Where a gap is accepted as out-of-scope for v1, note that
  inline rather than silently checking it off.
