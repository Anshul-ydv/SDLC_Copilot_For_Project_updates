import pytest
import httpx
import os

BASE_URL = "http://localhost:8000/api"

@pytest.fixture
def client():
    return httpx.Client(base_url=BASE_URL, timeout=30.0)

# --- AUTH TESTS ---

def test_api_001_login_valid_ba(client):
    """TC-API-001 — POST /auth/login — Valid BA Credentials"""
    response = client.post("/auth/login", json={
        "email": "ba@hsbc.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["role"] == "Business Analyst (BA)"
    assert data["user_id"] == "u1"

def test_api_002_login_valid_fba(client):
    """TC-API-002 — POST /auth/login — Valid FBA Credentials"""
    response = client.post("/auth/login", json={
        "email": "fba@hsbc.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert response.json()["role"] == "Functional BA (FBA)"

def test_api_003_login_valid_qa(client):
    """TC-API-003 — POST /auth/login — Valid QA Credentials"""
    response = client.post("/auth/login", json={
        "email": "qa@hsbc.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert response.json()["role"] == "QA / Tester"

def test_api_004_login_invalid_password(client):
    """TC-API-004 — POST /auth/login — Invalid Password"""
    response = client.post("/auth/login", json={
        "email": "ba@hsbc.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_api_005_login_unknown_email(client):
    """TC-API-005 — POST /auth/login — Unknown Email"""
    response = client.post("/auth/login", json={
        "email": "nobody@hsbc.com",
        "password": "password123"
    })
    assert response.status_code == 401

def test_api_006_login_missing_fields(client):
    """TC-API-006 — POST /auth/login — Missing Required Fields"""
    response = client.post("/auth/login", json={
        "email": "ba@hsbc.com"
    })
    assert response.status_code == 422

# --- SESSION TESTS ---

def test_api_007_create_session(client):
    """TC-API-007 — POST /chat/sessions — Create Session"""
    response = client.post("/chat/sessions", json={
        "user_id": "u1",
        "role": "Business Analyst (BA)",
        "title": "Test Session"
    })
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["title"] == "Test Session"
    return data["id"]

def test_api_008_create_session_missing_field(client):
    """TC-API-008 — POST /chat/sessions — Missing Body Fields"""
    response = client.post("/chat/sessions", json={
        "user_id": "u1",
        "role": "Business Analyst (BA)"
    })
    assert response.status_code == 422

def test_api_009_get_sessions(client):
    """TC-API-009 — GET /chat/sessions — Retrieve Sessions"""
    response = client.get("/chat/sessions", params={"user_id": "u1"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_api_010_get_messages(client):
    """TC-API-010 — GET /chat/sessions/{id}/messages — Load Session History"""
    # Create session first
    sess_resp = client.post("/chat/sessions", json={
        "user_id": "u1",
        "role": "Business Analyst (BA)",
        "title": "History Test"
    })
    session_id = sess_resp.json()["id"]
    response = client.get(f"/chat/sessions/{session_id}/messages")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# --- QUERY TESTS ---

def test_api_011_chat_query(client):
    """TC-API-011 — POST /chat/query — Standard Non-Streaming"""
    # First create a session
    sess_resp = client.post("/chat/sessions", json={
        "user_id": "u1",
        "role": "Business Analyst (BA)",
        "title": "Query Test"
    })
    session_id = sess_resp.json()["id"]
    
    response = client.post("/chat/query", json={
        "user_id": "u1",
        "session_id": session_id,
        "role": "Business Analyst (BA)",
        "query": "What is the capital of France?",
        "task_type": "BRD"
    })
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["session_id"] == session_id

def test_api_013_query_missing_field(client):
    """TC-API-013 — POST /chat/query — Missing Required Field"""
    response = client.post("/chat/query", json={
        "user_id": "u1",
        "session_id": "some-id",
        "role": "Business Analyst (BA)"
    })
    assert response.status_code == 422

def test_api_014_query_invalid_session(client):
    """TC-API-014 — POST /chat/query — Invalid session_id"""
    response = client.post("/chat/query", json={
        "user_id": "u1",
        "session_id": "non-existent-session-999",
        "role": "Business Analyst (BA)",
        "query": "Hello"
    })
    # The API might return 500 if the session ID isn't linked to a real record in DB while trying to save message
    assert response.status_code != 200

def test_api_018_upload_pdf(client):
    """TC-API-018 — POST /documents/upload — Valid PDF"""
    # Create a session first
    sess_resp = client.post("/chat/sessions", json={
        "user_id": "u1",
        "role": "Business Analyst (BA)",
        "title": "Upload Test"
    })
    session_id = sess_resp.json()["id"]
    
    with open("tests/test.pdf", "rb") as f:
        response = client.post("/documents/upload", 
            data={"session_id": session_id},
            files={"file": ("test.pdf", f, "application/pdf")}
        )
    assert response.status_code == 200
    assert response.json()["status"].lower().startswith("successfully")

def test_api_020_upload_csv(client):
    """TC-API-020 — POST /documents/upload — Valid CSV"""
    sess_resp = client.post("/chat/sessions", json={
        "user_id": "u1",
        "role": "Business Analyst (BA)",
        "title": "Upload CSV Test"
    })
    session_id = sess_resp.json()["id"]
    
    with open("tests/test.csv", "rb") as f:
        response = client.post("/documents/upload", 
            data={"session_id": session_id},
            files={"file": ("test_csv.csv", f, "text/csv")}
        )
    assert response.status_code == 200

def test_api_022_upload_invalid(client):
    """TC-API-022 — POST /documents/upload — Unsupported File Type"""
    sess_resp = client.post("/chat/sessions", json={
        "user_id": "u1",
        "role": "Business Analyst (BA)",
        "title": "Invalid Upload Test"
    })
    session_id = sess_resp.json()["id"]
    
    with open("tests/test.exe", "rb") as f:
        response = client.post("/documents/upload", 
            data={"session_id": session_id},
            files={"file": ("test.exe", f, "application/octet-stream")}
        )
    assert response.status_code == 400
    assert "not supported" in response.json()["detail"]

def test_api_026_health_check(client):
    """TC-API-026 — GET / — Health Check Endpoint"""
    # Note: this is at root, not /api
    root_client = httpx.Client(base_url="http://localhost:8000", timeout=10.0)
    response = root_client.get("/")
    assert response.status_code == 200
    assert "Welcome" in response.json()["message"]

def test_api_027_concurrent_requests():
    """TC-API-027 — API Concurrent Request Integrity"""
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    
    def send_query(session_id: str, query: str, user_id: str):
        """Send a query to a specific session"""
        with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
            response = client.post("/chat/query", json={
                "user_id": user_id,
                "session_id": session_id,
                "role": "Business Analyst (BA)",
                "query": query
            })
            return response.json()
    
    # Create 5 different sessions
    sessions = []
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        for i in range(5):
            sess_resp = client.post("/chat/sessions", json={
                "user_id": f"user_{i}",
                "role": "Business Analyst (BA)",
                "title": f"Concurrent Test Session {i}"
            })
            sessions.append((sess_resp.json()["id"], f"user_{i}"))
    
    # Fire 5 simultaneous requests to different sessions
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(send_query, session_id, f"Query {i}", user_id)
            for i, (session_id, user_id) in enumerate(sessions)
        ]
        results = [f.result() for f in futures]
    
    # Verify each session has correct response
    assert len(results) == 5
    for i, result in enumerate(results):
        assert "response" in result
        assert result["session_id"] == sessions[i][0]
    
    # Verify no cross-session data bleed by checking message history
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        for i, (session_id, user_id) in enumerate(sessions):
            messages_resp = client.get(f"/chat/sessions/{session_id}/messages")
            messages = messages_resp.json()
            
            # Should have exactly 2 messages: user query + assistant response
            assert len(messages) == 2
            assert messages[0]["role"] == "user"
            assert f"Query {i}" in messages[0]["content"]
            assert messages[1]["role"] == "assistant"

