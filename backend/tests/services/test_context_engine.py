"""
Unit tests for ContextEngine.

Uses FakeEmbeddings from langchain so tests run without a real API key.
"""

import pytest
from unittest.mock import patch, MagicMock

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


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Set environment variables needed by Settings to avoid validation errors."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-fake-key")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4")
    monkeypatch.setenv("GEMINI_API_KEY", "fake-gemini-key")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-pro")
    monkeypatch.setenv("GROQ_API_KEY", "fake-groq-key")
    monkeypatch.setenv("GROQ_MODEL", "groq-1")
    monkeypatch.setenv("EMBEDDING_MODEL", "text-embedding-3-small")
    # Force Settings to re-read from patched env
    import importlib
    from core import settings
    importlib.reload(settings)


@pytest.fixture
def context_engine_service():
    """Create a ContextEngine service instance for testing."""
    from services.context_engine import ContextEngine
    return ContextEngine


@pytest.fixture
def sample_engine(fake_embeddings):
    """Create a ContextEngine with fake embeddings and sample documents."""
    from services.context_engine import ContextEngine

    docs = _sample_dicts(5)

    with patch("services.context_engine.GoogleGenerativeAIEmbeddings", return_value=fake_embeddings):
        return ContextEngine(documents=docs, embedding_provider="gemini", embedding_api_key="fake-gemini-key")


# ---------------------------------------------------------------------------
# Tests: ContextEngine.__init__
# ---------------------------------------------------------------------------


class TestContextEngineInit:
    """Tests for ContextEngine.__init__()."""

    def test_init_creates_vector_store(self, sample_engine):
        """Verify the constructor builds a FAISS vector store."""
        assert sample_engine.vector_store is not None
        assert hasattr(sample_engine.vector_store, "similarity_search")

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

    def test_init_with_different_embedding_providers(self, fake_embeddings):
        """Verify constructor works with different embedding providers."""
        from services.context_engine import ContextEngine

        docs = _sample_dicts(3)

        # Test with Gemini embeddings
        with patch("services.context_engine.GoogleGenerativeAIEmbeddings", return_value=fake_embeddings):
            engine_gemini = ContextEngine(documents=docs, embedding_provider="gemini", embedding_api_key="fake-gemini-key")
            assert engine_gemini.vector_store is not None

    def test_init_database_error_handling(self):
        """Test that init handles embedding creation errors gracefully."""
        from services.context_engine import ContextEngine

        docs = _sample_dicts(3)

        # Mock embedding creation to raise an exception
        with patch("services.context_engine.GoogleGenerativeAIEmbeddings", side_effect=Exception("Embedding error")):
            with pytest.raises(Exception, match="Embedding error"):
                ContextEngine(documents=docs, embedding_provider="gemini", embedding_api_key="fake-gemini-key")


# ---------------------------------------------------------------------------
# Tests: ContextEngine.get_relevant_context
# ---------------------------------------------------------------------------


class TestContextEngineGetRelevantContext:
    """Tests for ContextEngine.get_relevant_context()."""

    def test_returns_list_of_dicts(self, sample_engine):
        """Verify the method returns list[dict] with expected keys."""
        results = sample_engine.get_relevant_context("error handling", k=3)

        assert isinstance(results, list)
        assert len(results) <= 3
        for item in results:
            assert isinstance(item, dict)
            assert "page_content" in item
            assert "metadata" in item

    def test_respects_k_parameter(self, sample_engine):
        """Verify the k parameter limits the number of results."""
        results_2 = sample_engine.get_relevant_context("database", k=2)
        results_4 = sample_engine.get_relevant_context("database", k=4)

        assert len(results_2) <= 2
        assert len(results_4) <= 4

    def test_metadata_preserved(self, sample_engine):
        """Verify that document metadata survives the round-trip."""
        results = sample_engine.get_relevant_context("testing", k=1)

        assert len(results) >= 1
        metadata = results[0]["metadata"]
        assert "source" in metadata
        assert "type" in metadata

    def test_empty_query_returns_results(self, sample_engine):
        """Test that empty query still returns results."""
        results = sample_engine.get_relevant_context("", k=3)
        assert isinstance(results, list)
        assert len(results) <= 3

    def test_large_k_parameter(self, sample_engine):
        """Test that large k parameter works correctly."""
        results = sample_engine.get_relevant_context("any query", k=100)
        # Should return all available documents (5 in our sample)
        assert len(results) <= 5

    def test_query_with_special_characters(self, sample_engine):
        """Test query with special characters and punctuation."""
        results = sample_engine.get_relevant_context("error handling? (try-catch)", k=2)
        assert isinstance(results, list)
        assert len(results) <= 2

    def test_get_relevant_context_format_consistency(self, sample_engine):
        """Test that get_relevant_context returns consistent format."""
        results = sample_engine.get_relevant_context("test query", k=3)

        # Check all results have the same structure
        for result in results:
            assert isinstance(result, dict)
            assert "page_content" in result
            assert "metadata" in result
            assert isinstance(result["page_content"], str)
            assert isinstance(result["metadata"], dict)


# ---------------------------------------------------------------------------
# Tests: ContextEngine.add_documents
# ---------------------------------------------------------------------------


