/**
 * Lookup build API
 *
 * POST /api/lookup/build
 *   Body (optional): { trained_on, dataset, splits }
 *   Runs build_annotation_lookup.py via `uv run`.
 *   If trained_on/dataset/splits are provided, sets env vars so the script
 *   can filter to just those combinations (falls back to full build otherwise).
 *
 * GET /api/lookup/status
 *   Returns which lookup files currently exist.
 */

import { execFileSync } from 'child_process'
import fs from 'fs'
import path from 'path'
import { jsonResponse, readBody } from '../utils.js'

const LOOKUP_DIR = 'data/annotation_lookup'
const SCRIPT = 'scripts/ere_performance/build_annotation_lookup.py'

export function createLookupMiddleware(projectRoot) {
  const lookupDir = path.join(projectRoot, LOOKUP_DIR)

  return async (req, res) => {
    const sub = req.url.replace(/^\//, '').split('?')[0]

    if (req.method === 'GET' && sub === 'status') {
      const files = fs.existsSync(lookupDir)
        ? fs.readdirSync(lookupDir).filter(f => f.endsWith('.json')).sort()
        : []
      return jsonResponse(res, 200, { files })
    }

    if (req.method === 'POST' && sub === 'build') {
      let filter = {}
      try { filter = await readBody(req) } catch { /* body is optional */ }

      const env = {
        ...process.env,
        ...(filter.trained_on  ? { BUILD_TRAINED_ON: filter.trained_on  } : {}),
        ...(filter.dataset     ? { BUILD_DATASET:    filter.dataset     } : {}),
        ...(filter.splits      ? { BUILD_SPLITS:     filter.splits.join(',') } : {}),
      }

      try {
        const output = execFileSync('uv', ['run', SCRIPT], {
          cwd: projectRoot,
          env,
          timeout: 300_000,
          encoding: 'utf-8',
        })
        return jsonResponse(res, 200, { ok: true, output })
      } catch (e) {
        return jsonResponse(res, 500, { ok: false, error: e.message, output: e.stdout ?? '' })
      }
    }

    jsonResponse(res, 404, { error: 'Not found' })
  }
}
