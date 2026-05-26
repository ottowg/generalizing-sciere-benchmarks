<template lang="pug">
v-container(fluid class="pa-6")
  .d-flex.align-center.mb-4
    div
      h2.text-h5 Label Statistics
      .text-caption.text-medium-emphasis(v-if="stats") Generated: {{ stats.generated }}
    v-spacer
    v-btn(v-if="!dockerMode" icon size="small" variant="text" :loading="loading" @click="buildAndLoad")
      v-icon mdi-refresh

  v-alert(v-if="error" type="error" class="mb-4") {{ error }}

  v-alert(v-if="!stats && !loading && !error" type="info" variant="tonal" class="mb-6")
    | No data yet.
    v-btn(v-if="!dockerMode" class="ml-2" size="small" variant="tonal" :loading="loading" @click="buildAndLoad") Generate

  template(v-if="stats")
    v-tabs(v-model="tab" class="mb-2")
      v-tab(value="entities")          Entities
      v-tab(value="entities-overtime") Entities Over Time
      v-tab(value="relations")         Relations
      v-tab(value="relations-overtime") Relations Over Time

    v-window(v-model="tab")

      //- ── ENTITIES ────────────────────────────────────────────────────────────
      v-window-item(value="entities")
        .text-caption.text-medium-emphasis.mb-5
          | Distribution of annotations per paper (all papers, including those with 0 of that label).
          | Bins show % of papers in each count range. Stats are over all papers.

        template(v-for="(_, ds) in stats.entities" :key="ds")
          v-sheet(class="mb-8 pa-4" rounded border)
            .d-flex.align-center.flex-wrap.ga-2.mb-3
              .text-subtitle-1.font-weight-bold {{ ds }}
              .text-caption.text-medium-emphasis {{ activeSplit(ds).n_papers }} papers
              v-spacer
              v-btn-toggle(
                :model-value="splitByDs[ds]"
                @update:model-value="v => splitByDs[ds] = v"
                mandatory density="compact" variant="outlined" color="primary"
              )
                v-btn(
                  v-for="sp in availableSplits(ds)" :key="sp"
                  :value="sp" size="small"
                ) {{ SPLIT_LABELS[sp] }}

            .overflow-auto
              table.dist-table
                thead
                  tr
                    th.label-col Label
                    th.bin-col(v-for="bin in BINS" :key="bin.label") {{ bin.label }}
                    th.stat-col Median
                    th.stat-col Mean
                    th.stat-col Min
                    th.stat-col Max
                tbody
                  tr(v-for="label in sortedLabels(activeSplit(ds).labels)" :key="label")
                    td.label-cell
                      span(:style="{ color: entityColor(label) }") {{ label }}
                    td.bin-col(
                      v-for="(bin, i) in computeBins(activeSplit(ds).by_label[label].per_paper, activeSplit(ds).n_papers)"
                      :key="i"
                    )
                      .bin-cell
                        .bin-bar(:style="{ width: Math.min(bin.pct, 100) + '%', background: BIN_COLORS[i] }")
                        span.bin-pct {{ bin.pct > 0 && bin.pct < 1 ? '<1' : bin.pct.toFixed(0) }}%
                    td.stat-col {{ computeStats(activeSplit(ds).by_label[label].per_paper).median }}
                    td.stat-col {{ computeStats(activeSplit(ds).by_label[label].per_paper).mean }}
                    td.stat-col {{ computeStats(activeSplit(ds).by_label[label].per_paper).min }}
                    td.stat-col {{ computeStats(activeSplit(ds).by_label[label].per_paper).max }}

            template(v-if="entityMappings[ds]")
              v-divider.my-3
              .text-caption.font-weight-medium.text-medium-emphasis.mb-2 Label mappings
              .d-flex.flex-wrap.ga-1
                v-chip(
                  v-for="row in entityMappings[ds]"
                  :key="row.original"
                  size="x-small"
                  :color="row.unified.startsWith('—') ? 'error' : 'default'"
                  variant="tonal"
                  label
                ) {{ row.original }} → {{ row.unified }}

      //- ── RELATIONS ───────────────────────────────────────────────────────────
      v-window-item(value="relations")
        .text-caption.text-medium-emphasis.mb-5
          | Distribution of relations per paper (all papers, including those with 0 of that type).
          | Bins show % of papers in each count range. Stats are over all papers.

        template(v-for="(_, ds) in stats.relations" :key="ds")
          v-sheet(class="mb-8 pa-4" rounded border)
            .d-flex.align-center.flex-wrap.ga-2.mb-3
              .text-subtitle-1.font-weight-bold {{ ds }}
              .text-caption.text-medium-emphasis {{ activeRelSplit(ds).n_papers }} papers
              v-spacer
              v-btn-toggle(
                :model-value="relSplitByDs[ds]"
                @update:model-value="v => relSplitByDs[ds] = v"
                mandatory density="compact" variant="outlined" color="primary"
              )
                v-btn(
                  v-for="sp in availableRelSplits(ds)" :key="sp"
                  :value="sp" size="small"
                ) {{ SPLIT_LABELS[sp] }}

            .overflow-auto
              table.dist-table
                thead
                  tr
                    th.label-col Group
                    th.label-col Label
                    th.bin-col(v-for="bin in BINS" :key="bin.label") {{ bin.label }}
                    th.stat-col Median
                    th.stat-col Mean
                    th.stat-col Min
                    th.stat-col Max
                tbody
                  template(v-for="(label, idx) in sortedRelLabels(activeRelSplit(ds).labels, ds)" :key="label")
                    tr(:class="{ 'group-border': idx > 0 && relGroupForLabel(ds, label) !== relGroupForLabel(ds, sortedRelLabels(activeRelSplit(ds).labels, ds)[idx - 1]) }")
                      td.group-cell
                        span.text-caption.text-medium-emphasis(
                          v-if="idx === 0 || relGroupForLabel(ds, label) !== relGroupForLabel(ds, sortedRelLabels(activeRelSplit(ds).labels, ds)[idx - 1])"
                        ) {{ relGroupForLabel(ds, label) }}
                      td.label-cell
                        span(:style="{ color: relColorStable(label) }") {{ label }}
                      td.bin-col(
                        v-for="(bin, i) in computeBins(activeRelSplit(ds).by_label[label].per_paper, activeRelSplit(ds).n_papers)"
                        :key="i"
                      )
                        .bin-cell
                          .bin-bar(:style="{ width: Math.min(bin.pct, 100) + '%', background: BIN_COLORS[i] }")
                          span.bin-pct {{ bin.pct > 0 && bin.pct < 1 ? '<1' : bin.pct.toFixed(0) }}%
                      td.stat-col {{ computeStats(activeRelSplit(ds).by_label[label].per_paper).median }}
                      td.stat-col {{ computeStats(activeRelSplit(ds).by_label[label].per_paper).mean }}
                      td.stat-col {{ computeStats(activeRelSplit(ds).by_label[label].per_paper).min }}
                      td.stat-col {{ computeStats(activeRelSplit(ds).by_label[label].per_paper).max }}

            template(v-if="relMappings[ds]")
              v-divider.my-3
              .text-caption.font-weight-medium.text-medium-emphasis.mb-2 Label mappings
              .d-flex.flex-wrap.ga-1
                v-chip(
                  v-for="row in relMappings[ds]"
                  :key="row.original"
                  size="x-small"
                  :color="row.unified.startsWith('—') ? 'error' : 'default'"
                  variant="tonal"
                  label
                ) {{ row.original }} → {{ row.unified }}{{ row.inverted ? ' ↔' : '' }}

      //- ── ENTITIES OVER TIME ──────────────────────────────────────────────────
      v-window-item(value="entities-overtime")
        .text-caption.text-medium-emphasis.mb-4
          | Mean entity count per paper per year (gold annotations).
          | X-axis labels show the number of papers in that year.

        .d-flex.flex-wrap.ga-4.mb-4
          div
            .text-caption.text-medium-emphasis.mb-1 Dataset
            v-btn-toggle(v-model="timeDs" mandatory density="compact" variant="outlined" color="primary")
              v-btn(v-for="ds in timeDatasets" :key="ds" :value="ds" size="small") {{ ds }}
          div
            .text-caption.text-medium-emphasis.mb-1 Split
            v-btn-toggle(v-model="timeSplit" mandatory density="compact" variant="outlined" color="primary")
              v-btn(v-for="sp in availableTimeSplits" :key="sp" :value="sp" size="small") {{ SPLIT_LABELS[sp] }}

        v-sheet(v-if="timeByYear" rounded border class="pa-4")
          EntityTimeChart(:byYear="timeByYear" :colorFn="entityColor" yLabel="Mean entities per paper")

      //- ── RELATIONS OVER TIME ─────────────────────────────────────────────────
      v-window-item(value="relations-overtime")
        .text-caption.text-medium-emphasis.mb-4
          | Mean relation count per paper per year (gold annotations).
          | X-axis labels show the number of papers in that year.

        .d-flex.flex-wrap.ga-4.mb-4
          div
            .text-caption.text-medium-emphasis.mb-1 Dataset
            v-btn-toggle(v-model="relTimeDs" mandatory density="compact" variant="outlined" color="primary")
              v-btn(v-for="ds in timeDatasets" :key="ds" :value="ds" size="small") {{ ds }}
          div
            .text-caption.text-medium-emphasis.mb-1 Split
            v-btn-toggle(v-model="relTimeSplit" mandatory density="compact" variant="outlined" color="primary")
              v-btn(v-for="sp in availableRelTimeSplits" :key="sp" :value="sp" size="small") {{ SPLIT_LABELS[sp] }}
          div
            .text-caption.text-medium-emphasis.mb-1 Group
            v-btn-toggle(v-model="relTimeGroup" mandatory density="compact" variant="outlined" color="primary")
              v-btn(v-for="g in relTimeGroups" :key="g" :value="g" size="small") {{ g }}

        v-sheet(v-if="relTimeByYearFiltered" rounded border class="pa-4")
          EntityTimeChart(:byYear="relTimeByYearFiltered" :colorFn="relColorStable" yLabel="Mean relations per paper")
