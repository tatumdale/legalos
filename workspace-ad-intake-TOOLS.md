# TOOLS.md — AD-Intake

## Tools I Use

### Email — himalaya CLI

Acme Dale Legal Services email via the `himalaya` CLI.

> **Note:** The `atlas` account is configured for `Atlas.Reid@tatumclaw.ai`.
> Acme Dale Legal Services intake emails (intake@acmedalelegal.co.uk) should be connected to a
> dedicated `harper-james` account in `~/.config/himalaya/accounts.toml`.

```bash
# List configured accounts
himalaya account list

# Add Acme Dale Legal Services account (when ready)
himalaya account add harper-james \
  --email intake@acmedalelegal.co.uk

# Poll envelopes
himalaya envelope list --account harper-james --since "2026-03-31T08:00:00Z"

# Read email body
himalaya envelope body ENVELOPE_ID --account harper-james
```

**Current working account:** `atlas` (Atlas.Reid@tatumclaw.ai — for testing)
**Production account:** `harper-james` (intake@acmedalelegal.co.uk — configure when ready)

### Database — SQLite

Matter records and audit log: `~/.openclaw/workspace-ad-shared/db/ad_matters.db`

```python
import sqlite3, uuid
db = sqlite3.connect("/Users/tatumclaw/.openclaw/workspace-ad-shared/db/ad_matters.db")
db.row_factory = sqlite3.Row

# Conflict check
existing = db.execute(
    "SELECT id FROM clients WHERE name=? OR company_name=?",
    (client_name, company_name)
).fetchone()

# Insert matter
matter_id = str(uuid.uuid4())
db.execute("""
    INSERT INTO matters (id, client_name, client_email, practice_area, matter_type,
        confidence_practice_area, confidence_matter_type, status, created_at)
    VALUES (?,?,?,?,?,?,?,?,datetime('now'))
""", (matter_id, name, email, pa, mt, conf_pa, conf_mt, 'intake'))

# Compliance checklist
db.execute("INSERT INTO compliance_checklist (id, matter_id) VALUES (?,?)",
           (str(uuid.uuid4()), matter_id))

# Audit log
db.execute("""
    INSERT INTO audit_log (id, matter_id, agent_id, action_type, detail,
        tokens_used, cost_usd, model_used, confidence_score, created_at)
    VALUES (?,?,?,?,?,?,?,?,?,datetime('now'))
""", (str(uuid.uuid4()), matter_id, 'AD-Intake', 'classified',
      detail, tokens, cost, model, conf))
db.commit()
```

### Telegram — OpenClaw message tool

**Trigger:** Telegram topic #7 — clients/intake messages land here.
**Notify AD-Review:** Same topic #7.

```python
from openclaw import message
message(
    action="send",
    channel="telegram",
    target="-1003708796513",
    message="New matter submitted for review — [Matter Ref]",
    threadId="7"
)
```

### Firm Config

```python
import json
with open("/Users/tatumclaw/.openclaw/workspace-ad-shared/db/firm_config.json") as f:
    cfg = json.load(f)
# cfg keys: firm_name, sra_number, colp_name, cofa_name, pi_insurer, address, email
```

### Matter Types Reference

```python
matter_types = db.execute(
    "SELECT * FROM matter_types WHERE practice_area_slug=?", (pa_slug,)
).fetchall()
# Fields: id, name, slug, practice_area_slug, fee_estimate, ai_effort, delivery_pattern
```

### LLM — Classification

Use MiniMax M2.7 via OpenClaw for classification (fast, pattern-matching).
For ambiguous matters: flag for AD-Review escalation rather than forcing a low-confidence classification.

### Intake Workflow

1. Telegram topic #7 message received (client instruction or intake trigger)
2. If email: read via himalaya, extract client name/company/email/substance
3. Conflict check against `clients` table
4. Classify: Practice Area + Matter Type + confidence scores
5. Generate client care letter (template: `client_care_letter.txt`)
6. Log matter + compliance checklist in DB
7. Notify AD-Review on Telegram topic #7