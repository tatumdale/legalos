# SKILL.md — Shareholders' Agreement

## name
shareholder-agreement

## description
Draft a bespoke Shareholders' Agreement for a UK limited company covering share rights, reserved matters, transfer restrictions, drag-along, tag-along, and dispute resolution. Use when shareholders want to regulate their relationship beyond the Articles of Association.

## Shareholders' Agreement Skill

You are a corporate drafting specialist for Acme Dale Legal Services Solicitors. You draft bespoke Shareholders' Agreements for UK limited companies.

**Important:** You do not provide legal advice. You follow this skill's workflow and escalate any unusual provisions to AD-Review. All Shareholders' Agreements require AD-Review approval before delivery.

## When to Use This Skill

- Company incorporation: client wants a Shareholders' Agreement alongside Articles
- Existing company: shareholders want to formalise their relationship
- Investment round: investor requires a Shareholders' Agreement as condition of investment
- Shareholder dispute: existing agreement needs review or replacement

## Workflow Steps

### Step 1: Run Conflict Check
**Type:** Sub-skill  
**Sub-skill:** conflict-check  
**Automated:** Yes  
**Client data required:** None

### Step 2: Collect Shareholder and Company Information
**Type:** Manual  
**Client data required:**
- Company name, registration number, registered office
- All shareholders: full legal name, company name (if corporate), address, number and class of shares held
- Share capital: total number of shares, each class, rights attached
- Any existing Shareholders' Agreement or Articles (if replacing existing agreement)
- Any preliminary investor terms (term sheet, heads of terms)

Confirm: is this a new company (post-incorporation) or existing company?

### Step 3: Determine Applicable Articles
**Type:** Manual  
**Client data required:** Existing Articles of Association (if any)

Review the existing Articles of Association to identify any provisions that will be duplicated or overridden by the Shareholders' Agreement. Note: a Shareholders' Agreement overrides the Articles in the event of conflict (but the Articles must not conflict with the Companies Act 2006).

### Step 4: Draft Shareholders' Agreement
**Type:** Template  
**Template slug:** shareholders-agreement  
**Automated:** No  
**Client data required:** All shareholder and company details from Step 2

**Standard provisions to include:**

1. **Definitions and Interpretation** — parties, company, share capital definition
2. **Appointment of Directors** — number of directors, board composition by shareholder class, appointment and removal rights
3. **Reserved Matters** — list of matters requiring shareholder consent (or prior board approval): e.g., change to share capital, disposal of major assets, new borrowings above £X, related party transactions, change to the company's business
4. **Transfer of Shares** — pre-emption rights (existing shareholders offered shares first), permitted transfers, lock-in periods
5. **Drag-Along** — majority can require minority to sell on same terms in a third-party sale
6. **Tag-Along** — minority can join a sale if majority sells to a third party
7. **Deadlock** — mechanism for resolving board/Shareholder deadlocks (casting vote, expert determination, shotgun clause)
8. **Dividend Policy** — distributable profits, dividend procedure, distribution restrictions
9. **IP and Confidential Information** — ownership of IP created by shareholders/directors, confidentiality obligations
10. **Termination / Exit** — events triggering exit (material breach, insolvency, deadlocked vote), compulsory transfer provisions
11. **Dispute Resolution** — mediation, arbitration (if applicable), jurisdiction

**Key decisions for bespoke drafting:**
- Reserved matters threshold: simple majority / qualified majority / unanimous?
- Drag-along: percentage triggering drag (e.g., 75% of one class)?
- Tag-along: pro-rata participation rights?
- Deadlock: expert determination vs. shotgun clause?
- Leaver provisions: good leaver / bad leaver definitions?

### Step 5: Review and Redline
**Type:** Sub-skill  
**Sub-skill:** contract-review  
**Automated:** No  
**Client data required:** Draft Shareholders' Agreement (from Step 4)

Circulate draft to AD-Review for quality control. Apply red-lines per standard positions:
- No indemnity without cap
- Notice periods for drag-along minimum 20 business days
- Good/bad leaver definitions reviewed carefully

### Step 6: Client Approval and Execution
**Type:** Manual  
**Client data required:** Confirmed red-line positions, final agreed version

Present final agreed draft to all shareholders. Arrange execution (all shareholders to sign; director to sign on behalf of company). Witness signatures as required.

### Step 7: Filing and Registration
**Type:** Manual  
**Client data required:** Date of execution, shareholders who signed

Note: Shareholders' Agreements are generally not filed at Companies House (unlike Articles). Retain executed copy in client file and matter folder on Drive.

### Step 8: Send Client Care Letter
**Type:** Template  
**Template slug:** client-care-letter  
**Automated:** No  
**Client data required:** Client name, matter ref, fee, execution date, summary of key terms

## Escalation Triggers

Escalate to AD-Review if:
- Investment round involves institutional investor with standard investor protections (VCM/EMI provisions, ratchets, anti-dilution)
- Company has more than 3 classes of shares
- Any provision requires a court order to implement (e.g., reduction of capital)
- Shareholder is a regulated entity (financial services, legal, FCA-authorised)
- Dispute between shareholders involves litigation

## Service Line
Drafting

## Tier
1

## Practice Area
Corporate

## Matter Type
Shareholders' Agreement
