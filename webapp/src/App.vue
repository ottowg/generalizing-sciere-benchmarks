<template lang="pug">
v-app(:theme="theme")
  AppNavBar(
    :is-dark="isDark"
    :current-view="currentView"
    @toggle-theme="toggleTheme"
    @set-view="setView"
  )

  v-main
    QualityMentions(v-if="currentView === 'quality-mentions'")
    QualityRelations(v-else-if="currentView === 'quality-relations'")
    AbbreviationRelations(v-else-if="currentView === 'quality-abbreviation'")
    UnificationPipeline(v-else-if="currentView === 'unification-pipeline'")
    UnificationRetention(v-else-if="currentView === 'unification-retention'")
    LabelStatistics(v-else-if="currentView === 'unification-label-stats'")
    LabelMapping(v-else-if="currentView === 'unification-label-mapping'")
    RelationSignatures(v-else-if="currentView === 'quality-signatures'")
    ExamplePaper(v-else-if="currentView === 'quality-example-paper'")
    RelationGraphDemo(v-else-if="currentView === 'data-models-graph'")
    SchemaPreview(v-else-if="currentView === 'data-models-schema'")
    ReproduceResults(v-else-if="currentView === 'performance-reproduce'")
    CrossDatasetPerformance(v-else-if="currentView === 'performance-cross-dataset'")
    MetadataDownload(v-else-if="currentView === 'metadata-download'")
    PaperMetadata(v-else-if="currentView?.startsWith('metadata-')" :view="currentView")
    v-sheet(v-else class="d-flex align-center justify-center" style="height:60vh;")
      span.text-disabled Select a view from the menu above.
</template>

<script setup>
import { ref, computed } from 'vue'
import AppNavBar from './components/AppNavBar.vue'
import QualityMentions from './components/QualityMentions.vue'
import AbbreviationRelations from './components/AbbreviationRelations.vue'
import QualityRelations from './components/QualityRelations.vue'
import UnificationPipeline from './components/UnificationPipeline.vue'
import UnificationRetention from './components/UnificationRetention.vue'
import LabelStatistics from './components/LabelStatistics.vue'
import LabelMapping from './components/LabelMapping.vue'
import RelationGraphDemo from './components/RelationGraphDemo.vue'
import RelationSignatures from './components/RelationSignatures.vue'
import ExamplePaper from './components/ExamplePaper.vue'
import SchemaPreview from './components/SchemaPreview.vue'
import ReproduceResults from './components/ReproduceResults.vue'
import CrossDatasetPerformance from './components/CrossDatasetPerformance.vue'
import PaperMetadata from './components/PaperMetadata.vue'
import MetadataDownload from './components/MetadataDownload.vue'

const theme = ref('light')
const isDark = computed(() => theme.value === 'dark')
const currentView = ref('metadata-pub-map')

function toggleTheme() {
  theme.value = isDark.value ? 'light' : 'dark'
}

function setView(view) {
  currentView.value = view
}
</script>
