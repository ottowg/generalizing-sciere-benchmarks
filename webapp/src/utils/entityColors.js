/**
 * Shared entity/relation color and layout-anchor utilities.
 * Used by LabelFilterPanel, RelationSignatures, ExamplePaper, etc.
 */

// ── entity colors ─────────────────────────────────────────────────────────────
export const ENTITY_COLORS = {
  // GSAP-ERE labels
  MLModel:           '#1d4ed8',
  MLModelGeneric:    '#1e40af',
  ModelArchitecture: '#3b82f6',
  Method:            '#2563eb',
  Dataset:           '#d97706',
  DataSource:        '#b45309',
  DatasetGeneric:    '#92400e',
  Task:              '#b91c1c',
  ReferenceLink:     '#6b7280',
  URL:               '#9ca3af',
  // SciER / SciNLP raw labels
  method:            '#2563eb',
  dataset:           '#d97706',
  task:              '#b91c1c',
  metric:            '#15803d',
}

export function entityColor(lbl) {
  return ENTITY_COLORS[lbl] ?? '#6b7280'
}

// ── semantic layout anchors ───────────────────────────────────────────────────
// Fractions of SVG width/height: method → top-left, data → top-right,
// task → lower-right, metric → lower-left, referential → near top-right.
export const ENTITY_ANCHORS = {
  Method:            { ax: 0.18, ay: 0.12 },
  method:            { ax: 0.18, ay: 0.12 },
  MLModel:           { ax: 0.18, ay: 0.12 },
  MLModelGeneric:    { ax: 0.18, ay: 0.12 },
  ModelArchitecture: { ax: 0.18, ay: 0.12 },
  Task:              { ax: 0.82, ay: 0.85 },
  task:              { ax: 0.82, ay: 0.85 },
  Dataset:           { ax: 0.82, ay: 0.12 },
  DatasetGeneric:    { ax: 0.82, ay: 0.12 },
  DataSource:        { ax: 0.82, ay: 0.12 },
  dataset:           { ax: 0.82, ay: 0.12 },
  metric:            { ax: 0.15, ay: 0.85 },
  ReferenceLink:     { ax: 0.92, ay: 0.20 },
  URL:               { ax: 0.92, ay: 0.20 },
}

// ── relation colors (stable singleton map) ────────────────────────────────────
const REL_COLORS = [
  '#e11d48', '#f97316', '#ca8a04', '#16a34a', '#0891b2',
  '#6366f1', '#9333ea', '#db2777', '#14b8a6', '#64748b',
  '#c2410c', '#15803d', '#1d4ed8', '#7e22ce', '#be185d',
]
const _relMap = new Map()
let   _relIdx = 0

export function relColorStable(lbl) {
  if (!_relMap.has(lbl)) {
    _relMap.set(lbl, REL_COLORS[_relIdx % REL_COLORS.length])
    _relIdx++
  }
  return _relMap.get(lbl)
}
