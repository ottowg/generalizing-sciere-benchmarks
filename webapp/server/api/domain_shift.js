/**
 * Domain-Shift Auxiliary Transfer Results API
 *
 * GET /api/domain-shift
 *   Returns data/webapp/domain_shift_results.json
 *
 * POST /api/domain-shift/build
 *   Runs scripts/ere_performance/domain_shift_results_report.py via `uv run`.
 *   Response: { ok, stdout, stderr }
 */

import { execFileSync } from 'child_process'
import fs   from 'fs'
import path from 'path'
import { jsonResponse } from '../utils.js'

const DATA_FILE = 'data/webapp/domain_shift_results.json'
const SCRIPT    = 'scripts/ere_performance/domain_shift_results_report.py'

export function createDomainShiftMiddleware(projectRoot) {
  const dataPath = path.join(projectRoot, DATA_FILE)

  return (req, res) => {
    const sub = req.url.replace(/^\//, '').split('?')[0]

    if (req.method === 'GET' && (!sub || sub === '')) {
      if (!fs.existsSync(dataPath)) {
        return jsonResponse(res, 404, { error: 'domain_shift_results.json not found. Run POST /api/domain-shift/build first.' })
      }
      return jsonResponse(res, 200, JSON.parse(fs.readFileSync(dataPath, 'utf-8')))
    }

    if (req.method === 'POST' && sub === 'build') {
      try {
        const stdout = execFileSync('uv', ['run', 'python', SCRIPT], {
          cwd:      projectRoot,
          timeout:  600_000,
          env:      { ...process.env },
          encoding: 'utf-8',
        })
        return jsonResponse(res, 200, { ok: true, stdout, stderr: '' })
      } catch (err) {
        return jsonResponse(res, 500, {
          ok:     false,
          stdout: err.stdout ?? '',
          stderr: err.stderr ?? err.message,
        })
      }
    }

    return jsonResponse(res, 404, { error: 'Not found' })
  }
}
