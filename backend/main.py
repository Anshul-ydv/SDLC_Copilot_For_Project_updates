from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, chat, documents
from app.database import engine
from app import models

#  database tables. creation
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SDLC Automation API",
    description="RAG-powered Copilot for SDLC documents (BRDs, FRDs, Test Packs)",
    version="1.0.0"
)

# Configure CORS for frontend access ############# MIDDLEWARE #################
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#  Routers for page switcihng
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat & Generation"])

@app.get("/")
def read_root():
    return {"message": "Welcome to SDLC Automation API. Visit /docs for Swagger UI."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
