import pytest, sys, os, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def app():
    """Create test app with in-memory DB."""
    from app import app, init_db, DB_PATH
    app.config['TESTING'] = True
    import app as app_module
    original_db = app_module.DB_PATH
    fd, tmpdb = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    app_module.DB_PATH = __import__('pathlib').Path(tmpdb)
    with app.test_client() as client:
        with app.app_context():
            init_db()
            yield client
    app_module.DB_PATH = original_db
    try:
        os.unlink(tmpdb)
    except: pass

@pytest.fixture
def client(app):
    return app
