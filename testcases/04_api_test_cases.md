# API Test Cases — HSBC SDLC Automation Copilot
**Document Version:** 1.0  
**Date:** 2026-03-26  
**Base URL:** `http://localhost:8000`  
**Reference:** SAD §6 (Data Flow), §7 (Architecture); Codebase: `auth.py`, `chat.py`, `documents.py`, `main.py`

---

## AUTH ENDPOINTS

---

### TC-API-001 — POST /auth/login — Valid BA Credentials

| Field | Value |
|---|---|
| **Priority** | Critical |
| **Endpoint** | `POST /auth/login` |
| **SAD Reference** | §4.1, §5.1 |

**Request:**
```json
{
  "email": "ba@hsbc.com",
  "password": "password123"
}
```

**Expected Response (200 OK):**
```json
{
  "token": "mock-jwt-token-for-Business Analyst (BA)",
  "role": "Business Analyst (BA)",
  "user_id": "u1"
}
```

**Assertions:**
- `status_code == 200`
- `body.token` is non-null and non-empty
- `body.role == "Business Analyst (BA)"`
- `body.user_id == "u1"`

---

### TC-API-002 — POST /auth/login — Valid FBA Credentials

| Field | Value |
|---|---|
| **Priority** | High |
| **Endpoint** | `POST /auth/login` |

**Request:**
```json
{ "email": "fba@hsbc.com", "password": "password123" }
```

**Assertions:**
- `status_code == 200`
- `body.role == "Functional BA (FBA)"`
- `body.user_id == "u2"`

---

### TC-API-003 — POST /auth/login — Valid QA Credentials

| Field | Value |
|---|---|
| **Priority** | High |
| **Endpoint** | `POST /auth/login` |

**Request:**
```json
{ "email": "qa@hsbc.com", "password": "password123" }
```

**Assertions:**
- `status_code == 200`
- `body.role == "QA / Tester"`
- `body.user_id == "u3"`

---

### TC-API-004 — POST /auth/login — Invalid Password

| Field | Value |
|---|---|
| **Priority** | High |
| **Endpoint** | `POST /auth/login` |

**Request:**
```json
{ "email": "ba@hsbc.com", "password": "wrongpassword" }
```

**Expected Response (401 Unauthorized):**
```json
{ "detail": "Invalid credentials" }
```

**Assertions:**
- `status_code == 401`
- `body.detail == "Invalid credentials"`

---

### TC-API-005 — POST /auth/login — Unknown Email

| Field | Value |
|---|---|
| **Priority** | High |
| **Endpoint** | `POST /auth/login` |

**Request:**
```json
{ "email": "nobody@hsbc.com", "password": "password123" }
```

**Assertions:**
- `status_code == 401`

---

### TC-API-006 — POST /auth/login — Missing Required Fields (Pydantic Validation)

| Field | Value |
|---|---|
| **Priority** | Medium |
| **Endpoint** | `POST /auth/login` |

**Request (password omitted):**
```json
{ "email": "ba@hsbc.com" }
```

**Expected Response (422 Unprocessable Entity)**

**Assertions:**
- `status_code == 422`
- `body.detail` contains field error referencing `"password"`

---

## CHAT SESSION ENDPOINTS

---

### TC-API-007 — POST /chat/sessions — Create Session

| Field | Value |
|---|---|
| **Priority** | Critical |
| **Endpoint** | `POST /chat/sessions` |
| **SAD Reference** | §4.5, §6 |

**Request:**
```json
{
  "user_id": "u1",
  "role": "Business Analyst (BA)",
  "title": "BRD Generation - Retail Banking"
}
```

**Expected Response (200 OK):**
```json
{
  "id": "<uuid>",
  "title": "BRD Generation - Retail Banking",
  "role": "Business Analyst (BA)",
  "user_id": "u1",
  "created_at": "<iso-timestamp>"
}
```

**Assertions:**
- `status_code == 200`
- `body.id` is a valid UUID (non-null)
- `body.title == "BRD Generation - Retail Banking"`
- `body.user_id == "u1"`
- DB: `chat_sessions` row created with matching data

---

### TC-API-008 — POST /chat/sessions — Missing Body Fields

| Field | Value |
|---|---|
| **Priority** | Medium |
| **Endpoint** | `POST /chat/sessions` |

**Request (title omitted):**
```json
{ "user_id": "u1", "role": "Business Analyst (BA)" }
```

