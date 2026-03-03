'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Plus,
  Pencil,
  Trash2,
  BookOpen,
  ChevronDown,
  ChevronUp,
  Calendar,
} from 'lucide-react';
import { Button, Card, Alert, ConfirmModal } from '@/components/ui';
import { RubricBuilder } from '@/components/ui/RubricBuilder';
import type { RubricData } from '@/components/ui/RubricBuilder';
import { PageHeader } from '@/components/layout';

// ---------------------------------------------------------------------------
// Types — aligned with API response schema
// ---------------------------------------------------------------------------

interface RubricSummary {
  id: number;
  title: string;
  description: string;
  created_at: string;
}

interface RubricLevel {
  id?: number;
  level_title: string;
  level_description: string;
  score_points: number;
}

interface RubricCriterion {
  id?: number;
  title: string;
  description: string;
  weight: number;
  levels: RubricLevel[];
}

interface RubricDetail extends RubricSummary {
  criteria: RubricCriterion[];
}

interface ApiResponse<T> {
  success: boolean;
  data: T;
  errors: string[];
  message: string;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function RubricsPage() {
  // Use relative URLs so the Next.js proxy rewrite handles routing to the backend.
  // This avoids CORS issues regardless of the NEXT_PUBLIC_API_URL value.
  const apiUrl = '';

  // Rubric list
  const [rubrics, setRubrics] = useState<RubricSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);

  // Lazy-loaded criteria — keyed by rubric id
  const [criteriaCache, setCriteriaCache] = useState<Record<number, RubricDetail>>({});
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [criteriaLoading, setCriteriaLoading] = useState<number | null>(null);

  // Create modal
  const [createOpen, setCreateOpen] = useState(false);

  // Edit modal
  const [editRubric, setEditRubric] = useState<RubricDetail | null>(null);
  const [editFetching, setEditFetching] = useState(false);

  // Delete modal
  const [deleteRubric, setDeleteRubric] = useState<RubricSummary | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Shared saving state (create + edit) and action-level error
  const [isSaving, setIsSaving] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  // ---------------------------------------------------------------------------
  // Fetch helpers
  // ---------------------------------------------------------------------------

  const fetchRubrics = useCallback(async () => {
    setLoading(true);
    setFetchError(null);
    try {
      const res = await fetch(`${apiUrl}/api/v1/rubrics/`);
      if (!res.ok) throw new Error(`Could not load rubrics (${res.status})`);
      const json: ApiResponse<RubricSummary[]> = await res.json();
      if (!json.success) throw new Error(json.message || 'Could not load rubrics');
      setRubrics(json.data);
    } catch (err) {
      setFetchError(err instanceof Error ? err.message : 'Could not load rubrics');
    } finally {
      setLoading(false);
    }
  }, [apiUrl]);

  useEffect(() => {
    fetchRubrics();
  }, [fetchRubrics]);

  /** Fetches and caches the full rubric detail (with criteria). */
  const fetchRubricDetail = useCallback(
    async (id: number): Promise<RubricDetail | null> => {
      if (criteriaCache[id]) return criteriaCache[id];
      try {
        const res = await fetch(`${apiUrl}/api/v1/rubrics/${id}`);
        if (!res.ok) throw new Error('Failed to load rubric details');
        const json: ApiResponse<RubricDetail> = await res.json();
        if (!json.success) throw new Error(json.message || 'Failed to load rubric details');
        setCriteriaCache((prev) => ({ ...prev, [id]: json.data }));
        return json.data;
      } catch {
        return null;
      }
    },
    [apiUrl, criteriaCache]
  );

  // ---------------------------------------------------------------------------
  // Interactions
  // ---------------------------------------------------------------------------

  const handleToggleCriteria = async (id: number) => {
    if (expandedId === id) {
      setExpandedId(null);
      return;
    }
    setExpandedId(id);
    if (!criteriaCache[id]) {
      setCriteriaLoading(id);
      await fetchRubricDetail(id);
      setCriteriaLoading(null);
    }
  };

