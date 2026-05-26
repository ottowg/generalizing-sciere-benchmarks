<template lang="pug">
v-container(fluid class="pa-6")
  .d-flex.align-center.mb-1
    div
      h2.text-h5 Auxiliary Transfer Documents
      .text-caption.text-medium-emphasis
        | SciER NLP domain-shift split and GSAP-ERE auxiliary sets.
        | Cluster 1 = NLP domain, Cluster 0 = non-NLP domain.
    v-spacer
    v-btn(
      v-if="tab === 'results'"
      variant="text" prepend-icon="mdi-refresh" size="small"
      :loading="building" @click="rebuild"
    ) Rebuild

  v-alert(v-if="loadError" type="error" density="compact" class="mb-4") {{ loadError }}
  v-progress-linear(v-if="loading" indeterminate class="mb-4")

  template(v-if="data")
    v-tabs(v-model="tab" class="mb-4")
      v-tab(value="summary") Summary
      v-tab(value="papers") Paper List
      v-tab(value="results") Results

    v-window(v-model="tab")

      //- ── SUMMARY ─────────────────────────────────────────────────────────────
      v-window-item(value="summary")
        .text-caption.font-weight-medium.text-medium-emphasis.text-uppercase.mb-2
          | Domain-Shift SciER split
        v-row(dense class="mb-4")
          v-col(v-for="card in scierCards" :key="card.label" cols="12" sm="4")
            v-card(variant="outlined" density="compact")
              v-card-text.pa-3
                .d-flex.align-center.ga-2
                  v-icon(:color="card.color" size="20") mdi-file-document-multiple-outline
                  div
                    .text-h6.font-weight-bold {{ card.count }}
                    .text-caption.text-medium-emphasis {{ card.label }}
                    .text-caption(:class="card.domainClass") {{ card.domain }}

        .text-caption.font-weight-medium.text-medium-emphasis.text-uppercase.mb-2
          | GSAP-ERE Auxiliary Sets
        v-row(dense class="mb-4")
          v-col(v-for="card in gsapCards" :key="card.label" cols="12" sm="4")
            v-card(variant="outlined" density="compact")
              v-card-text.pa-3
                .d-flex.align-center.ga-2
                  v-icon(:color="card.color" size="20") mdi-database-outline
                  div
                    .text-h6.font-weight-bold {{ card.count }}
                    .text-caption.text-medium-emphasis {{ card.label }}
                    .text-caption(:class="card.domainClass") {{ card.domain }}

        v-sheet(variant="outlined" rounded class="pa-4 mt-2")
          .text-subtitle-2.mb-2 Experimental Conditions
          table.run-table
            thead
              tr
                th Run
                th Description
                th SciER non-NLP
                th GSAP non-NLP aux
                th GSAP NLP aux
                th SciER dev
                th SciER test
            tbody
              tr(v-for="run in runs" :key="run.id")
                td.run-id {{ run.id }}
                td {{ run.desc }}
                td.num 66
                td.num {{ run.nonNlp }}
                td.num {{ run.nlp }}
                td.num 10
                td.num 22

      //- ── PAPER LIST ──────────────────────────────────────────────────────────
      v-window-item(value="papers")
        .d-flex.flex-wrap.ga-4.mb-3
          div
            .text-caption.text-medium-emphasis.mb-1 Domain
            v-btn-toggle(v-model="filterDomain" mandatory density="compact" variant="outlined" color="primary")
              v-btn(value="(all)" size="small") All
              v-btn(value="NLP" size="small") NLP
              v-btn(value="non-NLP" size="small") non-NLP

          div
            .text-caption.text-medium-emphasis.mb-1 Dataset
            v-btn-toggle(v-model="filterDataset" mandatory density="compact" variant="outlined" color="primary")
              v-btn(value="(all)" size="small") All
              v-btn(value="scier" size="small") SciER
              v-btn(value="gsap-ere" size="small") GSAP-ERE

          div
            .text-caption.text-medium-emphasis.mb-1 Role
            v-btn-toggle(v-model="filterRole" mandatory density="compact" variant="outlined" color="primary")
              v-btn(value="(all)" size="small") All
              v-btn(value="train" size="small") train
              v-btn(value="dev" size="small") dev
              v-btn(value="test" size="small") test
              v-btn(value="aux-nlp" size="small") auxiliary NLP
              v-btn(value="aux-non-nlp" size="small") auxiliary non-NLP
              v-btn(value="aux-mixed" size="small") auxiliary mixed

        .text-caption.text-medium-emphasis.mb-2 {{ filtered.length }} documents

        .overflow-auto
          table.doc-table
            thead
              tr
                th.col-title Title
                th.col-dataset Dataset
                th.col-split Orig. Split
                th.col-domain Domain
                th.col-role Experiment Role
            tbody
              tr(v-for="doc in filtered" :key="doc.doc_id")
                td.col-title
                  span.text-body-2 {{ doc.title }}
                td.col-dataset
                  v-chip(:color="doc.original_dataset === 'scier' ? 'error' : 'primary'" size="x-small" label variant="tonal")
                    | {{ doc.original_dataset === 'scier' ? 'SciER' : 'GSAP-ERE' }}
                td.col-split
                  span.text-caption.text-medium-emphasis {{ doc.original_split }}
                td.col-domain
                  v-chip(:color="doc.cluster_label === 'NLP' ? 'teal' : 'orange'" size="x-small" label variant="tonal")
                    | {{ doc.cluster_label }}
                td.col-role
                  template(v-if="doc.original_dataset === 'scier'")
                    v-chip(:color="splitColor(doc.experiment_split)" size="x-small" label variant="tonal")
                      | {{ doc.experiment_split }}
                  template(v-else)
                    .d-flex.ga-1.flex-wrap
                      v-chip(v-if="doc.in_non_nlp_aux" color="orange" size="x-small" label variant="tonal") non-NLP aux
                      v-chip(v-if="doc.in_nlp_aux" color="teal" size="x-small" label variant="tonal") NLP aux
                      v-chip(v-if="doc.in_mixed_aux" color="purple" size="x-small" label variant="tonal") mixed aux

      //- ── RESULTS ─────────────────────────────────────────────────────────────
      v-window-item(value="results")
        template(v-if="resultsError")
          v-alert(type="warning" variant="tonal" class="mb-4")
            | {{ resultsError }}
            v-btn.ml-3(size="small" variant="tonal" :loading="building" @click="rebuild") Build now

        template(v-else-if="!results")
          v-alert(type="info" variant="tonal" class="mb-4")
            | No results yet.
            v-btn.ml-3(size="small" variant="tonal" :loading="building" @click="rebuild") Build now

        template(v-else)
          //- Split toggle
          .d-flex.flex-wrap.ga-4.mb-4
            div
              .text-caption.text-medium-emphasis.mb-1 Split
              v-btn-toggle(v-model="chartSplit" mandatory density="compact" variant="outlined" color="primary")
                v-btn(value="dev" size="small") Dev (non-NLP)
                v-btn(value="test" size="small") Test (NLP target)
            div
              .text-caption.text-medium-emphasis.mb-1 Options
              v-btn-toggle(v-model="showStd" multiple density="compact" variant="outlined" color="teal")
                v-btn(value="std" size="small") ± std

          //- Boxplot charts
          .text-caption.text-medium-emphasis.mb-3
            | Each box spans Q1–Q3, line = median, whiskers = min/max, dots = individual seeds.
          .d-flex.flex-wrap.ga-6.mb-6
            div(v-for="cm in CHART_METRICS" :key="cm.key")
              .text-caption.font-weight-medium.mb-1 {{ cm.label }}
              svg(:width="SVG_W" :height="SVG_H" style="overflow:visible;")
                g(:transform="`translate(${MG.left},${MG.top})`")
                  //- Grid + Y-axis
                  template(v-for="t in chartProps(cm.key).ticks" :key="t")
                    line(:x1="0" :x2="IW" :y1="ys(t, chartProps(cm.key))" :y2="ys(t, chartProps(cm.key))" stroke="#e0e0e0" stroke-width="1")
                    text(:x="-6" :y="ys(t, chartProps(cm.key)) + 4" text-anchor="end" font-size="10" fill="#888") {{ t }}
                  //- Baseline at zero
                  line(x1="0" :x2="IW" :y1="IH" :y2="IH" stroke="#bbb" stroke-width="1")
                  //- Boxplots
                  g(v-for="d in chartProps(cm.key).data" :key="d.trained_on" :transform="`translate(${xs(d.i, chartProps(cm.key).data.length)},0)`")
                    template(v-if="d.stats")
                      //- Whiskers
                      line(:y1="ys(d.stats.min, chartProps(cm.key))" :y2="ys(d.stats.q1, chartProps(cm.key))" x1="0" x2="0" :stroke="d.color" stroke-width="1.5" stroke-dasharray="3,2")
                      line(:y1="ys(d.stats.max, chartProps(cm.key))" :y2="ys(d.stats.q3, chartProps(cm.key))" x1="0" x2="0" :stroke="d.color" stroke-width="1.5" stroke-dasharray="3,2")
                      line(:y1="ys(d.stats.min, chartProps(cm.key))" :y2="ys(d.stats.min, chartProps(cm.key))" :x1="-BOX_W/4" :x2="BOX_W/4" :stroke="d.color" stroke-width="1.5")
                      line(:y1="ys(d.stats.max, chartProps(cm.key))" :y2="ys(d.stats.max, chartProps(cm.key))" :x1="-BOX_W/4" :x2="BOX_W/4" :stroke="d.color" stroke-width="1.5")
                      //- IQR box
                      rect(:x="-BOX_W/2" :y="ys(d.stats.q3, chartProps(cm.key))" :width="BOX_W" :height="Math.max(1, ys(d.stats.q1, chartProps(cm.key)) - ys(d.stats.q3, chartProps(cm.key)))" :fill="d.fill" :stroke="d.color" stroke-width="1.5" rx="2")
                      //- Median
                      line(:y1="ys(d.stats.med, chartProps(cm.key))" :y2="ys(d.stats.med, chartProps(cm.key))" :x1="-BOX_W/2" :x2="BOX_W/2" :stroke="d.color" stroke-width="2.5")
                      //- Seed dots
                      circle(v-for="(v, j) in d.stats.vals" :key="j" :cy="ys(v, chartProps(cm.key))" cx="0" r="3" :fill="d.color" opacity="0.75")
                    template(v-else)
                      //- No data marker
                      text(y="0" text-anchor="middle" font-size="10" fill="#bbb") –
                    //- Run label
                    text(:y="IH + 18" text-anchor="middle" font-size="11" font-weight="600" :fill="d.color") {{ d.label }}

          //- Table metric selector
          .d-flex.flex-wrap.ga-4.mb-3
            div
              .text-caption.text-medium-emphasis.mb-1 Table metric
              v-btn-toggle(v-model="metric" mandatory density="compact" variant="outlined" color="primary")
                v-btn(value="ner_exact_f1" size="small") NER
                v-btn(value="ner_partial_f1" size="small") NER≈
                v-btn(value="re_relaxed_f1" size="small") RE
                v-btn(value="re_relaxed_partial_f1" size="small") RE≈
                v-btn(value="re_strict_f1" size="small") RE+
                v-btn(value="re_strict_partial_f1" size="small") RE+≈

          //- Per-run table
          .text-subtitle-2.mb-2 Results by run
          .overflow-auto
            table.res-table
              thead
                tr
                  th Run
                  th Description
                  th Seeds
                  th Dev F1
                  th Test F1
                  th Δ (test − dev)
              tbody
                tr(v-for="row in tableRows" :key="row.trained_on")
                  td.run-col
                    v-chip(:color="runColor(row.trained_on)" size="x-small" label variant="tonal") {{ row.label }}
                  td {{ row.display }}
                  td.center {{ row.n_seeds ?? '—' }}
                  td.center
                    template(v-if="row.dev !== null")
                      | {{ row.dev.toFixed(1) }}
                      span.std(v-if="showStd.includes('std') && row.devStd > 0") ±{{ row.devStd.toFixed(1) }}
                    template(v-else) —
                  td.center
                    template(v-if="row.test !== null")
                      | {{ row.test.toFixed(1) }}
                      span.std(v-if="showStd.includes('std') && row.testStd > 0") ±{{ row.testStd.toFixed(1) }}
                    template(v-else) —
                  td.center(:class="deltaClass(row.delta)")
                    template(v-if="row.delta !== null") {{ row.delta > 0 ? '+' : '' }}{{ row.delta.toFixed(1) }}
                    template(v-else) —

          //- Per-seed details
          .text-subtitle-2.mt-5.mb-2 Seed-level detail
          .overflow-auto
            table.res-table
              thead
                tr
                  th Run
                  th Seed
                  th Dev F1
                  th Test F1
                  th Δ (test − dev)
              tbody
                template(v-for="row in tableRows" :key="row.trained_on")
                  tr(v-for="seed in row.seedRows" :key="seed.seed")
                    td.run-col
                      v-chip(:color="runColor(row.trained_on)" size="x-small" label variant="tonal") {{ row.label }}
                    td.center {{ seed.seed ?? '—' }}
                    td.center {{ seed.dev !== null ? seed.dev.toFixed(1) : '—' }}
                    td.center {{ seed.test !== null ? seed.test.toFixed(1) : '—' }}
                    td.center(:class="deltaClass(seed.delta)")
                      template(v-if="seed.delta !== null") {{ seed.delta > 0 ? '+' : '' }}{{ seed.delta.toFixed(1) }}
                      template(v-else) —
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// ── colours per run (keyed by trained_on prefix letter) ──────────────────────
const RUN_COLORS = {
  A: { border: '#757575', bg: 'rgba(117,117,117,0.15)', chip: 'grey'    },
  B: { border: '#F57C00', bg: 'rgba(245,124,0,0.15)',   chip: 'orange'  },  // non-NLP aux
  C: { border: '#00897B', bg: 'rgba(0,137,123,0.15)',   chip: 'teal'    },  // NLP aux
  D: { border: '#7B1FA2', bg: 'rgba(123,31,162,0.15)',  chip: 'purple'  },
}

