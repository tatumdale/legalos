# SKILL.md — Document Review & Gap Analysis

## Purpose

Produce consistent, structured legal document reviews using the AD Legal OS Gap Analysis format. Every review follows the same structure, making outputs predictable, comparable, and easy to navigate.

---

## When to Use This Skill

Use this skill when:
- A document is received for review (PDF, Word, or uploaded to the matter)
- AD-Drafting produces a document that needs quality-checking
- AD-Review is evaluating agent output
- Any legal document needs structured gap analysis against a framework

---

## Document Types & Frameworks

| Document Type | Primary Framework | Secondary |
|---|---|---|
| Privacy Policy | UK GDPR, DPA 2018, PECR | ICO Guidance |
| Terms of Service / Customer T&Cs | CRA 2015, UCTA 1977 | Consumer Rights Act 2015 |
| Software/SaaS Agreement | SGA 1979, CRA 2015 | SOGIT (Vendor playbook) |
| Employment Contract | Employment Rights Act 1996 | ACAS Code, IR35 (if contractor) |
| Settlement Agreement | Employment Rights Act 1996 | SOGIT, Equality Act 2010 |
| NDA / Confidentiality Agreement | Contract law | SOGIT (NDA playbook) |
| Shareholder Agreement | Companies Act 2006 | SOGIT |
| Data Processing Agreement | UK GDPR Art 28 | ICO DPA guidance |
| Cookie Policy | PECR | ICO Cookie guidance |
| Website Accessibility Statement | Equality Act 2010 | WCAG 2.1 |

---

## Review Input Checklist

Before starting, gather:

1. **Matter context** — GET /api/matters/{matter_id}/briefing
   - jurisdiction, client_type, deal_value_band, risk_appetite
   - matter-type-specific fields
2. **Document** — locate in matter record or Drive folder
   - If PDF: convert to Google Doc first (see PDF Ingestion below)
   - If Google Doc: open and read directly
3. **Applicable framework** — from document type table above
4. **Review lens** — from briefing or matter type (e.g. IR35, RAG weighting)

---

## Standard Gap Analysis Format

Every review output uses this structure:

### 1. Header Block

```
COMPLIANCE GAP ANALYSIS
[Document Title]
[Framework(s)]
Date: [YYYY-MM-DD]
Prepared for: [Client Name / Entity]
Document Assessed: [filename or URL]
Framework: [applicable law/regulation]
Disclaimer: This assessment is for informational purposes only...
```

### 2. Executive Summary

2–4 paragraphs:
- What the document is and who it belongs to
- What framework it was assessed against
- Overall condition (draft/final, gaps identified, general risk level)
- Risk breakdown: total gaps, then by colour band

**Risk colour bands:**
- 🔴 RED (score ≥16): Critical — must address before proceeding
- 🟠 ORANGE (score 9–15): High — address before publishing or signing
- 🟡 YELLOW (score 5–8): Medium — address promptly after critical items
- 🟢 GREEN (score <5): Low — address when convenient

**Risk Score = Severity × Likelihood**
- Severity: 1=Negligible, 2=Low, 3=Moderate, 4=High
- Likelihood: 1=Rare, 2=Unlikely, 3=Possible, 4=Likely, 5=Almost Certain

### 3. Risk Summary Table

A table with one row per gap. Columns:

| ID | Gap | Reference | Severity | Likelihood | Risk Level |
|---|---|---|---|---|---|
| GAP-01 | Purpose-to-Legal-Basis Mapping Missing | UK GDPR Art 13(1)(c) | 3 | 4 | ORANGE (12) |
| GAP-02 | ... | ... | ... | ... | ... |

Sort by Risk Level descending (RED first, then ORANGE, YELLOW, GREEN). Within each colour band, sort by score descending.

Number gaps sequentially: GAP-01, GAP-02... regardless of colour.

### 4. Detailed Findings

One section per gap, in Risk Summary order. Each section is a sub-table or structured block:

```
[ID]: [Gap Title]
Legal Reference: [specific article/section/regulation]
Policy/Document Section: [where found in document, or "Not present"]
Severity: [N] – [label]
Likelihood: [N] – [label]
Risk Score: [N] ([COLOUR])
Finding: [2–3 sentences. What is the gap? Why does it matter?]
Recommendation: [Specific, actionable. What should the client do? Include example language where helpful.]
```

### 5. Prioritised Remediation Plan

A summary table grouped by priority band:

```
Priority 1: Address Before Proceeding (RED / ORANGE)
| ID | Gap | Action | Effort |
Priority 2: Address Promptly (YELLOW)
| ID | Gap | Action | Effort |
Priority 3: Address When Convenient (GREEN)
| ID | Gap | Action | Effort |
```

Effort labels: Trivial / Low / Medium / Medium–High / High

### 6. Outside Counsel Consideration

2–4 sentences. Should this matter be escalated to a human solicitor?
Consider: complexity, volume of RED/ORANGE gaps, client already live, international transfer issues, novel legal questions.

---

## Review Lenses

Apply these depending on document type and briefing context:

### IR35 Lens (for contractor agreements)
- Worker status test applied
- Personal service company indicator
- Control, substitution, mutuality of obligation assessed
- IR35 status: Inside IR35 / Outside IR35 / Not applicable
- Recommended mitigation clauses if Inside IR35

### Clause Weighting Lens (for commercial contracts)
Rate each material clause:
| Clause | Risk | Weight | Notes |
For: exclusion of liability, limitation of liability, indemnification, termination, IP ownership, governing law

Weight: HIGH (uncapped or >£100K exposure) / MEDIUM / LOW

### RAG Framework (from commercial-law skill)
Apply RED/AMBER/GREEN to each major clause:
- RED: void exclusion, uncapped indemnity, termination-at-will + non-compete
- AMBER: questionable clauses requiring negotiation
- GREEN: balanced, client-favourable clauses

---

## PDF Ingestion Workflow

When a PDF document is received:

1. **Upload to Google Drive** — save to the matter's Drive folder
2. **Convert to Google Doc** — right-click → Open with → Google Docs, OR use `gog drive import`
3. **Copy link to matter record** — note the Google Doc URL in the matter's output field
4. **Read the Google Doc** — use gog or open directly for review

If conversion fails (scanned PDF, image-based):
- Use OCR or describe the limitation in the review header
- Note: "Document received as scanned PDF. Text extraction attempted but accuracy not guaranteed."

---

## Document Generation

When producing a new document (e.g. privacy policy, terms, DPA):

1. Start from the **appropriate template** in Google Drive
2. Populate using matter context (client name, service, jurisdiction from briefing)
3. Apply the **briefing risk appetite**:
   - Conservative → err on side of disclosure, detailed rights
   - Balanced → standard commercial position
   - Commercial → streamlined, maximum flexibility for client
4. Save as Google Doc in the matter's Drive folder
5. Link in the matter record
6. If client requests Word/PDF: File → Download → appropriate format

---

## Output Delivery

- **Save** to the matter's Google Drive folder
- **Link** in the matter record (output field or notes)
- **Email** to client if instructed (via AD-Drafting / AD-Review)
- **Attach** to audit log entry

Never output a review purely to chat. Always persist to Drive and link to the matter.

---

## Quality Standards

- Every gap must have a specific legal reference (Article/Regulation/section)
- Every finding must include a concrete recommendation
- Recommendations should include example clause/language where helpful
- Risk scores must be calculated (Severity × Likelihood) and shown
- Table of contents / gap IDs must be consistent (GAP-01, GAP-02...)
- Executive summary must state total gap count and risk breakdown
- No gap is marked RED without a specific, actionable remediation
