"""
Unit tests for AIEvaluationEngine.

This module contains comprehensive tests for the AIEvaluationEngine class,
covering all evaluation operations and error handling scenarios.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from services.ai_evaluation_engine import AIEvaluationEngine
from services.evaluation_service_api import run_evaluation_task
from services.ai_client import AIProvider
from models import Evaluation, Rubric, Criterion, Level, Finding
from core.settings import settings
from core.messages import Messages
from core.database import SessionLocal
from schemas.response import APIResponse
from schemas.evaluation import EvaluationResponse, EvaluationResponseWithFindings, FindingResponse


class TestAIEvaluationEngine:
    """Test cases for the AIEvaluationEngine class."""

    @pytest.fixture
    def ai_engine(self):
        """Create an AIEvaluationEngine instance for testing."""
        with patch('services.ai_evaluation_engine.AIClient') as mock_ai_client:
            engine = AIEvaluationEngine(provider=AIProvider.OPENAI)
            engine.git_loader = Mock()
            engine.ai_client = mock_ai_client.return_value
            return engine

    @pytest.fixture
    def mock_rubric_data(self):
        """Create mock rubric data for testing."""
        return {
            'title': 'Test Rubric',
            'criteria': [
                {
                    'id': 1,
                    'title': 'Code Quality',
                    'description': 'Evaluate code quality',
                    'weight': 1.0,
                    'levels': [
                        {'id': 1, 'title': 'Excellent', 'description': 'Perfect code', 'score_points': 4.0},
                        {'id': 2, 'title': 'Good', 'description': 'Good code', 'score_points': 3.0}
                    ]
                }
            ],
            'max_possible_score': 4.0  # Maximum possible score for this rubric
        }

    @pytest.fixture
    def mock_code_chunks(self):
        """Create mock code chunks for testing."""
        # Create proper Document objects that match what GitLoaderService returns
        from langchain_core.documents import Document
        return [
            Document(
                page_content="def test_function(): pass",
                metadata={"file_path": "test.py", "type": "code"}
            )
        ]

    @pytest.fixture
    def mock_briefing_chunks(self):
        """Create mock briefing chunks for testing."""
        # Create proper Document objects that match what BriefingProcessor returns
        from langchain_core.documents import Document
        return [
            Document(
                page_content="Requirement 1: Implement basic functionality",
                metadata={"type": "requirement"}
            )
        ]

    def test_evaluate_repository_success(self, ai_engine, mock_rubric_data, mock_code_chunks, mock_briefing_chunks):
        """Test successful evaluation of a repository."""
        # Mock git loader
        ai_engine.git_loader.fetch_and_process.return_value = mock_code_chunks
        
        # Mock AIClient response
        ai_engine.ai_client.chat.return_value = '''
        {
            "level_id": 1,
            "file_path": "test.py",
            "evidence": "def test_function(): pass",
            "improvement": "Add docstring"
        }
        '''
        
        # Mock ContextEngine to avoid real API calls
        with patch('services.ai_evaluation_engine.ContextEngine') as mock_context_engine:
            mock_context_instance = Mock()
            # Return properly formatted context results that match what ContextEngine.get_relevant_context returns
            mock_context_results = [
                {
                    "page_content": chunk.page_content,
                    "metadata": chunk.metadata
                }
                for chunk in mock_briefing_chunks
            ]
            mock_context_instance.get_relevant_context.return_value = mock_context_results
            mock_context_engine.return_value = mock_context_instance
            
            # Also mock the _evaluate_criterion method to avoid the actual evaluation
            with patch.object(ai_engine, '_evaluate_criterion') as mock_evaluate_criterion:
                mock_evaluate_criterion.return_value = {
                    'criterion_id': 1,
                    'selected_level_id': 1,
                    'file_path': 'test.py',
                    'evidence_snippet': 'def test_function(): pass',
                    'improvement_suggestion': 'Add docstring',
                    'score_points': 4.0
                }
            
            # Mock _load_rubric_data
            with patch.object(ai_engine, '_load_rubric_data', return_value=mock_rubric_data):
                # Execute
                result = ai_engine.evaluate_repository(
                    evaluation_id=1,
                    repo_url="https://github.com/test/repo",
                    rubric_id=1,
                    briefing_chunks=mock_briefing_chunks
                )
            
            # Verify
            assert result['total_score'] == 100.0  # Normalized to 100-point scale
            assert len(result['findings']) == 1
            assert result['findings'][0]['score_points'] == 4.0
            assert result['findings'][0]['file_path'] == 'test.py'

    def test_evaluate_repository_git_loader_failure(self, ai_engine):
        """Test evaluation failure when git loader fails."""
        # Mock git loader failure
        ai_engine.git_loader.fetch_and_process.side_effect = Exception("Git clone failed")
        
        # Execute and verify
        with pytest.raises(RuntimeError, match="Failed to clone repository https://github.com/test/repo: Git clone failed"):
            ai_engine.evaluate_repository(
                evaluation_id=1,
                repo_url="https://github.com/test/repo",
                rubric_id=1,
                briefing_chunks=[]
            )

    def test_evaluate_repository_rubric_loading_failure(self, ai_engine, mock_code_chunks):
        """Test evaluation failure when rubric loading fails."""
        # Mock successful git loading but failed rubric loading
        ai_engine.git_loader.fetch_and_process.return_value = mock_code_chunks
        
        with patch.object(ai_engine, '_load_rubric_data', side_effect=Exception("Rubric not found")):
            with pytest.raises(RuntimeError, match="Failed to load rubric 1: Rubric not found"):
                ai_engine.evaluate_repository(
                    evaluation_id=1,
                    repo_url="https://github.com/test/repo",
                    rubric_id=1,
                    briefing_chunks=[]
                )

    def test_evaluate_repository_ai_client_failure(self, ai_engine, mock_rubric_data, mock_code_chunks):
        """Test evaluation continues when AI Client fails for a criterion."""
        # Mock git loader to return proper code chunks
        ai_engine.git_loader.fetch_and_process.return_value = mock_code_chunks
        
        # Mock AIClient failure
        ai_engine.ai_client.chat.side_effect = Exception("API Error")
        
        # Mock ContextEngine to avoid real API calls
        with patch('services.ai_evaluation_engine.ContextEngine') as mock_context_engine:
            mock_context_instance = Mock()
            mock_context_instance.get_relevant_context.return_value = []
            mock_context_engine.return_value = mock_context_instance
            
            with patch.object(ai_engine, '_load_rubric_data', return_value=mock_rubric_data):
                result = ai_engine.evaluate_repository(
                    evaluation_id=1,
                    repo_url="https://github.com/test/repo",
                    rubric_id=1,
                    briefing_chunks=[]
                )
            
            # Should have a finding with fallback values
            assert len(result['findings']) == 1
            assert result['findings'][0]['score_points'] == 0.0  # Failed evaluations get 0 points
            assert "Evaluation failed" in result['findings'][0]['improvement_suggestion']

    def test_parse_evaluation_response_valid_json(self, ai_engine):
        """Test parsing of valid JSON response from AI."""
        response_text = '''
        {
            "level_id": 2,
            "file_path": "src/main.py",
            "evidence": "def main(): pass",
            "improvement": "Add error handling"
        }
        '''
        
        criterion = {
            'id': 1,
            'title': 'Test Criterion',
            'levels': [
                {'id': 1, 'title': 'Level 1', 'description': 'Desc 1', 'score_points': 1.0},
                {'id': 2, 'title': 'Level 2', 'description': 'Desc 2', 'score_points': 2.0}
            ]
        }
        
        result = ai_engine._parse_evaluation_response(response_text, criterion)
        
        assert result['selected_level_id'] == 2
        assert result['file_path'] == 'src/main.py'
        assert result['evidence_snippet'] == 'def main(): pass'
        assert result['improvement_suggestion'] == 'Add error handling'
        assert result['score_points'] == 2.0

    def test_parse_evaluation_response_invalid_json(self, ai_engine):
        """Test parsing fallback when JSON is invalid."""
        response_text = "This is not JSON"
        
        criterion = {
            'id': 1,
            'title': 'Test Criterion',
            'levels': [
                {'id': 1, 'title': 'Level 1', 'description': 'Desc 1', 'score_points': 1.0}
            ]
        }
        
        result = ai_engine._parse_evaluation_response(response_text, criterion)
        
        assert result['selected_level_id'] == 1  # Default to first level
        assert result['score_points'] == 1.0
        assert "No JSON response found" in result['evidence_snippet']  # Updated to match actual behavior


class TestRunEvaluationTask:
    """Test cases for the run_evaluation_task background function."""

    @patch('services.evaluation_service_api.SessionLocal')
    @patch('services.evaluation_service_api.AIEvaluationEngine')
    @patch('services.ai_evaluation_engine.GitLoaderService')
    def test_run_evaluation_task_success(self, mock_git_loader_service, mock_ai_engine_class, mock_session_local):
        """Test successful completion of background evaluation task."""
        # Mock database session and evaluation
        mock_db = Mock(spec=Session)
        mock_session_local.return_value = mock_db
        
        # Create a mock evaluation object with proper string attributes
        mock_evaluation = Mock(spec=Evaluation)
        mock_evaluation.id = 1
        mock_evaluation.repo_url = "https://github.com/test/repo"  # String value
        mock_evaluation.rubric_id = 1
        mock_evaluation.briefing_snapshot = '[{"page_content": "Test requirement"}]'
        mock_evaluation.ai_provider = "openai"
        mock_evaluation.ai_model = "gpt-4"
        mock_evaluation.ai_api_key = "test_key"
        
        # Configure the mock to track status changes
        mock_evaluation.status = settings.EVALUATION_STATUS_PENDING
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_evaluation
        
        # Mock AI engine and evaluation result
        mock_ai_engine = Mock()
        mock_ai_engine_class.return_value = mock_ai_engine
        
        mock_evaluation_result = {
            'findings': [
                {
                    'criterion_id': 1,
                    'selected_level_id': 1,
                    'file_path': 'test.py',
                    'evidence_snippet': 'test code',
                    'improvement_suggestion': 'test improvement',
                    'score_points': 3.0
                }
            ],
            'total_score': 3.0,
            'ai_summary': 'Test summary'
        }
        mock_ai_engine.evaluate_repository.return_value = mock_evaluation_result
        
        # Mock the _load_rubric_data method to avoid database connection
        with patch.object(mock_ai_engine, '_load_rubric_data') as mock_load_rubric:
            mock_load_rubric.return_value = {
                'title': 'Test Rubric',
                'criteria': [
                    {
                        'id': 1,
                        'title': 'Code Quality',
                        'description': 'Evaluate code quality',
                        'weight': 1.0,
                        'levels': [
                            {'id': 1, 'title': 'Excellent', 'description': 'Perfect code', 'score_points': 4.0},
                            {'id': 2, 'title': 'Good', 'description': 'Good code', 'score_points': 3.0}
                        ]
                    }
                ],
                'max_possible_score': 4.0
            }
        
        # Mock GitLoaderService to avoid actual git operations
        with patch('services.ai_evaluation_engine.GitLoaderService') as mock_git_loader:
            mock_git_loader_instance = Mock()
            mock_git_loader.return_value = mock_git_loader_instance
            mock_git_loader_instance.fetch_and_process.return_value = []
        
        # Mock the SessionLocal import in the run_evaluation_task function
        with patch('services.evaluation_service_api.SessionLocal', return_value=mock_db):
            # Execute
            run_evaluation_task(
                evaluation_id=1, 
                db_url="test_url",
                ai_provider=mock_evaluation.ai_provider,
                ai_model=mock_evaluation.ai_model,
                ai_api_key=mock_evaluation.ai_api_key
            )
        
        # Verify status updates - should be processing initially, then completed
        # Note: The actual implementation updates status to completed at the end
        assert mock_evaluation.status == settings.EVALUATION_STATUS_COMPLETED
        mock_db.commit.assert_called()
        
        # Verify finding creation
        assert mock_db.add.call_count == 1
        created_finding = mock_db.add.call_args[0][0]
        assert isinstance(created_finding, Finding)
        assert created_finding.criterion_id == 1
        assert created_finding.file_path == 'test.py'
        
        # Verify final status update
        assert mock_evaluation.total_score == 3.0
        assert mock_evaluation.ai_summary == 'Test summary'
        assert mock_evaluation.status == settings.EVALUATION_STATUS_COMPLETED

    @patch('services.ai_evaluation_engine.SessionLocal')
    def test_run_evaluation_task_evaluation_not_found(self, mock_session_local):
        """Test background task when evaluation record is not found."""
        mock_db = Mock(spec=Session)
        mock_session_local.return_value = mock_db
        
        # Mock evaluation not found
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Execute
        run_evaluation_task(evaluation_id=999, db_url="test_url")
        
        # Should exit early without errors
        mock_db.commit.assert_not_called()

    @patch('services.evaluation_service_api.SessionLocal')
    def test_run_evaluation_task_json_decode_error(self, mock_session_local):
        """Test background task when briefing snapshot is invalid JSON."""
        mock_db = Mock(spec=Session)
        mock_session_local.return_value = mock_db
        
        mock_evaluation = Mock(spec=Evaluation)
        mock_evaluation.id = 1
        mock_evaluation.briefing_snapshot = 'invalid json'
        mock_evaluation.ai_provider = "openai"
        mock_evaluation.ai_model = "gpt-4"
        mock_evaluation.ai_api_key = "test_key"
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_evaluation
        
        # Execute
        run_evaluation_task(
            evaluation_id=1,
            db_url="test_url",
            ai_provider=mock_evaluation.ai_provider,
            ai_model=mock_evaluation.ai_model,
            ai_api_key=mock_evaluation.ai_api_key,
        )
        
        # Should update status to failed
        assert mock_evaluation.status == settings.EVALUATION_STATUS_FAILED
        assert "Evaluation failed: Invalid briefing data: Expecting value: line 1 column 1 (char 0)" in mock_evaluation.ai_summary

    @patch('services.evaluation_service_api.SessionLocal')
    @patch('services.evaluation_service_api.AIEvaluationEngine')
    def test_run_evaluation_task_ai_evaluation_failure(self, mock_ai_engine_class, mock_session_local):
        """Test background task when AI evaluation fails."""
        mock_db = Mock(spec=Session)
        mock_session_local.return_value = mock_db
        
        mock_evaluation = Mock(spec=Evaluation)
        mock_evaluation.id = 1
        mock_evaluation.repo_url = "https://github.com/test/repo"  # String value to avoid regex issues
        mock_evaluation.briefing_snapshot = '[{"page_content": "Test"}]'
        mock_evaluation.ai_provider = "openai"
        mock_evaluation.ai_model = "gpt-4"
        mock_evaluation.ai_api_key = "test_key"

        mock_db.query.return_value.filter.return_value.first.return_value = mock_evaluation
        
        mock_ai_engine = Mock()
        mock_ai_engine_class.return_value = mock_ai_engine
        mock_ai_engine.evaluate_repository.side_effect = Exception("AI evaluation failed")
        
        # Execute
        run_evaluation_task(
            evaluation_id=1,
            db_url="test_url",
            ai_provider=mock_evaluation.ai_provider,
            ai_model=mock_evaluation.ai_model,
            ai_api_key=mock_evaluation.ai_api_key,
        )
        
        # Should update status to failed
        assert mock_evaluation.status == settings.EVALUATION_STATUS_FAILED
        assert "AI evaluation failed" in mock_evaluation.ai_summary


class TestAIEvaluationEngineResponseFormat:
    """Tests for response format consistency."""

    @pytest.fixture
    def ai_engine(self):
        """Create an AIEvaluationEngine instance for testing."""
        with patch('services.ai_evaluation_engine.AIClient') as mock_ai_client:
            engine = AIEvaluationEngine(provider=AIProvider.OPENAI)
            engine.git_loader = Mock()
            engine.ai_client = mock_ai_client.return_value
            return engine

    @pytest.fixture
    def mock_rubric_data(self):
        """Create mock rubric data for testing."""
        return {
            'title': 'Test Rubric',
            'criteria': [
                {
                    'id': 1,
                    'title': 'Code Quality',
                    'description': 'Evaluate code quality',
                    'weight': 1.0,
                    'levels': [
                        {'id': 1, 'title': 'Excellent', 'description': 'Perfect code', 'score_points': 4.0},
                        {'id': 2, 'title': 'Good', 'description': 'Good code', 'score_points': 3.0}
                    ]
                }
            ]
        }

    @pytest.fixture
    def mock_code_chunks(self):
        """Create mock code chunks for testing."""
        # Create proper Document objects that match what GitLoaderService returns
        from langchain_core.documents import Document
        return [
            Document(
                page_content="def test_function(): pass",
                metadata={"file_path": "test.py", "type": "code"}
            )
        ]

    @pytest.fixture
    def mock_briefing_chunks(self):
        """Create mock briefing chunks for testing."""
        # Create proper Document objects that match what BriefingProcessor returns
        from langchain_core.documents import Document
        return [
            Document(
                page_content="Requirement 1: Implement basic functionality",
                metadata={"type": "requirement"}
            )
        ]

    def test_evaluate_repository_response_format_on_success(self, ai_engine, mock_rubric_data, mock_code_chunks, mock_briefing_chunks):
        """Test that successful evaluation response follows expected format."""
        # Mock git loader
        ai_engine.git_loader.fetch_and_process.return_value = mock_code_chunks
        
        # Mock AIClient response
        ai_engine.ai_client.chat.return_value = '''
        {
            "level_id": 1,
            "file_path": "test.py",
            "evidence": "def test_function(): pass",
            "improvement": "Add docstring"
        }
        '''
        
        # Mock ContextEngine to avoid real API calls
        with patch('services.ai_evaluation_engine.ContextEngine') as mock_context_engine:
            mock_context_instance = Mock()
            mock_context_instance.get_relevant_context.return_value = mock_briefing_chunks
            mock_context_engine.return_value = mock_context_instance
            
            # Mock _load_rubric_data
            with patch.object(ai_engine, '_load_rubric_data', return_value=mock_rubric_data):
                # Execute
                result = ai_engine.evaluate_repository(
                    evaluation_id=1,
                    repo_url="https://github.com/test/repo",
                    rubric_id=1,
                    briefing_chunks=mock_briefing_chunks
                )
            
            # Check response format
            assert isinstance(result, dict)
            assert 'findings' in result
            assert 'total_score' in result
            assert 'ai_summary' in result
            assert isinstance(result['findings'], list)
            assert isinstance(result['total_score'], (int, float))
            assert isinstance(result['ai_summary'], str)

    def test_evaluate_repository_response_format_on_error(self, ai_engine):
        """Test that error response follows expected format."""
        # Mock git loader failure
        ai_engine.git_loader.fetch_and_process.side_effect = Exception("Git clone failed")
        
        # Execute and verify
        with pytest.raises(RuntimeError):
            ai_engine.evaluate_repository(
                evaluation_id=1,
                repo_url="https://github.com/test/repo",
                rubric_id=1,
                briefing_chunks=[]
            )


class TestAIEvaluationEngineErrorHandling:
    """Tests for error handling scenarios."""

    @pytest.fixture
    def ai_engine(self):
        """Create an AIEvaluationEngine instance for testing."""
        with patch('services.ai_evaluation_engine.AIClient') as mock_ai_client:
            engine = AIEvaluationEngine(provider=AIProvider.OPENAI)
            engine.git_loader = Mock()
            engine.ai_client = mock_ai_client.return_value
            return engine

    @pytest.fixture
    def mock_code_chunks(self):
        """Create mock code chunks for testing."""
        # Create proper Document objects that match what GitLoaderService returns
        from langchain_core.documents import Document
        return [
            Document(
                page_content="def test_function(): pass",
                metadata={"file_path": "test.py", "type": "code"}
            )
        ]

    def test_evaluate_repository_database_error(self, ai_engine):
        """Test evaluation handles database errors gracefully."""
        # Mock git loader success but database error in _load_rubric_data
        ai_engine.git_loader.fetch_and_process.return_value = [Mock()]
        
        with patch.object(ai_engine, '_load_rubric_data', side_effect=Exception("Database connection error")):
            with pytest.raises(RuntimeError, match="Failed to load rubric 1: Database connection error"):
                ai_engine.evaluate_repository(
                    evaluation_id=1,
                    repo_url="https://github.com/test/repo",
                    rubric_id=1,
                    briefing_chunks=[]
                )

    def test_evaluate_repository_multiple_criteria_failure(self, ai_engine, mock_code_chunks):
        """Test evaluation handles multiple criteria failures gracefully."""
        # Mock git loader to return proper code chunks
        ai_engine.git_loader.fetch_and_process.return_value = mock_code_chunks
        
        # Mock rubric with multiple criteria
        mock_rubric_data = {
            'title': 'Test Rubric',
            'criteria': [
                {
                    'id': 1,
                    'title': 'Code Quality',
                    'description': 'Evaluate code quality',
                    'weight': 1.0,
                    'levels': [
                        {'id': 1, 'title': 'Excellent', 'description': 'Perfect code', 'score_points': 4.0},
                        {'id': 2, 'title': 'Good', 'description': 'Good code', 'score_points': 3.0}
                    ]
                },
                {
                    'id': 2,
                    'title': 'Documentation',
                    'description': 'Evaluate documentation',
                    'weight': 0.5,
                    'levels': [
                        {'id': 1, 'title': 'Excellent', 'description': 'Perfect docs', 'score_points': 4.0},
                        {'id': 2, 'title': 'Good', 'description': 'Good docs', 'score_points': 3.0}
                    ]
                }
            ]
        }
        
        # Mock AIClient failure for all criteria
        ai_engine.ai_client.chat.side_effect = Exception("API Error")
        
        # Mock ContextEngine to avoid real API calls
        with patch('services.ai_evaluation_engine.ContextEngine') as mock_context_engine:
            mock_context_instance = Mock()
            mock_context_instance.get_relevant_context.return_value = []
            mock_context_engine.return_value = mock_context_instance
            
            with patch.object(ai_engine, '_load_rubric_data', return_value=mock_rubric_data):
                result = ai_engine.evaluate_repository(
                    evaluation_id=1,
                    repo_url="https://github.com/test/repo",
                    rubric_id=1,
                    briefing_chunks=[]
                )
            
            # Should have findings for both criteria with fallback values
            assert len(result['findings']) == 2
            for finding in result['findings']:
                assert finding['score_points'] == 0.0
                assert "Evaluation failed" in finding['improvement_suggestion']


class TestAIEvaluationEngineIntegration:
    """Integration tests for AIEvaluationEngine."""

    @pytest.mark.parametrize("provider", [AIProvider.OPENAI, AIProvider.GEMINI, AIProvider.GROQ])
    @patch('services.ai_evaluation_engine.AIClient')
    def test_ai_engine_initialization_with_providers(self, mock_ai_client, provider):
        """Test that AIEvaluationEngine initializes the correct AIClient."""
        from core.settings import get_model, get_api_key
        AIEvaluationEngine(provider=provider)
        mock_ai_client.assert_called_with(
            provider=provider,
            model=get_model(provider),
            api_key=get_api_key(provider)
        )


class TestSettingsIntegration:
    """Test cases for settings integration with AI providers."""

    @patch('services.ai_client.OpenAI')
    @patch('services.ai_client.get_api_key')
    def test_ai_client_uses_explicit_api_key_over_settings(self, mock_get_api_key, mock_openai):
        """Test that AIClient uses explicit API key when provided, ignoring settings."""
        mock_get_api_key.return_value = "settings_key"
        
        from services.ai_client import AIClient, AIProvider
        
        # Create AIClient with explicit API key
        client = AIClient(provider=AIProvider.OPENAI, api_key="explicit_key")
        
        # Verify that get_api_key was not called
        mock_get_api_key.assert_not_called()

    @patch('services.ai_client.OpenAI')
    @patch('services.ai_evaluation_engine.get_api_key')
    def test_ai_evaluation_engine_uses_explicit_api_key_over_settings(self, mock_get_api_key, mock_openai):
        """Test that AIEvaluationEngine uses explicit API key when provided, ignoring settings."""
        mock_get_api_key.return_value = "settings_key"
        
        # Create AIEvaluationEngine with explicit API key
        engine = AIEvaluationEngine(provider=AIProvider.OPENAI, api_key="explicit_key")
        
        # Verify that get_api_key was not called
        mock_get_api_key.assert_not_called()
