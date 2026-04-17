<template lang="pug">
v-app-bar(color="deep-purple-darken-2" elevation="2")
  v-app-bar-title UnifiedSciERE
  v-spacer

  v-menu
    template(#activator="{ props }")
      v-btn(v-bind="props" :variant="isMetadataView ? 'tonal' : 'text'" prepend-icon="mdi-database-outline" append-icon="mdi-chevron-down") Metadata
    v-list(density="compact")
      v-list-item(
        prepend-icon="mdi-map-marker-path"
        title="Publication Map"
        :active="currentView === 'metadata-pub-map'"
        active-color="primary"
        @click="emit('set-view', 'metadata-pub-map')"
      )
      v-list-item(
        prepend-icon="mdi-chart-bar"
        title="Publication Statistics"
        :active="currentView === 'metadata-stats'"
        active-color="primary"
        @click="emit('set-view', 'metadata-stats')"
      )
      v-list-item(
        prepend-icon="mdi-format-list-bulleted"
        title="Overview"
        :active="currentView === 'metadata-overview'"
        active-color="primary"
        @click="emit('set-view', 'metadata-overview')"
      )
      v-list-item(
        prepend-icon="mdi-graph-outline"
        title="Outlet Map"
        :active="currentView === 'metadata-outlet-map'"
        active-color="primary"
        @click="emit('set-view', 'metadata-outlet-map')"
      )
      v-divider
      v-list-item(
        prepend-icon="mdi-download-outline"
        title="Download"
        :active="currentView === 'metadata-download'"
        active-color="primary"
        @click="emit('set-view', 'metadata-download')"
      )

  v-menu
    template(#activator="{ props }")
      v-btn(v-bind="props" :variant="isDataModelsView ? 'tonal' : 'text'" append-icon="mdi-chevron-down") Data Models
    v-list(density="compact")
      v-list-item(
        prepend-icon="mdi-graph-outline"
        title="Relation Signatures"
        :active="currentView === 'quality-signatures'"
        active-color="primary"
        @click="emit('set-view', 'quality-signatures')"
      )
      v-list-item(
        prepend-icon="mdi-book-open-variant-outline"
        title="Schema Preview"
        :active="currentView === 'data-models-schema'"
        active-color="primary"
        @click="emit('set-view', 'data-models-schema')"
      )

  v-menu
    template(#activator="{ props }")
      v-btn(v-bind="props" :variant="isUnificationView ? 'tonal' : 'text'" append-icon="mdi-chevron-down") Unification
    v-list(density="compact")
      v-list-item(
        prepend-icon="mdi-pipe"
        title="Pipeline"
        :active="currentView === 'unification-pipeline'"
        active-color="primary"
        @click="emit('set-view', 'unification-pipeline')"
      )
      v-list-item(
        prepend-icon="mdi-chart-bar"
        title="Retention Stats"
        :active="currentView === 'unification-retention'"
        active-color="primary"
        @click="emit('set-view', 'unification-retention')"
      )
      v-list-item(
        prepend-icon="mdi-chart-violin"
        title="Label Statistics"
        :active="currentView === 'unification-label-stats'"
        active-color="primary"
        @click="emit('set-view', 'unification-label-stats')"
      )
      v-list-item(
        prepend-icon="mdi-table-arrow-right"
        title="Label Mapping"
        :active="currentView === 'unification-label-mapping'"
        active-color="primary"
        @click="emit('set-view', 'unification-label-mapping')"
      )

  v-menu
    template(#activator="{ props }")
      v-btn(v-bind="props" :variant="isResultsView ? 'tonal' : 'text'" append-icon="mdi-chevron-down") Results
    v-list(density="compact")
      v-list-item(
        prepend-icon="mdi-replay"
        title="Reproduce Results"
        :active="currentView === 'performance-reproduce'"
        active-color="primary"
        @click="emit('set-view', 'performance-reproduce')"
      )
      v-list-item(
        prepend-icon="mdi-table-arrow-right"
        title="Cross-Dataset"
        :active="currentView === 'performance-cross-dataset'"
        active-color="primary"
        @click="emit('set-view', 'performance-cross-dataset')"
      )

  v-btn(
    :variant="currentView === 'quality-example-paper' ? 'tonal' : 'text'"
    prepend-icon="mdi-file-document-outline"
    @click="emit('set-view', 'quality-example-paper')"
  ) Examples

  v-menu(v-if="!dockerMode")
    template(#activator="{ props }")
      v-btn(v-bind="props" :variant="isMoreView ? 'tonal' : 'text'" append-icon="mdi-chevron-down") More
    v-list(density="compact")
      v-list-subheader Annotation Review
      v-list-item(
        prepend-icon="mdi-relation-many-to-many"
        title="Relation Review"
        :active="currentView === 'quality-relations'"
        active-color="primary"
        @click="emit('set-view', 'quality-relations')"
      )
      v-list-item(
        prepend-icon="mdi-tag-outline"
        title="Entity Review"
        :active="currentView === 'quality-mentions'"
        active-color="primary"
        @click="emit('set-view', 'quality-mentions')"
      )
      v-divider
      v-list-item(
        prepend-icon="mdi-text-short"
        title="Abbreviation Relations"
        :active="currentView === 'quality-abbreviation'"
        active-color="primary"
        @click="emit('set-view', 'quality-abbreviation')"
      )

  v-divider(v-if="!dockerMode" vertical class="mx-2")

  v-dialog(v-if="!dockerMode" v-model="annotatorDialog" max-width="320")
    template(#activator="{ props: dialogProps }")
      v-chip(
        v-bind="dialogProps"
        :color="annotator ? 'secondary' : 'warning'"
        :prepend-icon="annotator ? 'mdi-account-circle' : 'mdi-account-question'"
        class="mx-2"
        label
      ) {{ annotator || 'Set annotator' }}
    v-card
      v-card-title.pt-4 Annotator
      v-card-text
        v-text-field(
          v-model="annotatorInput"
          label="Your name"
          variant="outlined"
          density="compact"
          autofocus
          @keyup.enter="saveAnnotator"
        )
      v-card-actions
        v-spacer
        v-btn(variant="text" @click="annotatorDialog = false") Cancel
        v-btn(color="primary" variant="tonal" :disabled="!annotatorInput.trim()" @click="saveAnnotator") Save

  v-btn(:icon="isDark ? 'mdi-white-balance-sunny' : 'mdi-moon-waxing-crescent'" @click="emit('toggle-theme')")
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAnnotator } from '../composables/useAnnotator.js'
import { useDockerMode } from '../composables/useDockerMode.js'

const props = defineProps({
  isDark: Boolean,
  currentView: { type: String, default: null },
})

const emit = defineEmits(['toggle-theme', 'set-view'])

const isMetadataView    = computed(() => props.currentView?.startsWith('metadata-'))
const isDataModelsView  = computed(() => ['quality-signatures', 'data-models-schema'].includes(props.currentView))
const isUnificationView = computed(() => ['unification-pipeline', 'unification-retention', 'unification-label-stats', 'unification-label-mapping'].includes(props.currentView))
const isResultsView     = computed(() => ['performance-reproduce', 'performance-cross-dataset'].includes(props.currentView))
const isMoreView        = computed(() => ['quality-relations', 'quality-mentions', 'quality-abbreviation'].includes(props.currentView))

const { dockerMode } = useDockerMode()
const { annotator } = useAnnotator()
const annotatorDialog = ref(false)
const annotatorInput = ref(annotator.value)

function saveAnnotator() {
  annotator.value = annotatorInput.value.trim()
  annotatorDialog.value = false
}
</script>
