# RAG Service for processing documents and generating responses
import os
from tempfile import NamedTemporaryFile
from langchain_community.document_loaders import PyPDFLoader, CSVLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from app.services.prompt_templates import get_prompt_for_role

#  load this securely from .env
if "GROQ_API_KEY" not in os.environ:
    # Use getenv if not already in environ (e.g. from .env file loaded in main.py)
    os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY", "")

if not os.environ.get("GROQ_API_KEY"):
    print("Warning: GROQ_API_KEY not found in environment variables.")

class RAGService:
    def __init__(self):
        # Initialize Embeddings Models
        try:
            self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            # Initialize persistent local VectorDB using ChromaDB
            self.db_dir = "./chroma_db"
            os.makedirs(self.db_dir, exist_ok=True)
            self.vectorstore = Chroma(
                persist_directory=self.db_dir, 
                embedding_function=self.embeddings,
                collection_name="sdlc_reference_docs"
            )
            # LLM configured for precision - Updated to a supported model
            self.llm = ChatGroq(temperature=0.2, model_name="llama-3.3-70b-versatile")
        except Exception as e:
            import traceback
            print(f"Warning: RAG Initialization Mock mode due to API keys or Network: {e}")
            traceback.print_exc()
            self.llm = None
            self.vectorstore = None

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
        
    def process_file(self, file_path: str, filename: str):
        """ Extract text from documents, chunk them, and store in Chroma VectorDB. """
        if not self.vectorstore:
            return

        documents = []
        try:
            # Handle different document types
            if filename.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
                documents = loader.load()
            elif filename.endswith(".csv"):
                loader = CSVLoader(file_path)
                documents = loader.load()
            elif filename.endswith(".doc") or filename.endswith(".docx"):
                # langchain extension needed for docx, mocking extraction for example
                loader = Docx2txtLoader(file_path) 
                documents = loader.load()
            
            # Split texts and index
            texts = self.text_splitter.split_documents(documents)
            self.vectorstore.add_documents(texts)
            
            print(f"Successfully processed and embedded {len(texts)} chunks from {filename}")
        except Exception as e:
            print(f"Failed parsing file {filename}: {str(e)}")

    def generate_answer(self, query: str, role: str, task_type: str = None) -> str:
        """ Retrieve context from ChromaDB and generate structured response via OpenAI. """
        
        # Determine the role-specific rules and markdown templates
        system_prompt = get_prompt_for_role(role, task_type)

        if not self.vectorstore or not self.llm:
            # MOCK OFFLINE CAPABILITY 
            return f"[Mock Response logic. The system prompt executed was]:\n\n{system_prompt}\n\n[End Mock] I analyzed the reference documents and produced an output for your query: '{query}'"

        # Create RetrievalQA chain
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 20}) # Increased context window
        
        # Optimize semantic retrieval query if user clicked a generic action button
        search_query = query
        if task_type in ["brd", "frd", "test_pack"] and len(query) < 100:
             search_query = "business requirements functional specifications system architecture features overview constraints"

        # Define Instruction template injecting the retrieved docs and system prompt
        template = (
            f"SYSTEM INSTRUCTIONS:\n{system_prompt}\n\n"
            "CONTEXT DOCUMENTS:\n{context}\n\n"
            "USER REQUEST:\n{question}\n\n"
            "FINAL RESPONSE (Provide ONLY the content):"
        )
        qa_prompt = PromptTemplate(template=template, input_variables=["context", "question"])

        try:
            # 1. Retrieve relevant docs using the optimized search phrase
            docs = retriever.invoke(search_query)
            context = "\n\n".join([doc.page_content for doc in docs])
            
            # 2. Format the prompt directly
            final_prompt = template.format(context=context, question=query)
            
            # 3. Invoke LLM 
            response = self.llm.invoke(final_prompt)
            
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            return f"Error connecting to the LLM pipeline: {str(e)}"

    def stream_answer(self, query: str, role: str, task_type: str = None):
        """ Stream response chunks directly from the LLM. """
        system_prompt = get_prompt_for_role(role, task_type)

        if not self.vectorstore or not self.llm:
            yield f"[Mock Streaming]: {system_prompt[:50]}..."
            return

        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 20}) # Increased context window
        
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
            
            # Use .stream() for real-time output
            for chunk in self.llm.stream(final_prompt):
                content = chunk.content if hasattr(chunk, 'content') else str(chunk)
                if content:
                    yield content
        except Exception as e:
            yield f"Error in stream: {str(e)}"

# Singleton RAG instance
rag_service = RAGService()
