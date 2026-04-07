# SKILL.md — Matter Classifier

## name
matter-classifier

## description
Classify an incoming legal matter by practice area, service line, and tier. Use when receiving a new client instruction via email, chat, or form submission to determine which practice area skill to load and what tier of work applies.

## When to Use
- New client email or enquiry received
- Client intake form submitted
- Chat message containing a legal instruction
- Any time you need to determine what kind of legal work is being instructed

## How to Use This Skill
1. Read the incoming client communication and extract key facts
2. Apply the classification logic below to determine: practice_area, service_line, tier
3. Assess confidence for each dimension independently
4. If confidence is below 70% on any dimension, ask the client a specific clarifying question
5. Output a structured classification object

## Classification Taxonomy

### Practice Areas

| Code | Practice Area | Key Indicators |
|------|--------------|----------------|
| commercial-law | Commercial Law | Contracts for goods/services, B2B agreements, supply relationships, commercial terms |
| corporate-law | Corporate Law | Company formation, share purchases, M&A, incorporations, shareholder agreements |
| employment-law | Employment Law | Employment contracts, dismissals, TUPE, discrimination, settlement agreements |
| ip-law | Intellectual Property Law | Trade marks, patents, copyright, IP licensing, assignment, software disputes |
| data-protection | Data Protection & Privacy | GDPR, DPA 2018, data breaches, subject access requests, privacy notices |
| commercial-property | Commercial Property | Leases, purchases, sales, development, title, land registration |
| dispute-resolution | Dispute Resolution | Litigation, arbitration, mediation, pre-action letters, court claims |
| banking-finance | Banking & Finance | Loans, facilities, security, guarantees, refinancing |
| construction-law | Construction Law | JCT contracts, bespoke construction, adjudication, development agreements |
| immigration-law | Business Immigration | Visa applications, sponsor licences, right to work checks |
| employee-incentives | Employee Incentives | EMI options, share schemes, LTIP, bonus arrangements |

### Service Lines

| Code | Service Line | When to Use |
|------|-------------|--------------|
| drafting | Drafting | Client needs a document created or adapted |
| reviewing | Reviewing | Client needs a document analysed, red-lined, or assessed |
| negotiating | Negotiating | Client needs support in contract negotiations |
| advising | Advising | Client needs legal advice, opinion, or written note |
| precedents | Precedent & Process | Client needs a template, standard document, or process |

### Tier Definitions

**Tier 1 — Light / Routine**
- Standard form or simple precedent, minimal tailoring
- Single document, two parties, straightforward commercial terms
- No novel legal issues
- Low commercial risk

**Tier 2 — Standard / Bespoke**
- Fully tailored document or comprehensive review
- Multiple parties or material commercial complexity
- Some technical or regulatory elements
- Moderate commercial risk
- Requires substantive legal analysis

**Tier 3 — Complex / Strategic**
- Novel legal issues with no clear precedent
- Multiple parties, high value (>£50k), significant risk
- Regulatory complexity or cross-border elements
- Requires senior solicitor review before client-facing output
- **Must escalate to AD-Review before any output is sent**

## Classification Logic

### Step 1: Identify Practice Area

Read the client's communication and look for primary subject matter:

**Commercial Law signals:** "contract", "supplier", "customer", "agreement", "T&Cs", "terms of business", "goods", "services", "supply", "purchase", "sale", "licence", "distributorship", "framework agreement"

**Corporate Law signals:** "company formation", "incorporation", "shares", "acquisition", "purchase of shares", "M&A", "merger", "joint venture", "shareholders agreement", "director", " Articles of Association"

**Employment Law signals:** "employment contract", "worker", "employee", "dismissal", "HR", "redundancy", "TUPE", "settlement agreement", " tribunal", "discrimination", "harassment"

**IP Law signals:** "trade mark", "patent", "copyright", "intellectual property", "IP", "brand", "infringement", "licence of IP", "software"

**Data Protection signals:** "data", "GDPR", "privacy", "personal data", "data breach", "subject access request", "SAR", "DPA", "ICO", "cookies"

**Commercial Property signals:** "lease", "property", "land", "premises", "tenant", "landlord", "title", "transfer", "purchase of property"

**Dispute Resolution signals:** "dispute", "claim", "litigation", "court", "mediation", "arbitration", "pre-action", "breach of contract", "demand letter", "injunction"

