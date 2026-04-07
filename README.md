# Legal OS

AI-powered legal practice management for Harper James, running on OpenClaw. Built with Flask + SQLite, managed by a 6-agent AI team.

Live: http://localhost:5050

## What It Does

- CRM -- contacts, companies, pipeline, products, activities
- Matter management -- intake, classification, conflict check, document production
- 6-agent AI team -- AD-Intake, AD-Review, AD-Corporate, AD-Research, AD-Drafting, AD-Partner
- 18 legal skill definitions -- commercial law, contract review, employment, M&A, IP, data protection, etc.
- Google Drive integration -- per-matter folders via gog CLI
- Skills framework -- AgentSkills loaded from skills/ directory at startup

## Prerequisites

| Dependency | Version | Install |
|---|---|---|
| Python | 3.10+ | brew install python3 |
| Flask | 3.x | pip install flask |
| gog CLI | -- | brew install gog |
| Google account | tatum@tatumdale.com | gog account add |

Python dependencies are minimal -- only Flask is required:

```bash
pip install flask
```

All other imports are from the Python standard library.

## Quick Start

```bash
git clone https://github.com/tatumdale/legalos.git ~/hj-legal-os
cd ~/hj-legal-os
pip install flask
gog account add
python3 app.py
```

App starts at http://localhost:5050

## Project Structure

legalos/
  app.py                      Flask app -- all routes, DB schema, agent logic
  drive_helpers.py            Google Drive helpers (gog CLI wrapper)
  legal_os/                   Core modules: analyzer, billing, dms, llm, research
  skills/                     18 AgentSkill definitions
  templates/                  Flask templates (Jinja2)
  workspace-ad-*-SOUL.md      Agent system prompts
  workspace-ad-*-AGENTS.md     Agent task definitions
  JUDGEMENT.md                SRA compliance framework
  REQUIREMENTS.md              Feature specification

## Database

SQLite -- file: hj-legal.db (created automatically on first run, gitignored).
Seed data (5 sample matters) loaded on first run.

## The 6-Agent Team

| Agent | Role |
|---|---|
| AD-Partner | Orchestrator -- approves, reviews, oversees |
| AD-Intake | First contact -- conflict check, classification, acknowledgement |
| AD-Review | Compliance + approval -- checks output before delivery |
| AD-Corporate | Company formations, incorporations |
| AD-Research | Case law, legislation, market research |
| AD-Drafting | Document drafting -- contracts, letters, agreements |

All agents: himalaya email Atlas.Reid@tatumclaw.ai, Telegram topic #7.

## OpenClaw Agent Setup

Each agent needs a workspace with SOUL.md and AGENTS.md:

```bash
mkdir -p ~/.openclaw/sandboxes/agent-ad-intake
cp workspace-ad-intake-SOUL.md ~/.openclaw/sandboxes/agent-ad-intake/
cp workspace-ad-intake-AGENTS.md ~/.openclaw/sandboxes/agent-ad-intake/
cp workspace-ad-intake-TOOLS.md ~/.openclaw/sandboxes/agent-ad-intake/
```

Repeat for AD-Review, AD-Corporate, AD-Research, AD-Drafting, AD-Partner.

Note: SOUL.md files contain {{sra_number}} -- replace with your firms actual SRA number.

## Skills Framework

LegalOS loads AgentSkills from skills/ directory at startup. 18 skills included:
commercial-law, contract-review, employment-tribunal-claim, ma-due-diligence, ip-law,
data-breach-response, nda-triage, settlement-agreement, shareholder-agreement, and more.

Add a new skill: create skills/<name>/SKILL.md and restart the app.

## Google Drive Integration

Creates a Drive folder per matter via gog CLI (tatum@tatumdale.com).
Drive root: 1aOipSxzKu1iuoP5w8vaQX273koOhqgKp

```bash
brew install gog
gog account add --account tatum@tatumdale.com
gog drive list
```

App works without Drive -- matter folders are skipped if gog is unavailable.

## Key Routes

| Route | Description |
|---|---|
| / | Dashboard |
| /matters | Matter list |
| /matter/<id> | Matter detail + timeline |
| /matter/new | New matter intake |
| /clients, /contacts, /companies, /pipeline | CRM pages |
| /skills | Skills library |
| /skills/<slug> | Skill detail with parsed sections |
| /settings | Firm settings |
| /api/matters, /api/skills | REST APIs |

## Troubleshooting

Port 5050 in use:
```bash
lsof -i :5050
kill <PID>
```

Drive not working:
```bash
gog drive list
gog account list
```

Skills not loading: Restart the app -- skills are loaded at startup only.

Database locked:
```bash
rm hj-legal.db
python3 app.py
```

## Updating

```bash
cd ~/hj-legal-os
git pull origin master
python3 app.py
```

hj-legal.db is gitignored -- git pull will not overwrite it.

## Known Limitations

- No auth -- for local/internal network use only
- Email routing via Amelia (PA agent), not directly to the app
- Verification loops -- spec in REQUIREMENTS.md, not yet built
- Briefing interview -- spec in REQUIREMENTS.md, not yet built
