<template lang="pug">
v-dialog(v-model="open" max-width="820" scrollable)
  v-card
    //- Header
    v-toolbar(color="primary" density="compact")
      v-btn(icon="mdi-close" @click="open = false")
      v-toolbar-title Abbreviation Annotation Queue
      v-spacer
      .text-caption.mr-4(v-if="activeItems.length")
        | {{ activeAnnotated }} / {{ activeItems.length }} annotated
      v-progress-linear(
        v-if="activeItems.length"
        :model-value="activeItems.length ? (activeAnnotated / activeItems.length) * 100 : 0"
        color="white"
        bg-color="rgba(255,255,255,0.3)"
        style="position:absolute;bottom:0;left:0;right:0"
      )

    //- Subtask tabs
    v-tabs(
      v-if="!loading"
      v-model="subtask"
      color="primary"
      density="compact"
      bg-color="surface"
    )
      v-tab(value="A")
        | Subtask A
        v-chip(size="x-small" class="ml-2" :color="uncertainA.length ? 'primary' : 'default'" variant="tonal") {{ uncertainA.length }}
        v-chip(v-if="verifyA.length" size="x-small" class="ml-1" color="warning" variant="tonal") {{ verifyA.length }}
      v-tab(value="B")
        | Subtask B
        v-chip(size="x-small" class="ml-2" :color="uncertainB.length ? 'primary' : 'default'" variant="tonal") {{ uncertainB.length }}
        v-chip(v-if="verifyB.length" size="x-small" class="ml-1" color="warning" variant="tonal") {{ verifyB.length }}

    //- Loading
    v-card-text.d-flex.align-center.justify-center(v-if="loading" style="min-height:200px")
      v-progress-circular(indeterminate color="primary")

    //- Empty subtask
    v-card-text.d-flex.align-center.justify-center(v-else-if="!activeItems.length" style="min-height:200px")
      v-empty-state(
        icon="mdi-check-circle-outline"
        title="Queue is empty"
        text="No candidates in queue for this subtask. Rebuild the queue first."
      )

    //- Annotation area
    v-card-text(v-else-if="current")
      //- Metadata chips
      .d-flex.flex-wrap.gap-2.mb-3
        v-chip(
          v-if="current.queue_reason === 'verify_positive'"
          label size="small" color="warning" variant="tonal"
          prepend-icon="mdi-alert-circle-outline"
        ) Verify positive
        v-chip(label size="small" variant="tonal") {{ current.dataset }} / {{ current.split }}
        v-chip(label size="small" variant="tonal" color="orange")
          v-icon(start size="x-small") mdi-help-circle-outline
          | uncertainty {{ (current.uncertainty * 100).toFixed(0) }}%
        v-chip(label size="small" :color="signalColor(current.signals_fired, current.subtask)")
          | {{ current.signals_fired }}/{{ current.subtask === 'A' ? 6 : 3 }} signals
        v-chip(label size="small" variant="outlined") {{ current.relation_label || current.entity_type }}

      //- Sentence context
      SentenceView(:sample="sentenceSample(current)")

      //- Abbreviation pair (short abbreviates long)
      .d-flex.align-center.gap-3.mt-4.mb-5.px-1
        v-chip(label size="small" color="primary" variant="tonal") {{ current.short_text }}
        .text-caption.text-medium-emphasis.mx-1 ── abbreviates ──▶
        v-chip(label size="small" color="blue" variant="tonal") {{ current.long_text }}

      //- Verdict buttons
      .d-flex.flex-wrap.gap-2.mb-1
        v-btn(
          color="success"
          :variant="verdict === 1 ? 'elevated' : 'tonal'"
          prepend-icon="mdi-check"
          @click="verdict = 1"
        ) Correct
        v-btn(
          color="warning"
          :variant="verdict === 2 ? 'elevated' : 'tonal'"
          prepend-icon="mdi-swap-horizontal"
          @click="verdict = 2"
        ) Inverse correct
        v-btn(
          color="error"
          :variant="verdict === 0 ? 'elevated' : 'tonal'"
          prepend-icon="mdi-close"
          @click="verdict = 0"
        ) Not abbreviation

      v-alert(v-if="error" type="error" variant="tonal" density="compact" class="mt-3" closable @click:close="error=null") {{ error }}

    //- Navigation footer
    v-card-actions(v-if="!loading && activeItems.length")
      .text-caption.text-medium-emphasis {{ activeIdx + 1 }} / {{ activeItems.length }}
      v-spacer
      v-btn(
        variant="text"
        prepend-icon="mdi-chevron-left"
        :disabled="activeIdx === 0"
        @click="navigate(-1)"
      ) Prev
      v-btn(
        variant="text"
        append-icon="mdi-chevron-right"
        :disabled="isLast"
        @click="navigate(1)"
      ) Skip
      v-btn(
        color="primary"
        variant="tonal"
        append-icon="mdi-chevron-right"
        :disabled="verdict === null"
        :loading="saving"
        @click="save"
      ) {{ isLast ? 'Save' : 'Save & next' }}
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import SentenceView from './SentenceView.vue'
import { useAnnotator } from '../composables/useAnnotator.js'

