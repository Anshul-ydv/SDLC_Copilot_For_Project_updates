# UI Test Cases — HSBC SDLC Automation Copilot
**Document Version:** 1.0  
**Date:** 2026-03-26  
**Reference:** SAD §4 (Screen Specifications), §5 (Roles), Codebase: `ChatWindow.tsx`, `Sidebar.tsx`, `ReferencePanel.tsx`

---

## TC-UI-001 — Login Page Renders Correctly

| Field | Value |
|---|---|
| **Priority** | High |
| **Module** | Login Screen |
| **SAD Reference** | §4.1 Login Screen |

**Preconditions:** Application running at `http://localhost:3000`

**Steps:**
1. Navigate to `http://localhost:3000`.
2. Observe the rendered page.

**Expected Result:**
- Login form visible with Email field, Password field, and Login button.
- HSBC branding / logo displayed.
- No console errors.

---

## TC-UI-002 — Login With Valid BA Credentials

| Field | Value |
|---|---|
| **Priority** | Critical |
| **Module** | Login Screen → Dashboard |
| **SAD Reference** | §4.1, §5.1 |

**Steps:**
1. Enter `ba@hsbc.com` / `password123`.
2. Click **Login**.

**Expected Result:**
- Redirected to main workspace dashboard.
- Sidebar and chat window rendered.
- Role label shows **"Business Analyst (BA)"**.
- No error messages.

---

## TC-UI-003 — Login With FBA Credentials

| Field | Value |
|---|---|
| **Priority** | High |
| **Module** | Login Screen → Dashboard |
| **SAD Reference** | §5.1 |

**Steps:**
1. Enter `fba@hsbc.com` / `password123`. Click **Login**.

**Expected Result:**
- Role label shows **"Functional BA (FBA)"**.
- Dashboard renders correctly.

---

## TC-UI-004 — Login With QA Credentials

| Field | Value |
|---|---|
| **Priority** | High |
| **Module** | Login Screen → Dashboard |
| **SAD Reference** | §5.1 |

**Steps:**
1. Enter `qa@hsbc.com` / `password123`. Click **Login**.

**Expected Result:**
- Role label shows **"QA / Tester"**.
- Dashboard renders correctly.

---

## TC-UI-005 — Login With Invalid Credentials

| Field | Value |
|---|---|
| **Priority** | High |
| **Module** | Login Screen — Error Handling |
| **SAD Reference** | §4.1 Validations |

**Steps:**
1. Enter `invalid@hsbc.com` / `wrongpassword`.
2. Click **Login**.

**Expected Result:**
- Error message: `"Invalid credentials"` displayed.
- User stays on Login page. No redirect.

---

## TC-UI-006 — Login With Empty Fields

| Field | Value |
|---|---|
| **Priority** | Medium |
| **Module** | Login Screen — Validation |
| **SAD Reference** | §4.1 Validations |

**Steps:**
1. Leave Email and Password empty.
2. Click **Login**.

**Expected Result:**
- Field-level validation messages shown.
- No API call made (verified via Network tab).

---

## TC-UI-007 — Role Selector Modal on New Session

| Field | Value |
|---|---|
| **Priority** | High |
| **Module** | Role Selector Modal |
| **SAD Reference** | §4.2, §4.5 New Session Button |

**Steps:**
1. Log in.
2. Click **+ New Session** in the Sidebar.

**Expected Result:**
- Role Selector modal opens.
- Three options: BA, FBA, QA are visible.
- Session is created only after a role is selected.

---

## TC-UI-008 — Document Upload Drop Zone Renders

| Field | Value |
|---|---|
| **Priority** | High |
| **Module** | Document Upload Panel |
| **SAD Reference** | §4.3 Document Upload Panel |

**Steps:**
1. Log in and open or create a session.
2. Observe the Document Upload area.

**Expected Result:**
- An "Upload & Process" button (or drop zone) is visible.
- Accepted file types label shows PDF, DOCX, CSV.
- File size limit is communicated (e.g., max 20 MB).

---

## TC-UI-009 — Upload Valid PDF File

| Field | Value |
|---|---|
| **Priority** | Critical |
| **Module** | Document Upload Panel |
| **SAD Reference** | §4.3, §6.1 Document Ingestion Flow |

**Steps:**
1. Click **Browse Files** / drop a valid PDF.
2. Click **Upload & Process**.

