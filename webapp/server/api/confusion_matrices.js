/**
 * Confusion Matrices API
 *
 * GET /api/confusion-matrices?dataset=gsap-ere&split=dev&annot1=gold&annot2=gsap-ere&labelset=unified
 *   Returns pre-built JSON from data/confusion_matrices/. 404 if not built yet.
 *
 * POST /api/confusion-matrices/build
 *   Runs scripts/ere_confusion_analysis/build_confusion_matrices.py via `uv run`.
 *   Precomputes all combinations and saves to data/confusion_matrices/.
 */

import { execFileSync } from 'child_process'
import fs   from 'fs'
import path from 'path'
import { jsonResponse } from '../utils.js'

const SCRIPT   = 'scripts/ere_confusion_analysis/build_confusion_matrices.py'
const DATA_DIR = 'data/webapp/confusion_matrices'

const VALID_DATASETS    = new Set(['gsap-ere', 'scier', 'scinlp'])
const VALID_SPLITS      = new Set(['train', 'dev', 'test'])
const VALID_ANNOTATIONS = new Set(['gold', 'gsap-ere', 'scier', 'scinlp'])
const VALID_LABELSETS   = new Set(['unified', 'original'])

function cacheKey(dataset, split, annot1, annot2, labelset) {
  return `${dataset}_${split}_${annot1}_${annot2}_${labelset}`.replaceAll('-', '_')
}

function dataPath(projectRoot, dataset, split, annot1, annot2, labelset) {
  return path.join(projectRoot, DATA_DIR, `${cacheKey(dataset, split, annot1, annot2, labelset)}.json`)
}

function transposeHalf(half) {
  const { labels_annot1, labels_annot2, matrix, totals_annot1, totals_annot2 } = half
  const rows = labels_annot2.length
  const cols = labels_annot1.length
  const t = Array.from({ length: rows }, (_, i) => Array.from({ length: cols }, (_, j) => matrix[j][i]))
  return { labels_annot1: labels_annot2, labels_annot2: labels_annot1, matrix: t, totals_annot1: totals_annot2, totals_annot2: totals_annot1 }
}

function transposeData(data, annot1, annot2) {
  return {
    entities:  transposeHalf(data.entities),
    relations: transposeHalf(data.relations),
    params: { ...data.params, annot1, annot2 },
  }
}

export function createConfusionMatricesMiddleware(projectRoot) {
  return async (req, res) => {
    const url = new URL(req.url, 'http://x')
    const sub = url.pathname.replace(/^\/+/, '')  // '' or 'build'

    // POST /build
    if (req.method === 'POST' && sub === 'build') {
      try {
        const stdout = execFileSync(
          'uv', ['run', 'python', SCRIPT],
          { cwd: projectRoot, timeout: 1_800_000, encoding: 'utf-8' }
        )
        return jsonResponse(res, 200, { ok: true, stdout })
      } catch (err) {
        return jsonResponse(res, 500, {
          ok:     false,
          stderr: err.stderr ?? err.message,
          stdout: err.stdout ?? '',
        })
      }
    }

    // GET
    if (req.method === 'GET' && !sub) {
      const dataset  = url.searchParams.get('dataset')
      const split    = url.searchParams.get('split')
      const annot1   = url.searchParams.get('annot1')
      const annot2   = url.searchParams.get('annot2')
      const labelset = url.searchParams.get('labelset')

      if (!VALID_DATASETS.has(dataset))    return jsonResponse(res, 400, { error: `Invalid dataset: ${dataset}` })
      if (!VALID_SPLITS.has(split))        return jsonResponse(res, 400, { error: `Invalid split: ${split}` })
      if (!VALID_ANNOTATIONS.has(annot1))  return jsonResponse(res, 400, { error: `Invalid annot1: ${annot1}` })
      if (!VALID_ANNOTATIONS.has(annot2))  return jsonResponse(res, 400, { error: `Invalid annot2: ${annot2}` })
      if (!VALID_LABELSETS.has(labelset))  return jsonResponse(res, 400, { error: `Invalid labelset: ${labelset}` })

      const filePath = dataPath(projectRoot, dataset, split, annot1, annot2, labelset)
      if (fs.existsSync(filePath)) {
        return jsonResponse(res, 200, JSON.parse(fs.readFileSync(filePath, 'utf-8')))
      }
      // Try reversed direction and transpose on-the-fly
      const reversedPath = dataPath(projectRoot, dataset, split, annot2, annot1, labelset)
      if (fs.existsSync(reversedPath)) {
        return jsonResponse(res, 200, transposeData(JSON.parse(fs.readFileSync(reversedPath, 'utf-8')), annot1, annot2))
      }
      return jsonResponse(res, 404, { error: 'not_built' })
    }

    return jsonResponse(res, 404, { error: 'Not found' })
  }
}
