"""Settings routes tests."""
import pytest

def test_settings_page_loads(client):
    response = client.get('/settings')
    assert response.status_code == 200

def test_save_firm_config(client):
    response = client.post('/settings/firm-config',
        json={"firm_name": "Test Firm Updated", "sra_number": "123456"})
    assert response.status_code in (200, 302)
