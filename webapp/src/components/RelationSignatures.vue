<template lang="pug">
v-container(fluid)
  .d-flex.align-center.mb-1
    h2.text-h5 Relation Signatures
    v-spacer
    v-btn(
      v-if="!dockerMode"
      variant="text"
      prepend-icon="mdi-refresh"
      :loading="building"
      size="small"
      @click="rebuild"
    ) Rebuild

  v-tabs(v-model="activeTab" density="compact" color="primary" class="mb-3")
    v-tab(value="signatures") Signatures
    v-tab(value="forbidden") Schema Violations

  v-window(v-model="activeTab")

    //- ── SIGNATURES TAB ───────────────────────────────────────────────────────
    v-window-item(value="signatures")
      p.text-body-2.text-medium-emphasis.mb-2
        | A <strong>relation signature</strong> is a triple of subject entity type, relation type, and object entity type.
        | Each row in the table and each edge in the graph aggregates all annotations sharing that triple,
        | together with a count of how often it appears in the selected data slice.
      p.text-body-2.text-medium-emphasis.mb-4
        | Signatures can be <strong>allowed</strong> (present in the schema), carry a <strong>schema violation</strong>
        | (the combination is absent or the direction is reversed), or be <strong>unknown</strong> when no schema is
        | available for the selected label set. Schema violations are hidden by default to keep the graph
        | readable; uncheck the option below to reveal them. For a full quality breakdown per dataset and split,
        | see the Schema Violations tab.

      //- Filter bar
      v-row.mb-2(dense align="center")
        v-col(cols="auto")
          .text-caption.text-medium-emphasis.mb-1 Dataset
          v-btn-toggle(v-model="filterDataset" mandatory density="compact" variant="outlined" color="primary")
            v-btn(v-for="ds in meta.datasets" :key="ds" :value="ds" size="small") {{ ds }}
        v-col(cols="auto")
          .text-caption.text-medium-emphasis.mb-1 Annotations (Model Predictions)
          v-btn-toggle(v-model="filterModel" mandatory density="compact" variant="outlined" color="secondary")
            v-btn(v-for="m in meta.models" :key="m" :value="m" size="small") {{ m }}
        v-col(cols="auto")
          .text-caption.text-medium-emphasis.mb-1 Split
          v-btn-toggle(v-model="filterSplit" mandatory density="compact" variant="outlined" color="secondary")
            v-btn(value="(all)" size="small") All
            v-btn(v-for="s in meta.splits" :key="s" :value="s" size="small") {{ s }}
        v-col(cols="auto")
          .text-caption.text-medium-emphasis.mb-1 Label set
          v-btn-toggle(v-model="filterLabelSet" mandatory density="compact" variant="outlined" color="teal")
            v-btn(value="original" size="small" prepend-icon="mdi-label-outline") Original
            v-btn(value="unified"  size="small" prepend-icon="mdi-link-variant") Unified

      v-row.mb-1(dense align="center")
        v-col(cols="auto")
          v-checkbox(v-model="hideSelfRelations" label="Hide self-relations" density="compact" hide-details)
        v-col(cols="auto")
          v-checkbox(v-model="hideNotAllowed" label="Hide schema violations" density="compact" hide-details)

      v-row
        v-col(cols="12" md="8")
          GraphViz(
            ref="graphVizRef"
            :nodes="graphNodes"
            :edges="graphEdges"
            height="580px"
            mark-id="rgsig"
            :loading="loading"
          )
        v-col(cols="12" md="4")
          LabelFilterPanel(
            :available-entity-labels="availableEntityLabels"
            :available-relation-labels="availableRelationLabels"
            :selected-entity-labels="selectedEntityLabels"
            :selected-relation-labels="selectedRelationLabels"
            :entity-groups="groups.entity_groups ?? {}"
            :relation-groups="groups.relation_groups ?? {}"
            :entity-count-fn="entityCount"
            :rel-count-fn="relationCount"
            max-height="580px"
            @update:selected-entity-labels="selectedEntityLabels = $event"
            @update:selected-relation-labels="selectedRelationLabels = $event"
          )

      v-row.mt-2
        v-col(cols="12")
          v-card(variant="outlined")
            v-card-title.text-subtitle-2.d-flex.align-center.py-2.px-4
              | Signature Counts
              v-spacer
              span.text-caption.text-medium-emphasis(v-if="tableItems.length")
                | {{ tableItems.length.toLocaleString() }} signatures · {{ visibleTotal.toLocaleString() }} total
            v-data-table(
              :headers="tableHeaders"
              :items="tableItems"
              :items-per-page="25"
              density="compact"
              hover
              :sort-by="[{ key: 'count', order: 'desc' }]"
            )
              template(#item.status="{ item }")
                v-tooltip(:text="statusLabel(item.status)" location="right")
                  template(#activator="{ props }")
                    v-icon(v-bind="props" size="18" :color="statusColor(item.status)") {{ statusIcon(item.status) }}
              template(#item.subject_type="{ item }")
                span.px-2.py-0.rounded.text-white(
                  style="font-size:11px;font-weight:600;display:inline-block;line-height:18px;white-space:nowrap;"
                  :style="{ background: entityColor(item.subject_type) }"
                ) {{ item.subject_type }}
              template(#item.relation_type="{ item }")
                span.font-italic(style="font-size:11px;white-space:nowrap;" :style="{ color: relColorStable(item.relation_type) }") {{ item.relation_type }}
              template(#item.object_type="{ item }")
                span.px-2.py-0.rounded.text-white(
                  style="font-size:11px;font-weight:600;display:inline-block;line-height:18px;white-space:nowrap;"
                  :style="{ background: entityColor(item.object_type) }"
                ) {{ item.object_type }}
              template(#item.relation_group="{ item }")
                span.text-caption(:style="{ color: relationGroupColor(item.relation_group) }") {{ item.relation_group }}
              template(#item.count="{ item }")
                span.font-weight-medium {{ item.count.toLocaleString() }}
              template(
                v-for="ds in activeDatasets"
                :key="'slot-'+ds"
                #[`item.ds_${safeKey(ds)}`]="{ item }"
              )
                span(v-if="item.byDataset[ds]")
                  | {{ item.byDataset[ds].toLocaleString() }}
                  span.text-disabled  ({{ pct(item.byDataset[ds], datasetTotals[ds]) }})
                span.text-disabled(v-else) —

    //- ── SCHEMA VIOLATIONS TAB ───────────────────────────────────────────────
    v-window-item(value="forbidden")
      p.text-body-2.text-medium-emphasis.mb-2
        | A relation has a <strong>schema violation</strong> when its signature — the triple of subject
        | entity type, relation type, and object entity type — is absent from the schema specification
        | defined for that dataset. Violations come in two flavours: the direction of the relation is
        | reversed compared to the specification (<em>wrong direction</em>), or the combination simply
        | does not exist at all (<em>not allowed</em>).
      p.text-body-2.text-medium-emphasis.mb-4
        | The overview table reports what fraction of gold annotations in each dataset and split are
        | violations, evaluated against the unified schema. A high rate indicates systematic divergence
        | between the annotation guidelines and the schema — either noisy annotations or an incomplete
        | specification. The detailed list below lets you drill into the specific triples that are affected.

      //- ── Overview stats table ───────────────────────────────────────────────
      v-card.mb-6(variant="outlined")
        v-card-title.text-subtitle-2.py-2.px-4 Schema Violations in Gold Annotations (unified label set)
        v-data-table(
          :headers="violationStatsHeaders"
          :items="violationStatsRows"
          :sort-by="[]"
          :items-per-page="-1"
          density="compact"
          hover
        )
          template(#item.dataset="{ item }")
            v-chip(:color="dsColor(item.dataset)" size="small" variant="tonal") {{ item.dataset }}
          template(v-for="split in violationSplits" :key="'vslot-'+split" #[`item.${split}`]="{ item }")
            template(v-if="item[split]")
              span(:style="forbiddenPctStyle(item[split].pct)") {{ item[split].pct.toFixed(1) }}%
              span.text-disabled.ml-1 ({{ item[split].forbidden }}/{{ item[split].total }})
            span.text-disabled(v-else) —
          template(#bottom)

      //- ── Violation signature list ────────────────────────────────────────────
      .text-subtitle-2.font-weight-medium.mb-2 Violation Signatures

      v-row.mb-2(dense align="center")
        v-col(cols="auto")
          .text-caption.text-medium-emphasis.mb-1 Dataset
          v-btn-toggle(v-model="fFilterDataset" mandatory density="compact" variant="outlined" color="primary")
            v-btn(v-for="ds in meta.datasets" :key="ds" :value="ds" size="small") {{ ds }}
        v-col(cols="auto")
          .text-caption.text-medium-emphasis.mb-1 Annotations (Model Predictions)
          v-btn-toggle(v-model="fFilterModel" mandatory density="compact" variant="outlined" color="secondary")
            v-btn(v-for="m in meta.models" :key="m" :value="m" size="small") {{ m }}
        v-col(cols="auto")
          .text-caption.text-medium-emphasis.mb-1 Split
          v-btn-toggle(v-model="fFilterSplit" mandatory density="compact" variant="outlined" color="secondary")
            v-btn(value="(all)" size="small") All
            v-btn(v-for="s in meta.splits" :key="s" :value="s" size="small") {{ s }}
        v-col(cols="auto")
          .text-caption.text-medium-emphasis.mb-1 Label set
          v-btn-toggle(v-model="fFilterLabelSet" mandatory density="compact" variant="outlined" color="teal")
            v-btn(value="original" size="small" prepend-icon="mdi-label-outline") Original
            v-btn(value="unified"  size="small" prepend-icon="mdi-link-variant") Unified

      v-card(variant="outlined")
        v-card-title.text-subtitle-2.d-flex.align-center.py-2.px-4
          | Violating Signature Counts
          v-spacer
          span.text-caption.text-medium-emphasis(v-if="forbiddenTableItems.length")
            | {{ forbiddenTableItems.length.toLocaleString() }} signatures · {{ forbiddenTotal.toLocaleString() }} total
        v-data-table(
          :headers="forbiddenTableHeaders"
          :items="forbiddenTableItems"
          :items-per-page="25"
          density="compact"
          hover
          :sort-by="[{ key: 'count', order: 'desc' }]"
        )
          template(#item.status="{ item }")
            v-tooltip(:text="statusLabel(item.status)" location="right")
              template(#activator="{ props }")
                v-icon(v-bind="props" size="18" :color="statusColor(item.status)") {{ statusIcon(item.status) }}
          template(#item.subject_type="{ item }")
            span.px-2.py-0.rounded.text-white(
              style="font-size:11px;font-weight:600;display:inline-block;line-height:18px;white-space:nowrap;"
              :style="{ background: entityColor(item.subject_type) }"
            ) {{ item.subject_type }}
          template(#item.relation_type="{ item }")
            span.font-italic(style="font-size:11px;white-space:nowrap;" :style="{ color: relColorStable(item.relation_type) }") {{ item.relation_type }}
          template(#item.object_type="{ item }")
            span.px-2.py-0.rounded.text-white(
              style="font-size:11px;font-weight:600;display:inline-block;line-height:18px;white-space:nowrap;"
              :style="{ background: entityColor(item.object_type) }"
            ) {{ item.object_type }}
          template(#item.relation_group="{ item }")
            span.text-caption(:style="{ color: relationGroupColor(item.relation_group) }") {{ item.relation_group }}
          template(#item.count="{ item }")
            span.font-weight-medium {{ item.count.toLocaleString() }}
          template(
            v-for="ds in fActiveDatasets"
            :key="'fslot-'+ds"
            #[`item.ds_${safeKey(ds)}`]="{ item }"
          )
            span(v-if="item.byDataset[ds]")
              | {{ item.byDataset[ds].toLocaleString() }}
              span.text-disabled  ({{ pct(item.byDataset[ds], fDatasetTotals[ds]) }})
            span.text-disabled(v-else) —

  v-snackbar(v-model="snack.show" :color="snack.color" timeout="5000")
    | {{ snack.message }}
    template(#actions)
      v-btn(variant="text" @click="snack.show = false") Close
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import GraphViz        from './GraphViz.vue'
import LabelFilterPanel from './LabelFilterPanel.vue'
import { entityColor, relColorStable, ENTITY_ANCHORS } from '../utils/entityColors.js'
import { useDockerMode } from '../composables/useDockerMode.js'

const { dockerMode } = useDockerMode()
const graphVizRef = ref(null)
const activeTab   = ref('signatures')

// ── group / status helpers ────────────────────────────────────────────────────
const groups = ref({ entity_groups: {}, relation_groups: {} })

function relationGroupColor(gname) { return groups.value.relation_groups[gname]?.color ?? '#94a3b8' }

const DS_COLORS = { 'gsap-ere': 'blue', 'scier': 'green', 'scinlp': 'orange' }
function dsColor(ds) { return DS_COLORS[ds] ?? 'grey' }

function statusLabel(s) { return { allowed: 'Allowed', wrong_direction: 'Wrong direction', not_allowed: 'Not allowed', unknown: 'No data' }[s] ?? s }
function statusColor(s) { return { allowed: 'success', wrong_direction: 'warning', not_allowed: 'error', unknown: 'disabled' }[s] ?? 'grey' }
function statusIcon(s)  { return { allowed: 'mdi-check-circle', wrong_direction: 'mdi-swap-horizontal', not_allowed: 'mdi-close-circle', unknown: 'mdi-help-circle' }[s] ?? 'mdi-help-circle' }

// ── state ─────────────────────────────────────────────────────────────────────
const loading  = ref(true)
const building = ref(false)
const snack    = ref({ show: false, message: '', color: 'success' })

const allRows     = ref([])
const meta        = ref({ datasets: [], models: [], splits: [], label_sets: ['original', 'unified'] })
const allowedSigs = ref({})

// Signatures tab filters
const filterDataset  = ref('scinlp')
const filterModel    = ref('gold')
const filterSplit    = ref('(all)')
const filterLabelSet = ref('original')

const hideSelfRelations = ref(true)
const hideNotAllowed    = ref(true)

// Forbidden tab filters
const fFilterDataset  = ref('scinlp')
const fFilterModel    = ref('gold')
const fFilterSplit    = ref('(all)')
const fFilterLabelSet = ref('original')

// ── label selections ──────────────────────────────────────────────────────────
const availableEntityLabels   = ref([])
const availableRelationLabels = ref([])
const selectedEntityLabels    = ref([])
const selectedRelationLabels  = ref([])

// Labels hidden by default for GSAP-ERE in the original label set
const GSAP_DEFAULT_HIDDEN = new Set([
  'DataSource', 'DatasetGeneric', 'MLModelGeneric', 'ModelArchitecture', 'ReferenceLink', 'URL',
])

function withoutReferencing(rLabels) {
  const refs = new Set(groups.value.relation_groups['Referencing']?.members ?? [])
  return rLabels.filter(l => !refs.has(l))
}

function defaultSelectedLabels(eLabels, rLabels) {
  const isGsap = filterDataset.value === 'gsap-ere' && filterLabelSet.value === 'original'
  const filteredE = isGsap ? eLabels.filter(l => !GSAP_DEFAULT_HIDDEN.has(l)) : [...eLabels]
  const filteredR = withoutReferencing(rLabels)
  return { eLabels: filteredE, rLabels: filteredR }
}

// ── allowed signature sets ────────────────────────────────────────────────────
function buildAllowedSet(labelSet, model) {
  const as = allowedSigs.value
  if (!as || Object.keys(as).length === 0) return null
  const section = key => as[key]?.allowed ?? []
  const toSet = (triples) => new Set(triples.map(([s, r, o]) => `${s}|${r}|${o}`))
  if (labelSet === 'unified') return toSet(section('unified'))
  if (labelSet === 'original') {
    if (model !== '(all)' && model !== 'gold' && as[model]) return toSet(section(model))
    return toSet([...section('gsap-ere'), ...section('scier'), ...section('scinlp')])
  }
  return toSet(Object.values(as).flatMap(v => v?.allowed ?? []))
}

function buildWrongDirSet(labelSet, model) {
  const as = allowedSigs.value
  if (!as || Object.keys(as).length === 0) return null
  const section = key => as[key]?.wrong_direction ?? []
  const toSet = (triples) => new Set(triples.map(([s, r, o]) => `${s}|${r}|${o}`))
  if (labelSet === 'unified') return toSet(section('unified'))
  if (labelSet === 'original') {
    if (model !== '(all)' && model !== 'gold' && as[model]) return toSet(section(model))
    return toSet([...section('gsap-ere'), ...section('scier'), ...section('scinlp')])
  }
  return toSet(Object.values(as).flatMap(v => v?.wrong_direction ?? []))
}

const allowedSet  = computed(() => buildAllowedSet(filterLabelSet.value, filterModel.value))
const wrongDirSet = computed(() => buildWrongDirSet(filterLabelSet.value, filterModel.value))

function signatureStatus(row, aSet, wSet) {
  const key = `${row.subject_type}|${row.relation_type}|${row.object_type}`
  if (!aSet) return 'unknown'
  if (aSet.has(key))  return 'allowed'
  if (wSet?.has(key)) return 'wrong_direction'
  return 'not_allowed'
}

function isForbidden(row, aSet, wSet) {
  const s = signatureStatus(row, aSet, wSet)
  return s === 'not_allowed' || s === 'wrong_direction'
}

// ── data flow — Signatures tab ────────────────────────────────────────────────
const filteredRows = computed(() => allRows.value.filter(r => {
  // map stored 'raw' to display 'original' for filtering
  const ls = r.label_set === 'raw' ? 'original' : r.label_set
  if (r.dataset   !== filterDataset.value)                                   return false
  if (filterModel.value  !== '(all)' && r.model !== filterModel.value)      return false
  if (filterSplit.value  !== '(all)' && r.split !== filterSplit.value)      return false
  if (filterLabelSet.value !== '(all)' && ls !== filterLabelSet.value)      return false
  return true
}))

const aggregated = computed(() => {
  const map = new Map()
  for (const r of filteredRows.value) {
    const key = `${r.subject_type}|${r.relation_type}|${r.object_type}`
    if (!map.has(key)) map.set(key, {
      subject_type: r.subject_type, relation_type: r.relation_type, object_type: r.object_type,
      relation_group: r.relation_group ?? 'Other', count: 0,
    })
    map.get(key).count += r.count
  }
  return [...map.values()].sort((a, b) => b.count - a.count)
})

const entityCountMap = computed(() => {
  const m = new Map()
  for (const r of aggregated.value) {
    m.set(r.subject_type, (m.get(r.subject_type) ?? 0) + r.count)
    m.set(r.object_type,  (m.get(r.object_type)  ?? 0) + r.count)
  }
  return m
})
const relationCountMap = computed(() => {
  const m = new Map()
  for (const r of aggregated.value) m.set(r.relation_type, (m.get(r.relation_type) ?? 0) + r.count)
  return m
})
function entityCount(lbl)   { return entityCountMap.value.get(lbl)   ?? 0 }
function relationCount(lbl) { return relationCountMap.value.get(lbl) ?? 0 }

watch(aggregated, (rows) => {
  const eLabels = [...new Set(rows.flatMap(r => [r.subject_type, r.object_type]))].sort()
  const rLabels = [...new Set(rows.map(r => r.relation_type))].sort()
  availableEntityLabels.value   = eLabels
  availableRelationLabels.value = rLabels
  for (const l of rLabels) relColorStable(l)
  const def = defaultSelectedLabels(eLabels, rLabels)
  selectedEntityLabels.value   = def.eLabels
  selectedRelationLabels.value = def.rLabels
  graphVizRef.value?.clearPositions()
}, { immediate: false })

const visibleAggregated = computed(() => {
  const eSet = new Set(selectedEntityLabels.value)
  const rSet = new Set(selectedRelationLabels.value)
  return aggregated.value.filter(r =>
    eSet.has(r.subject_type) && eSet.has(r.object_type) && rSet.has(r.relation_type) &&
    (!hideSelfRelations.value || r.subject_type !== r.object_type) &&
    (!hideNotAllowed.value  || !isForbidden(r, allowedSet.value, wrongDirSet.value)) &&
    (!hideAllowed.value     ||  isForbidden(r, allowedSet.value, wrongDirSet.value))
  )
})

const activeDatasets = computed(() => {
  const ds = new Set(filteredRows.value.map(r => r.dataset))
  return meta.value.datasets.filter(d => ds.has(d))
})

const safeKey = ds => ds.replace(/-/g, '_')
function pct(n, total) { return total ? (n / total * 100).toFixed(1) + '%' : '–' }

const visibleFilteredRows = computed(() => {
  const eSet = new Set(selectedEntityLabels.value)
  const rSet = new Set(selectedRelationLabels.value)
  return filteredRows.value.filter(r =>
    eSet.has(r.subject_type) && eSet.has(r.object_type) && rSet.has(r.relation_type) &&
    (!hideSelfRelations.value || r.subject_type !== r.object_type) &&
    (!hideNotAllowed.value  || !isForbidden(r, allowedSet.value, wrongDirSet.value)) &&
    (!hideAllowed.value     ||  isForbidden(r, allowedSet.value, wrongDirSet.value))
  )
})

const datasetTotals = computed(() => {
  const m = {}
  for (const r of visibleFilteredRows.value)
    m[r.dataset] = (m[r.dataset] ?? 0) + r.count
  return m
})

const tableItems = computed(() => {
  const map = new Map()
  for (const r of visibleFilteredRows.value) {
    const key = `${r.subject_type}|${r.relation_type}|${r.object_type}`
    if (!map.has(key)) map.set(key, {
      subject_type: r.subject_type, relation_type: r.relation_type, object_type: r.object_type,
      relation_group: r.relation_group ?? 'Other', count: 0, byDataset: {},
    })
    const entry = map.get(key)
    entry.count += r.count
    entry.byDataset[r.dataset] = (entry.byDataset[r.dataset] ?? 0) + r.count
  }
  return [...map.values()]
    .sort((a, b) => b.count - a.count)
    .map(item => ({ ...item, status: signatureStatus(item, allowedSet.value, wrongDirSet.value) }))
})

const visibleTotal = computed(() => tableItems.value.reduce((s, r) => s + r.count, 0))

const tableHeaders = computed(() => {
  const base = [
    { title: '',         key: 'status',         sortable: true, width: '44px' },
    { title: 'Subject',  key: 'subject_type',   sortable: true },
    { title: 'Relation', key: 'relation_type',  sortable: true },
    { title: 'Object',   key: 'object_type',    sortable: true },
    { title: 'Group',    key: 'relation_group', sortable: true },
    { title: 'Total',    key: 'count',          sortable: true, align: 'end' },
  ]
  for (const ds of activeDatasets.value)
    base.push({ title: ds, key: `ds_${safeKey(ds)}`, sortable: true, align: 'end' })
  return base
})

// ── graph data ────────────────────────────────────────────────────────────────
const graphNodes = computed(() => {
  const typeSet = new Set()
  for (const r of visibleAggregated.value) { typeSet.add(r.subject_type); typeSet.add(r.object_type) }
  return [...typeSet].map(t => {
    const fs = 13, w = Math.max(70, t.length * fs * 0.62 + 20), h = fs * 1.8
    const node = { id: t, color: entityColor(t), w, h, fontSize: fs }
    const anchor = ENTITY_ANCHORS[t]
    if (anchor) { node.anchorX = anchor.ax; node.anchorY = anchor.ay; node.anchorStrength = 0.011 }
    return node
  })
})

const graphEdges = computed(() => {
  const rows = visibleAggregated.value
  if (!rows.length) return []
  const maxLog = Math.log(rows[0].count + 1)
  return rows.map(r => ({
    id: `${r.subject_type}|${r.relation_type}|${r.object_type}`,
    source: r.subject_type, target: r.object_type,
    label: r.relation_type, color: relColorStable(r.relation_type),
    strokeWidth: 1.5 + 4.5 * (Math.log(r.count + 1) / (maxLog || 1)),
    count: r.count,
  }))
})

// ── Schema Violations tab — stats ────────────────────────────────────────────
// Pivoted: one row per dataset, one column per split
const violationSplits = computed(() => {
  const seen = new Set()
  for (const r of allRows.value) {
    const ls = r.label_set === 'raw' ? 'original' : r.label_set
    if (r.model === 'gold' && ls === 'unified') seen.add(r.split)
  }
  return ['train', 'dev', 'test'].filter(s => seen.has(s))
})

const violationStatsRows = computed(() => {
  const aSet = buildAllowedSet('unified', 'gold')
  const wSet = buildWrongDirSet('unified', 'gold')
  // cell map: dataset → split → { total, forbidden }
  const cellMap = new Map()
  for (const r of allRows.value) {
    const ls = r.label_set === 'raw' ? 'original' : r.label_set
    if (r.model !== 'gold' || ls !== 'unified') continue
    if (!cellMap.has(r.dataset)) cellMap.set(r.dataset, {})
    const cell = cellMap.get(r.dataset)
    if (!cell[r.split]) cell[r.split] = { total: 0, forbidden: 0 }
    cell[r.split].total += r.count
    if (isForbidden(r, aSet, wSet)) cell[r.split].forbidden += r.count
  }
  return [...cellMap.entries()].map(([dataset, cells]) => {
    const row = { dataset }
    for (const [split, c] of Object.entries(cells))
      row[split] = { ...c, pct: c.total ? c.forbidden / c.total * 100 : 0 }
    return row
  })
})

const violationStatsHeaders = computed(() => [
  { title: 'Dataset', key: 'dataset', sortable: false },
  ...violationSplits.value.map(s => ({ title: s, key: s, sortable: false, align: 'end' })),
])

function forbiddenPctStyle(pct) {
  if (pct === 0) return 'color:#2e7d32;font-weight:600'
  if (pct < 5)  return 'color:#f57c00;font-weight:600'
  return 'color:#c62828;font-weight:600'
}

// ── Forbidden tab — signature list ────────────────────────────────────────────
const fAllowedSet  = computed(() => buildAllowedSet(fFilterLabelSet.value, fFilterModel.value))
const fWrongDirSet = computed(() => buildWrongDirSet(fFilterLabelSet.value, fFilterModel.value))

const fFilteredRows = computed(() => allRows.value.filter(r => {
  const ls = r.label_set === 'raw' ? 'original' : r.label_set
  if (r.dataset !== fFilterDataset.value)                                   return false
  if (fFilterModel.value !== '(all)' && r.model !== fFilterModel.value)    return false
  if (fFilterSplit.value !== '(all)' && r.split !== fFilterSplit.value)    return false
  if (fFilterLabelSet.value !== '(all)' && ls !== fFilterLabelSet.value)   return false
  return isForbidden(r, fAllowedSet.value, fWrongDirSet.value)
}))

const fActiveDatasets = computed(() => {
  const ds = new Set(fFilteredRows.value.map(r => r.dataset))
  return meta.value.datasets.filter(d => ds.has(d))
})

const fDatasetTotals = computed(() => {
  const m = {}
  for (const r of fFilteredRows.value)
    m[r.dataset] = (m[r.dataset] ?? 0) + r.count
  return m
})

const forbiddenTableItems = computed(() => {
  const map = new Map()
  for (const r of fFilteredRows.value) {
    const key = `${r.subject_type}|${r.relation_type}|${r.object_type}`
    if (!map.has(key)) map.set(key, {
      subject_type: r.subject_type, relation_type: r.relation_type, object_type: r.object_type,
      relation_group: r.relation_group ?? 'Other', count: 0, byDataset: {},
    })
    const entry = map.get(key)
    entry.count += r.count
    entry.byDataset[r.dataset] = (entry.byDataset[r.dataset] ?? 0) + r.count
  }
  return [...map.values()]
    .sort((a, b) => b.count - a.count)
    .map(item => ({ ...item, status: signatureStatus(item, fAllowedSet.value, fWrongDirSet.value) }))
})

const forbiddenTotal = computed(() => forbiddenTableItems.value.reduce((s, r) => s + r.count, 0))

const forbiddenTableHeaders = computed(() => {
  const base = [
    { title: '',         key: 'status',         sortable: true, width: '44px' },
    { title: 'Subject',  key: 'subject_type',   sortable: true },
    { title: 'Relation', key: 'relation_type',  sortable: true },
    { title: 'Object',   key: 'object_type',    sortable: true },
    { title: 'Group',    key: 'relation_group', sortable: true },
    { title: 'Total',    key: 'count',          sortable: true, align: 'end' },
  ]
  for (const ds of fActiveDatasets.value)
    base.push({ title: ds, key: `ds_${safeKey(ds)}`, sortable: true, align: 'end' })
  return base
})

// ── data fetch ────────────────────────────────────────────────────────────────
async function fetchData() {
  loading.value = true
  try {
    const res  = await fetch('/api/signatures')
    if (!res.ok) throw new Error(await res.text())
    const data = await res.json()
    allRows.value     = data.rows
    groups.value      = data.groups  ?? { entity_groups: {}, relation_groups: {} }
    allowedSigs.value = data.allowed ?? {}
    // Normalise meta: map 'raw' → 'original' in label_sets
    const rawMeta = data.meta
    meta.value = {
      ...rawMeta,
      label_sets: rawMeta.label_sets.map(l => l === 'raw' ? 'original' : l),
    }
    if (!data.meta.models.includes(filterModel.value))
      filterModel.value = data.meta.models[0] ?? '(all)'
    // Default dataset to scier if available
    if (data.meta.datasets.includes('scier')) {
      filterDataset.value  = 'scier'
      fFilterDataset.value = 'scier'
    } else if (data.meta.datasets.length) {
      filterDataset.value  = data.meta.datasets[0]
      fFilterDataset.value = data.meta.datasets[0]
    }
  } catch (e) {
    snack.value = { show: true, message: `Failed to load: ${e.message}`, color: 'error' }
  } finally {
    loading.value = false
  }
}

async function rebuild() {
  building.value = true
  try {
    const res  = await fetch('/api/signatures/build', { method: 'POST' })
    const data = await res.json()
    if (data.ok) { snack.value = { show: true, message: 'Rebuilt.', color: 'success' }; await fetchData() }
    else snack.value = { show: true, message: `Failed: ${data.stderr}`, color: 'error' }
  } catch (e) {
    snack.value = { show: true, message: `Error: ${e.message}`, color: 'error' }
  } finally {
    building.value = false
  }
}

onMounted(async () => {
  await fetchData()
  const eLabels = [...new Set(aggregated.value.flatMap(r => [r.subject_type, r.object_type]))].sort()
  const rLabels = [...new Set(aggregated.value.map(r => r.relation_type))].sort()
  availableEntityLabels.value   = eLabels
  availableRelationLabels.value = rLabels
  for (const l of rLabels) relColorStable(l)
  const def = defaultSelectedLabels(eLabels, rLabels)
  selectedEntityLabels.value   = def.eLabels
  selectedRelationLabels.value = def.rLabels
})
</script>
