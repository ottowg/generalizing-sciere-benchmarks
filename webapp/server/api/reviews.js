import fs from 'fs'
import path from 'path'
import { randomUUID } from 'crypto'
import { jsonResponse, readBody } from '../utils.js'

export function createReviewsMiddleware(projectRoot) {
  const reviewsPath = path.join(projectRoot, 'data', 'webapp', 'reviews.json')

  function read() {
    if (!fs.existsSync(reviewsPath)) return []
    return JSON.parse(fs.readFileSync(reviewsPath, 'utf-8'))
  }

  function write(reviews) {
    fs.writeFileSync(reviewsPath, JSON.stringify(reviews, null, 2))
  }

  // GET  /api/reviews        → list all
  // POST /api/reviews        → create
  // PATCH /api/reviews/:id   → update (merge judgements or fields)
  // DELETE /api/reviews/:id  → delete
  return async (req, res) => {
    const id = req.url.replace(/^\//, '').split('?')[0] || null

    try {
      if (req.method === 'GET') {
        jsonResponse(res, 200, read())

      } else if (req.method === 'POST' && !id) {
        const body = await readBody(req)
        const review = { id: randomUUID(), createdAt: new Date().toISOString(), judgements: {}, ...body }
        const reviews = read()
        reviews.push(review)
        write(reviews)
        jsonResponse(res, 201, review)

      } else if (req.method === 'PATCH' && id) {
        const body = await readBody(req)
        const reviews = read()
        const idx = reviews.findIndex(r => r.id === id)
        if (idx === -1) return jsonResponse(res, 404, { error: 'Not found' })
        // Deep-merge judgements: { [sampleId]: { [annotator]: judgement } }
        const merged = { ...reviews[idx].judgements }
        for (const [sampleId, annotatorJudgements] of Object.entries(body.judgements ?? {})) {
          merged[sampleId] = { ...merged[sampleId], ...annotatorJudgements }
        }
        reviews[idx] = { ...reviews[idx], ...body, id, judgements: merged }
        write(reviews)
        jsonResponse(res, 200, reviews[idx])

      } else if (req.method === 'DELETE' && id) {
        const reviews = read()
        const idx = reviews.findIndex(r => r.id === id)
        if (idx === -1) return jsonResponse(res, 404, { error: 'Not found' })
        reviews.splice(idx, 1)
        write(reviews)
        jsonResponse(res, 204, {})

      } else {
        jsonResponse(res, 405, { error: 'Method not allowed' })
      }
    } catch (e) {
      jsonResponse(res, 500, { error: e.message })
    }
  }
}
