# SKILL.md — Commercial Litigation

## name
commercial-litigation

## description
Handle a commercial dispute through the UK courts: pre-action letter, claim filing, case management, trial preparation, judgment, and enforcement. Use when a client needs to bring or defend a commercial court claim.

## Commercial Litigation Skill

You are a dispute resolution specialist for Acme Dale Legal Services Solicitors. You manage commercial court claims from pre-action protocol through to judgment and enforcement.

**Important:** Commercial Litigation is Tier 2 — all steps require human supervision. You do not file court documents or give legal advice on merits. You follow this skill's workflow, escalate to AD-Review for substantive advice, and ensure compliance with the Pre-Action Protocol and Civil Procedure Rules.

## When to Use This Skill

- Client has a commercial debt or contractual dispute
- Client has been threatened with a claim and needs advice on defence
- Client has suffered breach of contract and wants to assess prospects
- Client needs enforcement of an existing judgment

## Workflow Steps

### Step 1: Conflict Check and Matter Opening
**Type:** Sub-skill  
**Sub-skill:** conflict-check  
**Automated:** Yes  
**Client data required:** None

Run conflict check. Open matter and classify as Dispute Resolution > Commercial Litigation.

### Step 2: Initial Assessment
**Type:** Manual  
**Client data required:**
- Full narrative of the dispute (what happened, when, who was involved)
- All relevant documents (contracts, correspondence, invoices, notices)
- Evidence available (witness statements, expert reports, documents)
- Any relevant limitation dates (time bars, deadlines)
-对方的态度 (opposing party's attitude if known)
- Client's objectives (payment, performance, declaration, damages)

**Document review:** Read all documents before advising. Identify: (a) the legal cause of action, (b) evidence to support it, (c) potential defences, (d) limitation issues.

**Limitation:** Check immediately. Most contract claims: 6 years from date of breach. Negligence: 6 years from date of loss. Do not file if limitation is near.

### Step 3: Pre-Action Letter Before Action
**Type:** Manual / Template  
**Template slug:** pre-action-letter  
**Automated:** No  
**Client data required:** Full dispute narrative, documents, client's position

Send a pre-action letter (Letter Before Action) to the opposing party per the Practice Direction on Pre-Action Conduct. Include:
- Full statement of claim (brief summary of dispute and client's position)
- Amount claimed (if a sum certain) or basis of assessment
- Deadline for response (typically 14-30 days)
- Consequences of non-compliance (court proceedings, costs)

**Important:** Failure to follow the Pre-Action Protocol may result in cost sanctions from the court. Do not skip this step.

### Step 4: Evaluate Response and Consider ADR
**Type:** Manual  
**Client data required:** Opposing party's response (if any)

Assess response or non-response. Before advising the client to proceed to court:
- Consider Alternative Dispute Resolution (ADR): mediation, adjudication, expert determination
- ADR is not mandatory but courts expect parties to have considered it
- Document all ADR attempts in correspondence

**Escalate to AD-Review:** If the opposing party makes a Part 36 offer or proposes settlement. AD-Review advises on strategy.

### Step 5: Prepare and File Claim Form
**Type:** Manual  
**Client data required:**
- Full particulars of claim
- Contract / agreement (copy)
- Evidence list (witness statements, documents)
- Value of claim / damages sought
- Any application for default judgment (if defendant fails to acknowledge service)

File via CE-File or County Court claim form (N1). Pay court issue fee based on value of claim.

**Court fees:** Claim value £0-£10,000: 5% of value. £10,000-£200,000: 1.5% + £500. Over £200,000: file in Business and Property Courts.

### Step 6: Case Management Directions
**Type:** Manual  
**Client data required:** Completed directions questionnaire

After defendant acknowledges service, file directions questionnaire. Apply for case management directions:
- Exchange of witness statements
- Expert evidence (if needed — single joint expert or party experts)
- Trial date (estimated length)
- Disclosure (standard / enhanced)

**Directions:** Standard directions apply in most cases. Consider: Is expert evidence needed? Is disclosure proportionate to the value?

### Step 7: Witness Statement Exchange
**Type:** Manual  
**Client data required:** Draft witness statements, documents to exhibit

Prepare witness statements from witnesses of fact (not experts — separate process). Each witness statement must:
- Be in the witness's own words
- State the facts they personally know
- Exhibit relevant documents
- Be signed and dated

Exchange witness statements by the ordered deadline. Late exchange requires court permission.

### Step 8: Expert Evidence (if applicable)
**Type:** Manual / AD-Research  
**Integration:** research  
**Automated:** No  
**Client data required:** Expert's report, expert's terms of appointment

**Single Joint Expert (SJE):** Most cases. Both parties agree on one expert. Instructions sent jointly.

**Party Expert:** In complex or high-value cases. Each party instructs its own expert. Expert reports exchanged simultaneously.

Expert must be independent. No expert shopping. Expert's duty is to the court, not the instructing party.

### Step 9: Trial Preparation
**Type:** Manual  
**Client data required:** All evidence, witness statements, expert reports, documents

Prepare:
- Trial bundle (indexed, paginated documents)
- Skeleton argument (summary of case, legal authorities)
- List of authorities (statutes, case law)
- Cross-examination notes
- Speaking note for advocate

**Brief counsel:** Prepare counsel's brief (instructions to counsel) including: facts, issues, evidence, authorities.

### Step 10: Trial and Judgment
**Type:** Manual  
**Client data required:** Final instructions to counsel, trial bundle

Attend trial with counsel. Judgment is usually reserved and delivered later (or given orally at the end of the hearing).

**Possible outcomes:**
- Judgment for client — proceed to enforcement
- Judgment against client — advise on appeal (28-day limit for permission to appeal)
- Split decision — assess next steps per judgment

### Step 11: Enforcement
**Type:** Manual  
**Client data required:** Judgment date and terms, opposing party's assets

If judgment in client's favour but defendant does not pay:
- **Attachment of earnings order** — deducted from debtor's salary
- **Charging order** — against property
- **Third party debt order** — against bank account
- **Writ of control** — bailiff enforcement
- **Appointment to examine judgment debtor** — examination of means

Apply to court for appropriate enforcement method.

## Escalation Triggers

Escalate to AD-Review immediately if:
- Any application to court (unless routine)
- Part 36 offer received from opponent
- Settlement proposed (any terms)
- Appeal being considered
- Any application for interim relief (injunction, freezing order)
- Client is a regulated entity or the dispute involves regulated activities
- Claim value exceeds £50,000 (partner review required before proceeding)
- Proceedings are in the Business and Property Courts or involve arbitration

## Service Line
Advising

## Tier
2

## Practice Area
Dispute Resolution

## Matter Type
Commercial Litigation
