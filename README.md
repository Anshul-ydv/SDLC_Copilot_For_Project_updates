# SDLC Automation Copilot

An enterprise-grade AI-powered Retrieval-Augmented Generation (RAG) platform that revolutionizes Software Development Lifecycle (SDLC) documentation creation. Designed for Business Analysts (BAs), Functional Business Analysts (FBAs), and Quality Assurance (QA) engineers to generate high-fidelity Business Requirement Documents (BRDs), Functional Requirement Documents (FRDs), and comprehensive Test Packs.

**NEW in v2.1.0**: Integrated MCP (Model Context Protocol) Multi-Agent Pipeline for advanced document processing with 5 specialized AI agents!

**Latest Updates (April 2026)**:
- ✅ All deprecations fixed (Python 3.12+, Pydantic v2, SQLAlchemy 2.0 compatible)
- ✅ HuggingFace token integration for faster model downloads
- ✅ 100% cloud-native architecture (PostgreSQL, Pinecone, Qdrant)
- ✅ Zero local database overhead

---

## 🚀 Quick Start

```bash
# 1. Clone and setup
cd backend
python3 -m venv ../.venv
source ../.venv/bin/activate
pip install -r requirements.txt

# 2. Configure .env (see Configuration section)
cp .env.example .env
# Edit .env with your API keys

# 3. Start backend
python -m uvicorn main:app --reload

# 4. Start frontend (new terminal)
cd frontend
npm install
npm run dev

# 5. Login at http://localhost:3000
# Email: ba@hsbc.com | Password: password123
```

**API Docs**: http://localhost:8000/docs

---

## Table of Contents

