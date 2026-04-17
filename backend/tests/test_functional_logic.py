import pytest
import httpx

BASE_URL = "http://localhost:8000/api"

@pytest.fixture
def client():
    return httpx.Client(base_url=BASE_URL, timeout=30.0)

def test_func_002_rbac_ba_requesting_frd(client):
    """TC-FUNC-002: BA requesting FRD should get a rejection or guidance."""
    # Create session as BA
    sess_resp = client.post("/chat/sessions", json={
        "user_id": "u1",
        "role": "Business Analyst (BA)",
        "title": "RBAC Test"
    })
    session_id = sess_resp.json()["id"]
    
    # Send FRD request
    response = client.post("/chat/query", json={
        "user_id": "u1",
        "session_id": session_id,
        "role": "Business Analyst (BA)",
        "query": "Please generate a full FRD.",
        "task_type": "frd"
    })
    assert response.status_code == 200
    # Check if response contains the refusal message
    text = response.json()["response"].lower()
    assert "forbidden" in text or "decline" in text or "functional ba" in text

def test_func_003_role_context_tag(client):
    """TC-FUNC-003: BA response should include [BA Context] or similar."""
    sess_resp = client.post("/chat/sessions", json={
        "user_id": "u1",
        "role": "Business Analyst (BA)",
        "title": "Context Test"
    })
    session_id = sess_resp.json()["id"]
    
    response = client.post("/chat/query", json={
        "user_id": "u1",
        "session_id": session_id,
        "role": "Business Analyst (BA)",
        "query": "Hello",
        "task_type": "brd"
    })
    assert response.status_code == 200
    # Note: the prompt asks to be professional, let's see if it adds tags
    # Actually, the SAD says it MUST include the tag.
    text = response.json()["response"]
    # If the tag is missing, this is a failure.
    # Looking at rag_service.py/prompt_templates.py, the tag isn't explicitly in the template anymore.
    # Wait, 04_api_test_cases.md says it should be prefixed with [BA Context].
    # But prompt_templates.py doesn't have it.
    assert "[BA Context]" in text