</template>

<script setup>
import { ref, computed, onMounted, reactive, watch } from 'vue'
import EntityTimeChart from './EntityTimeChart.vue'
import { entityColor, relColorStable } from '../utils/entityColors.js'
import { useDockerMode } from '../composables/useDockerMode.js'

const { dockerMode } = useDockerMode()
const stats    = ref(null)
const loading  = ref(false)
const error    = ref(null)
const tab      = ref('entities')
const pipeline = ref(null)

const timeDs       = ref('gsap-ere')
const timeSplit    = ref('all')
const timeDatasets = ['gsap-ere', 'scier', 'scinlp']

const availableTimeSplits = computed(() => {
  const keys = Object.keys(stats.value?.entities_by_year?.[timeDs.value]?.splits ?? {})
  return [...SPLIT_ORDER.filter(s => keys.includes(s)), ...keys.filter(s => !SPLIT_ORDER.includes(s))]
})

const timeByYear = computed(() =>
  stats.value?.entities_by_year?.[timeDs.value]?.splits?.[timeSplit.value] ?? null
)

const relTimeDs    = ref('gsap-ere')
const relTimeSplit = ref('all')

const availableRelTimeSplits = computed(() => {
  const keys = Object.keys(stats.value?.relations_by_year?.[relTimeDs.value]?.splits ?? {})
  return [...SPLIT_ORDER.filter(s => keys.includes(s)), ...keys.filter(s => !SPLIT_ORDER.includes(s))]
})