1. [What is This Project?](#what-is-this-project)
2. [Why Use This?](#why-use-this)
3. [When to Use This?](#when-to-use-this)
4. [How to Get Started](#how-to-get-started)
5. [MCP Multi-Agent Pipeline](#mcp-multi-agent-pipeline) ⭐ NEW
6. [System Architecture](#system-architecture)
7. [Technology Stack](#technology-stack)
8. [Project Structure](#project-structure)
9. [API Documentation](#api-documentation)
10. [Authentication](#authentication)
11. [Database Setup](#database-setup)
12. [Configuration](#configuration)
13. [Running the Application](#running-the-application)
14. [Testing](#testing)
15. [Troubleshooting](#troubleshooting)
16. [Future Enhancements](#future-enhancements)

---

## What is This Project?

The SDLC Automation Copilot is an intelligent workspace that combines:

- **AI-Powered Generation**: Uses OpenRouter's Gemma 2 27B model for high-quality, comprehensive document generation
- **Semantic Search**: Retrieves relevant context from your documents using vector embeddings
- **Role-Based Customization**: Generates content tailored to BA, FBA, or QA perspectives
- **Session Management**: Maintains persistent chat histories and document versions
- **Real-time Streaming**: Provides token-by-token response streaming for interactive experience
- **Session-Based Isolation**: Documents are filtered by session for complete data isolation

### Core Capabilities

| Feature | Description |
|---------|-------------|
| **Document Upload** | Ingest PDF, DOCX, CSV files for knowledge base |
| **Semantic Search** | Find relevant content using AI-powered similarity matching |
| **Role-Based Generation** | Generate BRDs, FRDs, or Test Packs based on user role |
| **Session Persistence** | Save and retrieve chat histories across sessions |
| **Feedback System** | Rate generated content and get AI improvement suggestions |
| **Real-time Streaming** | Stream responses token-by-token for interactive experience |
| **MCP Multi-Agent Pipeline** | Process documents through 5 specialized AI agents for comprehensive analysis |

---

## Why Use This?

### Problems It Solves

| Problem | Solution |
|---------|----------|
| **Time-Consuming Documentation** | Generate requirements in minutes instead of days |
| **Inconsistent Quality** | Maintain unified tone and structure across documents |
| **Manual Errors** | AI-powered generation reduces human mistakes |
| **Context Loss** | RAG ensures all content is grounded in source materials |
| **Role Confusion** | Role-based generation ensures appropriate technical depth |

### Key Benefits

- **Accelerated Throughput**: Reduce documentation time from days to minutes
- **Consistency**: Unified tone and structure across all documents
- **Traceability**: Every requirement grounded in source documentation
- **Role Optimization**: Content tailored to BA, FBA, or QA needs
- **Iterative Refinement**: Save, review, and improve generated content
- **Enterprise-Grade**: Secure, scalable, production-ready architecture
- **Session Isolation**: Complete data separation between sessions  

---

## When to Use This?

### Ideal Use Cases

1. **New Project Kickoff**
   - Generate initial BRD from business requirements
   - Create FRD from business specifications
   - Develop comprehensive test pack

2. **Requirements Refinement**
   - Iterate on existing requirements
   - Generate alternative versions
   - Get AI-powered improvement suggestions

3. **Documentation Backlog**
   - Quickly document legacy systems
   - Create missing documentation
   - Standardize existing documents

4. **Cross-Functional Collaboration**
   - BA generates business requirements
   - FBA creates technical specifications
   - QA develops test strategies

### Not Suitable For

- Real-time code generation
- Architectural decision making (requires human expertise)
- Security-critical documentation (requires manual review)
- Highly specialized domain knowledge (requires expert input)  

---

## How to Get Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL database (Render or Neon recommended)
- OpenRouter API key (free tier available)
- Pinecone API key (for vector search)
- Qdrant Cloud account (for document storage)

### Quick Start (5 minutes)

#### 1. Clone and Setup Backend

```bash
cd backend
python3 -m venv ../.venv
source ../.venv/bin/activate  # Windows: ..\.venv\Scripts\activate
pip install -r requirements.txt
```

#### 2. Configure Environment

Create `backend/.env`:

```env
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# LLM: OpenRouter (Gemma 2 27B)
OPENROUTER_API_KEY=your_openrouter_api_key_here

# JWT Authentication
JWT_SECRET_KEY=your_secret_key_here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Vector Store: Pinecone
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX_NAME=sdlc-copilot

# Document Store: Qdrant Cloud
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_key
QDRANT_COLLECTION_NAME=sdlc_documents
```

#### 3. Start Backend

```bash
cd backend
source ../.venv/bin/activate
../.venv/bin/python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend runs at: `http://localhost:8000`

#### 4. Setup Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: `http://localhost:3000`

#### 5. Login

Use test credentials:
- Email: `ba@hsbc.com`
- Password: `password123`

---

## MCP Multi-Agent Pipeline

### What is MCP?

The **Model Context Protocol (MCP) Multi-Agent Pipeline** is an advanced document processing system that uses 5 specialized AI agents working together to comprehensively analyze and structure documents.

```
Input Document → Reader Agent → [5 Specialist Agents] → Master Receiver → Doc Maker → Output
```

### The 5 Specialist Agents

1. **Requirements Agent (S1)** - Extracts functional and non-functional requirements
2. **Table Analyzer Agent (S2)** - Analyzes table structures and data quality
3. **Business Logic Agent (S3)** - Identifies business rules and process flows
4. **Change Request Agent (S4)** - Tracks version changes and scope deltas
5. **Validation Agent (S5)** - Validates document consistency and completeness

### Quick Start with MCP

```bash
# Install python-docx dependency
pip install python-docx

# Process a document through MCP pipeline
curl -X POST "http://localhost:8000/api/mcp/process" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@requirements.pdf" \
  -F "session_id=test-session" \
  -F "output_format=docx"
```

### What You Get

The MCP pipeline produces:
- **Formatted DOCX document** with cover page, TOC, and professional styling
- **Extracted requirements** with IDs, types, and priorities
- **Analyzed tables** with schemas and anomaly detection
- **Business rules** and process flows
- **Change tracking** with impact analysis
- **Validation report** with quality checks
- **7 intermediate JSON files** for full transparency

### MCP Documentation

- **Quick Start**: `files/MCP_QUICK_START.md` - Get started in 5 minutes
- **Integration Guide**: `files/MCP_INTEGRATION_README.md` - Complete documentation
- **Architecture**: `files/MCP_ARCHITECTURE.md` - System design
- **Implementation**: `files/IMPLEMENTATION_GUIDE.md` - Step-by-step guide

### MCP API Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /api/mcp/process` | Process document through MCP pipeline |
| `GET /api/mcp/download/{session_id}/{filename}` | Download processed document |
| `GET /api/mcp/intermediate/{session_id}/{type}` | Get intermediate JSON outputs |
| `GET /api/mcp/status/{document_id}` | Check processing status |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
│                   (Next.js Frontend)                         │
│  - Chat Interface  - Document Upload  - Session Management  │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS / REST API
┌────────────────────────▼────────────────────────────────────┐
│                  API Layer (FastAPI)                         │
│  - Authentication  - Chat Endpoints  - Document Management  │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼──────┐  ┌──────▼──────┐  ┌────▼──────────┐
│  PostgreSQL  │  │  ChromaDB   │  │  Groq LLM    │
│  (Metadata)  │  │  (Vectors)  │  │  (Inference) │
└──────────────┘  └─────────────┘  └──────────────┘
```

### Data Flow

1. **Document Upload** → Parser → Chunker → Embeddings → ChromaDB
2. **User Query** → Retrieve Context → LLM Prompt → Groq API → Stream Response
3. **Session Management** → Store in PostgreSQL → Retrieve History

---

## Technology Stack

### Frontend
- **Framework**: Next.js 16 (React 19)
- **Styling**: CSS with responsive design
- **State Management**: React Context API
- **Real-time**: Fetch API with ReadableStream

### Backend
- **Framework**: FastAPI (Python)
- **Server**: Uvicorn (ASGI)
- **Database**: SQLAlchemy ORM
- **Authentication**: JWT (JSON Web Tokens)

### AI & ML
- **LLM**: OpenRouter Gemma 2 27B (Free Tier)
- **Context Window**: 16,000 tokens
- **Embeddings**: HuggingFace sentence-transformers/all-MiniLM-L6-v2 (384 dimensions)
- **Vector DB**: Pinecone (Serverless)
- **Document Store**: Qdrant Cloud
- **Orchestration**: LangChain

### Infrastructure
- **Database**: PostgreSQL (Render) - Cloud-hosted, no local SQLite
- **Vector Search**: Pinecone (Serverless) - Cloud-hosted
- **Document Store**: Qdrant Cloud - Cloud-hosted
- **Embeddings**: HuggingFace sentence-transformers (with HF_TOKEN for faster downloads)
- **Deployment**: Docker-ready
- **Version Control**: Git
- **Architecture**: 100% cloud-native, zero local database overhead

---

## Project Structure

```
project/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py           # JWT authentication endpoints
│   │   │   ├── chat.py           # Chat and session endpoints
│   │   │   └── documents.py      # Document upload and feedback
│   │   ├── services/
│   │   │   ├── rag_service.py    # RAG pipeline
│   │   │   ├── pdf_service.py    # PDF generation
│   │   │   └── feedback_service.py # AI feedback
│   │   ├── utils/
│   │   │   └── auth_utils.py     # JWT utilities
│   │   ├── models.py             # Database models
│   │   └── database.py           # Database config
│   ├── tests/                    # Test suite
│   ├── main.py                   # Entry point
│   ├── requirements.txt          # Python dependencies
│   ├── .env                      # Environment variables
│   └── JWT_AUTH_README.md        # JWT documentation
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx          # Home page
│   │   │   ├── chat/
│   │   │   │   └── page.tsx      # Chat interface
│   │   │   └── layout.tsx        # Root layout
│   │   ├── components/
│   │   │   ├── ChatWindow.tsx    # Chat UI
│   │   │   ├── Sidebar.tsx       # Session sidebar
│   │   │   └── ReferencePanel.tsx # Document references
│   │   └── store/
│   │       └── useAppStore.ts    # State management
│   ├── public/                   # Static assets
│   ├── package.json              # Node dependencies
│   └── next.config.ts            # Next.js config
│
├── testcases/                    # Test documentation
├── SADDOC/                       # Architecture documentation
├── README.md                     # This file
└── .gitignore                    # Git ignore rules
```

---

## API Documentation

### Authentication Endpoints

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "ba@hsbc.com",
  "password": "password123"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "role": "Business Analyst (BA)",
  "user_id": "u1",
  "email": "ba@hsbc.com",
  "expires_in": 30
}
```

#### Get Current User
```http
GET /api/auth/me
Authorization: Bearer {access_token}

Response:
{
  "user_id": "u1",
  "email": "ba@hsbc.com",
  "role": "Business Analyst (BA)"
}
```

### Chat Endpoints

#### Create Session
```http
POST /api/chat/sessions
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "user_id": "u1",
  "role": "Business Analyst (BA)",
  "title": "Project X Requirements"
}

Response:
{
  "id": "session-123",
  "title": "Project X Requirements",
  "role": "Business Analyst (BA)",
  "user_id": "u1",
  "created_at": "2026-04-15T10:30:00"
}
```

#### Get Sessions
```http
GET /api/chat/sessions?user_id=u1
Authorization: Bearer {access_token}

Response:
{
  "sessions": [
    {
      "id": "session-123",
      "title": "Project X Requirements",
      "role": "Business Analyst (BA)",
      "user_id": "u1",
      "created_at": "2026-04-15T10:30:00"
    }
  ]
}
```

#### Send Query (Streaming)
```http
POST /api/chat/query/stream
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "user_id": "u1",
  "session_id": "session-123",
  "role": "Business Analyst (BA)",
  "query": "Generate a BRD for user authentication system",
  "task_type": "brd",
  "context_files": ["doc1.pdf"]
}

Response: Server-Sent Events stream
```

### Document Endpoints

#### Upload Document
```http
POST /api/documents/upload
Authorization: Bearer {access_token}
Content-Type: multipart/form-data

file: <binary>
session_id: session-123

Response:
{
  "id": "doc-123",
  "filename": "requirements.pdf",
  "file_size": 102400,
  "file_type": "pdf",
  "status": "Successfully uploaded and indexed in knowledge base"
}
```

#### List Documents
```http
GET /api/documents/list?session_id=session-123
Authorization: Bearer {access_token}

Response:
{
  "documents": [
    {
      "id": "doc-123",
      "filename": "requirements.pdf",
      "file_size": 102400,
      "file_type": "pdf",
      "upload_date": "2026-04-15T10:30:00",
      "status": "indexed"
    }
  ]
}
```

#### Submit Feedback
```http
POST /api/documents/{document_id}/feedback
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "rating": "thumbs_down",
  "feedback_text": "Missing security requirements",
  "doc_type": "BRD",
  "user_id": "u1"
}

Response:
{
  "status": "success",
  "message": "Feedback submitted successfully",
  "feedback_id": "feedback-123",
  "rating": "thumbs_down",
  "ai_suggestions": "Consider adding: Authentication mechanisms, Authorization levels, Data encryption requirements..."
}
```

---

## Authentication

### JWT Authentication

The project uses JWT (JSON Web Tokens) for secure API authentication.

#### How It Works

1. **Login**: Send credentials to `/api/auth/login`
2. **Receive Token**: Get JWT token in response
3. **Store Token**: Save in localStorage or secure storage
4. **Use Token**: Include in `Authorization: Bearer {token}` header
5. **Token Expiration**: Default 30 minutes, then login again

#### Test Users

| Email | Password | Role |
|-------|----------|------|
| ba@hsbc.com | password123 | Business Analyst (BA) |
| fba@hsbc.com | password123 | Functional BA (FBA) |
| qa@hsbc.com | password123 | QA / Tester |

#### Token Structure

```json
{
  "sub": "u1",                          // User ID
  "email": "ba@hsbc.com",               // User email
  "role": "Business Analyst (BA)",      // User role
  "exp": 1234567890                     // Expiration timestamp
}
```

#### Configuration

```env
JWT_SECRET_KEY=your_secret_key_here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

For detailed JWT documentation, see `backend/JWT_AUTH_README.md`

---

## Database Setup

### Cloud-Native Architecture ☁️

This project uses **100% cloud databases** - no local database files are created:

| Database Type | Service | Purpose | Status |
|---------------|---------|---------|--------|
| **Relational DB** | PostgreSQL on Render | User auth, sessions, documents | ✅ Online |
| **Vector Store** | Pinecone Cloud | Semantic search embeddings | ✅ Online |
| **Document Store** | Qdrant Cloud | Document storage & retrieval | ✅ Online |

**Benefits:**
- ✅ Zero local disk usage for databases
- ✅ Reduced processor load (all DB operations handled by cloud)
- ✅ Better performance (cloud databases are optimized)
- ✅ Automatic backups and scaling

### PostgreSQL (Production)

#### Using Render (Recommended)

1. Go to [render.com](https://render.com)
2. Create new PostgreSQL database
3. Copy connection string
4. Add to `.env`:

```env
DATABASE_URL=postgresql://user:password@host:port/database
```

#### Using Neon (Alternative)

1. Go to [neon.tech](https://neon.tech)
2. Create new project
3. Copy connection string
4. Add to `.env`

### SQLite (Development/Testing Only)

SQLite is used **only** for:
- ✅ Running tests (in-memory: `sqlite:///:memory:`)
- ✅ Local development without internet (fallback)

**Note:** Since `DATABASE_URL` is set in `.env`, SQLite is never used in production. No local database files (`sql_app.db`, `chroma_db/`) are created.

### Database Models

The system uses these core models:

```python
User
├── id (UUID)
├── email (unique)
├── hashed_password
├── role (BA, FBA, QA)
└── created_at

ChatSession
├── id (UUID)
├── title
├── role
├── user_id (FK)
└── created_at

ChatMessage
├── id (UUID)
├── session_id (FK)
├── role (user/assistant)
├── content
└── created_at

Document
├── id (UUID)
├── filename
├── file_path
├── file_size
├── file_type (pdf, docx, csv)
├── status (uploaded, indexed, error)
├── user_id (FK)
└── upload_date

DocumentFeedback
├── id (UUID)
├── document_id (FK)
├── user_id (FK)
├── rating (thumbs_up, thumbs_down)
├── feedback_text
├── ai_improvement_suggestions
└── created_at
```

---

## Configuration

### Environment Variables

Create `backend/.env` with:

```env
# ── Database ──────────────────────────────────────────
DATABASE_URL=postgresql://user:password@host:port/database

# ── LLM: OpenRouter (Gemma 2 27B) ─────────────────────
OPENROUTER_API_KEY=your_openrouter_api_key_here

# ── HuggingFace Hub ───────────────────────────────────
# For downloading embedding models (READ token sufficient)
HF_TOKEN=hf_your_huggingface_token_here

# ── Vector Search: Pinecone ───────────────────────────
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=sdlc-copilot

# ── Document Store: Qdrant Cloud ──────────────────────
QDRANT_URL=https://your-cluster-id.us-east-1-1.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_COLLECTION_NAME=sdlc_documents

# ── JWT Authentication ────────────────────────────────
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# ── App Settings ──────────────────────────────────────
ENVIRONMENT=production
```

### Getting API Keys

#### OpenRouter API Key
1. Visit [openrouter.ai](https://openrouter.ai)
2. Sign up for free account
3. Create API key
4. Copy to `.env`
5. Free tier includes Gemma 2 27B model

#### Pinecone API Key
1. Visit [pinecone.io](https://pinecone.io)
2. Create free account
3. Create serverless index (dimension: 384, metric: cosine)
4. Copy API key and index name

#### HuggingFace Token (Optional but Recommended)
1. Visit [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Create new token with **READ** access
3. Copy token (starts with `hf_`)
4. Add to `.env`

**Why?**
- ✅ Faster model downloads
- ✅ Higher rate limits
- ✅ No warning messages
- ✅ READ token is sufficient (no write access needed)

**Note:** The project works without a token, but you'll see warnings and have slower downloads.
1. Visit [cloud.qdrant.io](https://cloud.qdrant.io)
2. Create free account
3. Create cluster
4. Copy URL and API key

---

## Running the Application

### Development Mode

#### Terminal 1: Backend
```bash
cd backend
source ../.venv/bin/activate
../.venv/bin/python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend: `http://localhost:8000`  
Swagger UI: `http://localhost:8000/docs`

#### Terminal 2: Frontend
```bash
cd frontend
npm run dev
```

Frontend: `http://localhost:3000`

### Production Mode

#### Backend
```bash
cd backend
../.venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Frontend
```bash
cd frontend
npm run build
npm run start
```

### Docker Deployment

```bash
docker-compose up -d
```

---

## Testing

### Test JWT Authentication

```bash
cd backend
python test_jwt_auth.py
```

Tests:
- ✅ Login with valid credentials
- ✅ Get user info with token
- ✅ Verify token validity
- ✅ Reject invalid credentials
- ✅ Reject invalid tokens

### Test Database Connection

```bash
cd backend
python test_db_connection.py
```

Tests:
- ✅ PostgreSQL connection
- ✅ Table creation
- ✅ CRUD operations

### Run Test Suite

```bash
cd backend
pytest tests/
```

---

## Troubleshooting

### Backend Issues

#### "Could not validate credentials"
- Token expired (30 min default)
- Wrong JWT_SECRET_KEY in .env
- Token format incorrect (should be: `Bearer <token>`)

**Solution**: Login again to get new token

#### "Database connection failed"
- Check DATABASE_URL in .env
- Verify PostgreSQL is running
- Run: `python test_db_connection.py`

**Solution**: Update DATABASE_URL or start PostgreSQL

#### "OPENROUTER_API_KEY not found"
- Missing OPENROUTER_API_KEY in .env
- Key is invalid or expired

**Solution**: Get new key from [openrouter.ai](https://openrouter.ai)

### Frontend Issues

#### CORS errors
- Frontend origin not in CORS allowed list
- Backend not running

**Solution**: 
- Check CORS config in `backend/main.py`
- Ensure backend is running on port 8000

#### "Cannot connect to API"
- Backend not running
- Wrong API URL

**Solution**: 
- Start backend: `../.venv/bin/python -m uvicorn main:app --reload`
- Check frontend API URL configuration

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Invalid/expired token | Login again |
| 404 Not Found | Endpoint doesn't exist | Check API documentation |
| 500 Server Error | Backend error | Check server logs |
| CORS Error | Frontend origin blocked | Update CORS config |
| Database Error | Connection failed | Check DATABASE_URL |

---

## Future Enhancements

### Planned Features

- Multi-Model Support: Google Gemini, OpenAI GPT-4o, Anthropic Claude
- Jira Integration: Auto-populate Jira tickets
- Advanced Export: Word, PDF with custom templates
- Collaborative Editing: Real-time multi-user editing
- Version Control: Track document versions
- Custom Prompts: User-defined generation templates
- Analytics Dashboard: Usage metrics and insights
- Refresh Tokens: Extended session management
- User Registration: Self-service signup
- Role Management: Custom roles and permissions
- Document Comparison: Side-by-side version comparison
- Template Library: Pre-built document templates

### Roadmap

**Q2 2026**
- Multi-model LLM support
- Advanced export formats

**Q3 2026**
- Jira integration
- Collaborative editing

**Q4 2026**
- Analytics dashboard
- Custom prompt templates

---

## Support & Documentation

### Additional Resources

- **JWT Authentication**: See `backend/JWT_AUTH_README.md`
- **Frontend Integration**: See `backend/FRONTEND_INTEGRATION.md`
- **Test Cases**: See `testcases/` directory
- **Architecture**: See `SADDOC/SDLC_SADupdated.pdf`

### Getting Help

1. Check troubleshooting section above
2. Review API documentation
3. Check test files for examples
4. Review server logs for errors

### Contact

For support or contributions, contact the development team.

---

## License

This project is developed for internal SDLC automation. All rights reserved.

---

## Project Status

Production Ready

- JWT Authentication: Implemented
- Database: Configured (PostgreSQL on Render)
- Vector Search: Pinecone Serverless
- Document Store: Qdrant Cloud
- LLM: OpenRouter Gemma 2 27B (16K context)
- Session Isolation: Complete data separation
- API: Fully functional
- Frontend: Responsive UI
- Testing: Comprehensive test suite
- Documentation: Complete

**Last Updated**: April 20, 2026  
**Version**: 2.1.0

---

## Recent Updates & Improvements

### April 20, 2026 - v2.1.1 (Maintenance Release)

#### Deprecation Fixes ✅
- **Fixed Python 3.12+ compatibility**: Updated `datetime.utcnow` to `datetime.now(timezone.utc)` in all models
- **Fixed Pydantic v2 compatibility**: Migrated from `class Config` to `model_config = ConfigDict()`
- **Fixed SQLAlchemy 2.0 compatibility**: Migrated from `declarative_base()` to `DeclarativeBase` class
- **Result**: 100% compliant with Python 3.12+, Pydantic 2.x, and SQLAlchemy 2.0

#### HuggingFace Integration ✅
- **Added HF_TOKEN support**: Faster model downloads and higher rate limits
- **Token type**: READ token (sufficient for downloading embedding models)
- **Benefit**: No more "unauthenticated requests" warnings

#### Database Architecture ✅
- **Removed local databases**: Deleted `sql_app.db` (132 KB) and `chroma_db/` (556 KB)
- **100% cloud-native**: All data stored in PostgreSQL (Render), Pinecone, and Qdrant Cloud
- **Benefits**: 
  - Zero local disk usage for databases
  - Reduced processor load (all DB operations handled by cloud)
  - Better performance and automatic backups

#### Documentation ✅
- **New**: `DEPRECATION_AUDIT_REPORT.md` - Complete deprecation audit
- **New**: `DEPRECATION_FIXES_SUMMARY.md` - Quick reference of all fixes
- **New**: `LOCAL_DB_CLEANUP.md` - Database cleanup documentation
- **Updated**: README.md with latest architecture and configuration

### v2.1.0 - MCP Integration

### v2.1.0 - MCP Integration

#### Key Features
#### Key Features
- **MCP Multi-Agent Pipeline**: Integrated 5 specialized AI agents for comprehensive document processing
- **Advanced Document Analysis**: Extract requirements, tables, business logic, and change requests
- **Professional Output**: Generate formatted DOCX documents with proper styling
- **Intermediate Transparency**: Access all 7 intermediate JSON outputs
- **Quality Validation**: Automatic document consistency and completeness checks
- **Multiple Delivery Modes**: Download, API response, webhook, and email options

### v2.0.0 - OpenRouter Migration

- Switched from Groq to OpenRouter for better model selection
- Increased context window from 8K to 16K tokens
- Implemented session-based document filtering
- Enhanced chunk size (3000 chars) for better context
- Increased retrieval documents (30 vs 20) for comprehensive responses
- Fixed embeddings model configuration
- Improved document generation quality
