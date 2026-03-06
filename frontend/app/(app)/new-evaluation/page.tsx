'use client';

import React, { useState, useEffect } from 'react';
import { Github, FileText } from 'lucide-react';
import {
  Button,
  Input,
  Select,
  Card,
  CardContent,
  Alert,
} from '@/components/ui';
import { PageHeader } from '@/components/layout';
import type { SelectOption } from '@/components/ui';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface RubricOption {
  id: number;
  title: string;
}

interface FormState {
  rubricId: string;
  briefingPath: string;
  repoUrl: string;
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
    briefingPath: '',
    repoUrl: '',
  });

  // UI
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  // Load rubrics on mount
  useEffect(() => {
    fetch(`/api/v1/rubrics/`)
      .then((res) => {
        if (!res.ok) throw new Error('Failed to load rubrics');
        return res.json();
      })
      .then((json: { success: boolean; data: RubricOption[] }) => {
        if (!json.success) {
          setRubricsError(true);
          setRubricsLoading(false);
          return;
        }
        setRubrics(json.data ?? []);
        setRubricsLoading(false);
      })
      .catch(() => {
        setRubricsError(true);
        setRubricsLoading(false);
      });
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitError(null);
    setSubmitSuccess(false);
    setIsSubmitting(true);

    try {
      const res = await fetch('/api/v1/evaluations/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          rubric_id: parseInt(form.rubricId, 10),
          repo_url: form.repoUrl,
          briefing_path: form.briefingPath,
        }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(
          (err as { message?: string; detail?: string })?.message ??
          (err as { detail?: string })?.detail ??
          'Evaluation failed. Please try again.'
        );
      }

      setSubmitSuccess(true);
      setForm({ rubricId: '', briefingPath: '', repoUrl: '' });
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
    form.briefingPath.trim() !== '' &&
    form.repoUrl.trim() !== '';

  return (
    <div className="max-w-3xl mx-auto">
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

            {/* Project Briefing Path */}
            <Input
              label="Project Briefing Path (PDF)"
              type="text"
              placeholder="/data/briefings/project-briefing.pdf"
              value={form.briefingPath}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, briefingPath: e.target.value }))
              }
              helperText="Absolute path to the briefing PDF on the server."
              leftIcon={<FileText className="w-4 h-4" />}
              fullWidth
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