**Assertions:**
- `status_code == 422`
- `body.detail` references `"title"` field

---

### TC-API-009 — GET /chat/sessions — Retrieve Sessions for a User

| Field | Value |
|---|---|
| **Priority** | Critical |
| **Endpoint** | `GET /chat/sessions?user_id=u1` |
| **SAD Reference** | §4.5, §6 |

**Expected Response (200 OK):**
```json
[
  {
    "id": "...",
    "title": "...",
    "role": "...",
    "user_id": "u1",
    "created_at": "..."
  }
]
```

**Assertions:**
- `status_code == 200`
- All returned sessions have `user_id == "u1"`
- Sessions ordered by `created_at` descending (newest first)
- Other user's sessions are NOT present

---

### TC-API-010 — GET /chat/sessions/{session_id}/messages — Load Session History

| Field | Value |
|---|---|
| **Priority** | Critical |
| **Endpoint** | `GET /chat/sessions/{session_id}/messages` |
| **SAD Reference** | §4.4, §6.2 |

**Precondition:** At least one message pair sent in session.

**Expected Response (200 OK):**
```json
[
  { "id": "...", "role": "user", "content": "...", "created_at": "..." },
  { "id": "...", "role": "assistant", "content": "...", "created_at": "..." }
]
```

**Assertions:**
- `status_code == 200`
- Messages ordered ascending by `created_at`
- `role` values are only `"user"` or `"assistant"`
- `content` fields are non-empty

---

## CHAT QUERY ENDPOINTS

---

### TC-API-011 — POST /chat/query — Standard Non-Streaming

| Field | Value |
|---|---|
| **Priority** | Critical |
| **Endpoint** | `POST /chat/query` |
| **SAD Reference** | §6.2, `chat.py` |

**Request:**
```json
{
  "user_id": "u1",
  "session_id": "<valid_session_id>",
  "role": "Business Analyst (BA)",
  "query": "What are the key business requirements in the uploaded BRD?",
  "task_type": "BRD",
  "context_files": []
}
```

**Expected Response (200 OK):**
```json
{
  "response": "<non-empty AI text>",
  "source_documents": ["None"],
  "session_id": "<session_id>"
}
```

**Assertions:**
- `status_code == 200`
- `body.response` is a non-empty string
- `body.session_id` matches request `session_id`
- DB: 2 new `chat_messages` rows (user + assistant) created

---

### TC-API-012 — POST /chat/query — task_type Routing

| Field | Value |
|---|---|
| **Priority** | High |
| **Endpoint** | `POST /chat/query` |
| **SAD Reference** | §5.3 Role-Specific Conditions |

| task_type | Role | Expected Response Structure |
|---|---|---|
| `"BRD"` | BA | BRD sections: Purpose, Background, Scope, Stakeholders, Requirements |
| `"FRD"` | FBA | FRD sections: Functional Requirements (shall), Interface Specs, Data Dictionary |
| `"Test Plan"` | QA | Test Pack table: Test ID, Scenario, Preconditions, Steps, Expected Result, Priority |
| `null` | Any | General Q&A response; no specific doc structure |

**Assertions:** Response content and structure matches task_type.

---

### TC-API-013 — POST /chat/query — Missing Required Field

| Field | Value |
|---|---|
| **Priority** | Medium |
| **Endpoint** | `POST /chat/query` |

**Request (query field omitted):**
```json
{
  "user_id": "u1",
  "session_id": "<id>",
  "role": "Business Analyst (BA)"
}
```

**Assertions:**
- `status_code == 422`
- `body.detail` references `"query"` field

---

### TC-API-014 — POST /chat/query — Invalid session_id

| Field | Value |
|---|---|
| **Priority** | High |
| **Endpoint** | `POST /chat/query` |

**Request:**
```json
{
  "user_id": "u1",
  "session_id": "non-existent-session-999",
  "role": "Business Analyst (BA)",
  "query": "Hello",
  "task_type": null,
  "context_files": []
}
```

**Assertions:**
- `status_code` in `[404, 500]`
- `body.detail` is a non-empty error string
- No orphaned `chat_messages` rows created (rollback verified)

---

### TC-API-015 — POST /chat/query/stream — Real-Time Streaming

| Field | Value |
|---|---|
| **Priority** | Critical |
| **Endpoint** | `POST /chat/query/stream` |
| **SAD Reference** | §6.2 Steps 16–20 |

