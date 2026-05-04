# SDLC Automation Copilot

## Overview

The SDLC Automation Copilot is an enterprise-grade AI-powered platform that revolutionizes Software Development Lifecycle (SDLC) documentation creation. Built specifically for Business Analysts (BAs), Functional Business Analysts (FBAs), and Quality Assurance (QA) engineers, this system leverages Retrieval-Augmented Generation (RAG) technology and a sophisticated Multi-Agent Pipeline to generate high-fidelity Business Requirement Documents (BRDs), Functional Requirement Documents (FRDs), and comprehensive Test Packs.

### Version Information
- Current Version: 2.1.0
- Release Date: April 2026
- Status: Production Ready
- Architecture: 100% Cloud-Native

### Key Features
- AI-powered document generation using NVIDIA Nemotron 3 Nano 30B
- MCP (Model Context Protocol) Multi-Agent Pipeline with 5 specialized agents
- JWT-based authentication with role-based access control
- Semantic search using Pinecone vector database
- Cloud-native architecture (PostgreSQL, Pinecone, Qdrant)
- Session-based document isolation
- Real-time streaming responses
- Support for PDF, DOCX, and CSV document uploads
- AI-powered feedback and improvement suggestions

---

##  Quick Start

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
# Email: ba@xyz.com | Password: password123
# Admin: admin1@hsbc.com | Password: admin123
```

**API Docs**: http://localhost:8000/docs  
**Admin Portal**: http://localhost:3000/admin

---

## Table of Contents

1. [What is This Project?](#what-is-this-project)
2. [Why Use This?](#why-use-this)
3. [When to Use This?](#when-to-use-this)
4. [How to Get Started](#how-to-get-started)
5. [MCP Multi-Agent Pipeline](#mcp-multi-agent-pipeline)
6. [System Architecture](#system-architecture)
7. [Technology Stack](#technology-stack)
8. [Project Structure](#project-structure)
9. [Admin Dashboard](#admin-dashboard)
10. [API Documentation](#api-documentation)
11. [Authentication](#authentication)
12. [Database Setup](#database-setup)
13. [Configuration](#configuration)
14. [Running the Application](#running-the-application)
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
| **Document Upload** | Ingest PDF, DOCX, CSV files into knowledge base with automatic chunking and indexing |
| **Semantic Search** | Find relevant content using HuggingFace embeddings and Pinecone vector search |
| **Role-Based Generation** | Generate BRDs (BA), FRDs (FBA), or Test Packs (QA) based on user role |
| **Session Management** | Isolated chat sessions with persistent history and document filtering |
| **Feedback System** | Rate generated content (thumbs up/down) and receive AI improvement suggestions |
| **Real-time Streaming** | Token-by-token response streaming for interactive experience |
| **MCP Multi-Agent Pipeline** | Process documents through 5 specialized AI agents for comprehensive analysis |
| **Priority-Based Retrieval** | Documents tagged with priority levels for weighted search results |

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
- Email: `ba@xyz.com`
- Password: `password123`

**Admin Access:**
- Email: `admin1@hsbc.com`
- Password: `admin123`
- Access: http://localhost:3000/admin

---

## MCP Multi-Agent Pipeline

### What is MCP?

The **Model Context Protocol (MCP) Multi-Agent Pipeline** is an advanced document processing system that uses 6 specialized AI agents working together to comprehensively analyze and structure documents.

```
Input Document → Reader Agent → [5 Specialist Agents] → Master Receiver → Unified Output
```

### The 6 AI Agents

1. **Document Reader Agent** - Parses documents and extracts structured JSON with sections and tables
2. **Requirements Agent (S1)** - Extracts functional, non-functional requirements, and constraints with IDs
3. **Table Analyzer Agent (S2)** - Analyzes table structures, infers schemas, detects anomalies
4. **Business Logic Agent (S3)** - Identifies business rules (IF/THEN), process flows, and decision points
5. **Change Request Agent (S4)** - Tracks version changes, scope deltas, and CR references
6. **Validation Agent (S5)** - Validates document consistency, completeness, and structural integrity
7. **Master Receiver Agent** - Merges all outputs into unified payload with conflict resolution

### Quick Start with MCP

```bash
# Process a document through MCP pipeline
curl -X POST "http://localhost:8000/api/mcp/process" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@requirements.pdf" \
  -F "session_id=test-session"

# Download unified output
curl "http://localhost:8000/api/mcp/download/test-session/unified_payload.json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o unified_payload.json

# Get specific intermediate file
curl "http://localhost:8000/api/mcp/intermediate/test-session/requirements" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### What You Get

The MCP pipeline produces:
- **Unified JSON payload** with all extracted information merged
- **7 intermediate JSON files** for full transparency:
  - `reader_output.json` - Parsed document structure
  - `s1_requirements.json` - All requirements extracted
  - `s2_table_schemas.json` - Table schemas and analysis
  - `s3_business_logic.json` - Business rules and flows
  - `s4_change_requests.json` - Change tracking
  - `s5_validation.json` - Validation report
  - `unified_payload.json` - Final merged output
- **Structured data** ready for downstream processing or document generation
- **Validation report** with errors and warnings
- **Cross-references** between requirements, tables, and change requests

### MCP Agent Details

Each agent uses Google Gemma 2 27B IT model with:
- Temperature: 0.2 (for consistent, deterministic outputs)
- Max tokens: 16,000
- Structured JSON output with strict schema validation
- Error handling with fallback responses

### MCP API Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /api/mcp/process` | Process document through MCP pipeline (multipart/form-data) |
| `GET /api/mcp/download/{session_id}/{filename}` | Download processed JSON outputs |
| `GET /api/mcp/intermediate/{session_id}/{file_type}` | Get specific intermediate JSON file |
| `GET /api/mcp/status/{document_id}` | Check document processing status |

**Note**: The MCP pipeline currently outputs JSON files. DOCX generation can be added using the `mcp_document_generator.py` service.

---