function runKey(trained_on) {
  return trained_on?.[0]?.toUpperCase() ?? 'X'
}

function runColor(trained_on) {
  return RUN_COLORS[runKey(trained_on)]?.chip ?? 'grey'
}

// ── state ─────────────────────────────────────────────────────────────────────
const data         = ref(null)
const loading      = ref(false)
const loadError    = ref(null)
const results      = ref(null)
const resultsError = ref(null)
const building     = ref(false)
const tab          = ref('summary')

const chartSplit = ref('test')
const showStd    = ref([])

// ── Boxplot chart constants ───────────────────────────────────────────────────
const CHART_METRICS = [
  { key: 'ner_exact_f1', label: 'NER F1' },
  { key: 're_relaxed_f1', label: 'RE F1' },
]
const SVG_W = 260, SVG_H = 210
const MG = { top: 15, right: 12, bottom: 30, left: 42 }
const IW = SVG_W - MG.left - MG.right
const IH = SVG_H - MG.top - MG.bottom
const BOX_W = 34

function quartiles(vals) {
  if (!vals.length) return null
  const s = [...vals].sort((a, b) => a - b)
  const q = p => {
    const i = p * (s.length - 1), lo = Math.floor(i), hi = Math.ceil(i)
    return lo === hi ? s[lo] : s[lo] + (s[hi] - s[lo]) * (i - lo)
  }
  return { min: s[0], q1: q(0.25), med: q(0.5), q3: q(0.75), max: s.at(-1), vals: s }
}

