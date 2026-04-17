<template lang="pug">
v-navigation-drawer(v-model="drawerModel" width="300")
  SidebarQuality(
    v-if="isQualityView"
    :current-view="currentView"
    @set-view="emit('set-view', $event)"
  )
  SidebarMarkdown(
    v-else
    :files="files"
    :selected="selected"
    @select="emit('select', $event)"
  )
</template>

<script setup>
import { computed } from 'vue'
import SidebarMarkdown from './SidebarMarkdown.vue'
import SidebarQuality from './SidebarQuality.vue'

const props = defineProps({
  files: { type: Object, default: () => ({ docs: [], paper: [], reports: [] }) },
  selected: { type: String, default: null },
  currentView: { type: String, default: null },
})

const emit = defineEmits(['select', 'set-view'])

const drawerModel = defineModel('drawer')

const isQualityView = computed(() => props.currentView !== null && props.currentView !== undefined)
</script>
