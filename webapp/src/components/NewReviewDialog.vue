<template lang="pug">
v-dialog(v-model="open" max-width="900" scrollable)
  v-card
    v-card-title.pt-4 {{ review ? 'Configure Review' : 'New Annotation Review' }}
    v-card-subtitle.pb-2 {{ type === 'mentions' ? 'Entity Mentions' : 'Relations' }}

    v-card-text
      //- Locked notice
      v-alert.mb-4(
        v-if="isLocked"
        type="info"
        variant="tonal"
        density="compact"
        :text="`Initialized with ${review.samples.length} samples. Settings are locked.`"
      )
        template(#append)
          v-btn(size="small" variant="text" @click="localUnlocked = true; fetchPreview()") Unlock & edit

      .d-flex.gap-10(style="align-items: flex-start")
        //- Left column: form controls
        .flex-shrink-0(style="width: 280px")
          //- Data context
          v-select(
            v-model="form.dataset"
            :disabled="isLocked"
            :items="datasets"
            label="Dataset"
            variant="outlined"
            density="compact"
            class="mb-3"
          )
          v-select(
            v-model="form.model"
            :items="datasets"
            :disabled="isLocked"
            label="Model"
            hint="identified by training source"
            persistent-hint
            variant="outlined"
            density="compact"
            class="mb-4"
          )

          //- Label & scope
          v-label.text-caption.mb-1 Label Set
          v-btn-toggle(
            v-model="form.labelSet"
            mandatory
            :disabled="isLocked"
            density="compact"
            color="primary"
            class="mb-4 d-flex"
          )
            v-btn(value="original" class="flex-grow-1" :disabled="crossDataset") Original
            v-btn(value="unified" class="flex-grow-1") Unified
          .text-caption.text-medium-emphasis.mt-n3.mb-4(v-if="crossDataset")
            | Dataset and model differ — only Unified labels are comparable.

          v-label.text-caption.mb-1 Split
          v-chip-group(
            v-model="form.splits"
            multiple
            :disabled="isLocked"
            selected-class="text-primary"
            class="mb-4"
          )
            v-chip(v-for="s in splits" :key="s" :value="s" filter) {{ s }}

          v-label.text-caption.mb-1 Outcome
          v-chip-group(
            v-model="form.outcomes"
            multiple
            :disabled="isLocked"
            selected-class="text-primary"
            class="mb-5"
          )
            v-chip(v-for="o in outcomes" :key="o.value" :value="o.value" filter) {{ o.label }}

          v-divider.mb-4

          //- Sampling
          v-label.text-caption.mb-1 Sampling
          v-btn-toggle(
            v-model="form.sampling"
            mandatory
            :disabled="isLocked"
            density="compact"
            color="primary"
            class="mb-4 d-flex"
          )
            v-btn(value="random" class="flex-grow-1") Random
            v-btn(value="score" class="flex-grow-1") By Score

          v-text-field(
            v-model.number="form.samplesPerLabel"
            label="Samples per combination"
            :disabled="isLocked"
            type="number"
            min="1"
            variant="outlined"
            density="compact"
          )

        //- Right column: preview
        .flex-grow-1
          .d-flex.align-center.mb-2
            v-icon.mr-1(size="small" color="medium-emphasis") mdi-eye-outline
            span.text-caption.text-medium-emphasis Sample preview
          .preview-box.rounded.pa-3(style="background: rgba(0,0,0,0.04); min-height: 80px")
            //- Locked: read straight from stored samples — no API call needed
            template(v-if="isLocked")
              .d-flex.align-center.gap-2
                v-icon(size="small" color="success") mdi-lock-outline
                span.text-body-2
                  strong {{ review.samples.length }}
                  |  samples locked
            //- Unlocked: live count from API
            template(v-else-if="!isValid")
              span.text-caption.text-disabled Fill in all fields to see a preview.
            template(v-else-if="previewLoading")
              v-progress-linear(indeterminate rounded height="2")
            template(v-else-if="previewError")
              span.text-caption.text-error Lookup data not built yet — use Initialize on the list.
            template(v-else-if="previewTotal != null")
              .mb-2
                span.text-h5 {{ previewTotal }}
                span.text-caption.text-medium-emphasis.ml-2 {{ type }} to annotate
              v-table(density="compact" v-if="labelRows.length")
                thead
                  tr
                    th.text-left.pr-0(style="width:32px")
                      v-checkbox-btn(
                        :model-value="allLabelsSelected"
                        :indeterminate="someLabelsSelected"
                        density="compact"
                        hide-details
                        :disabled="isLocked"
                        @click="toggleAllLabels"
                      )
                    th.text-left
                      .d-flex.align-center.gap-2
                        span Label
                        template(v-if="!isLocked")
                          a.text-caption.ml-2(
                            href="#"
                            style="text-decoration: none"
                            @click.prevent="form.labels = null"
                          ) all
                          span.text-caption.text-disabled /
                          a.text-caption(
                            href="#"
                            style="text-decoration: none"
                            @click.prevent="form.labels = []"
                          ) none
                    th.text-right(v-for="o in selectedOutcomes" :key="o") {{ o.toUpperCase() }}
                    th.text-right(v-if="selectedOutcomes.length > 1") Sum
                tbody
                  tr(
                    v-for="row in labelRows"
                    :key="row.label"
                    style="cursor: pointer"
                    :style="isLabelSelected(row.label) ? {} : { opacity: 0.4 }"
                    @click="!isLocked && toggleLabel(row.label)"
                  )
                    td.pr-0
                      v-checkbox-btn(
                        :model-value="isLabelSelected(row.label)"
                        density="compact"
                        hide-details
                        :disabled="isLocked"
                        @click.stop="toggleLabel(row.label)"
                      )
                    td {{ row.label }}
                    td.text-right(v-for="o in selectedOutcomes" :key="o") {{ row[o] }}
                    td.text-right(v-if="selectedOutcomes.length > 1") {{ row.sum }}
                tfoot
                  tr.font-weight-bold
                    td
                    td Total
                    td.text-right(v-for="o in selectedOutcomes" :key="o") {{ totalsRow[o] }}
                    td.text-right(v-if="selectedOutcomes.length > 1") {{ totalsRow.sum }}
            template(v-else)
              span.text-caption.text-disabled Computing…

    v-card-actions
      v-spacer
      v-btn(variant="text" @click="open = false") Cancel
      v-btn(
        v-if="!isLocked"
        variant="tonal"
        :disabled="!isValid"
        @click="submit"
      ) {{ review ? 'Save' : 'Create' }}
      v-btn(
        color="primary"
        :disabled="!isValid || previewError || previewTotal === 0"
        :title="isLocked ? 'Re-generate sample list' : (review ? 'Save config and lock sample list' : 'Create and lock sample list')"
        @click="initialize"
      )
        v-icon.mr-1 mdi-database-arrow-down-outline
        | {{ isLocked ? 'Re-initialize' : 'Initialize' }}
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { fetchSampleCount } from '../composables/useReviews.js'

const props = defineProps({
  type:   { type: String, required: true },
  review: { type: Object, default: null },
})

const emit = defineEmits(['create', 'update', 'initialize'])

const open = defineModel({ type: Boolean })

const localUnlocked = ref(false)
const isLocked = computed(() => !localUnlocked.value && (props.review?.samples?.length > 0))

const datasets = ['gsap-ere', 'scier', 'scinlp']
const splits   = ['train', 'dev', 'test']
const outcomes = [
  { value: 'tp', label: 'TP' },
  { value: 'fp', label: 'FP' },
  { value: 'fn', label: 'FN' },
]

function defaultForm() {
  return { dataset: null, model: null, labelSet: 'original', splits: [], outcomes: [], labels: null, sampling: 'random', samplesPerLabel: 20 }
}

const form = ref(defaultForm())

watch(open, v => {
  localUnlocked.value = false
  if (v && props.review) {
    form.value = {
      dataset:         props.review.dataset,
      model:           props.review.model,
      labelSet:        props.review.labelSet,
      splits:          [...props.review.splits],
      outcomes:        [...props.review.outcomes],
      labels:          props.review.labels?.length > 0 ? [...props.review.labels] : null,
      sampling:        props.review.sampling,
      samplesPerLabel: props.review.samplesPerLabel,
    }
  } else if (v && !props.review) {
    form.value = defaultForm()
  }
  // Trigger preview immediately on open (no debounce) for unlocked state
  if (v && !isLocked.value) fetchPreview()
})

const crossDataset = computed(() =>
  !!form.value.dataset && !!form.value.model && form.value.dataset !== form.value.model
)

// Auto-switch to unified when dataset ≠ model
watch(crossDataset, yes => { if (yes) form.value.labelSet = 'unified' })

const isValid = computed(() =>
  form.value.dataset &&
  form.value.model &&
  form.value.splits.length > 0 &&
  form.value.outcomes.length > 0 &&
  form.value.samplesPerLabel > 0
)

// ── preview table ─────────────────────────────────────────────────────────────
const selectedOutcomes = computed(() => form.value.outcomes ?? [])

const labelRows = computed(() => {
  if (!previewCounts.value) return []
  return Object.entries(previewCounts.value)
    .map(([label, counts]) => {
      const row = { label }
      let sum = 0
      for (const o of selectedOutcomes.value) {
        row[o] = counts[o] ?? 0
        sum += row[o]
      }
      row.sum = sum
      return row
    })
    .sort((a, b) => b.sum - a.sum)
})

const totalsRow = computed(() => {
  const row = {}
  let totalSum = 0
  for (const o of selectedOutcomes.value) {
    row[o] = labelRows.value.reduce((s, r) => s + (r[o] ?? 0), 0)
    totalSum += row[o]
  }
  row.sum = totalSum
  return row
})

// ── label selection ───────────────────────────────────────────────────────────
// null = all labels included (no filter); [] = none; [...] = specific subset
const allLabels = computed(() => labelRows.value.map(r => r.label))

const allLabelsSelected  = computed(() => form.value.labels === null || form.value.labels.length === allLabels.value.length)
const someLabelsSelected = computed(() => Array.isArray(form.value.labels) && form.value.labels.length > 0 && form.value.labels.length < allLabels.value.length)

function isLabelSelected(label) {
  return form.value.labels === null || form.value.labels.includes(label)
}

function toggleLabel(label) {
  const current = form.value.labels === null ? [...allLabels.value] : [...form.value.labels]
  const idx = current.indexOf(label)
  if (idx === -1) current.push(label)
  else current.splice(idx, 1)
  form.value.labels = current.length === allLabels.value.length ? null : current
}

function toggleAllLabels() {
  form.value.labels = allLabelsSelected.value ? [] : null
}

// ── live preview ───────────────────────────────────────────────────────────────
const previewTotal   = ref(null)
const previewCounts  = ref(null)
const previewLoading = ref(false)
const previewError   = ref(false)
let   previewTimer   = null

watch(form, () => {
  previewTotal.value  = null
  previewCounts.value = null
  previewError.value  = false
  if (!isValid.value) return
  clearTimeout(previewTimer)
  previewTimer = setTimeout(fetchPreview, 400)
}, { deep: true })

async function fetchPreview() {
  if (!isValid.value) return
  previewLoading.value = true
  previewError.value   = false
  try {
    // Always fetch counts for all labels so the table shows every label (deselected ones are greyed out)
    const pseudoReview = { ...form.value, labels: null, type: props.type }
    const data = await fetchSampleCount(pseudoReview)
    if (data.error || data.total == null) { previewError.value = true; return }
    previewTotal.value  = data.total
    previewCounts.value = data.counts
  } catch {
    previewError.value = true
  } finally {
    previewLoading.value = false
  }
}

// ── actions ───────────────────────────────────────────────────────────────────
function payload() { return { ...form.value, labels: form.value.labels ?? [], type: props.type } }

function submit() {
  emit(props.review ? 'update' : 'create', payload())
  open.value = false
}

function initialize() {
  emit('initialize', payload())
  open.value = false
}
</script>