function chartProps(metricKey) {
  if (!results.value) return { data: [], ticks: [], yMin: 0, yMax: 100 }
  const data = results.value.runs.map((run, i) => {
    const sd   = run[chartSplit.value]
    const vals = (sd?.seeds ?? []).map(s => s[metricKey]).filter(v => v != null)
    const key  = run.trained_on[0].toUpperCase()
    const c    = RUN_COLORS[key] ?? { border: '#999', bg: 'rgba(150,150,150,0.15)' }
    return { trained_on: run.trained_on, label: key, color: c.border, fill: c.bg, stats: quartiles(vals), i }
  })
  const allVals = data.flatMap(d => d.stats?.vals ?? [])
  if (!allVals.length) return { data, ticks: [], yMin: 0, yMax: 100 }
  const rawMin = Math.min(...allVals), rawMax = Math.max(...allVals)
  const pad  = Math.max((rawMax - rawMin) * 0.18, 3)
  const yMin = Math.max(0,   Math.floor(rawMin - pad))
  const yMax = Math.min(100, Math.ceil(rawMax  + pad))
  const step = (yMax - yMin) <= 15 ? 2 : (yMax - yMin) <= 30 ? 5 : 10
  const ticks = []
  for (let t = Math.ceil(yMin / step) * step; t <= yMax; t += step) ticks.push(t)
  return { data, ticks, yMin, yMax }
}

