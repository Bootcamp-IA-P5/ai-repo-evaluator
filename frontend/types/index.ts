/**
 * Tipos TypeScript compartidos en toda la aplicación
 */

// === TIPOS DE RÚBRICA ===
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

// === TIPOS DE EVALUACIÓN ===
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

// === TIPOS DE LLM ===
export type LLMProvider = 'openai' | 'groq' | 'anthropic';

export interface LLMModel {
  id: string;
  name: string;
  provider: LLMProvider;
  contextWindow: number;
}

// === TIPOS DE REPOSITORIO ===
export interface Repository {
  url: string;
  owner: string;
  name: string;
  branch?: string;
  lastCommit?: string;
}

// === TIPOS DE RESPUESTA API ===
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
