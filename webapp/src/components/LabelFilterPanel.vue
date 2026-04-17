<template lang="pug">
v-card(variant="outlined" :style="`max-height:${maxHeight};overflow-y:auto;`")

  //- ── Entity Labels ──────────────────────────────────────────────────────────
  .px-3.pt-3.pb-1
    .d-flex.align-center
      span.text-subtitle-2.font-weight-bold Entity Labels
      v-spacer
      v-btn(size="x-small" variant="text" class="mr-1" @click="selectAllEntities") All
      v-btn(size="x-small" variant="text" color="error" @click="clearAllEntities") None

  template(v-for="(members, gname) in entityGroupsVisible" :key="'eg-'+gname")
    .px-3.py-1.d-flex.align-center(
      style="gap:4px;"
      :style="{ borderLeft: `3px solid ${entityGroupColor(gname)}` }"
    )
      span.text-caption.font-weight-bold(:style="{ color: entityGroupColor(gname) }") {{ gname }}
      v-checkbox-btn(
        :model-value="entityGroupState(gname) === 'all'"
        :indeterminate="entityGroupState(gname) === 'some'"
        color="grey-darken-2"
        density="compact" hide-details
        style="transform:scale(0.82);transform-origin:left center;flex-shrink:0;"
        @click.prevent="toggleEntityGroup(gname)"
      )
    .py-0.pl-3(v-for="lbl in members" :key="lbl")
      .d-flex.align-center.px-1(style="min-height:26px;gap:6px;")
        span.px-2.py-0.rounded.text-white(
          style="font-size:11px;font-weight:600;display:inline-block;line-height:18px;"
          :style="{ background: entityColor(lbl) }"
        ) {{ lbl }}
        v-checkbox-btn(
          :model-value="selectedEntityLabels.includes(lbl)"
          color="grey-darken-2"
          density="compact" hide-details
          style="transform:scale(0.82);transform-origin:left center;flex:0 0 auto;"
          @update:model-value="toggleEntityLabel(lbl, $event)"
        )
        span.text-caption.text-disabled.ml-auto(v-if="entityCountFn !== null")
          | {{ entityCountFn(lbl) != null ? entityCountFn(lbl).toLocaleString() : '' }}

  v-divider.my-1

  //- ── Relation Labels ────────────────────────────────────────────────────────
  .px-3.pt-1.pb-1
    .d-flex.align-center
      span.text-subtitle-2.font-weight-bold Relation Labels
      v-spacer
      v-btn(size="x-small" variant="text" class="mr-1" @click="selectAllRelations") All
      v-btn(size="x-small" variant="text" color="error" @click="clearAllRelations") None

  template(v-for="(members, gname) in relationGroupsVisible" :key="'rg-'+gname")
    .px-3.py-1.d-flex.align-center(
      style="gap:4px;"
      :style="{ borderLeft: `3px solid ${relationGroupColor(gname)}` }"
    )
      span.text-caption.font-weight-bold(:style="{ color: relationGroupColor(gname) }") {{ gname }}
      v-checkbox-btn(
        :model-value="relationGroupState(gname) === 'all'"
        :indeterminate="relationGroupState(gname) === 'some'"
        color="grey-darken-2"
        density="compact" hide-details
        style="transform:scale(0.82);transform-origin:left center;flex-shrink:0;"
        @click.prevent="toggleRelationGroup(gname)"
      )
    .py-0.pl-3(v-for="lbl in members" :key="lbl")
      .d-flex.align-center.px-1(style="min-height:26px;gap:6px;")
        span.px-2.py-0.rounded.text-white(
          style="font-size:11px;font-weight:600;display:inline-block;line-height:18px;"
          :style="{ background: relColorStable(lbl) }"
        ) {{ lbl }}
        v-checkbox-btn(
          :model-value="selectedRelationLabels.includes(lbl)"
          color="grey-darken-2"
          density="compact" hide-details
          style="transform:scale(0.82);transform-origin:left center;flex:0 0 auto;"
          @update:model-value="toggleRelationLabel(lbl, $event)"
        )
        span.text-caption.text-disabled.ml-auto(v-if="relCountFn !== null")
          | {{ relCountFn(lbl) != null ? relCountFn(lbl).toLocaleString() : '' }}
</template>

<script setup>
import { computed } from 'vue'
import { entityColor, relColorStable } from '../utils/entityColors.js'