## System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER (Browser)                              │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    Next.js 16 + React 19 Frontend                    │  │
│  │                                                                      │  │
│  │  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────┐   │  │
│  │  │  Chat Interface │  │ Admin Dashboard  │  │ Model Management│   │  │
│  │  │  - Messages     │  │ - User CRUD      │  │ - API Keys      │   │  │
│  │  │  - Streaming    │  │ - Role Assign    │  │ - Model Config  │   │  │
│  │  │  - References   │  │ - Test Login     │  │ - Status        │   │  │
│  │  └─────────────────┘  └──────────────────┘  └─────────────────┘   │  │
│  │                                                                      │  │
│  │  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────┐   │  │
│  │  │ Document Upload │  │ Session Manager  │  │ Reference Panel │   │  │
│  │  │ - PDF/DOCX/CSV  │  │ - Create Session │  │ - Show Context  │   │  │
│  │  │ - Progress      │  │ - List Sessions  │  │ - Display Refs  │   │  │
│  │  │ - Status        │  │ - Delete Session │  │ - Feedback      │   │  │
│  │  └─────────────────┘  └──────────────────┘  └─────────────────┘   │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬─────────────────────────────────────────────┘
                                 │
                    REST API + Server-Sent Events (SSE)
                                 │
┌────────────────────────────────▼─────────────────────────────────────────────┐
│                    API LAYER (FastAPI + Uvicorn)                             │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      Authentication & Authorization                  │  │
│  │  ┌─────────────────────────────────────────────────────────────┐   │  │
│  │  │ /api/auth/login          - User/Admin JWT authentication    │   │  │
│  │  │ /api/auth/me             - Get current user info            │   │  │
│  │  │ /api/admin/login         - Admin authentication             │   │  │
│  │  │ /api/admin/users         - User management (CRUD)           │   │  │
│  │  │ /api/admin/models        - AI model management              │   │  │
│  │  └─────────────────────────────────────────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      Chat & Document Processing                      │  │
│  │  ┌─────────────────────────────────────────────────────────────┐   │  │
│  │  │ /api/chat/sessions       - Session management              │   │  │
│  │  │ /api/chat/query/stream   - Streaming RAG queries           │   │  │
│  │  │ /api/documents/upload    - Document ingestion              │   │  │
│  │  │ /api/documents/list      - List documents by session       │   │  │
│  │  │ /api/documents/feedback  - Submit feedback & suggestions   │   │  │
│  │  │ /api/mcp/process         - MCP pipeline processing         │   │  │
│  │  │ /api/mcp/download        - Download MCP outputs            │   │  │
│  │  └─────────────────────────────────────────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      Service Layer                                   │  │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────┐   │  │
│  │  │ RAG Service      │  │ MCP Pipeline     │  │ Feedback       │   │  │
│  │  │ - Retrieval      │  │ - 6 AI Agents    │  │ Service        │   │  │
│  │  │ - Ranking        │  │ - JSON Output    │  │ - Analysis     │   │  │
│  │  │ - Streaming      │  │ - Validation     │  │ - Suggestions  │   │  │
│  │  └──────────────────┘  └──────────────────┘  └────────────────┘   │  │
│  │                                                                      │  │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────┐   │  │
│  │  │ PDF Service      │  │ Document Gen     │  │ Prompt         │   │  │
│  │  │ - PDF Parsing    │  │ - DOCX Creation  │  │ Templates      │   │  │
│  │  │ - Text Extract   │  │ - Formatting     │  │ - Role-based   │   │  │
│  │  └──────────────────┘  └──────────────────┘  └────────────────┘   │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬─────────────────────────────────────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┬──────────────┐
        │                        │                        │              │
