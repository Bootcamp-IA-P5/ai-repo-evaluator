"""
ContextEngine — FAISS-based vector index for RAG semantic search.

This module provides the ContextEngine class that builds a FAISS vector
index from document chunks (briefing requirements, source code) and
enables semantic similarity search for the AI evaluation engine.

Used by the Grading Loop to retrieve the most relevant context
for each rubric criterion evaluation.
"""

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

from core.logging_config import logger


class ContextEngine:
    """
    FAISS-powered context retrieval engine for RAG.

    Converts document chunks into vector embeddings and provides
    semantic similarity search to find relevant context for each
    evaluation criterion.

    Attributes:
        embeddings: OpenAIEmbeddings instance for vectorization.
        vector_store: FAISS index built from the provided documents.
    """

    def __init__(self, documents: list[dict], openai_api_key: str = None):
        """
        Initialize the context engine with documents and build the FAISS index.

        Args:
            documents: List of document dicts with 'page_content' and 'metadata'
                       keys, or langchain Document objects.
            openai_api_key: OpenAI API key for embeddings. If None, reads from
                            settings.OPENAI_API_KEY (BYOK pattern).

        Raises:
            ValueError: If documents list is empty.
        """
        if not documents:
            raise ValueError("Cannot create ContextEngine with an empty document list.")

        # Lazy import to avoid triggering pydantic validation at module level
        from core.settings import settings

        # BYOK: use provided key or fall back to environment config
        api_key = openai_api_key or settings.OPENAI_API_KEY
        self.embeddings = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            openai_api_key=api_key,
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

    def add_documents(self, documents: list[dict]) -> None:
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
