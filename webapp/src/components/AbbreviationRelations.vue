<template lang="pug">
v-container(fluid class="pa-6")
  .d-flex.align-center.mb-1
    div
      h2.text-h5 {{ experiment?.title || 'Abbreviation Relations' }}
      .text-subtitle-2.text-medium-emphasis(v-if="experiment?.subtitle") {{ experiment.subtitle }}
    v-spacer
    .text-caption.text-medium-emphasis.mr-3(v-if="stats") Generated: {{ fmtDate(stats.generated) }}
    v-btn(icon size="small" variant="text" :loading="loading" title="Regenerate statistics" @click="regenerate")
      v-icon mdi-refresh

  v-alert(v-if="error" type="error" variant="tonal" class="mb-4" closable @click:close="error=null") {{ error }}
  v-alert(v-if="regenMsg" type="success" variant="tonal" class="mb-4" closable @click:close="regenMsg=null") {{ regenMsg }}

  v-tabs(v-model="tab" color="primary" class="mb-4")
    v-tab(value="overview") Overview
    v-tab(value="coverage") Coverage Stats
    v-tab(value="detection") Detection Stats
    v-tab(value="annotation") Annotation Queue

  v-tabs-window(v-model="tab")

    //- ── Overview ──────────────────────────────────────────────────────────
    v-tabs-window-item(value="overview")
      v-row
        v-col(cols="12" md="8")
          .text-body-1.mb-4(v-if="experiment?.description" style="white-space:pre-wrap") {{ experiment.description }}

          template(v-if="experiment?.motivation")
            h3.text-subtitle-1.font-weight-bold.mb-2 Motivation
            .text-body-2.mb-4(style="white-space:pre-wrap") {{ experiment.motivation }}

          template(v-if="experiment?.research_questions?.length")
            h3.text-subtitle-1.font-weight-bold.mb-2 Research Questions
            v-list(lines="two" class="mb-4")
              v-list-item(
                v-for="rq in experiment.research_questions"
                :key="rq.id"
                :subtitle="rq.text"
                class="px-0"
              )
                template(#title)
                  span.font-weight-bold {{ rq.id }}
                  span.ml-1.text-medium-emphasis — {{ rq.short }}

        v-col(cols="12" md="4")
          template(v-if="experiment?.subtasks")
            h3.text-subtitle-1.font-weight-bold.mb-2 Detection Subtasks
            v-card(v-for="(sub, key) in experiment.subtasks" :key="key" variant="outlined" class="mb-3")
              v-card-title.text-body-2 Subtask {{ key }}: {{ sub.name }}
              v-card-text
                .text-caption.mb-2(style="white-space:pre-wrap") {{ sub.description }}
                v-list(density="compact" class="pa-0")
                  v-list-item(
                    v-for="sig in sub.signals"
                    :key="sig.id"
                    :subtitle="sig.description"
                    class="px-0"
                  )
                    template(#title)
                      span.text-caption.font-weight-medium {{ sig.id }}: {{ sig.name }}

    //- ── Coverage ──────────────────────────────────────────────────────────
    v-tabs-window-item(value="coverage")
      template(v-if="stats")
        h3.text-subtitle-1.font-weight-bold.mb-1 Table 1: Parenthesized Gold Mentions (%)
        .text-caption.text-medium-emphasis.mb-3 Fraction of gold entity mentions whose text contains '(' by dataset and split

        v-table(density="compact" class="abbrev-table mb-6")
          thead
            tr
              th Dataset
              th.text-right(v-for="split in splits" :key="split") {{ split }}
          tbody
            tr(v-for="ds in datasets" :key="ds")
              td {{ ds }}
              td.text-right(v-for="split in splits" :key="split")
                span(:style="pctStyle(goldPct(ds, split), goldMax(split))") {{ fmtPct(goldPct(ds, split)) }}

        h3.text-subtitle-1.font-weight-bold.mb-1 Table 2: Parenthesized Predicted Mentions (%)
        .text-caption.text-medium-emphasis.mb-3 Model predictions on each eval dataset × split — higher values indicate the model transfers its training distribution

        v-table(density="compact" class="abbrev-table mb-4")
          thead
            tr
              th Eval Dataset
              th Split
              th.text-right(v-for="model in models" :key="model") {{ model }} model
          tbody
            template(v-for="ds in datasets" :key="ds")
              tr(v-for="split in predSplits" :key="ds+split")
                td {{ ds }}
                td.text-caption {{ split }}
                td.text-right(v-for="model in models" :key="model")
                  span(:style="pctStyle(predPct(ds, split, model), predMax(ds, split))") {{ fmtPct(predPct(ds, split, model)) }}

        v-alert(v-if="stats.errors?.length" type="warning" variant="tonal" class="mt-4" density="compact")
          .text-caption(v-for="e in stats.errors" :key="e") {{ e }}

      v-skeleton-loader(v-else type="table" :loading="loading")

    //- ── Detection ─────────────────────────────────────────────────────────
    v-tabs-window-item(value="detection")
      template(v-if="stats")
        .text-caption.text-medium-emphasis.mb-4
          | Rule-based detector applied to gold annotations.
          | Subtask A: mention pairs linked by coreference / Synonym-Of / SimilarWith.
          | Subtask B: single spans with parenthetical text encoding both forms.

        v-tabs(v-model="detectionSplit" density="compact" color="primary" class="mb-3")
          v-tab(v-for="split in splits" :key="split" :value="split") {{ split }}

        v-table(density="compact" class="abbrev-table")
          thead
            tr
              th Dataset
              th.text-right Subtask A candidates
              th.text-right A positives
              th.text-right A borderline
              th.text-right A negatives
              th.text-right Subtask B candidates
              th.text-right B positives
              th.text-right B borderline
              th.text-right B negatives
          tbody
            tr(v-for="row in detectionRows" :key="row.dataset")
              td {{ row.dataset }}
              td.text-right {{ row.subtask_a.candidates }}
              td.text-right.font-weight-medium(:style="posStyle(row.subtask_a.positives, row.subtask_a.candidates)") {{ row.subtask_a.positives }}
              td.text-right(:style="borderStyle(row.subtask_a.borderline, row.subtask_a.candidates)") {{ row.subtask_a.borderline }}
              td.text-right {{ row.subtask_a.negatives }}
              td.text-right {{ row.subtask_b.candidates }}
              td.text-right.font-weight-medium(:style="posStyle(row.subtask_b.positives, row.subtask_b.candidates)") {{ row.subtask_b.positives }}
              td.text-right(:style="borderStyle(row.subtask_b.borderline, row.subtask_b.candidates)") {{ row.subtask_b.borderline }}
              td.text-right {{ row.subtask_b.negatives }}

      v-skeleton-loader(v-else type="table" :loading="loading")

    //- ── Annotation Queue ───────────────────────────────────────────────────
    v-tabs-window-item(value="annotation")
      AbbreviationReview(v-model="reviewOpen" @annotated="loadQueueMeta")

      v-list(lines="two")
        v-list-item(
          prepend-icon="mdi-tag-text-outline"
          title="Abbreviation Annotation Queue"
          subtitle="Candidates sampled via Gaussian from the full distribution — annotate to refine the classifier"
        )
          template(#append)
            .d-flex.align-center.gap-2
              v-btn(
                size="small"
                variant="text"
                icon="mdi-refresh"
                :loading="rebuilding"
                title="Rebuild queue"
                @click="rebuildQueue"
              )
              v-btn(
                color="primary"
                variant="tonal"
                prepend-icon="mdi-play"
                @click="reviewOpen = true"
              ) Start

      //- ── Queue config ────────────────────────────────────────────────────
      .d-flex.align-center.flex-wrap.gap-3.mt-2.mb-1
        v-text-field(
          v-model.number="queueSize"
          label="Queue size per subtask"
          type="number"
          min="5" max="500"
          density="compact"
          variant="outlined"
          hide-details
          style="max-width:210px"
        )
        v-text-field(
          v-model.number="sigmaCfg"
          label="Gaussian σ"
          type="number"
          min="0.01" max="0.5" step="0.01"
          density="compact"
          variant="outlined"
          hide-details
          style="max-width:140px"
        )

      //- ── Rebuild log ─────────────────────────────────────────────────────
      v-card.mt-3(v-if="rebuildLog.length" variant="outlined")
        v-card-text.pa-2
          pre(ref="logEl" style="max-height:220px;overflow-y:auto;font-size:0.72rem;line-height:1.5;font-family:monospace;white-space:pre-wrap")
            span(
              v-for="(line, i) in rebuildLog" :key="i"
              :class="line.type === 'err' ? 'text-warning' : line.type === 'error' ? 'text-error' : ''"
            ) {{ line.text + '\n' }}

      //- ── Classifier performance ────────────────────────────────────────
      template(v-if="queueMeta")
        v-divider.my-4

        .text-subtitle-2.font-weight-bold.mb-3 Classifier Performance
        v-row(dense)
          v-col(v-for="sub in ['A','B']" :key="sub" cols="12" sm="6")
            v-card(variant="outlined")
              v-card-title.text-body-2 Subtask {{ sub }}
              v-card-text
                template(v-if="queueMeta.summary && queueMeta.summary[sub]")
                  .text-caption.text-medium-emphasis.mb-1
                    | {{ totalCandidates(sub) }} candidates
                    |  · {{ queueMeta.summary[sub].n_weak_pos }} pos
                    |  · {{ queueMeta.summary[sub].n_borderline_unannotated }} borderline
                    |  · {{ queueMeta.summary[sub].n_weak_neg }} neg
                  .text-caption.text-medium-emphasis.mb-2
                    | {{ (queueMeta.summary[sub].n_human_pos || 0) + (queueMeta.summary[sub].n_human_neg || 0) }} manual
                    |  · {{ queueMeta.summary[sub].n_human_pos || 0 }} pos
                    |  · {{ queueMeta.summary[sub].n_human_neg || 0 }} neg
                template(v-if="queueMeta['eval_' + sub.toLowerCase()]")
                  v-table(density="compact" class="abbrev-table")
                    tbody
                      tr
                        td.text-caption Precision
                        td.text-right.font-weight-medium {{ (queueMeta['eval_' + sub.toLowerCase()].precision * 100).toFixed(1) }}
                      tr
                        td.text-caption Recall
                        td.text-right.font-weight-medium {{ (queueMeta['eval_' + sub.toLowerCase()].recall * 100).toFixed(1) }}
                      tr
                        td.text-caption F1
                        td.text-right.font-weight-medium {{ (queueMeta['eval_' + sub.toLowerCase()].f1 * 100).toFixed(1) }}
                  .text-caption.text-medium-emphasis.mt-2
                    | Test set: {{ queueMeta['eval_' + sub.toLowerCase()].n_test }} items
                    |  ({{ queueMeta['eval_' + sub.toLowerCase()].pct_manual }}% manual)
                .text-caption.text-medium-emphasis(v-else) Not enough test data yet

        //- ── Evaluation history ──────────────────────────────────────────
        template(v-if="evalHistory.length")
          v-row.mt-5(dense)
            v-col(v-for="sub in ['A','B']" :key="sub" cols="12" md="6")
              .text-subtitle-2.font-weight-bold.mb-2 Subtask {{ sub }} — Eval History
              v-table(density="compact" class="abbrev-table")
                thead
                  tr
                    th Time
                    th.text-right Annot.
                    th.text-right Rule F1
                    th.text-right ML F1
                    th.text-right Gain
                    th.text-right P
                    th.text-right R
                    th.text-right n_test
                    th.text-right manual%
                tbody
                  tr(v-for="(h, i) in evalHistory.filter(h => h[sub])" :key="i")
                    td.text-caption {{ fmtDate(h.timestamp) }}
                    td.text-right {{ h.n_annotated }}
                    td.text-right.text-medium-emphasis {{ h[sub].rule_based ? (h[sub].rule_based.f1 * 100).toFixed(1) : '—' }}
                    td.text-right.font-weight-medium {{ (h[sub].f1 * 100).toFixed(1) }}
                    td.text-right(:class="gainColor(h[sub].f1_gain)")
                      | {{ h[sub].f1_gain != null ? (h[sub].f1_gain >= 0 ? '+' : '') + (h[sub].f1_gain * 100).toFixed(1) : '—' }}
                    td.text-right {{ (h[sub].precision * 100).toFixed(1) }}
                    td.text-right {{ (h[sub].recall * 100).toFixed(1) }}
                    td.text-right {{ h[sub].n_test }}
                    td.text-right {{ h[sub].pct_manual }}%
                  tr(v-if="!evalHistory.filter(h => h[sub]).length")
                    td.text-caption.text-medium-emphasis(colspan="9") No evaluations yet
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import AbbreviationReview from './AbbreviationReview.vue'

const YAML_PATH    = 'data/abbreviation/experiment.yaml'
const STATS_PATH   = 'data/abbreviation/coverage_stats.json'
const QUEUE_PATH   = 'data/abbreviation/al_queue.json'
const HISTORY_PATH = 'data/abbreviation/eval_history.json'

const tab            = ref('overview')
const detectionSplit = ref('dev')
const reviewOpen     = ref(false)
const rebuilding     = ref(false)
const experiment    = ref(null)
const stats         = ref(null)
const loading       = ref(false)
const error         = ref(null)
const regenMsg      = ref(null)
const queueMeta     = ref(null)   // { eval_a, eval_b, summary, annotations_loaded }
const evalHistory   = ref([])

// Queue config & rebuild log
const queueSize  = ref(20)
const sigmaCfg   = ref(0.15)
const rebuildLog = ref([])   // [{ type: 'log'|'err'|'error'|'done', text }]
const logEl      = ref(null) // template ref for auto-scroll

// ── Derived ─────────────────────────────────────────────────────────────────

const splits     = ['train', 'dev', 'test']
const predSplits = ['dev', 'test']
const datasets   = computed(() => {
  if (!stats.value) return []
  return [...new Set(stats.value.parenthesized_gold.map(r => r.dataset))].sort()
})
const models = computed(() => {
  if (!stats.value) return []
  return [...new Set(stats.value.parenthesized_pred.map(r => r.model))].sort()
})

function goldPct(dataset, split) {
  if (!stats.value) return null
  const row = stats.value.parenthesized_gold.find(r => r.dataset === dataset && r.split === split)
  return row ? row.pct : null
}

function goldMax(split) {
  if (!stats.value) return 0
  return Math.max(...stats.value.parenthesized_gold
    .filter(r => r.split === split)
    .map(r => r.pct ?? 0))
}

function predPct(dataset, split, model) {
  if (!stats.value) return null
  const row = stats.value.parenthesized_pred.find(
    r => r.dataset === dataset && r.split === split && r.model === model
  )
  return row ? row.pct : null
}

function predMax(dataset, split) {
  if (!stats.value) return 0
  return Math.max(...stats.value.parenthesized_pred
    .filter(r => r.dataset === dataset && r.split === split)
    .map(r => r.pct ?? 0))
}

const detectionRows = computed(() => {
  if (!stats.value) return []
  return stats.value.detection.filter(
    r => r.split === detectionSplit.value && r.annotator === 'gold'
  )
})

// ── Formatting ───────────────────────────────────────────────────────────────

function fmtPct(v) {
  if (v === null || v === undefined) return '—'
  return v.toFixed(1) + ' %'
}

function gainColor(gain) {
  if (gain == null) return ''
  if (gain > 0.005) return 'text-success'
  if (gain < -0.005) return 'text-error'
  return 'text-medium-emphasis'
}

function totalCandidates(sub) {
  const s = queueMeta.value?.summary?.[sub]
  if (!s) return 0
  return (s.n_weak_pos || 0) + (s.n_weak_neg || 0) + (s.n_borderline_unannotated || 0)
         + (s.n_human_pos || 0) + (s.n_human_neg || 0)
}

function fmtDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })
}

