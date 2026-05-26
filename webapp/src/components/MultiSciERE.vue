<template lang="pug">
v-container(fluid)
  .d-flex.align-center.mb-3
    h2.text-h5 MultiSciERE Results
    v-chip.ml-3(v-if="generatedAt" size="small" variant="tonal" color="grey") {{ generatedAt }}
    v-spacer
    v-btn(v-if="!dockerMode" variant="text" prepend-icon="mdi-refresh" size="small" :loading="building" @click="rebuild") Rebuild

  v-tabs(v-model="activeTab" density="compact" color="primary" class="mb-4")
    v-tab(value="radar") Radar Charts
    v-tab(value="seeded") Summary
    v-tab(value="entities") Entities
    v-tab(value="relations") Relations

  //- ── Summary tab ─────────────────────────────────────────────────────────
  div(v-if="activeTab === 'seeded'")
    .d-flex.flex-wrap.ga-4.mb-3
      div
        .text-caption.text-medium-emphasis.mb-1 Metrics
        v-btn-toggle(v-model="seededMetrics" multiple density="compact" variant="outlined" color="primary")
          v-btn(value="ner" size="small") NER
          v-btn(value="ner_partial" size="small") NER≈
          v-btn(value="re" size="small") RE
          v-btn(value="re_partial" size="small") RE≈
          v-btn(value="rep" size="small") RE+
          v-btn(value="rep_partial" size="small") RE+≈
      div
        .text-caption.text-medium-emphasis.mb-1 Options
        .d-flex(style="gap:8px;")
          v-btn-toggle(v-model="seededDelta" multiple density="compact" variant="outlined" color="secondary")
            v-btn(value="delta" size="small") Δ delta
          v-btn-toggle(v-model="seededStd" multiple density="compact" variant="outlined" color="teal")
            v-btn(value="std" size="small") ± std
      div
        .text-caption.text-medium-emphasis.mb-1 Test set
        v-btn-toggle(v-model="seededDatasets" multiple density="compact" variant="outlined" color="primary")
          v-btn(value="gsap-ere" size="small") GSAP-ERE
          v-btn(value="scier" size="small") SciER
          v-btn(value="scinlp" size="small") SciNLP
      div
        .text-caption.text-medium-emphasis.mb-1 Label space
        v-btn-toggle(v-model="seededLabelSet" mandatory density="compact" variant="outlined" color="secondary")
          v-btn(value="original" size="small") Original
          v-btn(value="unified" size="small") Unified
      div(v-if="seededDatasets.includes('scier') && seededDatasets.length === 1")
        .text-caption.text-medium-emphasis.mb-1 Split
        v-btn-toggle(v-model="seededSplit" mandatory density="compact" variant="outlined" color="teal")
          v-btn(value="test" size="small") Test
          v-btn(value="test_ood" size="small") OOD

    div(v-if="seededRows.length === 0" class="text-medium-emphasis text-body-2 pa-4") No seeded model data — run the report script first.
    v-data-table(
      v-else
      :headers="seededHeaders"
      :items="seededAllRows"
      :items-per-page="-1"
      density="compact" hover
      :cell-props="seededCellProps"
      :row-props="seededRowProps"
    )
      template(#bottom)
      template(#item.trained_on="{ item }")
        span(:class="item.is_baseline ? 'font-weight-bold' : ''") {{ item.trained_on_label }}
      template(#item.test_dataset="{ item }")
        v-chip(:color="datasetColor(item.test_dataset)" size="small" variant="tonal") {{ item.test_dataset }}
      template(#item.ner_f1="{ item }")
        span(:style="f1Style(item.ner_f1)") {{ item.ner_f1 != null ? item.ner_f1.toFixed(1) : '–' }}
        span.text-caption.text-medium-emphasis.ml-1(v-if="showStdSeeded && item.ner_std != null") ±{{ item.ner_std.toFixed(1) }}
      template(#item.ner_delta="{ item }")
        span(v-if="item.ner_delta != null" :class="item.ner_delta >= 0 ? 'text-success font-weight-medium' : 'text-error font-weight-medium'")
          | {{ item.ner_delta >= 0 ? '+' : '' }}{{ item.ner_delta.toFixed(1) }}
        span(v-else class="text-disabled") –
      template(#item.ner_p_f1="{ item }")
        span(:style="f1Style(item.ner_p_f1)") {{ item.ner_p_f1 != null ? item.ner_p_f1.toFixed(1) : '–' }}
        span.text-caption.text-medium-emphasis.ml-1(v-if="showStdSeeded && item.ner_p_std != null") ±{{ item.ner_p_std.toFixed(1) }}
      template(#item.ner_p_delta="{ item }")
        span(v-if="item.ner_p_delta != null" :class="item.ner_p_delta >= 0 ? 'text-success font-weight-medium' : 'text-error font-weight-medium'")
          | {{ item.ner_p_delta >= 0 ? '+' : '' }}{{ item.ner_p_delta.toFixed(1) }}
        span(v-else class="text-disabled") –
      template(#item.re_f1="{ item }")
        span(:style="f1Style(item.re_f1)") {{ item.re_f1 != null ? item.re_f1.toFixed(1) : '–' }}
        span.text-caption.text-medium-emphasis.ml-1(v-if="showStdSeeded && item.re_std != null") ±{{ item.re_std.toFixed(1) }}
      template(#item.re_delta="{ item }")
        span(v-if="item.re_delta != null" :class="item.re_delta >= 0 ? 'text-success font-weight-medium' : 'text-error font-weight-medium'")
          | {{ item.re_delta >= 0 ? '+' : '' }}{{ item.re_delta.toFixed(1) }}
        span(v-else class="text-disabled") –
      template(#item.re_p_f1="{ item }")
        span(:style="f1Style(item.re_p_f1)") {{ item.re_p_f1 != null ? item.re_p_f1.toFixed(1) : '–' }}
        span.text-caption.text-medium-emphasis.ml-1(v-if="showStdSeeded && item.re_p_std != null") ±{{ item.re_p_std.toFixed(1) }}
      template(#item.re_p_delta="{ item }")
        span(v-if="item.re_p_delta != null" :class="item.re_p_delta >= 0 ? 'text-success font-weight-medium' : 'text-error font-weight-medium'")
          | {{ item.re_p_delta >= 0 ? '+' : '' }}{{ item.re_p_delta.toFixed(1) }}
        span(v-else class="text-disabled") –
      template(#item.rep_f1="{ item }")
        span(:style="f1Style(item.rep_f1)") {{ item.rep_f1 != null ? item.rep_f1.toFixed(1) : '–' }}
        span.text-caption.text-medium-emphasis.ml-1(v-if="showStdSeeded && item.rep_std != null") ±{{ item.rep_std.toFixed(1) }}
      template(#item.rep_delta="{ item }")
        span(v-if="item.rep_delta != null" :class="item.rep_delta >= 0 ? 'text-success font-weight-medium' : 'text-error font-weight-medium'")
          | {{ item.rep_delta >= 0 ? '+' : '' }}{{ item.rep_delta.toFixed(1) }}
        span(v-else class="text-disabled") –
      template(#item.rep_p_f1="{ item }")
        span(:style="f1Style(item.rep_p_f1)") {{ item.rep_p_f1 != null ? item.rep_p_f1.toFixed(1) : '–' }}
        span.text-caption.text-medium-emphasis.ml-1(v-if="showStdSeeded && item.rep_p_std != null") ±{{ item.rep_p_std.toFixed(1) }}
      template(#item.rep_p_delta="{ item }")
        span(v-if="item.rep_p_delta != null" :class="item.rep_p_delta >= 0 ? 'text-success font-weight-medium' : 'text-error font-weight-medium'")
          | {{ item.rep_p_delta >= 0 ? '+' : '' }}{{ item.rep_p_delta.toFixed(1) }}
        span(v-else class="text-disabled") –

  //- ── Radar Charts tab ────────────────────────────────────────────────────
  div(v-if="activeTab === 'radar'")
    .d-flex.flex-wrap.ga-4.mb-3
      div
        .text-caption.text-medium-emphasis.mb-1 Metrics
        v-btn-toggle(v-model="radarMetrics" multiple density="compact" variant="outlined" color="primary")
          v-btn(value="ner" size="small") NER
          v-btn(value="ner_p" size="small") NER≈
          v-btn(value="re" size="small") RE
          v-btn(value="rep_p" size="small") RE+≈
          v-btn(value="rep" size="small") RE+
      div
        .text-caption.text-medium-emphasis.mb-1 Group by
        v-btn-toggle(v-model="radarGroupBy" mandatory density="compact" variant="outlined" color="secondary")
          v-btn(value="metric" size="small") Metric
          v-btn(value="dataset" size="small") Dataset
      div
        .text-caption.text-medium-emphasis.mb-1 Label space
        v-btn-toggle(v-model="seededLabelSet" mandatory density="compact" variant="outlined" color="secondary")
          v-btn(value="original" size="small") Original
          v-btn(value="unified" size="small") Unified
      div
        .text-caption.text-medium-emphasis.mb-1 Split (SciER)
        v-btn-toggle(v-model="seededSplit" mandatory density="compact" variant="outlined" color="teal")
          v-btn(value="test" size="small") Test
          v-btn(value="test_ood" size="small") OOD
    div(v-if="!radarHasData" class="text-medium-emphasis text-body-2 pa-4") No seeded model data — run the report script first.
    template(v-else-if="radarGroupBy === 'metric'")
      v-row(dense)
        v-col(v-for="metric in radarActiveMetrics" :key="metric.id" cols="12" sm="6")
          v-card(variant="outlined")
            v-card-title.text-subtitle-2.text-center.pt-3.pb-0 {{ metric.title }}
            v-card-text(style="height:300px;position:relative;")
              Radar(:data="radarChartData(metric)" :options="radarOpts")
    template(v-else)
      v-row(dense)
        v-col(v-for="ds in RADAR_AXIS_ORDER" :key="ds" cols="12" md="4")
          v-card(variant="outlined")
            v-card-title.text-subtitle-2.text-center.pt-3.pb-0 {{ RADAR_AXIS_LABELS[ds] }}
            v-card-text(style="height:320px;position:relative;")
              Radar(:data="radarChartDataByDataset(ds)" :options="radarOptsByDataset")

  //- ── Entity label-wise tab ───────────────────────────────────────────────
  div(v-if="activeTab === 'entities'")
    .d-flex.flex-wrap.ga-4.mb-3
      div
        .text-caption.text-medium-emphasis.mb-1 Test set
        v-btn-toggle(v-model="filterDataset" mandatory density="compact" variant="outlined" color="primary")
          v-btn(value="gsap-ere" size="small") GSAP-ERE
          v-btn(value="scier" size="small") SciER
          v-btn(value="scinlp" size="small") SciNLP
      div
        .text-caption.text-medium-emphasis.mb-1 Label space
        v-btn-toggle(v-model="filterLabelSet" mandatory density="compact" variant="outlined" color="secondary")
          v-btn(value="original" size="small") Original
          v-btn(value="unified" size="small") Unified
      div
        .text-caption.text-medium-emphasis.mb-1 NER metric
        v-btn-toggle(v-model="filterNerMatch" mandatory density="compact" variant="outlined" color="primary")
          v-btn(value="exact" size="small") NER
          v-btn(value="partial" size="small") NER≈
      div
        .text-caption.text-medium-emphasis.mb-1 Trained on
        v-btn-toggle(
          :model-value="activeLabelTrainedOn"
          @update:model-value="filterLabelTrainedOn = $event"
          mandatory density="compact" variant="outlined" color="primary"
        )
          v-btn(v-for="to in labelTrainedOnOptions" :key="to" :value="to" size="small") {{ displayModel(to) }}
      v-btn-toggle(v-model="showLabelDelta" multiple density="compact" variant="outlined" color="teal" style="align-self:flex-end")
        v-btn(value="delta" size="small") Δ delta
    v-data-table(
      :headers="labelEntDetailHeaders"
      :items="entityLabelRows"
      :sort-by="[{ key: 'f1', order: 'desc' }]"
      :cell-props="labelCellProps"
      :items-per-page="-1"
      density="compact" hover
    )
      template(#item.precision="{ item }")
        span(:style="pStyle(item.precision)") {{ item.precision.toFixed(1) }}
      template(#item.recall="{ item }")
        span(:style="rStyle(item.recall)") {{ item.recall.toFixed(1) }}
      template(#item.f1="{ item }")
        span(:style="f1Style(item.f1)") {{ item.f1.toFixed(1) }}
      template(#item.delta_f1="{ item }")
        span(v-if="item.delta_f1 != null" :class="item.delta_f1 >= 0 ? 'text-success font-weight-medium' : 'text-error font-weight-medium'")
          | {{ item.delta_f1 >= 0 ? '+' : '' }}{{ item.delta_f1.toFixed(1) }}
        span(v-else class="text-disabled") –
      template(#body.append)
        tr(
          v-for="row in entityAggRows" :key="`agg-ent-${row.label}`"
          style="border-top:2px solid rgba(0,0,0,0.15);background:rgba(0,0,0,0.03);font-weight:600;"
        )
          td {{ row.label }}
          td.text-end(:style="`background:${BG_P};${pStyle(row.precision)}`") {{ row.precision.toFixed(1) }}
          td.text-end(:style="`background:${BG_R};${rStyle(row.recall)}`") {{ row.recall.toFixed(1) }}
          td.text-end(:style="`background:${BG_F1};`") #[span(:style="f1Style(row.f1)") {{ row.f1.toFixed(1) }}]
          td.text-end(v-if="showDeltaLabel" :style="`background:${BG_DELTA};`")
            span(v-if="row.delta_f1 != null" :class="row.delta_f1 >= 0 ? 'text-success font-weight-medium' : 'text-error font-weight-medium'")
              | {{ row.delta_f1 >= 0 ? '+' : '' }}{{ row.delta_f1.toFixed(1) }}
            span(v-else class="text-disabled") –
      template(#bottom)

  //- ── Relation label-wise tab ─────────────────────────────────────────────
  div(v-if="activeTab === 'relations'")
    .d-flex.flex-wrap.ga-4.mb-3
      div
        .text-caption.text-medium-emphasis.mb-1 Test set
        v-btn-toggle(v-model="filterDataset" mandatory density="compact" variant="outlined" color="primary")
          v-btn(value="gsap-ere" size="small") GSAP-ERE
          v-btn(value="scier" size="small") SciER
          v-btn(value="scinlp" size="small") SciNLP
      div
        .text-caption.text-medium-emphasis.mb-1 Label space
        v-btn-toggle(v-model="filterLabelSet" mandatory density="compact" variant="outlined" color="secondary")
          v-btn(value="original" size="small") Original
          v-btn(value="unified" size="small") Unified
      div
        .text-caption.text-medium-emphasis.mb-1 RE metric
        v-btn-toggle(v-model="filterReMatch" mandatory density="compact" variant="outlined" color="primary")
          v-btn(value="relaxed" size="small") RE
          v-btn(value="relaxed_partial" size="small") RE≈
          v-btn(value="strict" size="small") RE+
          v-btn(value="strict_partial" size="small") RE+≈
      div
        .text-caption.text-medium-emphasis.mb-1 Trained on
        v-btn-toggle(
          :model-value="activeLabelTrainedOn"
          @update:model-value="filterLabelTrainedOn = $event"
          mandatory density="compact" variant="outlined" color="primary"
        )
          v-btn(v-for="to in labelTrainedOnOptions" :key="to" :value="to" size="small") {{ displayModel(to) }}
      v-btn-toggle(v-model="showLabelDelta" multiple density="compact" variant="outlined" color="teal" style="align-self:flex-end")
        v-btn(value="delta" size="small") Δ delta
    v-data-table(
      :headers="labelRelDetailHeaders"
      :items="relationLabelRows"
      :sort-by="[{ key: 'group', order: 'asc' }, { key: 'f1', order: 'desc' }]"
      :cell-props="labelCellProps"
      :items-per-page="-1"
      density="compact" hover
    )
      template(#item.group="{ item }")
        span.text-caption.text-medium-emphasis {{ item.group }}
      template(#item.precision="{ item }")
        span(:style="pStyle(item.precision)") {{ item.precision.toFixed(1) }}
      template(#item.recall="{ item }")
        span(:style="rStyle(item.recall)") {{ item.recall.toFixed(1) }}
      template(#item.f1="{ item }")
        span(:style="f1Style(item.f1)") {{ item.f1.toFixed(1) }}
      template(#item.delta_f1="{ item }")
        span(v-if="item.delta_f1 != null" :class="item.delta_f1 >= 0 ? 'text-success font-weight-medium' : 'text-error font-weight-medium'")
          | {{ item.delta_f1 >= 0 ? '+' : '' }}{{ item.delta_f1.toFixed(1) }}
        span(v-else class="text-disabled") –
      template(#body.append)
        tr(
          v-for="row in relationAggRows" :key="`agg-rel-${row.label}`"
          style="border-top:2px solid rgba(0,0,0,0.15);background:rgba(0,0,0,0.03);font-weight:600;"
        )
          td
          td {{ row.label }}
          td.text-end(:style="`background:${BG_P};${pStyle(row.precision)}`") {{ row.precision.toFixed(1) }}
          td.text-end(:style="`background:${BG_R};${rStyle(row.recall)}`") {{ row.recall.toFixed(1) }}
          td.text-end(:style="`background:${BG_F1};`") #[span(:style="f1Style(row.f1)") {{ row.f1.toFixed(1) }}]
          td.text-end(v-if="showDeltaLabel" :style="`background:${BG_DELTA};`")
            span(v-if="row.delta_f1 != null" :class="row.delta_f1 >= 0 ? 'text-success font-weight-medium' : 'text-error font-weight-medium'")
              | {{ row.delta_f1 >= 0 ? '+' : '' }}{{ row.delta_f1.toFixed(1) }}
            span(v-else class="text-disabled") –
      template(#bottom)

  v-snackbar(v-model="snack.show" :color="snack.color" timeout="4000") {{ snack.message }}
</template>

<script setup>
import { ref, computed, watch } from "vue";
import { useDockerMode } from "../composables/useDockerMode.js";
import {
    Chart as ChartJS,
    RadarController, RadialLinearScale,
    PointElement, LineElement, Filler,
    Tooltip as ChartTooltip, Legend as ChartLegend,
} from "chart.js";
import { Radar } from "vue-chartjs";

ChartJS.register(RadarController, RadialLinearScale, PointElement, LineElement, Filler, ChartTooltip, ChartLegend);

const { dockerMode } = useDockerMode();
const building = ref(false);
const generatedAt = ref(null);
const allSummary = ref([]);
const allLabels = ref([]);
const reported = ref({});
const seededComparison = ref([]);
const pipeline = ref(null);
const snack = ref({ show: false, message: "", color: "success" });
const activeTab = ref("radar");
const showStd = ref(true);
const seededMetrics = ref(["ner", "re", "rep"]);
const seededDelta = ref(["delta"]);
const seededStd = ref(["std"]);
const seededDatasets = ref(["gsap-ere", "scier", "scinlp"]);
const seededLabelSet = ref("original");
const seededSplit = ref("test");
const showDelta = computed(() => seededDelta.value.includes("delta"));
const showStdSeeded = computed(() => seededStd.value.includes("std"));

const DATASETS = ["gsap-ere", "scier", "scinlp"];

const DATASET_TO_PRED_LS_LOCAL = {
    "gsap-ere": "gsap",
    scier: "scier",
    scinlp: "scinlp",
};

// Display labels for known model IDs
const MODEL_DISPLAY = {
    "multi-sciere-gsap": "gsap-ere",
    "multi-sciere-scier": "scier",
    "multi-sciere-scinlp": "scinlp",
    "multi-sciere-scinlp-gsap-ere": "gsap-ere + scinlp",
    "multi-sciere-gsap-ere-scier": "gsap-ere + scier",
    "multi-sciere-scinlp-scier": "scier + scinlp",
    "multi-sciere-gsap-ere-scier-scinlp": "gsap-ere + scier + scinlp",
};
function displayModel(modelId) {
    return MODEL_DISPLAY[modelId] ?? modelId;
}

const filterDataset = ref("gsap-ere");
const filterLabelSet = ref("original");
const filterNerMatch = ref("exact");
const filterReMatch  = ref("relaxed");

// ── Label tab: Trained-on selection & delta ───────────────────────────────────
const filterLabelTrainedOn = ref(null)   // null → auto-select first available
const showLabelDelta       = ref(["delta"])
const showDeltaLabel       = computed(() => showLabelDelta.value.includes("delta"))

watch(filterDataset, () => { filterLabelTrainedOn.value = null })

const baselineLabelTrainedOn = computed(() =>
    "multi-sciere-" + DATASET_TO_PRED_LS[filterDataset.value]
)

const labelTrainedOnOptions = computed(() => {
    const baseline = baselineLabelTrainedOn.value
    const seen = new Set()
    const nonBase = []
    for (const r of allLabels.value) {
        if (r.dataset !== filterDataset.value) continue
        const to = r.trained_on
        if (seen.has(to)) continue
        seen.add(to)
        if (to !== baseline) nonBase.push(to)
    }
    return seen.has(baseline) ? [baseline, ...nonBase] : nonBase
})

const activeLabelTrainedOn = computed(() => {
    const opts = labelTrainedOnOptions.value
    if (!opts.length) return null
    return (filterLabelTrainedOn.value && opts.includes(filterLabelTrainedOn.value))
        ? filterLabelTrainedOn.value
        : opts[0]
})

function makeBaselineF1Map(task, matchKey) {
    const map = {}
    for (const r of allLabels.value) {
        if (r.task      !== task                       ) continue
        if (r.dataset   !== filterDataset.value        ) continue
        if (r.label_set !== filterLabelSet.value       ) continue
        if (r.match     !== matchKey                   ) continue
        if (r.trained_on !== baselineLabelTrainedOn.value) continue
        map[r.label] = r.f1
    }
    return map
}

const entBaselineF1Map = computed(() => makeBaselineF1Map("ner", filterNerMatch.value))
const relBaselineF1Map = computed(() => makeBaselineF1Map("re",  filterReMatch.value))

const DATASET_COLORS = { "gsap-ere": "blue", scier: "green", scinlp: "orange" };
function datasetColor(ds) {
    return DATASET_COLORS[ds] ?? "grey";
}

const C_P = "#1565c0";
const C_R = "#c62828";
const C_F1 = "#2e7d32";
const C_PAPER = "#546e7a";
const C_DELTA = "#37474f";

function pStyle(v) {
    if (v == null) return "color:#9e9e9e;";
    const t = Math.max(0, Math.min(1, v / 100));
    return `color:rgb(${Math.round(180 - t * 159)},${Math.round(210 - t * 109)},${Math.round(245 - t * 53)});font-weight:600;`;
}
function rStyle(v) {
    if (v == null) return "color:#9e9e9e;";
    const t = Math.max(0, Math.min(1, v / 100));
    return `color:rgb(${Math.round(245 - t * 47)},${Math.round(180 - t * 140)},${Math.round(180 - t * 140)});font-weight:600;`;
}
function f1Style(v) {
    if (v == null) return "color:#9e9e9e;";
    const t = Math.max(0, Math.min(1, v / 100));
    const r = Math.round(220 - t * 150);
    const g = Math.round(100 + t * 100);
    return `color:rgb(${r},${g},60);font-weight:600;`;
}

function col(columns, key) {
    return columns.find((c) => c.key === key) ?? { key };
}

const perfHeaders = [
    { key: "dataset", title: "Dataset", sortable: true },
    { key: "label_set", title: "Label set", sortable: true },
    { key: "ner_exact_precision", title: "P", sortable: true, align: "end" },
    { key: "ner_exact_recall", title: "R", sortable: true, align: "end" },
    { key: "ner_exact_f1", title: "F1", sortable: true, align: "end" },
    { key: "ner_partial_precision", title: "P", sortable: true, align: "end" },
    { key: "ner_partial_recall", title: "R", sortable: true, align: "end" },
    { key: "ner_partial_f1", title: "F1", sortable: true, align: "end" },
    { key: "re_relaxed_precision", title: "P", sortable: true, align: "end" },
    { key: "re_relaxed_recall", title: "R", sortable: true, align: "end" },
    { key: "re_relaxed_f1", title: "F1", sortable: true, align: "end" },
    {
        key: "re_relaxed_partial_precision",
        title: "P",
        sortable: true,
        align: "end",
    },
    {
        key: "re_relaxed_partial_recall",
        title: "R",
        sortable: true,
        align: "end",
    },
    { key: "re_relaxed_partial_f1", title: "F1", sortable: true, align: "end" },
    { key: "re_strict_precision", title: "P", sortable: true, align: "end" },
    { key: "re_strict_recall", title: "R", sortable: true, align: "end" },
    { key: "re_strict_f1", title: "F1", sortable: true, align: "end" },
    {
        key: "re_strict_partial_precision",
        title: "P",
        sortable: true,
        align: "end",
    },
    {
        key: "re_strict_partial_recall",
        title: "R",
        sortable: true,
        align: "end",
    },
    { key: "re_strict_partial_f1", title: "F1", sortable: true, align: "end" },
];

const BG_P = "rgba(21,101,192,0.07)";
const BG_R = "rgba(198,40,40,0.07)";
const BG_F1 = "rgba(46,125,50,0.07)";
const BG_PAPER = "rgba(84,110,122,0.06)";
const BG_DELTA = "rgba(55,71,79,0.04)";

const PERF_P_KEYS = new Set([
    "ner_exact_precision",
    "ner_partial_precision",
    "re_relaxed_precision",
    "re_relaxed_partial_precision",
    "re_strict_precision",
    "re_strict_partial_precision",
]);
const PERF_R_KEYS = new Set([
    "ner_exact_recall",
    "ner_partial_recall",
    "re_relaxed_recall",
    "re_relaxed_partial_recall",
    "re_strict_recall",
    "re_strict_partial_recall",
]);
const PERF_F1_KEYS = new Set([
    "ner_exact_f1",
    "ner_partial_f1",
    "re_relaxed_f1",
    "re_relaxed_partial_f1",
    "re_strict_f1",
    "re_strict_partial_f1",
]);
const COMP_F1_KEYS = new Set(["ner_exact_f1", "re_relaxed_f1", "re_strict_f1"]);
const COMP_PAPER_KEYS = new Set([
    "ner_reported",
    "re_reported",
    "rep_reported",
]);
const COMP_DELTA_KEYS = new Set(["ner_delta", "re_delta", "rep_delta"]);

function perfCellProps({ column }) {
    const k = column?.key;
    if (PERF_P_KEYS.has(k)) return { style: `background:${BG_P};` };
    if (PERF_R_KEYS.has(k)) return { style: `background:${BG_R};` };
    if (PERF_F1_KEYS.has(k)) return { style: `background:${BG_F1};` };
    return {};
}
function compCellProps({ column }) {
    const k = column?.key;
    if (COMP_F1_KEYS.has(k)) return { style: `background:${BG_F1};` };
    if (COMP_PAPER_KEYS.has(k)) return { style: `background:${BG_PAPER};` };
    if (COMP_DELTA_KEYS.has(k)) return { style: `background:${BG_DELTA};` };
    return {};
}
function labelCellProps({ column }) {
    const k = column?.key;
    if (k === "precision") return { style: `background:${BG_P};` };
    if (k === "recall")    return { style: `background:${BG_R};` };
    if (k === "f1")        return { style: `background:${BG_F1};` };
    if (k === "delta_f1")  return { style: `background:${BG_DELTA};` };
    return {};
}

const SEP = "border-right:1px solid rgba(0,0,0,0.12);";
const perfSubCols = [
    {
        key: "ner_exact_precision",
        label: "P",
        style: `color:${C_P};background:${BG_P};`,
    },
    {
        key: "ner_exact_recall",
        label: "R",
        style: `color:${C_R};background:${BG_R};`,
    },
    {
        key: "ner_exact_f1",
        label: "F1",
        style: `color:${C_F1};background:${BG_F1};`,
    },
    {
        key: "ner_partial_precision",
        label: "P",
        style: `color:${C_P};background:${BG_P};opacity:0.8;`,
    },
    {
        key: "ner_partial_recall",
        label: "R",
        style: `color:${C_R};background:${BG_R};opacity:0.8;`,
    },
    {
        key: "ner_partial_f1",
        label: "F1",
        style: `color:${C_F1};background:${BG_F1};opacity:0.8;${SEP}`,
    },
    {
        key: "re_relaxed_precision",
        label: "P",
        style: `color:${C_P};background:${BG_P};`,
    },
    {
        key: "re_relaxed_recall",
        label: "R",
        style: `color:${C_R};background:${BG_R};`,
    },
    {
        key: "re_relaxed_f1",
        label: "F1",
        style: `color:${C_F1};background:${BG_F1};`,
    },
    {
        key: "re_relaxed_partial_precision",
        label: "P",
        style: `color:${C_P};background:${BG_P};opacity:0.8;`,
    },
    {
        key: "re_relaxed_partial_recall",
        label: "R",
        style: `color:${C_R};background:${BG_R};opacity:0.8;`,
    },
    {
        key: "re_relaxed_partial_f1",
        label: "F1",
        style: `color:${C_F1};background:${BG_F1};opacity:0.8;${SEP}`,
    },
    {
        key: "re_strict_precision",
        label: "P",
        style: `color:${C_P};background:${BG_P};`,
    },
    {
        key: "re_strict_recall",
        label: "R",
        style: `color:${C_R};background:${BG_R};`,
    },
    {
        key: "re_strict_f1",
        label: "F1",
        style: `color:${C_F1};background:${BG_F1};`,
    },
    {
        key: "re_strict_partial_precision",
        label: "P",
        style: `color:${C_P};background:${BG_P};opacity:0.8;`,
    },
    {
        key: "re_strict_partial_recall",
        label: "R",
        style: `color:${C_R};background:${BG_R};opacity:0.8;`,
    },
    {
        key: "re_strict_partial_f1",
        label: "F1",
        style: `color:${C_F1};background:${BG_F1};opacity:0.8;`,
    },
];

const compHeaders = [
    { key: "dataset", title: "Dataset", sortable: true },
    { key: "ner_exact_f1", title: "NER F1", sortable: true, align: "end" },
    { key: "ner_reported", title: "NER Paper", sortable: true, align: "end" },
    { key: "ner_delta", title: "Δ NER", sortable: true, align: "end" },
    { key: "re_relaxed_f1", title: "RE F1", sortable: true, align: "end" },
    { key: "re_reported", title: "RE Paper", sortable: true, align: "end" },
    { key: "re_delta", title: "Δ RE", sortable: true, align: "end" },
    { key: "re_strict_f1", title: "RE+ F1", sortable: true, align: "end" },
    { key: "rep_reported", title: "RE+ Paper", sortable: true, align: "end" },
    { key: "rep_delta", title: "Δ RE+", sortable: true, align: "end" },
];

const compSubCols = [
    {
        key: "ner_exact_f1",
        label: "F1",
        style: `color:${C_F1};background:${BG_F1};`,
    },
    {
        key: "ner_reported",
        label: "Paper",
        style: `color:${C_PAPER};background:${BG_PAPER};`,
    },
    {
        key: "ner_delta",
        label: "Δ",
        style: `color:${C_DELTA};background:${BG_DELTA};border-right:1px solid rgba(0,0,0,0.12);`,
    },
    {
        key: "re_relaxed_f1",
        label: "F1",
        style: `color:${C_F1};background:${BG_F1};`,
    },
    {
        key: "re_reported",
        label: "Paper",
        style: `color:${C_PAPER};background:${BG_PAPER};`,
    },
    {
        key: "re_delta",
        label: "Δ",
        style: `color:${C_DELTA};background:${BG_DELTA};border-right:1px solid rgba(0,0,0,0.12);`,
    },
    {
        key: "re_strict_f1",
        label: "F1",
        style: `color:${C_F1};background:${BG_F1};`,
    },
    {
        key: "rep_reported",
        label: "Paper",
        style: `color:${C_PAPER};background:${BG_PAPER};`,
    },
    {
        key: "rep_delta",
        label: "Δ",
        style: `color:${C_DELTA};background:${BG_DELTA};`,
    },
];

const compRows = computed(() =>
    allSummary.value
        .filter((r) => r.label_set === "original")
        .map((r) => {
            const rep = reported.value[r.dataset] ?? {};
            return {
                ...r,
                ner_reported: rep.NER ?? null,
                ner_delta:
                    rep.NER != null
                        ? +(r.ner_exact_f1 - rep.NER).toFixed(1)
                        : null,
                re_reported: rep.RE ?? null,
                re_delta:
                    rep.RE != null
                        ? +(r.re_relaxed_f1 - rep.RE).toFixed(1)
                        : null,
                rep_reported: rep["RE+"] ?? null,
                rep_delta:
                    rep["RE+"] != null
                        ? +(r.re_strict_f1 - rep["RE+"]).toFixed(1)
                        : null,
            };
        }),
);

// ── Seeded comparison table ───────────────────────────────────────────────────

const METRIC_DEFS = [
    {
        id: "ner",
        f1Key: "ner_f1",
        deltaKey: "ner_delta",
        f1Title: "NER F1",
        deltaTitle: "Δ NER",
    },
    {
        id: "ner_partial",
        f1Key: "ner_p_f1",
        deltaKey: "ner_p_delta",
        f1Title: "NER≈ F1",
        deltaTitle: "Δ NER≈",
    },
    {
        id: "re",
        f1Key: "re_f1",
        deltaKey: "re_delta",
        f1Title: "RE F1",
        deltaTitle: "Δ RE",
    },
    {
        id: "re_partial",
        f1Key: "re_p_f1",
        deltaKey: "re_p_delta",
        f1Title: "RE≈ F1",
        deltaTitle: "Δ RE≈",
    },
    {
        id: "rep",
        f1Key: "rep_f1",
        deltaKey: "rep_delta",
        f1Title: "RE+ F1",
        deltaTitle: "Δ RE+",
    },
    {
        id: "rep_partial",
        f1Key: "rep_p_f1",
        deltaKey: "rep_p_delta",
        f1Title: "RE+≈ F1",
        deltaTitle: "Δ RE+≈",
    },
];

const seededHeaders = computed(() => {
    const h = [
        { key: "trained_on", title: "Trained on", sortable: true },
        { key: "test_dataset", title: "Test set", sortable: true },
    ];
    for (const def of METRIC_DEFS) {
        if (!seededMetrics.value.includes(def.id)) continue;
        h.push({
            key: def.f1Key,
            title: def.f1Title,
            sortable: true,
            align: "end",
        });
        if (showDelta.value)
            h.push({
                key: def.deltaKey,
                title: def.deltaTitle,
                sortable: true,
                align: "end",
            });
    }
    return h;
});

const SEEDED_F1_KEYS = new Set([
    "ner_f1",
    "ner_p_f1",
    "re_f1",
    "re_p_f1",
    "rep_f1",
    "rep_p_f1",
]);
const SEEDED_DELTA_KEYS = new Set([
    "ner_delta",
    "ner_p_delta",
    "re_delta",
    "re_p_delta",
    "rep_delta",
    "rep_p_delta",
]);
function seededCellProps({ column }) {
    const k = column?.key;
    if (SEEDED_F1_KEYS.has(k)) return { style: `background:${BG_F1};` };
    if (SEEDED_DELTA_KEYS.has(k)) return { style: `background:${BG_DELTA};` };
    return {};
}

// Build flat rows for the seeded comparison table for a given test dataset.
// First row: baseline; subsequent rows: seeded models.
// Baseline uses seeded mean/std from seededComparison if available, else allSummary single value.
function seededRowsFor(testDataset) {
    const baselineKey = testDataset; // e.g. "gsap-ere", "scinlp"
    const evalLabelSet = seededLabelSet.value;
    const split = testDataset === "scier" ? seededSplit.value : "test";

    const matchesSplit = (sc) => (sc.split ?? "test") === split;

    // Prefer seeded baseline (mean/std) over single-run baseline
    const baselineSeeded = seededComparison.value.find(
        (sc) => sc.test_dataset === testDataset && sc.model_id === baselineKey && sc.eval_label_set === evalLabelSet && matchesSplit(sc),
    );
    const baselineSingle = allSummary.value.find(
        (r) =>
            r.dataset === testDataset &&
            r.label_set === evalLabelSet &&
            r.trained_on === baselineKey,
    );
    const hasBaseline = baselineSeeded || baselineSingle;

    // Values used for delta computation — prefer seeded mean
    const baseNer = baselineSeeded
        ? baselineSeeded.ner_exact_f1_mean
        : (baselineSingle?.ner_exact_f1 ?? null);
    const baseNerP = baselineSeeded
        ? baselineSeeded.ner_partial_f1_mean
        : (baselineSingle?.ner_partial_f1 ?? null);
    const baseRe = baselineSeeded
        ? baselineSeeded.re_relaxed_f1_mean
        : (baselineSingle?.re_relaxed_f1 ?? null);
    const baseReP = baselineSeeded
        ? baselineSeeded.re_relaxed_partial_f1_mean
        : (baselineSingle?.re_relaxed_partial_f1 ?? null);
    const baseRep = baselineSeeded
        ? baselineSeeded.re_strict_f1_mean
        : (baselineSingle?.re_strict_f1 ?? null);
    const baseRepP = baselineSeeded
        ? baselineSeeded.re_strict_partial_f1_mean
        : (baselineSingle?.re_strict_partial_f1 ?? null);

    const rows = [];
    if (hasBaseline) {
        rows.push({
            trained_on_label: displayModel(baselineKey),
            is_baseline: true,
            ner_f1: baseNer,
            ner_std: baselineSeeded?.ner_exact_f1_std ?? null,
            ner_delta: null,
            ner_p_f1: baseNerP,
            ner_p_std: baselineSeeded?.ner_partial_f1_std ?? null,
            ner_p_delta: null,
            re_f1: baseRe,
            re_std: baselineSeeded?.re_relaxed_f1_std ?? null,
            re_delta: null,
            re_p_f1: baseReP,
            re_p_std: baselineSeeded?.re_relaxed_partial_f1_std ?? null,
            re_p_delta: null,
            rep_f1: baseRep,
            rep_std: baselineSeeded?.re_strict_f1_std ?? null,
            rep_delta: null,
            rep_p_f1: baseRepP,
            rep_p_std: baselineSeeded?.re_strict_partial_f1_std ?? null,
            rep_p_delta: null,
        });
    }
    for (const sc of seededComparison.value) {
        if (sc.test_dataset !== testDataset || sc.model_id === baselineKey || sc.eval_label_set !== evalLabelSet || !matchesSplit(sc))
            continue;
        const delta = (base, val) =>
            base != null ? +(val - base).toFixed(1) : null;
        rows.push({
            trained_on_label: displayModel(sc.model_id),
            is_baseline: false,
            ner_f1: sc.ner_exact_f1_mean,
            ner_std: sc.ner_exact_f1_std,
            ner_delta: delta(baseNer, sc.ner_exact_f1_mean),
            ner_p_f1: sc.ner_partial_f1_mean,
            ner_p_std: sc.ner_partial_f1_std,
            ner_p_delta: delta(baseNerP, sc.ner_partial_f1_mean),
            re_f1: sc.re_relaxed_f1_mean,
            re_std: sc.re_relaxed_f1_std,
            re_delta: delta(baseRe, sc.re_relaxed_f1_mean),
            re_p_f1: sc.re_relaxed_partial_f1_mean,
            re_p_std: sc.re_relaxed_partial_f1_std,
            re_p_delta: delta(baseReP, sc.re_relaxed_partial_f1_mean),
            rep_f1: sc.re_strict_f1_mean,
            rep_std: sc.re_strict_f1_std,
            rep_delta: delta(baseRep, sc.re_strict_f1_mean),
            rep_p_f1: sc.re_strict_partial_f1_mean,
            rep_p_std: sc.re_strict_partial_f1_std,
            rep_p_delta: delta(baseRepP, sc.re_strict_partial_f1_mean),
        });
    }
    return rows;
}

const seededRows = computed(() => DATASETS.flatMap((ds) => seededRowsFor(ds)));

const seededAllRows = computed(() => {
    const rows = DATASETS.filter((ds) =>
        seededDatasets.value.includes(ds),
    ).flatMap((ds) =>
        seededRowsFor(ds).map((row) => ({ ...row, test_dataset: ds })),
    );
    return rows.map((row, i) => ({
        ...row,
        _group_sep: i > 0 && rows[i - 1].test_dataset !== row.test_dataset,
    }));
});

function seededRowProps({ item }) {
    return item._group_sep
        ? { style: "border-top: 3px solid rgba(0,0,0,0.22);" }
        : {};
}

const labelEntDetailHeaders = computed(() => {
    const h = [
        { title: "Label", key: "label",     sortable: true },
        { title: "P",     key: "precision", sortable: true, align: "end" },
        { title: "R",     key: "recall",    sortable: true, align: "end" },
        { title: "F1",    key: "f1",        sortable: true, align: "end" },
    ]
    if (showDeltaLabel.value)
        h.push({ title: "Δ F1", key: "delta_f1", sortable: true, align: "end" })
    return h
});

const labelRelDetailHeaders = computed(() => {
    const h = [
        { title: "Group", key: "group",     sortable: true },
        { title: "Label", key: "label",     sortable: true },
        { title: "P",     key: "precision", sortable: true, align: "end" },
        { title: "R",     key: "recall",    sortable: true, align: "end" },
        { title: "F1",    key: "f1",        sortable: true, align: "end" },
    ]
    if (showDeltaLabel.value)
        h.push({ title: "Δ F1", key: "delta_f1", sortable: true, align: "end" })
    return h
});

function filterNer(r) {
    return r.task === "ner"
        && r.dataset   === filterDataset.value
        && r.label_set === filterLabelSet.value
        && r.match     === filterNerMatch.value
}
function filterRe(r) {
    return r.task === "re"
        && r.dataset   === filterDataset.value
        && r.label_set === filterLabelSet.value
        && r.match     === filterReMatch.value
}

// Per-dataset native pred label set (mirrors DATASET_TO_PRED_LS in the script)
const DATASET_TO_PRED_LS = {
    "gsap-ere": "gsap",
    scier: "scier",
    scinlp: "scinlp",
};

// ── Relation semantic groups ──────────────────────────────────────────────────
const UNIFIED_TO_GROUP = {
    appliedTo:          "Task Binding",
    benchmarkFor:       "Task Binding",
    trainedEvaluatedOn: "Data Usage",
    usedFor:            "Model Design",
    coreference:        "Peer Relating",
    isHyponymOf:        "Peer Relating",
    isComparedTo:       "Peer Relating",
    isPartOf:           "Peer Relating",
}
const GROUP_ORDER = ["Task Binding", "Data Usage", "Model Design", "Peer Relating", "Dropped", "Other"]

const relMappings = computed(() => pipeline.value?.relation_mappings ?? {})

function relGroupForRow(row) {
    if (row.label_set === "unified") return UNIFIED_TO_GROUP[row.label] ?? "Other"
    const mappings = relMappings.value?.[row.dataset] ?? []
    const entry = mappings.find(m => m.original === row.label)
    if (!entry) return UNIFIED_TO_GROUP[row.label] ?? "Other"
    if (entry.unified.startsWith("—")) return "Dropped"
    return UNIFIED_TO_GROUP[entry.unified] ?? "Other"
}

// Only the matching trained_on per dataset (original + unified), 2 rows per dataset
const nativeSummary = computed(() =>
    allSummary.value.filter(
        (r) => r.trained_on === `multi-sciere-${DATASET_TO_PRED_LS[r.dataset]}`,
    ),
);

const AGGREGATE_LABELS = new Set(["micro", "macro", "weighted"]);

function withDelta(r, baseMap) {
    const base = baseMap[r.label]
    return { ...r, delta_f1: base != null ? +(r.f1 - base).toFixed(1) : null }
}

const entityLabelRows = computed(() =>
    allLabels.value
        .filter(r => filterNer(r) && !AGGREGATE_LABELS.has(r.label) && r.trained_on === activeLabelTrainedOn.value)
        .map(r => withDelta(r, entBaselineF1Map.value))
)
const entityAggRows = computed(() =>
    allLabels.value
        .filter(r => filterNer(r) && AGGREGATE_LABELS.has(r.label) && r.trained_on === activeLabelTrainedOn.value)
        .map(r => withDelta(r, entBaselineF1Map.value))
)
const relationLabelRows = computed(() =>
    allLabels.value
        .filter(r => filterRe(r) && !AGGREGATE_LABELS.has(r.label) && r.trained_on === activeLabelTrainedOn.value)
        .map(r => withDelta({ ...r, group: relGroupForRow(r) }, relBaselineF1Map.value))
        .sort((a, b) => {
            const gi = (GROUP_ORDER.indexOf(a.group) + 1 || 999) - (GROUP_ORDER.indexOf(b.group) + 1 || 999)
            return gi !== 0 ? gi : b.f1 - a.f1
        })
)
const relationAggRows = computed(() =>
    allLabels.value
        .filter(r => filterRe(r) && AGGREGATE_LABELS.has(r.label) && r.trained_on === activeLabelTrainedOn.value)
        .map(r => withDelta(r, relBaselineF1Map.value))
)

// ── Radar charts ─────────────────────────────────────────────────────────────

const RADAR_AXIS_ORDER  = ['scier', 'scinlp', 'gsap-ere'];
const RADAR_AXIS_LABELS = { 'gsap-ere': 'GSAP-ERE', scier: 'SciER', scinlp: 'SciNLP' };
const MULTI_COMBO_DEFS  = [
    { id: 'multi-sciere-gsap-ere-scier',        label: 'GSAP-ERE + SciER',  rgb: '99,110,250'  },
    { id: 'multi-sciere-scinlp-gsap-ere',       label: 'GSAP-ERE + SciNLP', rgb: '239,85,59'   },
    { id: 'multi-sciere-scinlp-scier',          label: 'SciER + SciNLP',    rgb: '0,204,150'   },
    { id: 'multi-sciere-gsap-ere-scier-scinlp', label: 'All',               rgb: '171,99,250'  },
];
const RADAR_METRICS = [
    { id: 'ner',   key: 'ner_exact_f1_mean',          title: 'NER'   },
    { id: 'ner_p', key: 'ner_partial_f1_mean',         title: 'NER≈'  },
    { id: 're',    key: 're_relaxed_f1_mean',          title: 'RE'    },
    { id: 'rep_p', key: 're_strict_partial_f1_mean',   title: 'RE+≈'  },
    { id: 'rep',   key: 're_strict_f1_mean',           title: 'RE+'   },
];
// Pentagon axis order for "By Dataset" mode (NER top-left, NER≈ top-right, RE+≈ right, RE bottom, RE+ bottom-left)
const RADAR_BY_DATASET_ORDER = ['ner', 'ner_p', 'rep_p', 're', 'rep'];
const RADAR_BY_DATASET_START_ANGLE = -126 * Math.PI / 180;

const radarGroupBy = ref('dataset');
const radarMetrics = ref(['ner', 'ner_p', 're', 'rep_p', 'rep']);
const radarActiveMetrics = computed(() =>
    RADAR_METRICS.filter(m => radarMetrics.value.includes(m.id))
);

function getSeededF1forRadar(modelId, testDs) {
    const split = testDs === 'scier' ? seededSplit.value : 'test';
    return seededComparison.value.find(
        s => s.model_id === modelId &&
             s.test_dataset === testDs &&
             s.eval_label_set === seededLabelSet.value &&
             (s.split ?? 'test') === split
    ) ?? null;
}

function radarChartData(metric) {
    const labels = RADAR_AXIS_ORDER.map(ds => RADAR_AXIS_LABELS[ds]);
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
    };
    const comboDatasets = MULTI_COMBO_DEFS.map(combo => {
        const data = RADAR_AXIS_ORDER.map(testDs => {
            const ce = getSeededF1forRadar(combo.id, testDs);
            const be = getSeededF1forRadar(testDs,   testDs);
            if (!ce || !be) return null;
            const cf = ce[metric.key], bf = be[metric.key];
            if (cf == null || bf == null) return null;
            return +(cf - bf).toFixed(2);
        });
        return {
            label: combo.label,
            data,
            borderColor: `rgb(${combo.rgb})`,
            backgroundColor: `rgba(${combo.rgb},0.12)`,
            pointBackgroundColor: `rgb(${combo.rgb})`,
            pointBorderColor: '#fff',
            pointRadius: 4,
            borderWidth: 2,
            spanGaps: false,
        };
    });
    return { labels, datasets: [refDataset, ...comboDatasets] };
}

const radarHasData = computed(() =>
    seededComparison.value.length > 0 && seededRows.value.length > 0
);

const radarOpts = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
        r: {
            suggestedMin: -4,
            suggestedMax: 8,
            ticks: { stepSize: 2, font: { size: 9 }, callback: v => (v > 0 ? '+' : '') + v },
            grid: { color: 'rgba(0,0,0,0.1)' },
            angleLines: { color: 'rgba(0,0,0,0.18)' },
            pointLabels: { font: { size: 12, weight: '500' } },
        },
    },
    plugins: {
        legend: { position: 'bottom', labels: { boxWidth: 10, padding: 8, font: { size: 11 } } },
        tooltip: { callbacks: { label: ctx => ` ${ctx.dataset.label}: ${ctx.raw != null ? (ctx.raw >= 0 ? '+' : '') + ctx.raw.toFixed(1) : 'n/a'}` } },
    },
};

const radarOptsByDataset = {
    responsive: true,
    maintainAspectRatio: false,
    startAngle: RADAR_BY_DATASET_START_ANGLE,
    scales: {
        r: {
            suggestedMin: -4,
            suggestedMax: 8,
            ticks: { stepSize: 2, font: { size: 9 }, callback: v => (v > 0 ? '+' : '') + v },
            grid: { color: 'rgba(0,0,0,0.1)' },
            angleLines: { color: 'rgba(0,0,0,0.18)' },
            pointLabels: { font: { size: 11, weight: '500' } },
        },
    },
    plugins: {
        legend: { position: 'bottom', labels: { boxWidth: 10, padding: 8, font: { size: 11 } } },
        tooltip: { callbacks: { label: ctx => ` ${ctx.dataset.label}: ${ctx.raw != null ? (ctx.raw >= 0 ? '+' : '') + ctx.raw.toFixed(1) : 'n/a'}` } },
    },
};

function radarChartDataByDataset(testDs) {
    const activeIds = new Set(radarMetrics.value);
    const axisMetrics = RADAR_METRICS
        .filter(m => activeIds.has(m.id))
        .sort((a, b) => RADAR_BY_DATASET_ORDER.indexOf(a.id) - RADAR_BY_DATASET_ORDER.indexOf(b.id));

    const baseEntry = getSeededF1forRadar(testDs, testDs);

    const labels = axisMetrics.map(m => {
        if (!baseEntry) return m.title;
        const bf = baseEntry[m.key];
        if (bf == null) return m.title;
        const bs = baseEntry[m.key.replace('_mean', '_std')];
        const stdPart = bs != null ? `±${bs.toFixed(1)}` : '';
        return [m.title, `(F1 ${bf.toFixed(1)}${stdPart})`];
    });

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
    };

    const comboDatasets = MULTI_COMBO_DEFS.flatMap(combo => {
        const ce = getSeededF1forRadar(combo.id, testDs);
        if (!ce) return [];
        const data = axisMetrics.map(m => {
            if (!baseEntry) return null;
            const cf = ce[m.key], bf = baseEntry[m.key];
            if (cf == null || bf == null) return null;
            return +(cf - bf).toFixed(2);
        });
        return [{
            label: combo.label,
            data,
            borderColor: `rgb(${combo.rgb})`,
            backgroundColor: `rgba(${combo.rgb},0.12)`,
            pointBackgroundColor: `rgb(${combo.rgb})`,
            pointBorderColor: '#fff',
            pointRadius: 4,
            borderWidth: 2,
            spanGaps: false,
        }];
    });
    return { labels, datasets: [refDataset, ...comboDatasets] };
}

async function fetchData() {
    try {
        const res = await fetch("/api/multi-sciere");
        if (!res.ok) {
            snack.value = {
                show: true,
                message: "No data yet — click Rebuild.",
                color: "warning",
            };
            return;
        }
        const data = await res.json();
        generatedAt.value = data.generated_at
            ? new Date(data.generated_at).toLocaleString()
            : null;
        allSummary.value = data.summary ?? [];
        allLabels.value = data.labels ?? [];
        reported.value = data.reported ?? {};
        seededComparison.value = data.seeded_comparison ?? [];
    } catch (e) {
        snack.value = {
            show: true,
            message: `Failed to load: ${e.message}`,
            color: "error",
        };
    }
}

async function rebuild() {
    building.value = true;
    try {
        const res = await fetch("/api/multi-sciere/build", { method: "POST" });
        const data = await res.json();
        if (data.ok) {
            snack.value = {
                show: true,
                message: "Rebuilt successfully.",
                color: "success",
            };
            await fetchData();
        } else
            snack.value = {
                show: true,
                message: `Failed: ${data.stderr?.slice(0, 200)}`,
                color: "error",
            };
    } catch (e) {
        snack.value = {
            show: true,
            message: `Error: ${e.message}`,
            color: "error",
        };
    } finally {
        building.value = false;
    }
}

fetchData();
</script>
