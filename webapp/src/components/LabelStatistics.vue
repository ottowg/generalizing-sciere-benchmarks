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
      v-tab(value="entities") Entities
      v-tab(value="relations") Relations
      v-tab(value="overtime") Over Time

    v-window(v-model="tab")

      //- ── ENTITIES ────────────────────────────────────────────────────────────
      v-window-item(value="entities")
        .text-caption.text-medium-emphasis.mb-5
          | Each violin: annotations per paper (only papers with ≥1 of that label).
          | Horizontal line = median &nbsp;·&nbsp; box = IQR &nbsp;·&nbsp; dot = mean.

        template(v-for="(dsData, ds) in stats.entities" :key="ds")
          v-sheet(class="mb-8 pa-4" rounded border)
            .d-flex.align-center.mb-3
              .text-subtitle-1.font-weight-bold {{ ds }}
              .text-caption.text-medium-emphasis.ml-3 {{ dsData.n_papers }} papers total

            .d-flex.flex-wrap.ga-4.mb-2
              .violin-card(v-for="label in dsData.labels" :key="label")
                .label-name.text-center.mb-1(
                  :title="label"
                  :style="{ color: entityColor(label) }"
                ) {{ label }}
                ViolinPlot(
                  :data="dsData.by_label[label].per_paper_present"
                  :color="entityColor(label)"
                  :width="84"
                  :height="130"
                )
                .text-caption.text-center.text-medium-emphasis ø {{ dsData.by_label[label].summary_present.mean }}
                .text-caption.text-center.text-disabled {{ dsData.by_label[label].pct_papers }}% of papers

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
          | Each violin: relations per paper (only papers with ≥1 relation of that type).
          | Horizontal line = median &nbsp;·&nbsp; box = IQR &nbsp;·&nbsp; dot = mean.

        template(v-for="(dsData, ds) in stats.relations" :key="ds")
          v-sheet(class="mb-8 pa-4" rounded border)
            .d-flex.align-center.mb-3
              .text-subtitle-1.font-weight-bold {{ ds }}
              .text-caption.text-medium-emphasis.ml-3 {{ dsData.n_papers }} papers total

            .d-flex.flex-wrap.ga-4.mb-2
              .violin-card(v-for="label in dsData.labels" :key="label")
                .label-name.text-center.mb-1(
                  :title="label"
                  :style="{ color: relColorStable(label) }"
                ) {{ label }}
                ViolinPlot(
                  :data="dsData.by_label[label].per_paper_present"
                  :color="relColorStable(label)"
                  :width="84"
                  :height="130"
                )
                .text-caption.text-center.text-medium-emphasis ø {{ dsData.by_label[label].summary_present.mean }}
                .text-caption.text-center.text-disabled {{ dsData.by_label[label].pct_papers }}% of papers

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

      //- ── OVER TIME ───────────────────────────────────────────────────────────
      v-window-item(value="overtime")
        .text-caption.text-medium-emphasis.mb-4
          | Mean entity count per paper per year (all splits pooled, gold annotations).
          | X-axis labels show the number of papers annotated in that year.

        v-row.mb-4(dense align="center")
          v-col(cols="6" sm="3" md="2")
            v-select(
              v-model="timeDs"
              :items="timeDatasets"
              label="Dataset"
              density="compact"
              variant="outlined"
              hide-details
            )
          v-col(cols="auto")
            v-checkbox(v-model="timeShowTotal" label="Show total" density="compact" hide-details)

        v-sheet(v-if="timeByYear" rounded border class="pa-4")
          EntityTimeChart(:byYear="timeByYear" :showTotal="timeShowTotal")
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import ViolinPlot from './ViolinPlot.vue'
import EntityTimeChart from './EntityTimeChart.vue'
import { entityColor, relColorStable } from '../utils/entityColors.js'
import { useDockerMode } from '../composables/useDockerMode.js'

const { dockerMode } = useDockerMode()
const stats   = ref(null)
const loading = ref(false)
const error   = ref(null)
const tab     = ref('entities')
const pipeline = ref(null)

const timeDs        = ref('gsap-ere')
const timeShowTotal = ref(true)
const timeDatasets  = ['gsap-ere', 'scier', 'scinlp']
const timeByYear    = computed(() => stats.value?.entities_by_year?.[timeDs.value] ?? null)

const entityMappings = computed(() => pipeline.value?.label_mappings   ?? {})
const relMappings    = computed(() => pipeline.value?.relation_mappings ?? {})

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
.violin-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 84px;
}
.label-name {
  font-size: 0.68rem;
  font-weight: 600;
  max-width: 84px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  cursor: default;
}
</style>
