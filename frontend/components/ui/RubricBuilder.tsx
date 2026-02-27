'use client';

import React, { useState, useCallback } from 'react';
import { cn } from '@/lib/utils/cn';
import { Button } from './Button';
import { DropdownMenu } from './DropdownMenu';
import {
  X,
  Plus,
  Trash2,
  Copy,
  GripVertical,
  MoreVertical,
  ChevronDown,
  ToggleLeft,
  ToggleRight,
} from 'lucide-react';

// ---------------------------------------------------------------------------
// Types — designed to map 1-to-1 with the future API payload
// ---------------------------------------------------------------------------

export interface RubricLevel {
  /** Unique identifier (uuid in production, random string here) */
  id: string;
  title: string;
  description: string;
  /** Points awarded for this level. Ignored when useScores is false. */
  points: number;
}

export interface RubricCriterion {
  id: string;
  title: string;
  description: string;
  /** Ordered list of performance levels (columns) */
  levels: RubricLevel[];
}

export interface RubricData {
  title: string;
  useScores: boolean;
  /** Highest-to-lowest or lowest-to-highest column order */
  scoreOrder: 'descending' | 'ascending';
  criteria: RubricCriterion[];
}

export interface RubricBuilderProps {
  /**
   * Initial rubric data. Leave undefined to start a fresh rubric.
   * Tip: pass the API response here when editing an existing rubric.
   */
  defaultValue?: Partial<RubricData>;
  /**
   * Called when the user clicks "Save".
   * Receives the full RubricData payload — ready to POST/PUT to the API.
   */
  onSave?: (data: RubricData) => void | Promise<void>;
  /** Called when the user clicks the X button */
  onClose?: () => void;
  /** Shows a spinner on the Save button while the API call is in flight */
  isSaving?: boolean;
  /** Label shown in the top-left header area */
  headerTitle?: string;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const uid = () => Math.random().toString(36).slice(2, 9);

const defaultLevel = (points = 1): RubricLevel => ({
  id: uid(),
  title: '',
  description: '',
  points,
});

const defaultCriterion = (): RubricCriterion => ({
  id: uid(),
  title: '',
  description: '',
  levels: [defaultLevel(1)],
});

const emptyRubric = (): RubricData => ({
  title: '',
  useScores: true,
  scoreOrder: 'descending',
  criteria: [defaultCriterion()],
});

// ---------------------------------------------------------------------------
// Sub-component: LevelCell
// ---------------------------------------------------------------------------

interface LevelCellProps {
  level: RubricLevel;
  useScores: boolean;
  isOnly: boolean;
  onChange: (updated: RubricLevel) => void;
  onDelete: () => void;
  onAddBefore: () => void;
  onAddAfter: () => void;
}

const LevelCell: React.FC<LevelCellProps> = ({
  level,
  useScores,
  isOnly,
  onChange,
  onDelete,
  onAddBefore,
  onAddAfter,
}) => {
  const update = (field: Partial<RubricLevel>) =>
    onChange({ ...level, ...field });

  return (
    <div className="relative flex items-stretch gap-0 group/level">
      {/* Add level BEFORE button */}
      <button
        type="button"
        onClick={onAddBefore}
        title="Add level before"
        className={cn(
          'self-center opacity-0 group-hover/level:opacity-100 transition-opacity',
          'w-7 h-7 rounded-full border-2 border-indigo-400 bg-white text-indigo-500',
          'flex items-center justify-center hover:bg-indigo-50 shrink-0 -ml-3.5 z-10'
        )}
      >
        <Plus className="w-3.5 h-3.5" />
      </button>

      {/* Level card */}
      <div className="flex-1 border border-gray-200 rounded-lg p-3 bg-white min-w-40">
        {/* Points */}
        {useScores && (
          <div className="mb-2">
            <label className="text-xs text-gray-400 block mb-0.5">
              Points (required)
            </label>
            <input
              type="number"
              min={0}
              value={level.points}
              onChange={(e) =>
                update({ points: Math.max(0, Number(e.target.value)) })
              }
              className={cn(
                'w-full border-b border-gray-300 focus:border-indigo-500 focus:outline-none',
                'text-sm pb-0.5 bg-transparent'
              )}
            />
          </div>
        )}

        {/* Level title */}
        <input
          type="text"
          value={level.title}
          onChange={(e) => update({ title: e.target.value })}
          placeholder="Level title"
          className={cn(
            'w-full border-b border-gray-300 focus:border-indigo-500 focus:outline-none',
            'text-sm pb-0.5 bg-transparent mb-2 placeholder:text-gray-300'
          )}
        />

        {/* Level description */}
        <textarea
          value={level.description}
          onChange={(e) => update({ description: e.target.value })}
          placeholder="Description"
          rows={3}
          className={cn(
            'w-full border-b border-gray-300 focus:border-indigo-500 focus:outline-none',
            'text-sm pb-0.5 bg-transparent resize-none placeholder:text-gray-300'
          )}
        />

        {/* Delete level (hidden if it's the only one) */}
        {!isOnly && (
          <button
            type="button"
            onClick={onDelete}
            title="Delete level"
            className={cn(
              'mt-2 text-gray-400 hover:text-red-500 transition-colors',
              'opacity-0 group-hover/level:opacity-100'
            )}
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      {/* Add level AFTER button */}
      <button
        type="button"
        onClick={onAddAfter}
        title="Add level after"
        className={cn(
          'self-center opacity-0 group-hover/level:opacity-100 transition-opacity',
          'w-7 h-7 rounded-full border-2 border-indigo-400 bg-white text-indigo-500',
          'flex items-center justify-center hover:bg-indigo-50 shrink-0 -mr-3.5 z-10'
        )}
      >
        <Plus className="w-3.5 h-3.5" />
      </button>
    </div>
  );
};

// ---------------------------------------------------------------------------
// Sub-component: CriterionCard
// ---------------------------------------------------------------------------

interface CriterionCardProps {
  criterion: RubricCriterion;
  useScores: boolean;
  isOnly: boolean;
  onChange: (updated: RubricCriterion) => void;
  onDelete: () => void;
  onDuplicate: () => void;
}

const CriterionCard: React.FC<CriterionCardProps> = ({
  criterion,
  useScores,
  isOnly,
  onChange,
  onDelete,
  onDuplicate,
}) => {
  const update = (field: Partial<RubricCriterion>) =>
    onChange({ ...criterion, ...field });

  const updateLevel = (index: number, updated: RubricLevel) => {
    const levels = [...criterion.levels];
    levels[index] = updated;
    update({ levels });
  };

  const deleteLevel = (index: number) => {
    update({ levels: criterion.levels.filter((_, i) => i !== index) });
  };

  const addLevelAt = (index: number) => {
    const levels = [...criterion.levels];
    const adjacentPoints =
      index < levels.length ? levels[index].points : levels[index - 1]?.points ?? 1;
    levels.splice(index, 0, defaultLevel(Math.max(0, adjacentPoints - 1)));
    update({ levels });
  };

  const maxPoints = useScores
    ? Math.max(...criterion.levels.map((l) => l.points))
    : null;

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5 group/card">
      {/* Card header row */}
      <div className="flex items-start gap-2 mb-4">
        {/* Drag handle (visual only for now) */}
        <GripVertical className="w-5 h-5 text-gray-300 cursor-grab mt-1 shrink-0" />

        {/* Title + description */}
        <div className="flex-1 space-y-2">
          <input
            type="text"
            value={criterion.title}
            onChange={(e) => update({ title: e.target.value })}
            placeholder="Criterion title (required)"
            className={cn(
              'w-full border-b border-gray-300 focus:border-indigo-500 focus:outline-none',
              'text-base font-medium pb-1 bg-transparent placeholder:text-gray-300'
            )}
          />
          <input
            type="text"
            value={criterion.description}
            onChange={(e) => update({ description: e.target.value })}
            placeholder="Criterion description"
            className={cn(
              'w-full border-b border-gray-300 focus:border-indigo-500 focus:outline-none',
              'text-sm text-gray-600 pb-1 bg-transparent placeholder:text-gray-300'
            )}
          />
        </div>

        {/* Max points badge */}
        {useScores && (
          <span className="text-sm text-gray-500 shrink-0">
            /{maxPoints} pts
          </span>
        )}

        {/* Three-dot menu */}
        <DropdownMenu
          align="right"
          trigger={
            <button
              type="button"
              className="p-1 rounded hover:bg-gray-100 text-gray-400 hover:text-gray-700 transition-colors"
            >
              <MoreVertical className="w-4 h-4" />
            </button>
          }
          groups={[
            {
              items: [
                {
                  key: 'duplicate',
                  label: 'Duplicate criterion',
                  icon: <Copy className="w-4 h-4" />,
                  onClick: onDuplicate,
                },
              ],
            },
            {
              items: [
                {
                  key: 'delete',
                  label: 'Delete criterion',
                  icon: <Trash2 className="w-4 h-4" />,
                  destructive: true,
                  disabled: isOnly,
                  onClick: onDelete,
                },
              ],
            },
          ]}
        />
      </div>

      {/* Levels row — horizontal scroll on small screens */}
      <div className="flex gap-3 overflow-x-auto pb-2">
        {criterion.levels.map((level, i) => (
          <LevelCell
            key={level.id}
            level={level}
            useScores={useScores}
            isOnly={criterion.levels.length === 1}
            onChange={(updated) => updateLevel(i, updated)}
            onDelete={() => deleteLevel(i)}
            onAddBefore={() => addLevelAt(i)}
            onAddAfter={() => addLevelAt(i + 1)}
          />
        ))}
      </div>
    </div>
  );
};

// ---------------------------------------------------------------------------
// Main: RubricBuilder
// ---------------------------------------------------------------------------

/**
 * RubricBuilder — full-screen rubric creation/editing UI inspired by Google Classroom.
 *
 * Features:
 * - Rubric title input
 * - Toggle: use scores on/off
 * - Score order selector (descending / ascending)
 * - Add / delete / duplicate criteria
 * - Add / delete performance levels per criterion (with + buttons on each side)
 * - Points, level title and level description per cell
 * - onSave callback receives a typed RubricData payload ready for the API
 * - isSaving prop shows loading state on the Save button
 *
 * @example
 * // In a page or inside a Modal
 * <RubricBuilder
 *   headerTitle="Create rubric"
 *   onClose={() => setOpen(false)}
 *   onSave={async (data) => {
 *     await api.post('/rubrics', data);
 *     setOpen(false);
 *   }}
 *   isSaving={isSubmitting}
 * />
 *
 * @example
 * // Editing an existing rubric
 * <RubricBuilder
 *   headerTitle="Edit rubric"
 *   defaultValue={existingRubric}   // ← API response shape matches RubricData
 *   onSave={(data) => api.put(`/rubrics/${id}`, data)}
 *   onClose={handleClose}
 * />
 */
export const RubricBuilder: React.FC<RubricBuilderProps> = ({
  defaultValue,
  onSave,
  onClose,
  isSaving = false,
  headerTitle = 'Create rubric',
}) => {
  const [rubric, setRubric] = useState<RubricData>(() => ({
    ...emptyRubric(),
    ...defaultValue,
  }));

  const update = (field: Partial<RubricData>) =>
    setRubric((prev) => ({ ...prev, ...field }));

  // --- Criteria operations ---

  const updateCriterion = useCallback(
    (index: number, updated: RubricCriterion) => {
      const criteria = [...rubric.criteria];
      criteria[index] = updated;
      update({ criteria });
    },
    [rubric.criteria]
  );

  const deleteCriterion = useCallback(
    (index: number) => {
      update({ criteria: rubric.criteria.filter((_, i) => i !== index) });
    },
    [rubric.criteria]
  );

  const duplicateCriterion = useCallback(
    (index: number) => {
      const source = rubric.criteria[index];
      const clone: RubricCriterion = {
        ...source,
        id: uid(),
        levels: source.levels.map((l) => ({ ...l, id: uid() })),
        title: source.title ? `${source.title} (copy)` : '',
      };
      const criteria = [...rubric.criteria];
      criteria.splice(index + 1, 0, clone);
      update({ criteria });
    },
    [rubric.criteria]
  );

  const addCriterion = () => {
    update({ criteria: [...rubric.criteria, defaultCriterion()] });
  };

  // --- Total points ---
  const totalPoints = rubric.useScores
    ? rubric.criteria.reduce(
        (sum, c) => sum + Math.max(...c.levels.map((l) => l.points), 0),
        0
      )
    : null;

  // --- Save ---
  const handleSave = () => onSave?.(rubric);

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------

  return (
    <div className="flex flex-col h-full bg-white min-h-screen">
      {/* ── Top header bar ── */}
      <header className="flex items-center justify-between px-5 py-3 border-b border-gray-200 bg-white sticky top-0 z-20 shadow-sm">
        <div className="flex items-center gap-3">
          {onClose && (
            <button
              type="button"
              onClick={onClose}
              className="p-1.5 rounded-full hover:bg-gray-100 transition-colors text-gray-500"
              aria-label="Close"
            >
              <X className="w-5 h-5" />
            </button>
          )}
          <span className="text-base font-medium text-gray-800">
            {headerTitle}
          </span>
        </div>

        <Button
          onClick={handleSave}
          isLoading={isSaving}
          disabled={!rubric.title.trim()}
          size="sm"
        >
          Save
        </Button>
      </header>

      {/* ── Main content ── */}
      <main className="flex-1 overflow-y-auto px-4 py-8 bg-gray-50">
        <div className="max-w-4xl mx-auto space-y-6">

          {/* Rubric title */}
          <div className="flex items-start justify-between gap-4">
            <input
              type="text"
              value={rubric.title}
              onChange={(e) => update({ title: e.target.value })}
              placeholder="Untitled rubric"
              className={cn(
                'flex-1 text-3xl font-bold text-gray-900 bg-transparent',
                'border-b-2 border-transparent focus:border-indigo-400 focus:outline-none',
                'pb-1 placeholder:text-gray-300 transition-colors'
              )}
            />

            {/* Rubric-level three-dot menu */}
            <DropdownMenu
              align="right"
              trigger={
                <button
                  type="button"
                  className="p-1.5 rounded-full hover:bg-gray-100 text-gray-500 transition-colors mt-1"
                >
                  <MoreVertical className="w-5 h-5" />
                </button>
              }
              groups={[
                {
                  items: [
                    {
                      key: 'reset',
                      label: 'Reset rubric',
                      icon: <Trash2 className="w-4 h-4" />,
                      destructive: true,
                      onClick: () => setRubric(emptyRubric()),
                    },
                  ],
                },
              ]}
            />
          </div>

          {/* Score settings row */}
          <div className="flex flex-wrap items-center gap-6">
            {/* Use scores toggle */}
            <button
              type="button"
              onClick={() => update({ useScores: !rubric.useScores })}
              className="flex items-center gap-2 text-sm font-medium text-gray-700"
            >
              {rubric.useScores ? (
                <ToggleRight className="w-9 h-9 text-indigo-600" />
              ) : (
                <ToggleLeft className="w-9 h-9 text-gray-400" />
              )}
              Use scores
            </button>

            {/* Score order selector */}
            {rubric.useScores && (
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <span>Score order:</span>
                <div className="relative">
                  <select
                    value={rubric.scoreOrder}
                    onChange={(e) =>
                      update({
                        scoreOrder: e.target.value as RubricData['scoreOrder'],
                      })
                    }
                    className={cn(
                      'appearance-none pr-8 pl-2 py-1 border border-gray-300 rounded-md',
                      'text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white'
                    )}
                  >
                    <option value="descending">Descending</option>
                    <option value="ascending">Ascending</option>
                  </select>
                  <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                </div>
              </div>
            )}

            {/* Total points badge */}
            {rubric.useScores && totalPoints !== null && (
              <span className="ml-auto text-sm font-medium text-gray-500">
                Total: <strong className="text-gray-800">{totalPoints}</strong> pts
              </span>
            )}
          </div>

          {/* Criteria list */}
          <div className="space-y-4">
            {rubric.criteria.map((criterion, index) => (
              <CriterionCard
                key={criterion.id}
                criterion={criterion}
                useScores={rubric.useScores}
                isOnly={rubric.criteria.length === 1}
                onChange={(updated) => updateCriterion(index, updated)}
                onDelete={() => deleteCriterion(index)}
                onDuplicate={() => duplicateCriterion(index)}
              />
            ))}
          </div>

          {/* Add criterion button */}
          <button
            type="button"
            onClick={addCriterion}
            className={cn(
              'flex items-center gap-2 px-4 py-2.5 rounded-lg border-2 border-dashed',
              'border-gray-300 text-gray-500 text-sm font-medium w-full justify-center',
              'hover:border-indigo-400 hover:text-indigo-600 hover:bg-indigo-50 transition-colors'
            )}
          >
            <Plus className="w-4 h-4" />
            Add criterion
          </button>
        </div>
      </main>
    </div>
  );
};

RubricBuilder.displayName = 'RubricBuilder';
