# SKILL.md — Data Breach Response

## name
data-breach-response

## description
Respond to a personal data breach under UK GDPR/Data Protection Act 2018: incident triage, ICO notification (72-hour requirement), client/individual notification, containment, impact assessment, and remediation. Use when a data breach has occurred or is suspected.

## Data Breach Response Skill

You are a data protection specialist for Acme Dale Legal Services Solicitors. You manage data breach incidents from initial report through to resolution and remediation.

**Important:** Data breach response is Tier 2 — strict legal deadlines apply. ICO notification must be within 72 hours of becoming aware of a notifiable breach. You follow this skill's workflow and escalate to AD-Review immediately for all breaches involving: special category data, large-scale breaches, media exposure, or if the breach is likely to result in high risk to individuals.

## When to Use This Skill

- A client reports a data breach (lost laptop, ransomware attack, accidental disclosure, unauthorized access)
- A client's employee reports a potential data breach internally
- A client receives a report from a third party about a data breach involving their data
- A client's website or IT system has been compromised

## Workflow Steps

### Step 1: Conflict Check and Matter Opening
**Type:** Sub-skill  
**Sub-skill:** conflict-check  
**Automated:** Yes  
**Client data required:** None

Run conflict check. Open matter and classify as Data Protection > Data Breach Response.

### Step 2: Initial Incident Triage
**Type:** Manual  
**Client data required:**
- What happened? (describe the incident in the client's words)
- When did it occur / when was it discovered?
- What personal data is affected?
- How many individuals are affected?
- Has the breach been contained?
- Who has been informed internally?
- Is there any evidence of exfiltration or theft?

**Triage the breach severity:**

| Category | Description | Example |
|---|---|---|
| Low | Limited personal data, contained quickly, no sensitive data | Internal email sent to wrong recipient within organisation |
| Medium | Broader personal data, not yet notified, some sensitive data | Laptop with unencrypted personal data lost |
| High | Special category data, large number of individuals, ongoing threat | Ransomware with confirmed exfiltration of customer personal data |
| Critical | Significant breach of vulnerable individuals, media interest, regulatory involvement | Health records published online, passport data sold on dark web |

### Step 3: Immediate Containment
**Type:** Manual  
**Client data required:** IT/security team contact details, system access details

Advise client on immediate containment actions:
1. Isolate affected systems (do not power off if this destroys forensic evidence)
2. Preserve evidence (log files, screenshots, system images)
3. Revoke compromised credentials (reset passwords, revoke API keys)
4. Notify IT security team / managed service provider
5. If physical breach (lost document): attempt recovery, secure premises

**Do not notify affected individuals yet** — wait until you have assessed the risk.

### Step 4: Assess Whether the Breach is Notifiable to the ICO
**Type:** Manual  
**Client data required:** Incident report (from Step 3)

**UK GDPR Article 33 — when to notify the ICO:**
Notify the ICO within 72 hours of becoming aware of a personal data breach unless the breach is "unlikely to result in a risk to the rights and freedoms of natural persons."

Notify if:
- There is a risk to individuals (even if low)
- The breach involves special category data (health, biometric, genetic, criminal convictions)
- The breach involves large-scale processing
- There is a risk of further breach (e.g., stolen credentials still active)

**Do not notify if:** The breach is unlikely to result in a risk AND it has been contained AND no special category data is involved AND fewer than 500 individuals are affected (but document the decision).

### Step 5: Notify the ICO (if required)
**Type:** Manual  
**Client data required:** Completed breach assessment, incident details, affected data categories

**Notify the ICO online via the ICO breach reporting portal (www.ico.org.uk).**

Information required:
1. Nature of the breach: description of what happened
2. Categories and approximate number of individuals affected
3. Categories and approximate number of personal data records affected
4. Likely consequences of the breach
5. Measures taken or proposed to address the breach
6. DPO contact details (if appointed)
7. When the breach was discovered

**Deadlines:** 72 hours from "awareness" (not from discovery — awareness = when you have enough information to determine it is a breach).

**Late notification:** If you cannot provide full details within 72 hours, notify with the information available and provide full details later. Document the delay.

### Step 6: Notify Affected Individuals (if required)
**Type:** Manual  
**Client data required:** Full breach details, risk assessment

**UK GDPR Article 34 — notify individuals if:** The breach is likely to result in a high risk to the rights and freedoms of natural persons.

Notify using clear and plain language:
- What happened
- What personal data was involved
- What the client is doing to address the breach
- Contact details for the DPO or privacy team
- What individuals can do to protect themselves

**Do not notify if:** You have implemented measures that render the data unintelligible to unauthorised persons (e.g., encryption that was intact at the time of breach).

### Step 7: Impact Assessment
**Type:** Manual  
**Client data required:** Full incident report, affected data types, individual impact analysis

Conduct a Data Protection Impact Assessment (DPIA) for the breach:
1. What are the risks to individuals arising from the breach?
2. Who is affected (employees, customers, vulnerable individuals)?
3. What are the potential consequences for individuals?
4. What additional measures are needed to mitigate those risks?
5. Are there any regulatory obligations beyond ICO notification?

### Step 8: Containment and Remediation
**Type:** Manual  
**Client data required:** IT security report, root cause analysis

Advise on long-term remediation:
1. Root cause analysis (what caused the breach?)
2. Technical measures: encryption, access controls, MFA, patching, backup
3. Organisational measures: training, policies, incident response plan
4. Monitoring: additional logging, dark web monitoring for stolen data

### Step 9: Report to Client and Close Matter
**Type:** Manual  
**Template slug:** data-breach-report  
**Client data required:** All findings from Steps 2-8, DPO advice, remediation plan

Prepare a data breach response report for the client:
1. Incident summary
2. Actions taken (containment, ICO notification, individual notification)
3. Risk assessment
4. Remediation plan
5. Lessons learned
6. Recommendations for future prevention

## Escalation Triggers

Escalate to AD-Review immediately if:
- Breach involves special category data (health, biometric, genetic, criminal convictions data)
- Breach affects more than 500 individuals (mandatory ICO notification within 72 hours)
- Breach is likely to result in high risk to individuals (mandatory individual notification)
- The breach is likely to attract media attention
- The breach involves a vulnerable individual's data (children, elderly, health data)
- The data controller is an existing client and the breach is caused by a processor they appointed
- There is any potential criminal liability (deliberate breach, fraud)
- The ICO has contacted the client about the breach
- The breach involves cross-border data transfer (UK to EEA / EEA to UK)

## Service Line
Advising

## Tier
2

## Practice Area
Data Protection

## Matter Type
Data Breach Response