**Request:** Same as TC-API-011.

**Expected Response:**
- HTTP 200
- `Content-Type: text/plain`
- Body delivered as progressive text chunks
- Chunks concatenated = coherent, non-empty response

**Assertions:**
- `status_code == 200`
- `Content-Type == "text/plain"`
- Each chunk is a non-empty string fragment
- After stream ends: `chat_messages` row for `role='assistant'` committed to DB
- `created_at` of assistant message is after user message `created_at`

---

### TC-API-016 — POST /chat/query/stream — Error in Stream Handled Gracefully

| Field | Value |
|---|---|
| **Priority** | High |
| **Endpoint** | `POST /chat/query/stream` |
| **SAD Reference** | §6.2 Step 21 |

**Precondition:** Ollama server unreachable.

**Expected Result:**
- Stream sends error chunk: `"Error in stream: <message>"`
- DB rolled back: no partial assistant message stored
- HTTP status still 200 (streaming already started) but error text in body

---

### TC-API-017 — POST /chat/query — SQL Injection Prevention

| Field | Value |
|---|---|
| **Priority** | Critical |
| **Endpoint** | `POST /chat/query` |
| **SAD Reference** | §6.2 Step 14 — query sanitised; SQLAlchemy ORM used |

**Request:**
```json
{
  "user_id": "u1",
  "session_id": "' OR '1'='1",
  "role": "Business Analyst (BA)",
  "query": "DROP TABLE chat_messages; --",
  "task_type": null
}
```

**Assertions:**
- `status_code` in `[404, 422, 500]` — NOT 200
- `chat_messages` table still intact after request
- SQLAlchemy ORM prevents raw SQL execution

---

## DOCUMENT ENDPOINTS

---

### TC-API-018 — POST /documents/upload — Valid PDF

| Field | Value |
|---|---|
| **Priority** | Critical |
| **Endpoint** | `POST /documents/upload` |
| **Content-Type** | `multipart/form-data` |
| **SAD Reference** | §6.1 Document Ingestion |

**Form Data:** `file = <requirements.pdf binary>`

**Expected Response (200 OK):**
```json
{
  "id": "<uuid>",
  "filename": "requirements.pdf",
  "file_size": <bytes>,
  "file_type": "pdf",
  "status": "Successfully uploaded and indexed in knowledge base"
}
```

**Assertions:**
- `status_code == 200`
- `body.filename == "requirements.pdf"`
- `body.file_type == "pdf"`
- `body.status` contains `"indexed"`
- `body.id` is a valid UUID
- DB: `Document` row with `status='indexed'`
- File exists on disk at `uploaded_docs/requirements.pdf`

---

### TC-API-019 — POST /documents/upload — Valid DOCX

| Field | Value |
|---|---|
| **Priority** | High |
| **Endpoint** | `POST /documents/upload` |

**Form Data:** `file = <FRD.docx binary>`

**Assertions:**
- `status_code == 200`
- `body.file_type == "docx"`

---

### TC-API-020 — POST /documents/upload — Valid CSV

| Field | Value |
|---|---|
| **Priority** | High |
| **Endpoint** | `POST /documents/upload` |

**Form Data:** `file = <data.csv binary>`

**Assertions:**
- `status_code == 200`
- `body.file_type == "csv"`

---

### TC-API-021 — POST /documents/upload — No File Provided

| Field | Value |
|---|---|
| **Priority** | Medium |
| **Endpoint** | `POST /documents/upload` |

**Request:** No file field in form data.

**Assertions:**
- `status_code == 422`
- Error message references missing `file` field

---

### TC-API-022 — POST /documents/upload — Unsupported File Type

| Field | Value |
|---|---|
| **Priority** | High |
| **Endpoint** | `POST /documents/upload` |
| **SAD Reference** | §6.1 Step 4 — server-side MIME validation |

**Form Data:** `file = <malware.exe binary>`

**Assertions:**
- `status_code` in `[400, 422, 500]`
- No `Document` row created in DB
- File does not persist in `uploaded_docs/`

---

### TC-API-023 — GET /documents/list — Returns All Documents

| Field | Value |
|---|---|
| **Priority** | High |
| **Endpoint** | `GET /documents/list` |
| **SAD Reference** | §4.3 |