┌───────▼──────────┐  ┌──────────▼──────────┐  ┌─────────▼────────┐  ┌──▼──────────┐
│  PostgreSQL      │  │  Pinecone Cloud    │  │  Qdrant Cloud    │  │ OpenRouter  │
│  (Metadata DB)   │  │  (Vector Search)   │  │  (Doc Storage)   │  │ (LLM API)   │
│                  │  │                    │  │                  │  │             │
│ ┌──────────────┐ │  │ ┌────────────────┐ │  │ ┌──────────────┐ │  │ ┌─────────┐ │
│ │ Users        │ │  │ │ Embeddings     │ │  │ │ Documents    │ │  │ │Nemotron │ │
│ │ Sessions     │ │  │ │ 384-dim        │ │  │ │ Chunks       │ │  │ │3 Nano   │ │
│ │ Messages     │ │  │ │ Cosine Sim     │ │  │ │ Metadata     │ │  │ │30B      │ │
│ │ Documents    │ │  │ │ Auto-index     │ │  │ │ Auto-collect │ │  │ │         │ │
│ │ Feedback     │ │  │ │ Serverless     │ │  │ │ Serverless   │ │  │ │Gemma 2  │ │
│ │ AI Models    │ │  │ │                │ │  │ │              │ │  │ │27B IT   │ │
│ └──────────────┘ │  │ └────────────────┘ │  │ └──────────────┘ │  │ └─────────┘ │
└──────────────────┘  └────────────────────┘  └──────────────────┘  └─────────────┘
```

### Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DOCUMENT UPLOAD FLOW                                │
└─────────────────────────────────────────────────────────────────────────────┘

User Upload (PDF/DOCX/CSV)
        │
        ▼
┌──────────────────────┐
│ PDF/DOCX Parser      │  Extract text, tables, metadata
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Text Chunker         │  Split into 3000-char chunks
│ (400 char overlap)   │  with metadata preservation
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Embedding Generator  │  Convert chunks to 384-dim vectors
│ (HuggingFace)        │  using sentence-transformers
└──────────┬───────────┘
           │
        ┌──┴──┐
        │     │
        ▼     ▼
    Pinecone  Qdrant
    (Vector)  (Storage)
    Index     Collection
        │     │
        └──┬──┘
           │
           ▼
    ✓ Document Indexed
      Ready for Search


┌─────────────────────────────────────────────────────────────────────────────┐
│                         USER QUERY FLOW (RAG)                               │
└─────────────────────────────────────────────────────────────────────────────┘

User Query
    │
    ▼
┌──────────────────────┐
│ Session Filter       │  Filter documents by session_id
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Query Embedding      │  Convert query to 384-dim vector
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Semantic Search      │  Retrieve top 30 similar chunks
│ (Pinecone)           │  using cosine similarity
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Priority Weighting   │  Rank by: relevance + priority
│ & Ranking            │  (High > Medium > Low)
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Context Assembly     │  Build prompt with:
│                      │  - Query
│                      │  - Top 30 contexts
│                      │  - Role-based template
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ LLM Inference        │  Send to OpenRouter
│ (Nemotron 3 30B)     │  - Timeout: 30 seconds
│                      │  - Context: 16K tokens
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Token Streaming      │  Stream response to client
│ (Server-Sent Events) │  token-by-token in real-time
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Store Message        │  Save to PostgreSQL:
│                      │  - session_id
│                      │  - user_query
│                      │  - ai_response
│                      │  - timestamp
└──────────┬───────────┘
           │
           ▼
    ✓ Response Complete
      Ready for Feedback


┌─────────────────────────────────────────────────────────────────────────────┐
│                    MCP MULTI-AGENT PIPELINE FLOW                            │
└─────────────────────────────────────────────────────────────────────────────┘

Input Document (PDF/DOCX)
        │
        ▼
┌──────────────────────────────────────────┐
│ Document Reader Agent                    │
│ - Parse document structure               │
│ - Extract sections, tables, metadata     │
│ - Output: reader_output.json             │
└──────────┬───────────────────────────────┘
           │
        ┌──┴──────────────────────────────────────────┐
        │                                             │
        ▼                                             ▼
┌──────────────────────────┐          ┌──────────────────────────┐
│ S1: Requirements Agent   │          │ S2: Table Analyzer Agent │
│ - Extract requirements   │          │ - Analyze table schemas  │
│ - Identify constraints   │          │ - Detect anomalies       │
│ - Assign IDs             │          │ - Infer relationships    │
│ Output: s1_requirements  │          │ Output: s2_table_schemas │
└──────────┬───────────────┘          └──────────┬───────────────┘
           │                                     │
        ┌──┴──────────────────────────────────────┴──┐
        │                                            │
        ▼                                            ▼
┌──────────────────────────┐          ┌──────────────────────────┐
│ S3: Business Logic Agent │          │ S4: Change Request Agent │
│ - Identify business rules│          │ - Track version changes  │
│ - Extract IF/THEN logic  │          │ - Identify scope deltas  │
│ - Map process flows      │          │ - Reference CRs          │
│ Output: s3_business_logic│          │ Output: s4_change_requests
└──────────┬───────────────┘          └──────────┬───────────────┘
           │                                     │
        ┌──┴──────────────────────────────────────┴──┐
        │                                            │
        ▼                                            ▼
┌──────────────────────────┐          ┌──────────────────────────┐
│ S5: Validation Agent     │          │ Master Receiver Agent    │
│ - Validate consistency   │          │ - Merge all outputs      │
│ - Check completeness     │          │ - Resolve conflicts      │
│ - Verify structure       │          │ - Create unified payload │
│ Output: s5_validation    │          │ Output: unified_payload  │
└──────────┬───────────────┘          └──────────┬───────────────┘
           │                                     │
           └──────────────────┬──────────────────┘
                              │
                              ▼
                    ┌──────────────────────┐
                    │ 7 JSON Output Files  │
                    │ - reader_output      │
                    │ - s1_requirements    │
                    │ - s2_table_schemas   │
                    │ - s3_business_logic  │
                    │ - s4_change_requests │
                    │ - s5_validation      │
                    │ - unified_payload    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ✓ MCP Processing Complete
                      Ready for Download/Generation


┌─────────────────────────────────────────────────────────────────────────────┐
│                      FEEDBACK & IMPROVEMENT FLOW                            │
└─────────────────────────────────────────────────────────────────────────────┘

User Feedback (Thumbs Up/Down)
        │
        ▼
┌──────────────────────┐
│ Store Feedback       │  Save to PostgreSQL:
│                      │  - document_id
│                      │  - rating (up/down)
│                      │  - feedback_text
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ AI Analysis          │  Send to LLM:
│ (Feedback Service)   │  - Analyze feedback
│                      │  - Generate suggestions
│                      │  - Identify improvements
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Store Suggestions    │  Save to PostgreSQL:
│                      │  - ai_improvement_suggestions
│                      │  - timestamp
└──────────┬───────────┘
           │
           ▼
    ✓ Feedback Processed
      Suggestions Available


┌─────────────────────────────────────────────────────────────────────────────┐
│                    ADMIN OPERATIONS FLOW                                    │
└─────────────────────────────────────────────────────────────────────────────┘

Admin Login
    │
    ▼
┌──────────────────────┐
│ Verify Credentials   │  Check email & password
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Generate JWT Token   │  Create admin token
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Admin Dashboard      │  Access admin features:
│                      │  - User Management
│                      │  - Model Management
└──────────┬───────────┘
           │
        ┌──┴──────────────────────────────┐
        │                                 │
        ▼                                 ▼
┌──────────────────────┐      ┌──────────────────────┐
│ User Management      │      │ Model Management     │
│ - Create user        │      │ - View models        │
│ - Edit user          │      │ - Update API keys    │
│ - Delete user        │      │ - Set default model  │
│ - Test login         │      │ - Activate/Deactivate
│ - Assign roles       │      │ - Delete model       │
└──────────┬───────────┘      └──────────┬───────────┘
           │                             │
           ▼                             ▼
    PostgreSQL Update          PostgreSQL Update
           │                             │
           └──────────────┬──────────────┘
                          │
                          ▼
                    ✓ Admin Operation Complete
```

### Data Flow

1. **Document Upload** → Parser (PDF/DOCX/CSV) → Chunker (3000 chars) → Embeddings (384-dim) → Pinecone + Qdrant
2. **User Query** → Session Filter → Retrieve Context (Top 30) → Priority Weighting → LLM Prompt → OpenRouter API → Stream Response
3. **Session Management** → Create Session → Store Messages → Filter Documents by Session ID
4. **MCP Pipeline** → Document Reader → 5 Specialist Agents → Master Receiver → Unified JSON Output
5. **Feedback Loop** → User Rating → AI Analysis → Improvement Suggestions → Store in PostgreSQL

### Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FRONTEND COMPONENT INTERACTIONS                          │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌──────────────────┐
                              │   App Layout     │
                              │  (Root Layout)   │
                              └────────┬─────────┘
                                       │
                ┌──────────────────────┼──────────────────────┐
                │                      │                      │
                ▼                      ▼                      ▼
        ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
        │ Chat Page    │      │ Admin Page   │      │ Landing Page │
        └──────┬───────┘      └──────┬───────┘      └──────────────┘
               │                     │
        ┌──────┴──────┐       ┌──────┴──────┐
        │             │       │             │
        ▼             ▼       ▼             ▼
    ┌────────┐  ┌──────────┐ ┌────────┐ ┌──────────┐
    │ChatWin │  │Reference │ │User    │ │AI Model  │
    │dow     │  │Panel     │ │Mgmt    │ │Mgmt      │
    └────────┘  └──────────┘ └────────┘ └──────────┘
        │             │          │          │
        ▼             ▼          ▼          ▼
    ┌────────────────────────────────────────────┐
    │         Zustand Store (useAppStore)        │
    │  - Current session                         │
    │  - Messages                                │
    │  - Documents                               │
    │  - User info                               │
    │  - Admin state                             │
    └────────────────────────────────────────────┘
        │
        ▼
    ┌────────────────────────────────────────────┐
    │      Axios HTTP Client                     │
    │  - Interceptors for auth                   │
    │  - Error handling                          │
    │  - Request/response transformation         │
    └────────────────────────────────────────────┘
        │
        ▼
    Backend API