function pctStyle(val, maxVal) {
  if (val === null || val === undefined || maxVal === 0) return ''
  const t = val / maxVal
  // Blue tones: low = light blue, high = strong blue
  const r = Math.round(220 - t * 100)
  const g = Math.round(230 - t * 80)
  const b = Math.round(255 - t * 60)
  return `color:rgb(${r},${g},${b});font-weight:${t > 0.7 ? 700 : 400}`
}

function posStyle(count, total) {
  if (!total) return ''
  const t = count / total
  return `color:rgb(${Math.round(40 + (1-t)*180)},${Math.round(120 + t*80)},${Math.round(40 + (1-t)*60)})`
}

function borderStyle(count, total) {
  if (!total) return ''
  return 'color:rgba(0,0,0,0.5)'
}

// ── Data loading ─────────────────────────────────────────────────────────────

async function loadAll() {
  loading.value = true
  error.value = null
  try {
    const [expRes, statsRes] = await Promise.all([
      fetch(`/api/yaml?path=${encodeURIComponent(YAML_PATH)}`),
      fetch(`/api/json?path=${encodeURIComponent(STATS_PATH)}&_t=${Date.now()}`),
    ])
    if (expRes.ok) experiment.value = await expRes.json()
    if (statsRes.ok) stats.value = await statsRes.json()
    else if (statsRes.status === 404) stats.value = null
    else throw new Error(`Stats: ${statsRes.status} ${statsRes.statusText}`)
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function loadQueueMeta() {
  try {
    const [qRes, hRes] = await Promise.all([
      fetch(`/api/json?path=${encodeURIComponent(QUEUE_PATH)}&_t=${Date.now()}`),
      fetch(`/api/json?path=${encodeURIComponent(HISTORY_PATH)}&_t=${Date.now()}`),
    ])
    if (qRes.ok) {
      const d = await qRes.json()
      queueMeta.value = { eval_a: d.eval_a ?? null, eval_b: d.eval_b ?? null,
                          summary: d.summary, annotations_loaded: d.annotations_loaded }
    }
    if (hRes.ok) evalHistory.value = (await hRes.json()).slice().reverse()
    else if (hRes.status === 404) evalHistory.value = []
  } catch (_) { /* silently ignore */ }
}

async function regenerate() {
  loading.value = true
  error.value = null
  regenMsg.value = null
  try {
    const res    = await fetch('/api/regenerate?report=abbreviation-coverage', { method: 'POST' })
    const result = await res.json()
    if (!result.ok) throw new Error(result.stderr || 'Script failed')
    const statsRes = await fetch(`/api/json?path=${encodeURIComponent(STATS_PATH)}&_t=${Date.now()}`)
    if (statsRes.ok) stats.value = await statsRes.json()
    regenMsg.value = 'Statistics regenerated successfully.'
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function rebuildQueue() {
  rebuilding.value = true
  rebuildLog.value = []
  error.value = null
  regenMsg.value = null

  const params = new URLSearchParams({
    report:     'abbreviation-al-queue',
    queue_size: String(queueSize.value),
    sigma:      String(sigmaCfg.value),
  })
  const es = new EventSource(`/api/regenerate-stream?${params}`)

  const scrollLog = () => nextTick(() => {
    if (logEl.value) logEl.value.scrollTop = logEl.value.scrollHeight
  })

  es.onmessage = async (ev) => {
    const { type, text } = JSON.parse(ev.data)
    rebuildLog.value.push({ type, text })
    scrollLog()
    if (type === 'done' || type === 'error') {
      es.close()
      rebuilding.value = false
      if (type === 'done') {
        await loadQueueMeta()
        regenMsg.value = text?.includes('up to date')
          ? 'Queue is up to date — no new annotations.'
          : 'Queue rebuilt successfully.'
      } else {
        error.value = 'Queue rebuild failed — see log above.'
      }
    }
  }

  es.onerror = () => {
    es.close()
    rebuilding.value = false
    error.value = 'Connection error during rebuild.'
  }
}

onMounted(() => { loadAll(); loadQueueMeta() })
</script>

<style scoped>
.abbrev-table {
  width: auto;
}
</style>
