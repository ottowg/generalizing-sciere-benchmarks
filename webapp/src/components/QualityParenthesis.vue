<template lang="pug">
v-container(fluid class="pa-6")
  .d-flex.align-center.mb-4
    div
      h2.text-h5 {{ report?.title || 'Parenthesized Mentions' }}
      .text-caption.text-medium-emphasis(v-if="report") Generated: {{ report.generated }}
    v-spacer
    v-btn(icon size="small" variant="text" :loading="loading" @click="regenerate")
      v-icon mdi-refresh

  v-alert(v-if="error" type="error" class="mb-4") {{ error }}

  template(v-if="report")
    v-alert(type="info" variant="tonal" class="mb-6" icon="mdi-information-outline") {{ report.info }}

    .text-subtitle-1.font-weight-medium.mb-2 Parenthesized Mention Rate — Gold
    .text-caption.text-medium-emphasis.mb-3 All splits combined
    v-table(density="compact" class="mb-6 overview-table")
      thead
        tr
          th Entity Type
          th.text-right(v-for="ds in uniqueDatasets" :key="ds") {{ ds }}
      tbody
        tr(v-for="label in uniqueLabels" :key="label")
          td {{ label }}
          td.text-right(v-for="ds in uniqueDatasets" :key="ds")
            strong(v-if="isGoldMax(label, ds)") {{ goldOverview[ds]?.[label] ?? '—' }}
            span(v-else) {{ goldOverview[ds]?.[label] ?? '—' }}

    .text-subtitle-1.font-weight-medium.mb-2 Explore by Dataset, Split & Model
    v-card(variant="flat" color="grey-lighten-4" :rounded="false" class="mb-4 pa-3")
      .filter-row
        .filter-label Dataset
        v-btn-toggle(v-model="filterDataset" multiple density="compact" color="primary" variant="outlined")
          v-btn(v-for="v in uniqueDatasets" :key="v" :value="v" size="small") {{ v }}

      .filter-row.mt-2
        .filter-label Split
        v-btn-toggle(v-model="filterSplit" multiple density="compact" color="primary" variant="outlined")
          v-btn(v-for="v in uniqueSplits" :key="v" :value="v" size="small") {{ v }}

      .filter-row.mt-2
        .filter-label Model
        v-btn-toggle(v-model="filterAnnotator" multiple density="compact" color="primary" variant="outlined")
          v-btn(v-for="v in uniqueAnnotators" :key="v" :value="v" size="small") {{ v }}

      .filter-row.mt-2
        .filter-label Entity Type
        v-btn-toggle(v-model="filterLabel" multiple density="compact" color="primary" variant="outlined")
          v-btn(v-for="v in uniqueLabels" :key="v" :value="v" size="small") {{ v }}

    v-data-table(
      :headers="tableHeaders"
      :items="filteredRows"
      :loading="loading"
      density="compact"
      :items-per-page="-1"
      hide-default-footer
      class="mb-4"
    )
      template(#item.pct="{ item }") {{ item.pct }}%

    v-expansion-panels(variant="accordion")
      v-expansion-panel(title="Notes")
        v-expansion-panel-text
          ul
            li(v-for="note in report.notes" :key="note") {{ note }}

    v-alert(v-if="report.errors?.length" type="warning" class="mt-4" variant="tonal")
      div(v-for="e in report.errors" :key="e") {{ e }}
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'

const JSON_PATH = 'reports/ere_confusion_analysis/parenthesized_mentions.json'

const report = ref(null)
const loading = ref(false)
const error = ref(null)

const filterDataset   = ref([])
const filterSplit     = ref([])
const filterAnnotator = ref([])
const filterLabel     = ref([])

const unique = key => [...new Set((report.value?.rows ?? []).map(r => r[key]))].sort()

const uniqueDatasets   = computed(() => unique('dataset'))
const uniqueSplits     = computed(() => unique('split'))
const uniqueAnnotators = computed(() => unique('annotator'))
const uniqueLabels     = computed(() => unique('label'))

function initFilters() {
  filterDataset.value   = []
  filterSplit.value     = []
  filterAnnotator.value = []
  filterLabel.value     = [...uniqueLabels.value]
}

watch(report, initFilters)

// Overview table: gold only, all splits combined, % per dataset × entity type
const goldOverview = computed(() => {
  if (!report.value) return {}
  const agg = {}  // { dataset: { label: { count, total } } }
  for (const r of report.value.rows) {
    if (r.annotator !== 'gold') continue
    if (!agg[r.dataset]) agg[r.dataset] = {}
    if (!agg[r.dataset][r.label]) agg[r.dataset][r.label] = { count: 0, total: 0 }
    agg[r.dataset][r.label].count += r.count
    agg[r.dataset][r.label].total += r.total
  }
  // Format as percentages
  const result = {}
  for (const [ds, labels] of Object.entries(agg)) {
    result[ds] = {}
    for (const [label, { count, total }] of Object.entries(labels)) {
      result[ds][label] = total > 0 ? (count / total * 100).toFixed(1) + '%' : '0%'
    }
  }
  return result
})

function isGoldMax(label, dataset) {
  const values = uniqueDatasets.value
    .map(ds => parseFloat(goldOverview.value[ds]?.[label]) || 0)
  const max = Math.max(...values)
  return max > 0 && (parseFloat(goldOverview.value[dataset]?.[label]) || 0) === max
}

const tableHeaders = [
  { title: 'Entity Type', key: 'label',    sortable: true },
  { title: 'Count',       key: 'count',    sortable: true, align: 'end' },
  { title: 'Total',       key: 'total',    sortable: true, align: 'end' },
  { title: '%',           key: 'pct',      sortable: true, align: 'end' },
  { title: 'Examples',    key: 'examples', sortable: false },
]

const filteredRows = computed(() => {
  if (!report.value) return []
  const filtered = report.value.rows.filter(r =>
    filterDataset.value.includes(r.dataset) &&
    filterSplit.value.includes(r.split) &&
    filterAnnotator.value.includes(r.annotator) &&
    filterLabel.value.includes(r.label)
  )
  // Aggregate by entity type, recomputing % from summed count and total
  const byLabel = new Map()
  for (const r of filtered) {
    if (!byLabel.has(r.label)) {
      byLabel.set(r.label, { label: r.label, count: 0, total: 0, examples: new Set() })
    }
    const agg = byLabel.get(r.label)
    agg.count += r.count
    agg.total += r.total
    r.examples.split('; ').filter(Boolean).forEach(e => agg.examples.add(e))
  }
  return [...byLabel.values()].map(agg => ({
    label:    agg.label,
    count:    agg.count,
    total:    agg.total,
    pct:      agg.total > 0 ? +(agg.count / agg.total * 100).toFixed(1) : 0,
    examples: [...agg.examples].slice(0, 5).join('; '),
  }))
})

async function fetchReport() {
  const res = await fetch(`/api/json?path=${encodeURIComponent(JSON_PATH)}&_t=${Date.now()}`)
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  report.value = await res.json()
}

async function load() {
  loading.value = true
  error.value = null
  try {
    await fetchReport()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function regenerate() {
  loading.value = true
  error.value = null
  try {
    const res = await fetch('/api/regenerate?report=quality-parenthesis', { method: 'POST' })
    const result = await res.json()
    if (!result.ok) throw new Error(result.stderr || 'Script failed')
    await fetchReport()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.overview-table {
  width: auto;
  display: inline-table;
}
.filter-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.filter-label {
  width: 80px;
  font-size: 0.75rem;
  color: rgba(0,0,0,0.6);
  flex-shrink: 0;
}
</style>
