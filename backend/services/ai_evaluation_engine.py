"""
AI Evaluation Engine - Core service for running repository evaluations.

This module orchestrates the complete AI evaluation workflow:
1. Repository cloning and code analysis
2. RAG-augmented criterion evaluation
3. Finding creation with WHIS data
4. Score calculation and aggregation
5. AI summary generation
"""

import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

from core.logging_config import logger
from core.settings import settings, get_api_key, get_model
from core.database import SessionLocal
from core.messages import Messages
from models import Evaluation, Rubric, Criterion, Level, Finding
from services.git_loader import GitLoaderService
from services.ai_client import AIClient, AIProvider
import os


class AIEvaluationEngine:
    """
    Core AI evaluation engine that orchestrates the complete evaluation workflow.
    
    This service handles:
    - Repository cloning and code analysis
    - RAG-augmented criterion evaluation using different AI providers
    - Finding creation with WHIS data (Where, How, Improvement, Score)
    - Weighted score calculation
    - AI summary generation
    """

    def __init__(self, provider: AIProvider = AIProvider.GEMINI, model: Optional[str] = None, api_key: Optional[str] = None):
        """Initialize the AI evaluation engine with required services."""
        self.git_loader = GitLoaderService()
        # If no API key provided, use settings
        if api_key is None:
            api_key = get_api_key(provider)
            model = get_model(provider)
        logger.debug(f"Provider: {provider}, Model: {model}, API Key: {api_key[:5]}")
        self.ai_client = AIClient(provider=provider, model=model, api_key=api_key)

    def evaluate_repository(
        self, 
        evaluation_id: int, 
        repo_url: str, 
        rubric_id: int, 
        briefing_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Execute the complete AI evaluation workflow.
        
        Args:
            evaluation_id: ID of the evaluation record
            repo_url: URL of the repository to evaluate
            rubric_id: ID of the rubric to use for evaluation
            briefing_chunks: List of briefing document chunks for RAG context
            
        Returns:
            Dictionary containing evaluation results with findings, total score, and AI summary
        """
        logger.info(f"Starting AI evaluation for evaluation {evaluation_id}")
        
        # 1. Clone repository and process code
        try:
            logger.debug(f"Cloning repository: {repo_url}")
            code_chunks = self.git_loader.fetch_and_process(repo_url)
            logger.info(f"Repository cloned successfully: {len(code_chunks)} code chunks generated")
        except Exception as e:
            logger.error(f"Failed to clone repository {repo_url}: {e}")
            raise RuntimeError(Messages.AIRepository.CLONING_FAILED.format(
                repo_url=repo_url, 
                error=str(e)
            ))

        # 2. Load rubric criteria and levels
        try:
            rubric_data = self._load_rubric_data(rubric_id)
            logger.info(f"Loaded rubric {rubric_id} with {len(rubric_data['criteria'])} criteria")
        except Exception as e:
            logger.error(f"Failed to load rubric {rubric_id}: {e}")
            raise RuntimeError(Messages.AIRubric.LOADING_FAILED.format(
                rubric_id=rubric_id, 
                error=str(e)
            ))

        # 3. Evaluate each criterion
        findings = []
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for criterion in rubric_data['criteria']:
            try:
                logger.debug(f"Evaluating criterion: {criterion['title']}")
                
                # Evaluate this criterion
                finding_result = self._evaluate_criterion(
                    criterion=criterion,
                    code_chunks=code_chunks,
                    briefing_chunks=briefing_chunks
                )
                
                if finding_result:
                    findings.append(finding_result)
                    total_weighted_score += finding_result['score_points'] * criterion['weight']
                    total_weight += criterion['weight']
                    logger.debug(f"Criterion '{criterion['title']}' evaluated: {finding_result['score_points']} points")
                else:
                    # Create a failed finding record when _evaluate_criterion returns None
                    findings.append({
                        'criterion_id': criterion['id'],
                        'selected_level_id': None,
                        'file_path': None,
                        'evidence_snippet': None,
                        'improvement_suggestion': "Evaluation failed: No result returned",
                        'score_points': 0.0
                    })
                
            except Exception as e:
                logger.error(f"Failed to evaluate criterion '{criterion['title']}': {e}")
                # Create a failed finding record
                findings.append({
                    'criterion_id': criterion['id'],
                    'selected_level_id': None,
                    'file_path': None,
                    'evidence_snippet': None,
                    'improvement_suggestion': Messages.AIEvaluation.CRITERION_EVALUATION_FAILED.format(
                        criterion_title=criterion['title'], 
                        error=str(e)
                    ),
                    'score_points': 0.0
                })

        # 4. Calculate total score
        if total_weight > 0:
            total_score = total_weighted_score
        else:
            total_score = 0.0
            
        logger.info(f"Evaluation completed. Total score: {total_score:.2f}")

        # 5. Generate AI summary
        try:
            ai_summary = self._generate_ai_summary(
                repo_url=repo_url,
                rubric_title=rubric_data['title'],
                findings=findings,
                total_score=total_score
            )
            logger.info("AI summary generated successfully")
        except Exception as e:
            logger.error(f"Failed to generate AI summary: {e}")
            ai_summary = Messages.AIEvaluation.AI_SUMMARY_GENERATION_FAILED.format(error=str(e))

        return {
            'findings': findings,
            'total_score': total_score,
            'ai_summary': ai_summary
        }

    def _load_rubric_data(self, rubric_id: int) -> Dict[str, Any]:
        """
        Load rubric data including criteria and levels from database.
        
        Args:
            rubric_id: ID of the rubric to load
            
        Returns:
            Dictionary containing rubric title and list of criteria with levels
        """
        db = SessionLocal()
        try:
            # Load rubric
            rubric = db.query(Rubric).filter(Rubric.id == rubric_id).first()
            if not rubric:
                raise ValueError(Messages.AIRubric.NOT_FOUND.format(rubric_id=rubric_id))

            # Load criteria with levels
            criteria = db.query(Criterion).filter(Criterion.rubric_id == rubric_id).all()
            
            criteria_data = []
            for criterion in criteria:
                levels = db.query(Level).filter(Level.criterion_id == criterion.id).all()
                
                criteria_data.append({
                    'id': criterion.id,
                    'title': criterion.title,
                    'description': criterion.description,
                    'weight': criterion.weight,
                    'levels': [
                        {
                            'id': level.id,
                            'title': level.level_title,
                            'description': level.level_description,
                            'score_points': level.score_points
                        }
                        for level in levels
                    ]
                })

            return {
                'id': rubric.id,
                'title': rubric.title,
                'description': rubric.description,
                'criteria': criteria_data
            }

        finally:
            db.close()

    def _evaluate_criterion(
        self, 
        criterion: Dict[str, Any], 
        code_chunks: List[Any], 
        briefing_chunks: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Evaluate a single criterion using RAG-augmented AI analysis.
        
        Args:
            criterion: Dictionary containing criterion data and levels
            code_chunks: List of code documents from repository
            briefing_chunks: List of briefing document chunks
            
        Returns:
            Dictionary containing finding data or None if evaluation failed
        """
        # Prepare RAG context
        context = self._prepare_rag_context(criterion, code_chunks, briefing_chunks)
        
        # Prepare prompt for AI
        prompt = self._build_evaluation_prompt(criterion, context)
        
        try:
            # Call AI provider API
            response_text = self.ai_client.chat(prompt)
            
            # Parse response
            evaluation_result = self._parse_evaluation_response(
                response_text,
                criterion
            )
            
            return evaluation_result
            
        except Exception as e:
            logger.error(f"AI API call failed for criterion '{criterion['title']}': {e}")
            return None

    def _prepare_rag_context(
        self, 
        criterion: Dict[str, Any], 
        code_chunks: List[Any], 
        briefing_chunks: List[Dict[str, Any]]
    ) -> str:
        """
        Prepare RAG context by finding relevant code and briefing chunks.
        
        Args:
            criterion: The criterion being evaluated
            code_chunks: All code chunks from repository
            briefing_chunks: All briefing chunks (can be dicts or Document objects)
            
        Returns:
            String containing relevant context for the evaluation
        """
        # For now, we'll use a simple approach - in a full implementation,
        # this would use vector similarity search to find the most relevant chunks
        
        # Get relevant briefing context (all chunks for now)
        # Handle both dict format (from JSON) and Document format
        briefing_context_parts = []
        for i, chunk in enumerate(briefing_chunks):
            if isinstance(chunk, dict):
                # Handle dict format (from JSON deserialization)
                content = chunk.get('page_content', '')
            else:
                # Handle Document object format
                content = getattr(chunk, 'page_content', '')
            briefing_context_parts.append(f"Requirement {i+1}: {content}")
        
        briefing_context = "\n\n".join(briefing_context_parts)
        
        # Get relevant code context (sample of code chunks)
        code_context = "\n\n".join([
            f"Code file {i+1} ({chunk.metadata.get('file_path', 'unknown')}): {chunk.page_content[:500]}..."
            for i, chunk in enumerate(code_chunks[:5])  # Limit to first 5 chunks
        ])
        
        return f"""
        CRITERION: {criterion['title']}
        DESCRIPTION: {criterion['description']}
        
        RELEVANT REQUIREMENTS:
        {briefing_context}
        
        RELEVANT CODE SAMPLES:
        {code_context}
        """

    def _build_evaluation_prompt(self, criterion: Dict[str, Any], context: str) -> str:
        """
        Build the evaluation prompt for AI API.
        
        Args:
            criterion: The criterion being evaluated
            context: RAG context containing relevant code and requirements
            
        Returns:
            String containing the evaluation prompt
        """
        levels_text = "\n".join([
            f"{level['id']}. {level['title']} ({level['score_points']} points): {level['description']}"
            for level in criterion['levels']
        ])
        
        return f"""
        Evaluate the code repository against the following criterion:

        CRITERION: {criterion['title']}
        DESCRIPTION: {criterion['description']}
        WEIGHT: {criterion['weight']}

        SCORING LEVELS:
        {levels_text}

        CONTEXT:
        {context}

        INSTRUCTIONS:
        1. Analyze the code against the criterion requirements
        2. Select the most appropriate scoring level (1-{len(criterion['levels'])})
        3. Provide specific evidence from the code
        4. Suggest concrete improvements

        FORMAT YOUR RESPONSE AS JSON:
        {{
            "level_id": <selected_level_id>,
            "file_path": "<relevant_file_path>",
            "evidence": "<specific_code_evidence>",
            "improvement": "<concrete_improvement_suggestion>"
        }}

        If the code doesn't contain relevant information, select the lowest level and explain why.
        """

    def _parse_evaluation_response(self, response_text: str, criterion: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse the AI response and extract evaluation data.
        
        Args:
            response_text: Raw response from AI API
            criterion: The criterion being evaluated
            
        Returns:
            Dictionary containing parsed evaluation result
        """
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_data = json.loads(json_match.group())
            else:
                # Fallback if no JSON found
                response_data = {"level_id": criterion['levels'][0]['id'], "evidence": "No JSON response found", "improvement": "Unable to parse response"}
            
            # Find the selected level
            selected_level = None
            for level in criterion['levels']:
                if level['id'] == response_data.get('level_id'):
                    selected_level = level
                    break
            
            if not selected_level:
                selected_level = criterion['levels'][0]  # Default to lowest level
            
            return {
                'criterion_id': criterion['id'],
                'selected_level_id': selected_level['id'],
                'file_path': response_data.get('file_path'),
                'evidence_snippet': response_data.get('evidence'),
                'improvement_suggestion': response_data.get('improvement'),
                'score_points': selected_level['score_points']
            }
            
        except Exception as e:
            logger.error(f"Failed to parse evaluation response: {e}")
            # Return fallback result
            return {
                'criterion_id': criterion['id'],
                'selected_level_id': criterion['levels'][0]['id'],
                'file_path': None,
                'evidence_snippet': f"Parse error: {str(e)}",
                'improvement_suggestion': "Unable to parse AI response",
                'score_points': criterion['levels'][0]['score_points']
            }

    def _generate_ai_summary(
        self, 
        repo_url: str, 
        rubric_title: str, 
        findings: List[Dict[str, Any]], 
        total_score: float
    ) -> str:
        """
        Generate a comprehensive AI summary of the evaluation.
        
        Args:
            repo_url: URL of the evaluated repository
            rubric_title: Title of the rubric used
            findings: List of all criterion findings
            total_score: Overall evaluation score
            
        Returns:
            String containing the AI-generated summary
        """
        # Prepare findings summary
        findings_summary = []
        for finding in findings:
            level_info = f"Score: {finding.get('score_points', 0)} points"
            evidence = finding.get('evidence_snippet', 'No evidence provided')
            improvement = finding.get('improvement_suggestion', 'No improvement suggested')
            
            findings_summary.append(f"""
            - {finding.get('criterion_id', 'Unknown criterion')}: {level_info}
              Evidence: {evidence[:200]}...
              Improvement: {improvement[:200]}...
            """)
        
        prompt = f"""
        Generate a comprehensive evaluation summary for a student project.

        REPOSITORY: {repo_url}
        RUBRIC: {rubric_title}
        OVERALL SCORE: {total_score:.2f}/10

        DETAILED FINDINGS:
        {chr(10).join(findings_summary)}

        INSTRUCTIONS:
        1. Provide an overall assessment of the project quality
        2. Highlight the strongest aspects of the implementation
        3. Identify the most critical areas for improvement
        4. Provide actionable recommendations for the student
        5. Keep the tone constructive and educational

        FORMAT: Write a 3-4 paragraph summary suitable for student feedback.
        """

        try:
            response_text = self.ai_client.chat(prompt)
            return response_text
            
        except Exception as e:
            logger.error(f"Failed to generate AI summary: {e}")
            return f"Summary generation failed: {str(e)}"


def run_evaluation_task(
    evaluation_id: int, 
    db_url: str,
    ai_provider: str = None,
    ai_model: str = None,
    ai_api_key: str = None
):
    """
    Background task for running the AI evaluation process.

    This task is triggered after the evaluation record is created and
    performs the long-running AI analysis. It manages the evaluation
    lifecycle: pending → processing → completed/failed.

    Args:
        evaluation_id: The ID of the evaluation to process
        db_url: Database URL for creating a new session
        ai_provider: AI provider to use (openai, gemini, grok) - optional
        ai_model: Specific model for the provider - optional
        ai_api_key: API key for the provider - optional
    """
    # Create a new database session for the background task
    db = SessionLocal()

    try:
        logger.debug(f"Starting background evaluation task for evaluation {evaluation_id}")

        # 1. Update status to 'processing'
        evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
        if evaluation is None:
            logger.error(f"Evaluation {evaluation_id} not found in background task")
            return

        evaluation.status = settings.EVALUATION_STATUS_PROCESSING
        db.commit()
        logger.debug(f"Evaluation {evaluation_id} status updated to '{settings.EVALUATION_STATUS_PROCESSING}'")

        # 2. Initialize AI evaluation engine
        # Use provided AI configuration or default to settings
        if ai_provider and ai_model and ai_api_key:
            ai_engine = AIEvaluationEngine(
                provider=AIProvider(ai_provider),
                model=ai_model,
                api_key=ai_api_key
            )
        else:
            # Use default configuration from settings
            ai_engine = AIEvaluationEngine()

        # 3. Parse briefing chunks from snapshot
        try:
            briefing_chunks = json.loads(evaluation.briefing_snapshot)
            logger.debug(f"Parsed {len(briefing_chunks)} briefing chunks")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse briefing snapshot for evaluation {evaluation_id}: {e}")
            raise RuntimeError(Messages.AIEvaluation.PARSING_RESPONSE_FAILED.format(
                error=str(e)
            ))

        # 4. Run AI evaluation
        try:
            evaluation_result = ai_engine.evaluate_repository(
                evaluation_id=evaluation_id,
                repo_url=evaluation.repo_url,
                rubric_id=evaluation.rubric_id,
                briefing_chunks=briefing_chunks
            )
            
            logger.info(f"AI evaluation completed for evaluation {evaluation_id}")
            
        except Exception as e:
            logger.error(f"AI evaluation failed for evaluation {evaluation_id}: {e}")
            # Re-raise to trigger error handling below
            raise

        # 5. Create finding records
        for finding_data in evaluation_result['findings']:
            finding = Finding(
                evaluation_id=evaluation_id,
                criterion_id=finding_data['criterion_id'],
                selected_level_id=finding_data['selected_level_id'],
                file_path=finding_data.get('file_path'),
                evidence_snippet=finding_data.get('evidence_snippet'),
                improvement_suggestion=finding_data.get('improvement_suggestion')
            )
            db.add(finding)

        # 6. Update evaluation with results
        evaluation.total_score = evaluation_result['total_score']
        evaluation.ai_summary = evaluation_result['ai_summary']
        evaluation.status = settings.EVALUATION_STATUS_COMPLETED
        
        db.commit()

        logger.info(f"Evaluation {evaluation_id} completed successfully with score {evaluation_result['total_score']:.2f}")

    except Exception as e:
        # 7. On failure, update status to 'failed'
        logger.error(f"Evaluation {evaluation_id} failed: {e}")

        try:
            evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
            if evaluation:
                evaluation.status = settings.EVALUATION_STATUS_FAILED
                evaluation.ai_summary = f"Evaluation failed: {str(e)}"
                db.commit()
        except Exception as commit_error:
            logger.error(f"Failed to update evaluation status to '{settings.EVALUATION_STATUS_FAILED}': {commit_error}")

    finally:
        db.close()