const relTimeByYear = computed(() =>
  stats.value?.relations_by_year?.[relTimeDs.value]?.splits?.[relTimeSplit.value] ?? null
)

const relTimeGroup = ref('All')

watch(relTimeDs, () => { relTimeGroup.value = 'All' })

const relTimeGroups = computed(() => {
  const labels = new Set()
  for (const yearData of Object.values(relTimeByYear.value ?? {}))
    for (const lbl of Object.keys(yearData.by_label ?? {})) labels.add(lbl)
  const present = new Set([...labels].map(l => relGroupForLabel(relTimeDs.value, l)))
  return ['All', ...GROUP_ORDER.filter(g => present.has(g))]
})

const relTimeByYearFiltered = computed(() => {
  if (!relTimeByYear.value) return null
  if (relTimeGroup.value === 'All') return relTimeByYear.value
  return Object.fromEntries(
    Object.entries(relTimeByYear.value).map(([year, data]) => [
      year,
      {
        ...data,
        by_label: Object.fromEntries(
          Object.entries(data.by_label).filter(
            ([lbl]) => relGroupForLabel(relTimeDs.value, lbl) === relTimeGroup.value
          )
        ),
      },
    ])
  )
})

const entityMappings = computed(() => pipeline.value?.label_mappings   ?? {})
const relMappings    = computed(() => pipeline.value?.relation_mappings ?? {})

