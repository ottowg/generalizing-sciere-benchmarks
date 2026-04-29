<template lang="pug">
v-container(fluid)
  .d-flex.align-center.mb-3
    h2.text-h5 Confusion Matrices
    v-spacer
    v-btn(
      v-if="!dockerMode"
      size="small" variant="text" prepend-icon="mdi-refresh"
      :loading="building"
      @click="buildData"
    ) Build

  //- ── Controls ────────────────────────────────────────────────────────────
  v-row.mb-2(dense align="center")
    v-col(cols="auto")
      .text-caption.text-medium-emphasis.mb-1 Test Dataset
      v-btn-toggle(v-model="dataset" mandatory density="compact" variant="outlined" color="primary")
        v-btn(value="gsap-ere" size="small") GSAP-ERE
        v-btn(value="scier"   size="small") SciER
        v-btn(value="scinlp"  size="small") SciNLP

    v-col(cols="auto")
      .text-caption.text-medium-emphasis.mb-1 Split
      v-btn-toggle(v-model="split" mandatory density="compact" variant="outlined" color="primary")
        v-btn(value="train" size="small") Train
        v-btn(value="dev"   size="small") Dev
        v-btn(value="test"  size="small") Test

    v-col(cols="auto")
      .text-caption.text-medium-emphasis.mb-1 Label set
      v-btn-toggle(v-model="labelset" mandatory density="compact" variant="outlined" color="teal")
        v-btn(value="unified"  size="small" prepend-icon="mdi-link-variant") Unified
        v-btn(value="original" size="small" prepend-icon="mdi-label-outline") Original

    v-col(cols="auto")
      .text-caption.text-medium-emphasis.mb-1 Row
      v-btn-toggle(v-model="annotRow" mandatory density="compact" variant="outlined" color="primary")
        v-btn(v-for="a in ANNOT_OPTIONS" :key="a.value" :value="a.value" size="small") {{ a.label }}

    v-col(cols="auto")
      .text-caption.text-medium-emphasis.mb-1 Column
      v-btn-toggle(v-model="annotCol" mandatory density="compact" variant="outlined" color="primary")
        v-btn(v-for="a in ANNOT_OPTIONS" :key="a.value" :value="a.value" size="small") {{ a.label }}

  //- ── Not built ───────────────────────────────────────────────────────────
  v-alert(
    v-if="notBuilt && !loading"
    type="info" variant="tonal" class="mb-4"
  )
    | No data yet.
    template(v-if="!dockerMode")
      |  Click
      strong  Build
      |  to precompute all combinations (runs the unification pipeline, takes a few minutes).

  //- ── Loading / error ─────────────────────────────────────────────────────
  v-alert(v-if="error && !notBuilt" type="error" variant="tonal" class="mb-3") {{ error }}

  v-progress-linear(v-if="loading || building" indeterminate color="primary" class="mb-3")

  //- ── Tabs ────────────────────────────────────────────────────────────────
  v-tabs(v-if="currentMatrix" v-model="activeTab" density="compact" color="primary" class="mb-3")
    v-tab(value="entities")  Entities
    v-tab(value="relations") Relations

  //- ── Display mode toggle ─────────────────────────────────────────────────
  .d-flex.align-center.mb-2(v-if="currentMatrix" style="gap:8px;")
    .text-caption.text-medium-emphasis Show:
    v-btn-toggle(v-model="displayMode" mandatory density="compact" variant="outlined" color="default" size="small")
      v-btn(value="count" size="small") Count
      v-btn(value="row%"  size="small") Row %

  //- ── Matrix table ────────────────────────────────────────────────────────
  template(v-if="currentMatrix && !loading")
    .text-caption.text-medium-emphasis.mb-1
      | Rows: {{ annotLabel(annotRow) }} &nbsp;·&nbsp; Columns: {{ annotLabel(annotCol) }}
    .overflow-auto(style="max-height:65vh;")
      table.confusion-table(@mouseleave="hoveredCol = null")
        thead
          tr
            th.label-cell
            th.col-header(
              v-for="(col, ci) in currentMatrix.labels_annot2" :key="col"
              :class="{ 'col-hl': hoveredCol === ci }"
            ) {{ col }}
            th.total-col Total
        tbody
          tr(v-for="(row, ri) in currentMatrix.matrix" :key="currentMatrix.labels_annot1[ri]")
            td.row-header {{ currentMatrix.labels_annot1[ri] }}
            td.cell(
              v-for="(val, ci) in row" :key="ci"
              :style="cellStyle(val, ri, ci)"
              :class="{ 'col-hl': hoveredCol === ci }"
              :title="`${currentMatrix.labels_annot1[ri]} → ${currentMatrix.labels_annot2[ci]}: ${val}`"
              @mouseenter="hoveredCol = ci"
            )
              span {{ displayMode === 'count' ? val : rowPct(val, ri) }}
            td.total-col {{ currentMatrix.totals_annot1[currentMatrix.labels_annot1[ri]] }}
          tr.total-row
            td.row-header Total
            td.total-col(
              v-for="(col, ci) in currentMatrix.labels_annot2" :key="col"
              :class="{ 'col-hl': hoveredCol === ci }"
            )
              | {{ currentMatrix.totals_annot2[col] }}
            td.total-col


  v-snackbar(v-model="snack.show" :color="snack.color" timeout="6000")
    | {{ snack.message }}
    template(#actions)
      v-btn(variant="text" @click="snack.show = false") Close
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useDockerMode } from '../composables/useDockerMode.js'

const { dockerMode } = useDockerMode()

