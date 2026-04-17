<template lang="pug">
v-container(fluid)
  //- ── Header ──────────────────────────────────────────────────────────────
  .d-flex.align-center.mb-3
    h2.text-h5 Example Paper
    v-chip.ml-3(size="small" color="teal-darken-1" variant="tonal") {{ labelMode }} labels
    v-spacer
    v-btn(
      size="small"
      :variant="semanticLayout ? 'flat' : 'outlined'"
      :color="semanticLayout ? 'primary' : 'default'"
      density="compact"
      prepend-icon="mdi-vector-triangle"
      class="mr-2"
      @click="toggleSemanticLayout"
    ) Cluster by Role
    v-btn(
      v-if="!dockerMode"
      size="small" variant="text" prepend-icon="mdi-refresh"
      :loading="building"
      @click="buildData"
    ) Rebuild

  //- ── Controls row 1: dataset · view mode · label mode ────────────────────
  v-row.mb-1(dense align="center")
    v-col(cols="auto")
      .text-caption.text-medium-emphasis.mb-1 Test Dataset
      v-btn-toggle(v-model="activeDs" mandatory density="compact" variant="outlined" color="primary")
        v-btn(value="gsap-ere" size="small") GSAP-ERE
        v-btn(value="scier"   size="small") SciER
        v-btn(value="scinlp"  size="small") SciNLP
    v-col(cols="auto")
      .text-caption.text-medium-emphasis.mb-1 Annotations
      v-btn-toggle(v-model="viewMode" mandatory density="compact" variant="outlined" color="secondary")
        v-btn(value="gold"     size="small" prepend-icon="mdi-check-circle-outline") Gold
        v-btn(value="gsap-ere" size="small") GSAP-ERE
        v-btn(value="scier"    size="small") SciER
        v-btn(value="scinlp"   size="small") SciNLP
    v-col(cols="auto")
      .text-caption.text-medium-emphasis.mb-1 Label set
      v-btn-toggle(v-model="labelMode" mandatory density="compact" variant="outlined" color="teal")
        v-btn(value="unified"  size="small" prepend-icon="mdi-link-variant") Unified
        v-btn(value="original" size="small" prepend-icon="mdi-label-outline") Original

  //- ── Controls row 2: paper select · degree ───────────────────────────────
  v-row.mb-2(dense align="center")
    v-col(cols="auto")
      v-select(
        v-model="selectedDocId"
        :items="docOptions"
        label="Paper"
        density="compact"
        variant="outlined"
        hide-details
        style="min-width:300px;"
      )
    v-col(cols="auto" style="min-width:200px;")
      .d-flex.align-center(style="gap:8px;")
        span.text-caption(style="white-space:nowrap;color:rgba(0,0,0,0.55);") Min degree
        v-slider(
          v-model="minDegree"
          :min="0" :max="3" step="1"
          density="compact"
          hide-details
          color="primary"
          style="flex:1;"
          thumb-label
        )
        span.text-caption(style="width:16px;text-align:right;color:rgba(0,0,0,0.55);") {{ minDegree }}

  //- ── Not built yet ───────────────────────────────────────────────────────
  v-alert(
    v-if="notBuilt"
    type="info" variant="tonal" class="mb-4"
  )
    | No data yet. Click
    strong  Rebuild
    |  to build example papers from the test sets (runs the unification pipeline, takes ~60 s).

  //- ── Paper metadata ──────────────────────────────────────────────────────
  .mb-2(v-if="currentPaper && currentPaper.metadata?.title")
    span.text-subtitle-2.font-weight-bold {{ currentPaper.metadata.title }}
    span.text-caption.text-disabled.ml-2(v-if="currentPaper.metadata.year") {{ currentPaper.metadata.year }}
    span.text-caption.ml-2(v-if="metaVenue") · {{ metaVenue }}
    .text-caption.text-disabled(v-if="currentPaper.metadata.authors?.length")
      | {{ currentPaper.metadata.authors.slice(0, 4).join(', ') }}{{ currentPaper.metadata.authors.length > 4 ? ' et al.' : '' }}

  //- ── Graph + Filter ──────────────────────────────────────────────────────
  v-row(v-if="currentPaper")
    v-col(cols="12" md="8")
      GraphViz(
        ref="graphRef"
        :nodes="graphNodes"
        :edges="graphEdges"
        height="560px"
        mark-id="expaper"
        :loading="loading"
      )
      //- Legend bar
      .d-flex.align-center.justify-space-between.px-3.py-2.mt-1(
        style="border:1px solid rgba(0,0,0,0.1);border-radius:8px;flex-wrap:wrap;gap:8px;"
      )
        .d-flex.flex-wrap.align-center(style="gap:10px;")
          .d-flex.align-center(v-for="t in legendEntityTypes" :key="t" style="gap:4px;")
            span.rounded(style="width:11px;height:11px;display:inline-block;flex-shrink:0;" :style="{ background: entityColor(t) }")
            span.text-caption {{ t }}
        .d-flex.flex-wrap.align-center(style="gap:4px;")
          span.px-2.py-0.rounded.text-white(
            v-for="r in legendRelTypes" :key="r"
            style="font-size:10px;line-height:17px;display:inline-block;"
            :style="{ background: relColorStable(r) }"
          ) {{ r }}
    v-col(cols="12" md="4")
      LabelFilterPanel(
        :available-entity-labels="availableEntityLabels"
        :available-relation-labels="availableRelationLabels"
        :selected-entity-labels="selectedEntityLabels"
        :selected-relation-labels="selectedRelationLabels"
        :entity-count-fn="entityCountFn"
        :rel-count-fn="relCountFn"
        max-height="560px"
        @update:selected-entity-labels="selectedEntityLabels = $event"
        @update:selected-relation-labels="selectedRelationLabels = $event"
      )

  //- ── Sentences ───────────────────────────────────────────────────────────
  v-expansion-panels.mt-3(v-if="currentPaper" variant="accordion")
    v-expansion-panel
      v-expansion-panel-title
        span.text-subtitle-2 Sentences ({{ currentPaper.sentences.length }})
      v-expansion-panel-text
        .py-1(
          v-for="(s, i) in currentPaper.sentences" :key="i"
          style="font-size:13px;line-height:1.6;border-bottom:1px solid rgba(0,0,0,0.06);padding:4px 0;"
        )
          span.text-disabled.mr-2(style="font-size:11px;") {{ i + 1 }}
          | {{ s }}

  v-snackbar(v-model="snack.show" :color="snack.color" timeout="6000")
    | {{ snack.message }}
    template(#actions)
      v-btn(variant="text" @click="snack.show = false") Close
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import GraphViz       from './GraphViz.vue'
import LabelFilterPanel from './LabelFilterPanel.vue'
import { entityColor, relColorStable, ENTITY_ANCHORS } from '../utils/entityColors.js'
import { useDockerMode } from '../composables/useDockerMode.js'

const { dockerMode } = useDockerMode()
const MAX_NODE_W = 150
const NODE_FS    = 11
const CHAR_W     = 6.0   // measured average for bold 11px SVG text
const H_PAD      = 10    // total horizontal padding (5px each side)
const MAX_CHARS  = Math.floor((MAX_NODE_W - H_PAD) / CHAR_W)   // ≈ 23 chars

// ── state ─────────────────────────────────────────────────────────────────────
const activeDs       = ref('gsap-ere')
const viewMode       = ref('gold')       // 'gold' | 'gsap-ere' | 'scier' | 'scinlp'
const labelMode      = ref('unified')    // 'unified' | 'original'
const selectedDocId  = ref(null)
const loading        = ref(false)
const building       = ref(false)
const notBuilt       = ref(false)
const graphRef       = ref(null)
const snack          = ref({ show: false, message: '', color: 'success' })
const semanticLayout = ref(false)
const minDegree      = ref(1)

const outlets = ref({})

// papers[dataset] = [{ doc_id, metadata, sentences, gold: {unified,original}, predictions: {trained_on: {unified,original}} }]
const papers = ref({ 'gsap-ere': [], scier: [], scinlp: [] })

// ── label selections ──────────────────────────────────────────────────────────
const selectedEntityLabels   = ref([])
const selectedRelationLabels = ref([])

// ── derived ───────────────────────────────────────────────────────────────────
const currentDatasetPapers = computed(() => papers.value[activeDs.value] ?? [])

const docOptions = computed(() =>
  currentDatasetPapers.value.map(p => {
    const t = p.metadata?.title
    const display = t
      ? (t.length > 50 ? t.slice(0, 49) + '…' : t)
      : p.doc_id
    return { title: display, value: p.doc_id }
  })
)

const currentPaper = computed(() =>
  currentDatasetPapers.value.find(p => p.doc_id === selectedDocId.value) ?? null
)

const currentData = computed(() => {
  if (!currentPaper.value) return { entities: [], relations: [] }
  const lm = labelMode.value
  if (viewMode.value === 'gold') {
    return currentPaper.value.gold?.[lm] ?? { entities: [], relations: [] }
  }
  return currentPaper.value.predictions?.[viewMode.value]?.[lm] ?? { entities: [], relations: [] }
})

// ── paper metadata helpers ─────────────────────────────────────────────────────
const metaVenue = computed(() => {
  const m = currentPaper.value?.metadata
  if (!m) return ''
  const outlet = outlets.value[m.outlet_id]
  if (outlet) return outlet.abbr || outlet.name || m.venue
  return m.venue || ''
})

// ── available labels ──────────────────────────────────────────────────────────
const availableEntityLabels = computed(() => {
  const s = new Set(currentData.value.entities.map(e => e.label))
  return [...s].sort()
})
const availableRelationLabels = computed(() => {
  const s = new Set(currentData.value.relations.map(r => r.label))
  return [...s].sort()
})

// ── count helpers ─────────────────────────────────────────────────────────────
const entityCountMap = computed(() => {
  const m = new Map()
  for (const e of currentData.value.entities) m.set(e.label, (m.get(e.label) ?? 0) + e.count)
  return m
})
const relCountMap = computed(() => {
  const m = new Map()
  for (const r of currentData.value.relations) m.set(r.label, (m.get(r.label) ?? 0) + r.count)
  return m
})
function entityCountFn(lbl) { return entityCountMap.value.get(lbl) ?? null }
function relCountFn(lbl)    { return relCountMap.value.get(lbl)    ?? null }

// ── abbreviation ──────────────────────────────────────────────────────────────
function abbrev(text) {
  return text.length > MAX_CHARS ? text.slice(0, MAX_CHARS - 1) + '…' : text
}

// ── graph nodes ───────────────────────────────────────────────────────────────
const graphNodes = computed(() => {
  const eSet = new Set(selectedEntityLabels.value)
  const rSet = new Set(selectedRelationLabels.value)

  const selectedEntityIds = new Set(
    currentData.value.entities.filter(e => eSet.has(e.label)).map(e => e.id)
  )

  const degreeMap = new Map()
  for (const r of currentData.value.relations) {
    if (!rSet.has(r.label)) continue
    if (!selectedEntityIds.has(r.subject_id) || !selectedEntityIds.has(r.object_id)) continue
    degreeMap.set(r.subject_id, (degreeMap.get(r.subject_id) ?? 0) + 1)
    degreeMap.set(r.object_id,  (degreeMap.get(r.object_id)  ?? 0) + 1)
  }

  const minDeg = minDegree.value
  return currentData.value.entities
    .filter(e => eSet.has(e.label) && (degreeMap.get(e.id) ?? 0) >= minDeg)
    .map(e => {
      const displayText = abbrev(e.text)
      const isAbbrev    = displayText !== e.text
      const w     = Math.min(MAX_NODE_W, Math.max(44, displayText.length * CHAR_W + H_PAD))
      const fullW = isAbbrev ? Math.min(280, Math.max(44, e.text.length * CHAR_W + H_PAD)) : null
      const h = Math.round(NODE_FS * 1.85)
      const node = {
        id: e.id, label: displayText,
        fullLabel: isAbbrev ? e.text : null, fullW,
        color: entityColor(e.label), w, h, fontSize: NODE_FS,
      }
      if (semanticLayout.value) {
        const anchor = ENTITY_ANCHORS[e.label]
        if (anchor) { node.anchorX = anchor.ax; node.anchorY = anchor.ay; node.anchorStrength = 0.011 }
      }
      return node
    })
})

// ── graph edges ───────────────────────────────────────────────────────────────
const graphEdges = computed(() => {
  const rSet    = new Set(selectedRelationLabels.value)
  const nodeIds = new Set(graphNodes.value.map(n => n.id))
  const maxLog  = Math.log(Math.max(...currentData.value.relations.map(r => r.count), 1) + 1)

  return currentData.value.relations
    .filter(r => rSet.has(r.label) && nodeIds.has(r.subject_id) && nodeIds.has(r.object_id))
    .map(r => ({
      id:          `${r.subject_id}|${r.label}|${r.object_id}`,
      source:      r.subject_id,
      target:      r.object_id,
      label:       r.label,
      color:       relColorStable(r.label),
      strokeWidth: 1.5 + 3.5 * (Math.log(r.count + 1) / (maxLog || 1)),
      count:       r.count,
    }))
})

// ── legend data ───────────────────────────────────────────────────────────────
const legendEntityTypes = computed(() => {
  const s = new Set(graphNodes.value.map(n => {
    const parts = n.id.split('|'); return parts[parts.length - 1]
  }))
  return [...s].sort()
})
const legendRelTypes = computed(() => [...new Set(graphEdges.value.map(e => e.label))].sort())

// ── semantic layout toggle ────────────────────────────────────────────────────
function toggleSemanticLayout() {
  semanticLayout.value = !semanticLayout.value
  graphRef.value?.clearPositions()
}

// ── Reset filter when paper changes (not on viewMode / labelMode switch) ──────
watch(selectedDocId, (newId) => {
  if (!newId) return
  nextTick(() => {
    for (const l of availableRelationLabels.value) relColorStable(l)
    selectedEntityLabels.value = [...availableEntityLabels.value]
    const rels = [...availableRelationLabels.value]
    selectedRelationLabels.value = rels.length > 1
      ? [rels[Math.floor(Math.random() * rels.length)]]
      : [...rels]
    graphRef.value?.clearPositions()
  })
}, { immediate: false })

// ── dataset switch ────────────────────────────────────────────────────────────
watch(activeDs, async () => { await fetchPapers(activeDs.value) })

// ── doc selection reset when papers list changes ──────────────────────────────
watch(currentDatasetPapers, (ps) => {
  selectedDocId.value = ps[0]?.doc_id ?? null
}, { immediate: true })

// ── data fetch ────────────────────────────────────────────────────────────────
async function fetchPapers(dataset) {
  loading.value  = true
  notBuilt.value = false
  try {
    const res = await fetch(`/api/example-paper?dataset=${dataset}`)
    if (res.status === 404) { notBuilt.value = true; return }
    if (!res.ok) throw new Error(await res.text())
    const data = await res.json()
    papers.value[dataset] = data.papers ?? []
  } catch (e) {
    snack.value = { show: true, message: `Failed to load: ${e.message}`, color: 'error' }
  } finally {
    loading.value = false
  }
}

async function fetchOutlets() {
  try {
    const res  = await fetch('/api/json?path=data/metadata/outlet_info.json')
    if (!res.ok) return
    const data = await res.json()
    const map  = {}
    for (const o of data) map[o.id] = o
    outlets.value = map
  } catch (_) {}
}

async function buildData() {
  building.value = true
  try {
    const res  = await fetch('/api/example-paper/build', { method: 'POST' })
    const data = await res.json()
    if (data.ok) {
      snack.value = { show: true, message: 'Built successfully.', color: 'success' }
      notBuilt.value = false
      for (const ds of ['gsap-ere', 'scier', 'scinlp']) await fetchPapers(ds)
    } else {
      snack.value = { show: true, message: `Build failed: ${data.stderr?.slice(0, 200)}`, color: 'error' }
    }
  } catch (e) {
    snack.value = { show: true, message: `Error: ${e.message}`, color: 'error' }
  } finally {
    building.value = false
  }
}

onMounted(() => {
  fetchOutlets()
  fetchPapers('gsap-ere')
  fetchPapers('scier')
  fetchPapers('scinlp')
})
</script>
