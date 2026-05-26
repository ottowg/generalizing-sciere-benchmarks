/**
 * Production server for HuggingFace Spaces deployment.
 *
 * Serves the Vite-built frontend from dist/ and wires up all API
 * middleware handlers (the same ones used in vite.config.js dev mode).
 *
 * Usage:
 *   node webapp/server.js
 *
 * Environment:
 *   PORT  - listen port (default 7860, required by HF Spaces)
 */

import http from 'http'
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'
import yaml from 'js-yaml'

import { createLabelStatsMiddleware }    from './server/api/label_stats.js'
import { createCrossDatasetMiddleware }  from './server/api/cross_dataset.js'
import { createSamplesMiddleware }       from './server/api/samples.js'
import { createLookupMiddleware }        from './server/api/lookup.js'
import { createSignaturesMiddleware }    from './server/api/signatures.js'
import { createReproduceMiddleware }     from './server/api/reproduce.js'
import { createMultiSciEREMiddleware }   from './server/api/multi_sciere.js'
import { createExamplePaperMiddleware }      from './server/api/example_paper.js'
import { createPaperMetadataMiddleware }     from './server/api/paper_metadata.js'
import { createConfusionMatricesMiddleware } from './server/api/confusion_matrices.js'
import { createDomainShiftMiddleware }       from './server/api/domain_shift.js'
import { jsonResponse }                  from './server/utils.js'

const __dirname   = path.dirname(fileURLToPath(import.meta.url))
const projectRoot = path.resolve(__dirname, '..')
const distDir     = path.join(__dirname, 'dist')
const PORT        = process.env.PORT ?? 7860

// ── API route table ───────────────────────────────────────────────────────────

const apiHandlers = [
  ['/api/label-stats',    createLabelStatsMiddleware(projectRoot)],
  ['/api/cross-dataset',  createCrossDatasetMiddleware(projectRoot)],
  ['/api/samples',        createSamplesMiddleware(projectRoot)],
  ['/api/lookup',         createLookupMiddleware(projectRoot)],
  ['/api/signatures',     createSignaturesMiddleware(projectRoot)],
  ['/api/reproduce',      createReproduceMiddleware(projectRoot)],
  ['/api/multi-sciere',   createMultiSciEREMiddleware(projectRoot)],
  ['/api/example-paper',       createExamplePaperMiddleware(projectRoot)],
  ['/api/paper-metadata',      createPaperMetadataMiddleware(projectRoot)],
  ['/api/confusion-matrices',  createConfusionMatricesMiddleware(projectRoot)],
  ['/api/domain-shift',        createDomainShiftMiddleware(projectRoot)],
]

// ── Generic file-serving handlers (mirrored from vite.config.js) ─────────────

function handleFiles(res) {
  const list = (dir, prefix) => {
    if (!fs.existsSync(path.join(projectRoot, dir))) return []
    return fs.readdirSync(path.join(projectRoot, dir), { recursive: true })
      .filter(f => f.endsWith('.md'))
      .map(f => ({ name: f, path: `${dir}/${f}` }))
  }
  jsonResponse(res, 200, {
    docs:    list('docs',    'docs'),
    paper:   list('paper',   'paper'),
    reports: list('reports', 'reports'),
  })
}

function handleContent(req, res) {
  const filePath = new URL(req.url, 'http://x').searchParams.get('path')
  if (!filePath) { res.statusCode = 400; res.end('Missing path'); return }
  const full = path.resolve(projectRoot, filePath)
  if (!full.startsWith(projectRoot)) { res.statusCode = 403; res.end('Forbidden'); return }
  if (!fs.existsSync(full)) { res.statusCode = 404; res.end('Not found'); return }
  res.setHeader('Content-Type', 'text/plain; charset=utf-8')
  res.end(fs.readFileSync(full, 'utf-8'))
}

function handleJson(req, res) {
  const filePath = new URL(req.url, 'http://x').searchParams.get('path')
  if (!filePath) { res.statusCode = 400; res.end('Missing path'); return }
  const full = path.resolve(projectRoot, filePath)
  if (!full.startsWith(projectRoot)) { res.statusCode = 403; res.end('Forbidden'); return }
  if (!fs.existsSync(full)) { res.statusCode = 404; res.end('Not found'); return }
  res.setHeader('Content-Type', 'application/json; charset=utf-8')
  res.end(fs.readFileSync(full, 'utf-8'))
}

function handleYaml(req, res) {
  const filePath = new URL(req.url, 'http://x').searchParams.get('path')
  if (!filePath) { res.statusCode = 400; res.end('Missing path'); return }
  const full = path.resolve(projectRoot, filePath)
  if (!full.startsWith(projectRoot)) { res.statusCode = 403; res.end('Forbidden'); return }
  if (!fs.existsSync(full)) { res.statusCode = 404; res.end('Not found'); return }
  try {
    res.setHeader('Content-Type', 'application/json; charset=utf-8')
    res.end(JSON.stringify(yaml.load(fs.readFileSync(full, 'utf-8'))))
  } catch (e) { res.statusCode = 500; res.end(`YAML parse error: ${e.message}`) }
}

// ── MIME types for static files ───────────────────────────────────────────────

const MIME = {
  '.html': 'text/html', '.js': 'application/javascript',
  '.css': 'text/css', '.json': 'application/json',
  '.svg': 'image/svg+xml', '.png': 'image/png',
  '.ico': 'image/x-icon', '.woff': 'font/woff', '.woff2': 'font/woff2',
  '.ttf': 'font/ttf', '.eot': 'application/vnd.ms-fontobject',
}

// ── Request handler ───────────────────────────────────────────────────────────

const server = http.createServer((req, res) => {
  const urlPath = req.url.split('?')[0]

  // Generic API handlers
  if (urlPath === '/api/files') return handleFiles(res)
  if (urlPath.startsWith('/api/content')) return handleContent(req, res)
  if (urlPath.startsWith('/api/json'))    return handleJson(req, res)
  if (urlPath.startsWith('/api/yaml'))    return handleYaml(req, res)

  // Rebuild/regenerate endpoints — no-op in production (docker mode)
  if (req.method === 'POST' && (
    urlPath.endsWith('/build') || urlPath.startsWith('/api/regenerate')
  )) {
    return jsonResponse(res, 503, { ok: false, stderr: 'Rebuild not available in this deployment.' })
  }

  // Registered API middleware
  for (const [prefix, handler] of apiHandlers) {
    if (urlPath === prefix || urlPath.startsWith(prefix + '/') || urlPath.startsWith(prefix + '?')) {
      req.url = req.url.slice(prefix.length) || '/'
      return handler(req, res)
    }
  }

  // Static files from dist/ with SPA fallback
  let filePath = path.join(distDir, urlPath === '/' ? 'index.html' : urlPath)
  if (!fs.existsSync(filePath)) filePath = path.join(distDir, 'index.html')
  const ext = path.extname(filePath)
  res.setHeader('Content-Type', MIME[ext] ?? 'application/octet-stream')
  fs.createReadStream(filePath).on('error', () => {
    res.statusCode = 404; res.end('Not found')
  }).pipe(res)
})

server.listen(PORT, '0.0.0.0', () => {
  console.log(`UnifiedSciERE running on http://0.0.0.0:${PORT}`)
})
