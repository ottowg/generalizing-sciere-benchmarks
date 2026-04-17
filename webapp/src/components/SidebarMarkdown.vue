<template lang="pug">
v-list(nav density="compact" open-strategy="multiple" :opened="openedGroups")

  //- ── Documentation ──────────────────────────────────────────────────────
  template(v-if="files.docs?.length")
    v-list-subheader Documentation
    v-list-item(
      v-for="doc in files.docs"
      :key="doc.path"
      :title="basename(doc.name)"
      prepend-icon="mdi-file-document-outline"
      :active="selected === doc.path"
      active-color="primary"
      @click="emit('select', doc.path)"
    )

  //- ── Paper ──────────────────────────────────────────────────────────────
  template(v-if="files.paper?.length")
    v-list-subheader Paper
    v-list-group(
      v-for="(items, folder) in paperGroups"
      :key="'paper-' + folder"
      :value="'paper-' + folder"
    )
      template(#activator="{ props }")
        v-list-item(v-bind="props" :title="folderTitle(folder)" prepend-icon="mdi-folder-outline")
      v-list-item(
        v-for="file in items"
        :key="file.path"
        :title="basename(file.name)"
        prepend-icon="mdi-file-document-outline"
        :active="selected === file.path"
        active-color="primary"
        @click="emit('select', file.path)"
      )

  //- ── Reports ────────────────────────────────────────────────────────────
  template(v-if="files.reports?.length")
    v-list-subheader Reports
    v-list-group(
      v-for="(items, folder) in reportGroups"
      :key="'report-' + folder"
      :value="'report-' + folder"
    )
      template(#activator="{ props }")
        v-list-item(v-bind="props" :title="folderTitle(folder)" prepend-icon="mdi-folder-outline")
      v-list-item(
        v-for="file in items"
        :key="file.path"
        :title="basename(file.name)"
        prepend-icon="mdi-file-chart-outline"
        :active="selected === file.path"
        active-color="primary"
        @click="emit('select', file.path)"
      )
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  files: { type: Object, default: () => ({ docs: [], paper: [], reports: [] }) },
  selected: { type: String, default: null },
})

const emit = defineEmits(['select'])

function makeGroups(files, prefix) {
  const groups = {}
  for (const file of files) {
    const parts = file.path.replace(prefix + '/', '').split('/')
    const folder = parts.length > 1 ? parts[0] : ''
    if (!groups[folder]) groups[folder] = []
    groups[folder].push(file)
  }
  return groups
}

const paperGroups  = computed(() => makeGroups(props.files.paper  ?? [], 'paper'))
const reportGroups = computed(() => makeGroups(props.files.reports ?? [], 'reports'))

const openedGroups = computed(() => [
  ...Object.keys(paperGroups.value).map(f  => 'paper-'  + f),
  ...Object.keys(reportGroups.value).map(f => 'report-' + f),
])

function basename(filePath) {
  return filePath.split('/').pop().replace(/\.md$/, '').replace(/_/g, ' ')
}

function folderTitle(folder) {
  if (!folder) return '(root)'
  return folder.replace(/_/g, ' ')
}
</script>
