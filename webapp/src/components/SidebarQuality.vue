<template lang="pug">
v-list(nav density="compact")
  v-list-subheader Annotation Review
  v-list-item(
    prepend-icon="mdi-tag-outline"
    title="Mentions"
    :active="currentView === 'quality-mentions'"
    active-color="primary"
    @click="emit('set-view', 'quality-mentions')"
  )
  v-list-item(
    prepend-icon="mdi-relation-many-to-many"
    title="Relations"
    :active="currentView === 'quality-relations'"
    active-color="primary"
    @click="emit('set-view', 'quality-relations')"
  )

  v-divider.my-2

  v-list-subheader Quality
  v-list-item(
    prepend-icon="mdi-text-short"
    title="Abbreviation Relations"
    :active="currentView === 'quality-abbreviation'"
    active-color="primary"
    @click="emit('set-view', 'quality-abbreviation')"
  )

  v-divider.my-2

  v-list-subheader Unification
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
</template>

<script setup>
defineProps({
  currentView: { type: String, default: null },
})

const emit = defineEmits(['set-view'])
</script>
