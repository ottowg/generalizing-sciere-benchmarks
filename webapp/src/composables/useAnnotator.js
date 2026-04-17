import { ref, watch } from 'vue'

const STORAGE_KEY = 'annotator-name'

const annotator = ref(localStorage.getItem(STORAGE_KEY) || '')

watch(annotator, val => {
  if (val) localStorage.setItem(STORAGE_KEY, val)
  else localStorage.removeItem(STORAGE_KEY)
})

export function useAnnotator() {
  return { annotator }
}
