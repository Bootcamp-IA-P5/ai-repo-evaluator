"""
ContextEngine — FAISS-based vector index for RAG semantic search.

This module provides the ContextEngine class that builds a FAISS vector
index from document chunks (briefing requirements, source code) and
enables semantic similarity search for the AI evaluation engine.

Used by the Grading Loop to retrieve the most relevant context
for each rubric criterion evaluation.
"""

from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

from core.logging_config import logger

# Type alias for documents: supports both dict and Document objects
DocumentInput = dict | Document


class ContextEngine:
    """
    FAISS-powered context retrieval engine for RAG.

    Converts document chunks into vector embeddings and provides
    semantic similarity search to find relevant context for each
    evaluation criterion.

    Attributes:
        embeddings: The Embeddings instance (Google or OpenAI) for vectorization.
        vector_store: FAISS index built from the provided documents.
    """

    def __init__(
        self,
        documents: list[DocumentInput],
        embedding_provider: str = None,
        embedding_model: str = None,
        embedding_api_key: str = None,
    ):
        """
        Initialize the context engine with documents and build the FAISS index.

        Args:
            documents: List of document dicts with 'page_content' and 'metadata'
                    keys, or langchain Document objects.
            embedding_provider: Optional "gemini" or "openai". Evaluates to settings default if None.
            embedding_model: Optional specific model name. Evaluates to settings default if None.
            embedding_api_key: Optional API key. Evaluates to environment key if None.

        Raises:
            ValueError: If documents list is empty or provider is unsupported.
        """
        if not documents:
            raise ValueError("Cannot create ContextEngine with an empty document list.")

        # Create the correct embeddings client using the factory method
        self.embeddings = self._create_embeddings(
            provider=embedding_provider,
            model=embedding_model,
            api_key=embedding_api_key
        )

        # Extract texts and metadatas from documents (support both dict and Document)
        texts, metadatas = self._extract_texts_and_metadatas(documents)

        # Build the FAISS vector store
        logger.info(f"Building FAISS index with {len(texts)} document chunks...")
        self.vector_store = FAISS.from_texts(texts, self.embeddings, metadatas=metadatas)
        logger.info("FAISS index created successfully.")

    def get_relevant_context(self, query: str, k: int = 5) -> list[dict]:
        """
        Perform semantic similarity search against the FAISS index.

        Args:
            query: Natural language query (e.g., "error handling requirements").
            k: Number of most similar document chunks to return.
s
        Returns:
            List of dicts, each with 'page_content' and 'metadata' keys,
            ordered by relevance (most similar first).
        """
        results = self.vector_store.similarity_search(query, k=k)

        context = [
            {
                "page_content": doc.page_content,
                "metadata": doc.metadata,
            }
            for doc in results
        ]

        logger.debug(
            f"Context search for '{query[:60]}...' returned {len(context)} results"
        )
        return context

    def add_documents(self, documents: list[DocumentInput]) -> None:
        """
        Add new documents to the existing FAISS index.

        Useful for combining briefing requirements and code files
        into a single searchable index.

        Args:
            documents: List of document dicts with 'page_content' and 'metadata'
                    keys, or langchain Document objects.

        Raises:
            ValueError: If documents list is empty.
        """
        if not documents:
            raise ValueError("Cannot add an empty document list.")

        texts, metadatas = self._extract_texts_and_metadatas(documents)

        self.vector_store.add_texts(texts, metadatas=metadatas)
        logger.info(f"Added {len(texts)} documents to FAISS index.")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_texts_and_metadatas(
        documents: list,
    ) -> tuple[list[str], list[dict]]:
        """
        Extract texts and metadatas from a mixed list of dicts / Document objects.

        Args:
            documents: List of dicts or Document objects.

        Returns:
            Tuple of (texts, metadatas).
        """
        texts = []
        metadatas = []

        for doc in documents:
            if isinstance(doc, Document):
                texts.append(doc.page_content)
                metadatas.append(doc.metadata)
            elif isinstance(doc, dict):
                texts.append(doc.get("page_content", ""))
                metadatas.append(doc.get("metadata", {}))
            else:
                raise TypeError(
                    f"Unsupported document type: {type(doc)}. "
                    "Expected dict or langchain Document."
                )

        return texts, metadatas

    @staticmethod
    def _create_embeddings(provider: str = None, model: str = None, api_key: str = None):
        """
        Factory method to create the appropriate Embeddings instance.
        """
        from core.settings import settings, get_api_key, AIProvider
        
        # Resolve provider
        resolved_provider = (provider or settings.EMBEDDING_PROVIDER).lower()

        # Resolve model
        resolved_model = model or settings.EMBEDDING_MODEL

        # Create specific embedding provider
        if resolved_provider == "gemini":
            # For Gemini, use the key or fallback to environment API key
            resolved_key = api_key or get_api_key(AIProvider.GEMINI)
            if not resolved_key:
                raise ValueError("Embedding API key is required for Gemini embeddings")
            
            return GoogleGenerativeAIEmbeddings(
                model=resolved_model,
                google_api_key=resolved_key,
            )
            
        elif resolved_provider == "openai":
            # For OpenAI, default model if not explicitly configured in settings for embeddings
            if not resolved_model:
                resolved_model = "text-embedding-3-small" # Sensible default for OpenAI
            
            resolved_key = api_key or get_api_key(AIProvider.OPENAI)
            if not resolved_key:
                raise ValueError("Embedding API key is required for OpenAI embeddings")
                
            return OpenAIEmbeddings(
                model=resolved_model,
                api_key=resolved_key,
            )
            
        else:
            raise ValueError(f"Unsupported embedding provider: {resolved_provider}. Supported providers: gemini, openai")
