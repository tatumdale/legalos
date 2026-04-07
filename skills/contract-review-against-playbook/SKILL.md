# SKILL.md - Contract Review Against Playbook

## name
contract-review-against-playbook

## description
Review a contract against your organizations negotiation playbook. Analyze each clause, flag deviations, generate redline suggestions, and provide business impact analysis.

## Contract Review Against Playbook
You review a contract against your organizations negotiation playbook.

**Important:** You do not provide legal advice. All analysis should be reviewed by qualified legal professionals.

## Workflow

### Step 1: Accept the Contract
Accept as file upload (PDF, DOCX), URL (CLM, cloud storage), or pasted text. Prompt if none provided.

### Step 2: Gather Context
1. Which side are you on? (vendor/supplier, customer/buyer, licensor, licensee, partner)
2. Deadline: when does this need to be finalized?
3. Focus areas: any specific concerns?
4. Deal context: deal size, strategic importance, existing relationship

### Step 3: Load the Playbook
Look for playbook in local settings defining standard positions, acceptable ranges, and escalation triggers.

If no playbook: inform the user, offer to create one or proceed with general commercial standards, label clearly.

### Step 4: Clause-by-Clause Analysis
Cover at minimum: limitation of liability, indemnification, intellectual property, data protection, term and termination, governing law and dispute resolution, and any other material clauses.

### Step 5: Flag Deviations

GREEN - Acceptable: aligns with or better than standard, minor commercially reasonable variations, no action needed.

YELLOW - Negotiate: outside standard but within negotiable range, common in market, requires attention but not escalation. Include specific redline language and fallback position.

RED - Escalate: outside acceptable range, material risk, requires senior counsel review. Include why it is a RED flag, market standard, business impact, escalation path.

### Step 6: Generate Redline Suggestions
For each YELLOW and RED: current language, suggested alternative, rationale, priority (must-have or nice-to-have).

### Step 7: Business Impact Summary
- Overall risk assessment
- Top 3 issues
- Negotiation strategy (which issues to lead with, what to concede)
- Timeline considerations

### Step 8: CLM Routing (if connected)
Recommend appropriate approval workflow, routing path, required approvals based on contract value or risk flags.

## Output Format
Structure as: Overall RAG Assessment, Business Impact Summary, Clause Analysis table (Clause | Playbook Position | Contract Language | RAG | Notes), RED Deviations with risk/market standard/escalation, YELLOW Deviations with suggested redlines, GREEN Clauses.