const QUEUE_PATH = 'data/abbreviation/al_queue.json'

const open = defineModel({ type: Boolean })
const emit = defineEmits(['annotated'])

const { annotator } = useAnnotator()

const allItems  = ref([])
const loading   = ref(false)
const saving    = ref(false)
const error     = ref(null)
const subtask   = ref('A')
const idxA      = ref(0)
const idxB      = ref(0)
const verdict   = ref(null)
const annotatedA = ref(0)
const annotatedB = ref(0)

const itemsA       = computed(() => allItems.value.filter(i => i.subtask === 'A'))
const itemsB       = computed(() => allItems.value.filter(i => i.subtask === 'B'))
const uncertainA   = computed(() => itemsA.value.filter(i => i.queue_reason === 'uncertain'))
const uncertainB   = computed(() => itemsB.value.filter(i => i.queue_reason === 'uncertain'))
const verifyA      = computed(() => itemsA.value.filter(i => i.queue_reason === 'verify_positive' || i.queue_reason === 'verify_negative'))
const verifyB      = computed(() => itemsB.value.filter(i => i.queue_reason === 'verify_positive' || i.queue_reason === 'verify_negative'))

const activeItems     = computed(() => subtask.value === 'A' ? itemsA.value : itemsB.value)
const activeIdx       = computed(() => subtask.value === 'A' ? idxA.value : idxB.value)
const activeAnnotated = computed(() => subtask.value === 'A' ? annotatedA.value : annotatedB.value)

const current = computed(() => activeItems.value[activeIdx.value] ?? null)
const isLast  = computed(() => activeIdx.value >= activeItems.value.length - 1)

watch(subtask, () => { verdict.value = null })
watch(() => activeIdx.value, () => { verdict.value = null })
watch(open, v => { if (v) load() })

// ── SentenceView mapping ──────────────────────────────────────────────────

function sentenceSample(item) {
  if (item.subtask === 'A') {
    return {
      sentence: item.sentence,
      tokens:   item.tokens,
      subject:  { text: item.subject_text, label: item.type_a,
                  begin_token: item.subject_begin_token, end_token: item.subject_end_token },
      object:   { text: item.object_text,  label: item.type_b,
                  begin_token: item.object_begin_token,  end_token: item.object_end_token },
      label: item.relation_label,
    }
  }
  return {
    sentence:    item.sentence,
    tokens:      item.tokens,
    text:        item.span_text,
    label:       item.entity_type,
    begin_token: item.begin_token,
    end_token:   item.end_token,
  }
}

// ── Data loading ──────────────────────────────────────────────────────────

async function load() {
  loading.value = true
  error.value   = null
  try {
    const [qRes, idsRes] = await Promise.all([
      fetch(`/api/json?path=${encodeURIComponent(QUEUE_PATH)}&_t=${Date.now()}`),
      fetch('/api/annotated-ids'),
    ])
    if (!qRes.ok) throw new Error(`${qRes.status} ${qRes.statusText}`)
    const data = await qRes.json()
    const annotatedIds = new Set(idsRes.ok ? await idsRes.json() : [])
    allItems.value = (data.queue ?? []).filter(item => !annotatedIds.has(item.id))
    idxA.value = 0
    idxB.value = 0
    annotatedA.value = 0
    annotatedB.value = 0
    verdict.value = null
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

// ── Navigation & saving ───────────────────────────────────────────────────

function navigate(delta) {
  const next = activeIdx.value + delta
  if (next >= 0 && next < activeItems.value.length) {
    if (subtask.value === 'A') idxA.value = next
    else idxB.value = next
  }
}

async function save() {
  if (verdict.value === null || !annotator.value) return
  saving.value = true
  try {
    const res = await fetch('/api/annotate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: current.value.id, label: verdict.value, annotator: annotator.value }),
    })
    if (!res.ok) throw new Error(`Save failed: ${res.statusText}`)
    if (subtask.value === 'A') annotatedA.value++
    else annotatedB.value++
    emit('annotated')
    // Remove the annotated item from the list so it won't reappear
    const savedId = current.value.id
    allItems.value = allItems.value.filter(i => i.id !== savedId)
    // idx stays in place — next item shifts into current position
    // but clamp if we just removed the last item
    if (subtask.value === 'A') idxA.value = Math.min(idxA.value, itemsA.value.length - 1)
    else idxB.value = Math.min(idxB.value, itemsB.value.length - 1)
    if (activeItems.value.length === 0) open.value = false
  } catch (e) {
    error.value = e.message
  } finally {
    saving.value = false
  }
}

// ── Helpers ───────────────────────────────────────────────────────────────

function signalColor(fired, sub) {
  const t = fired / (sub === 'A' ? 6 : 3)
  if (t >= 0.8) return 'success'
  if (t >= 0.4) return 'warning'
  return 'error'
}
</script>
