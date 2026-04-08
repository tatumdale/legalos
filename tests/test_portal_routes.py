"""Portal routes tests."""
import pytest, json

def test_portal_invalid_token_returns_error(client):
    response = client.get('/portal/invalid-token-xyz')
    assert response.status_code in (404, 410)

def test_portal_matter_requires_auth(client):
    """Accessing matter portal without valid token should redirect or 403."""
    response = client.get('/portal/matter/nonexistent-matter-id')
    assert response.status_code != 200

def test_token_usage_api_requires_json(client):
    """log-token-usage endpoint should reject non-JSON."""
    response = client.post('/api/matters/test-id/log-token-usage',
                           data='not json', content_type='text/plain')
    assert response.status_code == 400

def test_token_usage_api_logs_correctly(client):
    """log-token-usage should store the record."""
    from app import get_db
    with client.application.app_context():
        db = get_db()
        matter = db.execute("SELECT id FROM matters LIMIT 1").fetchone()
        if not matter:
            pytest.skip("No matters in DB")
        mid = matter['id']

    response = client.post(f'/api/matters/{mid}/log-token-usage',
        json={"agent_id": "AD-Review", "model": "minimax-m2.7",
              "input_tokens": 100000, "output_tokens": 50000,
              "description": "test"})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data.get('logged') == True
    assert 'cost_gbp' in data

    with client.application.app_context():
        db = get_db()
        row = db.execute("SELECT * FROM token_usage_log WHERE matter_id=?", (mid,)).fetchone()
        assert row is not None
        assert row['input_tokens'] == 100000
