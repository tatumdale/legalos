# SKILL.md — Testing

## name
testing

## description
Comprehensive testing framework for the Legal OS: API endpoints, database integrity, UI routing, middleware, and error log analysis. Run before and after every code change, deployment, or feature release. Use when debugging issues, verifying fixes, or accepting new work.

## When to Use This Skill

- After any code change to app.py, templates, or database schema
- After deploying or restarting the server
- When a user reports an error or unexpected behavior
- Before marking a feature as complete
- Weekly health check of all Legal OS routes
- After database migration or schema changes

## Testing Skill

You are a QA engineer for the Legal OS. You test systematically, document failures, and verify fixes.

**Golden rule:** If the app starts, test the routes. If routes respond, test the data. If data looks right, test the UI. If UI works, check the logs.

## Testing Checklist

### Phase 1 — Server Health

1. **Server is running:** `lsof -i :5050` shows a Python process
2. **Health endpoint:** `GET /health` returns `{"status": "ok"}`
3. **No recent crash:** Check `/tmp/ad-legal-os.log` for ERROR or Traceback in the last 50 lines
4. **DB accessible:** `sqlite3 ad_matters.db ".tables"` shows expected tables

### Phase 2 — Route Coverage

Test every route in this order. A 200 is success. Anything else must be diagnosed.

| Route | Method | Expected | What to check |
|---|---|---|---|
| `/health` | GET | 200 | JSON status ok |
| `/` | GET | 200 | Dashboard renders |
| `/matters` | GET | 200 | Matter list loads |
| `/matter/<id>` | GET | 200 | Matter detail renders |
| `/agents` | GET | 200 | Agent status loads |
| `/compliance` | GET | 200 | Compliance checklist |
| `/settings` | GET | 200 | Settings page |
| `/settings/practice_areas` | GET | 200 | PA management |
| `/settings/matter_types` | GET | 200 | MT management |
| `/seed` | POST | 302 or 200 | Seeds data, redirects |
| `/precedents` | GET | 200 | Precedent library |
| `/intake` | GET | 200 | Intake form |
| `/skills` | GET | 200 | Skills grid loads |
| `/skills/<slug>` | GET | 200 | Skill detail renders |
| `/crm` | GET | 200 | CRM dashboard |
| `/crm/companies` | GET | 200 | Companies list |
| `/crm/contacts` | GET | 200 | Contacts list |
| `/crm/products` | GET | 200 | Products catalog |
| `/crm/pipeline` | GET | 200 | Kanban board |
| `/crm/activities` | GET | 200 | Activity log |
| `/crm/companies/<id>` | GET | 200 | Company detail |
| `/crm/contacts/<id>` | GET | 200 | Contact detail |

### Phase 3 — API Endpoints

Test all REST endpoints using `curl` or Python `requests`. Log the actual response.

**Matter endpoints:**
```bash
# Create a test matter
curl -s -X POST http://localhost:5050/api/matters \
  -H "Content-Type: application/json" \
  -d '{"client_name":"Test Client","client_email":"test@test.com","practice_area":"Commercial Law"}'

# Conflict check
curl -s -X POST http://localhost:5050/api/matters/<id>/conflict-check

# Conflict resolution
curl -s -X POST http://localhost:5050/api/matters/<id>/conflict-resolve \
  -H "Content-Type: application/json" \
  -d '{"resolution":"clear","resolved_by":"Test","notes":"Automated test"}'
```

**CRM endpoints:**
```bash
# List companies
curl -s http://localhost:5050/api/crm/companies

# List contacts
curl -s http://localhost:5050/api/crm/contacts

# List products
curl -s http://localhost:5050/api/crm/products

# Create contact
curl -s -X POST http://localhost:5050/api/crm/contacts \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Test","last_name":"User","email":"test@example.com"}'

# Update pipeline stage
curl -s -X PATCH http://localhost:5050/api/crm/pipelines/<id>/stage \
  -H "Content-Type: application/json" \
  -d '{"stage":"won"}'
```

**Skills endpoints:**
```bash
# List all skills
curl -s http://localhost:5050/api/skills

# Toggle active
curl -s -X PATCH http://localhost:5050/api/skills/<slug>/active

# Use count
curl -s -X POST http://localhost:5050/api/skills/<slug>/use
```

**Document endpoints:**
```bash
# Get drive folder
curl -s http://localhost:5050/api/matters/<id>/drive-folder

# List documents
curl -s http://localhost:5050/api/matters/<id>/documents

# Upload document (multipart)
curl -s -X POST http://localhost:5050/api/matters/<id>/documents \
  -F "file=@test.pdf" -F "doc_type=draft" -F "description=Test upload"
```

### Phase 4 — Database Integrity

