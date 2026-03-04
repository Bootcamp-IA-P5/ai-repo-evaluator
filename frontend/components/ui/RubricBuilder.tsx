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
// API payload types  ← map 1-to-1 with the backend schema
// ---------------------------------------------------------------------------

/** Maps to a single cell in the rubric grid (one performance level) */
export interface RubricLevel {
  /** Present when hydrated from the API (used for edit diffing). */
  id?: number;
  level_title: string;
  level_description: string;
  /** Points awarded at this level. Used when use_scores is enabled. */
  score_points: number;
}

/** Maps to a single row in the rubric grid (one evaluation criterion) */
export interface RubricCriterion {
  /** Present when hydrated from the API (used for edit diffing). */
  id?: number;
  title: string;
  description: string;
  /**
   * Multiplier applied to the criterion's max score when calculating the
   * weighted total. Example: weight=1.5 means this criterion counts 50% more.
   */
  weight: number;
  levels: RubricLevel[];
}

/** Root payload for POST /rubrics and PUT /rubrics/:id */
export interface RubricData {
  title: string;
  description: string;
  criteria: RubricCriterion[];
}

// ---------------------------------------------------------------------------
// Internal UI types — extend the API types with React-only fields
// (these are stripped before calling onSave)
// ---------------------------------------------------------------------------

interface InternalLevel extends RubricLevel {
  /** React key — never sent to the API */
  _id: string;
}

interface InternalCriterion extends RubricCriterion {
  /** React key — never sent to the API */
  _id: string;
  levels: InternalLevel[];
}

interface InternalRubric extends RubricData {
  criteria: InternalCriterion[];
  /** UI-only: whether to show the score_points field in each level cell */
  useScores: boolean;
  /** UI-only: visual column order (does not affect the payload) */
  scoreOrder: 'descending' | 'ascending';
}

// ---------------------------------------------------------------------------
// Component props
// ---------------------------------------------------------------------------

export interface RubricBuilderProps {
  /**
   * Pre-populate the builder with existing rubric data.
   * Pass the API response directly — the shape matches RubricData exactly.
   */
  defaultValue?: Partial<RubricData>;
  /**
   * Called when the user clicks "Save".
   * Receives the exact RubricData payload ready to POST/PUT to the API
   * (internal _id and UI-only fields are stripped automatically).
   */
  onSave?: (data: RubricData) => void | Promise<void>;
  /** Called when the user clicks the × button */
  onClose?: () => void;
  /** Puts the Save button in loading state while the API call is in flight */
  isSaving?: boolean;
  /** Label shown in the top-left header */
  headerTitle?: string;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const uid = () => Math.random().toString(36).slice(2, 9);

const defaultLevel = (score_points = 1): InternalLevel => ({
  _id: uid(),
  level_title: '',
  level_description: '',
  score_points,
});

const defaultCriterion = (): InternalCriterion => ({
  _id: uid(),
  title: '',
  description: '',
  weight: 1,
  levels: [defaultLevel(1)],
});

const emptyRubric = (): InternalRubric => ({
  title: '',
  description: '',
  useScores: true,
  scoreOrder: 'descending',
  criteria: [defaultCriterion()],
});

/**
 * Converts InternalRubric → RubricData (strips _id and UI-only fields).
 * This is the clean API payload passed to onSave.
 */
const buildPayload = (rubric: InternalRubric): RubricData => ({
  title: rubric.title,
  description: rubric.description,
  criteria: rubric.criteria.map((c) => ({
    // Preserve id so edit pages can diff existing vs new criteria
    ...(c.id !== undefined ? { id: c.id } : {}),
    title: c.title,
    description: c.description,
    weight: c.weight,
    levels: c.levels.map((l) => ({
      ...(l.id !== undefined ? { id: l.id } : {}),
      level_title: l.level_title,
      level_description: l.level_description,
      score_points: l.score_points,
    })),
  })),
});

/**
 * Hydrates a RubricData (from the API) into an InternalRubric (adds _id fields).
 */
const hydrateRubric = (data: Partial<RubricData>): InternalRubric => ({
  ...emptyRubric(),
  ...data,
  criteria: (data.criteria ?? [defaultCriterion()]).map((c) => ({
    _id: uid(),
    ...c,
    levels: (c.levels ?? [defaultLevel()]).map((l) => ({ _id: uid(), ...l })),
  })),
});

// ---------------------------------------------------------------------------
// Sub-component: LevelCell
// ---------------------------------------------------------------------------

interface LevelCellProps {
  level: InternalLevel;
  useScores: boolean;
  isOnly: boolean;
  onChange: (updated: InternalLevel) => void;
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
  const update = (field: Partial<InternalLevel>) => onChange({ ...level, ...field });

