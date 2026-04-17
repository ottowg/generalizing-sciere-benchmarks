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
      | Original dataset-specific labels mapped to the unified schema
      | (Dataset / Method / Task). Labels shown in
      span.text-error  red
      |  are dropped.
    v-table(density="compact" class="mb-8 mapping-table")
      thead
        tr
          th.text-left Original label
          th.text-left(v-for="ds in datasets" :key="ds") {{ ds }}
      tbody
        tr(v-for="label in entityLabels" :key="label")
          td.font-italic {{ label }}
          td(v-for="ds in datasets" :key="ds")
            template(v-if="entityMatrix[label]?.[ds] !== undefined")
              span(:class="entityMatrix[label][ds].startsWith('—') ? 'text-error' : 'text-medium-emphasis'")
                | {{ entityMatrix[label][ds] }}
            span.text-disabled(v-else) —

    //- ── Relation Mappings ─────────────────────────────────────────────────────
    .text-subtitle-1.font-weight-medium.mb-1 Relation Label Mappings
    .text-caption.text-medium-emphasis.mb-3
      | Original relation types mapped to the seven canonical relation types.
      | ↔ indicates the subject–object direction is inverted during mapping.
    v-table(density="compact" class="mapping-table")
      thead
        tr
          th.text-left Original label
          th.text-left(v-for="ds in datasets" :key="ds") {{ ds }}
      tbody
        tr(v-for="label in relationLabels" :key="label")
          td.font-italic {{ label }}
          td(v-for="ds in datasets" :key="ds")
            template(v-if="relationMatrix[label]?.[ds]")
              span(:class="relationMatrix[label][ds].unified.startsWith('—') ? 'text-error' : 'text-medium-emphasis'")
                | {{ relationMatrix[label][ds].unified }}
              span.text-caption.ml-1(v-if="relationMatrix[label][ds].inverted") ↔
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
  // Preferred order
  const order = ['gsap-ere', 'scier', 'scinlp']
  return [...order.filter(k => keys.includes(k)), ...keys.filter(k => !order.includes(k))]
})

// ── Entity mapping matrix: { [originalLabel]: { [dataset]: unifiedLabel } } ──
const entityMatrix = computed(() => {
  if (!report.value) return {}
  const m = {}
  for (const [ds, rows] of Object.entries(report.value.label_mappings ?? {})) {
    for (const row of rows) {
      if (!m[row.original]) m[row.original] = {}
      m[row.original][ds] = row.unified
    }
  }
  return m
})

const entityLabels = computed(() => Object.keys(entityMatrix.value).sort((a, b) => a.localeCompare(b)))

// ── Relation mapping matrix: { [originalLabel]: { [dataset]: { unified, inverted } } }
const relationMatrix = computed(() => {
  if (!report.value) return {}
  const m = {}
  for (const [ds, rows] of Object.entries(report.value.relation_mappings ?? {})) {
    for (const row of rows) {
      if (!m[row.original]) m[row.original] = {}
      m[row.original][ds] = { unified: row.unified, inverted: row.inverted }
    }
  }
  return m
})

const relationLabels = computed(() => Object.keys(relationMatrix.value).sort((a, b) => a.localeCompare(b)))

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