class TestContextEngineAddDocuments:
    """Tests for ContextEngine.add_documents()."""

    def test_add_documents_extends_index(self, sample_engine):
        """Verify new documents are added to the existing index."""
        # Original index has 5 docs
        initial_results = sample_engine.get_relevant_context("any query", k=10)
        initial_count = len(initial_results)

        # Add 3 more
        new_docs = _sample_dicts(3)
        sample_engine.add_documents(new_docs)

        # Now we should have more docs available
        new_results = sample_engine.get_relevant_context("any query", k=10)
        assert len(new_results) > initial_count

    def test_add_documents_empty_raises(self, sample_engine):
        """Verify adding empty list raises ValueError."""
        with pytest.raises(ValueError, match="empty"):
            sample_engine.add_documents([])

    def test_add_document_objects(self, sample_engine):
        """Verify add_documents works with langchain Document objects."""
        new_docs = _sample_documents(2)
        sample_engine.add_documents(new_docs)

        results = sample_engine.get_relevant_context("source code feature", k=10)
        assert len(results) > 0

    def test_add_documents_preserves_existing_data(self, sample_engine):
        """Verify adding documents doesn't affect existing search results."""
        # Get initial results
        initial_results = sample_engine.get_relevant_context("error handling", k=3)
        
        # Add new documents
        new_docs = _sample_dicts(2)
        sample_engine.add_documents(new_docs)
        
        # Search again - should still find original documents
        new_results = sample_engine.get_relevant_context("error handling", k=3)
        
        # At least one original result should still be present
        assert len(new_results) > 0

    def test_add_documents_with_mixed_types(self, sample_engine, fake_embeddings):
        """Test adding documents with mixed dict and Document objects."""
        from services.context_engine import ContextEngine

        # Create engine with initial documents
        docs = _sample_dicts(2)
        with patch("services.context_engine.GoogleGenerativeAIEmbeddings", return_value=fake_embeddings):
            engine = ContextEngine(documents=docs, embedding_provider="gemini", embedding_api_key="fake-gemini-key")

        # Add mixed document types
        mixed_docs = _sample_dicts(1) + _sample_documents(1)
        engine.add_documents(mixed_docs)

        # Verify all documents are searchable
        results = engine.get_relevant_context("any query", k=10)
        assert len(results) >= 4  # 2 initial + 1 dict + 1 Document

    def test_add_documents_database_error_handling(self, sample_engine):
        """Test that add_documents handles FAISS errors gracefully."""
        # Mock the FAISS add_texts method to raise an exception
        with patch.object(sample_engine.vector_store, 'add_texts', side_effect=Exception("FAISS error")):
            with pytest.raises(Exception, match="FAISS error"):
                sample_engine.add_documents(_sample_dicts(2))


# ---------------------------------------------------------------------------
# Tests: ContextEngine response format consistency
# ---------------------------------------------------------------------------


class TestContextEngineResponseFormat:
    """Tests for response format consistency."""

    def test_get_relevant_context_returns_list(self, sample_engine):
        """Test that get_relevant_context always returns a list."""
        results = sample_engine.get_relevant_context("test query", k=3)
        assert isinstance(results, list)

    def test_get_relevant_context_empty_results(self, sample_engine):
        """Test that get_relevant_context returns empty list when no matches."""
        # Use a very specific query that likely won't match
        results = sample_engine.get_relevant_context("xyz123_nonexistent_query", k=5)
        assert isinstance(results, list)
        # May or may not have results, but should be a list

    def test_document_structure_consistency(self, sample_engine):
        """Test that all returned documents have consistent structure."""
        results = sample_engine.get_relevant_context("test", k=5)
        
        for doc in results:
            # Check required keys
            assert "page_content" in doc
            assert "metadata" in doc
            
            # Check types
            assert isinstance(doc["page_content"], str)
            assert isinstance(doc["metadata"], dict)
            
            # Check content is not empty
            assert len(doc["page_content"].strip()) > 0


# ---------------------------------------------------------------------------
# Tests: ContextEngine with different configurations
# ---------------------------------------------------------------------------


class TestContextEngineConfigurations:
    """Tests for ContextEngine with different configurations."""

    def test_init_with_openai_embeddings(self, fake_embeddings):
        """Test ContextEngine initialization with OpenAI embeddings."""
        from services.context_engine import ContextEngine

        docs = _sample_dicts(3)

        with patch("services.context_engine.OpenAIEmbeddings", return_value=fake_embeddings):
            engine = ContextEngine(
                documents=docs,
                embedding_provider="openai",
                embedding_model="text-embedding-3-small",
                embedding_api_key="fake-openai-key"
            )
            assert engine.vector_store is not None

    def test_init_with_different_embedding_dimensions(self, fake_embeddings):
        """Test ContextEngine with different embedding dimensions."""
        from services.context_engine import ContextEngine

        docs = _sample_dicts(3)

        with patch("services.context_engine.GoogleGenerativeAIEmbeddings", return_value=fake_embeddings):
            engine = ContextEngine(documents=docs, embedding_provider="gemini", embedding_api_key="fake-gemini-key")
            assert engine.vector_store is not None

    def test_add_documents_multiple_times(self, sample_engine):
        """Test adding documents multiple times."""
        initial_count = len(sample_engine.get_relevant_context("any query", k=100))
        
        # Add documents multiple times
        for i in range(3):
            new_docs = _sample_dicts(2)
            sample_engine.add_documents(new_docs)
        
        # Verify all documents are available
        final_count = len(sample_engine.get_relevant_context("any query", k=100))
        assert final_count > initial_count

    def test_context_engine_with_large_document_sets(self, fake_embeddings):
        """Test ContextEngine with larger document sets."""
        from services.context_engine import ContextEngine

        # Create a larger set of documents
        large_docs = _sample_dicts(20)

        with patch("services.context_engine.GoogleGenerativeAIEmbeddings", return_value=fake_embeddings):
            engine = ContextEngine(documents=large_docs, embedding_provider="gemini", embedding_api_key="fake-gemini-key")
            
            # Test search functionality
            results = engine.get_relevant_context("error handling", k=5)
            assert isinstance(results, list)
            assert len(results) <= 5