const ANNOT_OPTIONS = [
  { value: 'gold',     label: 'Gold'     },
  { value: 'gsap-ere', label: 'GSAP-ERE' },
  { value: 'scier',    label: 'SciER'    },
  { value: 'scinlp',   label: 'SciNLP'   },
]
const ANNOT_LABEL_MAP = Object.fromEntries(ANNOT_OPTIONS.map(a => [a.value, a.label]))
function annotLabel(v) { return ANNOT_LABEL_MAP[v] ?? v }

// ── state ─────────────────────────────────────────────────────────────────────
const dataset     = ref('gsap-ere')
const split       = ref('dev')
const labelset    = ref('unified')
const annotRow    = ref('gold')
const annotCol    = ref('gsap-ere')
const activeTab   = ref('entities')
const displayMode = ref('count')
const hoveredCol  = ref(null)
const loading     = ref(false)
const building    = ref(false)
const notBuilt    = ref(false)
const error       = ref(null)
const data        = ref(null)
const snack       = ref({ show: false, message: '', color: 'success' })

// ── derived ───────────────────────────────────────────────────────────────────
const currentMatrix = computed(() => {
  if (!data.value) return null
  return activeTab.value === 'entities' ? data.value.entities : data.value.relations
})

// ── row-normalised percentage ─────────────────────────────────────────────────
function rowPct(val, ri) {
  if (!currentMatrix.value) return ''
  const total = currentMatrix.value.totals_annot1[currentMatrix.value.labels_annot1[ri]] || 0
  if (total === 0) return '0%'
  return (val / total * 100).toFixed(1) + '%'
}

// ── cell color ────────────────────────────────────────────────────────────────
const maxByRow = computed(() => {
  if (!currentMatrix.value) return []
  return currentMatrix.value.matrix.map(row => Math.max(...row, 1))
})

function cellStyle(val, ri, ci) {
  if (!currentMatrix.value || val === 0) return {}
  const rowLabel = currentMatrix.value.labels_annot1[ri]
  const colLabel = currentMatrix.value.labels_annot2[ci]
  const isDiag   = rowLabel === colLabel && rowLabel !== 'NIL'
  const opacity  = displayMode.value === 'row%'
    ? val / (currentMatrix.value.totals_annot1[rowLabel] || 1)
    : val / maxByRow.value[ri]
  const r = isDiag ? 22 : 99
  const g = isDiag ? 101 : 102
  const b = isDiag ? 52  : 241
  return {
    background: `rgba(${r},${g},${b},${(opacity * 0.75 + 0.05).toFixed(3)})`,
    color: opacity > 0.55 ? '#fff' : 'inherit',
  }
}

// ── fetch ─────────────────────────────────────────────────────────────────────
async function fetchMatrix() {
  loading.value  = true
  notBuilt.value = false
  error.value    = null
  data.value     = null
  try {
    const url = `/api/confusion-matrices?dataset=${dataset.value}&split=${split.value}&annot1=${annotRow.value}&annot2=${annotCol.value}&labelset=${labelset.value}`
    const res = await fetch(url)
    if (res.status === 404) { notBuilt.value = true; return }
    if (!res.ok) {
      const body = await res.json().catch(() => ({ error: res.statusText }))
      throw new Error(body.error ?? res.statusText)
    }
    data.value = await res.json()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

// ── build ─────────────────────────────────────────────────────────────────────
async function buildData() {
  building.value = true
  try {
    const res  = await fetch('/api/confusion-matrices/build', { method: 'POST' })
    const body = await res.json()
    if (body.ok) {
      snack.value = { show: true, message: 'Built successfully.', color: 'success' }
      notBuilt.value = false
      await fetchMatrix()
    } else {
      snack.value = { show: true, message: `Build failed: ${body.stderr?.slice(0, 200)}`, color: 'error' }
    }
  } catch (e) {
    snack.value = { show: true, message: `Error: ${e.message}`, color: 'error' }
  } finally {
    building.value = false
  }
}

watch([dataset, split, labelset, annotRow, annotCol], fetchMatrix, { immediate: true })
</script>

<style scoped>
.confusion-table {
  border-collapse: collapse;
  font-size: 12px;
  white-space: nowrap;
}
.confusion-table th,
.confusion-table td {
  border: 1px solid rgba(0,0,0,0.1);
  padding: 3px 8px;
  text-align: right;
}
.label-cell  { min-width: 20px; }
.row-header  { text-align: left; font-weight: 500; padding-right: 12px; position: sticky; left: 0; background: inherit; }
.col-header  { font-weight: 500; text-align: center; position: sticky; top: 0; background: var(--v-theme-surface, #fff); z-index: 1; }
.total-col   { font-weight: 500; color: rgba(0,0,0,0.45); }
.total-row td { font-weight: 500; color: rgba(0,0,0,0.45); }
.cell { min-width: 44px; cursor: default; }

/* Row highlight on tr hover */
.confusion-table tbody tr:hover .row-header,
.confusion-table tbody tr:hover .cell,
.confusion-table tbody tr:hover .total-col {
  background-image: linear-gradient(rgba(0,0,0,0.07), rgba(0,0,0,0.07));
}

/* Column highlight */
.col-hl {
  background-image: linear-gradient(rgba(0,0,0,0.07), rgba(0,0,0,0.07));
}

/* Cell at intersection: double tint */
.confusion-table tbody tr:hover .cell.col-hl {
  background-image: linear-gradient(rgba(0,0,0,0.14), rgba(0,0,0,0.14));
}
</style>