  return (
    <div className="relative flex items-stretch gap-0 group/level">
      {/* + Add level BEFORE */}
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
        {/* score_points */}
        {useScores && (
          <div className="mb-2">
            <label className="text-xs text-gray-400 block mb-0.5">
              Points (required)
            </label>
            <input
              type="number"
              min={0}
              value={level.score_points}
              onChange={(e) =>
                update({ score_points: Math.max(0, Number(e.target.value)) })
              }
              className={cn(
                'w-full border-b border-gray-300 focus:border-indigo-500 focus:outline-none',
                'text-sm pb-0.5 bg-transparent text-gray-900'
              )}
            />
          </div>
        )}

        {/* level_title */}
        <input
          type="text"
          value={level.level_title}
          onChange={(e) => update({ level_title: e.target.value })}
          placeholder="Level title"
          className={cn(
            'w-full border-b border-gray-300 focus:border-indigo-500 focus:outline-none',
            'text-sm pb-0.5 bg-transparent mb-2 text-gray-900 placeholder:text-gray-300'
          )}
        />

        {/* level_description */}
        <textarea
          value={level.level_description}
          onChange={(e) => update({ level_description: e.target.value })}
          placeholder="Description"
          rows={3}
          className={cn(
            'w-full border-b border-gray-300 focus:border-indigo-500 focus:outline-none',
            'text-sm pb-0.5 bg-transparent resize-none text-gray-900 placeholder:text-gray-300'
          )}
        />

        {/* Delete level */}
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

      {/* + Add level AFTER */}
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
  criterion: InternalCriterion;
  useScores: boolean;
  isOnly: boolean;
  onChange: (updated: InternalCriterion) => void;
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
  const update = (field: Partial<InternalCriterion>) =>
    onChange({ ...criterion, ...field });

  const updateLevel = (index: number, updated: InternalLevel) => {
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
      index < levels.length
        ? levels[index].score_points
        : (levels[index - 1]?.score_points ?? 1);
    levels.splice(index, 0, defaultLevel(Math.max(0, adjacentPoints - 1)));
    update({ levels });
  };

  const maxPoints = useScores
    ? Math.max(...criterion.levels.map((l) => l.score_points), 0)
    : null;

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5 group/card">
      {/* Card header row */}
      <div className="flex items-start gap-2 mb-4">
        {/* Drag handle (visual only) */}
        <GripVertical className="w-5 h-5 text-gray-300 cursor-grab mt-1 shrink-0" />

        {/* title + description */}
        <div className="flex-1 space-y-2">
          <input
            type="text"
            value={criterion.title}
            onChange={(e) => update({ title: e.target.value })}
            placeholder="Criterion title (required)"
            className={cn(
              'w-full border-b border-gray-300 focus:border-indigo-500 focus:outline-none',
              'text-base font-medium pb-1 bg-transparent text-gray-900 placeholder:text-gray-300'
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

        {/* weight field */}
        <div className="flex flex-col items-end gap-0.5 shrink-0">
          <label className="text-xs text-gray-400">Weight</label>
          <input
            type="number"
            min={0.1}
            step={0.1}
            value={criterion.weight}
            onChange={(e) =>
              update({ weight: Math.max(0.1, parseFloat(e.target.value) || 1) })
            }
            className={cn(
              'w-16 border border-gray-300 rounded-md px-2 py-0.5 text-sm text-right',
              'focus:outline-none focus:ring-2 focus:ring-indigo-500'
            )}
          />
        </div>

        {/* Max points badge */}
        {useScores && (
          <span className="text-sm text-gray-500 shrink-0 mt-5">
            /{maxPoints} pts
          </span>
        )}

        {/* Three-dot menu */}
        <DropdownMenu
          align="right"
          trigger={
            <button
              type="button"
              className="p-1 rounded hover:bg-gray-100 text-gray-400 hover:text-gray-700 transition-colors mt-4"
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

      {/* Levels row */}
      <div className="flex gap-3 overflow-x-auto pb-2">
        {criterion.levels.map((level, i) => (
          <LevelCell
            key={level._id}
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
 * The payload emitted by onSave matches the backend schema exactly:
 * ```json
 * {
 *   "title": "Python Backend Project",
 *   "description": "Evaluates backend architecture, code quality...",
 *   "criteria": [
 *     {
 *       "title": "Error Handling",
 *       "description": "Evaluates the completeness of error handling",
 *       "weight": 1,
 *       "levels": [
 *         { "level_title": "Excellent", "level_description": "...", "score_points": 4 },
 *         { "level_title": "Satisfactory", "level_description": "...", "score_points": 3 }
 *       ]
 *     }
 *   ]
 * }
 * ```
 *
 * @example
 * // Create a new rubric
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
 * // Edit an existing rubric (API response shape matches RubricData directly)
 * <RubricBuilder
 *   headerTitle="Edit rubric"
 *   defaultValue={rubricFromApi}
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
  const [rubric, setRubric] = useState<InternalRubric>(() =>
    defaultValue ? hydrateRubric(defaultValue) : emptyRubric()
  );

  const update = (field: Partial<InternalRubric>) =>
    setRubric((prev) => ({ ...prev, ...field }));

  // --- Criteria operations ---

  const updateCriterion = useCallback(
    (index: number, updated: InternalCriterion) => {
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
      const clone: InternalCriterion = {
        ...source,
        _id: uid(),
        levels: source.levels.map((l) => ({ ...l, _id: uid() })),
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

  // --- Derived values ---
  const totalPoints = rubric.useScores
    ? rubric.criteria.reduce(
        (sum, c) => sum + Math.max(...c.levels.map((l) => l.score_points), 0),
        0
      )
    : null;

  // --- Save: strip internal fields and emit clean API payload ---
  const handleSave = () => onSave?.(buildPayload(rubric));

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------

  return (
    <div className="flex flex-col h-full bg-white">
      {/* ── Top header bar ── */}
      <header className="flex items-center justify-between px-5 py-3 border-b border-gray-200 bg-white shrink-0 z-20 shadow-sm">
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
      <main className="flex-1 min-h-0 overflow-y-auto px-4 py-8 bg-gray-50">
        <div className="max-w-4xl mx-auto space-y-6">

          {/* Rubric title + description */}
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1 space-y-2">
              <input
                type="text"
                value={rubric.title}
                onChange={(e) => update({ title: e.target.value })}
                placeholder="Untitled rubric"
                className={cn(
                  'w-full text-3xl font-bold text-gray-900 bg-transparent',
                  'border-b-2 border-transparent focus:border-indigo-400 focus:outline-none',
                  'pb-1 placeholder:text-gray-300 transition-colors'
                )}
              />
              {/* Rubric description (top-level API field) */}
              <input
                type="text"
                value={rubric.description}
                onChange={(e) => update({ description: e.target.value })}
                placeholder="Rubric description (optional)"
                className={cn(
                  'w-full text-sm text-gray-500 bg-transparent',
                  'border-b border-transparent focus:border-indigo-300 focus:outline-none',
                  'pb-0.5 placeholder:text-gray-300 transition-colors'
                )}
              />
            </div>

            {/* Rubric-level menu */}
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

          {/* Score settings row — UI only, not sent to API */}
          <div className="flex flex-wrap items-center gap-6">
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

            {rubric.useScores && (
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <span>Score order:</span>
                <div className="relative">
                  <select
                    value={rubric.scoreOrder}
                    onChange={(e) =>
                      update({ scoreOrder: e.target.value as InternalRubric['scoreOrder'] })
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
                key={criterion._id}
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
