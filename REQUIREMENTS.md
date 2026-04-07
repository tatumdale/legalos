# LegalOS Feature Requirements
## Two New Capabilities for the Harper James Legal OS

**Date:** 2026-04-07
**Prepared by:** Dexter Coder
**Status:** Draft — for Cursor Planning

---

## Overview

Two features drawn from LaVern AI's architecture, adapted for LegalOS's practice management context. Both are designed to improve the quality of agent output by adding structure before work begins (briefing) and structure after work is produced (verification loops).

**The two features:**
1. **Structured Briefing Interview** — rich context-gathering before any agent touches a matter
2. **Iterative Verification Loops** — output checked against criteria, sent back for revision if it fails

---

## Feature 1: Structured Briefing Interview

### What It Is

A configurable interview wizard that runs before or at the start of a matter. Instead of agents receiving a bare matter reference and working from nothing, they receive a rich briefing: jurisdiction, deal size, commercial intent, risk appetite, specific concerns, client type.

The briefing is built through a structured conversation with the client (or fee earner on behalf of the client). Questions adapt based on matter type — a contract review asks different things than a dispute or a company formation.

### Why We Want It

Legal analysis is fundamentally a context game. A non-compete clause means something different for a Fortune 500 CEO than for a junior developer. An indemnification cap matters differently in a £10M deal versus a £100K engagement. A termination clause that's standard in Delaware may be unenforceable in California.

Current LegalOS agents receive the matter title, some notes, and whatever context was captured in the intake form. The output is generic because the context is generic.

A structured briefing means every downstream agent — reviewer, drafter, researcher — receives the same rich picture of what the client actually needs. Output quality improves not because the model gets better, but because it knows what it's reviewing and why.

### How We Want It to Work

#### 1.1 Trigger Points

The briefing interview can be triggered in three ways:

- **Manual:** Fee earner starts a briefing from the matter detail page ("Prepare Briefing")
- **Automatic (recommended):** When a matter reaches `active` status from intake, the system prompts for briefing completion before agent work begins
- **Template-based:** Matter types can have a pre-configured briefing template with suggested questions pre-populated

#### 1.2 Interview Flow

The interview presents as a conversational wizard (multi-step form). It is NOT a free-text chat — it collects structured parameters. Each step shows one question or a small group of related questions.

**Core questions (always asked):**
- Jurisdiction (England & Wales default, but Scotland/Northern Ireland/other selectable)
- Client type (startup, SME, large corporate, individual, public sector)
- Counterparty (name, type if known)
- Deal/matter value (band: <£10K / £10K–£100K / £100K–£1M / £1M+ / undisclosed)
- Deadline (date picker, optional)
- Risk appetite (conservative / balanced / commercial — with one-line explanations)

**Questions by matter type (shown conditionally):**

| Matter Type | Additional Questions |
|---|---|
| Contract review | Counterparty jurisdiction, contract type (supply/services/licence), duration, known problem areas, whether negotiation is expected |
| Company formation | Structure (Ltd/LLP/other), jurisdiction of incorporation, number of directors, shareholders, any specific requirements |
| Employment | Employee level (junior/mid/senior exec), equity/incentives, restrictive covenant scope desired |
| IP | What IP is being protected (trade mark/patent/copyright/design), any existing registrations, whether third parties are involved |
| Dispute | Dispute type, stage (pre-action/active/proposed), whether litigation is threatened, opposing party known |
| Data protection | Data types involved (personal/sensitive/special category), number of data subjects (estimate), whether ICO notification is relevant |
| M&A / due diligence | Target jurisdiction, deal type (asset/share), deal stage, whether financials are in scope |

**Interview UX:**
- Multi-step form with progress indicator ("Step 2 of 5")
- Each step can be skipped (fields marked optional), but the fee earner is prompted to complete
- Voice input supported (using Mac say / browser speech API)
- Can save as draft and resume later
- On completion: summary shown ("Here's what we've captured"), fee earner can edit before confirming

