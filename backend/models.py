"""
SQLAlchemy ORM Models for AI Repository Evaluator.

This module defines the database schema for the AI-powered repository
evaluation system. The architecture is organized into two logical domains:

RUBRIC ARCHITECTURE (The "Rules"):
    - Rubric: Root container for grading checklists
    - Criterion: Individual evaluation dimensions
    - Level: Scoring options within each criterion

EVALUATION ENGINE (The "History & Results"):
    - Evaluation: Record of a repository analysis run
    - Finding: Specific evidence and scores for each criterion

Entity Relationship Diagram:
    Rubric (1) ─────< Criterion (N) ─────< Level (N)
        │
        └──────────< Evaluation (N) ─────< Finding (N)
                                                │
                                Criterion <─────┘
                                    Level <─────┘

Database: PostgreSQL or SQLite (via SQLAlchemy)
"""

import datetime
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


# =============================================================================
# RUBRIC ARCHITECTURE (The "Rules")
# =============================================================================

class Rubric(Base):
    """
    The root container for a grading checklist.
    
    Represents a complete evaluation rubric (e.g., 'Backend Final Project', 
    'Frontend Assessment'). A rubric contains multiple criteria that define
    the evaluation dimensions.
    
    Attributes:
        id: Unique identifier, auto-incremented primary key with index
        title: Human-readable name of the rubric (required, max 255 chars)
        description: Detailed explanation of the rubric's purpose
        created_at: Timestamp of rubric creation (auto-set to UTC now)
    
    Relationships:
        criteria: One-to-many → Criterion (cascade deleted with rubric)
        evaluations: One-to-many → Evaluation (independent lifetime)
    
    Example:
        rubric = Rubric(
            title="Python Backend Project", 
            description="Evaluates backend architecture and code quality"
        )
    """
    __tablename__ = "rubrics"

    # Primary key - auto-incremented unique identifier
    id = Column(Integer, primary_key=True, index=True)
    
    # Required: Human-readable name for the rubric (e.g., "Final Project Rubric")
    title = Column(String(255), nullable=False)
    
    # Optional: Detailed description of what this rubric evaluates
    description = Column(Text)
    
    # Auto-set timestamp when rubric is created (UTC timezone)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    # One-to-many: A rubric has multiple criteria; cascade delete ensures
    # criteria are removed when parent rubric is deleted
    criteria = relationship("Criterion", back_populates="rubric", cascade="all, delete-orphan")
    
    # One-to-many: A rubric can be used in multiple evaluations; no cascade
    # so evaluation history is preserved even if rubric is modified
    evaluations = relationship("Evaluation", back_populates="rubric")


class Criterion(Base):
    """
    A row in the rubric representing a single evaluation dimension.
    
    Each criterion defines a specific aspect to evaluate (e.g., 'Error Handling',
    'Database Schema', 'Code Style'). Criteria belong to a rubric and have
    multiple scoring levels associated with them.
    
    Attributes:
        id: Unique identifier, auto-incremented primary key with index
        rubric_id: Foreign key to parent Rubric (cascade deleted)
        title: Human-readable name of the criterion (required, max 255 chars)
        description: Detailed explanation of what this criterion evaluates
        weight: Relative weight for score calculation (default: 1.0)
    
    Relationships:
        rubric: Many-to-one → Rubric (parent rubric)
        levels: One-to-many → Level (cascade deleted with criterion)
    
    Note:
        Weight determines how much this criterion contributes to the total
        score. Higher weights = more impact on final evaluation score.
        Example: weight=2.0 means this criterion counts double.
    """
    __tablename__ = "criteria"

    # Primary key - auto-incremented unique identifier
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to parent Rubric; CASCADE delete ensures criterion is
    # removed when parent rubric is deleted
    rubric_id = Column(Integer, ForeignKey("rubrics.id", ondelete="CASCADE"))
    
    # Required: Human-readable name (e.g., "Error Handling", "Database Design")
    title = Column(String(255), nullable=False)
    
    # Optional: Detailed explanation of evaluation criteria
    description = Column(Text)
    
    # Weight for weighted average scoring; default 1.0 means equal weight
    # Higher values (e.g., 2.0) increase this criterion's importance
    weight = Column(Float, default=1.0)

    # Relationships
    # Many-to-one: Each criterion belongs to one rubric
    rubric = relationship("Rubric", back_populates="criteria")
    
    # One-to-many: A criterion has multiple scoring levels (e.g., Excellent, Good, Poor)
    # Cascade delete removes levels when parent criterion is deleted
    levels = relationship("Level", back_populates="criterion", cascade="all, delete-orphan")


