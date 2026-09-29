# Ad Hoc Inception: Private Event Preparation Checklist

Date: 2026-09-29
Status: illustrative source for Operator-led manual planning validation; unapproved
Authorship: assistant-drafted at the Operator's request, not an Operator decision

## Problem And Outcome

An event organizer needs a small private checklist for preparation tasks such as checking
supplies and confirming the room arrangement. Today those reminders can be scattered or
forgotten. The desired outcome is one durable list whose completion state is easy to inspect.

This is a proposed addition, not a claim that PokerNight already has event ownership,
authentication, storage or a checklist. Planning must inspect the selected operational base
and disclose absent prerequisites rather than invent existing functionality.

## Vocabulary And Scope

- Organizer: the person authorized to manage the selected event. Reuse an admitted role
  definition if one exists; otherwise its identity and authorization requirements need shaping.
- Preparation checklist: organizer-private reminders associated with exactly one event.
- Item: plain-text task label and a complete/incomplete state, initially incomplete.
- Completion: a reminder state only. It does not mean the event is approved or ready to start.

## Proposed Behavior

1. The organizer can add an item, rename it, mark it complete or incomplete, and delete it.
2. Labels contain 1-120 characters after trimming surrounding whitespace. Whitespace-only
   labels and longer labels are rejected with a clear error; existing data is unchanged.
3. Items remain in creation order when edited or completed. There is no manual reordering.
4. Duplicate labels are allowed; changing one item must not change another with the same label.
5. Leaving and reopening the event retains successfully saved labels, order and completion.
6. Each event has its own checklist. Editing one event never changes another event's items.
7. Other participants cannot read or change the organizer's private checklist. Enforcement
   must not rely only on hiding controls in the UI.
8. A failed save is reported without presenting the failed change as successfully persisted.
   Retrying one failed add must not create two copies of that requested item.

## Acceptance Examples

- Add "Check supplies": one incomplete item appears and survives reopening.
- Complete and then reopen that item: its completion state is retained; it can be undone.
- Add two identical labels, rename one: the other label and state remain unchanged.
- Submit spaces or a 121-character label: validation rejects it without altering saved items.
- Try accessing another organizer's checklist: no private content or mutation is allowed.
- Edit event A, then open event B: B's checklist is unchanged.
- Interrupt a save and retry: the outcome is explicit and the requested item is not duplicated.

## Decision To Resolve During Planning

Should deletion require confirmation, or offer undo after immediate removal? Neither is
selected by this sample. Discuss the tradeoff and append the Operator's actual decision
as a new source; preserve this original. Final acceptance criteria must cover the choice.

Technical realization, existing authorization integration and failure/retry behavior must
also be grounded in the real baseline before a complete proposal is claimed. Do not choose
a stack, API, database, fake phase ID or unsupported dependency merely to finish the exercise.

## Explicit Non-Goals

No player-visible tasks, task assignment, reminders/notifications, attachments, templates,
cross-event copying, automatic readiness gating or changes to league rules, scores, money,
registration or eligibility. No implementation is authorized by this document.

Reusable checklist templates are a possible later idea, not included work. Discuss whether
the Operator wants a separately captured deferred item; do not create one by inference.

## Planning Outcome Requested When Explicitly Invoked

Retain this source; assess terminology and prerequisites; draft proposed requirements and
work; resolve the open decision; then prepare a complete proposal only when requested.
Use as many phases as real dependencies justify, not a fixed count for demonstration.
The end-to-end validation ends at exact, reviewed, approved and verified admission of that
proposal into the selected repository specification, with execution progress unchanged.

This sample is separate from the preserved PokerNight inception pack. Do not silently add
it to that pack or to the later horizon's selected sources. Using it for a real admission
requires explicit Operator acceptance of its scope and destination.