#### 1.3 Briefing Storage and Injection

When a briefing is confirmed:

- Stored as a structured JSON object on the matter record: `briefing` field
- Also stored as a readable summary in the matter's `notes` field (for human review)
- When any agent is dispatched for this matter, the briefing is injected into the agent's system prompt as structured context

**Briefing object structure:**
```json
{
  "matter_id": "...",
  "completed_at": "2026-04-07T...",
  "jurisdiction": "England and Wales",
  "client_type": "SME",
  "client_name": "...",
  "counterparty": "...",
  "deal_value_band": "£100K–£1M",
  "deadline": "2026-04-30",
  "risk_appetite": "balanced",
  "additional_context": { ... },  // type-specific fields
  "summary": "Human-readable paragraph summary"
}
```

#### 1.4 Agent Prompt Integration

The AD agents' system prompts are updated to prepend briefing context:

```
[Briefing]
Client: {client_name}
Jurisdiction: {jurisdiction}
Matter type: {matter_type}
Risk appetite: {risk_appetite}
Deal value: {deal_value_band}
Key context: {summary}
[/Briefing]

[Original system prompt continues]
```

This is added to every agent that receives a task for this matter, automatically.

#### 1.5 UI Pages to Add/Modify

- **New page: `/matter/<id>/briefing`** — interview wizard
- **Modify: Matter detail page** — show briefing status badge; link to "Prepare Briefing" if incomplete; show briefing summary if complete
- **Modify: Matter list** — filter/flag matters with incomplete briefings

---

## Feature 2: Iterative Verification Loops (Ralph Pattern)

### What It Is

Agents produce output. Currently, that output is final — it's stored and presented to the fee earner. The verification loop adds a checking layer: the output is validated against defined criteria, and if it fails, it's sent back to the originating agent for revision. The loop repeats until output passes all checks or a maximum loop count is reached.

This is not quality control by a human. It's automated structural verification: does this contract include the required clauses? Is the advice within jurisdiction? Are the risks properly flagged? If not, send it back.

### Why We Want It

LaVern's architecture note is correct: "A single pass produces a draft. A loop that checks, revises, and checks again produces a deliverable."

Current LegalOS agents produce a single-pass output. For document review, that means: here's the review, here's the output, done. There's no check that the review actually caught the things it should have caught — no check that the drafted document actually includes the required provisions.

A verification loop doesn't guarantee perfect output, but it catches the obvious gaps before the fee earner ever sees the document. It shifts the agent from "produces a draft" to "produces a deliverable."

### How We Want It to Work

#### 2.1 Where Verification Applies

Verification loops apply to two primary workflows:

**A. Document Review (AD-Review)**
- Reviewer agent produces output
- Verification layer checks: required clauses present, risks flagged, jurisdiction correct, tier-appropriate depth
- If check fails: reviewer revises; loop up to N times

**B. Document Drafting (AD-Drafting)**
- Drafter agent produces document
- Verification layer checks: all required sections present, definitions complete, no internal contradictions, appropriate risk allocation
- If check fails: drafter revises; loop up to N times

#### 2.2 Verification Criteria (Per Matter Type)

Verification criteria are defined per practice area + service line + tier. Examples:

**Contract review — Tier 2 (Standard):**
- [ ] Jurisdiction-specific clauses present (governing law + jurisdiction)
- [ ] Termination rights identified and quantified
- [ ] Limitation of liability cap discussed or justified
- [ ] Payment/penalty clauses flagged
- [ ] Exclusion clauses assessed under UCTA reasonableness test
- [ ] Risk rating applied (RED/AMBER/GREEN)

**Contract drafting — Tier 2 (Standard):**
- [ ] All required sections present (parties, definitions, subject matter, consideration, obligations, payment, termination, liability, confidentiality, IP, force majeure, dispute resolution, general provisions)
- [ ] Definitions section complete and consistent with usage
- [ ] Governing law and jurisdiction clause present
- [ ] No internal contradictions detected
- [ ] Risk allocation appropriate to matter tier