**Expected Result:**
- File appears in the documents list with status **"Processing"** then **"Ready"** (indexed).
- Toast or success message shown.
- File name, type (pdf), and size displayed.

---

## TC-UI-010 — Upload Invalid File Type (e.g., .exe)

| Field | Value |
|---|---|
| **Priority** | High |
| **Module** | Document Upload Panel — Client Validation |
| **SAD Reference** | §4.3 Validations, §6.1 Step 2 |

**Steps:**
1. Attempt to upload a `.exe` file.

**Expected Result:**
- Upload is **blocked client-side** before any server call.
- Inline error toast: file type not supported.
- No POST request sent to server (verified in Network tab).

---

## TC-UI-011 — "No Documents" Banner When Session Has No Files

| Field | Value |
|---|---|
| **Priority** | High |
| **Module** | Chat Window — Functional Conditions |
| **SAD Reference** | §4.4.4 Functional Conditions |

**Steps:**
1. Create a new session without uploading any documents.
2. Observe the chat window.

**Expected Result:**
- Yellow warning banner shown: `"Please upload at least one reference document before sending a query."`
- Send button is **disabled**.

---

## TC-UI-012 — Chat Message Query Length Validation

| Field | Value |
|---|---|
| **Priority** | High |
| **Module** | Chat Window — Message Input |
| **SAD Reference** | §4.4 Validations, §6.2 Step 12 |

**Scenarios:**
| Scenario | Input Length | Expected |
|---|---|---|
| Normal | 100 chars | Send allowed |
| Near-limit warning | 3,800 chars | Character counter turns red |
| At limit | 4,001 chars | Send disabled; tooltip shows |
| Empty/whitespace | 0–spaces | Send button stays disabled |

---

## TC-UI-013 — Send Message and Receive AI Streaming Response

| Field | Value |
|---|---|
| **Priority** | Critical |
| **Module** | Chat Window — Streaming |
| **SAD Reference** | §4.4, §6.2 RAG Query Flow |

**Preconditions:** Session active with at least one uploaded document.

**Steps:**
1. Type `"Generate a BRD for a retail banking feature"`.
2. Press **Enter** or click **Send**.

**Expected Result:**
- User message appears immediately in chat.
- AI response streams token-by-token (visible typewriter effect).
- Response prefixed with `[BA Context]` (or appropriate role context tag).
- Send button disabled and input locked during streaming.
- After stream ends: both messages saved; send button re-enabled.

---

## TC-UI-014 — AI Response Feedback (Thumbs Up / Down)

| Field | Value |
|---|---|
| **Priority** | Medium |
| **Module** | Chat Window — Feedback |
| **SAD Reference** | §4.4.2 UI Elements (Feedback Buttons), §4.4.4 |

**Steps:**
1. Send a query; receive AI response.
2. Click the **thumbs-down** icon on the assistant message.

**Expected Result:**
- Optional correction text field appears (max 500 characters).
- Submitting stores feedback in the Feedback table.
- Thumbs-up click stores positive feedback without extra input.

---

## TC-UI-015 — Session Title — Auto-Generated and Editable

| Field | Value |
|---|---|
| **Priority** | Medium |
| **Module** | Chat Window — Session Title |
| **SAD Reference** | §4.4.2 Session Title, §4.5.3 Validations |

**Steps:**
1. Create a session and send the first message.
2. Observe the session title in the chat header.
3. Click the title to edit it.
4. Type a new name (3–80 characters) and press **Enter**.

**Expected Result:**
- Title auto-generated from first query (max 80 chars, truncated with ellipsis).
- Edit mode opens inline. Saved on Enter or focus loss.
- Title under 3 chars shows error: `"Title must be 3–80 characters"`.

---

## TC-UI-016 — Session History Sidebar — Session List

| Field | Value |
|---|---|
| **Priority** | High |
| **Module** | Session History Sidebar |
| **SAD Reference** | §4.5 |

**Steps:**
1. Log in with multiple existing sessions.
2. Observe the sidebar.

**Expected Result:**
- Sessions listed in descending order (newest first).
- Each card shows session title and creation info.
- "X sessions" counter visible in sidebar header.

---

## TC-UI-017 — Session Search (Debounced)

| Field | Value |
|---|---|
| **Priority** | Medium |
| **Module** | Session History Sidebar — Search |
| **SAD Reference** | §4.5.2 Session Search Input |

