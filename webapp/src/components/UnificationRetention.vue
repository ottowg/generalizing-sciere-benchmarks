<template lang="pug">
v-container(fluid class="pa-6")
  .d-flex.align-center.mb-2
    div
      h2.text-h5 {{ report?.title || 'Retention Statistics' }}
      .text-caption.text-medium-emphasis(v-if="report") Generated: {{ report.generated }}
    v-spacer
    v-btn(v-if="!dockerMode" icon size="small" variant="text" :loading="loading" @click="regenerate")
      v-icon mdi-refresh

  v-alert(v-if="error" type="error" class="mb-4") {{ error }}

  template(v-if="report")
    v-alert(type="info" variant="tonal" class="mb-6" icon="mdi-information-outline") {{ report.info }}

    .text-subtitle-1.font-weight-medium.mb-2 Summary
    v-table(density="compact" class="mb-6 overview-table")
      thead
        tr
          th Dataset
          th.text-right Entities (orig)
          th.text-right Entities kept
          th.text-right %
          th.text-right Relations (orig)
          th.text-right Relations kept
          th.text-right %
      tbody
        tr(v-for="r in report.summary" :key="r.dataset")
          td {{ r.dataset }}
          td.text-right {{ r.entities_original.toLocaleString() }}
          td.text-right {{ r.entities_kept.toLocaleString() }}
          td.text-right
            strong(v-if="isMinEntityPct(r)") {{ r.entities_pct }}%
            span(v-else) {{ r.entities_pct }}%
          td.text-right {{ r.relations_original.toLocaleString() }}
          td.text-right {{ r.relations_kept.toLocaleString() }}
          td.text-right
            strong(v-if="isMinRelationPct(r)") {{ r.relations_pct }}%
            span(v-else) {{ r.relations_pct }}%

    .text-subtitle-1.font-weight-medium.mb-2 Entity Retention Breakdown
    v-table(density="compact" class="mb-6")
      thead
        tr
          th Dataset
          th.text-right Original
          th.text-right Removed: merge
          th.text-right Removed: unmapped
          th.text-right Removed: corrections
          th.text-right Span-normalised
          th.text-right Kept
      tbody
        tr(v-for="r in report.entity_breakdown" :key="r.dataset")
          td {{ r.dataset }}
          td.text-right {{ r.original.toLocaleString() }}
          td.text-right {{ fmtCell(r.removed_merge) }}
          td.text-right {{ fmtCell(r.removed_unmapped) }}
          td.text-right {{ r.removed_corrections ? fmtCell(r.removed_corrections) : '—' }}
          td.text-right {{ fmtCell(r.span_normalised) }}
          td.text-right
            strong {{ fmtCell(r.kept) }}

    .text-subtitle-1.font-weight-medium.mb-2 Relation Retention Breakdown
    v-table(density="compact" class="mb-6")
      thead
        tr
          th Dataset
          th.text-right Original
          th.text-right Removed: merge
          th.text-right Removed: unmapped
          th.text-right Kept
      tbody
        tr(v-for="r in report.relation_breakdown" :key="r.dataset")
          td {{ r.dataset }}
          td.text-right {{ r.original.toLocaleString() }}
          td.text-right {{ fmtCell(r.removed_merge) }}
          td.text-right {{ fmtCell(r.removed_unmapped) }}
          td.text-right
            strong {{ fmtCell(r.kept) }}

    .text-subtitle-1.font-weight-medium.mb-2 Dropped Entity Labels
    v-table(density="compact" class="overview-table")
      thead
        tr
          th Dataset
          th Dropped labels
      tbody
        tr(v-for="(labels, ds) in report.dropped_labels" :key="ds")
          td {{ ds }}
          td
            span(v-if="labels.length") {{ labels.join(', ') }}
            em(v-else) none
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useDockerMode } from '../composables/useDockerMode.js'

const RETENTION_PATH = 'reports/unification/retention.json'

const { dockerMode } = useDockerMode()
const report  = ref(null)
const loading = ref(false)
const error   = ref(null)

function fmtCell({ count, pct }) {
  return count > 0 ? `${count.toLocaleString()} (${pct}%)` : '—'
}

const isMinEntityPct = (row) => {
  if (!report.value) return false
  const min = Math.min(...report.value.summary.map(r => r.entities_pct))
  return row.entities_pct === min
}
const isMinRelationPct = (row) => {
  if (!report.value) return false
  const min = Math.min(...report.value.summary.map(r => r.relations_pct))
  return row.relations_pct === min
}

async function fetchReport() {
  const res = await fetch(`/api/json?path=${encodeURIComponent(RETENTION_PATH)}&_t=${Date.now()}`)
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  report.value = await res.json()
}

async function load() {
  loading.value = true
  error.value = null
  try { await fetchReport() }
  catch (e) { error.value = e.message }
  finally { loading.value = false }
}

async function regenerate() {
  loading.value = true
  error.value = null
  try {
    const res = await fetch('/api/regenerate?report=unification', { method: 'POST' })
    const result = await res.json()
    if (!result.ok) throw new Error(result.stderr || 'Script failed')
    await fetchReport()
  } catch (e) { error.value = e.message }
  finally { loading.value = false }
}

onMounted(load)
</script>

<style scoped>
.overview-table { width: auto; display: inline-table; }
</style>