**Company formation — Tier 1 (Light):**
- [ ] Articles of Association match selected structure
- [ ] Director appointment details complete
- [ ] Shareholder structure matches instructions
- [ ] Companies House filing requirements identified

#### 2.3 Verification Agent (AD-Verify)

A new specialist agent: **AD-Verify**. Its sole purpose is to check output against criteria and return a structured pass/fail report.

**AD-Verify receives:**
- The original task (what was asked)
- The agent's output (what was produced)
- The verification criteria for this matter type + tier
- The matter's briefing context

**AD-Verify returns:**
```json
{
  "passed": false,
  "checks": [
    { "criterion": "Governing law clause present", "passed": true, "note": "English law selected, clause 14.2" },
    { "criterion": "Termination rights identified", "passed": false, "note": "No termination provisions found for insolvency scenario" },
    { "criterion": "Limitation of liability discussed", "passed": true, "note": "Cap of £1M identified at clause 9.1" }
  ],
  "revision_prompt": "The review did not identify termination rights. Revise to include termination provisions, specifically addressing: (1) termination for convenience, (2) termination for breach, (3) insolvency scenario."
}
```

#### 2.4 Loop Flow

```
Agent produces output
    ↓
AD-Verify checks against criteria
    ↓
[passed?] → YES → Output goes to fee earner
    ↓ NO
[loop_count < max_loops?] → YES → Agent revises based on AD-Verify revision_prompt
    ↓ NO               ↓
Flag for fee earner    Loop count incremented
human review           AD-Verify checks again
```

**Max loops configurable:**
- Default: 2 (one revision allowed)
- Per matter type: configurable in matter type settings
- Fee earner can override: request extra loop or accept despite failed checks

#### 2.5 Verification Log

Every verification run is logged on the matter:

```
[2026-04-07 14:30] AD-Verify (loop 1): FAILED — 2 checks failed
  - Termination rights: NOT PASSED
  - Risk rating: NOT PASSED
  → Revision requested

[2026-04-07 14:32] AD-Drafting: Revision submitted

[2026-04-07 14:33] AD-Verify (loop 2): PASSED — all checks passed
  → Output approved for delivery
```

The fee earner sees this log on the matter detail page.

#### 2.6 UI Pages to Add/Modify

- **New page: `/matter/<id>/verification-log`** — verification history for the matter (or embed in matter detail timeline)
- **Modify: Matter detail page** — show verification status badge; failed checks highlighted in red; loop count shown
- **Modify: Matter type settings** — add/remove verification criteria per practice area + tier

---

## Shared Implementation Notes

### Database Changes

**Matters table — add fields:**
- `briefing` (TEXT, JSON) — structured briefing object
- `briefing_completed_at` (TEXT, ISO datetime)
- `verification_loops_enabled` (INTEGER, default 1)
- `verification_max_loops` (INTEGER, default 2)

**New table: `verification_log`:**
```sql
CREATE TABLE verification_log (
    id TEXT PRIMARY KEY,
    matter_id TEXT REFERENCES matters(id),
    agent_id TEXT,
    loop_number INTEGER,
    passed INTEGER,
    criteria_json TEXT,
    revision_prompt TEXT,
    created_at TEXT
);
```

### Agent Changes

**New agent: AD-Verify**
- Specialty: quality assurance / verification
- Receives: task + output + criteria + briefing
- Returns: structured pass/fail + revision prompt if failed
- Works silently — no client-facing messages

**Existing agents modified:**
- AD-Intake: ability to launch briefing wizard after matter activation
- AD-Review: loop integration — pause for verification, revise on failure
- AD-Drafting: loop integration — pause for verification, revise on failure
- AD-Partner: receives notification when verification permanently fails