// ── Split state per dataset ───────────────────────────────────────────────────
const splitByDs    = reactive({ 'gsap-ere': 'all', 'scier': 'all', 'scinlp': 'all' })
const relSplitByDs = reactive({ 'gsap-ere': 'all', 'scier': 'all', 'scinlp': 'all' })

const SPLIT_LABELS = { all: 'All', train: 'Train', dev: 'Dev', test: 'Test', test_ood: 'Test OOD' }
const SPLIT_ORDER  = ['all', 'train', 'dev', 'test', 'test_ood']

function availableSplits(ds) {
  const keys = Object.keys(stats.value?.entities?.[ds]?.splits ?? {})
  return [...SPLIT_ORDER.filter(s => keys.includes(s)), ...keys.filter(s => !SPLIT_ORDER.includes(s))]
}

function availableRelSplits(ds) {
  const keys = Object.keys(stats.value?.relations?.[ds]?.splits ?? {})
  return [...SPLIT_ORDER.filter(s => keys.includes(s)), ...keys.filter(s => !SPLIT_ORDER.includes(s))]
}

function activeSplit(ds) {
  return stats.value?.entities?.[ds]?.splits?.[splitByDs[ds]] ?? { labels: [], n_papers: 0, by_label: {} }
}

function activeRelSplit(ds) {
  return stats.value?.relations?.[ds]?.splits?.[relSplitByDs[ds]] ?? { labels: [], n_papers: 0, by_label: {} }
}

// ── Relation semantic groups ──────────────────────────────────────────────────
const UNIFIED_TO_GROUP = {
  appliedTo:          'Task Binding',
  benchmarkFor:       'Task Binding',
  trainedEvaluatedOn: 'Data Usage',
  usedFor:            'Model Design',
  coreference:        'Peer Relating',
  isHyponymOf:        'Peer Relating',
  isComparedTo:       'Peer Relating',
  isPartOf:           'Peer Relating',
}
const GROUP_ORDER = ['Task Binding', 'Data Usage', 'Model Design', 'Peer Relating', 'Dropped', 'Other']

function relGroupForLabel(ds, label) {
  const mappings = relMappings.value?.[ds] ?? []
  const entry = mappings.find(m => m.original === label)
  if (!entry) return UNIFIED_TO_GROUP[label] ?? 'Other'
  if (entry.unified.startsWith('—')) return 'Dropped'
  return UNIFIED_TO_GROUP[entry.unified] ?? 'Other'
}

function sortedRelLabels(labels, ds) {
  if (!labels) return []
  return [...labels].sort((a, b) => {
    const ga = GROUP_ORDER.indexOf(relGroupForLabel(ds, a))
    const gb = GROUP_ORDER.indexOf(relGroupForLabel(ds, b))
    const gi = (ga === -1 ? 999 : ga) - (gb === -1 ? 999 : gb)
    return gi !== 0 ? gi : a.localeCompare(b)
  })
}

// ── Label ordering — ReferenceLink and URL go last ────────────────────────────
const LABEL_TAIL = new Set(['ReferenceLink', 'URL'])

function sortedLabels(labels) {
  if (!labels) return []
  const main = labels.filter(l => !LABEL_TAIL.has(l))
  const tail = labels.filter(l => LABEL_TAIL.has(l))
  return [...main, ...tail]
}

