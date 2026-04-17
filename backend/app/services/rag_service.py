# RAG Service - Online Database Stack
# Relational: PostgreSQL (via DATABASE_URL in .env)
# Vector Search: Pinecone (via PINECONE_API_KEY + PINECONE_INDEX_NAME in .env)
# Document Store: Qdrant Cloud (via QDRANT_URL + QDRANT_API_KEY in .env)

import os
from langchain_community.document_loaders import PyPDFLoader, CSVLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from app.services.prompt_templates import get_prompt_for_role
from dotenv import load_dotenv

load_dotenv()

# ── Load API Keys from .env ───────────────────────────────────────────────────
GROQ_API_KEY     = os.getenv("GROQ_API_KEY", "")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_INDEX   = os.getenv("PINECONE_INDEX_NAME", "sdlc-copilot")
QDRANT_URL       = os.getenv("QDRANT_URL", "")
QDRANT_API_KEY   = os.getenv("QDRANT_API_KEY", "")
QDRANT_COLLECTION= os.getenv("QDRANT_COLLECTION_NAME", "sdlc_documents")

if GROQ_API_KEY:
    os.environ["GROQ_API_KEY"] = GROQ_API_KEY
else:
    print("Warning: GROQ_API_KEY not found in environment.")


class RAGService:
    def __init__(self):
        # ── 1. Embedding Model (shared between Pinecone & Qdrant) ────────────
        try:
            self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        except Exception as e:
            print(f"Warning: Could not load embeddings model: {e}")
            self.embeddings = None

        # ── 2. Pinecone (Vector Search for RAG retrieval) ────────────────────
        self.pinecone_store = None
        if PINECONE_API_KEY and self.embeddings:
            try:
                from pinecone import Pinecone, ServerlessSpec
                from langchain_pinecone import PineconeVectorStore

                pc = Pinecone(api_key=PINECONE_API_KEY)

                # Create index if it does not already exist
                existing_indexes = [idx.name for idx in pc.list_indexes()]
                if PINECONE_INDEX not in existing_indexes:
                    pc.create_index(
                        name=PINECONE_INDEX,
                        dimension=384,       # all-MiniLM-L6-v2 output dim
                        metric="cosine",
                        spec=ServerlessSpec(cloud="aws", region="us-east-1")
                    )
                    print(f"Pinecone index '{PINECONE_INDEX}' created.")

                self.pinecone_store = PineconeVectorStore(
                    index_name=PINECONE_INDEX,
                    embedding=self.embeddings,
                    pinecone_api_key=PINECONE_API_KEY
                )
                print("Pinecone vector store connected successfully.")
            except Exception as e:
                print(f"Warning: Could not connect to Pinecone: {e}")

        # ── 3. Qdrant (Document Save / Full-text + Vector Search) ────────────
        self.qdrant_store = None
        if QDRANT_URL and QDRANT_API_KEY and self.embeddings:
            try:
                from qdrant_client import QdrantClient
                from qdrant_client.models import Distance, VectorParams
                from langchain_qdrant import QdrantVectorStore

                qdrant_client = QdrantClient(
                    url=QDRANT_URL,
                    api_key=QDRANT_API_KEY,
                )

                # Create collection if it doesn't exist
                existing = [c.name for c in qdrant_client.get_collections().collections]
                if QDRANT_COLLECTION not in existing:
                    qdrant_client.create_collection(
                        collection_name=QDRANT_COLLECTION,
                        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                    )
                    print(f"Qdrant collection '{QDRANT_COLLECTION}' created.")

                self.qdrant_store = QdrantVectorStore(
                    client=qdrant_client,
                    collection_name=QDRANT_COLLECTION,
                    embedding=self.embeddings,
                )
                print("Qdrant document store connected successfully.")
            except Exception as e:
                print(f"Warning: Could not connect to Qdrant: {e}")

        # ── 4. LLM ───────────────────────────────────────────────────────────
        self.llm = None
        try:
            self.llm = ChatGroq(temperature=0.2, model_name="llama-3.3-70b-versatile")
        except Exception as e:
            print(f"Warning: Could not initialize Groq LLM: {e}")

        # ── 5. Text Splitter ─────────────────────────────────────────────────
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )

    # ── Process & Store Documents ─────────────────────────────────────────────
    def process_file(self, file_path: str, filename: str):
        """
        Extract text from a document, chunk it, and store chunks in:
          - Pinecone (for semantic RAG retrieval in generate_answer)
          - Qdrant   (for document search and raw document access)
        """
        documents = []
        try:
            if filename.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
                documents = loader.load()
            elif filename.endswith(".csv"):
                loader = CSVLoader(file_path)
                documents = loader.load()
            elif filename.endswith((".doc", ".docx")):
                loader = Docx2txtLoader(file_path)
                documents = loader.load()
            else:
                print(f"Unsupported file type for: {filename}")
                return

            texts = self.text_splitter.split_documents(documents)

            # Store in Pinecone for RAG retrieval
            if self.pinecone_store:
                self.pinecone_store.add_documents(texts)
                print(f"[Pinecone] Indexed {len(texts)} chunks from '{filename}'")

            # Store in Qdrant for document search/save
            if self.qdrant_store:
                self.qdrant_store.add_documents(texts)
                print(f"[Qdrant] Saved {len(texts)} chunks from '{filename}'")

            if not self.pinecone_store and not self.qdrant_store:
                print("Warning: No online vector store configured. Check your .env keys.")

        except Exception as e:
            print(f"Failed parsing file '{filename}': {str(e)}")
            raise

    # ── Generate Answer via RAG ───────────────────────────────────────────────
    def generate_answer(self, query: str, role: str, task_type: str = None) -> str:
        """Retrieve context from Pinecone and generate a structured response via Groq."""
        system_prompt = get_prompt_for_role(role, task_type)

        # Use Qdrant as fallback if Pinecone is unavailable
        active_store = self.pinecone_store or self.qdrant_store

        if not active_store or not self.llm:
            return (
                f"[Mock Response]: No online vector store or LLM connected.\n\n"
                f"System prompt that would be used:\n{system_prompt}"
            )

        retriever = active_store.as_retriever(search_kwargs={"k": 20})

        search_query = query
        if task_type in ["brd", "frd", "test_pack"] and len(query) < 100:
            search_query = "business requirements functional specifications system architecture features overview constraints"

        template = (
            f"SYSTEM INSTRUCTIONS:\n{system_prompt}\n\n"
            "CONTEXT DOCUMENTS:\n{context}\n\n"
            "USER REQUEST:\n{question}\n\n"
            "FINAL RESPONSE (Provide ONLY the content):"
        )

        try:
            docs = retriever.invoke(search_query)
            context = "\n\n".join([doc.page_content for doc in docs])
            final_prompt = template.format(context=context, question=query)
            response = self.llm.invoke(final_prompt)
            return response.content if hasattr(response, "content") else str(response)
        except Exception as e:
            return f"Error in RAG pipeline: {str(e)}"

    # ── Stream Answer via RAG ─────────────────────────────────────────────────
    def stream_answer(self, query: str, role: str, task_type: str = None):
        """Stream response chunks directly from the LLM."""
        system_prompt = get_prompt_for_role(role, task_type)

        active_store = self.pinecone_store or self.qdrant_store

        if not active_store or not self.llm:
            yield f"[Mock Streaming]: {system_prompt[:80]}..."
            return

        retriever = active_store.as_retriever(search_kwargs={"k": 20})

        search_query = query
        if task_type in ["brd", "frd", "test_pack"] and len(query) < 100:
            search_query = "business requirements functional specifications system architecture features overview constraints"

        template = (
            f"SYSTEM INSTRUCTIONS:\n{system_prompt}\n\n"
            "CONTEXT DOCUMENTS:\n{context}\n\n"
            "USER REQUEST:\n{question}\n\n"
            "FINAL RESPONSE (Provide ONLY the content):"
        )

        try:
            docs = retriever.invoke(search_query)
            context = "\n\n".join([doc.page_content for doc in docs])
            final_prompt = template.format(context=context, question=query)

            for chunk in self.llm.stream(final_prompt):
                content = chunk.content if hasattr(chunk, "content") else str(chunk)
                if content:
                    yield content
        except Exception as e:
            yield f"Error in stream: {str(e)}"


# Singleton
rag_service = RAGService()
