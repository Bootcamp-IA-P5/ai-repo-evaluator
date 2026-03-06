"""
Test cases for the AI Evaluation Engine service.

This module tests the complete async evaluation workflow including:
- Repository cloning and processing
- RAG-augmented criterion evaluation
- Finding creation and score calculation
- Error handling and status management
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from services.ai_evaluation_engine import AIEvaluationEngine, run_evaluation_task
from services.ai_client import AIProvider
from models import Evaluation, Rubric, Criterion, Level, Finding
from core.settings import settings
from unittest.mock import patch


class TestAIEvaluationEngine:
    """Test cases for the AIEvaluationEngine class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Patch the AIClient to prevent it from being initialized
        with patch('services.ai_evaluation_engine.AIClient') as mock_ai_client:
            self.ai_engine = AIEvaluationEngine(provider=AIProvider.OPENAI)
            self.ai_engine.git_loader = Mock()
            self.ai_engine.ai_client = mock_ai_client.return_value

    def test_evaluate_repository_success(self):
        """Test successful evaluation of a repository."""
        # Mock data
        evaluation_id = 1
        repo_url = "https://github.com/test/repo"
        rubric_id = 1
        
        # Mock code chunks from git loader
        mock_code_chunks = [
            Mock(page_content="def test_function(): pass", metadata={"file_path": "test.py"})
        ]
        self.ai_engine.git_loader.fetch_and_process.return_value = mock_code_chunks
        
        # Mock briefing chunks
        briefing_chunks = [
            {"page_content": "Requirement 1: Implement basic functionality"}
        ]
        
        # Mock rubric data
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
                }
            ]
        }
        
        # Mock AIClient response
        self.ai_engine.ai_client.chat.return_value = '''
        {
            "level_id": 1,
            "file_path": "test.py",
            "evidence": "def test_function(): pass",
            "improvement": "Add docstring"
        }
        '''
        
        # Mock _load_rubric_data
        with patch.object(self.ai_engine, '_load_rubric_data', return_value=mock_rubric_data):
            # Execute
            result = self.ai_engine.evaluate_repository(
                evaluation_id=evaluation_id,
                repo_url=repo_url,
                rubric_id=rubric_id,
                briefing_chunks=briefing_chunks
            )
            
            # Verify
            assert result['total_score'] == 4.0
            assert len(result['findings']) == 1
            assert result['findings'][0]['score_points'] == 4.0
            assert result['findings'][0]['file_path'] == 'test.py'

    def test_evaluate_repository_git_loader_failure(self):
        """Test evaluation failure when git loader fails."""
        # Mock git loader failure
        self.ai_engine.git_loader.fetch_and_process.side_effect = Exception("Git clone failed")
        
        # Execute and verify
        with pytest.raises(RuntimeError, match="Repository cloning failed"):
            self.ai_engine.evaluate_repository(
                evaluation_id=1,
                repo_url="https://github.com/test/repo",
                rubric_id=1,
                briefing_chunks=[]
            )

    def test_evaluate_repository_rubric_loading_failure(self):
        """Test evaluation failure when rubric loading fails."""
        # Mock successful git loading but failed rubric loading
        self.ai_engine.git_loader.fetch_and_process.return_value = []
        
        with patch.object(self.ai_engine, '_load_rubric_data', side_effect=Exception("Rubric not found")):
            with pytest.raises(RuntimeError, match="Rubric loading failed"):
                self.ai_engine.evaluate_repository(
                    evaluation_id=1,
                    repo_url="https://github.com/test/repo",
                    rubric_id=1,
                    briefing_chunks=[]
                )

    def test_evaluate_repository_ai_client_failure(self):
        """Test evaluation continues when AI Client fails for a criterion."""
        # Mock data
        mock_code_chunks = [Mock(page_content="test", metadata={"file_path": "test.py"})]
        self.ai_engine.git_loader.fetch_and_process.return_value = mock_code_chunks
        
        mock_rubric_data = {
            'title': 'Test Rubric',
            'criteria': [
                {
                    'id': 1,
                    'title': 'Code Quality',
                    'description': 'Evaluate code quality',
                    'weight': 1.0,
                    'levels': [
                        {'id': 1, 'title': 'Excellent', 'description': 'Perfect code', 'score_points': 4.0}
                    ]
                }
            ]
        }
        
        # Mock AIClient failure
        self.ai_engine.ai_client.chat.side_effect = Exception("API Error")
        
        with patch.object(self.ai_engine, '_load_rubric_data', return_value=mock_rubric_data):
            result = self.ai_engine.evaluate_repository(
                evaluation_id=1,
                repo_url="https://github.com/test/repo",
                rubric_id=1,
                briefing_chunks=[]
            )
            
            # Should have a finding with fallback values
            assert len(result['findings']) == 1
            assert result['findings'][0]['score_points'] == 0.0  # Failed evaluations get 0 points
            assert "Evaluation failed" in result['findings'][0]['improvement_suggestion']

    def test_parse_evaluation_response_valid_json(self):
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
        
        result = self.ai_engine._parse_evaluation_response(response_text, criterion)
        
        assert result['selected_level_id'] == 2
        assert result['file_path'] == 'src/main.py'
        assert result['evidence_snippet'] == 'def main(): pass'
        assert result['improvement_suggestion'] == 'Add error handling'
        assert result['score_points'] == 2.0

    def test_parse_evaluation_response_invalid_json(self):
        """Test parsing fallback when JSON is invalid."""
        response_text = "This is not JSON"
        
        criterion = {
            'id': 1,
            'title': 'Test Criterion',
            'levels': [
                {'id': 1, 'title': 'Level 1', 'description': 'Desc 1', 'score_points': 1.0}
            ]
        }
        
        result = self.ai_engine._parse_evaluation_response(response_text, criterion)
        
        assert result['selected_level_id'] == 1  # Default to first level
        assert result['score_points'] == 1.0
        assert "No JSON response found" in result['evidence_snippet']  # Updated to match actual behavior


