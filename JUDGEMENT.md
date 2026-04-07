# JUDGEMENT.md — Acme Dale Legal Services Legal OS
## Institutional Memory & Decision Framework for HJ Agents

*This file is the collective institutional memory of the Acme Dale Legal Services Legal OS. Read by all HJ agents at session start and overlaid on their SOUL.md. It improves agent judgement over time by capturing real contract learnings, precedent decisions, and allocation logic.*

---

## Section 1 — How to Use This File

Every HJ agent reads this at session start. It acts as:
1. **Judgement overlay** — additional context supplementing (not replacing) the agent SOUL.md
2. **Precedent library** — structured entries from completed matters guiding future decisions
3. **LLM allocation guide** — which model to use for which task type
4. **Escalation logic** — codified rules for when to flag vs. approve vs. reject

**Rule:** When in doubt, follow SOUL.md. When a precedent exists here, apply it. When neither applies, escalate.

---

## Section 2 — LLM Allocation Table

| Task Type | Recommended Model | Rationale |
|---|---|---|
| Matter intake / classification | MiniMax M2.7 | Fast, cost-effective. Pattern-matching — no deep reasoning needed. |
| Contract clause review (single clause) | MiniMax M2.7 | Speed-first. Flag anything unusual to escalate. |
| Full contract RAG analysis | Opus 4.6 (Cursor) | Complex reasoning, cross-referencing, risk assessment — frontier model. |
| Client care letter generation | MiniMax M2.7 | Template-driven with minor variations. |
| SRA compliance check | MiniMax M2.7 | Rule application — pattern matching against known framework. |
| Escalation / high-risk decision | Opus 4.6 (Cursor) | Nuanced judgement required. Never delegate to fast model. |
| Drafting / red-lining | Opus 4.6 (Cursor) | Precision and legal quality paramount. |
| Research / case law | Opus 4.6 (Cursor) | Accuracy over speed. |

**OpenClaw model aliases:**
- minimax/MiniMax-M2.7 — default, fast reasoning
- minimax/MiniMax-M2.7-highspeed — heavy reasoning tasks  
- opus-4.6-thinking — frontier model via Cursor CLI: agent --print --trust --yolo --workspace <path>

---

## Section 3 — Contract Review Judgement Framework

### RAG Definitions

| Rating | Meaning | Action |
|---|---|---|
| GREEN | Clause is balanced, commercially reasonable, no material risk | No action required. Document and proceed. |
| AMBER | Clause presents risk/imbalance to flag, may require negotiation | Note in output. Inform client. Address before execution if time permits. |
| RED | Clause presents material risk, is one-sided, or may be unenforceable | Do NOT execute. Return with red-line requests. |

### Standard RED Triggers
- Termination without notice AND non-compete in same agreement — disproportionate restriction
- IP assignment with NO infringement warranty — no recourse for third-party IP claims
- Uncapped indemnities in favour of Acme Dale Legal Services — commercially aggressive
- No PI insurance requirement for Supplier — Acme Dale Legal Services bears negligence risk
- Assignment of future IP without warranty of originality

### Standard GREEN Triggers
- Confidentiality with reasonable carve-outs (public domain, prior knowledge, Operation of Law)
- Post-termination assistance limited to 30 days and reasonable scope
- Substitution rights with Acme Dale Legal Services consent; Supplier remains liable
- Termination for cause with reasonable cure period
- Worker status indemnity triggered only after final HMRC determination

---

## Section 4 — Precedent Entries

---

### [AC/2026/0001] — Company Formation — 2026-03-27

**What we learned:** Standard UK limited company incorporation is routine. Critical path: name clearance with Companies House (usually same day if filed by 3pm). Articles must match shareholders agreement. Standard model articles (Table A) appropriate for simple 2-person companies.

**Decision rationale:** Two directors, two shareholders, equal shareholding. No unusual voting rights or reserved matters. Standard articles appropriate.

**Outcome:** Incorporation filed and confirmed. Share certificates issued.

**RAG summary:** GREEN — standard incorporation, no material risk factors.

**LLM used:** MiniMax M2.7.

**Precedent value:** Medium — Good template for small company formations. Advise clients that a shareholders agreement is recommended even for 50/50 owned companies.

**Keywords:** incorporation, Companies Act 2006, Table A, new company, name clearance

---

### [AC/2026/0002] — M&A Share Purchase — 2026-03-27

**What we learned:** SPA warranties and indemnities are key risk areas. Non-compete post-Tillman v Egon Zehnder [2012] enforceable for up to 12 months if reasonable in scope and geography. Indemnities in Sch.4 should be separately negotiated from general warranties — they survive longer and are not subject to the knowledge qualifier.