// ── Histogram bins ────────────────────────────────────────────────────────────
const BINS = [
  { label: '0',        min: 0,   max: 0       },
  { label: '1–5',      min: 1,   max: 5       },
  { label: '6–25',     min: 6,   max: 25      },
  { label: '26–50',    min: 26,  max: 50      },
  { label: '51–250',   min: 51,  max: 250     },
  { label: '251–500',  min: 251, max: 500     },
  { label: '501+',     min: 501, max: Infinity },
]
const BIN_COLORS = ['#bdbdbd', '#64b5f6', '#4dd0e1', '#26a69a', '#ffa726', '#ef6c00', '#ef5350']

function computeBins(perPaper, nTotal) {
  const counts = new Array(BINS.length).fill(0)
  for (const v of perPaper) {
    const i = BINS.findIndex(b => v >= b.min && v <= b.max)
    if (i >= 0) counts[i]++
  }
  return counts.map((c, i) => ({
    label: BINS[i].label,
    count: c,
    pct: nTotal > 0 ? (c / nTotal) * 100 : 0,
  }))
}

function computeStats(perPaper) {
  if (!perPaper?.length) return { median: '–', mean: '–', min: '–', max: '–' }
  const s = [...perPaper].sort((a, b) => a - b)
  const n = s.length
  const mid = Math.floor(n / 2)
  const median = n % 2 === 0 ? (s[mid - 1] + s[mid]) / 2 : s[mid]
  const mean = s.reduce((a, b) => a + b, 0) / n
  const fmt = v => Number.isInteger(v) ? v : v.toFixed(1)
  return { median: fmt(median), mean: fmt(mean), min: s[0], max: s[n - 1] }
}

// ── Data fetching ─────────────────────────────────────────────────────────────
async function fetchStats() {
  const res = await fetch(`/api/label-stats?_t=${Date.now()}`)
  if (res.status === 404) { stats.value = null; return }
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  stats.value = await res.json()
}

async function fetchPipeline() {
  try {
    const res = await fetch(`/api/json?path=reports%2Funification%2Fpipeline.json&_t=${Date.now()}`)
    if (res.ok) pipeline.value = await res.json()
  } catch { /* optional */ }
}

async function load() {
  loading.value = true
  error.value = null
  try { await Promise.all([fetchStats(), fetchPipeline()]) }
  catch (e) { error.value = e.message }
  finally { loading.value = false }
}

async function buildAndLoad() {
  loading.value = true
  error.value = null
  try {
    const res = await fetch('/api/label-stats/build', { method: 'POST' })
    const result = await res.json()
    if (!result.ok) throw new Error(result.stderr || 'Build failed')
    await fetchStats()
  } catch (e) { error.value = e.message }
  finally { loading.value = false }
}

onMounted(load)
</script>

<style scoped>
/* ── Histogram table ─────────────────────────────────────────────────────── */
.dist-table {
  border-collapse: collapse;
  font-size: 0.78rem;
  white-space: nowrap;
}
.dist-table th,
.dist-table td {
  padding: 5px 10px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.07);
  text-align: right;
  vertical-align: middle;
}
.dist-table th {
  font-weight: 600;
  font-size: 0.72rem;
  color: rgba(0, 0, 0, 0.55);
  padding-bottom: 6px;
}
.dist-table th.label-col,
.dist-table td.label-cell {
  text-align: left;
  padding-left: 0;
}
.bin-col   { min-width: 60px; }
.stat-col  { min-width: 46px; font-variant-numeric: tabular-nums; }
.group-cell { min-width: 100px; color: rgba(0,0,0,0.45); font-size: 0.72rem; white-space: nowrap; }
.group-border td { border-top: 2px solid rgba(0,0,0,0.1); }

.bin-cell {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  height: 20px;
  background: rgba(0, 0, 0, 0.04);
  border-radius: 3px;
  overflow: hidden;
  min-width: 48px;
}
.bin-bar {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  opacity: 0.35;
}
.bin-pct {
  position: relative;
  padding-right: 5px;
  font-size: 0.72rem;
  z-index: 1;
}

</style>
