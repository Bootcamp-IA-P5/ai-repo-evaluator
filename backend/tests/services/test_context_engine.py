"""
Unit tests for ContextEngine.

Uses FakeEmbeddings from langchain so tests run without a real API key.
"""

import pytest
from unittest.mock import patch

from langchain_core.documents import Document
from langchain_core.embeddings import FakeEmbeddings


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FAKE_DIM = 64  # Dimension for fake embeddings (small = fast)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _sample_dicts(n: int = 5) -> list[dict]:
    """Generate sample document dicts matching the spec format."""
    topics = [
        "Error handling with try-except blocks",
        "Database connection pooling strategy",
        "REST API endpoint design patterns",
        "Unit testing with pytest framework",
        "Docker containerization configuration",
    ]
    return [
        {
            "page_content": topics[i % len(topics)] + f" chunk {i}",
            "metadata": {"source": "test", "type": "requirement", "chunk_index": i},
        }
        for i in range(n)
    ]


def _sample_documents(n: int = 3) -> list[Document]:
    """Generate sample langchain Document objects."""
    return [
        Document(
            page_content=f"Source code implementing feature {i}",
            metadata={"source": "test_repo", "type": "source_code", "index": i},
        )
        for i in range(n)
    ]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def fake_embeddings():
    """FakeEmbeddings — implements the full Embeddings interface without API."""
    return FakeEmbeddings(size=FAKE_DIM)




@pytest.fixture
def engine(fake_embeddings):
    """Create a ContextEngine with fake embeddings and sample documents."""
    from services.context_engine import ContextEngine

    docs = _sample_dicts(5)

    with patch("services.context_engine.GoogleGenerativeAIEmbeddings", return_value=fake_embeddings):
        return ContextEngine(documents=docs, embedding_provider="gemini", embedding_api_key="fake-gemini-key")


# ---------------------------------------------------------------------------
# Tests: __init__
# ---------------------------------------------------------------------------


class TestInit:
    """Tests for ContextEngine.__init__()."""

    def test_init_creates_vector_store(self, engine):
        """Verify the constructor builds a FAISS vector store."""
        assert engine.vector_store is not None
        assert hasattr(engine.vector_store, "similarity_search")

    def test_init_empty_documents_raises(self, fake_embeddings):
        """Verify empty document list raises ValueError."""
        from services.context_engine import ContextEngine

        with patch("services.context_engine.GoogleGenerativeAIEmbeddings", return_value=fake_embeddings):
            with pytest.raises(ValueError, match="empty"):
                ContextEngine(documents=[], embedding_provider="gemini", embedding_api_key="fake-gemini-key")

    def test_init_accepts_document_objects(self, fake_embeddings):
        """Verify constructor works with langchain Document objects too."""
        from services.context_engine import ContextEngine

        docs = _sample_documents(3)

        with patch("services.context_engine.GoogleGenerativeAIEmbeddings", return_value=fake_embeddings):
            engine = ContextEngine(documents=docs, embedding_provider="gemini", embedding_api_key="fake-gemini-key")

        assert engine.vector_store is not None


# ---------------------------------------------------------------------------
# Tests: Factory / Embeddings Creation
# ---------------------------------------------------------------------------


class TestFactory:
    """Tests for ContextEngine._create_embeddings() and provider logic."""

    def test_factory_creates_google_embeddings(self, fake_embeddings):
        """Verify default provider creates GoogleGenerativeAIEmbeddings."""
        from services.context_engine import ContextEngine
        
        docs = _sample_dicts(1)
        with patch("services.context_engine.GoogleGenerativeAIEmbeddings", return_value=fake_embeddings) as mock_gemini:
            engine = ContextEngine(documents=docs, embedding_provider="gemini", embedding_api_key="test-key")
            mock_gemini.assert_called_once()
            assert engine.embeddings == fake_embeddings

    def test_factory_creates_openai_embeddings(self, fake_embeddings):
        """Verify openai provider creates OpenAIEmbeddings."""
        from services.context_engine import ContextEngine
        
        docs = _sample_dicts(1)
        with patch("services.context_engine.OpenAIEmbeddings", return_value=fake_embeddings) as mock_openai:
            engine = ContextEngine(documents=docs, embedding_provider="openai", embedding_api_key="test-key")
            mock_openai.assert_called_once()
            assert engine.embeddings == fake_embeddings

    def test_factory_raises_for_unsupported_provider(self, fake_embeddings):
        """Verify unsupported provider raises ValueError."""
        from services.context_engine import ContextEngine
        
        docs = _sample_dicts(1)
        with pytest.raises(ValueError, match="Unsupported embedding provider"):
            ContextEngine(documents=docs, embedding_provider="unknown-provider")


# ---------------------------------------------------------------------------
# Tests: get_relevant_context
# ---------------------------------------------------------------------------


class TestGetRelevantContext:
    """Tests for ContextEngine.get_relevant_context()."""

    def test_returns_list_of_dicts(self, engine):
        """Verify the method returns list[dict] with expected keys."""
        results = engine.get_relevant_context("error handling", k=3)

        assert isinstance(results, list)
        assert len(results) <= 3
        for item in results:
            assert isinstance(item, dict)
            assert "page_content" in item
            assert "metadata" in item

    def test_respects_k_parameter(self, engine):
        """Verify the k parameter limits the number of results."""
        results_2 = engine.get_relevant_context("database", k=2)
        results_4 = engine.get_relevant_context("database", k=4)

        assert len(results_2) <= 2
        assert len(results_4) <= 4

    def test_metadata_preserved(self, engine):
        """Verify that document metadata survives the round-trip."""
        results = engine.get_relevant_context("testing", k=1)

        assert len(results) >= 1
        metadata = results[0]["metadata"]
        assert "source" in metadata
        assert "type" in metadata


# ---------------------------------------------------------------------------
# Tests: add_documents
# ---------------------------------------------------------------------------


class TestAddDocuments:
    """Tests for ContextEngine.add_documents()."""

    def test_add_documents_extends_index(self, engine):
        """Verify new documents are added to the existing index."""
        # Original index has 5 docs
        initial_results = engine.get_relevant_context("any query", k=10)
        initial_count = len(initial_results)

        # Add 3 more
        new_docs = _sample_dicts(3)
        engine.add_documents(new_docs)

        # Now we should have more docs available
        new_results = engine.get_relevant_context("any query", k=10)
        assert len(new_results) > initial_count

    def test_add_documents_empty_raises(self, engine):
        """Verify adding empty list raises ValueError."""
        with pytest.raises(ValueError, match="empty"):
            engine.add_documents([])

    def test_add_document_objects(self, engine):
        """Verify add_documents works with langchain Document objects."""
        new_docs = _sample_documents(2)
        engine.add_documents(new_docs)

        results = engine.get_relevant_context("source code feature", k=10)
        assert len(results) > 0