**Decision rationale:** Deal value £2.4m = mid-market. Standard warranty caps (1% of purchase price for general warranties). Locked box chosen over completion accounts — simpler and faster for businesses with clean audited accounts.

**Outcome:** In progress — due diligence ongoing.

**RAG summary:** AMBER — standard mid-market terms, no RED items.

**LLM used:** MiniMax M2.7.

**Precedent value:** High — Good mid-market SPA template. Locked box suitable for profitable businesses with clean audited accounts.

**Keywords:** SPA, warranties, indemnities, locked box, Tillman, non-compete, Sch.4, completion accounts

---

### [AC/2026/0003] — Consultancy Agreement Contract Review — 2026-03-29

**What we learned:** When reviewing supplier agreements (vs. client-facing engagements), the risk profile differs. Key risks: (1) uncapped indemnities; (2) IP infringement gaps; (3) termination/non-compete asymmetry; (4) absence of Supplier PI insurance requirement. Critical insight: cl.8.1 (termination at will) + cl.5.1.2 (non-compete) in the same agreement creates a structural imbalance — Acme Dale Legal Services can terminate instantly while the non-compete persists. This combination frequently appears in supplier agreements and should always be flagged RED.

**Decision rationale:** This was Acme Dale Legal Services own supplier contract (engaging Tatumdale Ltd). Despite short-form, structural imbalances required flagging. Three RED items, three AMBER items, three GREEN items.

**Outcome:** Matter returned. Not recommended for execution in current form. Tatum to red-line specific clauses before signing.

**RAG summary:**
- RED (3): cl.5.1.2 non-compete (no time/geography limits, disproportionate given termination at will), cl.7.2/7.3 IP assignment (no infringement warranty), cl.8.1 termination (at will, no notice)
- AMBER (3): cl.3.1 scope (non-exclusive, no minimum commitment), cl.3.7 post-termination assistance (uncapped), cl.4.5.1 tax indemnity (uncapped)
- GREEN (3): cl.4.5.2 worker status indemnity (post-HMRC determination only), cl.3.8 substitution (Acme Dale Legal Services consent required, Supplier remains liable), cl.6.1/6.2 confidentiality (standard carve-outs)

**LLM used:** MiniMax M2.7 (matter creation) + Opus 4.6 Cursor (RAG analysis generation).

**RED-line requests generated:**
1. cl.5.1.2: Narrow to specifically competitive engagements; add 3-month post-termination time limit; carve-out for Tatumdale existing client base
2. cl.7.2/7.3: Add warranty Supplier warrants deliverables will not infringe third-party IP rights; add indemnity for infringement claims
3. cl.8.1: Add minimum 30-day notice period; if terminated without cause, Supplier entitled to fees for notice period; non-compete to lapse on termination without cause
4. cl.4.5.1: Cap indemnity at 12 months fees

**Escalation note:** This matter involved Acme Dale Legal Services as a party — a potential independence conflict for the Legal OS. When Acme Dale Legal Services appears as a client or counterparty, the reviewing solicitor must be external to the engagement. Always note conflicts in the audit trail.

**Precedent value:** High — First supplier services agreement reviewed. The cl.8.1 + cl.5.1.2 interaction is a recurring pattern to watch in all supplier agreements.

**Keywords:** consultancy agreement, supplier services, IP assignment, non-compete, termination at will, indemnity caps, substitution, TUPE, IR35

---

## Section 5 — Escalation Matrix

| Situation | Action | Who |
|---|---|---|
| Any RED clause in contract review | Do not execute. Return with red-line requests. | AD-Review |
| Any matter involving Acme Dale Legal Services as a party | Flag conflict in audit trail. Ensure external review. | AD-Review |
| Classification confidence below 70% | Reject. Return to intake with clarification request. | AD-Review |
| Matter value above £50,000 | Escalate to COLP (Tatum). | AD-Review |
| Potential conflict with existing Acme Dale Legal Services client | Reject. Flag to Tatum. | AD-Intake |
| SRA compliance issue suspected | Reject immediately. Flag to Tatum. | AD-Review |
| AI hallucination suspected in output | Reject immediately. Flag to Tatum. | AD-Review |

---

## Section 6 — Adding New Entries

After every completed matter, add to Section 4 using this template:

### [Matter Ref] — [Matter Type] — [Date]
**What we learned:** [Specific legal or practical insight]
**Decision rationale:** [Why we made the decisions we made]
**Outcome:** [What happened]
**RAG summary:** [RED/AMBER/GREEN counts and key clauses]
**LLM used:** [Model used for primary analysis]
**RED-line requests generated (if any):** [Specific clause change requests]
**Escalation notes:** [Any issues requiring human intervention]
**Precedent value:** High/Medium/Low + why
**Keywords:** [Searchable terms]