class Level(Base):
    """
    A scoring level within a criterion (e.g., 'Excellent', 'Satisfactory', 'Insufficient').
    
    Levels represent the possible scores for a criterion. Each level has a
    title, description explaining the criteria for that score, and point value.
    The AI evaluator uses level_description to justify assigned scores.
    
    Attributes:
        id: Unique identifier, auto-incremented primary key with index
        criterion_id: Foreign key to parent Criterion (cascade deleted)
        level_title: Display name for this level (required, max 100 chars)
        level_description: Detailed criteria text used by AI to justify scoring
        score_points: Numeric point value for this level (required)
    
    Relationships:
        criterion: Many-to-one → Criterion (parent criterion)
    
    Example:
        For criterion 'Error Handling':
        - Level "Excellent" (4 points): "Comprehensive error handling with logging"
        - Level "Satisfactory" (3 points): "Basic error handling present"
        - Level "Insufficient" (1 point): "Minimal or no error handling"
    """
    __tablename__ = "levels"

    # Primary key - auto-incremented unique identifier
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to parent Criterion; CASCADE delete ensures level is
    # removed when parent criterion is deleted
    criterion_id = Column(Integer, ForeignKey("criteria.id", ondelete="CASCADE"))
    
    # Required: Display name (e.g., "Excellent", "Good", "Satisfactory", "Insufficient")
    level_title = Column(String(100), nullable=False)
    
    # The exact text the AI uses to justify the score - describes what
    # qualifies code for this level (used in AI prompt for evaluation)
    level_description = Column(Text)
    
    # Required: Numeric point value for this level (e.g., 4, 3, 2, 1, 0)
    score_points = Column(Float, nullable=False)

    # Relationships
    # Many-to-one: Each level belongs to one criterion
    criterion = relationship("Criterion", back_populates="levels")


# =============================================================================
# EVALUATION ENGINE (The "History & Results")
# =============================================================================

class Evaluation(Base):
    """
    Record of a single repository analysis run.
    
    An evaluation represents one complete assessment of a repository against
    a rubric. It stores input context (briefing, model version) and output
    results (total score, AI-generated summary, status).
    
    Attributes:
        id: Unique identifier, auto-incremented primary key with index
        rubric_id: Foreign key to the Rubric used for evaluation
        repo_url: URL of the evaluated repository (required, max 512 chars)
        briefing_snapshot: PDF text content captured at evaluation time
        model_version: AI model identifier used for generation (e.g., 'gpt-4')
        total_score: Aggregated score across all findings (default: 0.0)
        ai_summary: Qualitative global feedback generated by AI
        status: Evaluation state - 'pending', 'completed', 'failed' (default: 'pending')
        created_at: Timestamp of evaluation creation (auto-set to UTC now)
    
    Relationships:
        rubric: Many-to-one → Rubric (the rubric used for evaluation)
        findings: One-to-many → Finding (cascade deleted with evaluation)
    
    Note:
        briefing_snapshot preserves the input state at evaluation time,
        ensuring reproducibility and audit trail for scoring decisions.
        This allows historical evaluations to remain valid even if the
        original briefing document is modified.
    """
    __tablename__ = "evaluations"

    # Primary key - auto-incremented unique identifier
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to the Rubric used for this evaluation
    # No CASCADE delete - evaluations should persist even if rubric is modified
    rubric_id = Column(Integer, ForeignKey("rubrics.id"))
    
    # Required: URL of the repository being evaluated (GitHub, GitLab, etc.)
    repo_url = Column(String(512), nullable=False)
    
    # --- Traceability & Input History ---
    # Stores the PDF text content at time of evaluation for audit trail
    # and reproducibility purposes
    briefing_snapshot = Column(Text)
    
    # Tracks which AI model generated the results (e.g., "gpt-4", "gpt-3.5-turbo")
    # Important for comparing results across model versions
    model_version = Column(String(50))
    
    # --- Results ---
    # Aggregated score from all findings; calculated as weighted average
    # based on criterion weights and selected level scores
    total_score = Column(Float, default=0.0)
    
    # Qualitative 'Global Feedback' - AI-generated summary of the evaluation
    # providing overall assessment and recommendations
    ai_summary = Column(Text)
    
    # Evaluation state: 'pending' (in progress), 'completed' (finished), 
    # 'failed' (error occurred)
    status = Column(String(50), default="pending")
    
    # Auto-set timestamp when evaluation is created (UTC timezone)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    # Many-to-one: Each evaluation uses one rubric
    rubric = relationship("Rubric", back_populates="evaluations")
    
    # One-to-many: An evaluation has multiple findings (one per criterion)
    # Cascade delete removes all findings when evaluation is deleted
    findings = relationship("Finding", back_populates="evaluation", cascade="all, delete-orphan")


