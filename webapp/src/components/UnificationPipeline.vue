<template lang="pug">
v-container(fluid class="pa-6")
  .d-flex.align-center.mb-2
    div
      h2.text-h5 {{ report?.title || 'Unification Pipeline' }}
      .text-caption.text-medium-emphasis(v-if="report") Generated: {{ report.generated }}
    v-spacer
    v-btn(v-if="!dockerMode" icon size="small" variant="text" :loading="loading" @click="regenerate")
      v-icon mdi-refresh

  v-alert(v-if="error" type="error" class="mb-4") {{ error }}

  template(v-if="report")
    v-alert(type="info" variant="tonal" class="mb-6" icon="mdi-information-outline") {{ report.info }}

    .text-subtitle-1.font-weight-medium.mb-3 Pipeline Steps
    v-timeline(density="compact" side="end")
      v-timeline-item(
        v-for="step in report.steps"
        :key="step.number"
        :dot-color="step.enabled ? 'primary' : 'grey'"
        size="small"
      )
        v-card(variant="flat" color="grey-lighten-4" :rounded="false" class="pa-3 mb-1")
          .d-flex.align-center.mb-1
            .text-subtitle-2.font-weight-bold {{ step.number }}. {{ step.name }}
            v-spacer
            v-chip(size="x-small" :color="step.enabled ? 'primary' : 'grey'" variant="tonal" class="ml-2") {{ step.scope }}
            v-chip(v-if="!step.enabled" size="x-small" color="grey" variant="outlined" class="ml-1") disabled
          .text-body-2 {{ step.description }}
          template(v-if="step.config && Object.keys(step.config).length > 0")
            .mt-2
              template(v-if="step.config.static_blacklist")
                .text-caption.text-medium-emphasis.mb-1 Static blacklist ({{ step.config.static_blacklist.length }} terms)
                .text-caption {{ step.config.static_blacklist.join(', ') }}
              template(v-else-if="step.config.prefer_larger !== undefined")
                .text-caption.text-medium-emphasis Prefer larger span: {{ step.config.prefer_larger }}
              template(v-else-if="step.config.min_count !== undefined")
                .text-caption.text-medium-emphasis Min count threshold: {{ step.config.min_count }}

</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useDockerMode } from '../composables/useDockerMode.js'

const PIPELINE_PATH  = 'reports/unification/pipeline.json'

const { dockerMode } = useDockerMode()
const report  = ref(null)
const loading = ref(false)
const error   = ref(null)

async function fetchReport() {
  const res = await fetch(`/api/json?path=${encodeURIComponent(PIPELINE_PATH)}&_t=${Date.now()}`)
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  report.value = await res.json()
}

async function load() {
  loading.value = true
  error.value = null
  try { await fetchReport() }
  catch (e) { error.value = e.message }
  finally { loading.value = false }
}

async function regenerate() {
  loading.value = true
  error.value = null
  try {
    const res = await fetch('/api/regenerate?report=unification', { method: 'POST' })
    const result = await res.json()
    if (!result.ok) throw new Error(result.stderr || 'Script failed')
    await fetchReport()
  } catch (e) { error.value = e.message }
  finally { loading.value = false }
}

onMounted(load)
</script>