**Expected Response (200 OK):**
```json
{
  "documents": [
    {
      "id": "<uuid>",
      "filename": "requirements.pdf",
      "file_size": 204800,
      "file_type": "pdf",
      "upload_date": "2026-03-26T12:00:00",
      "status": "indexed"
    }
  ]
}
```

**Assertions:**
- `status_code == 200`
- `body.documents` is a list
- List ordered by `upload_date` descending
- Each document has all required fields: `id`, `filename`, `file_size`, `file_type`, `upload_date`, `status`

---

### TC-API-024 — GET /documents/list — Empty List When No Documents

| Field | Value |
|---|---|
| **Priority** | Low |
| **Endpoint** | `GET /documents/list` |

**Precondition:** Fresh environment; no documents uploaded.

**Assertions:**
- `status_code == 200`
- `body.documents == []`

---

## INFRASTRUCTURE / CROSS-CUTTING

---

### TC-API-025 — CORS Headers Present for Frontend Origin

| Field | Value |
|---|---|
| **Priority** | Medium |
| **Endpoint** | `OPTIONS http://localhost:8000/auth/login` |
| **SAD Reference** | §7.1 Tier 1 — Frontend communicates over HTTPS only |

**Assertions:**
- Response contains `Access-Control-Allow-Origin` header
- Value includes `http://localhost:3000` or `*`
- `Access-Control-Allow-Methods` includes `POST, GET, OPTIONS`

---

### TC-API-026 — GET / — Health Check Endpoint

| Field | Value |
|---|---|
| **Priority** | Low |
| **Endpoint** | `GET http://localhost:8000/` |

**Assertions:**
- `status_code == 200`
- Response JSON is non-empty (health status message)

---

### TC-API-027 — API Concurrent Request Integrity

| Field | Value |
|---|---|
| **Priority** | High |
| **Endpoint** | `POST /chat/query` |
| **SAD Reference** | §7 — Four-Tier Architecture |

**Steps:**
1. Create 5 separate sessions for user `u1`.
2. Fire 5 simultaneous POST `/chat/query` requests, each with a distinct `session_id`.

**Assertions:**
- All 5 responses return `status_code == 200`
- Each session contains exactly its own message pair (no cross-session bleed)
- No DB integrity errors or rollbacks

---

### TC-API-028 — API — Rate Limiting / Abuse Prevention

| Field | Value |
|---|---|
| **Priority** | Medium |
| **Endpoint** | `POST /chat/query` |
| **SAD Reference** | §4.4.3 — One in-flight query per session |

**Steps:**
1. Send 2 simultaneous POST `/chat/query` requests for the **same** session_id.

**Assertions:**
- Only one request is processed at a time.
- Second request is either queued, rejected (429), or returns an error message.
- DB contains no duplicate user message rows for the same timestamp.

---

### TC-API-029 — Response Schema Validation — All Endpoints Return Expected Shape

| Field | Value |
|---|---|
| **Priority** | High |
| **SAD Reference** | Pydantic schemas in `chat.py`, `auth.py` |

**Endpoint → Required Fields:**

| Endpoint | Required Response Fields |
|---|---|
| POST /auth/login | `token`, `role`, `user_id` |
| POST /chat/sessions | `id`, `title`, `role`, `user_id`, `created_at` |
| GET /chat/sessions | Array of `id`, `title`, `role`, `user_id`, `created_at` |
| GET /chat/sessions/{id}/messages | Array of `id`, `role`, `content`, `created_at` |
| POST /chat/query | `response`, `source_documents`, `session_id` |
| POST /documents/upload | `id`, `filename`, `file_size`, `file_type`, `status` |
| GET /documents/list | `documents` array with full metadata |

**Assertion:** No required field is missing or `null` in any success (2xx) response.

---

### TC-API-030 — All Endpoints Return JSON Content-Type (except /query/stream)

| Field | Value |
|---|---|
| **Priority** | Medium |

**Assertions for each endpoint:**
- `Content-Type: application/json` in response headers for all endpoints **except** `/chat/query/stream`.
- `/chat/query/stream` returns `Content-Type: text/plain`.

---

*Total API Test Cases: **30***

---

## Summary

| Endpoint Group | Test Count |
|---|---|
| Auth (`/auth/*`) | 6 |
| Chat Sessions (`/chat/sessions`) | 4 |
| Chat Query (`/chat/query`, `/query/stream`) | 7 |
| Documents (`/documents/*`) | 7 |
| Infrastructure / Cross-Cutting | 6 |
| **Total** | **30** |