### Key Design Decisions to Confirm Before Build

1. **Briefing interview: who answers?** Fee earner (on behalf of client) or client directly? Decision: fee earner-first. The interview is a tool for the fee earner to capture context, not a client self-service form (at least initially).

2. **Briefing: mandatory or optional?** Recommendation: strongly encouraged for Tier 2 and Tier 3 matters, optional for Tier 1. Configurable per matter type.

3. **Verification loop: always on?** Recommendation: on by default for Tier 2 and Tier 3 document review and drafting. Off by default for Tier 1 (speed over depth). Fee earner can override per matter.

4. **AD-Verify: separate agent or integrated check function?** Recommendation: separate agent (AD-Verify) with its own skill. Cleaner architecture, easier to improve criteria over time without modifying the reviewer/drafter agents.

---

## Out of Scope (For This Build)

- Voice briefing input (step 1 is text/structured form only)
- Client self-service briefing portal
- Automatic precedent injection based on briefing
- Multi-agent adversarial debate (full LaVern-style — separate future feature)
- Billing/cost tracking integration
- Google Drive auto-filing based on verification status

---

## Priority and Effort Estimate

| Feature | Impact | Effort | Priority |
|---|---|---|---|
| Structured Briefing Interview | High | Medium | P1 |
| Iterative Verification Loops | High | Medium-High | P1 |
| AD-Verify agent | High | Medium | P1 (prerequisite for loops) |

All three are tightly coupled — briefing feeds verification, verification requires AD-Verify. Recommend building in order: AD-Verify → Verification Loops → Briefing.

---

## Management and Configuration

### Configuration Levels

Both features are configurable at three levels, with later levels overriding earlier ones:

| Level | Who sets it | Override-able per matter? |
|---|---|---|
| **System default** | Firm admin (settings page) | Yes — per matter |
| **Matter type override** | Firm admin (matter type config) | Yes — per matter |
| **Per-matter override** | Fee earner (matter detail page) | No — this is final |

This three-level approach means the firm can set sensible firm-wide defaults, adjust by matter type (e.g. M&A = strict, NDA pre-screening = loose), and still let fee earners override on individual matters when needed.

---

### Settings UI — Engagement Settings

A new section at `/settings/engagement` with two sub-sections:

#### Briefing Configuration

| Setting | Options | Default |
|---|---|---|
| Briefing required | Required / Recommended / Optional / Off | Recommended |
| Briefing question set | Per matter type (dropdown to select) | Built-in default |
| Allow fee earner to skip | Yes / No | Yes |

**Per matter type table** (rows = practice areas, columns = tiers 1/2/3):

| Practice Area | Tier 1 | Tier 2 | Tier 3 |
|---|---|---|---|
| Commercial Law | Optional | Required | Required |
| Employment Law | Optional | Required | Required |
| Company Formation | Recommended | Required | Required |
| IP Law | Optional | Required | Required |
| Data Protection | Recommended | Required | Required |
| ... | | | |

Each cell shows the configured behaviour (Required / Recommended / Optional / Off). Clicking a cell opens a popover to change it.

#### Question Template Editor

Each matter type has a **question template** — the set of questions asked in the briefing interview. Templates are stored as JSON and editable via a UI form (not raw JSON).

**Template structure** (stored per matter type, override-able):
```json
{
  "practice_area": "commercial-law",
  "service_line": "reviewing",
  "tier": 2,
  "required_fields": ["jurisdiction", "risk_appetite", "deal_value_band"],
  "conditional_fields": ["counterparty_jurisdiction", "contract_type"],
  "questions": {
    "jurisdiction": {
      "type": "select",
      "label": "Applicable law",
      "options": ["England and Wales", "Scotland", "Northern Ireland", "Other"],
      "default": "England and Wales"
    },
    "risk_appetite": {
      "type": "radio",
      "label": "Client risk appetite",
      "options": [
        {"value": "conservative", "label": "Conservative — minimise all risk"},
        {"value": "balanced", "label": "Balanced — normal commercial risk"},
        {"value": "commercial", "label": "Commercial — accept reasonable risk for deal velocity"}
      ]
    },
    "deal_value_band": {
      "type": "select",
      "label": "Deal / matter value",
      "options": ["Under £10K", "£10K–£100K", "£100K–£1M", "Over £1M", "Undisclosed"]
    }
  }
}
```

