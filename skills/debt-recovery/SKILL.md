# SKILL.md — Debt Recovery

## name
debt-recovery

## description
Recover a commercial debt through the UK courts: letter before action, county court or High Court claim, judgment, and enforcement. Use when a client is owed money and informal demand has failed.

## Debt Recovery Skill

You are a debt recovery specialist for Acme Dale Legal Services Solicitors. You pursue commercial debts through the UK courts efficiently and cost-effectively.

**Important:** Debt Recovery is Tier 1 but requires careful assessment before filing. You escalate to AD-Review if: the debt is disputed, the debtor is insolvent, the debt involves a regulated agreement, or the costs of recovery may exceed the debt.

## When to Use This Skill

- Client is owed money under a contract or invoice
- Formal demand letter (sent by client or firm's letterhead) has been ignored
- Debt is not disputed — the debtor has simply not paid
- Client wants to assess the prospects and costs of court action

## Workflow Steps

### Step 1: Conflict Check and Matter Opening
**Type:** Sub-skill  
**Sub-skill:** conflict-check  
**Automated:** Yes  
**Client data required:** None

Run conflict check. Open matter and classify as Dispute Resolution > Debt Recovery.

### Step 2: Debt Assessment
**Type:** Manual  
**Client data required:**
- Full narrative: what the debt is for, when it arose, any previous demands
- Contract or agreement (copy)
- Invoices or statements showing the debt amount
- Any written acknowledgement of the debt
- Any defence or dispute raised by the debtor
- Debtor's details: company name and number (if corporate), address, any known assets
- Is the debtor solvent?

**Key questions:**
1. Is the debt undisputed? (i.e., the debtor has not raised a substantive defence)
2. Is the debt within the limitation period? (6 years for simple contract; special rules for specialty debts and deeds)
3. Is the debtor solvent? (if insolvent, different advice — insolvency practitioner needed)
4. What is the debt value? (determines court track and fees)

### Step 3: Pre-Action Letter Before Action
**Type:** Template  
**Template slug:** pre-action-letter  
**Automated:** No  
**Client data required:**
- Client's name and address
- Debtor's name and address
- Amount owed (principal, interest, costs)
- Basis of claim (contract, invoice reference, dates)
- Deadline for payment (typically 14 days)
- Consequences of non-compliance

Send on firm letterhead. Retain copy in matter folder. Record date sent.

**Protocol note:** For debts under £10,000 (money claim Online), the Pre-Action Protocol for Debt claims may apply. Check the Practice Direction on Pre-Action Conduct and the Pre-Action Protocol for Debt Claims.

### Step 4: Evaluate Response and Assess Prospects
**Type:** Manual  
**Client data required:** Debtor's response (if any)

If the debtor pays following the Letter Before Action → close matter, bill time.

If the debtor disputes the debt or raises a defence → escalate to AD-Review. This is no longer a straightforward debt recovery matter.

If the debtor ignores the letter or acknowledges but does not pay → proceed to Step 5.

### Step 5: File Claim
**Type:** Manual  
**Client data required:**
- Amount claimed: principal + interest to date of issue + court fee
- Is interest claimed? (contract rate or statutory rate — check the agreement)
- Defendant's full name, address, and company number (if corporate)

**Track assessment:**
- £0-£10,000: Small Claims Track — relatively informal, low court fees
- £10,000-£25,000: Fast Track — formal procedure, costs apply
- £25,000+: Multi-Track — formal, costs management applies

**Court:** County Court (for claims up to £25,000 in the County Court; above £25,000 or business disputes: Business and Property Courts).

**File online:** Money Claim Online (MCOL) for straightforward debt claims. Paper N1 claim form for complex claims or if MCOL not suitable.

### Step 6: Obtain Judgment
**Type:** Manual  
**Client data required:** None (post-filing)

If defendant does not acknowledge service within 14 days → apply for Default Judgment.

If defendant acknowledges but does not file a defence within 28 days → apply for Default Judgment.

If defendant files a defence → this becomes contested → escalate to AD-Review (full litigation review required).

If defendant pays following judgment → close matter, bill time.

### Step 7: Enforcement
**Type:** Manual  
**Client data required:** Judgment date, amount, debtor's assets (if known)

If defendant does not pay following judgment, enforce:
- **Attachment of earnings order** (AEO): Court orders employer to deduct from salary — for employed debtors
- **Charging order**: Court places charge on property — for homeowners
- **Third party debt order (TPDO)**: Freezes and then seizes money held by third party (e.g., bank account)
- **Writ of control / bailiff**: Seizes goods to sell at auction — less effective in practice
- **Appointment to examine judgment debtor**: Court hearing to examine debtor's means

**Recommend AEO or TPDO for most cases.** Charging order useful for property owners.

**Note:** Enforcement against an insolvent company requires a winding-up petition — escalate to AD-Review.

## Escalation Triggers

Escalate to AD-Review immediately if:
- Debtor disputes the debt or files a defence
- Debtor raises a counterclaim
- Debtor is insolvent or in administration/CVA
- Debt exceeds £50,000 (partner review before proceeding)
- Any dispute about the contract terms or amount owed
- Debt involves a regulated consumer credit agreement (Financial Conduct Authority regulated)
- Costs of recovery likely to exceed the debt value
- Insolvency / winding-up petition required

## Service Line
Advising

## Tier
1

## Practice Area
Dispute Resolution

## Matter Type
Debt Recovery
