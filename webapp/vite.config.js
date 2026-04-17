import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import fs from 'fs'
import path from 'path'
import { spawn } from 'child_process'
import yaml from 'js-yaml'
import { createReviewsMiddleware } from './server/api/reviews.js'
import { createSamplesMiddleware } from './server/api/samples.js'
import { createLookupMiddleware } from './server/api/lookup.js'
import { createSignaturesMiddleware } from './server/api/signatures.js'
import { createReproduceMiddleware }    from './server/api/reproduce.js'
import { createCrossDatasetMiddleware } from './server/api/cross_dataset.js'
import { createExamplePaperMiddleware }  from './server/api/example_paper.js'
import { createPaperMetadataMiddleware } from './server/api/paper_metadata.js'
import { createLabelStatsMiddleware }   from './server/api/label_stats.js'

const projectRoot = path.resolve(import.meta.dirname, '..')

function getMarkdownFiles(dir, base = '') {
  const result = []
  if (!fs.existsSync(dir)) return result
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const rel = base ? `${base}/${entry.name}` : entry.name
    if (entry.isDirectory()) {
      result.push(...getMarkdownFiles(path.join(dir, entry.name), rel))
    } else if (entry.name.endsWith('.md')) {
      result.push(rel)
    }
  }
  return result
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, projectRoot, '')
  const host = env.WEBAPP_HOST || 'localhost'

  return {
    server: {
      host,
      watch: {
        usePolling: true,
        interval: 500,
      },
    },
    plugins: [
      vue(),
      {
        name: 'markdown-api',
        configureServer(server) {
          server.middlewares.use('/api/files', (_req, res) => {
            const docs    = getMarkdownFiles(path.join(projectRoot, 'docs'))
            const paper   = getMarkdownFiles(path.join(projectRoot, 'paper'))
            const reports = getMarkdownFiles(path.join(projectRoot, 'reports'))
            res.setHeader('Content-Type', 'application/json')
            res.end(JSON.stringify({
              docs:    docs.map(f    => ({ name: f, path: `docs/${f}`    })),
              paper:   paper.map(f   => ({ name: f, path: `paper/${f}`   })),
              reports: reports.map(f => ({ name: f, path: `reports/${f}` })),
            }))
          })

          server.middlewares.use('/api/content', (req, res) => {
            const url = new URL(req.url, 'http://localhost')
            const filePath = url.searchParams.get('path')
            if (!filePath) { res.statusCode = 400; res.end('Missing path'); return }
            const fullPath = path.resolve(projectRoot, filePath)
            if (!fullPath.startsWith(projectRoot)) { res.statusCode = 403; res.end('Forbidden'); return }
            if (!fs.existsSync(fullPath)) { res.statusCode = 404; res.end('Not found'); return }
            res.setHeader('Content-Type', 'text/plain; charset=utf-8')
            res.setHeader('Cache-Control', 'no-store')
            res.end(fs.readFileSync(fullPath, 'utf-8'))
          })

          server.middlewares.use('/api/json', (req, res) => {
            const url = new URL(req.url, 'http://localhost')
            const filePath = url.searchParams.get('path')
            if (!filePath) { res.statusCode = 400; res.end('Missing path'); return }
            const fullPath = path.resolve(projectRoot, filePath)
            if (!fullPath.startsWith(projectRoot)) { res.statusCode = 403; res.end('Forbidden'); return }
            if (!fs.existsSync(fullPath)) { res.statusCode = 404; res.end('Not found'); return }
            res.setHeader('Content-Type', 'application/json; charset=utf-8')
            res.setHeader('Cache-Control', 'no-store')
            res.end(fs.readFileSync(fullPath, 'utf-8'))
          })

          server.middlewares.use('/api/yaml', (req, res) => {
            const url = new URL(req.url, 'http://localhost')
            const filePath = url.searchParams.get('path')
            if (!filePath) { res.statusCode = 400; res.end('Missing path'); return }
            const fullPath = path.resolve(projectRoot, filePath)
            if (!fullPath.startsWith(projectRoot)) { res.statusCode = 403; res.end('Forbidden'); return }
            if (!fs.existsSync(fullPath)) { res.statusCode = 404; res.end('Not found'); return }
            try {
              const parsed = yaml.load(fs.readFileSync(fullPath, 'utf-8'))
              res.setHeader('Content-Type', 'application/json; charset=utf-8')
              res.setHeader('Cache-Control', 'no-store')
              res.end(JSON.stringify(parsed))
            } catch (e) {
              res.statusCode = 500; res.end(`YAML parse error: ${e.message}`)
            }
          })

          // Registry of allowed regeneration scripts (report key → script path)
          const REGENERATE_SCRIPTS = {
            'quality-parenthesis':      'scripts/ere_confusion_analysis/analyze_parenthesized_mentions.py',
            'abbreviation-coverage':    'scripts/abbreviation/coverage_stats.py',
            'abbreviation-al-queue':    'scripts/abbreviation/build_al_queue.py',
            'unification':              'scripts/ere_confusion_analysis/generate_unification_overview.py',
          }

          // Streaming variant: GET /api/regenerate-stream?report=...&queue_size=20&sigma=0.15
          // Sends SSE events: { type: 'log'|'err'|'done'|'error', text: string }
          server.middlewares.use('/api/regenerate-stream', (req, res) => {
            const url = new URL(req.url, 'http://localhost')
            const report = url.searchParams.get('report')
            const script = REGENERATE_SCRIPTS[report]
            if (!script) { res.statusCode = 404; res.end(`Unknown report: ${report}`); return }

            const args = ['run', 'python', script]
            const queueSize = url.searchParams.get('queue_size')
            const sigma     = url.searchParams.get('sigma')
            if (queueSize) args.push('--queue-size', queueSize)
            if (sigma)     args.push('--sigma', sigma)

            res.setHeader('Content-Type', 'text/event-stream')
            res.setHeader('Cache-Control', 'no-cache')
            res.setHeader('Connection', 'keep-alive')
            res.flushHeaders()

            const send = (type, text) =>
              res.write(`data: ${JSON.stringify({ type, text })}\n\n`)

            let buf = ''
            const flushLines = (chunk, type) => {
              buf += chunk.toString()
              const lines = buf.split('\n')
              buf = lines.pop()           // keep incomplete last line
              for (const line of lines) if (line.trim()) send(type, line)
            }

            const proc = spawn('uv', args, { cwd: projectRoot })
            proc.stdout.on('data', d => flushLines(d, 'log'))
            proc.stderr.on('data', d => flushLines(d, 'err'))
            proc.on('close', code => {
              if (buf.trim()) send(code === 0 ? 'log' : 'err', buf)
              send(code === 0 ? 'done' : 'error', code === 0 ? 'Done.' : `Exit code ${code}`)
              res.end()
            })
            proc.on('error', err => { send('error', err.message); res.end() })
          })

          server.middlewares.use('/api/regenerate', (req, res) => {
            if (req.method !== 'POST') { res.statusCode = 405; res.end('Method Not Allowed'); return }
            const url = new URL(req.url, 'http://localhost')
            const report = url.searchParams.get('report')
            const script = REGENERATE_SCRIPTS[report]
            if (!script) { res.statusCode = 404; res.end(`Unknown report: ${report}`); return }

            const proc = spawn('uv', ['run', 'python', script], { cwd: projectRoot })
            const stdout = [], stderr = []
            proc.stdout.on('data', d => stdout.push(d))
            proc.stderr.on('data', d => stderr.push(d))
            proc.on('close', code => {
              res.setHeader('Content-Type', 'application/json')
              res.end(JSON.stringify({
                ok: code === 0,
                stdout: Buffer.concat(stdout).toString(),
                stderr: Buffer.concat(stderr).toString(),
              }))
            })
            proc.on('error', err => {
              res.statusCode = 500
              res.end(JSON.stringify({ ok: false, stderr: err.message }))
            })
          })

          // Return the set of already-annotated candidate IDs
          server.middlewares.use('/api/annotated-ids', (req, res) => {
            const filePath = path.join(projectRoot, 'data', 'abbreviation', 'annotations.jsonl')
            const ids = new Set()
            if (fs.existsSync(filePath)) {
              for (const line of fs.readFileSync(filePath, 'utf-8').split('\n')) {
                if (!line.trim()) continue
                try { ids.add(JSON.parse(line).id) } catch (_) {}
              }
            }
            res.setHeader('Content-Type', 'application/json')
            res.end(JSON.stringify([...ids]))
          })

          // Append one abbreviation annotation to annotations.jsonl
          server.middlewares.use('/api/annotate', (req, res) => {
            if (req.method !== 'POST') { res.statusCode = 405; res.end('Method Not Allowed'); return }
            let body = ''
            req.on('data', d => { body += d })
            req.on('end', () => {
              try {
                const { id, label, annotator } = JSON.parse(body)
                if (!id || label === undefined || !annotator) {
                  res.statusCode = 400; res.end('Missing id, label or annotator'); return
                }
                const record = JSON.stringify({
                  id,
                  label: Number(label),
                  annotator,
                  timestamp: new Date().toISOString(),
                }) + '\n'
                const filePath = path.join(projectRoot, 'data', 'abbreviation', 'annotations.jsonl')
                fs.mkdirSync(path.dirname(filePath), { recursive: true })
                fs.appendFileSync(filePath, record)
                res.setHeader('Content-Type', 'application/json')
                res.end(JSON.stringify({ ok: true }))
              } catch (e) {
                res.statusCode = 500; res.end(JSON.stringify({ ok: false, error: e.message }))
              }
            })
          })

          server.middlewares.use('/api/label-stats', createLabelStatsMiddleware(projectRoot))
          server.middlewares.use('/api/reviews', createReviewsMiddleware(projectRoot))
          server.middlewares.use('/api/samples', createSamplesMiddleware(projectRoot))
          server.middlewares.use('/api/lookup', createLookupMiddleware(projectRoot))
          server.middlewares.use('/api/signatures', createSignaturesMiddleware(projectRoot))
          server.middlewares.use('/api/reproduce',       createReproduceMiddleware(projectRoot))
          server.middlewares.use('/api/cross-dataset',  createCrossDatasetMiddleware(projectRoot))
          server.middlewares.use('/api/example-paper',    createExamplePaperMiddleware(projectRoot))
          server.middlewares.use('/api/paper-metadata',  createPaperMetadataMiddleware(projectRoot))
        },
      },
    ],
  }
})