function ys(val, cp) {
  return IH - ((val - cp.yMin) / (cp.yMax - cp.yMin || 1)) * IH
}

function xs(i, n) {
  return (i + 0.5) * (IW / n)
}

const metric = ref('re_relaxed_f1')  // used only by tables

const filterDomain  = ref('(all)')
const filterDataset = ref('(all)')
const filterRole    = ref('(all)')

// ── static run config (Summary tab) ──────────────────────────────────────────
const runs = [
  { id: 'A', desc: 'SciER non-NLP baseline',   nonNlp: 0,  nlp: 0  },
  { id: 'B', desc: 'non-NLP auxiliary',         nonNlp: 46, nlp: 0  },
  { id: 'C', desc: 'NLP auxiliary',             nonNlp: 0,  nlp: 46 },
  { id: 'D', desc: 'Mixed auxiliary control',   nonNlp: 23, nlp: 23 },
]

// ── Summary tab cards ─────────────────────────────────────────────────────────
const scierCards = computed(() => {
  if (!data.value) return []
  const s = data.value.statistics
  return [
    { label: 'Domain-shift train', count: s.scier_train, domain: 'non-NLP documents',      color: 'orange', domainClass: 'text-orange-darken-2' },
    { label: 'Domain-shift dev',   count: s.scier_dev,   domain: 'non-NLP documents',      color: 'orange', domainClass: 'text-orange-darken-2' },
    { label: 'Domain-shift test',  count: s.scier_test,  domain: 'NLP documents (target)', color: 'teal',   domainClass: 'text-teal-darken-1'   },
  ]
})