Firm admins can add, remove, or edit questions per matter type via the settings UI. New matter types can be created by copying from an existing template.

#### Verification Configuration

| Setting | Options | Default |
|---|---|---|
| Verification enabled | On / Off (system-wide) | On |
| Default max loops | 1–5 (slider) | 2 |
| Notify on permanent failure | Yes / No | Yes |

**Per matter type table** (same structure as briefing):

| Practice Area | Tier 1 | Tier 2 | Tier 3 |
|---|---|---|---|
| Commercial Law | Off | On (2 loops) | On (3 loops) |
| Employment Law | Off | On (2 loops) | On (3 loops) |
| Company Formation | Off | On (1 loop) | On (2 loops) |
| ... | | | |

#### Verification Criteria Editor

Each matter type + tier combination has a **criteria set** — the list of checks AD-Verify applies.

**Criteria structure**:
```json
{
  "practice_area": "commercial-law",
  "service_line": "reviewing",
  "tier": 2,
  "checks": [
    {
      "id": "governing_law",
      "label": "Governing law clause present",
      "description": "Review output must identify or note absence of governing law and jurisdiction clause",
      "enabled": true
    },
    {
      "id": "termination",
      "label": "Termination rights identified",
      "description": "Review must cover termination for convenience, breach, and insolvency scenarios",
      "enabled": true
    },
    {
      "id": "liability_cap",
      "label": "Limitation of liability addressed",
      "description": "Review must flag any limitation of liability clause and assess reasonableness",
      "enabled": true
    },
    {
      "id": "risk_rating",
      "label": "Risk rating applied",
      "description": "Each significant clause must have a RED/AMBER/GREEN risk rating",
      "enabled": true
    }
  ]
}
```

Firm admins can toggle individual checks on/off, add new criteria, or reorder them. AD-Verify reads the enabled criteria only.

---

### Per-Matter Override

On any individual matter, the fee earner can override the briefing and verification settings:

- **Skip briefing** — mark as "briefing not required" with a mandatory reason (client instructed / Tier 1 / other)
- **Force extra loops** — request additional verification iterations beyond the matter type default
- **Disable verification** — switch off loops entirely for this matter (with reason)
- **Add manual criteria** — add one-off checks specific to this matter

All overrides are logged in the matter audit trail.

---

### How Features Impact Existing Workflows

#### Matter Lifecycle

**Before:**
```
Intake → Conflict check → Classification → Matter opened → Work begins
```

**After (with briefing required):**
```
Intake → Conflict check → Classification → Matter opened
    ↓
Briefing pending (sub-state — work paused)
    ↓  Briefing completed
Work begins → [Verification loops if applicable]
```

If briefing is optional or skipped: work begins immediately. Briefing can be completed retroactively and its context still injected into future agent calls for this matter.

**Matter state changes:**
- `briefing_status` field on matter: `pending` / `complete` / `skipped` / `not_required`
- Agents do not auto-start for matters with `briefing_status = pending` (when briefing is required)

#### Agent Behaviour

| Agent | Briefing impact | Verification impact |
|---|---|---|
| **AD-Intake** | New: can trigger briefing wizard on matter activation | None |
| **AD-Review** | Reads briefing context in system prompt | Modified: pauses for AD-Verify, revises on failure |
| **AD-Drafting** | Reads briefing context in system prompt | Modified: pauses for AD-Verify, revises on failure |
| **AD-Research** | Reads briefing context in system prompt | Could verify research scope against brief |
| **AD-Corporate** | Reads briefing context in system prompt | Off by default (formations are simple) |
| **AD-Partner** | Receives briefing summary | Receives notification on permanent verification failure |
| **AD-Verify** | Uses briefing context in all checks | New agent — does the checking |

