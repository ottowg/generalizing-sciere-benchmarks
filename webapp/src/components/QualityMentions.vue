<template lang="pug">
v-container
  .d-flex.align-center.mb-4
    h2.text-h5 Annotation Reviews — Mentions
    v-spacer
    v-btn(
      variant="text"
      prepend-icon="mdi-database-sync-outline"
      :loading="globalBuilding"
      @click="buildAllLookups"
    ) Build Lookups
    v-btn.ml-2(color="primary" prepend-icon="mdi-plus" @click="openCreate") New Review

  NewReviewDialog(
    v-model="dialog"
    type="mentions"
    :review="editingReview"
    @create="onCreate"
    @update="onUpdate"
    @initialize="onInitialize"
  )

  v-list(v-if="mentionReviews.length" lines="two")
    v-list-item(
      v-for="r in mentionReviews"
      :key="r.id"
      :title="`${r.dataset} ← ${r.model}`"
      :subtitle="`${r.labelSet} · ${r.splits.join(', ')} · ${r.outcomes.join(', ')} · ${r.samplesPerLabel} samples`"
      prepend-icon="mdi-clipboard-list-outline"
    )
      template(#append)
        .d-flex.align-center.gap-1
          v-chip(
            size="small"
            class="mr-1"
            :color="r.samples?.length ? 'primary' : undefined"
            :prepend-icon="r.samples?.length ? 'mdi-lock-outline' : undefined"
            :title="r.samples?.length ? `${r.samples.length} samples locked` : 'Not initialized'"
          ) {{ annotatorProgress(r) }}

          //- Configure
          v-tooltip(text="Configure review" location="top")
            template(#activator="{ props: tip }")
              v-btn(
                v-bind="tip"
                size="small"
                variant="text"
                icon="mdi-pencil-outline"
                @click="openConfigure(r)"
              )

          v-divider(vertical class="mx-1")

          //- Start / Continue
          v-btn(
            size="small"
            :color="hasJudgements(r) ? 'primary' : 'success'"
            :prepend-icon="hasJudgements(r) ? 'mdi-play-circle' : 'mdi-play'"
            variant="tonal"
            :disabled="!isReady(r)"
            @click="openSession(r, hasJudgements(r) ? 'first-unjudged' : 'beginning')"
          ) {{ hasJudgements(r) ? 'Continue' : 'Start' }}

          v-tooltip(text="Restart from beginning" location="top")
            template(#activator="{ props: tip }")
              v-btn(
                v-bind="tip"
                v-if="hasJudgements(r)"
                size="small"
                variant="text"
                icon="mdi-restart"
                @click="openSession(r, 'beginning')"
              )

          v-tooltip(text="Delete review" location="top")
            template(#activator="{ props: tip }")
              v-btn(
                v-bind="tip"
                size="small"
                variant="text"
                color="error"
                icon="mdi-delete-outline"
                @click="confirmDelete(r)"
              )

  v-empty-state(
    v-else
    icon="mdi-clipboard-list-outline"
    title="No reviews yet"
    text="Create a review to start annotating."
  )

  v-snackbar(v-model="snackbar.show" :color="snackbar.color" timeout="5000")
    | {{ snackbar.message }}
    template(#actions)
      v-btn(variant="text" @click="snackbar.show = false") Close

  ReviewSession(
    v-if="activeReview"
    v-model="sessionOpen"
    :review="activeReview"
    :start-at="sessionStartAt"
    @close="activeReview = null"
  )

  v-dialog(v-model="deleteDialog" max-width="400")
    v-card(v-if="pendingDelete")
      v-card-title Delete review?
      v-card-text
        p.mb-3 This will permanently delete the review and cannot be undone.
        v-list(density="compact" bg-color="transparent")
          v-list-item(
            v-if="pendingDelete.samples?.length"
            prepend-icon="mdi-lock-outline"
            :title="`${pendingDelete.samples.length} locked samples will be lost`"
          )
          v-list-item(
            v-if="totalJudgements(pendingDelete) > 0"
            prepend-icon="mdi-comment-check-outline"
            :title="`${totalJudgements(pendingDelete)} judgement(s) from ${judgeCount(pendingDelete)} annotator(s)`"
            subtitle="All annotation work will be deleted"
          )
          v-list-item(
            v-if="totalJudgements(pendingDelete) === 0 && !pendingDelete.samples?.length"
            prepend-icon="mdi-information-outline"
            title="No annotation data to lose"
          )
      v-card-actions
        v-spacer
        v-btn(variant="text" @click="deleteDialog = false") Cancel
        v-btn(color="error" variant="tonal" @click="doDelete") Delete
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import NewReviewDialog from './NewReviewDialog.vue'
import ReviewSession from './ReviewSession.vue'
import { useReviews, deleteReview, updateReview, fetchSampleCount, fetchSamples } from '../composables/useReviews.js'
import { useAnnotator } from '../composables/useAnnotator.js'

const dialog        = ref(false)
const editingReview = ref(null)
const snackbar      = ref({ show: false, message: '', color: 'success' })

const { reviews, fetchReviews, createReview } = useReviews()
const { annotator } = useAnnotator()
const mentionReviews = computed(() => reviews.value.filter(r => r.type === 'mentions'))

// ── lookup ────────────────────────────────────────────────────────────────────
const globalBuilding = ref(false)

async function buildAllLookups() {
  globalBuilding.value = true
  try {
    const res  = await fetch('/api/lookup/build', { method: 'POST' })
    const data = await res.json()
    snackbar.value = data.ok
      ? { show: true, message: 'Lookup data built successfully.', color: 'success' }
      : { show: true, message: `Build failed: ${data.error}`, color: 'error' }
  } catch (e) {
    snackbar.value = { show: true, message: `Build error: ${e.message}`, color: 'error' }
  } finally {
    globalBuilding.value = false
  }
}

// ── sample totals ─────────────────────────────────────────────────────────────
const sampleTotals = ref({})

async function loadCounts(reviewList) {
  const results = await Promise.allSettled(
    reviewList.map(r => fetchSampleCount(r).then(data => ({ id: r.id, total: data.total ?? 0 })))
  )
  for (const r of results) {
    if (r.status === 'fulfilled') sampleTotals.value[r.value.id] = r.value.total
  }
}

onMounted(async () => {
  await fetchReviews()
  if (mentionReviews.value.length) loadCounts(mentionReviews.value)
})

// ── create / configure ────────────────────────────────────────────────────────
function openCreate() {
  editingReview.value = null
  dialog.value = true
}

function openConfigure(review) {
  editingReview.value = review
  dialog.value = true
}

async function onCreate(config) {
  const review = await createReview({ ...config, type: 'mentions' })
  fetchSampleCount(review).then(data => { sampleTotals.value[review.id] = data.total ?? 0 })
}

async function onUpdate(config) {
  const review = await updateReview(editingReview.value.id, config)
  editingReview.value = null
  fetchSampleCount(review).then(data => { sampleTotals.value[review.id] = data.total ?? 0 })
}

async function onInitialize(config) {
  const fullConfig = { ...config, type: 'mentions' }
  let review = editingReview.value
    ? await updateReview(editingReview.value.id, fullConfig)
    : await createReview(fullConfig)
  editingReview.value = null

  snackbar.value = { show: true, message: 'Fetching samples…', color: 'info' }
  try {
    const { samples } = await fetchSamples(review)
    review = await updateReview(review.id, { samples })
    sampleTotals.value[review.id] = samples.length
    snackbar.value = { show: true, message: `Initialized: ${samples.length} samples locked in.`, color: 'success' }
  } catch (e) {
    snackbar.value = { show: true, message: `Failed to initialize: ${e.message}`, color: 'error' }
  }
}

// ── session ───────────────────────────────────────────────────────────────────
const sessionOpen    = ref(false)
const activeReview   = ref(null)
const sessionStartAt = ref('first-unjudged')

function isReady(_review) {
  return true
}

function openSession(review, startAt) {
  activeReview.value   = review
  sessionStartAt.value = startAt
  sessionOpen.value    = true
}

// ── progress ──────────────────────────────────────────────────────────────────
function hasJudgements(review) {
  if (!annotator.value) return false
  return Object.values(review.judgements ?? {}).some(j => j[annotator.value])
}

function annotatorProgress(review) {
  const judged = annotator.value
    ? Object.values(review.judgements ?? {}).filter(j => j[annotator.value]).length
    : 0
  const total = review.samples?.length ?? sampleTotals.value[review.id]
  if (total == null) return `${judged} judged`
  const open = total - judged
  return open > 0 ? `${open} open · ${judged} judged` : `${judged} / ${total} done`
}

// ── delete ────────────────────────────────────────────────────────────────────
const deleteDialog  = ref(false)
const pendingDelete = ref(null)

function totalJudgements(review) {
  return Object.values(review.judgements ?? {}).reduce((sum, j) => sum + Object.keys(j).length, 0)
}

function judgeCount(review) {
  const annotators = new Set()
  for (const j of Object.values(review.judgements ?? {})) Object.keys(j).forEach(a => annotators.add(a))
  return annotators.size
}

function confirmDelete(review) {
  pendingDelete.value = review
  deleteDialog.value  = true
}

async function doDelete() {
  await deleteReview(pendingDelete.value.id)
  deleteDialog.value  = false
  pendingDelete.value = null
}
</script>
