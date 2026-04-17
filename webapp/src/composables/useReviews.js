import { ref } from 'vue'

/**
 * Fetch annotation samples for a review config.
 * review must have: model (trained_on), dataset, splits[], outcomes[], type, samplesPerLabel, sampling
 * Returns { samples, counts }
 */
function reviewParams(review) {
  const params = new URLSearchParams({
    trained_on:      review.model,
    dataset:         review.dataset,
    splits:          review.splits.join(','),
    type:            review.type,
    outcomes:        review.outcomes.join(','),
    samplesPerLabel: review.samplesPerLabel,
    sampling:        review.sampling,
    labelSet:        review.labelSet ?? 'original',
  })
  if (review.labels?.length) params.set('labels', review.labels.join(','))
  return params
}

export async function fetchSampleCount(review) {
  const params = reviewParams(review)
  params.set('countOnly', 'true')
  const res = await fetch(`/api/samples?${params}`)
  return res.json()  // { total, counts }
}

export async function fetchSamples(review, { label = null } = {}) {
  const params = reviewParams(review)
  if (label) params.set('label', label)
  const res = await fetch(`/api/samples?${params}`)
  return res.json()
}


const reviews = ref([])

async function fetchReviews() {
  const res = await fetch('/api/reviews')
  reviews.value = await res.json()
}

async function createReview(config) {
  const res = await fetch('/api/reviews', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  })
  const review = await res.json()
  reviews.value.push(review)
  return review
}

// judgements are nested: { [sampleId]: { [annotator]: { verdict, note } } }
async function recordJudgement(reviewId, sampleId, annotator, judgement) {
  const res = await fetch(`/api/reviews/${reviewId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ judgements: { [sampleId]: { [annotator]: judgement } } }),
  })
  const updated = await res.json()
  const idx = reviews.value.findIndex(r => r.id === reviewId)
  if (idx !== -1) reviews.value[idx] = updated
  return updated
}

async function deleteReview(reviewId) {
  await fetch(`/api/reviews/${reviewId}`, { method: 'DELETE' })
  reviews.value = reviews.value.filter(r => r.id !== reviewId)
}

async function updateReview(reviewId, config) {
  const res = await fetch(`/api/reviews/${reviewId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  })
  const updated = await res.json()
  const idx = reviews.value.findIndex(r => r.id === reviewId)
  if (idx !== -1) reviews.value[idx] = updated
  return updated
}

export { recordJudgement, deleteReview, updateReview }

export function useReviews() {
  return { reviews, fetchReviews, createReview, updateReview, recordJudgement, deleteReview }
}
