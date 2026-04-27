# RAG Service
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from langchain_community.document_loaders import PyPDFLoader, CSVLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from app.services.prompt_templates import get_prompt_for_role
from dotenv import load_dotenv

load_dotenv()

# Timeout configuration
INFERENCE_TIMEOUT_SECONDS = 30

# ── Load API Keys from .env ───────────────────────────────────────────────────
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_INDEX   = os.getenv("PINECONE_INDEX_NAME", "sdlc-copilot")
QDRANT_URL       = os.getenv("QDRANT_URL", "")
QDRANT_API_KEY   = os.getenv("QDRANT_API_KEY", "")
QDRANT_COLLECTION= os.getenv("QDRANT_COLLECTION_NAME", "sdlc_documents")

if OPENROUTER_API_KEY:
    os.environ["OPENROUTER_API_KEY"] = OPENROUTER_API_KEY
else:
    print("Warning: OPENROUTER_API_KEY not found in environment.")


class RAGService:
    def __init__(self):
        # ── 1. Embedding Model ────────────────────────────────────────────────
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
        except Exception as e:
            print(f"Warning: Could not load embeddings model: {e}")
            self.embeddings = None

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

        self.llm = None
        try:
            self.llm = ChatOpenAI(
                model="nvidia/nemotron-3-nano-30b-a3b:free",
                openai_api_key=OPENROUTER_API_KEY,
                openai_api_base="https://openrouter.ai/api/v1",
                temperature=0.3,
                max_completion_tokens=16000,
                default_headers={
                    "HTTP-Referer": "https://sdlc-copilot.app",
                    "X-Title": "SDLC Automation Copilot"
                }
            )
            print("OpenRouter LLM (NVIDIA Nemotron 3 Nano 30B) initialized successfully.")
        except Exception as e:
            print(f"Warning: Could not initialize OpenRouter LLM: {e}")

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=3000,
            chunk_overlap=400,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Thread pool for timeout handling
        self.executor = ThreadPoolExecutor(max_workers=4)

    def _invoke_with_timeout(self, prompt: str, timeout: int = INFERENCE_TIMEOUT_SECONDS):
        """
        Invoke LLM with timeout protection.
        
        Args:
            prompt: The prompt to send to LLM
            timeout: Timeout in seconds (default 30)
            
        Returns:
            LLM response
            
        Raises:
            TimeoutError: If inference takes longer than timeout
        """
        try:
            future = self.executor.submit(self.llm.invoke, prompt)
            result = future.result(timeout=timeout)
            return result
        except FuturesTimeoutError:
            raise TimeoutError(f"AI model inference timed out after {timeout} seconds. Please try again or contact your administrator.")
        except Exception as e:
            raise Exception(f"Error during inference: {str(e)}")

    def process_file(self, file_path: str, filename: str, session_id: str = None, priority: str = "Medium"):
        """Extract, chunk, and store document in Pinecone and Qdrant."""
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

            for text in texts:
                if not hasattr(text, 'metadata'):
                    text.metadata = {}
                text.metadata['priority'] = priority
                text.metadata['filename'] = filename
                text.metadata['session_id'] = session_id or "global"

            if self.pinecone_store:
                try:
                    self.pinecone_store.add_documents(texts)
                    print(f"[Pinecone] Indexed {len(texts)} chunks from '{filename}' for session '{session_id}' with priority '{priority}'")
                except Exception as e:
                    print(f"[Pinecone] Error indexing documents: {e}")

            if self.qdrant_store:
                try:
                    self.qdrant_store.add_documents(texts)
                    print(f"[Qdrant] Saved {len(texts)} chunks from '{filename}' for session '{session_id}' with priority '{priority}'")
                except Exception as e:
                    print(f"[Qdrant] Error saving documents: {e}")

            if not self.pinecone_store and not self.qdrant_store:
                print("Warning: No online vector store configured. Check your .env keys.")
                raise Exception("No vector store available for document indexing")

        except Exception as e:
            print(f"Failed parsing file '{filename}': {str(e)}")
            raise

    # ── Generate Answer via RAG ───────────────────────────────────────────────
    def generate_answer(self, query: str, role: str, session_id: str = None, task_type: str = None) -> str:

        role_task_matrix = {
            'brd': ['Business Analyst (BA)'],
            'frd': ['Functional BA (FBA)'],
            'test_pack': ['QA / Tester']
        }
        
        if task_type and task_type in role_task_matrix:
            allowed_roles = role_task_matrix[task_type]
            if role not in allowed_roles:
                return f"This document type is available for {', '.join(allowed_roles)} roles. Please open a new session with the appropriate role."
        
        system_prompt = get_prompt_for_role(role, task_type)

        active_store = self.pinecone_store or self.qdrant_store

        if not active_store or not self.llm:
            return (
                f"[Mock Response]: No online vector store or LLM connected.\n\n"
                f"System prompt that would be used:\n{system_prompt}"
            )

        search_kwargs = {"k": 30}
        if session_id:
            search_kwargs["filter"] = {"session_id": session_id}

        retriever = active_store.as_retriever(search_kwargs=search_kwargs)

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

            scored_docs = []
            for doc in docs:
                score = getattr(doc, 'score', 1.0)
                priority = doc.metadata.get('priority', 'Medium')
                if priority == 'High':
                    score *= 1.3
                scored_docs.append((doc, score))

            scored_docs.sort(key=lambda x: x[1], reverse=True)
            context = "\n\n".join([doc.page_content for doc, _ in scored_docs[:30]])

            final_prompt = template.format(context=context, question=query)
            
            # Use timeout-protected invoke
            response = self._invoke_with_timeout(final_prompt, timeout=INFERENCE_TIMEOUT_SECONDS)
            return response.content if hasattr(response, "content") else str(response)
        except TimeoutError as e:
            return f"The AI model is currently unavailable. Please contact your administrator. (Timeout after {INFERENCE_TIMEOUT_SECONDS} seconds)"
        except Exception as e:
            return f"Error in RAG pipeline: {str(e)}"

    # ── Stream Answer via RAG ─────────────────────────────────────────────────
    def stream_answer(self, query: str, role: str, session_id: str = None, task_type: str = None):
        system_prompt = get_prompt_for_role(role, task_type)

        active_store = self.pinecone_store or self.qdrant_store

        if not active_store or not self.llm:
            yield f"[Mock Streaming]: {system_prompt[:80]}..."
            return

        search_kwargs = {"k": 30}
        if session_id:
            search_kwargs["filter"] = {"session_id": session_id}

        retriever = active_store.as_retriever(search_kwargs=search_kwargs)

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

            scored_docs = []
            for doc in docs:
                score = getattr(doc, 'score', 1.0)
                priority = doc.metadata.get('priority', 'Medium')
                if priority == 'High':
                    score *= 1.3
                scored_docs.append((doc, score))

            scored_docs.sort(key=lambda x: x[1], reverse=True)
            context = "\n\n".join([doc.page_content for doc, _ in scored_docs[:30]])

            final_prompt = template.format(context=context, question=query)

            # Stream with timeout protection
            start_time = asyncio.get_event_loop().time() if hasattr(asyncio, 'get_event_loop') else 0
            chunk_count = 0
            
            for chunk in self.llm.stream(final_prompt):
                # Check timeout
                if start_time > 0:
                    elapsed = asyncio.get_event_loop().time() - start_time
                    if elapsed > INFERENCE_TIMEOUT_SECONDS:
                        yield f"\n\n[Error: Response generation timed out after {INFERENCE_TIMEOUT_SECONDS} seconds]"
                        return
                
                content = chunk.content if hasattr(chunk, "content") else str(chunk)
                if content:
                    chunk_count += 1
                    yield content
            
            # If no chunks received within timeout, it's a timeout
            if chunk_count == 0:
                yield f"The AI model is currently unavailable. Please contact your administrator."
                
        except TimeoutError:
            yield f"The AI model is currently unavailable. Please contact your administrator. (Timeout after {INFERENCE_TIMEOUT_SECONDS} seconds)"
        except Exception as e:
            yield f"Error in stream: {str(e)}"


# Singleton
rag_service = RAGService()
