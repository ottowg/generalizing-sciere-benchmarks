<template lang="pug">
v-container(fluid)
  //- ── Header ──────────────────────────────────────────────────────────────
  .d-flex.align-center.mb-3
    h2.text-h5 Test Set Samples
    v-chip.ml-3(size="small" color="teal-darken-1" variant="tonal") {{ labelMode }} labels
    v-spacer
    v-btn(
      v-if="activeView === 'graph'"
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

  //- ── Shared controls: dataset · annotations · label set ──────────────────
  .d-flex.flex-wrap.ga-4.mb-3
    div
      .text-caption.text-medium-emphasis.mb-1 Test Dataset
      v-btn-toggle(v-model="activeDs" mandatory density="compact" variant="outlined" color="primary")
        v-btn(value="gsap-ere" size="small") GSAP-ERE
        v-btn(value="scier"   size="small") SciER
        v-btn(value="scinlp"  size="small") SciNLP
    div
      .text-caption.text-medium-emphasis.mb-1 Annotations
      v-btn-toggle(v-model="viewMode" mandatory density="compact" variant="outlined" color="secondary")
        v-btn(value="gold"     size="small" prepend-icon="mdi-check-circle-outline") Gold
        v-btn(value="gsap-ere" size="small") GSAP-ERE
        v-btn(value="scier"    size="small") SciER
        v-btn(value="scinlp"   size="small") SciNLP
    div
      .text-caption.text-medium-emphasis.mb-1 Label set
      v-btn-toggle(v-model="labelMode" mandatory density="compact" variant="outlined" color="teal")
        v-btn(value="unified"  size="small" prepend-icon="mdi-link-variant") Unified
        v-btn(value="original" size="small" prepend-icon="mdi-label-outline") Original

  //- ── View subnav ─────────────────────────────────────────────────────────
  v-tabs(v-model="activeView" density="compact" color="primary" class="mb-4")
    v-tab(value="graph" prepend-icon="mdi-graph-outline") Graph View
    v-tab(value="entity" prepend-icon="mdi-tag-multiple-outline") Entity View

  //- ── Not built yet ───────────────────────────────────────────────────────
  v-alert(
    v-if="notBuilt"
    type="info" variant="tonal" class="mb-4"
  )
    | No data yet. Click
    strong  Rebuild
    |  to build example papers from the test sets (runs the unification pipeline, takes ~60 s).

  //- ═══════════════════════════════════════════════════════════════════════
  //- GRAPH VIEW
  //- ═══════════════════════════════════════════════════════════════════════
  div(v-if="activeView === 'graph'")
    //- Paper select + min degree
    .d-flex.flex-wrap.ga-4.mb-3(style="align-items:flex-end;")
      div(style="min-width:300px;")
        .text-caption.text-medium-emphasis.mb-1 Paper
        v-select(
          v-model="selectedDocId"
          :items="docOptions"
          density="compact"
          variant="outlined"
          hide-details
        )
      div(style="min-width:200px;")
        .text-caption.text-medium-emphasis.mb-1 Min degree
        .d-flex.align-center(style="gap:8px;")
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

    //- Paper metadata
    .mb-2(v-if="currentPaper && currentPaper.metadata?.title")
      span.text-subtitle-2.font-weight-bold {{ currentPaper.metadata.title }}
      span.text-caption.text-disabled.ml-2(v-if="currentPaper.metadata.year") {{ currentPaper.metadata.year }}
      span.text-caption.ml-2(v-if="metaVenue") · {{ metaVenue }}
      .text-caption.text-disabled(v-if="currentPaper.metadata.authors?.length")
        | {{ currentPaper.metadata.authors.slice(0, 4).join(', ') }}{{ currentPaper.metadata.authors.length > 4 ? ' et al.' : '' }}

    //- Graph + Filter
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

    //- Sentences
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

  //- ═══════════════════════════════════════════════════════════════════════
  //- ENTITY VIEW
  //- ═══════════════════════════════════════════════════════════════════════
  div(v-if="activeView === 'entity'")
    //- Paper select + entity type filter
    .d-flex.flex-wrap.ga-4.mb-3(style="align-items:flex-end;")
      div(style="min-width:300px;")
        .text-caption.text-medium-emphasis.mb-1 Paper
        v-select(
          v-model="selectedDocId"
          :items="docOptions"
          density="compact"
          variant="outlined"
          hide-details
        )
      div(v-if="entityViewLabels.length")
        .text-caption.text-medium-emphasis.mb-1 Entity type
        v-btn-toggle(v-model="entityViewLabel" mandatory density="compact" variant="outlined" color="primary")
          v-btn(v-for="lbl in entityViewLabels" :key="lbl" :value="lbl" size="small") {{ lbl }}

    //- Paper metadata line
    .mb-3(v-if="currentPaper && currentPaper.metadata?.title")
      span.text-subtitle-2.font-weight-bold {{ currentPaper.metadata.title }}
      span.text-caption.text-disabled.ml-2(v-if="currentPaper.metadata.year") {{ currentPaper.metadata.year }}
      span.text-caption.ml-2(v-if="metaVenue") · {{ metaVenue }}
      .text-caption.text-disabled(v-if="currentPaper.metadata.authors?.length")
        | {{ currentPaper.metadata.authors.slice(0, 4).join(', ') }}{{ currentPaper.metadata.authors.length > 4 ? ' et al.' : '' }}

    p.text-body-2.text-medium-emphasis.mb-3(v-if="currentPaper && entityViewCards.length")
      | {{ entityViewCards.length }} {{ entityViewLabel }} entities in this paper · sorted by mention count

    //- Entity cards grid
    v-row(v-if="currentPaper && entityViewCards.length" dense)
      v-col(
        v-for="card in entityViewCards" :key="card.id"
        cols="12" sm="6" md="4"
      )
        v-card(
          variant="outlined" height="100%"
          :class="hoveredEntityCard === card.id ? 'ep-card-hovered' : ''"
          @mouseenter="hoveredEntityCard = card.id"
          @mouseleave="hoveredEntityCard = null"
        )
          v-card-text.pa-3
            //- Entity header
            .d-flex.align-center.mb-1(style="gap:6px;flex-wrap:wrap;")
              span.text-subtitle-2.font-weight-bold(style="word-break:break-word;") {{ card.text }}
              v-spacer
              v-chip(size="x-small" :color="entityColor(card.label)" variant="tonal") {{ card.label }}
              v-chip(size="x-small" variant="tonal" color="grey") ×{{ card.count }}
            //- Aliases
            .mb-2(v-if="card.aliases.length")
              span.text-caption.text-medium-emphasis(style="font-style:italic;")
                | also: {{ card.aliases.join(' · ') }}

            //- Relations grouped by type, oriented from this entity
            div(v-if="card.relGroups.length")
              div(v-for="grp in card.relGroups" :key="grp.relLabel" class="mb-2")
                //- Relation label badge
                .d-flex.align-center.mb-1(style="gap:4px;")
                  span.ep-rel-label(:style="{ background: relColorStable(grp.relLabel) }") {{ grp.relLabel }}
                //- Outgoing: entity → rel → target
                .ep-rel-item(v-for="e in grp.outgoing" :key="e.key" :class="e.sentence ? 'ep-rel-hoverable' : ''")
                  v-tooltip(v-if="e.sentence" activator="parent" location="bottom" max-width="420")
                    | {{ e.sentence }}
                  span.ep-dir-out →
                  span.ep-rel-target {{ e.text }}
                  v-chip.ml-1(size="x-small" :color="entityColor(e.label)" variant="tonal") {{ e.label }}
                //- Incoming (inverse): source → rel → entity, shown as ← from entity
                .ep-rel-item(v-for="e in grp.incoming" :key="e.key" :class="e.sentence ? 'ep-rel-hoverable' : ''")
                  v-tooltip(v-if="e.sentence" activator="parent" location="bottom" max-width="420")
                    | {{ e.sentence }}
                  span.ep-dir-in ←
                  span.ep-rel-target {{ e.text }}
                  v-chip.ml-1(size="x-small" :color="entityColor(e.label)" variant="tonal") {{ e.label }}

            .ep-no-rels(v-else)
              span.text-caption.text-disabled No relations in current view

            //- Hover: sample sentence
            div(v-if="hoveredEntityCard === card.id && card.sampleSentence")
              v-divider.my-2
              .ep-sentence "{{ card.sampleSentence }}"

    div(v-else-if="currentPaper && entityViewLabels.length" class="text-center text-disabled py-8")
      | No {{ entityViewLabel }} entities found.

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
const activeDs          = ref('gsap-ere')
const viewMode          = ref('gold')       // 'gold' | 'gsap-ere' | 'scier' | 'scinlp'
const labelMode         = ref('unified')    // 'unified' | 'original'
const selectedDocId     = ref(null)
const loading           = ref(false)
const building          = ref(false)
const notBuilt          = ref(false)
const graphRef          = ref(null)
const snack             = ref({ show: false, message: '', color: 'success' })
const semanticLayout    = ref(false)
const minDegree         = ref(1)
const activeView        = ref('graph')      // 'graph' | 'entity'
const entityViewLabel   = ref(null)
const hoveredEntityCard = ref(null)

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

// ── Entity View ───────────────────────────────────────────────────────────────

const entityViewLabels = computed(() => {
  const labels = new Set(currentData.value.entities.map(e => e.label))
  return [...labels].sort()
})

watch(entityViewLabels, (labels) => {
  if (!entityViewLabel.value || !labels.includes(entityViewLabel.value)) {
    entityViewLabel.value = labels[0] ?? null
  }
}, { immediate: true })

function parseEntityId(id) {
  const i = id.lastIndexOf('|')
  return { text: id.slice(0, i), label: id.slice(i + 1) }
}

const COREF_RELS = new Set(['Coreference', 'Synonym-Of', 'Similar-To'])

const entityViewCards = computed(() => {
  if (!entityViewLabel.value || !currentPaper.value) return []
  const lbl = entityViewLabel.value
  const { entities, relations } = currentData.value
  const sentences = currentPaper.value.sentences ?? []

  const filtered = entities.filter(e => e.label === lbl)
  if (!filtered.length) return []

  // Union-Find to group coreferent entities
  const parent = new Map(filtered.map(e => [e.id, e.id]))
  function find(id) {
    if (parent.get(id) !== id) parent.set(id, find(parent.get(id)))
    return parent.get(id)
  }
  const entityIds = new Set(filtered.map(e => e.id))
  for (const r of relations) {
    if (!COREF_RELS.has(r.label)) continue
    if (entityIds.has(r.subject_id) && entityIds.has(r.object_id)) {
      const pa = find(r.subject_id), pb = find(r.object_id)
      if (pa !== pb) parent.set(pa, pb)
    }
  }

  // Group by root
  const groups = new Map()
  for (const e of filtered) {
    const root = find(e.id)
    if (!groups.has(root)) groups.set(root, [])
    groups.get(root).push(e)
  }

  return [...groups.values()]
    .map(group => {
      group.sort((a, b) => b.count - a.count)
      const canonical = group[0]
      const totalCount = group.reduce((s, e) => s + e.count, 0)
      const aliases = group.length > 1 ? group.slice(1).map(e => e.text) : []
      const groupIds = new Set(group.map(e => e.id))

      // Collect all external relations, grouped by relation label
      const relMap = new Map()
      // Helper: find best sentence for a relation (both entities present; fallback to just related)
      const relSentence = (relatedText) => {
        const r1 = new RegExp(canonical.text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i')
        const r2 = new RegExp(relatedText.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i')
        const s = sentences.find(s => r1.test(s) && r2.test(s)) ?? sentences.find(s => r2.test(s)) ?? null
        return s && s.length > 220 ? s.slice(0, 219) + '…' : s
      }

      for (const r of relations) {
        if (COREF_RELS.has(r.label)) continue
        const isSubj = groupIds.has(r.subject_id) && !groupIds.has(r.object_id)
        const isObj  = groupIds.has(r.object_id)  && !groupIds.has(r.subject_id)
        if (!isSubj && !isObj) continue
        if (!relMap.has(r.label)) relMap.set(r.label, { outgoing: [], incoming: [] })
        const bucket = relMap.get(r.label)
        if (isSubj) {
          const { text, label } = parseEntityId(r.object_id)
          bucket.outgoing.push({ key: r.subject_id + r.label + r.object_id, text, label, sentence: relSentence(text) })
        } else {
          const { text, label } = parseEntityId(r.subject_id)
          bucket.incoming.push({ key: r.subject_id + r.label + r.object_id, text, label, sentence: relSentence(text) })
        }
      }
      const relGroups = [...relMap.entries()]
        .map(([relLabel, { outgoing, incoming }]) => ({ relLabel, outgoing, incoming }))
        .sort((a, b) => (b.outgoing.length + b.incoming.length) - (a.outgoing.length + a.incoming.length))

      const re = new RegExp(canonical.text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i')
      const found = sentences.find(s => re.test(s)) ?? null
      const sampleSentence = found && found.length > 180 ? found.slice(0, 179) + '…' : found

      return { id: canonical.id, text: canonical.text, label: canonical.label, count: totalCount, aliases, relGroups, sampleSentence }
    })
    .sort((a, b) => b.count - a.count)
})

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

<style scoped>
.ep-card-hovered {
  border-color: rgba(99, 110, 250, 0.5) !important;
  box-shadow: 0 0 0 1px rgba(99, 110, 250, 0.25);
}
.ep-sentence {
  font-size: 12px;
  line-height: 1.5;
  color: rgba(0, 0, 0, 0.65);
  font-style: italic;
}
.ep-rel-item {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 3px;
  font-size: 12px;
  margin-bottom: 3px;
  line-height: 1.4;
  padding-left: 6px;
}
.ep-dir-out {
  color: #636EFA;
  font-weight: 700;
  font-size: 12px;
  flex-shrink: 0;
}
.ep-dir-in {
  color: #EF553B;
  font-weight: 700;
  font-size: 12px;
  flex-shrink: 0;
}
.ep-rel-label {
  padding: 1px 6px;
  border-radius: 4px;
  color: white;
  font-size: 10px;
  font-weight: 500;
  white-space: nowrap;
}
.ep-rel-target {
  font-weight: 500;
  word-break: break-word;
}
.ep-rel-hoverable {
  cursor: help;
}
.ep-no-rels {
  margin-top: 4px;
}
</style>
