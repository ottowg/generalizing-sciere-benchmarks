/**
 * Example Paper API
 *
 * GET /api/example-paper?dataset=gsap-ere
 *   Returns pre-built papers for the given dataset (or all datasets if omitted).
 *   Response: { papers: [{ doc_id, dataset, sentences, gold, predicted }] }
 *
 * POST /api/example-paper/build
 *   Runs scripts/ere_quality/build_example_papers.py via `uv run`.
 *   Response: { ok, stdout, stderr }
 */

import { execFileSync } from 'child_process'
import fs   from 'fs'
import path from 'path'
import { jsonResponse } from '../utils.js'

const DATA_FILE = 'data/example_papers.json'
const SCRIPT    = 'scripts/ere_quality/build_example_papers.py'

export function createExamplePaperMiddleware(projectRoot) {
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
      const data    = JSON.parse(fs.readFileSync(dataPath, 'utf-8'))
      const dataset = url.searchParams.get('dataset')
      const papers  = dataset
        ? (data.papers?.[dataset] ?? [])
        : Object.values(data.papers ?? {}).flat()
      return jsonResponse(res, 200, { papers })
    }

    jsonResponse(res, 405, { error: 'Method not allowed' })
  }
}