class Finding(Base):
    """
    Individual 'WHIS' finding: Specific evidence discovered during evaluation.
    
    A finding captures the AI's assessment for a specific criterion, including
    the selected scoring level, evidence from the codebase, and improvement
    suggestions. Named 'WHIS' for Where-How-Improvement-Score data points.
    
    Attributes:
        id: Unique identifier, auto-incremented primary key with index
        evaluation_id: Foreign key to parent Evaluation (cascade deleted)
        criterion_id: Foreign key to the Criterion being evaluated
        selected_level_id: Foreign key to the Level assigned by AI (nullable)
        file_path: Location in repository where evidence was found (Where)
        evidence_snippet: Code excerpt demonstrating the finding (What)
        improvement_suggestion: Recommended action for improvement (How)
    
    Relationships:
        evaluation: Many-to-one → Evaluation (parent evaluation)
        criterion: Many-to-one → Criterion (the evaluated criterion)
        selected_level: Many-to-one → Level (the assigned score level)
    
    Note:
        The WHIS acronym represents:
        - W (Where): file_path - location in codebase
        - H (How): improvement_suggestion - how to improve
        - I (Improvement): implicitly covered by improvement_suggestion
        - S (Score): selected_level_id → score_points
        
        Each evaluation typically has one finding per criterion in the rubric.
    """
    __tablename__ = "findings"

    # Primary key - auto-incremented unique identifier
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to parent Evaluation; CASCADE delete ensures finding is
    # removed when parent evaluation is deleted
    evaluation_id = Column(Integer, ForeignKey("evaluations.id", ondelete="CASCADE"))
    
    # Foreign key to the Criterion being evaluated by this finding
    # No CASCADE - criterion reference should remain for data integrity
    criterion_id = Column(Integer, ForeignKey("criteria.id"))
    
    # Foreign key to the Level selected by AI; nullable to allow partial
    # evaluations where a level couldn't be determined
    selected_level_id = Column(Integer, ForeignKey("levels.id"), nullable=True)
    
    # --- WHIS Data Points ---
    # WHERE: File path in the repository where evidence was found
    # (e.g., "src/handlers/error_handler.py")
    file_path = Column(Text)
    
    # WHAT: Code excerpt or description demonstrating the finding
    # (e.g., "try/except block without logging")
    evidence_snippet = Column(Text)
    
    # HOW: Specific recommendation for improvement
    # (e.g., "Add logging statements to exception handlers")
    improvement_suggestion = Column(Text)

    # Relationships
    # Many-to-one: Each finding belongs to one evaluation
    evaluation = relationship("Evaluation", back_populates="findings")
    
    # Many-to-one: Each finding evaluates one criterion
    criterion = relationship("Criterion")
    
    # Many-to-one: Each finding has one selected scoring level
    selected_level = relationship("Level")
    