Entries should be factual and specific. No vague generalisations. Each entry should make future decisions faster and more accurate.

---

Maintained by the HJ agent team. Last updated: 2026-03-30.

---

## Section 5 — IR35-Specific Judgement Triggers

### Substitution Clauses (IR35)

| Clause Type | RAG | Rationale |
|---|---|---|
| PSC may substitute with any competent person; client consent not required | GREEN | Genuine substitution right; HMRC-accepted outside-IR35 indicator |
| Substitution with client consent (not to be unreasonably withheld) | AMBER | Consent requirement undermines genuineness; could be challenged |
| Substitution requires client's absolute discretion | RED | Illusory right; HMRC treats as personal service; inside IR35 |
| No substitution clause at all | RED | HMRC infers personal service obligation |

### Mutuality of Obligation (IR35)

| Clause Type | RAG | Rationale |
|---|---|---|
| No minimum commitment; either party may walk away | GREEN | No MOO; worker genuinely self-employed |
| Guaranteed minimum hours / minimum fee commitment | AMBER | MOO present; pushes toward employment |
| Rolling/ongoing contract with no end date AND no exit clause | RED | Strong MOO; HMRC treats as continuous employment |

### Non-Compete + Termination Interaction (IR35)

This is the specific structural issue in the Tatumdale Ltd contract (MAT/2026/003):

| Pattern | RAG | Rationale |
|---|---|---|
| Termination at will + non-compete with no time limit | RED | Enforceability doubtful. Courts look at overall picture. If Acme Dale Legal Services can terminate without cause AND immediately engage a competitor while the non-compete persists on the contractor, the restriction is disproportionate. IR35 risk: HMRC sees ongoing MOO through non-compete. |
| Non-compete with reasonable time/geography limit; termination with cause only | AMBER | Potentially enforceable if reasonable. IR35 risk reduced if there is a defined end. |

**The Tatumdale contract structural problem:** Termination without notice (8.1) combined with an unlimited non-compete (5.1.2) means Acme Dale Legal Services can terminate today, engage a competitor tomorrow, and the non-compete on Tatumdale Ltd persists indefinitely. This is not a genuine business-to-business relationship — it looks like employment with extra steps. This combination is a RED flag for both enforceability AND IR35.

---

## Section 6 — Legal OS Feature Notes (2026-03-30)

_Added during Legal OS Phase 2 build. Documents new system capabilities for agent reference._

### Time Tracking & Billing

- Time is logged in 6-minute units at £150/hr default rate (150 pence/minute)
- All time entries must be linked to a matter_id and agent_id
- Invoice creation (via `POST /api/invoices`) locks time entries (billing_status → 'invoiced')
- Disbursements added separately, included in invoice total
- Standard UK solicitor rate: £150–£300/hr. Default is £150/hr (15000 pence/min)

### Conflict Check Automation

- Runs on matter creation (automatic) and on demand via `POST /api/matters/<id>/conflict-check`
- Searches: existing client names, existing matter clients, adverse_parties field
- Result: CLEAR or CONFLICT_FOUND
- CONFLICT_FOUND → matter.conflict_check_status set to 'flagged' → AD-Review must escalate before matter proceeds
- Note: always excludes the matter being checked from its own results (self-referential fix applied 2026-03-30)

### Research (AD-Research Agent)

- BAILII searches are best-effort (no SLA on uptime, scraping may break)
- Internal precedents always searched first (matters with status='completed')
- Research Memo format: Question → Legal Position → Case Law → Analysis → Conclusions → Sources
- All research is audit_logged with action_type='research_completed'
- OSCOLA citation standard required for all case references

### Client Intake Form

- Route: GET/POST `/intake` — public-facing form, no auth required
- New matters created have status='pending_review'
- Telegram alert sent to @tatumdale on submission with matter reference
- Practice area inferred from matter type dropdown (Corporate/Employment/Commercial/IP/Data Privacy/Other)

### Precedent Library

- Route: GET `/precedents` and GET `/precedents/<matter_id>`
- Any completed matter can be saved as precedent via `POST /api/matters/<id>/precedent`
- Precedent entry includes: summary, outcome, RAG summary, key lessons
- Precedents are searchable by keyword (summary/key_lessons/summary) and practice area
- Precedent entries also appear in BAILII research results as internal precedent sources

### Deadlines

