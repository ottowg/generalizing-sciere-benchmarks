/**
 * Samples API — serves annotation review samples from pre-built lookup files.
 *
 * GET /api/samples
 *   ?trained_on=gsap
 *   &dataset=scier
 *   &splits=dev,test          (comma-separated, one or more)
 *   &type=mentions            (mentions | relations)
 *   &outcomes=fp,fn           (comma-separated subset of tp, fp, fn)
 *   &samplesPerLabel=20       (max samples returned per label+split+outcome combination)
 *   &sampling=random          (random | score)
 *   &label=Method             (optional: restrict to a single label)
 *
 * Response:
 * {
 *   samples: [ { id, outcome, label, score, text|subject/object, sentence, doc_id, sent_idx, ... } ],
 *   counts:  { "<label>": { tp: N, fp: N, fn: N } }   // totals before sampling
 * }
 *
 * Lookup files are read from <projectRoot>/data/annotation_lookup/{trained_on}_{dataset}_{split}[_unified].json
 * and are produced by scripts/ere_performance/build_annotation_lookup.py.
 */

import fs from 'fs'
import path from 'path'
import { jsonResponse, shuffle } from '../utils.js'

const LOOKUP_DIR = 'data/annotation_lookup'

function lookupFileName(trained_on, dataset, split, labelSet) {
  const suffix = labelSet === 'unified' ? '_unified' : ''
  return `${trained_on}_${dataset}_${split}${suffix}.json`
}

function loadLookup(projectRoot, trained_on, dataset, split, labelSet) {
  const filePath = path.join(projectRoot, LOOKUP_DIR, lookupFileName(trained_on, dataset, split, labelSet))
  if (!fs.existsSync(filePath)) return null
  return JSON.parse(fs.readFileSync(filePath, 'utf-8'))
}

/**
 * Sample up to n items per (label, outcome) bucket.
 * strategy = 'random' | 'score'
 *   - random: shuffle, take first n
 *   - score:  sort by score desc (high-confidence predictions first), take first n
 */
function sampleBucket(items, n, strategy) {
  if (strategy === 'score') {
    return [...items].sort((a, b) => b.score - a.score).slice(0, n)
  }
  return shuffle([...items]).slice(0, n)
}

export function createSamplesMiddleware(projectRoot) {
  return (req, res) => {
    if (req.method !== 'GET') return jsonResponse(res, 405, { error: 'Method not allowed' })

    const url = new URL(req.url, 'http://localhost')
    const p = url.searchParams

    const trained_on      = p.get('trained_on')
    const dataset         = p.get('dataset')
    const splitsParam     = p.get('splits')
    const type            = p.get('type')           // 'mentions' | 'relations'
    const outcomesParam   = p.get('outcomes')        // 'tp,fp,fn'
    const samplesPerLabel = parseInt(p.get('samplesPerLabel') || '20', 10)
    const sampling        = p.get('sampling') || 'random'
    const labelSet        = p.get('labelSet') || 'original'
    const labelFilter     = p.get('label') || null   // single-label override (e.g. from fetchSamples)
    const labelsParam     = p.get('labels')           // multi-label filter from review config
    const labelsFilter    = labelsParam ? new Set(labelsParam.split(',').map(s => s.trim()).filter(Boolean)) : null
    const countOnly       = p.get('countOnly') === 'true'

    if (!trained_on || !dataset || !splitsParam || !type || !outcomesParam) {
      return jsonResponse(res, 400, { error: 'Missing required params: trained_on, dataset, splits, type, outcomes' })
    }

    const splits   = splitsParam.split(',').map(s => s.trim()).filter(Boolean)
    const outcomes = new Set(outcomesParam.split(',').map(s => s.trim()).filter(Boolean))

    // Collect all matching samples across requested splits
    const allSamples = []
    const missing = []

    for (const split of splits) {
      const lookup = loadLookup(projectRoot, trained_on, dataset, split, labelSet)
      if (!lookup) { missing.push(lookupFileName(trained_on, dataset, split, labelSet).replace('.json', '')); continue }
      const items = lookup[type] ?? []
      for (const item of items) {
        if (!outcomes.has(item.outcome)) continue
        if (labelFilter && item.label !== labelFilter) continue
        if (labelsFilter && !labelsFilter.has(item.label)) continue
        allSamples.push(item)
      }
    }

    // Count totals per label+outcome before sampling (for display)
    const counts = {}
    for (const item of allSamples) {
      counts[item.label] ??= { tp: 0, fp: 0, fn: 0 }
      counts[item.label][item.outcome] = (counts[item.label][item.outcome] ?? 0) + 1
    }

    // Group by (label, split, outcome) — sampling unit
    const buckets = {}
    for (const item of allSamples) {
      const key = `${item.label}||${item.split ?? ''}||${item.outcome}`
      buckets[key] ??= []
      buckets[key].push(item)
    }

    // Total after sampling = sum of min(bucketSize, samplesPerLabel)
    const total = Object.values(buckets).reduce((sum, b) => sum + Math.min(b.length, samplesPerLabel), 0)

    if (countOnly) {
      return jsonResponse(res, 200, { total, counts, missing: missing.length ? missing : undefined })
    }

    const samples = Object.values(buckets).flatMap(bucket =>
      sampleBucket(bucket, samplesPerLabel, sampling)
    )

    jsonResponse(res, 200, { samples, counts, total, missing: missing.length ? missing : undefined })
  }
}
