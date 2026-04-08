# PROTECTED.md — AD Legal OS

Files and patterns that should NEVER be modified without explicit review.

## Hard Rules (Never Touch)

1. **Database schema in `app.py` `init_db()`** — Changing column names or table structures breaks existing data. Any schema change requires a migration script.

2. **`audit_log` INSERT format** — Correct columns: `(id, matter_id, agent_id, action_type, detail, human_override, human_reviewer, created_at)`. Never use `action`/`actor`/`details` — these columns don't exist.

3. **`JUDGEMENT.md`** — SRA compliance framework. Changing this invalidates the firm's compliance posture.

4. **`matter_type_config` and `verification_criteria` seed data** — These are legal business rules. Don't modify without AD-Partner approval.

5. **SRA number, firm name, regulatory fields in `DEFAULT_FIRM_CONFIG`** — These are legal identifiers.

## Patterns to Preserve

6. **Token cost calculation** — Always use `calculate_token_cost()` from app.py. Never inline rate calculations.

7. **DB connection pattern** — Always use `with app.app_context(): db = get_db()` for manual DB access. Never commit() outside of explicit transaction blocks.

8. **Flash messages** — Don't include secrets (tokens, URLs with IDs, API keys) in flash messages. They appear in the UI.

9. **Portal token storage** — Always hash tokens with SHA-256 before storing. Never store raw tokens.

10. **Agent SOUL files** — Each agent's SOUL.md governs their behaviour. Changes to SOUL files can cause the agent to behave unexpectedly. Requires review.

## Safe to Modify Freely

- `templates/` — UI templates (add classes, restructure, restyle freely)
- `static/css/style.css` — CSS (append new styles, modify freely)
- `email_poller.py` — Email integration module (new code, no dependencies)
- `legal_os/` — Internal helper modules (analyzer, billing, dms, llm, research)
- `tests/` — Test files (add freely, never break existing tests)

## Before Any Change

- Run: `python3 -c 'from app import app; print("OK")'`
- If there are new DB tables: add them to `init_briefing_schema()` with `CREATE TABLE IF NOT EXISTS`
- If changing a route: verify with `python3 -c "from app import app; app.test_client().get('/route')"`
- All new routes must be registered in `app.py` and tested

## Emergency Rollback

If something breaks after a deploy:
```bash
cd ~/ad-legal-os && git log --oneline -5
git revert HEAD  # revert last commit
python3 app.py    # restart
```
