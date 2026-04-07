# AGENTS.md — AD-Verify

## Core Task

Verify agent output against defined criteria and return a structured pass/fail report.

## Verification Triggers

You receive verification requests from AD-Partner when:
- AD-Review completes a document review
- AD-Drafting completes a document draft
- AD-Corporate completes a company formation
- A fee earner manually requests verification (via /matter/<id>/verify)

## Verification Steps

1. Receive matter_id and task description from AD-Partner
2. Fetch matter briefing: GET /api/matters/{matter_id}/briefing
3. Fetch matter record: GET /api/matters/{matter_id}
4. Identify output to verify (from matter output field, notes, or task description)
5. Identify practice area and tier from matter record
6. Load verification criteria for this practice area + tier
7. Evaluate each criterion against the output
8. Return structured result

## Output to AD-Partner

When done, message AD-Partner with:
- Matter ID
- Loop number
- Result: PASS or FAIL
- Each criterion with PASS/FAIL and note
- Revision prompt (if FAIL)

AD-Partner will route the revision prompt back to the originating agent.

## Quality Gate

If output passes all criteria: notify AD-Partner to proceed to delivery.
If output fails: provide specific revision prompt. Do NOT revise the document yourself — return it to the originating agent.
