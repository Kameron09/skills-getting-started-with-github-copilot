from fastapi.testclient import TestClient
import importlib.util
import sys
from pathlib import Path


# Load the FastAPI app from src/app.py without requiring package imports
APP_PATH = Path(__file__).resolve().parents[1] / 'src' / 'app.py'
spec = importlib.util.spec_from_file_location('app_module', str(APP_PATH))
app_module = importlib.util.module_from_spec(spec)
sys.modules['app_module'] = app_module
spec.loader.exec_module(app_module)

client = TestClient(app_module.app)


def test_get_activities():
    resp = client.get('/activities')
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Expect some known activities from the seeded in-memory DB
    assert 'Chess Club' in data
    assert 'participants' in data['Chess Club']


def test_signup_and_unregister_flow():
    activity = 'Chess Club'
    email = 'newstudent@mergington.edu'

    # Ensure the participant is not already present
    before = client.get('/activities').json()
    assert email not in before[activity]['participants']

    # Sign up
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert 'Signed up' in resp.json().get('message', '')

    # Check participant was added
    after = client.get('/activities').json()
    assert email in after[activity]['participants']

    # Unregister
    resp = client.post(f"/activities/{activity}/unregister?email={email}")
    assert resp.status_code == 200
    assert 'Removed' in resp.json().get('message', '')

    # Verify removal
    final = client.get('/activities').json()
    assert email not in final[activity]['participants']
