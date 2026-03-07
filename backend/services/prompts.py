"""
Prompt Engineering — Centralized prompt templates for AI evaluation.

This module defines the system prompt persona, grading prompt builder,
and summary prompt builder used by the AI Evaluation Engine.

All prompts are designed to:
- Establish a Senior Technical Grader persona
- Use the project briefing as the source of truth
- Enforce strict JSON output for programmatic parsing
- Follow the WHIS methodology (Where, How, Improvement, Score)
"""

from typing import Any

# SYSTEM PROMPT — The AI's "persona"

SYSTEM_PROMPT = """You are a Senior Technical Grader evaluating a student's GitHub repository.

YOUR ROLE:
- You assess code quality against specific rubric criteria.
- You provide evidence-based scoring with concrete examples from the code.
- You follow the WHIS methodology: Where (file path), What (evidence), How (improvement), Score (level).

YOUR RULES:
1. The project briefing is the ABSOLUTE SOURCE OF TRUTH. If a requirement is not in the briefing, do NOT penalize the student for it.
2. You MUST cite specific file paths and code snippets as evidence.
3. You MUST select exactly one scoring level from the provided options.
4. You MUST respond with valid JSON — no markdown, no explanation outside the JSON.
5. Be fair and constructive. Acknowledge what the student did well before suggesting improvements.
6. If you cannot find relevant code for a criterion, select the lowest level and explain why in "evidence"."""


# JSON OUTPUT SCHEMA — What the AI must return
_JSON_SCHEMA_INSTRUCTION = """\
You MUST respond with ONLY valid JSON in this EXACT format (no markdown, no extra text):
{
    "level_id": <integer: the ID of the selected scoring level>,
    "file_path": "<string: path to the most relevant file in the repository>",
    "evidence": "<string: specific code excerpt or observation that justifies the score>",
    "improvement": "<string: concrete, actionable suggestion for the student>"
}"""

# GRADING PROMPT BUILDER

def build_grading_prompt(
    criterion: dict[str, Any],
    levels: list[dict[str, Any]],
    briefing_context: str,
    code_evidence: str,
) -> str:
    """
    Build the complete grading prompt for a single criterion evaluation.

    Args:
        criterion: Dict with 'title', 'description', and 'weight' keys.
        levels: List of dicts, each with 'id', 'title', 'description',
                and 'score_points' keys.
        briefing_context: Relevant excerpts from the project briefing
                          (retrieved via ContextEngine).
        code_evidence: Relevant code snippets from the repository
                       (retrieved via ContextEngine).

    Returns:
        Complete prompt string ready to send to the LLM.
    """
    # Format the scoring levels table
    levels_text = "\n".join(
        f"  - ID {level['id']}: {level['title']} ({level['score_points']} pts) → {level['description']}"
        for level in levels
    )

    return f"""{SYSTEM_PROMPT}

CRITERION TO EVALUATE:
  Title: {criterion['title']}
  Description: {criterion['description']}
  Weight: {criterion.get('weight', 1.0)}

SCORING LEVELS (select exactly ONE by its ID):
{levels_text}

PROJECT BRIEFING CONTEXT (source of truth for requirements):
{briefing_context}

CODE EVIDENCE (from the student's repository):
{code_evidence}

INSTRUCTIONS:
1. Read the criterion description and the briefing context carefully.
2. Search the code evidence for proof that the student meets (or fails to meet) the criterion.
3. Select the scoring level that BEST matches the code quality observed.
4. Cite a specific file path and code snippet as evidence.
5. Provide a concrete, actionable improvement suggestion.

{_JSON_SCHEMA_INSTRUCTION}"""

# SUMMARY PROMPT BUILDER

def build_summary_prompt(
    repo_url: str,
    rubric_title: str,
    findings_summary: list[dict[str, Any]],
    total_score: float,
) -> str:
    """
    Build the prompt for generating the global evaluation summary.

    Args:
        repo_url: URL of the evaluated repository.
        rubric_title: Title of the rubric used for evaluation.
        findings_summary: List of dicts with 'criterion_title',
                          'score_points', 'evidence', and 'improvement' keys.
        total_score: Aggregated weighted score.

    Returns:
        Complete prompt string for summary generation.
    """
    # Format findings into a readable list
    findings_text = "\n".join(
        f"  - {f.get('criterion_title', 'Unknown')}: "
        f"{f.get('score_points', 0)} pts — "
        f"Evidence: {str(f.get('evidence', 'N/A'))[:200]} | "
        f"Improvement: {str(f.get('improvement', 'N/A'))[:200]}"
        for f in findings_summary
    )

    return f"""You are a Senior Technical Grader writing a final evaluation report for a student.

REPOSITORY: {repo_url}
RUBRIC: {rubric_title}
OVERALL SCORE: {total_score:.2f} / 10

DETAILED FINDINGS:
{findings_text}

INSTRUCTIONS:
1. Write a 3-4 paragraph summary suitable for student feedback.
2. Start with an overall assessment of the project quality.
3. Highlight the strongest aspects of the implementation.
4. Identify the most critical areas for improvement.
5. End with actionable recommendations.
6. Keep the tone CONSTRUCTIVE and EDUCATIONAL — this is a learning experience.

Write the summary in plain text (no JSON, no markdown)."""