┌─────────────────────────────────────────────────────────────────────────────┐
│                    BACKEND SERVICE INTERACTIONS                             │
└─────────────────────────────────────────────────────────────────────────────┘

                    ┌──────────────────────────┐
                    │   FastAPI Application    │
                    │   (main.py)              │
                    └────────────┬─────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
        ▼                        ▼                        ▼
    ┌─────────┐            ┌──────────┐            ┌──────────┐
    │Auth API │            │Chat API  │            │Admin API │
    └────┬────┘            └────┬─────┘            └────┬─────┘
         │                      │                      │
         ▼                      ▼                      ▼
    ┌─────────────────────────────────────────────────────────┐
    │              Service Layer                             │
    │                                                         │
    │  ┌──────────────┐  ┌──────────────┐  ┌────────────┐   │
    │  │ RAG Service  │  │ MCP Pipeline │  │ Feedback   │   │
    │  │              │  │              │  │ Service    │   │
    │  │ - Retrieve   │  │ - 6 Agents   │  │            │   │
    │  │ - Rank       │  │ - Process    │  │ - Analyze  │   │
    │  │ - Stream     │  │ - Validate   │  │ - Suggest  │   │
    │  └──────┬───────┘  └──────┬───────┘  └────┬───────┘   │
    │         │                 │               │            │
    │  ┌──────┴─────────────────┴───────────────┴──────┐    │
    │  │                                               │    │
    │  │  ┌──────────────┐  ┌──────────────────────┐  │    │
    │  │  │ PDF Service  │  │ Prompt Templates     │  │    │
    │  │  │              │  │                      │  │    │
    │  │  │ - Parse      │  │ - BA templates       │  │    │
    │  │  │ - Extract    │  │ - FBA templates      │  │    │
    │  │  │ - Chunk      │  │ - QA templates       │  │    │
    │  │  └──────────────┘  └──────────────────────┘  │    │
    │  └──────────────────────────────────────────────┘    │
    └─────────────────────────────────────────────────────────┘
        │
        ▼
    ┌─────────────────────────────────────────────────────────┐
    │              Data Access Layer (SQLAlchemy)            │
    │                                                         │
    │  ┌──────────────┐  ┌──────────────┐  ┌────────────┐   │
    │  │ User Model   │  │ Session Model│  │ Document   │   │
    │  │              │  │              │  │ Model      │   │
    │  │ - id         │  │ - id         │  │            │   │
    │  │ - email      │  │ - user_id    │  │ - id       │   │
    │  │ - password   │  │ - title      │  │ - filename │   │
    │  │ - role       │  │ - role       │  │ - path     │   │
    │  │ - is_admin   │  │ - created_at │  │ - status   │   │
    │  └──────────────┘  └──────────────┘  └────────────┘   │
    │                                                         │
    │  ┌──────────────┐  ┌──────────────┐  ┌────────────┐   │
    │  │ Message Model│  │ Feedback     │  │ AI Model   │   │
    │  │              │  │ Model        │  │ Model      │   │
    │  │ - id         │  │              │  │            │   │
    │  │ - session_id │  │ - id         │  │ - id       │   │
    │  │ - role       │  │ - rating     │  │ - name     │   │
    │  │ - content    │  │ - feedback   │  │ - provider │   │
    │  │ - created_at │  │ - suggestions│  │ - api_key  │   │
    │  └──────────────┘  └──────────────┘  └────────────┘   │
    └─────────────────────────────────────────────────────────┘
        │
        ▼
    ┌─────────────────────────────────────────────────────────┐
    │              External Services                          │
    │                                                         │
    │  ┌──────────────┐  ┌──────────────┐  ┌────────────┐   │
    │  │ PostgreSQL   │  │ Pinecone     │  │ Qdrant     │   │
    │  │              │  │              │  │            │   │
    │  │ - Metadata   │  │ - Vectors    │  │ - Documents│   │
    │  │ - Sessions   │  │ - Search     │  │ - Storage  │   │
    │  │ - Messages   │  │ - Index      │  │ - Retrieve │   │
    │  └──────────────┘  └──────────────┘  └────────────┘   │
    │                                                         │
    │  ┌──────────────────────────────────────────────────┐  │
    │  │ OpenRouter API                                   │  │
    │  │ - NVIDIA Nemotron 3 Nano 30B (RAG)              │  │
    │  │ - Google Gemma 2 27B IT (MCP)                   │  │
    │  │ - Token streaming                               │  │
    │  │ - 30-second timeout protection                  │  │
    │  └──────────────────────────────────────────────────┘  │
    └─────────────────────────────────────────────────────────┘
