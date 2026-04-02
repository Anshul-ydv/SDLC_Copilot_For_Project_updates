# Integration Test Cases — HSBC SDLC Automation Copilot
**Document Version:** 1.0  
**Date:** 2026-03-26  
**Reference:** SAD §6 (Data Flow), §7 (Architecture), §8; Codebase: `chat.py`, `documents.py`, `auth.py`, `rag_service.py`, `useAppStore.ts`

---

## TC-INT-001 — Frontend Login Calls Backend Auth API

| Field | Value |
|---|---|
| **Priority** | Critical |
| **Components** | Next.js Login Page ↔ `POST /auth/login` |
| **SAD Reference** | §4.1, §6 |

**Steps:**
1. Open browser Network tab.
2. Enter `ba@hsbc.com` / `password123` and click **Login**.

**Expected Result:**
- `POST http://localhost:8000/auth/login` is fired.
- Request body: `{ "email": "ba@hsbc.com", "password": "password123" }`.
- Response 200: `{ "token": "...", "role": "Business Analyst (BA)", "user_id": "u1" }`.
- Zustand store (`useAppStore`) updated: `user.token`, `user.role`, `user.userId` set.
- User redirected to dashboard.

---

## TC-INT-002 — New Session Created in Backend When Clicking "+ New Session"

| Field | Value |
|---|---|
| **Priority** | Critical |
| **Components** | `Sidebar.tsx` ↔ `POST /chat/sessions` ↔ SQLite |
| **SAD Reference** | §4.5, §6 |

**Steps:**
1. Log in. Click **+ New Session**, select a role.

**Expected Result:**
- `POST http://localhost:8000/chat/sessions` fired with `{ user_id, role, title }`.
- Response 200 with session UUID, title, created_at.
- New session appears at the top of the Sidebar list.
- `useAppStore.activeSessionId` set to the new session's ID.

---

## TC-INT-003 — Chat Query Saved to SQLite as User + Assistant Messages

| Field | Value |
|---|---|
| **Priority** | Critical |
| **Components** | `ChatWindow.tsx` ↔ `POST /chat/query` ↔ SQLite |
| **SAD Reference** | §6.2, `chat.py` |

**Steps:**
1. Send message: `"Summarize the uploaded BRD"`.
2. Receive AI response.
3. Query SQLite: `SELECT * FROM chat_messages WHERE session_id='<id>'`.

**Expected Result:**
- Two rows exist: `role='user'` and `role='assistant'`.
- Content matches sent query and AI response.
- `created_at` timestamps are ordered correctly.

---

## TC-INT-004 — Streaming Response Delivered via `/query/stream` and Saved After Completion

| Field | Value |
|---|---|
| **Priority** | Critical |
| **Components** | `ChatWindow.tsx` ↔ `POST /chat/query/stream` ↔ SQLite |
| **SAD Reference** | §6.2, `chat.py` streaming endpoint |

**Steps:**
1. Send a query via the chat window (streaming mode).
2. Monitor Network tab while streaming.
3. After stream ends, check DB.

**Expected Result:**
- Response arrives as `text/plain` streaming chunks.
- Chunks appear incrementally in the UI.
- **After** stream ends: one `role='assistant'` message row committed to SQLite.
- Refreshing the session loads the complete message.

---

## TC-INT-005 — Document Upload Triggers RAG Ingestion Pipeline

| Field | Value |
|---|---|
| **Priority** | Critical |
| **Components** | Upload UI ↔ `POST /documents/upload` ↔ `rag_service.process_file()` ↔ ChromaDB/Qdrant |
| **SAD Reference** | §6.1 Document Ingestion Flow Steps 1–10 |

**Steps:**
1. Upload a PDF containing keyword "BASBA Phase 2".

**Expected Result:**
- File saved to `uploaded_docs/` on disk.
- `Document` record inserted in SQLite with `status='uploaded'` initially.
- `rag_service.process_file()` called (PDF chunked + embedded + stored in vector DB).
- `Document.status` updated to `'indexed'`.
- Response body confirms `"Successfully uploaded and indexed in knowledge base"`.

---

## TC-INT-006 — RAG Retrieval Returns Contextually Relevant Chunks

| Field | Value |
|---|---|
| **Priority** | Critical |
| **Components** | `POST /chat/query` ↔ `rag_service.generate_answer()` ↔ ChromaDB ↔ Gemini/Ollama |
| **SAD Reference** | §6.2 Steps 15–18, §7.2 |

**Steps:**
1. Upload a document with sentence: `"OAuth 2.0 is mandatory for all API access"`.
2. Ask: `"What authentication protocol is required for APIs?"`.

**Expected Result:**
- RAG service encodes query into 384-dim vector (MiniLM).
- Vector similarity search retrieves chunk containing "OAuth 2.0".
- Retrieved context injected into LLM prompt.
- AI response references "OAuth 2.0".

---

## TC-INT-007 — Session History Loads from Backend on Sidebar Navigation

