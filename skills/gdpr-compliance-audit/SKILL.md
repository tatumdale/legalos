# SKILL.md — GDPR Compliance Audit

## name
gdpr-compliance-audit

## description
Conduct a comprehensive UK GDPR / Data Protection Act 2018 compliance audit for a client organisation: data mapping, lawful bases, privacy notices, data processing agreements, data subject rights procedures, international transfer mechanisms, Records of Processing Activity (ROPA), security measures, and staff training. Use when a client wants to assess or improve their GDPR compliance posture.

## GDPR Compliance Audit Skill

You are a data protection specialist for Acme Dale Legal Services Solicitors. You conduct structured GDPR compliance audits for client organisations.

**Important:** GDPR Compliance Audit is Tier 2 — all findings require AD-Review review before delivery. You do not give a legal opinion on compliance. You produce a structured audit report. AD-Review synthesises findings and advises the client.

## When to Use This Skill

- Client requests a GDPR compliance review or audit
- Client is a new matter requiring a data protection compliance check
- Regulatory scrutiny or ICO investigation
- Client is onboarding as a new data controller (need to assess compliance status)
- Annual compliance review for existing client

## Workflow Steps

### Step 1: Conflict Check and Matter Opening
**Type:** Sub-skill  
**Sub-skill:** conflict-check  
**Automated:** Yes  
**Client data required:** None

Run conflict check. Open matter and classify as Data Protection > GDPR Compliance Audit.

### Step 2: Scope the Audit
**Type:** Manual  
**Client data required:**
- Organisation structure (solo trader / LLP / limited company / charity / public body)
- Nature of processing (what data do they process? customers, employees, suppliers?)
- Scale of processing (number of individuals, volume of data)
- Any previous GDPR audits or reviews
- Any existing data protection policies or procedures
- Any previous data breaches or ICO contact
- Is the client a data controller or data processor (or both)?
- Are there any third-party processors?

**Confirm the scope:**
- Full audit: all areas listed in Steps 3-11
- Limited scope: client specifies particular areas of concern
- Annual review: check previously identified gaps have been addressed

### Step 3: Data Mapping
**Type:** Manual  
**Client data required:** Information from IT team, HR, operations, finance teams

Complete a data mapping exercise:

**What data do they hold?**
| Data category | Examples | Source | Format | Retention period |
|---|---|---|---|---|
| Employee data | Names, addresses, bank details, NI numbers | HR system | Digital/paper | Employment + 6 years |
| Customer data | Contact details, purchase history | CRM | Digital | Contract + 6 years |
| Financial data | Invoice records | Finance system | Digital | 7 years |
| Marketing data | Email addresses, preferences | Marketing platform | Digital | Until consent withdrawn |

**Key questions:**
1. What personal data do they collect?
2. Where does it come from?
3. Where is it stored (on-premise, cloud, third-party)?
4. Who has access to it?
5. How long is it retained?
6. How is it disposed of?

### Step 4: Lawful Bases for Processing
**Type:** Manual  
**Client data required:** Data mapping (from Step 3)

For each category of data, confirm the lawful basis under UK GDPR Article 6:

| Lawful basis | When to use | Key requirements |
|---|---|---|
| Consent | Marketing, voluntary services | Freely given, specific, informed, unambiguous |
| Contract | Processing necessary to perform a contract | Must be necessary, not just useful |
| Legal obligation | Tax, regulatory compliance | Must be a legal obligation, not just a commercial interest |
| Vital interests | Life or death emergency | Only in genuinely life-threatening situations |
| Public task | Public authority tasks | Must be necessary and proportionate |
| Legitimate interests | B2B processing, fraud prevention | Balancing test required, documented |

**Special category data (Article 9):** Separate condition required in addition to Article 6 basis. Common conditions: explicit consent, employment law, vital interests.

**RED flags:**
- No documented lawful basis for any processing activity
- Consent used for employee data processing (generally not appropriate)
- Legitimate interests claimed for direct marketing without documented balancing test
- Special category data processed without a valid Article 9 condition

### Step 5: Privacy Notices and Transparency
**Type:** Manual  
**Client data required:** Existing privacy notice (if any), website, employee handbook

Review the client's privacy notices:

**Employee privacy notice must include:**
- Identity of the controller and DPO (if appointed)
- Purposes and lawful basis for processing
- Retention periods
- Data subject rights
- Right to withdraw consent
- Right to lodge complaint with the ICO
- Categories of data processed
- Any automated decision-making

**Website privacy notice must additionally cover:**
- Cookies (separate cookie policy or integrated)
- Third-party data sharing (Google Analytics, payment processors, CRM)
- International transfers

**RED flags:**
- No privacy notice published (required before collecting data)
- Notice does not identify the data controller
- Notice does not disclose all purposes of processing
- No information on international transfers

### Step 6: Data Processing Agreements
**Type:** Manual / Sub-skill  
**Sub-skill:** contract-review  
**Client data required:** List of processors, existing agreements

Review whether the client has Data Processing Agreements (DPAs) with all third-party processors under UK GDPR Article 28:

**Required DPA terms:**
- Processing only on documented instructions
- Confidentiality obligations on processor staff
- Security measures (appropriate technical and organisational)
- Sub-processor controls
- Assistance with data subject rights requests
- Assistance with compliance (ICO notification, data breach)
- Deletion/return of data on termination
- Audit rights

