'use client';

import React, { useState, useEffect } from 'react';
import { Github, Eye, EyeOff } from 'lucide-react';
import {
  Button,
  Input,
  Select,
  FileUpload,
  Card,
  CardContent,
  Alert,
} from '@/components/ui';
import { PageHeader } from '@/components/layout';
import type { SelectOption } from '@/components/ui';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const AI_PROVIDERS: SelectOption[] = [
  { value: 'groq', label: 'Groq' },
  { value: 'openai', label: 'OpenAI' },
  { value: 'anthropic', label: 'Anthropic' },
];

const MODELS_BY_PROVIDER: Record<string, SelectOption[]> = {
  groq: [
    { value: 'llama-3.3-70b-versatile', label: 'LLaMA 3.3 70B' },
    { value: 'llama3-8b-8192', label: 'LLaMA 3 8B' },
    { value: 'mixtral-8x7b-32768', label: 'Mixtral 8x7B' },
  ],
  openai: [
    { value: 'gpt-4o', label: 'GPT-4o' },
    { value: 'gpt-4o-mini', label: 'GPT-4o Mini' },
    { value: 'gpt-4-turbo', label: 'GPT-4 Turbo' },
  ],
  anthropic: [
    { value: 'claude-3-5-sonnet-20241022', label: 'Claude 3.5 Sonnet' },
    { value: 'claude-3-5-haiku-20241022', label: 'Claude 3.5 Haiku' },
    { value: 'claude-3-opus-20240229', label: 'Claude 3 Opus' },
  ],
};

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface RubricOption {
  id: number;
  title: string;
}

interface FormState {
  rubricId: string;
  briefingFile: File | null;
  repoUrl: string;
  provider: string;
  model: string;
  apiKey: string;
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function NewEvaluationPage() {
  // Rubrics from API
  const [rubrics, setRubrics] = useState<RubricOption[]>([]);
  const [rubricsLoading, setRubricsLoading] = useState(true);
  const [rubricsError, setRubricsError] = useState(false);

  // Form
  const [form, setForm] = useState<FormState>({
    rubricId: '',
    briefingFile: null,
    repoUrl: '',
    provider: '',
    model: '',
    apiKey: '',
  });

  // UI
  const [showApiKey, setShowApiKey] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  // Load rubrics on mount
  useEffect(() => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';
    fetch(`${apiUrl}/api/v1/rubrics`)
      .then((res) => {
        if (!res.ok) throw new Error('Failed to load rubrics');
        return res.json();
      })
      .then((data: RubricOption[]) => {
        setRubrics(data);
        setRubricsLoading(false);
      })
      .catch(() => {
        setRubricsError(true);
        setRubricsLoading(false);
      });
  }, []);

  // Model options depend on selected provider
  const modelOptions: SelectOption[] = form.provider
    ? (MODELS_BY_PROVIDER[form.provider] ?? [])
    : [];

  // Reset model when provider changes
  const handleProviderChange = (value: string) => {
    setForm((prev) => ({ ...prev, provider: value, model: '' }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitError(null);
    setSubmitSuccess(false);
    setIsSubmitting(true);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';
      const body = new FormData();
      body.append('rubric_id', form.rubricId);
      if (form.briefingFile) body.append('briefing', form.briefingFile);
      body.append('repo_url', form.repoUrl);
      body.append('provider', form.provider);
      body.append('model', form.model);
      if (form.apiKey) body.append('api_key', form.apiKey);

      const res = await fetch(`${apiUrl}/api/v1/evaluations`, {
        method: 'POST',
        body,
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(
          (err as { detail?: string })?.detail ?? 'Evaluation failed. Please try again.'
        );
      }

      setSubmitSuccess(true);
      // Reset form on success
      setForm({ rubricId: '', briefingFile: null, repoUrl: '', provider: '', model: '', apiKey: '' });
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : 'Unexpected error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const rubricOptions: SelectOption[] = rubrics.map((r) => ({
    value: String(r.id),
    label: r.title,
  }));

  const isFormValid =
    form.rubricId !== '' &&
    form.briefingFile !== null &&
    form.repoUrl.trim() !== '' &&
    form.provider !== '' &&
    form.model !== '';

  return (
    <div className="max-w-3xl mx-auto w-full">
      <PageHeader
        title="New Evaluation"
        description="Configure and run an AI-powered repository evaluation"
      />

      {submitSuccess && (
        <Alert
          variant="success"
          message="Evaluation started successfully! Check Past Evaluations for results."
          className="mb-6"
        />
      )}

      {submitError && (
        <Alert
          variant="error"
          message={submitError}
          className="mb-6"
          onDismiss={() => setSubmitError(null)}
        />
      )}

      <Card>
        <CardContent className="pt-6">
          <form onSubmit={handleSubmit} className="space-y-6">

            {/* Evaluation Rubric */}
            <Select
              label="Evaluation Rubric"
              placeholder={rubricsLoading ? 'Loading rubrics...' : 'Select a rubric...'}
              options={rubricOptions}
              value={form.rubricId}
              onChange={(val) => setForm((prev) => ({ ...prev, rubricId: val }))}
              disabled={rubricsLoading || rubricsError}
              error={
                rubricsError
                  ? 'Could not load rubrics. Is the backend running?'
                  : undefined
              }
              fullWidth
            />

            {/* Project Briefing (PDF) */}
            <FileUpload
              label="Project Briefing (PDF)"
              accept=".pdf"
              maxSize={10}
              onFileSelect={(file) =>
                setForm((prev) => ({ ...prev, briefingFile: file }))
              }
            />

            {/* GitHub Repository URL */}
            <Input
              label="GitHub Repository URL"
              type="url"
              placeholder="https://github.com/username/repository"
              value={form.repoUrl}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, repoUrl: e.target.value }))
              }
              leftIcon={<Github className="w-4 h-4" />}
              fullWidth
            />

            {/* AI Provider */}
            <Select
              label="AI Provider"
              placeholder="Select a provider..."
              options={AI_PROVIDERS}
              value={form.provider}
              onChange={handleProviderChange}
              fullWidth
            />

            {/* Model */}
            <Select
              label="Model"
              placeholder={
                form.provider ? 'Select a model...' : 'Select a provider first'
              }
              options={modelOptions}
              value={form.model}
              onChange={(val) => setForm((prev) => ({ ...prev, model: val }))}
              disabled={!form.provider}
              fullWidth
            />

            {/* API Key — BYOK (optional) */}
            <Input
              label="API Key (Optional — BYOK)"
              type={showApiKey ? 'text' : 'password'}
              placeholder="sk-..."
              value={form.apiKey}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, apiKey: e.target.value }))
              }
              helperText="Leave empty to use the default backend key."
              rightIcon={
                <button
                  type="button"
                  onClick={() => setShowApiKey((v) => !v)}
                  className="text-gray-400 hover:text-gray-600 focus:outline-none"
                  aria-label={showApiKey ? 'Hide API key' : 'Show API key'}
                >
                  {showApiKey ? (
                    <EyeOff className="w-4 h-4" />
                  ) : (
                    <Eye className="w-4 h-4" />
                  )}
                </button>
              }
              fullWidth
            />

            {/* Submit */}
            <Button
              type="submit"
              variant="primary"
              size="lg"
              fullWidth
              disabled={!isFormValid || isSubmitting}
              isLoading={isSubmitting}
            >
              Run Evaluation
            </Button>

          </form>
        </CardContent>
      </Card>
    </div>
  );
}
