<template lang="pug">
v-container(fluid)
  .d-flex.align-center.mb-3
    h2.text-h5 Cross-Dataset Performance
    v-chip.ml-3(v-if="generatedAt" size="small" variant="tonal" color="grey") {{ generatedAt }}
    v-spacer
    v-btn(v-if="!dockerMode" variant="text" prepend-icon="mdi-refresh" size="small" :loading="building" @click="rebuild") Rebuild

  v-tabs(v-model="activeTab" density="compact" color="primary" class="mb-4")
    v-tab(value="summary") Summary
    v-tab(value="entities") Entities
    v-tab(value="relations") Relations
    v-tab(value="multi-sciere-generalization") MultiSciERE Generalization

  //- ── Summary tab ────────────────────────────────────────────────────────
  div(v-if="activeTab === 'summary'")
    v-row.mb-3(dense align="center")
      v-col(cols="6" sm="3" md="2")
        v-select(v-model="filterSplit" :items="['(both)', 'dev', 'test']" label="Split" density="compact" variant="outlined" hide-details)
    v-data-table(
      :headers="summaryHeaders"
      :items="summaryRows"
      :sort-by="[{ key: 'train_ds', order: 'asc' }]"
      :cell-props="summaryCellProps"
      :items-per-page="-1"
      density="compact" hover class="grouped-table"
    )
      template(#item.train_ds="{ item }")
        v-chip(:color="dsColor(item.train_ds)" size="small" variant="tonal") {{ item.train_ds }}
      template(#item.test_ds="{ item }")
        v-chip(:color="dsColor(item.test_ds)" size="small" variant="tonal") {{ item.test_ds }}
      template(#item.split="{ item }")
        v-chip(size="x-small" variant="tonal") {{ item.split }}
      template(#item.ner_exact_f1="{ item }")
        span(:style="f1Style(item.ner_exact_f1)") {{ fmt(item.ner_exact_f1) }}
      template(#item.ner_partial_f1="{ item }")
        span(:style="f1Style(item.ner_partial_f1)") {{ fmt(item.ner_partial_f1) }}
      template(#item.re_relaxed_f1="{ item }")
        span(:style="f1Style(item.re_relaxed_f1)") {{ fmt(item.re_relaxed_f1) }}
      template(#item.re_relaxed_partial_f1="{ item }")
        span(:style="f1Style(item.re_relaxed_partial_f1)") {{ fmt(item.re_relaxed_partial_f1) }}
      template(#item.re_strict_f1="{ item }")
        span(:style="f1Style(item.re_strict_f1)") {{ fmt(item.re_strict_f1) }}
      template(#item.re_strict_partial_f1="{ item }")
        span(:style="f1Style(item.re_strict_partial_f1)") {{ fmt(item.re_strict_partial_f1) }}
      template(#bottom)

  //- ── Entity label-wise tab ───────────────────────────────────────────────
  div(v-if="activeTab === 'entities'")
    v-row.mb-3(dense align="center")
      v-col(cols="6" sm="3" md="2")
        v-select(v-model="filterTrainDs" :items="['(all)', ...TRAIN_DS]" label="Train" density="compact" variant="outlined" hide-details)
      v-col(cols="6" sm="3" md="2")
        v-select(v-model="filterTestDs" :items="['(all)', ...DS]" label="Test" density="compact" variant="outlined" hide-details)
      v-col(cols="6" sm="3" md="2")
        v-select(v-model="filterSplitLabel" :items="['(both)', 'dev', 'test']" label="Split" density="compact" variant="outlined" hide-details)
      v-col(cols="6" sm="3" md="2")
        v-select(v-model="filterNerMatch" :items="['exact', 'partial', '(both)']" label="Match" density="compact" variant="outlined" hide-details)
    v-data-table(
      :headers="labelHeaders"
      :items="entityLabelRows"
      :sort-by="[{ key: 'f1', order: 'desc' }]"
      :cell-props="labelCellProps"
      :items-per-page="-1"
      density="compact" hover
    )
      template(#item.train_ds="{ item }")
        v-chip(:color="dsColor(item.train_ds)" size="small" variant="tonal") {{ item.train_ds }}
      template(#item.test_ds="{ item }")
        v-chip(:color="dsColor(item.test_ds)" size="small" variant="tonal") {{ item.test_ds }}
      template(#item.split="{ item }")
        v-chip(size="x-small" variant="tonal") {{ item.split }}
      template(#item.match="{ item }")
        span.text-caption.text-medium-emphasis {{ item.match }}
      template(#item.precision="{ item }")
        span(:style="pStyle(item.precision)") {{ item.precision.toFixed(1) }}
      template(#item.recall="{ item }")
        span(:style="rStyle(item.recall)") {{ item.recall.toFixed(1) }}
      template(#item.f1="{ item }")
        span(:style="f1Style(item.f1)") {{ item.f1.toFixed(1) }}
      template(#body.append)
        tr(
          v-for="row in entityAggRows"
          :key="`${row.train_ds}|${row.test_ds}|${row.split}|${row.match}|${row.label}`"
          style="border-top:2px solid rgba(0,0,0,0.15);background:rgba(0,0,0,0.03);font-weight:600;"
        )
          td
            v-chip(:color="dsColor(row.train_ds)" size="small" variant="tonal") {{ row.train_ds }}
          td
            v-chip(:color="dsColor(row.test_ds)" size="small" variant="tonal") {{ row.test_ds }}
          td
            v-chip(size="x-small" variant="tonal") {{ row.split }}
          td
            span.text-caption.text-medium-emphasis {{ row.match }}
          td {{ row.label }}
          td.text-end(:style="`background:${BG_P};${pStyle(row.precision)}`") {{ row.precision.toFixed(1) }}
          td.text-end(:style="`background:${BG_R};${rStyle(row.recall)}`") {{ row.recall.toFixed(1) }}
          td.text-end(:style="`background:${BG_F1};`") #[span(:style="f1Style(row.f1)") {{ row.f1.toFixed(1) }}]
      template(#bottom)

  //- ── Relation label-wise tab ─────────────────────────────────────────────
  div(v-if="activeTab === 'relations'")
    v-row.mb-3(dense align="center")
      v-col(cols="6" sm="3" md="2")
        v-select(v-model="filterTrainDs" :items="['(all)', ...TRAIN_DS]" label="Train" density="compact" variant="outlined" hide-details)
      v-col(cols="6" sm="3" md="2")
        v-select(v-model="filterTestDs" :items="['(all)', ...DS]" label="Test" density="compact" variant="outlined" hide-details)
      v-col(cols="6" sm="3" md="2")
        v-select(v-model="filterSplitLabel" :items="['(both)', 'dev', 'test']" label="Split" density="compact" variant="outlined" hide-details)
      v-col(cols="6" sm="3" md="2")
        v-select(v-model="filterReMatch" :items="['relaxed', 'relaxed_partial', 'strict', 'strict_partial', '(both)']" label="RE metric" density="compact" variant="outlined" hide-details)
    v-data-table(
      :headers="labelHeaders"
      :items="relationLabelRows"
      :sort-by="[{ key: 'f1', order: 'desc' }]"
      :cell-props="labelCellProps"
      :items-per-page="-1"
      density="compact" hover
    )
      template(#item.train_ds="{ item }")
        v-chip(:color="dsColor(item.train_ds)" size="small" variant="tonal") {{ item.train_ds }}
      template(#item.test_ds="{ item }")
        v-chip(:color="dsColor(item.test_ds)" size="small" variant="tonal") {{ item.test_ds }}
      template(#item.split="{ item }")
        v-chip(size="x-small" variant="tonal") {{ item.split }}
      template(#item.match="{ item }")
        span.text-caption.text-medium-emphasis {{ item.match }}
      template(#item.precision="{ item }")
        span(:style="pStyle(item.precision)") {{ item.precision.toFixed(1) }}
      template(#item.recall="{ item }")
        span(:style="rStyle(item.recall)") {{ item.recall.toFixed(1) }}
      template(#item.f1="{ item }")
        span(:style="f1Style(item.f1)") {{ item.f1.toFixed(1) }}
      template(#body.append)
        tr(
          v-for="row in relationAggRows"
          :key="`${row.train_ds}|${row.test_ds}|${row.split}|${row.match}|${row.label}`"
          style="border-top:2px solid rgba(0,0,0,0.15);background:rgba(0,0,0,0.03);font-weight:600;"
        )
          td
            v-chip(:color="dsColor(row.train_ds)" size="small" variant="tonal") {{ row.train_ds }}
          td
            v-chip(:color="dsColor(row.test_ds)" size="small" variant="tonal") {{ row.test_ds }}
          td
            v-chip(size="x-small" variant="tonal") {{ row.split }}
          td
            span.text-caption.text-medium-emphasis {{ row.match }}
          td {{ row.label }}
          td.text-end(:style="`background:${BG_P};${pStyle(row.precision)}`") {{ row.precision.toFixed(1) }}
          td.text-end(:style="`background:${BG_R};${rStyle(row.recall)}`") {{ row.recall.toFixed(1) }}
          td.text-end(:style="`background:${BG_F1};`") #[span(:style="f1Style(row.f1)") {{ row.f1.toFixed(1) }}]
      template(#bottom)

  //- ── MultiSciERE Generalization tab ─────────────────────────────────────
  div(v-if="activeTab === 'multi-sciere-generalization'")
    v-row.mb-3(dense align="center")
      v-col(cols="6" sm="3" md="2")
        v-select(v-model="filterGenDs" :items="DS" label="Dataset" density="compact" variant="outlined" hide-details)
    p.text-caption.text-medium-emphasis.mb-3 Unified label set · test split · comparing {{ filterGenDs }}-trained model vs multi-sciere ({{ filterGenDs }} label space)
    v-data-table(
      :headers="generalizationHeaders"
      :items="generalizationRows"
      :sort-by="[{ key: 'train_ds', order: 'asc' }]"
      :cell-props="summaryCellProps"
      :items-per-page="-1"
      density="compact" hover class="grouped-table"
    )
      template(#item.train_ds="{ item }")
        v-chip(:color="dsColor(item.train_ds)" size="small" variant="tonal") {{ item.train_ds }}
      template(#item.test_ds="{ item }")
        v-chip(:color="dsColor(item.test_ds)" size="small" variant="tonal") {{ item.test_ds }}
      template(#item.ner_exact_f1="{ item }")
        span(:style="f1Style(item.ner_exact_f1)") {{ fmt(item.ner_exact_f1) }}
      template(#item.ner_partial_f1="{ item }")
        span(:style="f1Style(item.ner_partial_f1)") {{ fmt(item.ner_partial_f1) }}
      template(#item.re_relaxed_f1="{ item }")
        span(:style="f1Style(item.re_relaxed_f1)") {{ fmt(item.re_relaxed_f1) }}
      template(#item.re_relaxed_partial_f1="{ item }")
        span(:style="f1Style(item.re_relaxed_partial_f1)") {{ fmt(item.re_relaxed_partial_f1) }}
      template(#item.re_strict_f1="{ item }")
        span(:style="f1Style(item.re_strict_f1)") {{ fmt(item.re_strict_f1) }}
      template(#item.re_strict_partial_f1="{ item }")
        span(:style="f1Style(item.re_strict_partial_f1)") {{ fmt(item.re_strict_partial_f1) }}
      template(#bottom)

    h3.text-subtitle-1.font-weight-bold.mt-6.mb-2 MultiSciERE Label Set Comparison
    v-row.mb-3(dense align="center")
      v-col(cols="6" sm="3" md="2")
        v-select(v-model="filterGenTestDs" :items="DS" label="Test dataset" density="compact" variant="outlined" hide-details)
    p.text-caption.text-medium-emphasis.mb-3 Unified label set · test split · all three multi-sciere label spaces on {{ filterGenTestDs }}
    v-data-table(
      :headers="generalizationHeaders"
      :items="labelSetComparisonRows"
      :sort-by="[{ key: 'train_ds', order: 'asc' }]"
      :cell-props="summaryCellProps"
      :items-per-page="-1"
      density="compact" hover class="grouped-table"
    )
      template(#item.train_ds="{ item }")
        v-chip(:color="dsColor(item.train_ds)" size="small" variant="tonal") {{ item.train_ds }}
      template(#item.test_ds="{ item }")
        v-chip(:color="dsColor(item.test_ds)" size="small" variant="tonal") {{ item.test_ds }}
      template(#item.ner_exact_f1="{ item }")
        span(:style="f1Style(item.ner_exact_f1)") {{ fmt(item.ner_exact_f1) }}
      template(#item.ner_partial_f1="{ item }")
        span(:style="f1Style(item.ner_partial_f1)") {{ fmt(item.ner_partial_f1) }}
      template(#item.re_relaxed_f1="{ item }")
        span(:style="f1Style(item.re_relaxed_f1)") {{ fmt(item.re_relaxed_f1) }}
      template(#item.re_relaxed_partial_f1="{ item }")
        span(:style="f1Style(item.re_relaxed_partial_f1)") {{ fmt(item.re_relaxed_partial_f1) }}
      template(#item.re_strict_f1="{ item }")
        span(:style="f1Style(item.re_strict_f1)") {{ fmt(item.re_strict_f1) }}
      template(#item.re_strict_partial_f1="{ item }")
        span(:style="f1Style(item.re_strict_partial_f1)") {{ fmt(item.re_strict_partial_f1) }}
      template(#bottom)

  v-snackbar(v-model="snack.show" :color="snack.color" timeout="4000") {{ snack.message }}
</template>

<script setup>
import { ref, computed } from 'vue'
import { useDockerMode } from '../composables/useDockerMode.js'

const DS = ['gsap-ere', 'scier', 'scinlp']
const TRAIN_DS = [...DS, 'unified-sciere']
const DS_COLORS = { 'gsap-ere': 'blue', 'scier': 'green', 'scinlp': 'orange', 'unified-sciere': 'purple', 'multi-sciere-gsap': 'deep-orange', 'multi-sciere-scier': 'deep-orange', 'multi-sciere-scinlp': 'deep-orange' }
const DATASET_TO_PRED_LS = { 'gsap-ere': 'gsap', 'scier': 'scier', 'scinlp': 'scinlp' }
function dsColor(ds) { return DS_COLORS[ds] ?? 'grey' }

const { dockerMode } = useDockerMode()
const building         = ref(false)
const generatedAt      = ref(null)
const allSummary       = ref([])
const allEntities      = ref([])
const allRelations     = ref([])
const multiSciereSummary = ref([])
const snack            = ref({ show: false, message: '', color: 'success' })
const activeTab        = ref('summary')

const filterGenDs      = ref('scinlp')
const filterSplit      = ref('test')
const filterSplitLabel = ref('test')
const filterTrainDs    = ref('(all)')
const filterTestDs     = ref('(all)')
const filterNerMatch   = ref('partial')
const filterReMatch    = ref('relaxed')

// ── colors ────────────────────────────────────────────────────────────────────
const C_P  = '#1565c0'
const C_R  = '#c62828'
const C_F1 = '#2e7d32'
const BG_P  = 'rgba(21,101,192,0.07)'
const BG_R  = 'rgba(198,40,40,0.07)'
const BG_F1 = 'rgba(46,125,50,0.07)'

function pStyle(v) {
  if (v == null) return 'color:#9e9e9e;'
  const t = Math.max(0, Math.min(1, v / 100))
  return `color:rgb(${Math.round(180-t*159)},${Math.round(210-t*109)},${Math.round(245-t*53)});font-weight:600;`
}
function rStyle(v) {
  if (v == null) return 'color:#9e9e9e;'
  const t = Math.max(0, Math.min(1, v / 100))
  return `color:rgb(${Math.round(245-t*47)},${Math.round(180-t*140)},${Math.round(180-t*140)});font-weight:600;`
}
function f1Style(v) {
  if (v == null) return 'color:#9e9e9e;'
  const t = Math.max(0, Math.min(1, v / 100))
  return `color:rgb(${Math.round(220-t*150)},${Math.round(100+t*100)},60);font-weight:600;`
}
function fmt(v) { return v != null ? v.toFixed(1) : '–' }

// ── summary table ─────────────────────────────────────────────────────────────
const summaryHeaders = computed(() => {
  const h = [
    { key: 'train_ds',      title: 'Train',  sortable: true },
    { key: 'test_ds',       title: 'Test',   sortable: true },
    ...(filterSplit.value === '(both)' ? [{ key: 'split', title: 'Split', sortable: true }] : []),
    { key: 'ner_exact_f1',          title: 'NER',      sortable: true, align: 'end' },
    { key: 'ner_partial_f1',        title: 'NER≈',     sortable: true, align: 'end' },
    { key: 're_relaxed_f1',         title: 'RE',       sortable: true, align: 'end' },
    { key: 're_relaxed_partial_f1', title: 'RE≈',      sortable: true, align: 'end' },
    { key: 're_strict_f1',          title: 'RE+',      sortable: true, align: 'end' },
    { key: 're_strict_partial_f1',  title: 'RE+≈',     sortable: true, align: 'end' },
  ]
  return h
})

const F1_KEYS = new Set(['ner_exact_f1','ner_partial_f1','re_relaxed_f1','re_relaxed_partial_f1','re_strict_f1','re_strict_partial_f1'])
function summaryCellProps({ column }) {
  if (F1_KEYS.has(column?.key)) return { style: `background:${BG_F1};` }
  return {}
}

const summaryRows = computed(() =>
  allSummary.value.filter(r => filterSplit.value === '(both)' || r.split === filterSplit.value)
)

// ── MultiSciERE Generalization tab ────────────────────────────────────────────
const generalizationHeaders = [
  { key: 'train_ds',             title: 'Train',  sortable: true },
  { key: 'test_ds',              title: 'Test',   sortable: true },
  { key: 'ner_exact_f1',         title: 'NER',    sortable: true, align: 'end' },
  { key: 'ner_partial_f1',       title: 'NER≈',   sortable: true, align: 'end' },
  { key: 're_relaxed_f1',        title: 'RE',     sortable: true, align: 'end' },
  { key: 're_relaxed_partial_f1',title: 'RE≈',    sortable: true, align: 'end' },
  { key: 're_strict_f1',         title: 'RE+',    sortable: true, align: 'end' },
  { key: 're_strict_partial_f1', title: 'RE+≈',   sortable: true, align: 'end' },
]

const generalizationRows = computed(() => {
  const ds        = filterGenDs.value
  const predLs    = DATASET_TO_PRED_LS[ds]
  const multiName = `multi-sciere-${predLs}`

  const baseRows = allSummary.value
    .filter(r => r.train_ds === ds && r.split === 'test')

  const multiRows = multiSciereSummary.value
    .filter(r => r.label_set === 'unified' && r.trained_on === multiName)
    .map(r => ({
      train_ds:              multiName,
      test_ds:               r.dataset,
      ner_exact_f1:          r.ner_exact_f1,
      ner_partial_f1:        r.ner_partial_f1,
      re_relaxed_f1:         r.re_relaxed_f1,
      re_relaxed_partial_f1: r.re_relaxed_partial_f1,
      re_strict_f1:          r.re_strict_f1,
      re_strict_partial_f1:  r.re_strict_partial_f1,
    }))

  return [...baseRows, ...multiRows]
})

const filterGenTestDs = ref('gsap-ere')

const labelSetComparisonRows = computed(() =>
  multiSciereSummary.value
    .filter(r => r.label_set === 'unified' && r.dataset === filterGenTestDs.value)
    .map(r => ({
      train_ds:              r.trained_on,
      test_ds:               r.dataset,
      ner_exact_f1:          r.ner_exact_f1,
      ner_partial_f1:        r.ner_partial_f1,
      re_relaxed_f1:         r.re_relaxed_f1,
      re_relaxed_partial_f1: r.re_relaxed_partial_f1,
      re_strict_f1:          r.re_strict_f1,
      re_strict_partial_f1:  r.re_strict_partial_f1,
    }))
)

// ── label tables ──────────────────────────────────────────────────────────────
const labelHeaders = [
  { title: 'Train',  key: 'train_ds', sortable: true },
  { title: 'Test',   key: 'test_ds',  sortable: true },
  { title: 'Split',  key: 'split',    sortable: true },
  { title: 'Match',  key: 'match',    sortable: true },
  { title: 'Label',  key: 'label',    sortable: true },
  { title: 'P',      key: 'precision',sortable: true, align: 'end' },
  { title: 'R',      key: 'recall',   sortable: true, align: 'end' },
  { title: 'F1',     key: 'f1',       sortable: true, align: 'end' },
]

function labelCellProps({ column }) {
  if (column?.key === 'precision') return { style: `background:${BG_P};` }
  if (column?.key === 'recall')    return { style: `background:${BG_R};` }
  if (column?.key === 'f1')        return { style: `background:${BG_F1};` }
  return {}
}

const AGGREGATE_LABELS = new Set(['micro', 'macro', 'weighted'])

function filterEntity(r) {
  if (filterTrainDs.value    !== '(all)' && r.train_ds !== filterTrainDs.value)  return false
  if (filterTestDs.value     !== '(all)' && r.test_ds  !== filterTestDs.value)   return false
  if (filterSplitLabel.value !== '(both)' && r.split   !== filterSplitLabel.value) return false
  if (filterNerMatch.value   !== '(both)' && r.match   !== filterNerMatch.value)  return false
  return true
}
function filterRelation(r) {
  if (filterTrainDs.value    !== '(all)' && r.train_ds !== filterTrainDs.value)  return false
  if (filterTestDs.value     !== '(all)' && r.test_ds  !== filterTestDs.value)   return false
  if (filterSplitLabel.value !== '(both)' && r.split   !== filterSplitLabel.value) return false
  if (filterReMatch.value    !== '(both)' && r.match   !== filterReMatch.value)   return false
  return true
}

const entityLabelRows   = computed(() => allEntities.value.filter(r =>  filterEntity(r)   && !AGGREGATE_LABELS.has(r.label)))
const entityAggRows     = computed(() => allEntities.value.filter(r =>  filterEntity(r)   &&  AGGREGATE_LABELS.has(r.label)))
const relationLabelRows = computed(() => allRelations.value.filter(r => filterRelation(r) && !AGGREGATE_LABELS.has(r.label)))
const relationAggRows   = computed(() => allRelations.value.filter(r => filterRelation(r) &&  AGGREGATE_LABELS.has(r.label)))

// ── fetch / rebuild ───────────────────────────────────────────────────────────
async function fetchData() {
  try {
    const [cdRes, msRes] = await Promise.all([
      fetch('/api/cross-dataset'),
      fetch('/api/multi-sciere'),
    ])
    if (!cdRes.ok) { snack.value = { show: true, message: 'No cross-dataset data yet — click Rebuild.', color: 'warning' }; return }
    const data = await cdRes.json()
    generatedAt.value  = data.generated_at ? new Date(data.generated_at).toLocaleString() : null
    allSummary.value   = data.summary         ?? []
    allEntities.value  = data.entity_labels   ?? []
    allRelations.value = data.relation_labels ?? []
    if (msRes.ok) {
      const msData = await msRes.json()
      multiSciereSummary.value = msData.summary ?? []
    }
  } catch (e) {
    snack.value = { show: true, message: `Failed to load: ${e.message}`, color: 'error' }
  }
}

async function rebuild() {
  building.value = true
  try {
    const res  = await fetch('/api/cross-dataset/build', { method: 'POST' })
    const data = await res.json()
    if (data.ok) { snack.value = { show: true, message: 'Rebuilt successfully.', color: 'success' }; await fetchData() }
    else snack.value = { show: true, message: `Failed: ${data.stderr?.slice(0, 200)}`, color: 'error' }
  } catch (e) {
    snack.value = { show: true, message: `Error: ${e.message}`, color: 'error' }
  } finally {
    building.value = false
  }
}

fetchData()
</script>