const gsapCards = computed(() => {
  if (!data.value) return []
  const s = data.value.statistics
  return [
    { label: 'non-NLP auxiliary', count: s.gsap_non_nlp_aux, domain: 'Run B — non-NLP control',     color: 'orange', domainClass: 'text-orange-darken-2'  },
    { label: 'NLP auxiliary',     count: s.gsap_nlp_aux,     domain: 'Run C — target-domain',       color: 'teal',   domainClass: 'text-teal-darken-1'    },
    { label: 'Mixed auxiliary',   count: s.gsap_mixed_aux,   domain: 'Run D — 23 NLP + 23 non-NLP', color: 'purple', domainClass: 'text-purple-darken-2'  },
  ]
})

// ── Paper list ────────────────────────────────────────────────────────────────
const filtered = computed(() => {
  if (!data.value) return []
  return data.value.documents.filter(doc => {
    if (filterDataset.value !== '(all)' && doc.original_dataset !== filterDataset.value) return false
    if (filterDomain.value  !== '(all)' && doc.cluster_label    !== filterDomain.value)  return false
    if (filterRole.value !== '(all)') {
      const r = filterRole.value
      if (r === 'train'       && !(doc.original_dataset === 'scier'   && doc.experiment_split === 'train')) return false
      if (r === 'dev'         && !(doc.original_dataset === 'scier'   && doc.experiment_split === 'dev'))   return false
      if (r === 'test'        && !(doc.original_dataset === 'scier'   && doc.experiment_split === 'test'))  return false
      if (r === 'aux-nlp'     && !(doc.original_dataset === 'gsap-ere' && doc.in_nlp_aux))                  return false
      if (r === 'aux-non-nlp' && !(doc.original_dataset === 'gsap-ere' && doc.in_non_nlp_aux))              return false
      if (r === 'aux-mixed'   && !(doc.original_dataset === 'gsap-ere' && doc.in_mixed_aux))                return false
    }
    return true
  })
})

// ── Results helpers ───────────────────────────────────────────────────────────
function _meanF1(splitData) {
  return splitData?.[`${metric.value}_mean`] ?? null
}
function _stdF1(splitData) {
  return splitData?.[`${metric.value}_std`] ?? 0
}
function _seedF1(seedRecord) {
  return seedRecord?.[metric.value] ?? null
}

