<template lang="pug">
v-container(fluid class="pa-8" style="max-width: 1000px")
  .d-flex.justify-end.mb-2(v-if="props.path")
    v-btn(icon size="small" variant="text" :loading="loading" @click="load(props.path)")
      v-icon mdi-refresh
  .d-flex.justify-center.mt-10(v-if="loading")
    v-progress-circular(indeterminate color="primary")
  v-alert(v-else-if="error" type="error" class="mt-4") {{ error }}
  .markdown-body(v-else v-html="rendered")
</template>

<script setup>
import { ref, watch } from 'vue'
import { marked } from 'marked'

const props = defineProps({ path: String })

const rendered = ref('')
const loading = ref(false)
const error = ref(null)

async function load(path) {
  if (!path) return
  loading.value = true
  error.value = null
  try {
    const res = await fetch(`/api/content?path=${encodeURIComponent(path)}&_t=${Date.now()}`)
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
    rendered.value = marked(await res.text())
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

watch(() => props.path, load, { immediate: true })
</script>

<style scoped>
.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3) {
  margin-top: 1.5em;
  margin-bottom: 0.5em;
  font-weight: 600;
}
.markdown-body :deep(h1) { font-size: 1.8em; }
.markdown-body :deep(h2) { font-size: 1.4em; }
.markdown-body :deep(h3) { font-size: 1.15em; }

.markdown-body :deep(code) {
  background: rgba(128, 128, 128, 0.12);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.88em;
  font-family: monospace;
}
.markdown-body :deep(pre) {
  background: rgba(128, 128, 128, 0.1);
  padding: 1em;
  border-radius: 6px;
  overflow-x: auto;
  margin: 1em 0;
}
.markdown-body :deep(pre code) {
  background: none;
  padding: 0;
}
.markdown-body :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 1em 0;
  font-size: 0.92em;
}
.markdown-body :deep(th),
.markdown-body :deep(td) {
  border: 1px solid rgba(128, 128, 128, 0.25);
  padding: 8px 14px;
}
.markdown-body :deep(th) {
  background: rgba(128, 128, 128, 0.08);
  font-weight: 600;
}
.markdown-body :deep(tr:hover) {
  background: rgba(128, 128, 128, 0.05);
}
.markdown-body :deep(blockquote) {
  border-left: 4px solid rgba(128, 128, 128, 0.3);
  margin: 1em 0;
  padding: 0.5em 1em;
  color: rgba(128, 128, 128, 0.8);
}
.markdown-body :deep(li) {
  margin: 0.25em 0;
}
.markdown-body :deep(p) {
  line-height: 1.7;
  margin: 0.75em 0;
}
</style>