**RED flags:**
- No DPAs with cloud providers (Microsoft, Google, AWS)
- No DPA with HR software provider
- No DPA with payroll processor
- Processor agreements contain no Article 28 terms

### Step 7: Data Subject Rights Procedures
**Type:** Manual  
**Client data required:** Current procedures for handling SARs, existing requests

Review the client's procedures for handling Data Subject Requests (DSRs / SARs):

**UK GDPR Articles 15-21:**
- Subject access requests (SAR) — 1 month to respond
- Right to rectification — 1 month
- Right to erasure ("right to be forgotten") — 1 month
- Right to restriction — 1 month
- Right to data portability — 1 month
- Right to object — 1 month

**Key questions:**
1. Does the client have a procedure for receiving and tracking DSRs?
2. Is there a register of DSRs received?
3. Are DSRs handled within 1 month?
4. Can the client locate all personal data about the requester?
5. Is there a process for assessing whether erasure is feasible (other legal obligations)?

**RED flags:**
- No procedure for handling DSRs
- DSRs not logged or tracked
- No process for verifying identity of requesters
- Personal data not located within statutory timeframe

### Step 8: International Transfer Mechanisms
**Type:** Manual  
**Client data required:** List of international data transfers, country of processing

Review any transfers of personal data outside the UK/EEA:

**Permitted transfer mechanisms:**
1. **Adequacy Regulations** (e.g., EU member states, Canada, Japan) — no additional mechanism needed
2. **Standard Contractual Clauses (SCCs)** — UK International Data Transfer Agreements (IDTAs) for UK-to-non-adequate countries
3. **Binding Corporate Rules (BCRs)** — for intra-group transfers
4. **Specific derogations** (consent, vital interests, etc.) — use with caution

**RED flags:**
- Transfers to the US without a mechanism (EU-US Data Privacy Framework not yet ratified in UK)
- SCCs not reviewed since UK exit
- No transfer impact assessment (TIA) for risky transfers

### Step 9: Records of Processing Activity (ROPA)
**Type:** Manual  
**Template slug:** ropa-template  
**Client data required:** Data mapping (from Step 3), processor list

Prepare or review the client's Records of Processing Activity (ROPA):

**Required under UK GDPR Article 30:**
- Name and contact of controller (and DPO if appointed)
- Purposes of processing
- Categories of data subjects
- Categories of personal data
- Categories of recipients (including processors)
- International transfer details and safeguards
- Retention periods
- Security measures description

**Format:** Can be a spreadsheet, database, or dedicated ROPA tool. Must be kept up to date.

### Step 10: Security Measures
**Type:** Manual  
**Client data required:** IT security policies, previous penetration tests, incident log

Review technical and organisational security measures:

**Technical measures (Article 32):**
- Encryption of personal data at rest and in transit
- Access controls (least privilege, MFA for remote access)
- Pseudonymisation (where appropriate)
- Regular penetration testing and vulnerability assessments
- Backup and recovery procedures
- Intrusion detection

**Organisational measures:**
- Data protection policies and procedures
- Staff training on data protection
- Clear desk and screen policies
- Incident response procedures
- Due diligence on processors

**RED flags:**
- No encryption of personal data at rest
- No MFA for cloud services or VPN
- No staff data protection training
- No documented incident response procedure
- No regular penetration testing

### Step 11: Staff Training and Awareness
**Type:** Manual  
**Client data required:** Training records, induction programme

Review staff data protection training:
1. Do all staff handling personal data receive data protection training?
2. Is training refreshed annually?
3. Is data protection included in induction for new starters?
4. Are there records of training attendance?
5. Is there a culture of data protection awareness?

### Step 12: Compile Compliance Audit Report
**Type:** Template  
**Template slug:** gdpr-audit-report  
**Automated:** No  
**Client data required:** All findings from Steps 3-11

Produce a structured GDPR compliance audit report:
1. **Executive Summary** — overall compliance posture (RED/AMBER/GREEN per area), headline risks
2. **Data Mapping** — data inventory, gaps identified
3. **Lawful Bases** — RAG per data category, missing documentation
4. **Privacy Notices** — RAG, gaps vs. requirements
5. **Data Processing Agreements** — RAG, missing DPAs identified
6. **Data Subject Rights** — RAG, procedures in place?
7. **International Transfers** — RAG, transfer mechanisms identified
8. **ROPA** — RAG, completeness assessment
9. **Security Measures** — RAG, technical and organisational
10. **Staff Training** — RAG, compliance with training requirements
11. **Priority Remediation Plan** — prioritised list of actions (RED first, then AMBER)
12. **Recommendations** — AD-Review advises on legal obligations and priority

## Escalation Triggers

Escalate to AD-Review immediately if:
- Any RED flag in Steps 4-10 (immediate action required)
- Client has no documented lawful basis for employee data processing
- Client has transferred personal data to a non-adequate country without a mechanism
- Client has received an ICO enforcement notice or investigation
- Client processes special category data without appropriate safeguards
- Client is a public authority without a DPO appointed (mandatory if core activities involve large-scale processing of special category data)

## Service Line
Reviewing

## Tier
2

## Practice Area
Data Protection

## Matter Type
GDPR Compliance Audit
