# AD Legal OS

AI-powered legal practice management for Acme Dale, running on OpenClaw. Built with Flask + SQLite, managed by a 6-agent AI team.

**Live:** http://localhost:5050

---

## What It Does

- **CRM** -- contacts, companies, pipeline, products, activities
- **Matter management** -- intake, classification, conflict check, document production
- **Structured Briefing Interview** -- multi-step wizard collecting jurisdiction, client type, deal value, risk appetite, and matter-type-specific context before work begins
- **Standardised Document Review** -- gap analysis format (GAP-01, GAP-02...) with risk scoring (Severity x Likelihood = RED/ORANGE/YELLOW/GREEN), applicable across all document types
- **6-agent AI team** -- AD-Intake, AD-Review, AD-Corporate, AD-Research, AD-Drafting, AD-Partner
- **19 legal skill definitions** -- commercial law, contract review, employment, M&A, IP, data protection, document-review, etc.
- **Google Drive integration** -- per-matter folders via gog CLI
- **Skills framework** -- AgentSkills loaded from skills/ directory at startup

---

## Prerequisites

| Dependency | Version | Install |
|---|---|---|
| Python | 3.10+ | `brew install python3` |
| Flask | 3.x | `pip install flask` |
| gog CLI | -- | `brew install gog` |
| Google account | tatum@tatumdale.com | `gog account add` |

**Python dependencies are minimal -- only Flask is required:**

```bash
pip install flask
```

All other imports are from the Python standard library.

---

## Quick Start

```bash
git clone https://github.com/tatumdale/legalos.git ~/ad-legal-os
cd ~/ad-legal-os
pip install flask
gog account add
python3 app.py
```

App starts at **http://localhost:5050**

---

## Project Structure

```
legalos/
  app.py                      Flask app -- all routes, DB schema, agent logic
  drive_helpers.py            Google Drive helpers (gog CLI wrapper)
  legal_os/                   Core modules: analyzer, billing, dms, llm, research
  skills/                     19 AgentSkill definitions
  templates/                  Flask templates (Jinja2)
  workspace-ad-*-SOUL.md      Agent system prompts
  workspace-ad-*-AGENTS.md    Agent task definitions
  JUDGEMENT.md                SRA compliance framework
  REQUIREMENTS.md             Feature specification + build status
```

---

## Database

**SQLite** -- file: `db/ad_matters.db` (created automatically on first run, gitignored).
Seed data (5 sample matters) loaded on first run.

---

## The 6-Agent Team

| Agent | Role |
|---|---|
| **AD-Partner** | Orchestrator -- approves, reviews, oversees |
| **AD-Intake** | First contact -- conflict check, classification, acknowledgement |
| **AD-Review** | Compliance + approval -- checks output before delivery |
| **AD-Corporate** | Company formations, incorporations |
| **AD-Research** | Case law, legislation, market research |
| **AD-Drafting** | Document drafting -- contracts, letters, agreements |

All agents: himalaya email Atlas.Reid@tatumclaw.ai, Telegram topic #7.

---

## Structured Briefing Interview

Before work begins on a matter, the fee earner completes a structured briefing interview at `/matter/<id>/briefing`. This collects:

- Jurisdiction, client type, counterparty, deal value band, deadline, risk appetite
- Matter-type-specific questions (contract type, structure, employee level, deal stage, etc.)

Agents fetch briefing context via `GET /api/matters/<id>/briefing` before starting work.

Configure per-matter-type behaviour (Required / Recommended / Optional / Off) at `/settings/engagement`.

---

## Document Review Standard

All document reviews follow the **AD Legal OS Gap Analysis Format**:

1. **Header** -- document title, framework, date, prepared for, disclaimer
2. **Executive Summary** -- narrative overview + gap counts by risk colour
3. **Risk Summary Table** -- GAP-01, GAP-02... with legal reference, Severity x Likelihood
4. **Detailed Findings** -- one per gap: legal reference, policy section, finding, recommendation
5. **Prioritised Remediation Plan** -- grouped by priority (Before Proceeding / Promptly / When Convenient)
6. **Outside Counsel Consideration** -- escalation recommendation