const tableRows = computed(() => {
  if (!results.value) return []
  return results.value.runs.map(run => {
    const devMean  = _meanF1(run.dev)
    const testMean = _meanF1(run.test)
    const delta    = devMean !== null && testMean !== null ? testMean - devMean : null

    // Build per-seed rows by matching dev/test seeds
    const devSeeds  = run.dev?.seeds  ?? []
    const testSeeds = run.test?.seeds ?? []
    const seedMap   = {}
    for (const s of devSeeds)  { seedMap[s.seed] = { seed: s.seed, dev:  _seedF1(s), test: null } }
    for (const s of testSeeds) {
      if (seedMap[s.seed]) seedMap[s.seed].test = _seedF1(s)
      else seedMap[s.seed] = { seed: s.seed, dev: null, test: _seedF1(s) }
    }
    const seedRows = Object.values(seedMap).map(s => ({
      ...s,
      delta: s.dev !== null && s.test !== null ? s.test - s.dev : null,
    }))

    return {
      trained_on: run.trained_on,
      label:      run.trained_on[0].toUpperCase(),
      display:    run.display,
      n_seeds:    run.dev?.n_seeds ?? run.test?.n_seeds ?? null,
      dev:        devMean,
      devStd:     _stdF1(run.dev),
      test:       testMean,
      testStd:    _stdF1(run.test),
      delta,
      seedRows,
    }
  })
})

function deltaClass(delta) {
  if (delta === null) return ''
  if (delta >= 1)  return 'text-success'
  if (delta <= -1) return 'text-error'
  return 'text-medium-emphasis'
}


// ── data loading ──────────────────────────────────────────────────────────────
function splitColor(split) {
  return split === 'train' ? 'primary' : split === 'dev' ? 'secondary' : 'success'
}

async function load() {
  loading.value  = true
  loadError.value = null
  try {
    const r = await fetch('/api/json?path=data/webapp/static/auxiliary_transfer_docs.json')
    if (!r.ok) { loadError.value = `Failed to load document list (${r.status})`; return }
    data.value = await r.json()
  } catch (e) {
    loadError.value = e.message
  } finally {
    loading.value = false
  }
}

async function loadResults() {
  resultsError.value = null
  try {
    const r = await fetch('/api/domain-shift')
    if (r.status === 404) { resultsError.value = 'No results yet — click Rebuild to compute.'; return }
    if (!r.ok) { resultsError.value = `Failed to load results (${r.status})`; return }
    results.value = await r.json()
  } catch (e) {
    resultsError.value = e.message
  }
}

async function rebuild() {
  building.value = true
  try {
    const r = await fetch('/api/domain-shift/build', { method: 'POST' })
    const body = await r.json()
    if (!body.ok) { resultsError.value = body.stderr || 'Build failed'; return }
    await loadResults()
  } catch (e) {
    resultsError.value = e.message
  } finally {
    building.value = false
  }
}

onMounted(async () => {
  await load()
  await loadResults()
})
</script>

<style scoped>
.doc-table,
.res-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}
.doc-table th, .doc-table td,
.res-table th, .res-table td {
  padding: 6px 10px;
  border-bottom: 1px solid rgba(0,0,0,.08);
  vertical-align: middle;
}
.doc-table thead th,
.res-table thead th {
  background: rgba(0,0,0,.03);
  font-weight: 600;
  white-space: nowrap;
  position: sticky;
  top: 0;
  z-index: 1;
}
.doc-table tbody tr:hover,
.res-table tbody tr:hover { background: rgba(0,0,0,.02); }

.col-title   { min-width: 280px; }
.col-dataset,
.col-split,
.col-domain  { white-space: nowrap; }
.col-role    { min-width: 120px; }
.run-col     { white-space: nowrap; }
.center      { text-align: center; }
.std         { font-size: 11px; color: #888; margin-left: 2px; }

.run-table {
  border-collapse: collapse;
  font-size: 13px;
  width: 100%;
}
.run-table th,
.run-table td {
  padding: 5px 12px;
  border-bottom: 1px solid rgba(0,0,0,.08);
  text-align: left;
}
.run-table thead th { font-weight: 600; white-space: nowrap; }
.run-table .run-id  { font-weight: 700; }
.run-table .num     { text-align: center; }

</style>