  const handleEditClick = async (rubric: RubricSummary) => {
    setActionError(null);
    setEditFetching(true);
    const detail = await fetchRubricDetail(rubric.id);
    setEditFetching(false);
    if (!detail) {
      setActionError('Could not load rubric details for editing.');
      return;
    }
    setEditRubric(detail);
  };

  const handleCreate = async (data: RubricData) => {
    setIsSaving(true);
    setActionError(null);
    try {
      const res = await fetch(`${apiUrl}/api/v1/rubrics/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error(`Failed to create rubric (${res.status})`);
      const json: ApiResponse<RubricSummary> = await res.json();
      if (!json.success) throw new Error(json.message || 'Failed to create rubric');
      setCreateOpen(false);
      await fetchRubrics();
    } catch (err) {
      setActionError(err instanceof Error ? err.message : 'Failed to create rubric');
    } finally {
      setIsSaving(false);
    }
  };

  const handleEdit = async (data: RubricData) => {
    if (!editRubric) return;
    setIsSaving(true);
    setActionError(null);
    try {
      // Step 1: Update rubric metadata only (PUT only accepts title + description)
      const metaRes = await fetch(`${apiUrl}/api/v1/rubrics/${editRubric.id}/`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: data.title, description: data.description }),
      });
      if (!metaRes.ok) throw new Error(`Failed to update rubric (${metaRes.status})`);
      const metaJson: ApiResponse<RubricSummary> = await metaRes.json();
      if (!metaJson.success) throw new Error(metaJson.message || 'Failed to update rubric');

      // Step 2: Diff criteria — delete removed, update existing, create new
      const existingIds = new Set(editRubric.criteria.map((c) => c.id).filter(Boolean));
      const incomingIds = new Set(data.criteria.map((c) => c.id).filter(Boolean));

      // 2a. Delete criteria that were removed in the editor
      for (const existing of editRubric.criteria) {
        if (existing.id && !incomingIds.has(existing.id)) {
          await fetch(`${apiUrl}/api/v1/rubrics/${editRubric.id}/criteria/${existing.id}/`, {
            method: 'DELETE',
          });
        }
      }

      // 2b. Update existing criteria / create new ones
      for (const criterion of data.criteria) {
        const payload = {
          title: criterion.title,
          description: criterion.description,
          weight: criterion.weight,
          levels: criterion.levels,
        };

        if (criterion.id && existingIds.has(criterion.id)) {
          // Update existing criterion (PUT accepts title, description, weight, levels)
          await fetch(
            `${apiUrl}/api/v1/rubrics/${editRubric.id}/criteria/${criterion.id}/`,
            {
              method: 'PUT',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(payload),
            }
          );
        } else {
          // Create new criterion
          await fetch(`${apiUrl}/api/v1/rubrics/${editRubric.id}/criteria/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
          });
        }
      }

      // Invalidate cache so updated criteria are refetched on next expand
      setCriteriaCache((prev) => {
        const next = { ...prev };
        delete next[editRubric.id];
        return next;
      });
      setEditRubric(null);
      await fetchRubrics();
    } catch (err) {
      setActionError(err instanceof Error ? err.message : 'Failed to update rubric');
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteRubric) return;
    setIsDeleting(true);
    setActionError(null);
    try {
      const res = await fetch(`${apiUrl}/api/v1/rubrics/${deleteRubric.id}`, {
        method: 'DELETE',
      });
      if (!res.ok) throw new Error(`Failed to delete rubric (${res.status})`);
      const json: ApiResponse<null> = await res.json();
      if (!json.success) throw new Error(json.message || 'Failed to delete rubric');
      // Clean up cache and expanded state
      setCriteriaCache((prev) => {
        const next = { ...prev };
        delete next[deleteRubric.id];
        return next;
      });
      if (expandedId === deleteRubric.id) setExpandedId(null);
      setDeleteRubric(null);
      await fetchRubrics();
    } catch (err) {
      setActionError(err instanceof Error ? err.message : 'Failed to delete rubric');
    } finally {
      setIsDeleting(false);
    }
  };

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------

  return (
    <div className="max-w-6xl mx-auto">
      <PageHeader
        title="Evaluation Rubrics"
        description="Manage evaluation criteria and scoring templates"
        action={
          <Button
            leftIcon={<Plus className="w-4 h-4" />}
            onClick={() => {
              setActionError(null);
              setCreateOpen(true);
            }}
          >
            Create Rubric
          </Button>
        }
      />

      {/* Action-level error (create / edit / delete failures) */}
      {actionError && (
        <Alert
          variant="error"
          message={actionError}
          className="mb-6"
          onDismiss={() => setActionError(null)}
        />
      )}

      {/* Loading state */}
      {loading ? (
        <div className="flex items-center justify-center py-24 text-gray-500">
          <div className="text-center">
            <div className="w-8 h-8 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
            <p className="text-sm">Loading rubrics...</p>
          </div>
        </div>
      ) : fetchError ? (
        /* Fetch error state */
        <Alert variant="error" message={fetchError} />
      ) : rubrics.length === 0 ? (
        /* Empty state */
        <div className="flex flex-col items-center justify-center py-24 text-center">
          <BookOpen className="w-14 h-14 mb-4 text-gray-200" />
          <p className="text-lg font-semibold text-gray-700">No rubrics yet</p>
          <p className="mt-1 text-sm text-gray-500">
            Create your first rubric to start evaluating repositories.
          </p>
          <Button
            className="mt-6"
            leftIcon={<Plus className="w-4 h-4" />}
            onClick={() => {
              setActionError(null);
              setCreateOpen(true);
            }}
          >
            Create Rubric
          </Button>
        </div>
      ) : (
        /* Rubric card grid */
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {rubrics.map((rubric) => {
            const isExpanded = expandedId === rubric.id;
            const isLoadingCriteria = criteriaLoading === rubric.id;
            const detail = criteriaCache[rubric.id];

            return (
              <Card key={rubric.id} padding="none" className="flex flex-col">
                {/* Card body */}
                <div className="p-5 flex-1">
                  {/* Top row: icon + action buttons */}
                  <div className="flex items-start justify-between gap-2 mb-3">
                    <div className="p-2 bg-indigo-50 rounded-lg shrink-0">
                      <BookOpen className="w-5 h-5 text-indigo-600" />
                    </div>
                    <div className="flex gap-1 shrink-0">
                      {/* Edit button */}
                      <button
                        onClick={() => handleEditClick(rubric)}
                        disabled={editFetching}
                        className="p-1.5 rounded text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 transition-colors disabled:opacity-50"
                        title="Edit rubric"
                        aria-label="Edit rubric"
                      >
                        {editFetching ? (
                          <div className="w-4 h-4 border border-indigo-600 border-t-transparent rounded-full animate-spin" />
                        ) : (
                          <Pencil className="w-4 h-4" />
                        )}
                      </button>
                      {/* Delete button */}
                      <button
                        onClick={() => {
                          setActionError(null);
                          setDeleteRubric(rubric);
                        }}
                        className="p-1.5 rounded text-gray-400 hover:text-red-600 hover:bg-red-50 transition-colors"
                        title="Delete rubric"
                        aria-label="Delete rubric"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  {/* Title & description */}
                  <h3 className="text-base font-semibold text-gray-900 leading-snug mb-1">
                    {rubric.title}
                  </h3>
                  {rubric.description && (
                    <p className="text-sm text-gray-500 line-clamp-2">{rubric.description}</p>
                  )}

                  {/* Stats */}
                  <div className="mt-4 space-y-1.5 text-sm border-t border-gray-100 pt-3">
                    {detail && (
                      <div className="flex justify-between text-gray-600">
                        <span>Criteria</span>
                        <span className="font-medium text-gray-900">{detail.criteria.length}</span>
                      </div>
                    )}
                    <div className="flex items-center justify-between text-gray-600">
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3.5 h-3.5 shrink-0" />
                        Created
                      </span>
                      <span className="font-medium text-gray-900">
                        {formatDate(rubric.created_at)}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Expanded criteria list */}
                {isExpanded && detail && (
                  <div className="border-t border-gray-100 px-5 py-3 bg-gray-50">
                    {detail.criteria.length === 0 ? (
                      <p className="text-sm text-gray-400 italic">No criteria defined.</p>
                    ) : (
                      <ul className="space-y-3">
                        {detail.criteria.map((criterion, idx) => (
                          <li key={idx}>
                            <p className="text-sm font-medium text-gray-800">{criterion.title}</p>
                            {criterion.description && (
                              <p className="text-xs text-gray-500 mt-0.5 leading-relaxed">
                                {criterion.description}
                              </p>
                            )}
                            <p className="text-xs text-indigo-600 mt-1">
                              Weight: {criterion.weight} &middot; {criterion.levels.length} level
                              {criterion.levels.length !== 1 ? 's' : ''}
                            </p>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                )}

                {/* View Criteria toggle */}
                <button
                  onClick={() => handleToggleCriteria(rubric.id)}
                  className="border-t border-gray-100 px-5 py-3 flex items-center justify-between w-full text-sm font-medium text-indigo-600 hover:bg-indigo-50 transition-colors rounded-b-lg"
                >
                  {isLoadingCriteria ? (
                    <span className="flex items-center gap-2">
                      <div className="w-3.5 h-3.5 border border-indigo-600 border-t-transparent rounded-full animate-spin" />
                      Loading...
                    </span>
                  ) : (
                    <span>View Criteria</span>
                  )}
                  {isExpanded ? (
                    <ChevronUp className="w-4 h-4" />
                  ) : (
                    <ChevronDown className="w-4 h-4" />
                  )}
                </button>
              </Card>
            );
          })}
        </div>
      )}

      {/* ── Create Overlay ── */}
      {createOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          {/* Backdrop */}
          <div className="absolute inset-0 bg-black/50" aria-hidden="true" />
          {/* Panel */}
          <div className="relative w-full max-w-5xl max-h-[90vh] bg-white rounded-xl shadow-xl flex flex-col overflow-hidden">
            <RubricBuilder
              onSave={handleCreate}
              onClose={() => setCreateOpen(false)}
              isSaving={isSaving}
              headerTitle="New Rubric"
            />
          </div>
        </div>
      )}

      {/* ── Edit Overlay ── */}
      {editRubric !== null && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          {/* Backdrop */}
          <div className="absolute inset-0 bg-black/50" aria-hidden="true" />
          {/* Panel */}
          <div className="relative w-full max-w-5xl max-h-[90vh] bg-white rounded-xl shadow-xl flex flex-col overflow-hidden">
            <RubricBuilder
              defaultValue={{
                title: editRubric.title,
                description: editRubric.description,
                criteria: editRubric.criteria,
              }}
              onSave={handleEdit}
              onClose={() => setEditRubric(null)}
              isSaving={isSaving}
              headerTitle="Edit Rubric"
            />
          </div>
        </div>
      )}

      {/* ── Delete Confirm Modal ── */}
      <ConfirmModal
        isOpen={deleteRubric !== null}
        onClose={() => setDeleteRubric(null)}
        onConfirm={handleDelete}
        title="Delete Rubric"
        message={`Are you sure you want to delete "${deleteRubric?.title}"? This will permanently remove the rubric and all its criteria.`}
        confirmLabel="Delete"
        cancelLabel="Cancel"
        confirmVariant="danger"
        isLoading={isDeleting}
      />
    </div>
  );
}
