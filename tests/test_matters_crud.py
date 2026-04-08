"""Matter CRUD tests."""
import pytest, json

def test_matters_list(client):
    response = client.get('/matters')
    assert response.status_code == 200

def test_matter_detail_not_found(client):
    response = client.get('/matter/nonexistent-id-xyz')
    # Route redirects to /matters when not found
    assert response.status_code in (302, 404)

def test_matter_detail_with_real_id(client):
    from app import get_db
    with client.application.app_context():
        db = get_db()
        matter = db.execute("SELECT id FROM matters LIMIT 1").fetchone()
        if not matter:
            pytest.skip("No matters in DB")
        mid = matter['id']

    response = client.get(f'/matter/{mid}')
    assert response.status_code == 200

def test_create_intake_requires_post(client):
    response = client.get('/intake/new')
    assert response.status_code in (404, 405)

def test_audit_log_insert(client):
    """Verify audit_log INSERT with correct columns works."""
    from app import get_db
    import uuid
    from datetime import datetime
    with client.application.app_context():
        db = get_db()
        matter = db.execute("SELECT id FROM matters LIMIT 1").fetchone()
        if not matter:
            pytest.skip("No matters in DB")
        mid = matter['id']

        tid = str(uuid.uuid4())
        db.execute(
            "INSERT INTO audit_log (id, matter_id, agent_id, action_type, detail, human_override, human_reviewer, created_at) VALUES (?,?,?,?,?,0,?,?)",
            (tid, mid, 'test', 'test_action', '{"note":"test"}', 'system',
             datetime.now().isoformat()))
        db.commit()

        row = db.execute("SELECT * FROM audit_log WHERE id=?", (tid,)).fetchone()
        assert row is not None
        assert row['agent_id'] == 'test'
        assert row['action_type'] == 'test_action'
