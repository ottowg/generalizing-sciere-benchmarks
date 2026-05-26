/**
 * Relation Signatures API
 *
 * GET /api/signatures
 *   Returns the full relation_signatures.json data array.
 *   Response: { rows: [...], groups, allowed, meta: { datasets, models, splits, label_sets } }
 *   allowed: { <dataset>: { allowed: [[s,r,o],...], wrong_direction: [[s,r,o],...] }, ... }
 *
 * POST /api/signatures/build
 *   Triggers scripts/ere_quality/relation_signatures.py via `uv run`.
 *   Response: { ok, stdout, stderr }
 */

import { execFileSync } from 'child_process'
import fs from 'fs'
import path from 'path'
import yaml from 'js-yaml'
import { jsonResponse } from '../utils.js'

const DATA_FILE     = 'data/webapp/relation_signatures.json'
const GROUPS_FILE   = 'data/webapp/semantic_groups.json'
const ALLOWED_FILE  = 'data/webapp/allowed_signatures.yaml'
const SCRIPT        = 'scripts/ere_quality/relation_signatures.py'

/**
 * Flatten the nested YAML structure { subj: { rel: { obj: null } } }
 * into an array of [subj, rel, obj] triples.
 */
function flattenNested(nested) {
  if (!nested) return []
  const out = []
  for (const [subj, rels] of Object.entries(nested)) {
    for (const [rel, objs] of Object.entries(rels ?? {})) {
      for (const obj of Object.keys(objs ?? {})) {
        out.push([subj, rel, obj])
      }
    }
  }
  return out
}

/**
 * Parse allowed_signatures.yaml and return a flat representation:
 *   { <dataset>: { allowed: [[s,r,o],...], wrong_direction: [[s,r,o],...] } }
 */
function loadAllowed(allowedPath) {
  if (!fs.existsSync(allowedPath)) return {}
  const doc = yaml.load(fs.readFileSync(allowedPath, 'utf-8')) ?? {}
  const out = {}
  for (const [dataset, sections] of Object.entries(doc)) {
    out[dataset] = {
      allowed:         flattenNested(sections?.allowed),
      wrong_direction: flattenNested(sections?.wrong_direction),
    }
  }
  return out
}

export function createSignaturesMiddleware(projectRoot) {
  const dataPath    = path.join(projectRoot, DATA_FILE)
  const groupsPath  = path.join(projectRoot, GROUPS_FILE)
  const allowedPath = path.join(projectRoot, ALLOWED_FILE)

  return async (req, res) => {
    const sub = req.url.replace(/^\//, '').split('?')[0]

    // GET / — serve the data
    if (req.method === 'GET' && (!sub || sub === '')) {
      if (!fs.existsSync(dataPath)) {
        return jsonResponse(res, 404, { error: 'relation_signatures.json not found. Run POST /api/signatures/build first.' })
      }
      const rows   = JSON.parse(fs.readFileSync(dataPath, 'utf-8'))
      const groups = fs.existsSync(groupsPath)
        ? JSON.parse(fs.readFileSync(groupsPath, 'utf-8'))
        : { entity_groups: {}, relation_groups: {} }
      const allowed = loadAllowed(allowedPath)
      const uniq = key => [...new Set(rows.map(r => r[key]))].sort()
      return jsonResponse(res, 200, {
        rows,
        groups,
        allowed,
        meta: {
          datasets:   uniq('dataset'),
          models:     uniq('model'),
          splits:     uniq('split'),
          label_sets: uniq('label_set'),
        },
      })
    }

    // POST /build — regenerate
    if (req.method === 'POST' && sub === 'build') {
      try {
        const output = execFileSync('uv', ['run', 'python', SCRIPT], {
          cwd: projectRoot,
          timeout: 300_000,
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