const props = defineProps({
  availableEntityLabels:   { type: Array,    default: () => [] },
  availableRelationLabels: { type: Array,    default: () => [] },
  selectedEntityLabels:    { type: Array,    default: () => [] },
  selectedRelationLabels:  { type: Array,    default: () => [] },
  // { groupName: { color: string, members: string[] } }
  entityGroups:            { type: Object,   default: () => ({}) },
  relationGroups:          { type: Object,   default: () => ({}) },
  entityCountFn:           { type: Function, default: null },
  relCountFn:              { type: Function, default: null },
  maxHeight:               { type: String,   default: '580px' },
})

const emit = defineEmits(['update:selectedEntityLabels', 'update:selectedRelationLabels'])

// ── group color helpers ───────────────────────────────────────────────────────
function entityGroupColor(gname)   { return props.entityGroups[gname]?.color   ?? '#6b7280' }
function relationGroupColor(gname) { return props.relationGroups[gname]?.color ?? '#94a3b8' }

// ── visible groups (only those with at least one available member) ─────────────
const entityGroupsVisible = computed(() => {
  const avail = new Set(props.availableEntityLabels)
  const result = {}
  for (const [gname, gdata] of Object.entries(props.entityGroups)) {
    const members = (gdata.members ?? []).filter(m => avail.has(m))
    if (members.length) result[gname] = members
  }
  const grouped = new Set(Object.values(result).flat())
  const other   = props.availableEntityLabels.filter(l => !grouped.has(l))
  if (other.length) result['Other'] = other
  return result
})

const relationGroupsVisible = computed(() => {
  const avail = new Set(props.availableRelationLabels)
  const result = {}
  for (const [gname, gdata] of Object.entries(props.relationGroups)) {
    const members = (gdata.members ?? []).filter(m => avail.has(m))
    if (members.length) result[gname] = members
  }
  const grouped = new Set(Object.values(result).flat())
  const other   = props.availableRelationLabels.filter(l => !grouped.has(l))
  if (other.length) result['Other'] = other
  return result
})

// ── group checkbox states ─────────────────────────────────────────────────────
function entityGroupState(gname) {
  const members = entityGroupsVisible.value[gname] ?? []
  const n = members.filter(l => props.selectedEntityLabels.includes(l)).length
  return n === 0 ? 'none' : n === members.length ? 'all' : 'some'
}
function relationGroupState(gname) {
  const members = relationGroupsVisible.value[gname] ?? []
  const n = members.filter(l => props.selectedRelationLabels.includes(l)).length
  return n === 0 ? 'none' : n === members.length ? 'all' : 'some'
}

// ── toggle helpers ────────────────────────────────────────────────────────────
function toggleEntityLabel(lbl, checked) {
  const next = [...props.selectedEntityLabels]
  if (checked) { if (!next.includes(lbl)) next.push(lbl) }
  else         { const i = next.indexOf(lbl); if (i !== -1) next.splice(i, 1) }
  emit('update:selectedEntityLabels', next)
}
function toggleRelationLabel(lbl, checked) {
  const next = [...props.selectedRelationLabels]
  if (checked) { if (!next.includes(lbl)) next.push(lbl) }
  else         { const i = next.indexOf(lbl); if (i !== -1) next.splice(i, 1) }
  emit('update:selectedRelationLabels', next)
}

function toggleEntityGroup(gname) {
  const members = entityGroupsVisible.value[gname] ?? []
  const allOn   = entityGroupState(gname) === 'all'
  const next    = [...props.selectedEntityLabels]
  for (const lbl of members) {
    const i = next.indexOf(lbl)
    if (allOn && i !== -1)  next.splice(i, 1)
    if (!allOn && i === -1) next.push(lbl)
  }
  emit('update:selectedEntityLabels', next)
}
function toggleRelationGroup(gname) {
  const members = relationGroupsVisible.value[gname] ?? []
  const allOn   = relationGroupState(gname) === 'all'
  const next    = [...props.selectedRelationLabels]
  for (const lbl of members) {
    const i = next.indexOf(lbl)
    if (allOn && i !== -1)  next.splice(i, 1)
    if (!allOn && i === -1) next.push(lbl)
  }
  emit('update:selectedRelationLabels', next)
}

function selectAllEntities()  { emit('update:selectedEntityLabels',   [...props.availableEntityLabels])   }
function clearAllEntities()   { emit('update:selectedEntityLabels',   [])                                 }
function selectAllRelations() { emit('update:selectedRelationLabels', [...props.availableRelationLabels]) }
function clearAllRelations()  { emit('update:selectedRelationLabels', [])                                 }
</script>