**Banking & Finance signals:** "loan", "facility", "security", "guarantee", "mortgage", "refinancing", "LMA", "credit"

**Construction Law signals:** "construction", "JCT", "building", "contractor", "subcontractor", "RIBA", "development", "adjudication", "NEC"

**Immigration Law signals:** "visa", "immigration", "sponsor licence", "Skilled Worker", "right to work", "UKVI", "Home Office"

**Employee Incentives signals:** "EMI", "share options", "share scheme", "LTIP", "incentive", "equity", "shareholder", "SAYE"

If signals conflict (e.g., employment + commercial contract), use the **dominant** signal — what is the primary purpose of the transaction?

### Step 2: Identify Service Line

What is the client asking you to DO?

- "Can you draft..." or "we need an agreement" → **drafting**
- "Can you review..." or "can you look at..." or "red-line" or "advise on this contract" → **reviewing**
- "Can you negotiate..." or "can you support us in negotiations" → **negotiating**
- "What do you think about..." or "advise us on..." or "what are our options" → **advising**
- "Do you have a template..." or "send us your standard..." → **precedents**

A matter may involve more than one service line. Select the **primary** one for classification purposes.

### Step 3: Determine Tier

Apply the tier calibration based on the signals below:

**Tier 1 signals:** Standard form or minor tailoring only. Single document. Two parties. No unusual terms. Known commercial context (standard goods/services). Low value (<£10k exposure). No regulatory layer.

**Tier 2 signals:** Fully tailored. Multiple parties possible. Material commercial complexity. Some technical or regulatory elements. Moderate value (£10k–£50k). Non-standard commercial terms. Requires substantive analysis.

**Tier 3 signals:** Novel legal issues or unclear law. High value (>£50k). Multiple parties. Regulatory complexity. Cross-border elements. Significant risk to client. Novel industry or arrangement. Any threat of litigation. Any matter touching anti-money laundering, sanctions, or financial promotions.

## Confidence Scoring

Assess your confidence for each dimension separately:

- **Practice Area confidence:** How certain are you about the practice area?
- **Service Line confidence:** How certain are you about what the client needs?
- **Tier confidence:** How certain are you about the complexity level?

**Decision rules:**
- **>90% on all dimensions:** Proceed. Output classification. Auto-generate engagement letter.
- **70–90% on any dimension:** Flag the uncertainty in your output. Note what you're less certain about. Still proceed.
- **<70% on any dimension:** Stop. Ask the client one specific clarifying question. Do not proceed until you have clarity.

## Clarifying Questions (ask only one at a time)

If practice area unclear: "What is the primary subject matter of the work?"
If service line unclear: "Are you asking us to draft a new document, review an existing one, or provide advice?"
If tier unclear: "Is this a straightforward, standard matter or is there something more complex about it?"
If both PA and tier unclear: "Can you tell me a bit more about the context and what outcome you're looking for?"

## Output Format

Output the classification as a structured block at the end of your response:

```
MATTER CLASSIFICATION
──────────────────────────────────
Practice Area:   commercial-law (92%)
Service Line:     reviewing (87%)
Tier:             tier-2 (78%)
Primary Route:    AD-Review (reviewing, tier-2)
Confidence OK:   ✓ All dimensions >70%
Status:          PROCEED — generate engagement letter
──────────────────────────────────
```

If any dimension <70% confidence:
```
Tier:             tier-2 (?) (65%) ⚠️
Confidence OK:    ✗ Tier confidence below threshold
Status:          CLARIFY — ask client: [specific question]
──────────────────────────────────
```

## Escalation Triggers (always escalate to AD-Review)

- Tier 3 on any dimension
- Any matter involving >£50,000 at stake
- Any matter with potential litigation or court proceedings
- Any matter touching AML, sanctions, or regulatory reporting
- Client expresses dissatisfaction with AI-assisted process
- Novel legal issue with no clear precedent in the firm's knowledge base
- Any conflict of interest detected

## Metadata

```
practice_area: [see taxonomy table]
service_lines: [drafting, reviewing, negotiating, advising, precedents]
tiers: [tier-1, tier-2, tier-3]
escalates_to: AD-Review
legal_regime: England & Wales
regulator: Solicitors Regulation Authority (SRA)
```
