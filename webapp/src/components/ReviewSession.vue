<template lang="pug">
v-dialog(v-model="open" max-width="820" scrollable)
  v-card

    //- Header
    v-toolbar(color="primary" density="compact")
      v-btn(icon="mdi-close" @click="open = false")
      v-toolbar-title {{ review.dataset }} ← {{ review.model }} &nbsp;
        v-chip(size="x-small" label variant="tonal") {{ review.type }}
      v-spacer
      .text-caption.mr-4(v-if="samples.length")
        | {{ judgedCount }} / {{ samples.length }} judged
      v-progress-linear(
        v-if="samples.length"
        :model-value="(judgedCount / samples.length) * 100"
        color="white"
        bg-color="rgba(255,255,255,0.3)"
        style="position: absolute; bottom: 0; left: 0; right: 0"
      )

    //- Loading / empty
    v-card-text.d-flex.align-center.justify-center(v-if="loading" style="min-height: 200px")
      v-progress-circular(indeterminate color="primary")

    v-card-text.d-flex.align-center.justify-center(v-else-if="!samples.length" style="min-height: 200px")
      v-empty-state(icon="mdi-text-box-check-outline" title="No samples" text="No samples match the current review configuration.")

    //- Annotation area
    v-card-text(v-else)
      .d-flex.align-center.mb-3
        v-chip.mr-2(:color="outcomeColor(current.outcome)" label size="small") {{ current.outcome.toUpperCase() }}
        span.text-caption.text-medium-emphasis score: {{ current.score }}
        v-spacer
        span.text-caption.text-medium-emphasis {{ currentIndex + 1 }} / {{ samples.length }}

      SentenceView(:sample="current")

      //- Previous judgement note (if any)
      v-alert.mt-4(
        v-if="previousJudgement?.note"
        type="info"
        variant="tonal"
        density="compact"
      ) Note: {{ previousJudgement.note }}

      //- Verdict form
      .mt-5
        VerdictForm(
          :key="currentIndex"
          :type="review.type"
          :previous="previousJudgement"
          :entity-labels="entityLabels"
          :relation-labels="relationLabels"
          v-model="currentJudgement"
        )

      v-textarea.mt-4(
        v-model="note"
        label="Note (optional)"
        variant="outlined"
        density="compact"
        rows="2"
        auto-grow
        hide-details
      )

      //- Navigation
      .d-flex.align-center.mt-4.gap-3
        v-btn(
          variant="text"
          prepend-icon="mdi-chevron-left"
          :disabled="currentIndex === 0"
          @click="navigate(-1)"
        ) Prev

        v-spacer

        v-btn(
          color="primary"
          variant="tonal"
          append-icon="mdi-chevron-right"
          :disabled="!currentJudgement"
          @click="submitAndNext"
          :loading="saving"
        ) {{ isLast ? 'Save & finish' : 'Save & next' }}

        v-btn(
          variant="text"
          append-icon="mdi-chevron-right"
          @click="navigate(1)"
          :disabled="isLast"
        ) Skip
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import SentenceView from './SentenceView.vue'
import VerdictForm from './VerdictForm.vue'
import { fetchSamples, recordJudgement } from '../composables/useReviews.js'
import { useAnnotator } from '../composables/useAnnotator.js'

const props = defineProps({
  review:  { type: Object, required: true },
  startAt: { type: String, default: 'first-unjudged' },
})

const emit = defineEmits(['close'])

const open = defineModel({ type: Boolean })
watch(open, v => { if (!v) emit('close') })

const { annotator } = useAnnotator()

// ── data ──────────────────────────────────────────────────────────────────────
const samples      = ref([])
const loading      = ref(false)
const saving       = ref(false)
const currentIndex = ref(0)

const current  = computed(() => samples.value[currentIndex.value])
const isLast   = computed(() => currentIndex.value === samples.value.length - 1)

const judgedCount = computed(() =>
  samples.value.filter(s => props.review.judgements?.[s.id]?.[annotator.value]).length
)

const previousJudgement = computed(() =>
  current.value ? props.review.judgements?.[current.value.id]?.[annotator.value] : null
)

// ── verdict state ──────────────────────────────────────────────────────────────
const currentJudgement = ref(null)
const note = ref('')

watch(currentIndex, () => {
  note.value = previousJudgement.value?.note ?? ''
})

const entityLabels = computed(() => {
  const labels = new Set()
  for (const s of samples.value) {
    if (s.subject?.label) labels.add(s.subject.label)
    if (s.object?.label)  labels.add(s.object.label)
    if (!s.subject && s.label) labels.add(s.label)  // mention sample
  }
  return [...labels].sort()
})

const relationLabels = computed(() => {
  const labels = new Set()
  for (const s of samples.value) {
    if (s.label) labels.add(s.label)
  }
  return [...labels].sort()
})

// ── load ──────────────────────────────────────────────────────────────────────
async function load() {
  loading.value = true
  try {
    const data = props.review.samples?.length
      ? props.review.samples
      : (await fetchSamples(props.review)).samples ?? []
    samples.value = data
    if (props.startAt === 'first-unjudged') {
      const firstUnjudged = samples.value.findIndex(
        s => !props.review.judgements?.[s.id]?.[annotator.value]
      )
      currentIndex.value = firstUnjudged >= 0 ? firstUnjudged : 0
    } else {
      currentIndex.value = 0
    }
    note.value = previousJudgement.value?.note ?? ''
  } finally {
    loading.value = false
  }
}

watch(open, v => { if (v) load() }, { immediate: true })

// ── navigation & saving ───────────────────────────────────────────────────────
function navigate(delta) {
  const next = currentIndex.value + delta
  if (next >= 0 && next < samples.value.length) currentIndex.value = next
}

async function submitAndNext() {
  if (!currentJudgement.value || !annotator.value) return
  saving.value = true
  try {
    const judgement = {
      ...currentJudgement.value,
      note:     note.value.trim(),
      judgedAt: new Date().toISOString(),
    }
    await recordJudgement(props.review.id, current.value.id, annotator.value, judgement)
    if (!props.review.judgements[current.value.id]) props.review.judgements[current.value.id] = {}
    props.review.judgements[current.value.id][annotator.value] = judgement
    if (isLast.value) open.value = false
    else navigate(1)
  } finally {
    saving.value = false
  }
}

// ── helpers ───────────────────────────────────────────────────────────────────
function outcomeColor(outcome) {
  return { tp: 'success', fp: 'error', fn: 'warning' }[outcome] ?? 'grey'
}
</script>