- Statutory deadlines auto-suggested on matter creation for known types:
  - Employment: 3 months from dismissal for tribunal
  - Contract: 6-year limitation period
  - Personal injury: 3 years
- Upcoming deadlines shown on dashboard (fetched from `/api/deadlines`)

### LLM Configuration

- Firm-level LLM config in firm_config.json → `llm` section
- Provider options: `cursor` (default, uses Cursor CLI), `openai`, `anthropic`
- Cursor CLI uses `agent --print --trust --yolo` for LLM calls — no API key needed
- To change model: update `model` field (e.g. `claude-4.6-opus-high-thinking`)
- To enable OpenAI: set `provider: "openai"`, add `api_key`
- To enable Anthropic: set `provider: "anthropic"`, add `api_key`

---

## Section 5 — Conflict of Interest Decision Framework

*Codified: 2026-03-31. This section governs all conflict of interest identification, escalation, and resolution for Acme Dale Legal Services.*

### What Triggers a Conflict Check

A conflict check runs:
1. **Automatically on matter creation** — when a new matter is submitted
2. **On demand** — `POST /api/matters/{id}/conflict-check`
3. **On request** — when AD-Intake processes an email from a new client

### Conflict Types Detected

| Type | Meaning | Automatic Action |
|---|---|---|
| `existing_client` | Client name matches existing entry in clients table | Flag |
| `existing_matter_client` | Client has an active matter already | Flag |
| `adverse_party` | Client name appears in another matter's adverse_parties field | Flag |

### The Three-Part Conflict Test (SRA Rules 6 & 11)

Before accepting any instruction, apply the three-part test:

**1. Is there an existing client relationship?**
Does the proposed client (or a connected person/entity) already have a relationship with the firm?

**2. Would acting create a conflict of interest?**
Would the firm's duty to the existing client(s) conflict with the duties owed to the proposed client, or would the firm be acting for two clients whose interests are adverse?

**3. Can the conflict be managed?**
If yes to (2), can it be managed with informed consent, information barriers, or other safeguards — or must the firm decline?

### Resolution Options

| Decision | When to Use | Effect on Matter |
|---|---|---|
| **CLEAR** | No conflict exists, or any conflict is purely theoretical and can be managed | Matter proceeds normally |
| **CONSENT** | Conflict exists but all affected clients have given informed written consent after full disclosure of the conflict and its implications | Matter proceeds with conditions documented |
| **DECLINE** | Conflict cannot be managed — acting would breach SRA Rules 6 or 11 | Matter closed. Firm declines to act. |

### Consent Process (When to Use)

Consent may be appropriate when:
- The conflict is between two former clients in unrelated matters
- All clients have received full written disclosure of the conflict
- All clients have given explicit written consent
- The firm is satisfied no conflict of duty arises

Consent must be:
- In writing (email or letter)
- Signed or explicitly accepted by all affected clients
- Filed in the matter record
- Reviewed by COLP before proceeding

### Decline Process (When to Use)

Decline must occur when:
- The conflict is between current clients with directly adverse interests in the same or a substantially related matter
- Acting would require the firm to act against a former client's confidential information
- The conflict cannot be managed to the satisfaction of the COLP

Decline letter must:
- Be sent promptly (don't delay unreasonably)
- Explain that the firm cannot act due to a conflict of interest
- NOT disclose the identity of the client causing the conflict (confidentiality survives)
- NOT provide any legal advice to the potential new client on how to proceed

### Conflict Involving a Related Entity (Tatumdale Case Study)

**The Tatumdale Ltd question (2026-03-31):**

Tatumdale Ltd = client of Acme Dale Legal Services
Acme Dale Ltd = potential commercial counterparty to Tatumdale Ltd (if contract signed)

If Acme Dale acts for Tatumdale Ltd AND Acme Dale Ltd is a related entity of Acme Dale, the conflict test:

1. **Existing client**: Tatumdale Ltd — YES
2. **Would acting create a conflict**: Acme Dale Ltd is a separate commercial entity. The firm (Acme Dale) is not the same as Acme Dale Ltd (commercial). But: if a solicitor within Acme Dale has confidential information from another matter that is relevant to the Tatumdale contract, acting would breach duty.
3. **Can it be managed**: YES — if the matters are entirely unconnected and the solicitor acting for Tatumdale has no conflict of duty.

**Decision**: CLEARED — separate entities, no conflict of duty. Document this reasoning in the conflict_log notes.

### Escalation

All conflict findings are escalated automatically to topic #7 (Acme Dale Telegram) via Telegram notification. The COLP (Tatum) reviews and resolves.

---

*Last updated: 2026-03-31*
