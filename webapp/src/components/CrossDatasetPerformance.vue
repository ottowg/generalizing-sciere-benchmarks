<template lang="pug">
v-container(fluid)
  .d-flex.align-center.mb-3
    h2.text-h5 Cross-Dataset Performance
    v-chip.ml-3(v-if="generatedAt" size="small" variant="tonal" color="grey") {{ generatedAt }}
    v-spacer
    v-switch(v-model="showStd" label="Show ± std" density="compact" hide-details color="primary")
    v-btn(v-if="!dockerMode" variant="text" prepend-icon="mdi-refresh" size="small" :loading="building" @click="rebuild") Rebuild

  v-tabs(v-model="activeTab" density="compact" color="primary" class="mb-4")
    v-tab(value="radar") Radar Charts
    v-tab(value="summary") Summary
    v-tab(value="entities") Entities
    v-tab(value="relations") Relations
    v-tab(value="multi-sciere-generalization") MultiSciERE Generalization

  //- ── Radar Charts tab ────────────────────────────────────────────────────
  div(v-if="activeTab === 'radar'")
    .d-flex.flex-wrap.ga-4.mb-3
      div
        .text-caption.text-medium-emphasis.mb-1 Metrics
        v-btn-toggle(v-model="cdRadarMetrics" multiple density="compact" variant="outlined" color="primary")
          v-btn(value="ner" size="small") NER
          v-btn(value="ner_p" size="small") NER≈
          v-btn(value="re" size="small") RE
          v-btn(value="rep_p" size="small") RE+≈
          v-btn(value="rep" size="small") RE+
      div
        .text-caption.text-medium-emphasis.mb-1 Group by
        v-btn-toggle(v-model="cdRadarGroupBy" mandatory density="compact" variant="outlined" color="secondary")
          v-btn(value="metric" size="small") Metric
          v-btn(value="dataset" size="small") Dataset
      div
        .text-caption.text-medium-emphasis.mb-1 Split
        v-btn-toggle(v-model="cdRadarSplit" mandatory density="compact" variant="outlined" color="teal")
          v-btn(value="test" size="small") Test
          v-btn(value="dev" size="small") Dev
    div(v-if="!cdRadarHasData" class="text-medium-emphasis text-body-2 pa-4") No data yet — click Rebuild.
    template(v-else-if="cdRadarGroupBy === 'metric'")
      v-row(dense)
        v-col(v-for="metric in cdRadarActiveMetrics" :key="metric.id" cols="12" sm="6")
          v-card(variant="outlined")
            v-card-title.text-subtitle-2.text-center.pt-3.pb-0 {{ metric.title }}
            v-card-text(style="height:300px;position:relative;")
              Radar(:data="cdRadarChartData(metric)" :options="cdRadarOpts")
    template(v-else)
      v-row(dense)
        v-col(v-for="ds in CD_RADAR_AXIS_ORDER" :key="ds" cols="12" md="4")
          v-card(variant="outlined")
            v-card-title.text-subtitle-2.text-center.pt-3.pb-0 {{ CD_RADAR_AXIS_LABELS[ds] }}
            v-card-text(style="height:320px;position:relative;")
              Radar(:data="cdRadarChartDataByDataset(ds)" :options="cdRadarOptsByDataset")

  //- ── Summary tab ────────────────────────────────────────────────────────
  div(v-if="activeTab === 'summary'")
    .d-flex.flex-wrap.ga-4.mb-3
      div
        .text-caption.text-medium-emphasis.mb-1 Split
        v-btn-toggle(v-model="filterSplit" mandatory density="compact" variant="outlined" color="primary")
          v-btn(value="(both)" size="small") Both
          v-btn(value="dev" size="small") Dev
          v-btn(value="test" size="small") Test
    v-data-table(
      :headers="summaryHeaders"
      :items="summaryRows"
      :sort-by="[{ key: 'train_ds', order: 'asc' }]"
      :cell-props="summaryCellProps"
      :items-per-page="-1"
      density="compact" hover class="grouped-table"
    )
      template(#item.train_ds="{ item }")
        v-chip(:color="dsColor(item.train_ds)" size="small" variant="tonal") {{ item.train_ds }}
      template(#item.test_ds="{ item }")
        v-chip(:color="dsColor(item.test_ds)" size="small" variant="tonal") {{ item.test_ds }}
      template(#item.split="{ item }")
        v-chip(size="x-small" variant="tonal") {{ item.split }}
      template(#item.ner_exact_f1="{ item }")
        span(:style="f1Style(item.ner_exact_f1)") {{ fmt(item.ner_exact_f1) }}
        span.text-caption.text-medium-emphasis(v-if="showStd && item.ner_exact_f1_std != null") &nbsp;±{{ item.ner_exact_f1_std }}
      template(#item.ner_partial_f1="{ item }")
        span(:style="f1Style(item.ner_partial_f1)") {{ fmt(item.ner_partial_f1) }}
        span.text-caption.text-medium-emphasis(v-if="showStd && item.ner_partial_f1_std != null") &nbsp;±{{ item.ner_partial_f1_std }}
      template(#item.re_relaxed_f1="{ item }")
        span(:style="f1Style(item.re_relaxed_f1)") {{ fmt(item.re_relaxed_f1) }}
        span.text-caption.text-medium-emphasis(v-if="showStd && item.re_relaxed_f1_std != null") &nbsp;±{{ item.re_relaxed_f1_std }}
      template(#item.re_relaxed_partial_f1="{ item }")
        span(:style="f1Style(item.re_relaxed_partial_f1)") {{ fmt(item.re_relaxed_partial_f1) }}
        span.text-caption.text-medium-emphasis(v-if="showStd && item.re_relaxed_partial_f1_std != null") &nbsp;±{{ item.re_relaxed_partial_f1_std }}
      template(#item.re_strict_f1="{ item }")
        span(:style="f1Style(item.re_strict_f1)") {{ fmt(item.re_strict_f1) }}
        span.text-caption.text-medium-emphasis(v-if="showStd && item.re_strict_f1_std != null") &nbsp;±{{ item.re_strict_f1_std }}
      template(#item.re_strict_partial_f1="{ item }")
        span(:style="f1Style(item.re_strict_partial_f1)") {{ fmt(item.re_strict_partial_f1) }}
        span.text-caption.text-medium-emphasis(v-if="showStd && item.re_strict_partial_f1_std != null") &nbsp;±{{ item.re_strict_partial_f1_std }}
      template(#bottom)

  //- ── Entity label-wise tab ───────────────────────────────────────────────
  div(v-if="activeTab === 'entities'")
    .d-flex.flex-wrap.ga-4.mb-3
      div
        .text-caption.text-medium-emphasis.mb-1 Train
        v-btn-toggle(v-model="filterTrainDs" mandatory density="compact" variant="outlined" color="primary")
          v-btn(value="(all)" size="small") All
          v-btn(v-for="ds in TRAIN_DS" :key="ds" :value="ds" size="small") {{ ds }}
      div
        .text-caption.text-medium-emphasis.mb-1 Test
        v-btn-toggle(v-model="filterTestDs" mandatory density="compact" variant="outlined" color="primary")
          v-btn(value="(all)" size="small") All
          v-btn(v-for="ds in DS" :key="ds" :value="ds" size="small") {{ ds }}
      div
        .text-caption.text-medium-emphasis.mb-1 Split
        v-btn-toggle(v-model="filterSplitLabel" mandatory density="compact" variant="outlined" color="primary")
          v-btn(value="(both)" size="small") Both
          v-btn(value="dev" size="small") Dev
          v-btn(value="test" size="small") Test
      div
        .text-caption.text-medium-emphasis.mb-1 Match
        v-btn-toggle(v-model="filterNerMatch" mandatory density="compact" variant="outlined" color="primary")
          v-btn(value="exact" size="small") Exact
          v-btn(value="partial" size="small") Partial
          v-btn(value="(both)" size="small") Both
    v-data-table(
      :headers="labelHeaders"
      :items="entityLabelRows"
      :sort-by="[{ key: 'f1', order: 'desc' }]"
      :cell-props="labelCellProps"
      :items-per-page="-1"
      density="compact" hover
    )
      template(#item.train_ds="{ item }")
        v-chip(:color="dsColor(item.train_ds)" size="small" variant="tonal") {{ item.train_ds }}
      template(#item.test_ds="{ item }")
        v-chip(:color="dsColor(item.test_ds)" size="small" variant="tonal") {{ item.test_ds }}
      template(#item.split="{ item }")
        v-chip(size="x-small" variant="tonal") {{ item.split }}
      template(#item.match="{ item }")
        span.text-caption.text-medium-emphasis {{ item.match }}
      template(#item.precision="{ item }")
        span(:style="pStyle(item.precision)") {{ item.precision.toFixed(1) }}
      template(#item.recall="{ item }")
        span(:style="rStyle(item.recall)") {{ item.recall.toFixed(1) }}
      template(#item.f1="{ item }")
        span(:style="f1Style(item.f1)") {{ item.f1.toFixed(1) }}
      template(#body.append)
        tr(
          v-for="row in entityAggRows"
          :key="`${row.train_ds}|${row.test_ds}|${row.split}|${row.match}|${row.label}`"
          style="border-top:2px solid rgba(0,0,0,0.15);background:rgba(0,0,0,0.03);font-weight:600;"
        )
          td
            v-chip(:color="dsColor(row.train_ds)" size="small" variant="tonal") {{ row.train_ds }}
          td
            v-chip(:color="dsColor(row.test_ds)" size="small" variant="tonal") {{ row.test_ds }}
          td
            v-chip(size="x-small" variant="tonal") {{ row.split }}
          td
            span.text-caption.text-medium-emphasis {{ row.match }}
          td {{ row.label }}
          td.text-end(:style="`background:${BG_P};${pStyle(row.precision)}`") {{ row.precision.toFixed(1) }}
          td.text-end(:style="`background:${BG_R};${rStyle(row.recall)}`") {{ row.recall.toFixed(1) }}
          td.text-end(:style="`background:${BG_F1};`") #[span(:style="f1Style(row.f1)") {{ row.f1.toFixed(1) }}]
      template(#bottom)

  //- ── Relation label-wise tab ─────────────────────────────────────────────
  div(v-if="activeTab === 'relations'")
    .d-flex.flex-wrap.ga-4.mb-3
      div
        .text-caption.text-medium-emphasis.mb-1 Train
        v-btn-toggle(v-model="filterTrainDs" mandatory density="compact" variant="outlined" color="primary")
          v-btn(value="(all)" size="small") All
          v-btn(v-for="ds in TRAIN_DS" :key="ds" :value="ds" size="small") {{ ds }}
      div
        .text-caption.text-medium-emphasis.mb-1 Test
        v-btn-toggle(v-model="filterTestDs" mandatory density="compact" variant="outlined" color="primary")
          v-btn(value="(all)" size="small") All
          v-btn(v-for="ds in DS" :key="ds" :value="ds" size="small") {{ ds }}
      div
        .text-caption.text-medium-emphasis.mb-1 Split
        v-btn-toggle(v-model="filterSplitLabel" mandatory density="compact" variant="outlined" color="primary")
          v-btn(value="(both)" size="small") Both
          v-btn(value="dev" size="small") Dev
          v-btn(value="test" size="small") Test
      div
        .text-caption.text-medium-emphasis.mb-1 RE metric
        v-btn-toggle(v-model="filterReMatch" mandatory density="compact" variant="outlined" color="primary")
          v-btn(value="relaxed" size="small") RE
          v-btn(value="relaxed_partial" size="small") RE≈
          v-btn(value="strict" size="small") RE+
          v-btn(value="strict_partial" size="small") RE+≈
          v-btn(value="(both)" size="small") All
    v-data-table(
      :headers="labelHeaders"
      :items="relationLabelRows"
      :sort-by="[{ key: 'f1', order: 'desc' }]"
      :cell-props="labelCellProps"
      :items-per-page="-1"
      density="compact" hover
    )
      template(#item.train_ds="{ item }")
        v-chip(:color="dsColor(item.train_ds)" size="small" variant="tonal") {{ item.train_ds }}
      template(#item.test_ds="{ item }")
        v-chip(:color="dsColor(item.test_ds)" size="small" variant="tonal") {{ item.test_ds }}
      template(#item.split="{ item }")
        v-chip(size="x-small" variant="tonal") {{ item.split }}
      template(#item.match="{ item }")
        span.text-caption.text-medium-emphasis {{ item.match }}
      template(#item.precision="{ item }")
        span(:style="pStyle(item.precision)") {{ item.precision.toFixed(1) }}
      template(#item.recall="{ item }")
        span(:style="rStyle(item.recall)") {{ item.recall.toFixed(1) }}
      template(#item.f1="{ item }")
        span(:style="f1Style(item.f1)") {{ item.f1.toFixed(1) }}
      template(#body.append)
        tr(
          v-for="row in relationAggRows"
          :key="`${row.train_ds}|${row.test_ds}|${row.split}|${row.match}|${row.label}`"
          style="border-top:2px solid rgba(0,0,0,0.15);background:rgba(0,0,0,0.03);font-weight:600;"
        )
          td
            v-chip(:color="dsColor(row.train_ds)" size="small" variant="tonal") {{ row.train_ds }}
          td
            v-chip(:color="dsColor(row.test_ds)" size="small" variant="tonal") {{ row.test_ds }}
          td
            v-chip(size="x-small" variant="tonal") {{ row.split }}
          td
            span.text-caption.text-medium-emphasis {{ row.match }}
          td {{ row.label }}
          td.text-end(:style="`background:${BG_P};${pStyle(row.precision)}`") {{ row.precision.toFixed(1) }}
          td.text-end(:style="`background:${BG_R};${rStyle(row.recall)}`") {{ row.recall.toFixed(1) }}
          td.text-end(:style="`background:${BG_F1};`") #[span(:style="f1Style(row.f1)") {{ row.f1.toFixed(1) }}]
      template(#bottom)

  //- ── MultiSciERE Generalization tab ─────────────────────────────────────
  div(v-if="activeTab === 'multi-sciere-generalization'")
    .d-flex.flex-wrap.ga-4.mb-3
      div
        .text-caption.text-medium-emphasis.mb-1 Dataset
        v-btn-toggle(v-model="filterGenDs" mandatory density="compact" variant="outlined" color="primary")
          v-btn(v-for="ds in DS" :key="ds" :value="ds" size="small") {{ ds }}
    p.text-caption.text-medium-emphasis.mb-3 Unified label set · test split · comparing {{ filterGenDs }}-trained model vs multi-sciere ({{ filterGenDs }} label space)
    v-data-table(
      :headers="generalizationHeaders"
      :items="generalizationRows"
      :sort-by="[{ key: 'train_ds', order: 'asc' }]"
      :cell-props="summaryCellProps"
      :items-per-page="-1"
      density="compact" hover class="grouped-table"
    )
      template(#item.train_ds="{ item }")
        v-chip(:color="dsColor(item.train_ds)" size="small" variant="tonal") {{ item.train_ds }}
      template(#item.test_ds="{ item }")
        v-chip(:color="dsColor(item.test_ds)" size="small" variant="tonal") {{ item.test_ds }}
      template(#item.ner_exact_f1="{ item }")
        span(:style="f1Style(item.ner_exact_f1)") {{ fmt(item.ner_exact_f1) }}
      template(#item.ner_partial_f1="{ item }")
        span(:style="f1Style(item.ner_partial_f1)") {{ fmt(item.ner_partial_f1) }}
      template(#item.re_relaxed_f1="{ item }")
        span(:style="f1Style(item.re_relaxed_f1)") {{ fmt(item.re_relaxed_f1) }}
      template(#item.re_relaxed_partial_f1="{ item }")
        span(:style="f1Style(item.re_relaxed_partial_f1)") {{ fmt(item.re_relaxed_partial_f1) }}
      template(#item.re_strict_f1="{ item }")
        span(:style="f1Style(item.re_strict_f1)") {{ fmt(item.re_strict_f1) }}
      template(#item.re_strict_partial_f1="{ item }")
        span(:style="f1Style(item.re_strict_partial_f1)") {{ fmt(item.re_strict_partial_f1) }}
      template(#bottom)

    h3.text-subtitle-1.font-weight-bold.mt-6.mb-2 MultiSciERE Label Set Comparison
    .d-flex.flex-wrap.ga-4.mb-3
      div
        .text-caption.text-medium-emphasis.mb-1 Test dataset
        v-btn-toggle(v-model="filterGenTestDs" mandatory density="compact" variant="outlined" color="primary")
          v-btn(v-for="ds in DS" :key="ds" :value="ds" size="small") {{ ds }}
    p.text-caption.text-medium-emphasis.mb-3 Unified label set · test split · all three multi-sciere label spaces on {{ filterGenTestDs }}
    v-data-table(
      :headers="generalizationHeaders"
      :items="labelSetComparisonRows"
      :sort-by="[{ key: 'train_ds', order: 'asc' }]"
      :cell-props="summaryCellProps"
      :items-per-page="-1"
      density="compact" hover class="grouped-table"
    )
      template(#item.train_ds="{ item }")
        v-chip(:color="dsColor(item.train_ds)" size="small" variant="tonal") {{ item.train_ds }}
      template(#item.test_ds="{ item }")
        v-chip(:color="dsColor(item.test_ds)" size="small" variant="tonal") {{ item.test_ds }}
      template(#item.ner_exact_f1="{ item }")
        span(:style="f1Style(item.ner_exact_f1)") {{ fmt(item.ner_exact_f1) }}
      template(#item.ner_partial_f1="{ item }")
        span(:style="f1Style(item.ner_partial_f1)") {{ fmt(item.ner_partial_f1) }}
      template(#item.re_relaxed_f1="{ item }")
        span(:style="f1Style(item.re_relaxed_f1)") {{ fmt(item.re_relaxed_f1) }}
      template(#item.re_relaxed_partial_f1="{ item }")
        span(:style="f1Style(item.re_relaxed_partial_f1)") {{ fmt(item.re_relaxed_partial_f1) }}
      template(#item.re_strict_f1="{ item }")
        span(:style="f1Style(item.re_strict_f1)") {{ fmt(item.re_strict_f1) }}
      template(#item.re_strict_partial_f1="{ item }")
        span(:style="f1Style(item.re_strict_partial_f1)") {{ fmt(item.re_strict_partial_f1) }}
      template(#bottom)

  v-snackbar(v-model="snack.show" :color="snack.color" timeout="4000") {{ snack.message }}
</template>

<script setup>
import { ref, computed } from 'vue'
import { useDockerMode } from '../composables/useDockerMode.js'
import {
    Chart as ChartJS,
    RadarController, RadialLinearScale,
    PointElement, LineElement, Filler,
    Tooltip as ChartTooltip, Legend as ChartLegend,
} from 'chart.js'
import { Radar } from 'vue-chartjs'

ChartJS.register(RadarController, RadialLinearScale, PointElement, LineElement, Filler, ChartTooltip, ChartLegend)

const DS = ['gsap-ere', 'scier', 'scinlp']
const TRAIN_DS = [...DS, 'unified-sciere']
const DS_COLORS = { 'gsap-ere': 'blue', 'scier': 'green', 'scinlp': 'orange', 'unified-sciere': 'purple', 'multi-sciere-gsap': 'deep-orange', 'multi-sciere-scier': 'deep-orange', 'multi-sciere-scinlp': 'deep-orange' }
const DATASET_TO_PRED_LS = { 'gsap-ere': 'gsap', 'scier': 'scier', 'scinlp': 'scinlp' }
function dsColor(ds) { return DS_COLORS[ds] ?? 'grey' }

// ── Radar constants ───────────────────────────────────────────────────────────
const CD_RADAR_AXIS_ORDER  = ['scier', 'scinlp', 'gsap-ere']
const CD_RADAR_AXIS_LABELS = { 'gsap-ere': 'GSAP-ERE', scier: 'SciER', scinlp: 'SciNLP' }
const CD_RADAR_METRICS = [
    { id: 'ner',   key: 'ner_exact_f1',          title: 'NER'   },
    { id: 'ner_p', key: 'ner_partial_f1',         title: 'NER≈'  },
    { id: 're',    key: 're_relaxed_f1',          title: 'RE'    },
    { id: 'rep_p', key: 're_strict_partial_f1',   title: 'RE+≈'  },
    { id: 'rep',   key: 're_strict_f1',           title: 'RE+'   },
]
const CD_RADAR_BY_DATASET_ORDER      = ['ner', 'ner_p', 'rep_p', 're', 'rep']
const CD_RADAR_BY_DATASET_START_ANGLE = -126 * Math.PI / 180
const CD_TRAIN_DEFS = [
    { id: 'gsap-ere',       label: 'GSAP-ERE',      rgb: '25,118,210'  },
    { id: 'scier',          label: 'SciER',          rgb: '56,142,60'   },
    { id: 'scinlp',         label: 'SciNLP',         rgb: '245,124,0'   },
    { id: 'unified-sciere', label: 'UnifiedSciERE',  rgb: '123,31,162'  },
]

const cdRadarGroupBy = ref('dataset')
const cdRadarMetrics = ref(['ner', 'ner_p', 're', 'rep_p', 'rep'])
const cdRadarSplit   = ref('test')

const cdRadarActiveMetrics = computed(() =>
    CD_RADAR_METRICS.filter(m => cdRadarMetrics.value.includes(m.id))
)
const cdRadarHasData = computed(() => allSummary.value.length > 0)

function getCdEntry(trainDs, testDs) {
    return allSummary.value.find(
        r => r.train_ds === trainDs && r.test_ds === testDs && r.split === cdRadarSplit.value
    ) ?? null
}

function cdRadarChartData(metric) {
    const labels = CD_RADAR_AXIS_ORDER.map(ds => CD_RADAR_AXIS_LABELS[ds])
    const refDataset = {
        label: 'Baseline',
        data: [0, 0, 0],
        borderColor: 'rgba(0,0,0,0.3)',
        backgroundColor: 'transparent',
        borderWidth: 1.5,
        borderDash: [4, 4],
        pointRadius: 2,
        pointBackgroundColor: 'rgba(0,0,0,0.3)',
        spanGaps: true,
    }
    const seriesDatasets = CD_TRAIN_DEFS.flatMap(train => {
        const data = CD_RADAR_AXIS_ORDER.map(testDs => {
            if (train.id === testDs) return null
            const ce = getCdEntry(train.id, testDs)
            const be = getCdEntry(testDs, testDs)
            if (!ce || !be) return null
            const cf = ce[metric.key], bf = be[metric.key]
            if (cf == null || bf == null) return null
            return +(cf - bf).toFixed(2)
        })
        if (data.every(d => d === null)) return []
        return [{
            label: train.label,
            data,
            borderColor: `rgb(${train.rgb})`,
            backgroundColor: `rgba(${train.rgb},0.12)`,
            pointBackgroundColor: `rgb(${train.rgb})`,
            pointBorderColor: '#fff',
            pointRadius: 4,
            borderWidth: 2,
            spanGaps: false,
        }]
    })
    return { labels, datasets: [refDataset, ...seriesDatasets] }
}

function cdRadarChartDataByDataset(testDs) {
    const activeIds = new Set(cdRadarMetrics.value)
    const axisMetrics = CD_RADAR_METRICS
        .filter(m => activeIds.has(m.id))
        .sort((a, b) => CD_RADAR_BY_DATASET_ORDER.indexOf(a.id) - CD_RADAR_BY_DATASET_ORDER.indexOf(b.id))

    const baseEntry = getCdEntry(testDs, testDs)
    const labels = axisMetrics.map(m => {
        if (!baseEntry) return m.title
        const bf = baseEntry[m.key]
        return bf != null ? [m.title, `(F1 ${bf.toFixed(1)})`] : m.title
    })

    const refDataset = {
        label: 'Baseline',
        data: axisMetrics.map(() => 0),
        borderColor: 'rgba(0,0,0,0.3)',
        backgroundColor: 'transparent',
        borderWidth: 1.5,
        borderDash: [4, 4],
        pointRadius: 2,
        pointBackgroundColor: 'rgba(0,0,0,0.3)',
        spanGaps: true,
    }
    const seriesDatasets = CD_TRAIN_DEFS.flatMap(train => {
        if (train.id === testDs) return []
        const ce = getCdEntry(train.id, testDs)
        if (!ce) return []
        const data = axisMetrics.map(m => {
            if (!baseEntry) return null
            const cf = ce[m.key], bf = baseEntry[m.key]
            if (cf == null || bf == null) return null
            return +(cf - bf).toFixed(2)
        })
        return [{
            label: train.label,
            data,
            borderColor: `rgb(${train.rgb})`,
            backgroundColor: `rgba(${train.rgb},0.12)`,
            pointBackgroundColor: `rgb(${train.rgb})`,
            pointBorderColor: '#fff',
            pointRadius: 4,
            borderWidth: 2,
            spanGaps: false,
        }]
    })
    return { labels, datasets: [refDataset, ...seriesDatasets] }
}

const cdRadarOpts = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
        r: {
            suggestedMin: -20,
            suggestedMax: 10,
            ticks: { stepSize: 5, font: { size: 9 }, callback: v => (v > 0 ? '+' : '') + v },
            grid: { color: 'rgba(0,0,0,0.1)' },
            angleLines: { color: 'rgba(0,0,0,0.18)' },
            pointLabels: { font: { size: 12, weight: '500' } },
        },
    },
    plugins: {
        legend: { position: 'bottom', labels: { boxWidth: 10, padding: 8, font: { size: 11 } } },
        tooltip: { callbacks: { label: ctx => ` ${ctx.dataset.label}: ${ctx.raw != null ? (ctx.raw >= 0 ? '+' : '') + ctx.raw.toFixed(1) : 'n/a'}` } },
    },
}

const cdRadarOptsByDataset = {
    responsive: true,
    maintainAspectRatio: false,
    startAngle: CD_RADAR_BY_DATASET_START_ANGLE,
    scales: {
        r: {
            suggestedMin: -20,
            suggestedMax: 10,
            ticks: { stepSize: 5, font: { size: 9 }, callback: v => (v > 0 ? '+' : '') + v },
            grid: { color: 'rgba(0,0,0,0.1)' },
            angleLines: { color: 'rgba(0,0,0,0.18)' },
            pointLabels: { font: { size: 11, weight: '500' } },
        },
    },
    plugins: {
        legend: { position: 'bottom', labels: { boxWidth: 10, padding: 8, font: { size: 11 } } },
        tooltip: { callbacks: { label: ctx => ` ${ctx.dataset.label}: ${ctx.raw != null ? (ctx.raw >= 0 ? '+' : '') + ctx.raw.toFixed(1) : 'n/a'}` } },
    },
}

const { dockerMode } = useDockerMode()
const building         = ref(false)
const generatedAt      = ref(null)
const showStd          = ref(true)
const allSummary       = ref([])
const allEntities      = ref([])
const allRelations     = ref([])
const multiSciereSummary = ref([])
const snack            = ref({ show: false, message: '', color: 'success' })
const activeTab        = ref('radar')

const filterGenDs      = ref('scinlp')
const filterSplit      = ref('test')
const filterSplitLabel = ref('test')
const filterTrainDs    = ref('(all)')
const filterTestDs     = ref('(all)')
const filterNerMatch   = ref('partial')
const filterReMatch    = ref('relaxed')

// ── colors ────────────────────────────────────────────────────────────────────
const C_P  = '#1565c0'
const C_R  = '#c62828'
const C_F1 = '#2e7d32'
const BG_P  = 'rgba(21,101,192,0.07)'
const BG_R  = 'rgba(198,40,40,0.07)'
const BG_F1 = 'rgba(46,125,50,0.07)'

function pStyle(v) {
  if (v == null) return 'color:#9e9e9e;'
  const t = Math.max(0, Math.min(1, v / 100))
  return `color:rgb(${Math.round(180-t*159)},${Math.round(210-t*109)},${Math.round(245-t*53)});font-weight:600;`
}
function rStyle(v) {
  if (v == null) return 'color:#9e9e9e;'
  const t = Math.max(0, Math.min(1, v / 100))
  return `color:rgb(${Math.round(245-t*47)},${Math.round(180-t*140)},${Math.round(180-t*140)});font-weight:600;`
}
function f1Style(v) {
  if (v == null) return 'color:#9e9e9e;'
  const t = Math.max(0, Math.min(1, v / 100))
  return `color:rgb(${Math.round(220-t*150)},${Math.round(100+t*100)},60);font-weight:600;`
}
function fmt(v) { return v != null ? v.toFixed(1) : '–' }

// ── summary table ─────────────────────────────────────────────────────────────
const summaryHeaders = computed(() => {
  const h = [
    { key: 'train_ds',      title: 'Train',  sortable: true },
    { key: 'test_ds',       title: 'Test',   sortable: true },
    ...(filterSplit.value === '(both)' ? [{ key: 'split', title: 'Split', sortable: true }] : []),
    { key: 'ner_exact_f1',          title: 'NER',      sortable: true, align: 'end' },
    { key: 'ner_partial_f1',        title: 'NER≈',     sortable: true, align: 'end' },
    { key: 're_relaxed_f1',         title: 'RE',       sortable: true, align: 'end' },
    { key: 're_relaxed_partial_f1', title: 'RE≈',      sortable: true, align: 'end' },
    { key: 're_strict_f1',          title: 'RE+',      sortable: true, align: 'end' },
    { key: 're_strict_partial_f1',  title: 'RE+≈',     sortable: true, align: 'end' },
  ]
  return h
})

const F1_KEYS = new Set(['ner_exact_f1','ner_partial_f1','re_relaxed_f1','re_relaxed_partial_f1','re_strict_f1','re_strict_partial_f1'])
function summaryCellProps({ column }) {
  if (F1_KEYS.has(column?.key)) return { style: `background:${BG_F1};` }
  return {}
}

const summaryRows = computed(() =>
  allSummary.value.filter(r => filterSplit.value === '(both)' || r.split === filterSplit.value)
)

// ── MultiSciERE Generalization tab ────────────────────────────────────────────
const generalizationHeaders = [
  { key: 'train_ds',             title: 'Train',  sortable: true },
  { key: 'test_ds',              title: 'Test',   sortable: true },
  { key: 'ner_exact_f1',         title: 'NER',    sortable: true, align: 'end' },
  { key: 'ner_partial_f1',       title: 'NER≈',   sortable: true, align: 'end' },
  { key: 're_relaxed_f1',        title: 'RE',     sortable: true, align: 'end' },
  { key: 're_relaxed_partial_f1',title: 'RE≈',    sortable: true, align: 'end' },
  { key: 're_strict_f1',         title: 'RE+',    sortable: true, align: 'end' },
  { key: 're_strict_partial_f1', title: 'RE+≈',   sortable: true, align: 'end' },
]

const generalizationRows = computed(() => {
  const ds        = filterGenDs.value
  const predLs    = DATASET_TO_PRED_LS[ds]
  const multiName = `multi-sciere-${predLs}`

  const baseRows = allSummary.value
    .filter(r => r.train_ds === ds && r.split === 'test')

  const multiRows = multiSciereSummary.value
    .filter(r => r.label_set === 'unified' && r.trained_on === multiName)
    .map(r => ({
      train_ds:              multiName,
      test_ds:               r.dataset,
      ner_exact_f1:          r.ner_exact_f1,
      ner_partial_f1:        r.ner_partial_f1,
      re_relaxed_f1:         r.re_relaxed_f1,
      re_relaxed_partial_f1: r.re_relaxed_partial_f1,
      re_strict_f1:          r.re_strict_f1,
      re_strict_partial_f1:  r.re_strict_partial_f1,
    }))

  return [...baseRows, ...multiRows]
})

const filterGenTestDs = ref('gsap-ere')

const labelSetComparisonRows = computed(() =>
  multiSciereSummary.value
    .filter(r => r.label_set === 'unified' && r.dataset === filterGenTestDs.value)
    .map(r => ({
      train_ds:              r.trained_on,
      test_ds:               r.dataset,
      ner_exact_f1:          r.ner_exact_f1,
      ner_partial_f1:        r.ner_partial_f1,
      re_relaxed_f1:         r.re_relaxed_f1,
      re_relaxed_partial_f1: r.re_relaxed_partial_f1,
      re_strict_f1:          r.re_strict_f1,
      re_strict_partial_f1:  r.re_strict_partial_f1,
    }))
)

// ── label tables ──────────────────────────────────────────────────────────────
const labelHeaders = [
  { title: 'Train',  key: 'train_ds', sortable: true },
  { title: 'Test',   key: 'test_ds',  sortable: true },
  { title: 'Split',  key: 'split',    sortable: true },
  { title: 'Match',  key: 'match',    sortable: true },
  { title: 'Label',  key: 'label',    sortable: true },
  { title: 'P',      key: 'precision',sortable: true, align: 'end' },
  { title: 'R',      key: 'recall',   sortable: true, align: 'end' },
  { title: 'F1',     key: 'f1',       sortable: true, align: 'end' },
]

function labelCellProps({ column }) {
  if (column?.key === 'precision') return { style: `background:${BG_P};` }
  if (column?.key === 'recall')    return { style: `background:${BG_R};` }
  if (column?.key === 'f1')        return { style: `background:${BG_F1};` }
  return {}
}

const AGGREGATE_LABELS = new Set(['micro', 'macro', 'weighted'])

function filterEntity(r) {
  if (filterTrainDs.value    !== '(all)' && r.train_ds !== filterTrainDs.value)  return false
  if (filterTestDs.value     !== '(all)' && r.test_ds  !== filterTestDs.value)   return false
  if (filterSplitLabel.value !== '(both)' && r.split   !== filterSplitLabel.value) return false
  if (filterNerMatch.value   !== '(both)' && r.match   !== filterNerMatch.value)  return false
  return true
}
function filterRelation(r) {
  if (filterTrainDs.value    !== '(all)' && r.train_ds !== filterTrainDs.value)  return false
  if (filterTestDs.value     !== '(all)' && r.test_ds  !== filterTestDs.value)   return false
  if (filterSplitLabel.value !== '(both)' && r.split   !== filterSplitLabel.value) return false
  if (filterReMatch.value    !== '(both)' && r.match   !== filterReMatch.value)   return false
  return true
}

const entityLabelRows   = computed(() => allEntities.value.filter(r =>  filterEntity(r)   && !AGGREGATE_LABELS.has(r.label)))
const entityAggRows     = computed(() => allEntities.value.filter(r =>  filterEntity(r)   &&  AGGREGATE_LABELS.has(r.label)))
const relationLabelRows = computed(() => allRelations.value.filter(r => filterRelation(r) && !AGGREGATE_LABELS.has(r.label)))
const relationAggRows   = computed(() => allRelations.value.filter(r => filterRelation(r) &&  AGGREGATE_LABELS.has(r.label)))

// ── fetch / rebuild ───────────────────────────────────────────────────────────
async function fetchData() {
  try {
    const [cdRes, msRes] = await Promise.all([
      fetch('/api/cross-dataset'),
      fetch('/api/multi-sciere'),
    ])
    if (!cdRes.ok) { snack.value = { show: true, message: 'No cross-dataset data yet — click Rebuild.', color: 'warning' }; return }
    const data = await cdRes.json()
    generatedAt.value  = data.generated_at ? new Date(data.generated_at).toLocaleString() : null
    allSummary.value   = data.summary         ?? []
    allEntities.value  = data.entity_labels   ?? []
    allRelations.value = data.relation_labels ?? []
    if (msRes.ok) {
      const msData = await msRes.json()
      multiSciereSummary.value = msData.summary ?? []
    }
  } catch (e) {
    snack.value = { show: true, message: `Failed to load: ${e.message}`, color: 'error' }
  }
}

async function rebuild() {
  building.value = true
  try {
    const res  = await fetch('/api/cross-dataset/build', { method: 'POST' })
    const data = await res.json()
    if (data.ok) { snack.value = { show: true, message: 'Rebuilt successfully.', color: 'success' }; await fetchData() }
    else snack.value = { show: true, message: `Failed: ${data.stderr?.slice(0, 200)}`, color: 'error' }
  } catch (e) {
    snack.value = { show: true, message: `Error: ${e.message}`, color: 'error' }
  } finally {
    building.value = false
  }
}

fetchData()
</script>
