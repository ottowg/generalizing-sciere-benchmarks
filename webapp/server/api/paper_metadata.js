/**
 * Paper Metadata API
 *
 * GET /api/paper-metadata
 *   Returns pre-built metadata aggregations from data/webapp_metadata.json.
 *   Response: the full JSON object
 *
 * POST /api/paper-metadata/build
 *   Runs scripts/paper_metadata/build_webapp_metadata.py via `uv run`.
 *   Response: { ok, stdout, stderr }
 */

import { execFileSync } from 'child_process'
import fs   from 'fs'
import path from 'path'
import { jsonResponse } from '../utils.js'

const DATA_FILE = 'data/webapp/static/webapp_metadata.json'
const SCRIPT    = 'scripts/paper_metadata/build_webapp_metadata.py'

export function createPaperMetadataMiddleware(projectRoot) {
  return (req, res) => {
    const url = new URL(req.url, 'http://localhost')
    const sub = url.pathname.replace(/^\/+/, '')   // '' or 'build'

    // POST /build
    if (req.method === 'POST' && sub === 'build') {
      try {
        const stdout = execFileSync('uv', ['run', 'python', SCRIPT], {
          cwd:      projectRoot,
          timeout:  180_000,
          encoding: 'utf-8',
        })
        return jsonResponse(res, 200, { ok: true, stdout })
      } catch (e) {
        return jsonResponse(res, 500, {
          ok:     false,
          stderr: e.stderr ?? e.message,
          stdout: e.stdout ?? '',
        })
      }
    }

    // GET
    if (req.method === 'GET') {
      const dataPath = path.join(projectRoot, DATA_FILE)
      if (!fs.existsSync(dataPath)) {
        return jsonResponse(res, 404, { error: 'not_built' })
      }
      const data = JSON.parse(fs.readFileSync(dataPath, 'utf-8'))
      return jsonResponse(res, 200, data)
    }

    jsonResponse(res, 405, { error: 'Method not allowed' })
  }
}
