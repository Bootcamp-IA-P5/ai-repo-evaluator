/**
 * Shared TypeScript types across the application
 */

// === RUBRIC TYPES ===
export interface RubricCriteria {
  id: string;
  name: string;
  description: string;
  points: number;
  weight?: number;
}

export interface Rubric {
  id: string;
  name: string;
  description?: string;
  criteria: RubricCriteria[];
  totalPoints: number;
  createdAt?: string;
  updatedAt?: string;
}

// === EVALUATION TYPES ===
export interface EvaluationRequest {
  rubricId: string;
  briefingFile: File;
  repositoryUrl: string;
  provider: LLMProvider;
  model: string;
  apiKey?: string;
}

export interface EvaluationResult {
  id: string;
  score: number;
  maxScore: number;
  percentage: number;
  criteriaResults: CriteriaResult[];
  qualitativeComment: QualitativeComment;
  findings: Finding[];
  createdAt: string;
}

export interface CriteriaResult {
  criteriaId: string;
  criteriaName: string;
  achieved: boolean;
  points: number;
  maxPoints: number;
  comment?: string;
}

export interface QualitativeComment {
  strengths: string[];
  improvements: string[];
  overallAssessment: string;
}

export interface Finding {
  id: string;
  type: 'improvement' | 'issue' | 'suggestion';
  title: string;
  description: string;
  file?: string;
  line?: number;
  code?: string;
  priority: 'low' | 'medium' | 'high';
}

// === LLM TYPES ===
export type LLMProvider = 'gemini' | 'openai' | 'grok';

export interface LLMModel {
  id: string;
  name: string;
  provider: LLMProvider;
  contextWindow: number;
}

// === REPOSITORY TYPES ===
export interface Repository {
  url: string;
  owner: string;
  name: string;
  branch?: string;
  lastCommit?: string;
}

// === API RESPONSE TYPES ===
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface ApiError {
  message: string;
  code?: string;
  details?: Record<string, unknown>;
}
