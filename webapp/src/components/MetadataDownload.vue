<template lang="pug">
v-container(fluid)
  h2.text-h5.mb-1 Download
  p.text-body-2.text-medium-emphasis.mb-4
    | Export metadata as JSON or CSV. Data is loaded from the pre-built metadata file —
    | click Rebuild in any metadata view first if you need fresh data.

  v-alert(v-if="error" type="error" density="compact" closable class="mb-4") {{ error }}
  v-progress-linear(v-if="loading" indeterminate class="mb-4")

  v-row(dense)
    //- ── Paper metadata ──────────────────────────────────────────────────────
    v-col(cols="12" md="6")
      v-card(variant="outlined")
        v-card-title.text-subtitle-1
          v-icon.mr-2(size="18") mdi-file-document-multiple-outline
          | Papers
        v-card-subtitle(v-if="paperCount") {{ paperCount }} papers across GSAP, SciER, SciNLP
        v-card-text
          p.text-body-2.mb-3
            | Bibliographic metadata for all annotated publications: title, authors, year,
            | venue, outlet, citation count, arXiv / DOI identifiers, dataset membership and split.
          .d-flex(style="gap:10px;flex-wrap:wrap;")
            v-btn(
              variant="tonal" color="primary" prepend-icon="mdi-code-json"
              :loading="downloading.papers_json" :disabled="!meta"
              @click="downloadPapersJSON"
            ) JSON
            v-btn(
              variant="tonal" color="primary" prepend-icon="mdi-table"
              :loading="downloading.papers_csv" :disabled="!meta"
              @click="downloadPapersCSV"
            ) CSV

    //- ── Outlet info ─────────────────────────────────────────────────────────
    v-col(cols="12" md="6")
      v-card(variant="outlined")
        v-card-title.text-subtitle-1
          v-icon.mr-2(size="18") mdi-bookshelf
          | Outlets
        v-card-subtitle(v-if="outletCount") {{ outletCount }} publication venues
        v-card-text
          p.text-body-2.mb-3
            | Publication venue metadata: abbreviation, full name, type, topic area,
            | h-index, i10-index, 2-year citedness, and per-dataset paper counts.
          .d-flex(style="gap:10px;flex-wrap:wrap;")
            v-btn(
              variant="tonal" color="secondary" prepend-icon="mdi-code-json"
              :loading="downloading.outlets_json" :disabled="!meta"
              @click="downloadOutletsJSON"
            ) JSON
            v-btn(
              variant="tonal" color="secondary" prepend-icon="mdi-table"
              :loading="downloading.outlets_csv" :disabled="!meta"
              @click="downloadOutletsCSV"
            ) CSV
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const meta     = ref(null)
const loading  = ref(false)
const error    = ref(null)
const downloading = ref({
  papers_json: false, papers_csv: false,
  outlets_json: false, outlets_csv: false,
})

const paperCount  = computed(() => meta.value?.paper_map?.points?.length ?? null)
const outletCount = computed(() => meta.value?.outlet_list?.length ?? null)

// ── data load ─────────────────────────────────────────────────────────────────

async function load() {
  loading.value = true
  error.value   = null
  try {
    const r = await fetch('/api/paper-metadata')
    if (r.status === 404) { error.value = 'No metadata found — rebuild first.'; return }
    if (!r.ok) throw new Error(`HTTP ${r.status}`)
    meta.value = await r.json()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(load)

// ── CSV helpers ───────────────────────────────────────────────────────────────

function toCSV(rows, keys) {
  const escape = v => {
    const s = v == null ? '' : String(v)
    return s.includes(',') || s.includes('"') || s.includes('\n')
      ? `"${s.replace(/"/g, '""')}"` : s
  }
  return [keys.join(','), ...rows.map(r => keys.map(k => escape(r[k])).join(','))].join('\n')
}

function triggerDownload(content, filename, mime) {
  const blob = new Blob([content], { type: mime })
  const url  = URL.createObjectURL(blob)
  const a    = Object.assign(document.createElement('a'), { href: url, download: filename })
  a.click()
  URL.revokeObjectURL(url)
}

// ── papers ────────────────────────────────────────────────────────────────────

const PAPER_CSV_KEYS = [
  'doc_id', 'dataset', 'dataset_detail', 'split',
  'title', 'year', 'outlet_abbr', 'outlet_type', 'outlet_topic',
  'cited_by_count', 'arxiv_id', 'doi',
]

function downloadPapersJSON() {
  downloading.value.papers_json = true
  try {
    const rows = meta.value.paper_map.points.map(p => {
      const out = {}
      PAPER_CSV_KEYS.forEach(k => { out[k] = p[k] ?? null })
      return out
    })
    triggerDownload(JSON.stringify(rows, null, 2), 'unifiedsciere_papers.json', 'application/json')
  } finally {
    downloading.value.papers_json = false
  }
}

function downloadPapersCSV() {
  downloading.value.papers_csv = true
  try {
    const rows = meta.value.paper_map.points
    triggerDownload(toCSV(rows, PAPER_CSV_KEYS), 'unifiedsciere_papers.csv', 'text/csv')
  } finally {
    downloading.value.papers_csv = false
  }
}

// ── outlets ───────────────────────────────────────────────────────────────────

const OUTLET_CSV_KEYS = [
  'abbr', 'name', 'type', 'topic',
  'h_index', 'i10_index', 'citedness_2yr',
  'papers_total', 'papers_gsap_ere', 'papers_scier', 'papers_scinlp',
  'openalex_url',
]

function downloadOutletsJSON() {
  downloading.value.outlets_json = true
  try {
    const rows = meta.value.outlet_list.map(o => {
      const out = {}
      OUTLET_CSV_KEYS.forEach(k => { out[k] = o[k] ?? null })
      return out
    })
    triggerDownload(JSON.stringify(rows, null, 2), 'unifiedsciere_outlets.json', 'application/json')
  } finally {
    downloading.value.outlets_json = false
  }
}

function downloadOutletsCSV() {
  downloading.value.outlets_csv = true
  try {
    triggerDownload(
      toCSV(meta.value.outlet_list, OUTLET_CSV_KEYS),
      'unifiedsciere_outlets.csv', 'text/csv'
    )
  } finally {
    downloading.value.outlets_csv = false
  }
}
</script>
