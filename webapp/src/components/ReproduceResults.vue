<template lang="pug">
v-container(fluid)
  .d-flex.align-center.mb-3
    h2.text-h5 Reproduce Results
    v-chip.ml-3(v-if="generatedAt" size="small" variant="tonal" color="grey") {{ generatedAt }}
    v-spacer
    v-btn(v-if="!dockerMode" variant="text" prepend-icon="mdi-refresh" size="small" :loading="building" @click="rebuild") Rebuild

  v-tabs(v-model="activeTab" density="compact" color="primary" class="mb-4")
    v-tab(value="summary") Summary
    v-tab(value="entities") Entities
    v-tab(value="relations") Relations

  //- ── Summary tab ────────────────────────────────────────────────────────
  div(v-if="activeTab === 'summary'")
    h3.text-subtitle-1.font-weight-bold.mb-2 Comparison with Paper-Reported Results
    v-data-table(
      :headers="compHeaders"
      :items="compRows"
      :sort-by="[{ key: 'dataset', order: 'asc' }]"
      :cell-props="compCellProps"
      :items-per-page="-1"
      density="compact" hover class="grouped-table"
    )
      template(#bottom)
      template(#headers="{ columns, isSorted, getSortIcon, toggleSort }")
        tr
          th.v-data-table__th.text-start(rowspan="2" style="border-right:1px solid rgba(0,0,0,0.08);cursor:pointer;" @click="toggleSort(col(columns,'dataset'))")
            | Dataset
            v-icon(v-if="isSorted(col(columns,'dataset'))" size="14") {{ getSortIcon(col(columns,'dataset')) }}
          th.v-data-table__th.text-center(colspan="3" style="border-bottom:2px solid #1565c0;border-right:1px solid rgba(0,0,0,0.12);color:#1565c0;font-weight:700;") NER
          th.v-data-table__th.text-center(colspan="3" style="border-bottom:2px solid #6a1b9a;border-right:1px solid rgba(0,0,0,0.12);color:#6a1b9a;font-weight:700;") RE
          th.v-data-table__th.text-center(colspan="3" style="border-bottom:2px solid #4a148c;color:#4a148c;font-weight:700;") RE+
        tr
          th.v-data-table__th.text-end(
            v-for="c in compSubCols" :key="c.key"
            @click="toggleSort(col(columns, c.key))"
            style="cursor:pointer;white-space:nowrap;"
            :style="c.style"
          )
            | {{ c.label }}
            v-icon(v-if="isSorted(col(columns,c.key))" size="14") {{ getSortIcon(col(columns,c.key)) }}
      template(#item.dataset="{ item }")
        v-chip(:color="datasetColor(item.dataset)" size="small" variant="tonal") {{ item.dataset }}
      template(#item.ner_exact_f1="{ item }")
        span(:style="f1Style(item.ner_exact_f1)") {{ item.ner_exact_f1 }}
      template(#item.re_relaxed_f1="{ item }")
        span(:style="f1Style(item.re_relaxed_f1)") {{ item.re_relaxed_f1 }}
      template(#item.re_strict_f1="{ item }")
        span(:style="f1Style(item.re_strict_f1)") {{ item.re_strict_f1 }}
      template(#item.ner_reported="{ item }")
        span(:class="item.ner_reported == null ? 'text-disabled' : 'text-medium-emphasis'") {{ item.ner_reported ?? '–' }}
      template(#item.re_reported="{ item }")
        span(:class="item.re_reported == null ? 'text-disabled' : 'text-medium-emphasis'") {{ item.re_reported ?? '–' }}
      template(#item.rep_reported="{ item }")
        span(:class="item.rep_reported == null ? 'text-disabled' : 'text-medium-emphasis'") {{ item.rep_reported ?? '–' }}
      template(#item.ner_delta="{ item }")
        span(v-if="item.ner_delta != null" :class="item.ner_delta >= 0 ? 'text-success font-weight-medium' : 'text-error font-weight-medium'") {{ item.ner_delta >= 0 ? '+' : '' }}{{ item.ner_delta.toFixed(1) }}
        span(v-else class="text-disabled") –
      template(#item.re_delta="{ item }")
        span(v-if="item.re_delta != null" :class="item.re_delta >= 0 ? 'text-success font-weight-medium' : 'text-error font-weight-medium'") {{ item.re_delta >= 0 ? '+' : '' }}{{ item.re_delta.toFixed(1) }}
        span(v-else class="text-disabled") –
      template(#item.rep_delta="{ item }")
        span(v-if="item.rep_delta != null" :class="item.rep_delta >= 0 ? 'text-success font-weight-medium' : 'text-error font-weight-medium'") {{ item.rep_delta >= 0 ? '+' : '' }}{{ item.rep_delta.toFixed(1) }}
        span(v-else class="text-disabled") –

    h3.text-subtitle-1.font-weight-bold.mt-6.mb-2 Micro-averaged P / R / F1
    v-data-table(
      :headers="perfHeaders"
      :items="allSummary"
      :sort-by="[{ key: 'dataset', order: 'asc' }]"
      :cell-props="perfCellProps"
      :items-per-page="-1"
      density="compact" hover class="grouped-table"
    )
      template(#bottom)
      template(#headers="{ columns, isSorted, getSortIcon, toggleSort }")
        tr
          th.v-data-table__th.text-start(rowspan="2" style="border-right:1px solid rgba(0,0,0,0.08);cursor:pointer;" @click="toggleSort(col(columns,'dataset'))")
            | Dataset
            v-icon(v-if="isSorted(col(columns,'dataset'))" size="14") {{ getSortIcon(col(columns,'dataset')) }}
          th.v-data-table__th.text-start(rowspan="2" style="border-right:1px solid rgba(0,0,0,0.12);cursor:pointer;" @click="toggleSort(col(columns,'label_set'))")
            | Label set
            v-icon(v-if="isSorted(col(columns,'label_set'))" size="14") {{ getSortIcon(col(columns,'label_set')) }}
          th.v-data-table__th.text-center(colspan="3" style="border-bottom:2px solid #1565c0;border-right:1px solid rgba(0,0,0,0.12);color:#1565c0;font-weight:700;") NER
          th.v-data-table__th.text-center(colspan="3" style="border-bottom:2px solid #1565c0;border-right:1px solid rgba(0,0,0,0.12);color:#1565c0;font-weight:700;opacity:0.7;") NER≈
          th.v-data-table__th.text-center(colspan="3" style="border-bottom:2px solid #6a1b9a;border-right:1px solid rgba(0,0,0,0.12);color:#6a1b9a;font-weight:700;") RE
          th.v-data-table__th.text-center(colspan="3" style="border-bottom:2px solid #6a1b9a;border-right:1px solid rgba(0,0,0,0.12);color:#6a1b9a;font-weight:700;opacity:0.7;") RE≈
          th.v-data-table__th.text-center(colspan="3" style="border-bottom:2px solid #4a148c;border-right:1px solid rgba(0,0,0,0.12);color:#4a148c;font-weight:700;") RE+
          th.v-data-table__th.text-center(colspan="3" style="border-bottom:2px solid #4a148c;color:#4a148c;font-weight:700;opacity:0.7;") RE+≈
        tr
          th.v-data-table__th.text-end(
            v-for="c in perfSubCols" :key="c.key"
            @click="toggleSort(col(columns, c.key))"
            style="cursor:pointer;white-space:nowrap;"
            :style="c.style"
          )
            | {{ c.label }}
            v-icon(v-if="isSorted(col(columns,c.key))" size="14") {{ getSortIcon(col(columns,c.key)) }}
      template(#item.dataset="{ item }")
        v-chip(:color="datasetColor(item.dataset)" size="small" variant="tonal") {{ item.dataset }}
      template(#item.label_set="{ item }")
        v-chip(size="x-small" :color="item.label_set === 'unified' ? 'secondary' : 'default'" variant="tonal") {{ item.label_set }}
      template(#item.ner_exact_precision="{ item }")
        span(:style="pStyle(item.ner_exact_precision)") {{ item.ner_exact_precision }}
      template(#item.ner_exact_recall="{ item }")
        span(:style="rStyle(item.ner_exact_recall)") {{ item.ner_exact_recall }}
      template(#item.ner_exact_f1="{ item }")
        span(:style="f1Style(item.ner_exact_f1)") {{ item.ner_exact_f1 }}
      template(#item.ner_partial_precision="{ item }")
        span(:style="pStyle(item.ner_partial_precision)") {{ item.ner_partial_precision }}
      template(#item.ner_partial_recall="{ item }")
        span(:style="rStyle(item.ner_partial_recall)") {{ item.ner_partial_recall }}
      template(#item.ner_partial_f1="{ item }")
        span(:style="f1Style(item.ner_partial_f1)") {{ item.ner_partial_f1 }}
      template(#item.re_relaxed_precision="{ item }")
        span(:style="pStyle(item.re_relaxed_precision)") {{ item.re_relaxed_precision }}
      template(#item.re_relaxed_recall="{ item }")
        span(:style="rStyle(item.re_relaxed_recall)") {{ item.re_relaxed_recall }}
      template(#item.re_relaxed_f1="{ item }")
        span(:style="f1Style(item.re_relaxed_f1)") {{ item.re_relaxed_f1 }}
      template(#item.re_relaxed_partial_precision="{ item }")
        span(:style="pStyle(item.re_relaxed_partial_precision)") {{ item.re_relaxed_partial_precision }}
      template(#item.re_relaxed_partial_recall="{ item }")
        span(:style="rStyle(item.re_relaxed_partial_recall)") {{ item.re_relaxed_partial_recall }}
      template(#item.re_relaxed_partial_f1="{ item }")
        span(:style="f1Style(item.re_relaxed_partial_f1)") {{ item.re_relaxed_partial_f1 }}
      template(#item.re_strict_precision="{ item }")
        span(:style="pStyle(item.re_strict_precision)") {{ item.re_strict_precision }}
      template(#item.re_strict_recall="{ item }")
        span(:style="rStyle(item.re_strict_recall)") {{ item.re_strict_recall }}
      template(#item.re_strict_f1="{ item }")
        span(:style="f1Style(item.re_strict_f1)") {{ item.re_strict_f1 }}
      template(#item.re_strict_partial_precision="{ item }")
        span(:style="pStyle(item.re_strict_partial_precision)") {{ item.re_strict_partial_precision }}
      template(#item.re_strict_partial_recall="{ item }")
        span(:style="rStyle(item.re_strict_partial_recall)") {{ item.re_strict_partial_recall }}
      template(#item.re_strict_partial_f1="{ item }")
        span(:style="f1Style(item.re_strict_partial_f1)") {{ item.re_strict_partial_f1 }}

  //- ── Entity label-wise tab ───────────────────────────────────────────────
  div(v-if="activeTab === 'entities'")
    v-row.mb-3(dense align="center")
      v-col(cols="6" sm="3" md="2")
        v-select(v-model="filterDataset" :items="['(all)', 'gsap-ere', 'scier', 'scinlp']" label="Dataset" density="compact" variant="outlined" hide-details)
      v-col(cols="6" sm="3" md="2")
        v-select(v-model="filterLabelSet" :items="['original', 'unified', '(both)']" label="Label set" density="compact" variant="outlined" hide-details)
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
      template(#item.dataset="{ item }")
        v-chip(:color="datasetColor(item.dataset)" size="small" variant="tonal") {{ item.dataset }}
      template(#item.label_set="{ item }")
        v-chip(size="x-small" :color="item.label_set === 'unified' ? 'secondary' : 'default'" variant="tonal") {{ item.label_set }}
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
          v-for="row in entityAggRows" :key="`${row.dataset}-${row.label_set}-${row.match}-${row.label}`"
          style="border-top:2px solid rgba(0,0,0,0.15);background:rgba(0,0,0,0.03);font-weight:600;"
        )
          td
            v-chip(:color="datasetColor(row.dataset)" size="small" variant="tonal") {{ row.dataset }}
          td
            v-chip(size="x-small" :color="row.label_set === 'unified' ? 'secondary' : 'default'" variant="tonal") {{ row.label_set }}
          td
            span.text-caption.text-medium-emphasis {{ row.match }}
          td {{ row.label }}
          td.text-end(:style="`background:${BG_P};${pStyle(row.precision)}`") {{ row.precision.toFixed(1) }}
          td.text-end(:style="`background:${BG_R};${rStyle(row.recall)}`") {{ row.recall.toFixed(1) }}
          td.text-end(:style="BG_F1") #[span(:style="f1Style(row.f1)") {{ row.f1.toFixed(1) }}]
      template(#bottom)

  //- ── Relation label-wise tab ─────────────────────────────────────────────
  div(v-if="activeTab === 'relations'")
    v-row.mb-3(dense align="center")
      v-col(cols="6" sm="3" md="2")
        v-select(v-model="filterDataset" :items="['(all)', 'gsap-ere', 'scier', 'scinlp']" label="Dataset" density="compact" variant="outlined" hide-details)
      v-col(cols="6" sm="3" md="2")
        v-select(v-model="filterLabelSet" :items="['original', 'unified', '(both)']" label="Label set" density="compact" variant="outlined" hide-details)
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
      template(#item.dataset="{ item }")
        v-chip(:color="datasetColor(item.dataset)" size="small" variant="tonal") {{ item.dataset }}
      template(#item.label_set="{ item }")
        v-chip(size="x-small" :color="item.label_set === 'unified' ? 'secondary' : 'default'" variant="tonal") {{ item.label_set }}
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
          v-for="row in relationAggRows" :key="`${row.dataset}-${row.label_set}-${row.match}-${row.label}`"
          style="border-top:2px solid rgba(0,0,0,0.15);background:rgba(0,0,0,0.03);font-weight:600;"
        )
          td
            v-chip(:color="datasetColor(row.dataset)" size="small" variant="tonal") {{ row.dataset }}
          td
            v-chip(size="x-small" :color="row.label_set === 'unified' ? 'secondary' : 'default'" variant="tonal") {{ row.label_set }}
          td
            span.text-caption.text-medium-emphasis {{ row.match }}
          td {{ row.label }}
          td.text-end(:style="`background:${BG_P};${pStyle(row.precision)}`") {{ row.precision.toFixed(1) }}
          td.text-end(:style="`background:${BG_R};${rStyle(row.recall)}`") {{ row.recall.toFixed(1) }}
          td.text-end(:style="BG_F1") #[span(:style="f1Style(row.f1)") {{ row.f1.toFixed(1) }}]
      template(#bottom)

  v-snackbar(v-model="snack.show" :color="snack.color" timeout="4000") {{ snack.message }}
</template>

<script setup>
import { ref, computed } from 'vue'
import { useDockerMode } from '../composables/useDockerMode.js'

const { dockerMode } = useDockerMode()
const building    = ref(false)
const generatedAt = ref(null)
const allSummary  = ref([])
const allLabels   = ref([])
const reported    = ref({})
const snack       = ref({ show: false, message: '', color: 'success' })
const activeTab   = ref('summary')

const filterDataset  = ref('(all)')
const filterLabelSet = ref('original')
const filterNerMatch = ref('exact')
const filterReMatch  = ref('relaxed')

const DATASET_COLORS = { 'gsap-ere': 'blue', 'scier': 'green', 'scinlp': 'orange' }
function datasetColor(ds) { return DATASET_COLORS[ds] ?? 'grey' }

// Column header color constants
const C_P  = '#1565c0'   // blue
const C_R  = '#c62828'   // red
const C_F1 = '#2e7d32'   // green
const C_PAPER = '#546e7a'
const C_DELTA = '#37474f'

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
  const r = Math.round(220 - t * 150)
  const g = Math.round(100 + t * 100)
  return `color:rgb(${r},${g},60);font-weight:600;`
}

function col(columns, key) { return columns.find(c => c.key === key) ?? { key } }

// ── Summary perf table ────────────────────────────────────────────────────────
const perfHeaders = [
  { key: 'dataset',                       title: 'Dataset',   sortable: true },
  { key: 'label_set',                     title: 'Label set', sortable: true },
  { key: 'ner_exact_precision',           title: 'P',         sortable: true, align: 'end' },
  { key: 'ner_exact_recall',              title: 'R',         sortable: true, align: 'end' },
  { key: 'ner_exact_f1',                  title: 'F1',        sortable: true, align: 'end' },
  { key: 'ner_partial_precision',         title: 'P',         sortable: true, align: 'end' },
  { key: 'ner_partial_recall',            title: 'R',         sortable: true, align: 'end' },
  { key: 'ner_partial_f1',                title: 'F1',        sortable: true, align: 'end' },
  { key: 're_relaxed_precision',          title: 'P',         sortable: true, align: 'end' },
  { key: 're_relaxed_recall',             title: 'R',         sortable: true, align: 'end' },
  { key: 're_relaxed_f1',                 title: 'F1',        sortable: true, align: 'end' },
  { key: 're_relaxed_partial_precision',  title: 'P',         sortable: true, align: 'end' },
  { key: 're_relaxed_partial_recall',     title: 'R',         sortable: true, align: 'end' },
  { key: 're_relaxed_partial_f1',         title: 'F1',        sortable: true, align: 'end' },
  { key: 're_strict_precision',           title: 'P',         sortable: true, align: 'end' },
  { key: 're_strict_recall',              title: 'R',         sortable: true, align: 'end' },
  { key: 're_strict_f1',                  title: 'F1',        sortable: true, align: 'end' },
  { key: 're_strict_partial_precision',   title: 'P',         sortable: true, align: 'end' },
  { key: 're_strict_partial_recall',      title: 'R',         sortable: true, align: 'end' },
  { key: 're_strict_partial_f1',          title: 'F1',        sortable: true, align: 'end' },
]

const BG_P  = 'rgba(21,101,192,0.07)'
const BG_R  = 'rgba(198,40,40,0.07)'
const BG_F1 = 'rgba(46,125,50,0.07)'
const BG_PAPER = 'rgba(84,110,122,0.06)'
const BG_DELTA = 'rgba(55,71,79,0.04)'

const PERF_P_KEYS  = new Set(['ner_exact_precision','ner_partial_precision','re_relaxed_precision','re_relaxed_partial_precision','re_strict_precision','re_strict_partial_precision'])
const PERF_R_KEYS  = new Set(['ner_exact_recall','ner_partial_recall','re_relaxed_recall','re_relaxed_partial_recall','re_strict_recall','re_strict_partial_recall'])
const PERF_F1_KEYS = new Set(['ner_exact_f1','ner_partial_f1','re_relaxed_f1','re_relaxed_partial_f1','re_strict_f1','re_strict_partial_f1'])
const COMP_F1_KEYS = new Set(['ner_exact_f1','re_relaxed_f1','re_strict_f1'])
const COMP_PAPER_KEYS = new Set(['ner_reported','re_reported','rep_reported'])
const COMP_DELTA_KEYS = new Set(['ner_delta','re_delta','rep_delta'])

function perfCellProps({ column }) {
  const k = column?.key
  if (PERF_P_KEYS.has(k))  return { style: `background:${BG_P};` }
  if (PERF_R_KEYS.has(k))  return { style: `background:${BG_R};` }
  if (PERF_F1_KEYS.has(k)) return { style: `background:${BG_F1};` }
  return {}
}
function compCellProps({ column }) {
  const k = column?.key
  if (COMP_F1_KEYS.has(k))    return { style: `background:${BG_F1};` }
  if (COMP_PAPER_KEYS.has(k)) return { style: `background:${BG_PAPER};` }
  if (COMP_DELTA_KEYS.has(k)) return { style: `background:${BG_DELTA};` }
  return {}
}
function labelCellProps({ column }) {
  const k = column?.key
  if (k === 'precision') return { style: `background:${BG_P};` }
  if (k === 'recall')    return { style: `background:${BG_R};` }
  if (k === 'f1')        return { style: `background:${BG_F1};` }
  return {}
}

const SEP = 'border-right:1px solid rgba(0,0,0,0.12);'
const perfSubCols = [
  { key: 'ner_exact_precision',          label: 'P',  style: `color:${C_P};background:${BG_P};`  },
  { key: 'ner_exact_recall',             label: 'R',  style: `color:${C_R};background:${BG_R};`  },
  { key: 'ner_exact_f1',                 label: 'F1', style: `color:${C_F1};background:${BG_F1};` },
  { key: 'ner_partial_precision',        label: 'P',  style: `color:${C_P};background:${BG_P};opacity:0.8;`  },
  { key: 'ner_partial_recall',           label: 'R',  style: `color:${C_R};background:${BG_R};opacity:0.8;`  },
  { key: 'ner_partial_f1',               label: 'F1', style: `color:${C_F1};background:${BG_F1};opacity:0.8;${SEP}` },
  { key: 're_relaxed_precision',         label: 'P',  style: `color:${C_P};background:${BG_P};`  },
  { key: 're_relaxed_recall',            label: 'R',  style: `color:${C_R};background:${BG_R};`  },
  { key: 're_relaxed_f1',                label: 'F1', style: `color:${C_F1};background:${BG_F1};` },
  { key: 're_relaxed_partial_precision', label: 'P',  style: `color:${C_P};background:${BG_P};opacity:0.8;`  },
  { key: 're_relaxed_partial_recall',    label: 'R',  style: `color:${C_R};background:${BG_R};opacity:0.8;`  },
  { key: 're_relaxed_partial_f1',        label: 'F1', style: `color:${C_F1};background:${BG_F1};opacity:0.8;${SEP}` },
  { key: 're_strict_precision',          label: 'P',  style: `color:${C_P};background:${BG_P};`  },
  { key: 're_strict_recall',             label: 'R',  style: `color:${C_R};background:${BG_R};`  },
  { key: 're_strict_f1',                 label: 'F1', style: `color:${C_F1};background:${BG_F1};` },
  { key: 're_strict_partial_precision',  label: 'P',  style: `color:${C_P};background:${BG_P};opacity:0.8;`  },
  { key: 're_strict_partial_recall',     label: 'R',  style: `color:${C_R};background:${BG_R};opacity:0.8;`  },
  { key: 're_strict_partial_f1',         label: 'F1', style: `color:${C_F1};background:${BG_F1};opacity:0.8;` },
]

// ── Summary comparison table (raw only) ───────────────────────────────────────
const compHeaders = [
  { key: 'dataset',       title: 'Dataset',     sortable: true },
  { key: 'ner_exact_f1', title: 'NER F1',       sortable: true, align: 'end' },
  { key: 'ner_reported', title: 'NER Paper',    sortable: true, align: 'end' },
  { key: 'ner_delta',    title: 'Δ NER',        sortable: true, align: 'end' },
  { key: 're_relaxed_f1',title: 'RE F1',        sortable: true, align: 'end' },
  { key: 're_reported',  title: 'RE Paper',     sortable: true, align: 'end' },
  { key: 're_delta',     title: 'Δ RE',         sortable: true, align: 'end' },
  { key: 're_strict_f1', title: 'RE+ F1',       sortable: true, align: 'end' },
  { key: 'rep_reported', title: 'RE+ Paper',    sortable: true, align: 'end' },
  { key: 'rep_delta',    title: 'Δ RE+',        sortable: true, align: 'end' },
]

const compSubCols = [
  { key: 'ner_exact_f1',  label: 'F1',    style: `color:${C_F1};background:${BG_F1};`       },
  { key: 'ner_reported',  label: 'Paper', style: `color:${C_PAPER};background:${BG_PAPER};` },
  { key: 'ner_delta',     label: 'Δ',     style: `color:${C_DELTA};background:${BG_DELTA};border-right:1px solid rgba(0,0,0,0.12);` },
  { key: 're_relaxed_f1', label: 'F1',    style: `color:${C_F1};background:${BG_F1};`       },
  { key: 're_reported',   label: 'Paper', style: `color:${C_PAPER};background:${BG_PAPER};` },
  { key: 're_delta',      label: 'Δ',     style: `color:${C_DELTA};background:${BG_DELTA};border-right:1px solid rgba(0,0,0,0.12);` },
  { key: 're_strict_f1',  label: 'F1',    style: `color:${C_F1};background:${BG_F1};`       },
  { key: 'rep_reported',  label: 'Paper', style: `color:${C_PAPER};background:${BG_PAPER};` },
  { key: 'rep_delta',     label: 'Δ',     style: `color:${C_DELTA};background:${BG_DELTA};` },
]

const compRows = computed(() =>
  allSummary.value
    .filter(r => r.label_set === 'original')
    .map(r => {
      const rep = reported.value[r.dataset] ?? {}
      return {
        ...r,
        ner_reported: rep.NER    ?? null,
        ner_delta:    rep.NER    != null ? +(r.ner_exact_f1  - rep.NER).toFixed(1)    : null,
        re_reported:  rep.RE     ?? null,
        re_delta:     rep.RE     != null ? +(r.re_relaxed_f1 - rep.RE).toFixed(1)     : null,
        rep_reported: rep['RE+'] ?? null,
        rep_delta:    rep['RE+'] != null ? +(r.re_strict_f1  - rep['RE+']).toFixed(1) : null,
      }
    })
)

// ── Label-wise tables ─────────────────────────────────────────────────────────
const labelHeaders = [
  { title: 'Dataset',   key: 'dataset',   sortable: true },
  { title: 'Label set', key: 'label_set', sortable: true },
  { title: 'Match',     key: 'match',     sortable: true },
  { title: 'Label',     key: 'label',     sortable: true },
  { title: 'P',         key: 'precision', sortable: true, align: 'end' },
  { title: 'R',         key: 'recall',    sortable: true, align: 'end' },
  { title: 'F1',        key: 'f1',        sortable: true, align: 'end' },
]

function filterNer(r) {
  if (r.task !== 'ner') return false
  if (filterDataset.value  !== '(all)'  && r.dataset   !== filterDataset.value)  return false
  if (filterLabelSet.value !== '(both)' && r.label_set !== filterLabelSet.value) return false
  if (filterNerMatch.value !== '(both)' && r.match     !== filterNerMatch.value) return false
  return true
}
function filterRe(r) {
  if (r.task !== 're') return false
  if (filterDataset.value  !== '(all)'  && r.dataset   !== filterDataset.value)  return false
  if (filterLabelSet.value !== '(both)' && r.label_set !== filterLabelSet.value) return false
  if (filterReMatch.value  !== '(both)' && r.match     !== filterReMatch.value)  return false
  return true
}

const AGGREGATE_LABELS = new Set(['micro', 'macro', 'weighted'])

const entityLabelRows  = computed(() => allLabels.value.filter(r => filterNer(r) && !AGGREGATE_LABELS.has(r.label)))
const entityAggRows    = computed(() => allLabels.value.filter(r => filterNer(r) &&  AGGREGATE_LABELS.has(r.label)))
const relationLabelRows = computed(() => allLabels.value.filter(r => filterRe(r) && !AGGREGATE_LABELS.has(r.label)))
const relationAggRows   = computed(() => allLabels.value.filter(r => filterRe(r) &&  AGGREGATE_LABELS.has(r.label)))

// ── data fetch ────────────────────────────────────────────────────────────────
async function fetchData() {
  try {
    const res  = await fetch('/api/reproduce')
    if (!res.ok) { snack.value = { show: true, message: 'No data yet — click Rebuild.', color: 'warning' }; return }
    const data = await res.json()
    generatedAt.value = data.generated_at ? new Date(data.generated_at).toLocaleString() : null
    allSummary.value  = data.summary  ?? []
    allLabels.value   = data.labels   ?? []
    reported.value    = data.reported ?? {}
  } catch (e) {
    snack.value = { show: true, message: `Failed to load: ${e.message}`, color: 'error' }
  }
}

async function rebuild() {
  building.value = true
  try {
    const res  = await fetch('/api/reproduce/build', { method: 'POST' })
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