**Steps:**
1. Type in the session search box using 1 character (e.g., `"B"`).
2. Type 2 characters (e.g., `"BR"`).

**Expected Result:**
- 1 character: no filtering triggered.
- 2+ characters: filtered list updates after 300 ms debounce.
- Max search input: 100 characters.

---

## TC-UI-018 — Delete Session With Confirmation

| Field | Value |
|---|---|
| **Priority** | Medium |
| **Module** | Session History Sidebar — Delete |
| **SAD Reference** | §4.5.2 Delete Session Button, §4.5.3 |

**Steps:**
1. Hover over a session card; click the trash icon.
2. Observe the confirmation dialog.
3. Click **Delete** (red button).

**Expected Result:**
- Confirmation dialog: `"Delete this session and all its messages? This action cannot be undone."`
- Clicking Cancel: dialog closes, session remains.
- Clicking Delete: session soft-deleted; removed from list.

---

## TC-UI-019 — Logout Clears State and Redirects

| Field | Value |
|---|---|
| **Priority** | High |
| **Module** | Header / Sidebar — Logout |
| **SAD Reference** | §4.1, `useAppStore.ts` clearUser() |

**Steps:**
1. Log in. Click **Logout**.

**Expected Result:**
- Zustand store cleared (userId, role, token = null).
- Redirected to Login page.
- Back-navigation does not expose protected content.

---

## TC-UI-020 — Copy Response to Clipboard

| Field | Value |
|---|---|
| **Priority** | Low |
| **Module** | Chat Window — Action Buttons |
| **SAD Reference** | §5.2 Role × Functionality Matrix |

**Steps:**
1. Receive an AI response.
2. Click the **Copy to Clipboard** icon.

**Expected Result:**
- Response text is copied to clipboard (all roles: BA, FBA, QA).
- A brief confirmation tooltip/toast appears.

---

## TC-UI-021 — Export Response as Markdown

| Field | Value |
|---|---|
| **Priority** | Low |
| **Module** | Chat Window — Export |
| **SAD Reference** | §5.2 Role × Functionality Matrix |

**Steps:**
1. Receive an AI response.
2. Click **Export as Markdown (.md)**.

**Expected Result:**
- A `.md` file download is triggered.
- File content matches the assistant's response text.
- Available to all three roles.

---

## TC-UI-022 — Concurrent Query Prevention

| Field | Value |
|---|---|
| **Priority** | High |
| **Module** | Chat Window — Input Validation |
| **SAD Reference** | §4.4.3 Validations — Concurrent queries |

**Steps:**
1. Send a query; while the response is still streaming, attempt to send another query.

**Expected Result:**
- Send button remains disabled while a response is streaming.
- Input box is locked.
- Second query cannot be submitted until streaming finishes.

---

## TC-UI-023 — Ollama Unavailable — Inline Error Message

| Field | Value |
|---|---|
| **Priority** | High |
| **Module** | Chat Window — Error Handling |
| **SAD Reference** | §4.4.4 Functional Conditions, §6.2 Step 21 |

**Precondition:** Ollama inference server is stopped/unreachable.

**Steps:**
1. Send a query.

**Expected Result:**
- Inline error: `"The AI model is currently unavailable. Please contact your administrator."`
- Timeout after 30 seconds if no token is received.

---

## TC-UI-024 — Session Limit Warning (200 Sessions)

| Field | Value |
|---|---|
| **Priority** | Low |
| **Module** | Session History Sidebar |
| **SAD Reference** | §4.5.3 — Max 200 active sessions per user |

**Precondition:** User has 200 active sessions.

**Steps:**
1. Attempt to create a 201st session.

**Expected Result:**
- Notice displayed: `"Session limit reached. Oldest inactive sessions are archived automatically."`
- Oldest inactive session is auto-archived.

---

## TC-UI-025 — Responsive Layout at Tablet / Mobile Widths

| Field | Value |
|---|---|
| **Priority** | Low |
| **Module** | Overall Layout |

**Steps:**
1. Resize browser window to 768 px (tablet).
2. Resize to 375 px (mobile).

**Expected Result:**
- At 768 px: Sidebar collapses or overlays; content adjusts.
- At 375 px: All critical actions accessible; no horizontal scrollbar.

---

*Total UI Test Cases: **25***
