# SKILL.md - Generate Response from Templates

## name
generate-response-form-templates

## description
Generate a response to a common legal inquiry using configured templates.

## Workflow

### Inquiry Types
dsr (data subject request), hold (litigation hold), vendor (vendor question), nda (NDA request), privacy (privacy inquiry), subpoena, insurance, custom.

### Step 1: Identify Inquiry Type
Accept the inquiry type. Show categories if ambiguous.

### Step 2: Load Template
Look in local settings. If not found: offer to create one or provide reasonable default.

### Step 3: Check Escalation Triggers
DSR triggers: minor data, regulatory authority, litigation hold, employee dispute, fishing expedition.
Hold triggers: criminal liability, overbroad scope, prior holds.
Vendor triggers: dispute, litigation threat, binding commitment risk.
NDA triggers: competitor, government info, M&A context, unusual subject matter.
If trigger: alert user, recommend counsel review.

### Step 4: Gather Details
Prompt for requester name, type, regulation, deadline (DSR); matter, custodians, scope, outside counsel (Hold); vendor, agreement, question (Vendor); counterparty, purpose, mutual/unilateral (NDA).

### Step 5: Generate Response
Populate template. Professional tone, complete legal elements, specific dates, clear next steps, disclaimers. Present for review before sending.

### Step 6: Template Creation
If no template: ask inquiry type, key elements, audience. Draft with placeholders, include escalation triggers, present for review, save.

## Response Categories

### Data Subject Requests
Sub-categories: acknowledgment, identity verification, fulfillment, partial/full denial, extension.
Key: regulation reference, timeline, identity verification, data subject rights, supervisory authority complaint right.

### Discovery Holds
Sub-categories: initial notice, reminder/reaffirmation, modification, release.
Key: matter reference, preservation obligations, scope, spoliation prohibition, acknowledgment.

### Privacy Inquiries
Cookie/tracking, privacy policy, data sharing, child data, cross-border transfers.

### Vendor Legal Questions
Contract status, amendment requests, compliance certifications, audit requests, insurance certificates.

### NDA Requests
Sending standard form, accepting with markup, declining, renewal.

### Subpoena/Legal Process
Acknowledgment, objection, extension request, compliance cover letter.