**Agent prompt changes are additive** — briefing context is prepended to the existing system prompt. No existing prompt content is removed. Backward compatible.

#### Fee Earner Experience

- **Matter detail page:** Briefing status badge (🟡 Pending / 🟢 Complete / ⚪ Not required); Verification badge (loop count, pass/fail); "Prepare Briefing" button if pending
- **Matter list:** Optional filter — "Show matters with incomplete briefings"
- **Matter timeline:** Verification log entries appear as activity entries (see example in Feature 2 section)
- **Matter type settings:** New tab — "Briefing & Verification" — per type configuration
- **Settings page:** New section — "Engagement Settings" — firm-wide defaults

---

### What Stays the Same

| Feature | Impact |
|---|---|
| SOUL.md editor | Unchanged |
| Skills detail view | Unchanged |
| Existing matter records | Work fine — new fields are NULL/empty (graceful degradation) |
| Google Drive integration | Unchanged |
| CRM | Unchanged |
| Audit trail | Extended with briefing + verification events |
| Agent SOUL/AGENTS files | Unchanged |

---

### Database Summary

**New fields on `matters` table:**
- `briefing` (TEXT, JSON) — full briefing object
- `briefing_status` (TEXT) — `pending` / `complete` / `skipped` / `not_required`
- `briefing_completed_at` (TEXT, ISO datetime)
- `verification_loops_enabled` (INTEGER, 0 or 1)
- `verification_max_loops` (INTEGER, default 2)

**New table: `matter_type_config`** — per practice area × service line × tier config for both features
```sql
CREATE TABLE matter_type_config (
    id TEXT PRIMARY KEY,
    practice_area TEXT,
    service_line TEXT,
    tier INTEGER,
    briefing_behaviour TEXT DEFAULT 'recommended',
    briefing_template_json TEXT,
    verification_enabled INTEGER DEFAULT 1,
    verification_max_loops INTEGER DEFAULT 2,
    verification_criteria_json TEXT,
    updated_at TEXT
);
```

**New table: `verification_log`**
```sql
CREATE TABLE verification_log (
    id TEXT PRIMARY KEY,
    matter_id TEXT REFERENCES matters(id),
    agent_id TEXT,
    loop_number INTEGER,
    passed INTEGER,
    checks_json TEXT,
    revision_prompt TEXT,
    created_at TEXT
);
```

No existing tables deleted. No existing data modified. Old matters work without any changes.

---

### Quick Config Summary

| | Briefing | Verification |
|---|---|---|
| **New tables/fields** | 3 fields on matters + matter_type_config | verification_log + 2 fields on matters |
| **New agent** | No | Yes: AD-Verify |
| **Existing agent changes** | AD-Intake (triggers wizard) | AD-Review + AD-Drafting (loop handling) |
| **Existing features broken** | None | None |
| **Config location** | /settings/engagement | /settings/engagement |
| **Per-matter override** | Yes | Yes |
| **Backward compatible** | Yes | Yes (off by default for Tier 1) |
| **Graceful degradation** | Old matters: briefing_status = not_required | Old matters: verification_loops_enabled = 0 |

---

## Files Likely to Change

- `app.py` — new routes, new agents, modified matter flow
- `templates/matter_detail.html` — briefing badge, verification log embed
- `templates/briefing_wizard.html` — new page
- `templates/verification_log.html` — new page (or integrated)
- `db schema` — matters table update, new verification_log table
- Agent skill files for AD-Verify (new), AD-Review (modified), AD-Drafting (modified)
- `AGENTS.md` in workspace — AD-Verify agent documentation