**Risk scoring:** Severity (1-4) x Likelihood (1-5):
- RED >= 16 | ORANGE 9-15 | YELLOW 5-8 | GREEN < 5

Supported document types: Privacy Policy, Terms of Service, SaaS Agreements, Employment Contracts, Settlement Agreements, NDAs, Shareholder Agreements, DPAs, Cookie Policies.

---

## OpenClaw Agent Setup

Each agent needs a workspace with SOUL.md and AGENTS.md:

```bash
mkdir -p ~/.openclaw/sandboxes/agent-ad-intake
cp workspace-ad-intake-SOUL.md ~/.openclaw/sandboxes/agent-ad-intake/
cp workspace-ad-intake-AGENTS.md ~/.openclaw/sandboxes/agent-ad-intake/
```

Repeat for AD-Review, AD-Corporate, AD-Research, AD-Drafting, AD-Partner.

Note: SOUL.md files contain `{{sra_number}}` -- replace with your firm's actual SRA number.

---

## Skills Framework

LegalOS loads AgentSkills from the `skills/` directory at startup. **19 skills** included:

| Skill | Purpose |
|---|---|
| matter-classifier | Routes all new matters by PA, SL, Tier |
| commercial-law | Full commercial law capability (SGA, CRA, UCTA, etc.) |
| contract-review | RED/AMBER/GREEN clause assessment |
| document-review | Standardised gap analysis format |
| ir35 | IR35 worker status + PSC indicators |
| employment-tribunal-claim | ET claim drafting + ACAS procedure |
| ma-due-diligence | M&A transaction due diligence |
| nda-triage / nda-pre-screening | NDA classification + screening |
| settlement-agreement | Settlement agreement drafting |
| shareholder-agreement | Shareholder agreement drafting |
| company-formation | Ltd/LLP/CIC incorporations |
| data-breach-response | GDPR breach notification procedure |
| gdpr-compliance-audit | UK GDPR gap analysis |
| commercial-litigation | Dispute resolution |
| legal-risk-assessment | General risk evaluation |
| legal-meeting-briefing / legal-team-briefing | Meeting prep |
| compliance | SRA compliance checklist |
| generate-response-form-templates | Form template generation |
| vendor-agreement-status | Vendor agreement review |
| canned-responses | Standard legal correspondence |

Add a new skill: create `skills/<name>/SKILL.md` and restart the app.

---

## Google Drive Integration

Creates a Drive folder per matter via gog CLI (tatum@tatumdale.com).
Drive root: `1aOipSxzKu1iuoP5w8vaQX273koOhqgKp`

```bash
brew install gog
gog account add --account tatum@tatumdale.com
gog drive list
```

App works without Drive -- matter folders are skipped if gog is unavailable.

---

## Key Routes

| Route | Description |
|---|---|
| `/` | Dashboard |
| `/matters` | Matter list (filter by status, phase, PA, briefing) |
| `/matter/<id>` | Matter detail + timeline |
| `/matter/<id>/briefing` | Structured briefing interview wizard |
| `/matter/new` | New matter intake |
| `/clients`, `/contacts`, `/companies`, `/pipeline` | CRM pages |
| `/skills` | Skills library |
| `/skills/<slug>` | Skill detail with parsed sections |
| `/settings` | Firm settings |
| `/settings/engagement` | Briefing behaviour config per matter type |
| `/api/matters/<id>/briefing` | Agent briefing fetch endpoint |
| `/api/matters`, `/api/skills` | REST APIs |

---

## Troubleshooting

**Port 5050 in use:**
```bash
lsof -i :5050
kill <PID>
```

**Drive not working:**
```bash
gog drive list
gog account list
```

**Skills not loading:** Restart the app -- skills are loaded at startup only.

**Database locked:**
```bash
rm db/ad_matters.db
python3 app.py
```

---

## Updating

```bash
cd ~/ad-legal-os
git pull origin master
python3 app.py
```

`db/ad_matters.db` is gitignored -- git pull will not overwrite it.

---

## Known Limitations

- No auth -- for local/internal network use only
- Email routing via Amelia (PA agent), not directly to the app
- Verification loops -- spec in REQUIREMENTS.md, Sprint 3 in progress
