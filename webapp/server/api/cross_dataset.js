/**
 * Cross-Dataset Performance API
 *
 * GET /api/cross-dataset
 *   Returns data/cross_dataset_performance.json
 *
 * POST /api/cross-dataset/build
 *   Runs scripts/ere_performance/cross_dataset_performance.py via `uv run`.
 */

import { execFileSync } from 'child_process'
import fs from 'fs'
import path from 'path'
import { jsonResponse } from '../utils.js'

const DATA_FILE = 'data/webapp/cross_dataset_performance.json'
const SCRIPT    = 'scripts/ere_performance/cross_dataset_performance.py'

export function createCrossDatasetMiddleware(projectRoot) {
  const dataPath = path.join(projectRoot, DATA_FILE)

  return async (req, res) => {
    const sub = req.url.replace(/^\//, '').split('?')[0]

    if (req.method === 'GET' && (!sub || sub === '')) {
      if (!fs.existsSync(dataPath)) {
        return jsonResponse(res, 404, { error: 'cross_dataset_performance.json not found. Run POST /api/cross-dataset/build first.' })
      }
      return jsonResponse(res, 200, JSON.parse(fs.readFileSync(dataPath, 'utf-8')))
    }

    if (req.method === 'POST' && sub === 'build') {
      try {
        const output = execFileSync('uv', ['run', 'python', SCRIPT], {
          cwd: projectRoot,
          timeout: 1_200_000,
          env: { ...process.env },
        })
        return jsonResponse(res, 200, { ok: true, stdout: output.toString(), stderr: '' })
      } catch (err) {
        return jsonResponse(res, 500, {
          ok: false,
          stdout: err.stdout?.toString() ?? '',
          stderr: err.stderr?.toString() ?? err.message,
        })
      }
    }

    return jsonResponse(res, 404, { error: 'Not found' })
  }
}