```

### Request/Response Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TYPICAL USER QUERY FLOW                                  │
└─────────────────────────────────────────────────────────────────────────────┘

User Types Query in Chat
        │
        ▼
Frontend: ChatWindow Component
        │
        ├─ Validate input
        ├─ Add to local state
        ├─ Display in UI
        │
        ▼
Frontend: Axios HTTP Client
        │
        ├─ Add Authorization header (JWT token)
        ├─ POST /api/chat/query/stream
        ├─ Include: session_id, query, role, task_type
        │
        ▼
Backend: Chat API Router
        │
        ├─ Verify JWT token
        ├─ Check user permissions
        ├─ Validate session ownership
        │
        ▼
Backend: RAG Service
        │
        ├─ Filter documents by session_id
        ├─ Convert query to embedding (384-dim)
        ├─ Search Pinecone (top 30 results)
        ├─ Rank by relevance + priority
        ├─ Assemble context window
        │
        ▼
Backend: Prompt Templates
        │
        ├─ Select template by role (BA/FBA/QA)
        ├─ Format prompt with context
        ├─ Include task-specific instructions
        │
        ▼
Backend: OpenRouter API Call
        │
        ├─ Model: NVIDIA Nemotron 3 Nano 30B
        ├─ Context: 16K tokens
        ├─ Temperature: 0.7
        ├─ Max tokens: 2000
        ├─ Timeout: 30 seconds
        │
        ▼
Backend: Token Streaming
        │
        ├─ Receive tokens from LLM
        ├─ Stream via Server-Sent Events (SSE)
        ├─ Each token sent immediately
        │
        ▼
Frontend: SSE Listener
        │
        ├─ Receive token stream
        ├─ Append to response in real-time
        ├─ Update UI incrementally
        │
        ▼
Backend: Message Storage
        │
        ├─ After streaming complete
        ├─ Save to PostgreSQL:
        │  - session_id
        │  - user_query
        │  - ai_response
        │  - timestamp
        │
        ▼
Frontend: Display Complete
        │
        ├─ Show full response
        ├─ Enable feedback buttons
        ├─ Ready for next query


┌─────────────────────────────────────────────────────────────────────────────┐
│                    DOCUMENT UPLOAD FLOW                                     │
└─────────────────────────────────────────────────────────────────────────────┘

User Selects File (PDF/DOCX/CSV)
        │
        ▼
Frontend: Document Upload Component
        │
        ├─ Validate file type
        ├─ Check file size
        ├─ Show progress indicator
        │
        ▼
Frontend: FormData Preparation
        │
        ├─ Create FormData object
        ├─ Append file
        ├─ Append session_id
        ├─ POST /api/documents/upload
        │
        ▼
Backend: Document API Router
        │
        ├─ Verify JWT token
        ├─ Validate session ownership
        ├─ Check file type
        │
        ▼
Backend: PDF Service
        │
        ├─ Parse file (PDF/DOCX/CSV)
        ├─ Extract text and metadata
        ├─ Save to uploaded_docs/
        │
        ▼
Backend: Text Chunker
        │
        ├─ Split into 3000-char chunks
        ├─ Add 400-char overlap
        ├─ Preserve metadata
        │
        ▼
Backend: Embedding Generator
        │
        ├─ Load HuggingFace model
        ├─ Convert chunks to 384-dim vectors
        ├─ Batch process for efficiency
        │
        ▼
Backend: Vector Store Upload
        │
        ├─ Upload to Pinecone:
        │  - Vector embeddings
        │  - Chunk text
        │  - Metadata (session_id, priority)
        │
        ├─ Upload to Qdrant:
        │  - Document chunks
        │  - Full metadata
        │  - Searchable fields
        │
        ▼
Backend: Database Update
        │
        ├─ Save to PostgreSQL:
        │  - Document record
        │  - Status: "indexed"
        │  - Upload timestamp
        │
        ▼
Frontend: Upload Complete
        │
        ├─ Show success message
        ├─ Add to documents list
        ├─ Ready for queries


┌─────────────────────────────────────────────────────────────────────────────┐
│                    ADMIN USER CREATION FLOW                                 │
└─────────────────────────────────────────────────────────────────────────────┘

Admin Fills Create User Form
        │
        ▼
Frontend: Admin Page Component
        │
        ├─ Validate email format
        ├─ Validate password strength
        ├─ Verify role selection
        │
        ▼
Frontend: Axios HTTP Client
        │
        ├─ Add Authorization header (admin token)
        ├─ POST /api/admin/users
        ├─ Include: email, username, password, roles
        │
        ▼
Backend: Admin API Router
        │
        ├─ Verify admin JWT token
        ├─ Check admin permissions
        ├─ Validate input data
        │
        ▼
Backend: User Service
        │
        ├─ Check email uniqueness
        ├─ Hash password (bcrypt)
        ├─ Validate roles
        │
        ▼
Backend: Database Insert
        │
        ├─ Create User record:
        │  - id (UUID)
        │  - email
        │  - hashed_password
        │  - roles (array)
        │  - is_admin (false)
        │  - created_at
        │
        ▼
Backend: Response
        │
        ├─ Return success message
        ├─ Include user_id
        ├─ Include created_at
        │
        ▼
Frontend: Update UI
        │
        ├─ Show success notification
        ├─ Refresh users list
        ├─ Clear form
        ├─ Ready for next user creation
```

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
- **Primary LLM**: NVIDIA Nemotron 3 Nano 30B (via OpenRouter)
- **MCP LLM**: Google Gemma 2 27B IT (via OpenRouter)
- **Context Window**: 16,000 tokens
- **Embeddings**: HuggingFace sentence-transformers/all-MiniLM-L6-v2 (384 dimensions)
- **Vector DB**: Pinecone (Serverless, cosine similarity)
- **Document Store**: Qdrant Cloud
- **Orchestration**: LangChain
- **Chunk Size**: 3000 characters with 400 character overlap
- **Retrieval**: Top 30 documents with priority weighting

### Infrastructure
- **Database**: PostgreSQL (Render/Neon) - Cloud-hosted, no local SQLite
- **Vector Search**: Pinecone (Serverless) - Cloud-hosted with auto-index creation
- **Document Store**: Qdrant Cloud - Cloud-hosted with auto-collection creation
- **Embeddings**: HuggingFace sentence-transformers (with optional HF_TOKEN for faster downloads)
- **File Storage**: Local filesystem with configurable upload directory
- **Deployment**: Docker-ready, ASGI server (Uvicorn)
- **Version Control**: Git
- **Architecture**: 100% cloud-native, zero local database overhead
- **Timeout Protection**: 30-second inference timeout with graceful error handling

### Database Schema Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    POSTGRESQL DATABASE SCHEMA                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│      users           │
├──────────────────────┤
│ id (UUID) PK         │
│ email (VARCHAR)      │◄─────────────────────────────────┐
│ username (VARCHAR)   │                                  │
│ hashed_password      │                                  │
│ roles (ARRAY)        │                                  │
│ is_admin (BOOLEAN)   │                                  │
│ created_at (TIMESTAMP)                                  │
│ updated_at (TIMESTAMP)                                  │
└──────────────────────┘                                  │
         │                                                │
         │ 1:N                                            │
         │                                                │
         ▼                                                │
┌──────────────────────┐                                  │
│   chat_sessions      │                                  │
├──────────────────────┤                                  │
│ id (UUID) PK         │                                  │
│ user_id (UUID) FK ───┼──────────────────────────────────┘
│ title (VARCHAR)      │
│ role (VARCHAR)       │
│ created_at (TIMESTAMP)
│ updated_at (TIMESTAMP)
└──────────────────────┘
         │
         │ 1:N
         │
         ▼
┌──────────────────────┐
│   chat_messages      │
├──────────────────────┤
│ id (UUID) PK         │
│ session_id (UUID) FK │
│ role (VARCHAR)       │
│ content (TEXT)       │
│ created_at (TIMESTAMP)
└──────────────────────┘


