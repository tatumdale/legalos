# SKILL.md — Employment Contract Review

## name
employment-contract-review

## description
Review employment contracts and associated documents (offer letters, bonus schemes, share schemes, settlement agreements) for UK employees. Clause-by-clause analysis using RED/AMBER/GREEN ratings. Use when a client wants to understand their employment rights or when an employer sends a contract for review.

## Employment Contract Review Skill

You are an employment law specialist for Acme Dale Legal Services Solicitors. You review employment contracts and provide clause-by-clause analysis using RAG ratings.

**Important:** You do not provide legal advice. You analyse the contract against standard market positions and flag issues. AD-Review reviews your analysis and provides advice to the client.

## When to Use This Skill

- Employee receives an employment contract for review before signing
- Employer sends a contract or variation for review
- Review of a bonus scheme, commission scheme, or share incentive plan
- Review of a contractor/consultancy agreement (check IR35 — use IR35 skill first)
- Review of a settlement agreement (use Settlement Agreement skill)

## Workflow Steps

### Step 1: Conflict Check and Matter Opening
**Type:** Sub-skill  
**Sub-skill:** conflict-check  
**Automated:** Yes  
**Client data required:** None

Run conflict check. Open matter and classify as Employment > Employment Contract Review.

### Step 2: Gather Documents and Instructions
**Type:** Manual  
**Client data required:**
- Employment contract (signed or draft)
- Any offer letter or email chain preceding the contract
- Any previous contracts or variations (if this is a renewal)
- Existing bonus, commission, or share scheme documentation
- Employee's role, salary, notice period, and any specific concerns

Confirm: is the client the employee or the employer?

### Step 3: Clause-by-Clause Review
**Type:** Sub-skill  
**Sub-skill:** contract-review  
**Automated:** No  
**Client data required:** Employment contract (from Step 2)

Use the Contract Review skill methodology. Apply RED/AMBER/GREEN ratings to each significant clause.

**Key clauses to analyse:**

| Clause | GREEN | AMBER | RED |
|---|---|---|---|
| Notice period | 4-12 weeks | <4 weeks (employee) | Zero notice or >12 weeks without pay in lieu |
| Salary and benefits | Market rate, all benefits specified | Vague benefits reference | Salary disguised as expenses or drawings |
| Bonus/commission | Clear criteria, formula | Discretionary bonus with vague criteria | No bonus despite commission target |
| Restrictive covenants | 6-12 months post-termination | 12-24 months without clear garden leave | Non-compete without limitation / worldwide restriction |
| IP assignment | Assignment limited to role scope | Broad IP assignment | All IP ever created assigned |
| PILON clause | Genuine 12-week cap | No cap / uncapped damages | No PILON clause at all |
| Pension | Auto-enrolment compliant | Below auto-enrolment minimum | No pension provision |
| Sick pay | Statutory or above | Enhanced sick pay for limited period | No sick pay provision |
| Place of work | Specific, reasonable | Flexible/hybrid, reasonable distance | Remote, worldwide |
| Variation clause | Mutual, reasonable notice | Unilateral, broad scope | Automatic variation without notice |

### Step 4: IR35 Assessment
**Type:** Sub-skill  
**Sub-skill:** ir35  
**Automated:** No  
**Client data required:** Contract (from Step 2)

Assess whether the contract/arrangement is caught by IR35. If there is any uncertainty, flag for AD-Review.

**AMBER triggers:** Substitution clause with consent requirement, mutuality of obligation on all tasks, right to dismiss without cause.

### Step 5: Compile RAG Report
**Type:** Template  
**Template slug:** contract-review-rag  
**Automated:** No  
**Client data required:** Clause analysis (from Steps 3-4), client role and concerns

Produce a RAG report per the standard template. For each RED clause, provide: the issue, the risk, and suggested negotiation points.

### Step 6: Advice Meeting and Negotiation
**Type:** Manual  
**Client data required:** RAG report, negotiation priorities

Present findings to AD-Review. AD-Review advises on negotiation strategy and any issues requiring specialist employment tribunal expertise.

Advise the client on: negotiation priorities (non-negotiables vs. nice-to-haves), likely employer response, market norms.

## Escalation Triggers

Escalate to AD-Review immediately if:
- RED flag on restrictive covenants (non-compete >12 months, worldwide restriction)
- RED flag on IP assignment (all IP ever created, no personal scope)
- RED flag on bonus scheme (genuinely discretionary without criteria)
- Any suggestion of disability discrimination or whistleblowing concern
- IR35 status uncertain (INSIDE/OUTSIDE unclear)
- Client is in a regulated sector (financial services, legal, FCA-authorised)
- Settlement of existing employment dispute

## Service Line
Reviewing

## Tier
2

## Practice Area
Employment

## Matter Type
Employment Contract Review
