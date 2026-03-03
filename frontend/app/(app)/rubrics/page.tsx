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
  Check,
  X,
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
  // Inline level editing state (Option C — granular level management)
  // ---------------------------------------------------------------------------

  /** The level currently being edited inline in the expanded card view. */
  const [editingLevel, setEditingLevel] = useState<{
    rubricId: number;
    criterionId: number;
    levelId: number;
    data: { level_title: string; level_description: string; score_points: number };
  } | null>(null);

  /** The criterion that is currently receiving a new level (add-level form open). */
  const [addingLevel, setAddingLevel] = useState<{
    rubricId: number;
    criterionId: number;
    data: { level_title: string; level_description: string; score_points: number };
  } | null>(null);

  /** Indicates an in-flight PUT / POST / DELETE on a single level. */
  const [levelLoading, setLevelLoading] = useState(false);

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

  /**
   * Force-refetches a rubric detail and replaces the cache entry.
   * Used after inline level edits so the expanded card reflects the latest data.
   */
  const refreshRubricDetail = useCallback(
    async (id: number) => {
      try {
        const res = await fetch(`${apiUrl}/api/v1/rubrics/${id}/`);
        if (!res.ok) return;
        const json: ApiResponse<RubricDetail> = await res.json();
        if (!json.success) return;
        setCriteriaCache((prev) => ({ ...prev, [id]: json.data }));
      } catch { /* silently ignore refresh errors */ }
    },
    [apiUrl]
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
  // Inline level handlers (Option C — granular level management)
  // Each action calls the appropriate /criteria/{cid}/levels/* endpoint and
  // then refreshes the cached rubric detail so the expanded view stays in sync.
  // ---------------------------------------------------------------------------

  /**
   * PUT /rubrics/{rid}/criteria/{cid}/levels/{lid}/
   * Saves title, description, and score_points of the level currently in edit mode.
   */
  const handleUpdateLevel = async () => {
    if (!editingLevel) return;
    setLevelLoading(true);
    setActionError(null);
    try {
      const { rubricId, criterionId, levelId, data } = editingLevel;
      const res = await fetch(
        `${apiUrl}/api/v1/rubrics/criteria/${criterionId}/levels/${levelId}/`,
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
        }
      );
      if (!res.ok) throw new Error(`Failed to update level (${res.status})`);
      const json: ApiResponse<RubricLevel> = await res.json();
      if (!json.success) throw new Error(json.message || 'Failed to update level');
      setEditingLevel(null);
      await refreshRubricDetail(rubricId);
    } catch (err) {
      setActionError(err instanceof Error ? err.message : 'Failed to update level');
    } finally {
      setLevelLoading(false);
    }
  };

  /**
   * DELETE /rubrics/{rid}/criteria/{cid}/levels/{lid}/
   * Removes a single performance level from a criterion.
   */
  const handleDeleteLevel = async (rubricId: number, criterionId: number, levelId: number) => {
    setLevelLoading(true);
    setActionError(null);
    try {
      const res = await fetch(
        `${apiUrl}/api/v1/rubrics/criteria/${criterionId}/levels/${levelId}/`,
        { method: 'DELETE' }
      );
      if (!res.ok) throw new Error(`Failed to delete level (${res.status})`);
      await refreshRubricDetail(rubricId);
    } catch (err) {
      setActionError(err instanceof Error ? err.message : 'Failed to delete level');
    } finally {
      setLevelLoading(false);
    }
  };

  /**
   * POST /rubrics/{rid}/criteria/{cid}/levels/
   * Appends a new performance level to an existing criterion.
   */
  const handleAddLevel = async () => {
    if (!addingLevel) return;
    setLevelLoading(true);
    setActionError(null);
    try {
      const { rubricId, criterionId, data } = addingLevel;
      const res = await fetch(
        `${apiUrl}/api/v1/rubrics/criteria/${criterionId}/levels/`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
        }
      );
      if (!res.ok) throw new Error(`Failed to add level (${res.status})`);
      const json: ApiResponse<RubricLevel> = await res.json();
      if (!json.success) throw new Error(json.message || 'Failed to add level');
      setAddingLevel(null);
      await refreshRubricDetail(rubricId);
    } catch (err) {
      setActionError(err instanceof Error ? err.message : 'Failed to add level');
    } finally {
      setLevelLoading(false);
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

                {/* Expanded criteria list — with inline granular level management */}
                {isExpanded && detail && (
                  <div className="border-t border-gray-100 px-5 py-4 bg-gray-50 space-y-5">
                    {detail.criteria.length === 0 ? (
                      <p className="text-sm text-gray-400 italic">No criteria defined.</p>
                    ) : (
                      detail.criteria.map((criterion) => (
                        <div key={criterion.id ?? criterion.title} className="text-sm">
                          {/* Criterion header */}
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-semibold text-gray-800 flex-1">
                              {criterion.title}
                            </span>
                            <span className="text-xs text-indigo-600 shrink-0">
                              weight: {criterion.weight}
                            </span>
                          </div>
                          {criterion.description && (
                            <p className="text-xs text-gray-500 mb-2 leading-relaxed">
                              {criterion.description}
                            </p>
                          )}

                          {/* Levels */}
                          <div className="space-y-1 pl-1">
                            {criterion.levels.map((level) => {
                              const isEditingThis =
                                editingLevel?.criterionId === criterion.id &&
                                editingLevel?.levelId === level.id;

                              if (isEditingThis && editingLevel) {
                                return (
                                  <div
                                    key={level.id}
                                    className="rounded-md border border-indigo-300 bg-indigo-50 p-2 space-y-1.5"
                                  >
                                    <div className="flex items-center gap-2">
                                      <input
                                        autoFocus
                                        className="flex-1 text-xs border-b border-indigo-400 bg-transparent focus:outline-none placeholder:text-gray-400"
                                        placeholder="Level title"
                                        value={editingLevel.data.level_title}
                                        onChange={(e) =>
                                          setEditingLevel({
                                            ...editingLevel,
                                            data: { ...editingLevel.data, level_title: e.target.value },
                                          })
                                        }
                                      />
                                      <input
                                        type="number"
                                        min={0}
                                        className="w-14 text-xs border-b border-indigo-400 bg-transparent focus:outline-none text-right"
                                        value={editingLevel.data.score_points}
                                        onChange={(e) =>
                                          setEditingLevel({
                                            ...editingLevel,
                                            data: {
                                              ...editingLevel.data,
                                              score_points: Math.max(0, Number(e.target.value)),
                                            },
                                          })
                                        }
                                      />
                                      <span className="text-xs text-gray-400 shrink-0">pts</span>
                                      <button
                                        onClick={handleUpdateLevel}
                                        disabled={levelLoading}
                                        title="Save changes"
                                        className="p-1 rounded text-green-600 hover:bg-green-100 disabled:opacity-50 shrink-0"
                                      >
                                        {levelLoading ? (
                                          <div className="w-3 h-3 border border-green-600 border-t-transparent rounded-full animate-spin" />
                                        ) : (
                                          <Check className="w-3.5 h-3.5" />
                                        )}
                                      </button>
                                      <button
                                        onClick={() => setEditingLevel(null)}
                                        disabled={levelLoading}
                                        title="Cancel"
                                        className="p-1 rounded text-gray-500 hover:bg-gray-200 disabled:opacity-50 shrink-0"
                                      >
                                        <X className="w-3.5 h-3.5" />
                                      </button>
                                    </div>
                                    <textarea
                                      rows={2}
                                      className="w-full text-xs border-b border-indigo-300 bg-transparent focus:outline-none resize-none placeholder:text-gray-400"
                                      placeholder="Level description (optional)"
                                      value={editingLevel.data.level_description}
                                      onChange={(e) =>
                                        setEditingLevel({
                                          ...editingLevel,
                                          data: {
                                            ...editingLevel.data,
                                            level_description: e.target.value,
                                          },
                                        })
                                      }
                                    />
                                  </div>
                                );
                              }

                              return (
                                <div
                                  key={level.id}
                                  className="flex items-center gap-2 py-0.5 group/lvlrow"
                                >
                                  <span className="w-1.5 h-1.5 rounded-full bg-indigo-300 shrink-0" />
                                  <span
                                    className="flex-1 text-xs text-gray-700 truncate"
                                    title={level.level_description || level.level_title}
                                  >
                                    {level.level_title || (
                                      <span className="italic text-gray-400">(untitled)</span>
                                    )}
                                  </span>
                                  <span className="text-xs font-medium text-indigo-600 shrink-0">
                                    {level.score_points} pts
                                  </span>
                                  {/* Edit level — PUT /criteria/{cid}/levels/{lid}/ */}
                                  <button
                                    onClick={() =>
                                      setEditingLevel({
                                        rubricId: rubric.id,
                                        criterionId: criterion.id!,
                                        levelId: level.id!,
                                        data: {
                                          level_title: level.level_title,
                                          level_description: level.level_description,
                                          score_points: level.score_points,
                                        },
                                      })
                                    }
                                    title="Edit level"
                                    className="p-0.5 rounded text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 opacity-0 group-hover/lvlrow:opacity-100 transition-opacity shrink-0"
                                  >
                                    <Pencil className="w-3 h-3" />
                                  </button>
                                  {/* Delete level — DELETE /criteria/{cid}/levels/{lid}/ */}
                                  <button
                                    onClick={() =>
                                      handleDeleteLevel(rubric.id, criterion.id!, level.id!)
                                    }
                                    disabled={levelLoading || criterion.levels.length <= 1}
                                    title={
                                      criterion.levels.length <= 1
                                        ? 'Cannot delete the only level'
                                        : 'Delete level'
                                    }
                                    className="p-0.5 rounded text-gray-400 hover:text-red-600 hover:bg-red-50 opacity-0 group-hover/lvlrow:opacity-100 transition-opacity disabled:opacity-30 disabled:cursor-not-allowed shrink-0"
                                  >
                                    <Trash2 className="w-3 h-3" />
                                  </button>
                                </div>
                              );
                            })}

                            {/* Add level form / button — POST /criteria/{cid}/levels/ */}
                            {addingLevel?.criterionId === criterion.id ? (
                              <div className="rounded-md border border-indigo-300 bg-indigo-50 p-2 space-y-1.5 mt-1">
                                <div className="flex items-center gap-2">
                                  <input
                                    autoFocus
                                    className="flex-1 text-xs border-b border-indigo-400 bg-transparent focus:outline-none placeholder:text-gray-400"
                                    placeholder="Level title (required)"
                                    value={addingLevel.data.level_title}
                                    onChange={(e) =>
                                      setAddingLevel({
                                        ...addingLevel,
                                        data: { ...addingLevel.data, level_title: e.target.value },
                                      })
                                    }
                                  />
                                  <input
                                    type="number"
                                    min={0}
                                    className="w-14 text-xs border-b border-indigo-400 bg-transparent focus:outline-none text-right"
                                    value={addingLevel.data.score_points}
                                    onChange={(e) =>
                                      setAddingLevel({
                                        ...addingLevel,
                                        data: {
                                          ...addingLevel.data,
                                          score_points: Math.max(0, Number(e.target.value)),
                                        },
                                      })
                                    }
                                  />
                                  <span className="text-xs text-gray-400 shrink-0">pts</span>
                                  <button
                                    onClick={handleAddLevel}
                                    disabled={levelLoading || !addingLevel.data.level_title.trim()}
                                    title="Confirm add level"
                                    className="p-1 rounded text-green-600 hover:bg-green-100 disabled:opacity-50 shrink-0"
                                  >
                                    {levelLoading ? (
                                      <div className="w-3 h-3 border border-green-600 border-t-transparent rounded-full animate-spin" />
                                    ) : (
                                      <Check className="w-3.5 h-3.5" />
                                    )}
                                  </button>
                                  <button
                                    onClick={() => setAddingLevel(null)}
                                    disabled={levelLoading}
                                    title="Cancel"
                                    className="p-1 rounded text-gray-500 hover:bg-gray-200 disabled:opacity-50 shrink-0"
                                  >
                                    <X className="w-3.5 h-3.5" />
                                  </button>
                                </div>
                                <textarea
                                  rows={2}
                                  className="w-full text-xs border-b border-indigo-300 bg-transparent focus:outline-none resize-none placeholder:text-gray-400"
                                  placeholder="Level description (optional)"
                                  value={addingLevel.data.level_description}
                                  onChange={(e) =>
                                    setAddingLevel({
                                      ...addingLevel,
                                      data: {
                                        ...addingLevel.data,
                                        level_description: e.target.value,
                                      },
                                    })
                                  }
                                />
                              </div>
                            ) : (
                              <button
                                onClick={() =>
                                  setAddingLevel({
                                    rubricId: rubric.id,
                                    criterionId: criterion.id!,
                                    data: { level_title: '', level_description: '', score_points: 1 },
                                  })
                                }
                                className="flex items-center gap-1 text-xs text-indigo-500 hover:text-indigo-700 mt-1 px-1 py-0.5 rounded hover:bg-indigo-50 transition-colors"
                              >
                                <Plus className="w-3 h-3" />
                                Add level
                              </button>
                            )}
                          </div>
                        </div>
                      ))
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
          <div className="relative w-full max-w-5xl h-[90vh] bg-white rounded-xl shadow-xl flex flex-col overflow-hidden">
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
          <div className="relative w-full max-w-5xl h-[90vh] bg-white rounded-xl shadow-xl flex flex-col overflow-hidden">
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