┌──────────────────────┐
│    documents         │
├──────────────────────┤
│ id (UUID) PK         │
│ session_id (UUID) FK ├──────────────────┐
│ user_id (UUID) FK    │                  │
│ filename (VARCHAR)   │                  │
│ file_path (VARCHAR)  │                  │
│ file_size (INTEGER)  │                  │
│ file_type (VARCHAR)  │                  │
│ status (VARCHAR)     │                  │
│ upload_date (TIMESTAMP)                 │
└──────────────────────┘                  │
         │                                │
         │ 1:N                            │
         │                                │
         ▼                                │
┌──────────────────────┐                  │
│ document_feedback    │                  │
├──────────────────────┤                  │
│ id (UUID) PK         │                  │
│ document_id (UUID) FK├──────────────────┘
│ user_id (UUID) FK    │
│ rating (VARCHAR)     │
│ feedback_text (TEXT) │
│ ai_suggestions (TEXT)│
│ created_at (TIMESTAMP)
└──────────────────────┘


┌──────────────────────┐
│    ai_models         │
├──────────────────────┤
│ id (UUID) PK         │
│ name (VARCHAR)       │
│ provider (VARCHAR)   │
│ model_id (VARCHAR)   │
│ api_key (VARCHAR)    │
│ is_default (BOOLEAN) │
│ is_active (BOOLEAN)  │
│ description (TEXT)   │
│ created_at (TIMESTAMP)
│ updated_at (TIMESTAMP)
└──────────────────────┘


RELATIONSHIPS:
- users (1) ──────────────────────────── (N) chat_sessions
- users (1) ──────────────────────────── (N) documents
- users (1) ──────────────────────────── (N) document_feedback
- chat_sessions (1) ──────────────────── (N) chat_messages
- chat_sessions (1) ──────────────────── (N) documents
- documents (1) ──────────────────────── (N) document_feedback

INDEXES:
- users.email (UNIQUE)
- chat_sessions.user_id
- chat_messages.session_id
- documents.session_id
- documents.user_id
- document_feedback.document_id
- document_feedback.user_id
- ai_models.is_default
- ai_models.is_active
```

### Vector Store Schema (Pinecone)

```
Index: sdlc-copilot
Dimension: 384 (all-MiniLM-L6-v2)
Metric: cosine
Spec: Serverless (AWS us-east-1)

Vector Record Structure:
{
  "id": "chunk-uuid",
  "values": [0.123, 0.456, ...],  // 384-dimensional embedding
  "metadata": {
    "session_id": "session-uuid",
    "document_id": "doc-uuid",
    "chunk_index": 0,
    "text": "chunk content...",
    "priority": "high|medium|low",
    "file_type": "pdf|docx|csv",
    "created_at": "2026-04-15T10:30:00"
  }
}
```

### Document Store Schema (Qdrant)

```
Collection: sdlc_documents
Vector Size: 384
Distance: Cosine

Point Structure:
{
  "id": "chunk-uuid",
  "vector": [0.123, 0.456, ...],  // 384-dimensional embedding
  "payload": {
    "session_id": "session-uuid",
    "document_id": "doc-uuid",
    "filename": "requirements.pdf",
    "chunk_index": 0,
    "text": "chunk content...",
    "priority": "high|medium|low",
    "file_type": "pdf|docx|csv",
    "upload_date": "2026-04-15T10:30:00",
    "user_id": "user-uuid"
  }
}
```

---

## Project Structure

```
project/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py              # JWT authentication (login, user info)
│   │   │   ├── admin.py             # Admin operations (user & model management)
│   │   │   ├── chat.py              # Chat sessions, messages, streaming
│   │   │   ├── documents.py         # Upload, list, delete, feedback
│   │   │   └── mcp.py               # MCP pipeline processing
│   │   ├── services/
│   │   │   ├── rag_service.py       # RAG pipeline with timeout protection
│   │   │   ├── mcp_pipeline.py      # 6 AI agents for document processing
│   │   │   ├── mcp_document_generator.py # DOCX generation from JSON
│   │   │   ├── pdf_service.py       # PDF generation utilities
│   │   │   ├── feedback_service.py  # AI-powered feedback analysis
│   │   │   └── prompt_templates.py  # Role-based prompt templates
│   │   ├── utils/
│   │   │   ├── auth_utils.py        # JWT token creation/validation
│   │   │   ├── rbac_utils.py        # Role-based access control
│   │   │   └── security_utils.py    # Password hashing, security
│   │   ├── models.py                # SQLAlchemy models (User, Document, etc.)
│   │   └── database.py              # Database connection and session
│   ├── uploaded_docs/               # Document storage directory
│   ├── main.py                      # FastAPI application entry point
│   ├── requirements.txt             # Python dependencies
│   ├── .env.example                 # Environment template
│   ├── .env                         # Environment variables (not in git)
│   ├── seed_users.py                # Create test users
│   └── reset_database.py            # Database reset utility
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx             # Landing page
│   │   │   ├── layout.tsx           # Root layout with metadata
│   │   │   ├── globals.css          # Global styles
│   │   │   ├── chat/
│   │   │   │   └── page.tsx         # Main chat interface
│   │   │   └── admin/
│   │   │       ├── page.tsx         # Admin dashboard (user management)
│   │   │       └── models/
│   │   │           └── page.tsx     # AI model management
│   │   ├── components/
│   │   │   ├── ChatWindow.tsx       # Chat UI with streaming
│   │   │   ├── Sidebar.tsx          # Session management sidebar
│   │   │   └── ReferencePanel.tsx   # Document reference display
│   │   ├── lib/
│   │   │   └── axios.ts             # Axios configuration
│   │   └── store/
│   │       └── useAppStore.ts       # Zustand state management
│   ├── public/                      # Static assets (SVG icons)
│   ├── package.json                 # Node dependencies
│   ├── next.config.ts               # Next.js configuration
│   └── tsconfig.json                # TypeScript configuration
│
├── SADDOC/                          # Architecture documentation
│   └── SDLC_SADupdated.pdf
├── README.md                        # This file
└── .gitignore                       # Git ignore rules
```

---

## Admin Dashboard

### Overview

The Admin Dashboard provides comprehensive system management capabilities for administrators. Access it at `http://localhost:3000/admin`.

### Admin Features