| Field | Value |
|---|---|
| **Priority** | High |
| **Components** | `Sidebar.tsx` ↔ `GET /chat/sessions?user_id=<id>` ↔ `GET /chat/sessions/{id}/messages` |
| **SAD Reference** | §4.5, §6 |

**Steps:**
1. Log in. Sidebar auto-fetches session list.
2. Click on a past session.

**Expected Result:**
- `GET /chat/sessions?user_id=u1` returns sessions ordered newest-first.
- `GET /chat/sessions/{session_id}/messages` returns messages ordered ascending.
- Chat window renders historical messages in correct order.

---

## TC-INT-008 — Session Isolation: User A Sessions Not Visible to User B

| Field | Value |
|---|---|
| **Priority** | Critical |
| **Components** | `GET /chat/sessions` ↔ SQLite — user_id filter |
| **SAD Reference** | §4.5.3, §5.2 Role Matrix ("View other users' sessions: ✗") |

**Steps:**
1. Log in as BA (user_id=`u1`), create 2 sessions.
2. Log out. Log in as QA (user_id=`u3`).
3. Observe Sidebar session list.

**Expected Result:**
- QA user sees **only** their own sessions.
- BA's sessions are absent.
- Confirmed by `GET /chat/sessions?user_id=u3` returning sessions where `user_id='u3'` only.

---

## TC-INT-009 — Zustand Store State Reflects Full Auth Flow

| Field | Value |
|---|---|
| **Priority** | High |
| **Components** | `useAppStore.ts` ↔ `auth.py` |
| **SAD Reference** | §4.1, `useAppStore.ts` |

**Steps:**
1. Log in as FBA. Open React DevTools (Zustand store).

**Expected Result:**
- `user.userId = "u2"`
- `user.email = "fba@hsbc.com"`
- `user.role = "Functional BA (FBA)"`
- `user.token = "mock-jwt-token-for-Functional BA (FBA)"`
- `activeSessionId = null` (before any session selected)

---

## TC-INT-010 — Logout Clears Zustand Store Completely

| Field | Value |
|---|---|
| **Priority** | High |
| **Components** | `useAppStore.clearUser()` |
| **SAD Reference** | `useAppStore.ts` |

**Steps:**
1. Log in. Verify store has user data.
2. Click **Logout**.
3. Inspect store.

**Expected Result:**
- `user.userId = null`
- `user.role = null`
- `user.token = null`
- `activeSessionId = null`
- `documents = []`

---

## TC-INT-011 — Document List Populates Store and UI on Panel Open

| Field | Value |
|---|---|
| **Priority** | High |
| **Components** | `ReferencePanel.tsx` ↔ `GET /documents/list` ↔ `useAppStore.setDocuments()` |
| **SAD Reference** | §4.3 |

**Steps:**
1. Log in (with prior uploads). Open Reference Panel.
2. Monitor Network tab.

**Expected Result:**
- `GET /documents/list` is called automatically.
- Response populates `useAppStore.documents`.
- UI renders document list matching the API response.

---

## TC-INT-012 — Client-Side Validation Prevents Server Call for Invalid Uploads

| Field | Value |
|---|---|
| **Priority** | High |
| **Components** | Upload UI ↔ Client-Side Validation (SAD §6.1 Step 2) |
| **SAD Reference** | §6.1 Step 2 |

**Steps:**
1. Attempt to upload a `.png` file.
2. Monitor Network tab.

**Expected Result:**
- No `POST /documents/upload` request is fired.
- Inline error toast displayed.
- File is rejected purely client-side.

---

## TC-INT-013 — JWT Token Passed in Request Headers for Protected Endpoints

| Field | Value |
|---|---|
| **Priority** | High |
| **Components** | Frontend Fetch ↔ FastAPI JWT Validation |
| **SAD Reference** | §6.2 Step 14 |

**Steps:**
1. Log in. Send a chat query.
2. Inspect the Network request headers for `POST /chat/query/stream`.

**Expected Result:**
- `Authorization: Bearer <token>` header is present.
- Backend validates the JWT before processing.
- Request without token returns HTTP 401/403.

---

## TC-INT-014 — Session Ownership Check (HTTP 403 on Mismatched Session)

| Field | Value |
|---|---|
| **Priority** | High |
| **Components** | `POST /chat/query/stream` ↔ FastAPI session ownership check |
| **SAD Reference** | §6.2 Step 14 |

**Steps:**
1. Log in as BA. Get a session_id belonging to QA user.
2. POST to `/chat/query/stream` with that session_id.

**Expected Result:**
- HTTP 403 returned: session does not belong to authenticated user.

---

## TC-INT-015 — Document Upload addDocument Reflects Instantly in UI Without Full Page Refresh

| Field | Value |
|---|---|
| **Priority** | Medium |
| **Components** | `useAppStore.addDocument()` ↔ Upload response |
| **SAD Reference** | `useAppStore.ts`, §4.3 |

**Steps:**
1. Upload a new document.
2. Observe the document list without refreshing.

**Expected Result:**
- New document appears at the top of the list immediately.
- `useAppStore.addDocument()` adds to store without re-fetching full list.

---

*Total Integration Test Cases: **15***
