/**
 * MultiSciERE Results API
 *
 * GET /api/multi-sciere
 *   Returns data/multi_sciere_results.json
 *   Response: { generated_at, summary, labels, reported }
 *
 * POST /api/multi-sciere/build
 *   Runs scripts/ere_performance/multi_sciere_results_report.py via `uv run`.
 *   Response: { ok, stdout, stderr }
 */

import { execFileSync } from 'child_process'
import fs from 'fs'
import path from 'path'
import { jsonResponse } from '../utils.js'

const DATA_FILE = 'data/webapp/multi_sciere_results.json'
const SCRIPT    = 'scripts/ere_performance/multi_sciere_results_report.py'

export function createMultiSciEREMiddleware(projectRoot) {
  const dataPath = path.join(projectRoot, DATA_FILE)

  return async (req, res) => {
    const sub = req.url.replace(/^\//, '').split('?')[0]

    if (req.method === 'GET' && (!sub || sub === '')) {
      if (!fs.existsSync(dataPath)) {
        return jsonResponse(res, 404, { error: 'multi_sciere_results.json not found. Run POST /api/multi-sciere/build first.' })
      }
      return jsonResponse(res, 200, JSON.parse(fs.readFileSync(dataPath, 'utf-8')))
    }

    if (req.method === 'POST' && sub === 'build') {
      try {
        const output = execFileSync('uv', ['run', 'python', SCRIPT], {
          cwd: projectRoot,
          timeout: 600_000,
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