#### 1. User Management
- **Create Users**: Add new users with custom roles and credentials
- **Edit Users**: Update user information, passwords, and role assignments
- **Delete Users**: Remove users from the system (cannot delete admin users)
- **Test Login**: Verify user credentials directly from the admin panel
- **Role Assignment**: Assign multiple roles to users (BA, FBA, QA)

#### 2. AI Model Management
- **View Models**: See all configured AI models and their status
- **Update API Keys**: Securely update API keys for each model
- **Set Default Model**: Configure which model is used for system operations
- **Activate/Deactivate**: Enable or disable models without deletion
- **Model Details**: View provider, model ID, and API key preview

### Admin Credentials

| Email | Password | Role |
|-------|----------|------|
| admin1@hsbc.com | admin123 | System Administrator |

### Admin Workflows

#### Creating a New User

1. Navigate to `/admin`
2. Login with admin credentials
3. Click "Create New User"
4. Fill in email, username, and password
5. Select one or more roles (BA, FBA, QA)
6. Click "Create User"

#### Managing AI Models

1. From Admin Dashboard, click "AI Model Management"
2. View all configured models
3. To update an API key:
   - Click "Edit API Key" on the model
   - Enter the new API key
   - Click "Save"
4. To delete a model:
   - Click "Delete" (cannot delete default model)
   - Confirm deletion

#### Testing User Login

1. In the Users table, click "Test Login" on any user
2. Enter the user's password when prompted
3. System will verify credentials and show success/failure

### Admin API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/admin/login` | POST | Admin authentication |
| `/api/admin/users` | GET | List all users |
| `/api/admin/users` | POST | Create new user |
| `/api/admin/users/{user_id}` | PUT | Update user |
| `/api/admin/users/{user_id}` | DELETE | Delete user |
| `/api/admin/models/` | GET | List AI models |
| `/api/admin/models/{model_id}` | PUT | Update model API key |
| `/api/admin/models/{model_id}` | DELETE | Delete model |

### Security Notes

- Admin credentials should be changed immediately after first login
- API keys are encrypted and only the last 4 characters are displayed
- Admin operations are logged for audit purposes
- Only admin users can access the admin dashboard
- Default models cannot be deleted for system stability

---

## API Documentation

### Authentication Endpoints

#### Admin Login
```http
POST /api/admin/login
Content-Type: application/json

{
  "email": "admin1@hsbc.com",
  "password": "admin123"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "email": "admin1@hsbc.com",
  "expires_in": 30
}
```

#### User Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "ba@xyz.com",
  "password": "password123"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "role": "Business Analyst (BA)",
  "user_id": "u1",
  "email": "ba@xyz.com",
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
  "email": "ba@xyz.com",
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
| ba@xyz.com | password123 | Business Analyst (BA) |
| fba@xyz.com | password123 | Functional BA (FBA) |
| qa@xyz.com | password123 | QA / Tester |
| admin1@hsbc.com | admin123 | System Administrator |

#### Token Structure

```json
{
  "sub": "u1",                          // User ID
  "email": "ba@xyz.com",               // User email
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

### Cloud-Native Architecture

This project uses **100% cloud databases** - no local database files are created:

| Database Type | Service | Purpose | Status |
|---------------|---------|---------|--------|
| **Relational DB** | PostgreSQL on Render | User auth, sessions, documents | Online |
| **Vector Store** | Pinecone Cloud | Semantic search embeddings | Online |
| **Document Store** | Qdrant Cloud | Document storage & retrieval | Online |

**Benefits:**
- Zero local disk usage for databases
- Reduced processor load (all DB operations handled by cloud)
- Better performance (cloud databases are optimized)
- Automatic backups and scaling

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
- Running tests (in-memory: `sqlite:///:memory:`)
- Local development without internet (fallback)

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

# ── LLM: OpenRouter ───────────────────────────────────
# Primary: NVIDIA Nemotron 3 Nano 30B (RAG queries)
# MCP: Google Gemma 2 27B IT (document processing)
OPENROUTER_API_KEY=your_openrouter_api_key_here

# ── HuggingFace Hub ───────────────────────────────────
# Optional: For faster embedding model downloads (READ token sufficient)
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
INFERENCE_TIMEOUT_SECONDS=30
```

### Getting API Keys

#### OpenRouter API Key
1. Visit [openrouter.ai](https://openrouter.ai)
2. Sign up for free account
3. Create API key
4. Copy to `.env`
5. Free tier includes:
   - NVIDIA Nemotron 3 Nano 30B (primary RAG model)
   - Google Gemma 2 27B IT (MCP pipeline model)

#### Pinecone API Key
1. Visit [pinecone.io](https://pinecone.io)
2. Create free account
3. Copy API key
4. Add to `.env` (index auto-created on first run)
   - Dimension: 384 (all-MiniLM-L6-v2)
   - Metric: cosine
   - Spec: Serverless (AWS us-east-1)

#### HuggingFace Token (Optional but Recommended)
1. Visit [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Create new token with **READ** access
3. Copy token (starts with `hf_`)
4. Add to `.env`

**Why?**
- Faster model downloads
- Higher rate limits
- No warning messages
- READ token is sufficient (no write access needed)

**Note:** The project works without a token, but you'll see warnings and have slower downloads.

#### Qdrant Cloud API Key
1. Visit [cloud.qdrant.io](https://cloud.qdrant.io)
2. Create free account
3. Create cluster
4. Copy URL and API key
5. Add to `.env` (collection auto-created on first run)
   - Dimension: 384
   - Distance: cosine

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

**Solution**: Update DATABASE_URL or start PostgreSQL

#### "OPENROUTER_API_KEY not found"
- Missing OPENROUTER_API_KEY in .env
- Key is invalid or expired

**Solution**: Get new key from [openrouter.ai](https://openrouter.ai)

#### "AI model is currently unavailable"
- Inference timeout (30 seconds exceeded)
- OpenRouter API rate limit or downtime
- Network connectivity issues

**Solution**: 
- Wait and retry
- Check OpenRouter status
- Verify API key has credits

#### "No vector store available"
- Pinecone or Qdrant connection failed
- Missing API keys in .env

**Solution**: 
- Check PINECONE_API_KEY and QDRANT_API_KEY
- Verify cloud services are accessible
- Check index/collection names match

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
| 401 Unauthorized | Invalid/expired token | Login again to get new token |
| 404 Not Found | Endpoint doesn't exist | Check API documentation at /docs |
| 500 Server Error | Backend error | Check server logs for details |
| CORS Error | Frontend origin blocked | Update CORS config in main.py |
| Database Error | Connection failed | Check DATABASE_URL in .env |
| Timeout Error | Inference > 30s | Retry or check OpenRouter status |
| Vector Store Error | Pinecone/Qdrant down | Verify cloud service status |

---

## Future Enhancements

### Planned Features

- **Multi-Model Support**: Add support for GPT-4, Claude, and other LLMs
- **Advanced MCP Output**: Generate formatted DOCX/PDF from MCP pipeline
- **Jira Integration**: Auto-populate Jira tickets from requirements
- **Collaborative Editing**: Real-time multi-user document editing
- **Version Control**: Track document versions with diff view
- **Custom Prompts**: User-defined generation templates
- **Analytics Dashboard**: Usage metrics, token consumption, and insights
- **Refresh Tokens**: Extended session management beyond 30 minutes
- **User Registration**: Self-service signup with email verification
- **Role Management**: Custom roles and granular permissions
- **Document Comparison**: Side-by-side version comparison
- **Template Library**: Pre-built document templates for common use cases
- **Export Formats**: Word, PDF, Markdown with custom styling
- **Batch Processing**: Process multiple documents simultaneously
- **API Rate Limiting**: Protect against abuse with rate limits

### Roadmap

**Q2 2026**
- MCP Multi-Agent Pipeline (Completed)
- NVIDIA Nemotron 3 Nano 30B integration (Completed)
- Timeout protection for inference (Completed)
- DOCX generation from MCP output (In Progress)
- Enhanced error handling and logging

**Q3 2026**
- Multi-model LLM support (GPT-4, Claude)
- Jira integration
- Advanced export formats

**Q4 2026**
- Collaborative editing
- Analytics dashboard
- Custom prompt templates

---

## Support & Documentation

### Additional Resources

- **API Documentation**: Visit `http://localhost:8000/docs` for interactive Swagger UI
- **Architecture**: See `SADDOC/SDLC_SADupdated.pdf` for system architecture
- **Sample Documents**: Check `backend/uploaded_docs/` for example CSV files

