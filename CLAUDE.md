# AD Legal OS — Project Context

## What This Is

AD Legal OS (Acme Dale Legal OS) is an AI-powered legal practice management platform for small/medium law firms. Built with Flask + SQLite on the Mac mini, managed by a 6-agent AI team.

**Live:** http://localhost:5050
**Code:** ~/ad-legal-os/
**Repo:** https://github.com/tatumdale/legalos

## Current State — What is Built

### Core App
- Flask + SQLite (port 5050)
- CRM: contacts, companies, products, pipeline, activities
- Matter management: intake, classification, conflict check, document production
- Audit log: every state change tracked with actor + timestamp
- Google Drive integration via gog CLI

### 6-Agent Team
AD-Intake, AD-Review, AD-Corporate, AD-Research, AD-Drafting, AD-Partner.
All use Atlas.Reid@tatumclaw.ai identity, Telegram topic #7.

### 18 Legal Skills
Skills loaded from skills/ directory at startup. Cover: commercial law, contract review, employment, M&A due diligence, IP, data protection, NDA triage, settlement agreements, shareholder agreements, and more.

## What is Planned But Not Built (from REQUIREMENTS.md)

### Feature 1: Structured Briefing Interview
Multi-step interview wizard that collects structured context before agent work begins.
- Jurisdiction, client type, counterparty, deal value, deadline, risk appetite
- Conditional questions per matter type (contract review vs dispute vs formation etc.)
- Briefing stored per matter and injected into agent prompts
- UX: multi-step form, progress indicator, voice input, save as draft

### Feature 2: Iterative Verification Loops
Output quality gate between agent production and delivery.
- Criteria defined per matter type (compliance checklist, completeness check, risk flags)
- Automated scoring: PASS / AMBER / FAIL per criterion
- AMBER/FAIL triggers revision loop (back to relevant agent)
- Results logged in verification_log table
- Fee earner dashboard showing verification status

## Tech Stack
- Python 3.10+ / Flask 3.x / SQLite
- Jinja2 templates (no frontend framework)
- gog CLI for Google Drive
- OpenClaw for agent orchestration
- 1Password for secrets

## Key Files
- app.py — Flask app (routes, DB schema, agent logic)
- legal_os/ — core modules (analyzer, billing, dms, llm, research)
- skills/ — 18 skill definitions (SKILL.md format)
- templates/ — Flask templates
- workspace-ad-*-SOUL.md — agent system prompts

## Design Principles
- Keep dependencies minimal (Flask only, stdlib)
- Human-in-the-loop at key decision gates
- Structured output over free-text where possible
- Law firm context: conservative, risk-aware, SRA-compliant

## Next Steps (for Cursor to plan)
1. Review REQUIREMENTS.md in full
2. Decide which feature to build first (Briefing Interview vs Verification Loops)
3. Plan the build — architecture, DB schema changes, new routes, new templates
4. Implement incrementally with tests
