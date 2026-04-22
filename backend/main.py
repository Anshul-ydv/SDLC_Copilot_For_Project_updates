from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, chat, documents, mcp
from app.database import engine
from app import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SDLC Automation API",
    description="RAG-powered Copilot for SDLC documents (BRDs, FRDs, Test Packs) with MCP Multi-Agent Pipeline",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat & Generation"])
app.include_router(mcp.router, prefix="/api/mcp", tags=["MCP Pipeline"])

@app.get("/")
def read_root():
    return {
        "message": "Welcome to SDLC Automation API with MCP Multi-Agent Pipeline",
        "version": "2.1.0",
        "features": [
            "RAG-powered document generation",
            "MCP multi-agent document processing",
            "Session-based isolation",
            "Real-time streaming responses"
        ],
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
