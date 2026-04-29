<template lang="pug">
v-container(fluid class="pa-6")
  .d-flex.align-center.mb-2
    div
      h2.text-h5 Label Mappings
      .text-caption.text-medium-emphasis(v-if="report") Generated: {{ report.generated }}
    v-spacer
    v-btn(v-if="!dockerMode" icon size="small" variant="text" :loading="loading" @click="load")
      v-icon mdi-refresh

  v-alert(v-if="error" type="error" class="mb-4") {{ error }}

  template(v-if="report")
    //- ── Entity Mappings ───────────────────────────────────────────────────────
    .text-subtitle-1.font-weight-medium.mb-1 Entity Label Mappings
    .text-caption.text-medium-emphasis.mb-3
      | Per-dataset labels mapped to each unified entity label (Dataset / Method / Task).
      | Labels shown in
      span.text-error  red
      |  are dropped.
    v-table(density="compact" class="mb-8 mapping-table")
      thead
        tr
          th.text-left Unified
          th.text-left(v-for="ds in datasets" :key="ds") {{ ds }}
      tbody
        tr(v-for="uLabel in entityUnifiedLabels" :key="uLabel")
          td(:class="uLabel.startsWith('—') ? 'text-error font-italic' : 'font-weight-medium'") {{ uLabel }}
          td(v-for="ds in datasets" :key="ds")
            template(v-if="entityReverseMatrix[uLabel]?.[ds]?.length")
              span.text-medium-emphasis {{ entityReverseMatrix[uLabel][ds].join(', ') }}
            span.text-disabled(v-else) —

    //- ── Relation Mappings ─────────────────────────────────────────────────────
    .text-subtitle-1.font-weight-medium.mb-1 Relation Label Mappings
    .text-caption.text-medium-emphasis.mb-3
      | Per-dataset relation types mapped to each canonical relation.
      | ↔ indicates the subject–object direction is inverted during mapping.
    v-table(density="compact" class="mapping-table")
      thead
        tr
          th.text-left Unified
          th.text-left(v-for="ds in datasets" :key="ds") {{ ds }}
      tbody
        tr(v-for="uLabel in relationUnifiedLabels" :key="uLabel")
          td(:class="uLabel.startsWith('—') ? 'text-error font-italic' : 'font-weight-medium'") {{ uLabel }}
          td(v-for="ds in datasets" :key="ds")
            template(v-if="relationReverseMatrix[uLabel]?.[ds]?.length")
              span(v-for="(entry, i) in relationReverseMatrix[uLabel][ds]" :key="i")
                span.text-medium-emphasis {{ entry.original }}
                span.text-caption.ml-1(v-if="entry.inverted") ↔
                span(v-if="i < relationReverseMatrix[uLabel][ds].length - 1") ,&nbsp;
            span.text-disabled(v-else) —
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useDockerMode } from '../composables/useDockerMode.js'

const PIPELINE_PATH = 'reports/unification/pipeline.json'

const { dockerMode } = useDockerMode()
const report  = ref(null)
const loading = ref(false)
const error   = ref(null)

const datasets = computed(() => {
  const keys = Object.keys(report.value?.label_mappings ?? {})
  const order = ['gsap-ere', 'scier', 'scinlp']
  return [...order.filter(k => keys.includes(k)), ...keys.filter(k => !order.includes(k))]
})

// ── Entity reverse matrix: { [unifiedLabel]: { [dataset]: [original, ...] } } ─
const entityReverseMatrix = computed(() => {
  if (!report.value) return {}
  const m = {}
  for (const [ds, rows] of Object.entries(report.value.label_mappings ?? {})) {
    for (const row of rows) {
      if (!m[row.unified]) m[row.unified] = {}
      if (!m[row.unified][ds]) m[row.unified][ds] = []
      m[row.unified][ds].push(row.original)
    }
  }
  return m
})

// Non-dropped labels first (alphabetically), dropped last
const entityUnifiedLabels = computed(() =>
  Object.keys(entityReverseMatrix.value).sort((a, b) => {
    const aD = a.startsWith('—'), bD = b.startsWith('—')
    if (aD !== bD) return aD ? 1 : -1
    return a.localeCompare(b)
  })
)

// ── Relation reverse matrix: { [unifiedLabel]: { [dataset]: [{original, inverted}] } }
const relationReverseMatrix = computed(() => {
  if (!report.value) return {}
  const m = {}
  for (const [ds, rows] of Object.entries(report.value.relation_mappings ?? {})) {
    for (const row of rows) {
      if (!m[row.unified]) m[row.unified] = {}
      if (!m[row.unified][ds]) m[row.unified][ds] = []
      m[row.unified][ds].push({ original: row.original, inverted: row.inverted })
    }
  }
  return m
})

const relationUnifiedLabels = computed(() =>
  Object.keys(relationReverseMatrix.value).sort((a, b) => {
    const aD = a.startsWith('—'), bD = b.startsWith('—')
    if (aD !== bD) return aD ? 1 : -1
    return a.localeCompare(b)
  })
)

async function load() {
  loading.value = true
  error.value = null
  try {
    const res = await fetch(`/api/json?path=${encodeURIComponent(PIPELINE_PATH)}&_t=${Date.now()}`)
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
    report.value = await res.json()
  } catch (e) { error.value = e.message }
  finally { loading.value = false }
}

onMounted(load)
</script>

<style scoped>
.mapping-table {
  width: auto;
  min-width: 500px;
}
</style>