class TestRunEvaluationTask:
    """Test cases for the run_evaluation_task background function."""

    @patch('services.ai_evaluation_engine.SessionLocal')
    @patch('services.ai_evaluation_engine.AIEvaluationEngine')
    def test_run_evaluation_task_success(self, mock_ai_engine_class, mock_session_local):
        """Test successful completion of background evaluation task."""
        # Mock database session and evaluation
        mock_db = Mock(spec=Session)
        mock_session_local.return_value = mock_db
        
        mock_evaluation = Mock(spec=Evaluation)
        mock_evaluation.id = 1
        mock_evaluation.repo_url = "https://github.com/test/repo"
        mock_evaluation.rubric_id = 1
        mock_evaluation.briefing_snapshot = '[{"page_content": "Test requirement"}]'
        mock_evaluation.ai_provider = "openai"
        mock_evaluation.ai_model = "gpt-4"
        mock_evaluation.ai_api_key = "test_key"

        
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
        
        # Execute
        run_evaluation_task(evaluation_id=1, db_url="test_url")
        
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

    @patch('services.ai_evaluation_engine.SessionLocal')
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
        run_evaluation_task(evaluation_id=1, db_url="test_url")
        
        # Should update status to failed
        assert mock_evaluation.status == settings.EVALUATION_STATUS_FAILED
        assert "Invalid briefing data" in mock_evaluation.ai_summary

    @pytest.mark.parametrize("provider", [AIProvider.OPENAI, AIProvider.GEMINI, AIProvider.GROK])
    @patch('services.ai_evaluation_engine.AIClient')
    def test_ai_engine_initialization_with_providers(self, mock_ai_client, provider):
        """Test that AIEvaluationEngine initializes the correct AIClient."""
        AIEvaluationEngine(provider=provider)
        mock_ai_client.assert_called_with(provider=provider, model=None, api_key=None)

    @patch('services.ai_evaluation_engine.SessionLocal')
    @patch('services.ai_evaluation_engine.AIEvaluationEngine')
    def test_run_evaluation_task_ai_evaluation_failure(self, mock_ai_engine_class, mock_session_local):
        """Test background task when AI evaluation fails."""
        mock_db = Mock(spec=Session)
        mock_session_local.return_value = mock_db
        
        mock_evaluation = Mock(spec=Evaluation)
        mock_evaluation.id = 1
        mock_evaluation.briefing_snapshot = '[{"page_content": "Test"}]'
        mock_evaluation.ai_provider = "openai"
        mock_evaluation.ai_model = "gpt-4"
        mock_evaluation.ai_api_key = "test_key"

        mock_db.query.return_value.filter.return_value.first.return_value = mock_evaluation
        
        mock_ai_engine = Mock()
        mock_ai_engine_class.return_value = mock_ai_engine
        mock_ai_engine.evaluate_repository.side_effect = Exception("AI evaluation failed")
        
        # Execute
        run_evaluation_task(evaluation_id=1, db_url="test_url")
        
        # Should update status to failed
        assert mock_evaluation.status == settings.EVALUATION_STATUS_FAILED
        assert "AI evaluation failed" in mock_evaluation.ai_summary


class TestSettingsIntegration:
    """Test cases for settings integration with AI providers."""

    @patch('core.settings.get_api_key')
    def test_ai_client_uses_settings_api_key(self, mock_get_api_key):
        """Test that AIClient uses settings for API key when none provided."""
        mock_get_api_key.return_value = "settings_key"
        
        # Import here to avoid circular import issues in tests
        from services.ai_client import AIClient, AIProvider
        
        # Create AIClient without explicit API key
        client = AIClient(provider=AIProvider.OPENAI)
        
        # Verify that get_api_key was called
        mock_get_api_key.assert_called_once_with(AIProvider.OPENAI)

    @patch('core.settings.get_api_key')
    def test_ai_client_uses_explicit_api_key_over_settings(self, mock_get_api_key):
        """Test that AIClient uses explicit API key when provided, ignoring settings."""
        mock_get_api_key.return_value = "settings_key"
        
        from services.ai_client import AIClient, AIProvider
        
        # Create AIClient with explicit API key
        client = AIClient(provider=AIProvider.OPENAI, api_key="explicit_key")
        
        # Verify that get_api_key was not called
        mock_get_api_key.assert_not_called()

    @patch('core.settings.get_api_key')
    def test_ai_evaluation_engine_uses_settings_when_no_api_key(self, mock_get_api_key):
        """Test that AIEvaluationEngine uses settings for API key when none provided."""
        mock_get_api_key.return_value = "settings_key"
        
        # Create AIEvaluationEngine without explicit API key
        engine = AIEvaluationEngine(provider=AIProvider.OPENAI)
        
        # Verify that get_api_key was called
        mock_get_api_key.assert_called_once_with(AIProvider.OPENAI)

    @patch('core.settings.get_api_key')
    def test_ai_evaluation_engine_uses_explicit_api_key_over_settings(self, mock_get_api_key):
        """Test that AIEvaluationEngine uses explicit API key when provided, ignoring settings."""
        mock_get_api_key.return_value = "settings_key"
        
        # Create AIEvaluationEngine with explicit API key
        engine = AIEvaluationEngine(provider=AIProvider.OPENAI, api_key="explicit_key")
        
        # Verify that get_api_key was not called
        mock_get_api_key.assert_not_called()