```python
import sqlite3

DB = "/Users/tatumclaw/.openclaw/workspace-ad-shared/db/ad_matters.db"
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

# 1. Check all expected tables exist
tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
expected = ['matters', 'clients', 'documents', 'audit_log', 'compliance_checks',
             'conflict_log', 'skill_steps', 'skills_metadata',
             'crm_companies', 'crm_contacts', 'crm_directors',
             'crm_products', 'crm_company_products', 'crm_pipelines', 'crm_activities']
missing = [t for t in expected if t not in tables]
print(f"Missing tables: {missing}" if missing else "All tables present")

# 2. Check foreign keys are valid
for table in ['matters', 'documents', 'crm_contacts']:
    bad = conn.execute(f"""
        SELECT id FROM {table}
        WHERE client_id IS NOT NULL
        AND client_id NOT IN (SELECT id FROM clients)
    """).fetchall()
    print(f"{table} with invalid client_id: {len(bad)} rows")

# 3. Check no duplicate refs
dupes = conn.execute("""
    SELECT ref, COUNT(*) as cnt FROM matters
    WHERE ref IS NOT NULL
    GROUP BY ref HAVING cnt > 1
""").fetchall()
print(f"Duplicate matter refs: {dupes}")

# 4. Check all skills_metadata slugs match skill_steps
active_slugs = {r[0] for r in conn.execute("SELECT skill_slug FROM skills_metadata WHERE is_active=1").fetchall()}
step_slugs = {r[0] for r in conn.execute("SELECT DISTINCT skill_id FROM skill_steps").fetchall()}
orphan_skills = active_slugs - step_slugs
print(f"Active skills without steps: {orphan_skills}")

conn.close()
```

### Phase 5 — Error Log Analysis

```bash
# Check for errors in the last hour
tail -200 /tmp/ad-legal-os.log | grep -E "ERROR|Traceback|Exception|WARNING" | tail -20

# Check for 500 errors
tail -500 /tmp/ad-legal-os.log | grep "500\|Internal Server Error"

# Check for specific route errors
tail -200 /tmp/ad-legal-os.log | grep "/api/crm\|/api/matters\|/skills/"
```

### Phase 6 — UI Rendering (Canvas)

Use the canvas tool to visually verify pages:

```python
# Navigate to each key page
canvas(action="navigate", url="http://localhost:5050/crm")
canvas(action="snapshot", target="crm-dashboard")

canvas(action="navigate", url="http://localhost:5050/crm/companies")
canvas(action="snapshot", target="crm-companies")

canvas(action="navigate", url="http://localhost:5050/matters")
canvas(action="snapshot", target="matters-list")
```

Check for:
- Pages loading without JavaScript errors in browser console
- All panels and cards rendering with data
- Forms showing correct field labels
- Buttons that are wired up (hover effects, click handlers)

## Troubleshooting Common Errors

### "werkzeug.routing.exceptions.BuildError: Could not build url for endpoint 'X'"
**Cause:** Template uses `url_for('X')` but route `X` doesn't exist in app.py.
**Fix:** Add the missing route or fix the template to use the correct endpoint name.
```python
# Check which routes exist
grep "def crm_X\|@app.route.*crm.X" app.py
# Add missing route
```

### "sqlite3.OperationalError: no such column: X"
**Cause:** Column X was added to the code but not to the actual database schema.
**Fix:** Run the ALTER TABLE migration:
```python
conn.execute("ALTER TABLE tablename ADD COLUMN colname TEXT")
```

### "TypeError: unsupported operand type(s) for +: 'int' and 'str'"
**Cause:** Template uses `{{ value + "string" }}` with an integer variable.
**Fix:** Use `{{ value|string + "string" }}` or `{{ "%d" % value + "string" }}`

### "jinja2.exceptions.UndefinedError: 'X' is undefined"
**Cause:** Variable X not passed to `render_template()`.
**Fix:** Add `X=value` to the `render_template()` call.

### "500 Internal Server Error" on POST to /api/...
**Cause:** Usually a database error in the API handler.
**Fix:** Check the logs for the specific Python exception. Common causes:
- Wrong number of SQL bindings
- `None` passed to a NOT NULL column
- `uuid` not converted to string before INSERT

### "Network Error" in browser console for API calls
**Cause:** The Flask app is not accessible from the browser (common in canvas testing).
**Fix:** Access via actual browser at `http://localhost:5050`. Canvas sandbox can't reach localhost.

## Test Report Format

After every test session, record:

```
## Test Report — YYYY-MM-DD

### Routes Tested
| Route | Result | Notes |
|---|---|---|
| /health | ✅ 200 | |

### API Endpoints Tested
| Endpoint | Result | Response |

### Database Integrity
- Missing tables: none
- Invalid foreign keys: none
- Duplicate refs: none

### Log Errors (last 24h)
[None / list errors]

### Issues Found
1. [Issue] — [Root cause] — [Fix applied]

### Sign-off
Tested by: [name]
Date: [date]
Status: ✅ Ready / ⚠️ Blocking issues
```