### Key Files

- `backend/app/services/rag_service.py` - RAG pipeline implementation
- `backend/app/services/mcp_pipeline.py` - MCP agent implementation
- `backend/app/services/prompt_templates.py` - Role-based prompts
- `backend/app/models.py` - Database schema
- `frontend/src/components/ChatWindow.tsx` - Chat UI with streaming

### Getting Help

1. Check troubleshooting section above
2. Review API documentation at `/docs`
3. Review server logs for detailed errors
4. Verify environment variables in `.env`

### Common Questions

**Q: Why is my query timing out?**
A: The system has a 30-second timeout. Large documents or complex queries may exceed this. Try breaking down your request or contact your administrator.

**Q: Can I use local databases instead of cloud?**
A: The system is designed for cloud-native operation. Local databases (SQLite, ChromaDB) are not recommended for production.

**Q: How do I add more test users?**
A: Run `python backend/seed_users.py` to create additional test users or modify the script to add custom users.

**Q: What file formats are supported?**
A: PDF, DOCX, DOC, and CSV files are supported for upload and processing.

---

## License

This project is developed for SDLC automation purposes. All rights reserved.

---

## Contributors

Developed by the SDLC Automation Team

---

## Project Status

**Production Ready**

**Completed Features:**
- JWT Authentication with role-based access control
- Admin Dashboard with user management
- AI Model Management interface
- PostgreSQL database (cloud-hosted on Render/Neon)
- Pinecone vector search (serverless, auto-index creation)
- Qdrant document store (cloud-hosted, auto-collection creation)
- NVIDIA Nemotron 3 Nano 30B LLM (16K context window)
- MCP Multi-Agent Pipeline (6 specialized agents)
- Session-based document isolation
- Real-time streaming responses
- Document upload (PDF, DOCX, CSV)
- AI-powered feedback system
- Timeout protection (30s inference limit)
- Priority-based document retrieval
- Next.js 16 + React 19 frontend
- Responsive UI with Tailwind CSS
- Admin user and model management APIs

**In Progress:**
- DOCX generation from MCP unified payload
- Enhanced error handling and logging
- Performance optimization

**Last Updated**: April 25, 2026  
**Version**: 2.1.0

---

## Recent Updates & Improvements

### April 2026 - v2.1.0 (Current Release)

#### Admin Dashboard & User Management
- **Admin Portal**: Comprehensive admin dashboard at `/admin`
- **User Management**: Create, edit, delete, and test user accounts
- **Role Assignment**: Assign multiple roles to users (BA, FBA, QA)
- **AI Model Management**: View, update, and manage AI models and API keys
- **Admin Authentication**: Secure admin login with separate credentials
- **User Testing**: Test user login credentials directly from admin panel

#### MCP Multi-Agent Pipeline
- **Integrated 6 specialized AI agents** for comprehensive document processing
- **Document Reader Agent**: Parses documents into structured JSON
- **5 Specialist Agents**: Requirements, Tables, Business Logic, Change Requests, Validation
- **Master Receiver Agent**: Merges all outputs with conflict resolution
- **7 JSON outputs**: Full transparency with intermediate files
- **Google Gemma 2 27B IT**: Dedicated model for MCP pipeline

#### LLM Migration
- **Switched to NVIDIA Nemotron 3 Nano 30B** for primary RAG queries
- **Increased context window**: 8K → 16K tokens
- **Improved generation quality**: Better BRD/FRD/Test Pack outputs
- **Dual-model architecture**: Nemotron for RAG, Gemma for MCP

#### Performance & Reliability
- **Timeout protection**: 30-second inference limit with graceful error handling
- **Priority-based retrieval**: Documents tagged with High/Medium/Low priority
- **Enhanced chunking**: 3000 chars with 400 char overlap
- **Increased retrieval**: Top 30 documents (vs 20) for better context

#### Session Management
- **Session-based document filtering**: Complete data isolation between sessions
- **Persistent chat history**: Messages stored in PostgreSQL
- **Session metadata**: Track user, role, and creation time

#### Cloud-Native Architecture
- **100% cloud databases**: PostgreSQL (Render), Pinecone, Qdrant
- **Auto-index creation**: Pinecone index created automatically on first run
- **Auto-collection creation**: Qdrant collection created automatically
- **Zero local overhead**: No SQLite or ChromaDB files

#### Developer Experience
- **Seed users**: Pre-configured test users for all roles
- **Interactive API docs**: Swagger UI at `/docs`
- **Environment templates**: `.env.example` for easy setup
- **Database utilities**: Reset and seed scripts

---
