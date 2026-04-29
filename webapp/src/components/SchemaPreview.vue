<template lang="pug">
v-container(fluid)
  .d-flex.align-center.mb-1
    h2.text-h5 Schema Preview
    v-spacer
    v-btn(
      size="small"
      :variant="semanticLayout ? 'flat' : 'outlined'"
      :color="semanticLayout ? 'primary' : 'default'"
      density="compact"
      prepend-icon="mdi-vector-triangle"
      @click="toggleSemanticLayout"
    ) Cluster by Role

  p.text-body-2.text-medium-emphasis.mb-3
    | The same BERT paper excerpt annotated under three schemas. Shared entities appear in
    | equivalent positions; node colors encode entity type labels, which differ in granularity
    | across schemas. Edge labels show each schema's distinct relation vocabulary for
    | semantically equivalent links. GSAP-ERE uses a fine-grained entity hierarchy and adds
    | referential nodes (citations, URLs); SciNLP additionally annotates evaluation metrics.

  v-tabs(v-model="activeDs" density="compact" color="primary" class="mb-3")
    v-tab(value="gsap-ere") GSAP-ERE
    v-tab(value="scier") SciER
    v-tab(value="scinlp") SciNLP

  GraphViz(
    ref="graphRef"
    :nodes="graphNodes"
    :edges="graphEdges"
    height="calc(100vh - 320px)"
    mark-id="schema"
  )

  //- Legend bar: entity types left, relation types right
  .d-flex.align-center.justify-space-between.px-3.py-2.mt-1(
    style="border:1px solid rgba(0,0,0,0.1);border-radius:8px;flex-wrap:wrap;gap:8px;"
  )
    .d-flex.flex-wrap.align-center(style="gap:10px;")
      .d-flex.align-center(v-for="t in currentEntityTypes" :key="t" style="gap:4px;")
        span.rounded(style="width:11px;height:11px;display:inline-block;flex-shrink:0;" :style="{ background: nodeColor(t) }")
        span.text-caption {{ t }}
    .d-flex.flex-wrap.align-center(style="gap:4px;")
      span.px-2.py-0.rounded.text-white(
        v-for="r in currentRelationTypes" :key="r"
        style="font-size:10px;line-height:17px;display:inline-block;"
        :style="{ background: relColor(r) }"
      ) {{ r }}
</template>

<script setup>
import { ref, computed, watch } from "vue";
import GraphViz from "./GraphViz.vue";

// ── semantic layout anchors ───────────────────────────────────────────────────
// Method/Model → top-left, Dataset → top-right, Task → bottom-right,
// Metric → bottom-left, Referential → far right.
const SCHEMA_ANCHORS = {
    "gsap-ere": {
        Method: { ax: 0.15, ay: 0.15 },
        MLModel: { ax: 0.18, ay: 0.12 },
        ModelArchitecture: { ax: 0.12, ay: 0.25 },
        Dataset: { ax: 0.82, ay: 0.15 },
        DataSource: { ax: 0.82, ay: 0.15 },
        DatasetGeneric: { ax: 0.82, ay: 0.15 },
        Task: { ax: 0.8, ay: 0.82 },
        ReferenceLink: { ax: 0.95, ay: 0.5 },
        URL: { ax: 0.95, ay: 0.6 },
    },
    scier: {
        Method: { ax: 0.18, ay: 0.12 },
        Dataset: { ax: 0.82, ay: 0.15 },
        Task: { ax: 0.8, ay: 0.82 },
    },
    scinlp: {
        method: { ax: 0.18, ay: 0.12 },
        dataset: { ax: 0.82, ay: 0.15 },
        task: { ax: 0.8, ay: 0.82 },
        metric: { ax: 0.15, ay: 0.82 },
    },
};

// Relations that carry attribute / referential info → tighter springs
const GSAP_ATTR_RELS = new Set(["url", "citation"]);

// ── colors ────────────────────────────────────────────────────────────────────
const TYPE_COLORS = {
    MLModel: "#1d4ed8",
    MLModelGeneric: "#1e40af",
    ModelArchitecture: "#3b82f6",
    Method: "#2563eb",
    Dataset: "#d97706",
    DataSource: "#b45309",
    DatasetGeneric: "#92400e",
    Task: "#b91c1c",
    ReferenceLink: "#6b7280",
    URL: "#9ca3af",
    method: "#2563eb",
    dataset: "#d97706",
    task: "#b91c1c",
    metric: "#15803d",
};
function nodeColor(type) {
    return TYPE_COLORS[type] ?? "#6b7280";
}

const REL_PALETTE = [
    "#7c3aed",
    "#0369a1",
    "#b45309",
    "#b91c1c",
    "#065f46",
    "#9333ea",
    "#c2410c",
    "#166534",
    "#be123c",
    "#1d4ed8",
    "#6b7280",
    "#047857",
];
const relColorCache = new Map();
let relIdx = 0;
function relColor(rel) {
    if (!relColorCache.has(rel))
        relColorCache.set(rel, REL_PALETTE[relIdx++ % REL_PALETTE.length]);
    return relColorCache.get(rel);
}

// ── schema data ───────────────────────────────────────────────────────────────
// Core entities are shared across all three schemas (same node id).
// Entity type labels and relation labels differ per schema — this is what the
// view illustrates. GSAP-ERE adds referential nodes; SciNLP adds metric nodes.

const schemas = {
    "gsap-ere": {
        nodes: [
            // ── shared core ──────────────────────────────────────────
            { id: "BERT", type: "MLModel" },
            { id: "Transformer", type: "ModelArchitecture" },
            { id: "GPT", type: "MLModel" },
            { id: "ELMo", type: "MLModel" },
            { id: "BooksCorpus", type: "Dataset" },
            { id: "Wikipedia", type: "Dataset" },
            { id: "Smashwords", type: "DataSource" },
            { id: "GLUE", type: "Dataset" },
            { id: "language understanding", type: "Task" },
            { id: "question answering", type: "Task" },
            { id: "pre-training", type: "Method" },
            // ── GSAP-ERE specific ────────────────────────────────────
            { id: "MLM", type: "Method" },
            { id: "our model", type: "MLModel" },
            { id: "Zhu et al. 2015", type: "ReferenceLink" },
            { id: "hf.co/bookcorpus", type: "URL" },
            {
                id: "General Language Understanding Evaluation",
                type: "Dataset",
            },
        ],
        edges: [
            // shared semantic links (different relation labels per schema)
            {
                source: "General Language Understanding Evaluation",
                target: "GLUE",
                label: "coreference",
            },
            { source: "BERT", target: "Transformer", label: "architecture" },
            { source: "BERT", target: "BooksCorpus", label: "trainedOn" },
            { source: "our model", target: "Wikipedia", label: "trainedOn" },
            { source: "BERT", target: "SQuAD", label: "evaluatedOn" },
            { source: "BERT", target: "GLUE", label: "evaluatedOn" },
            {
                source: "GLUE",
                target: "language understanding",
                label: "benchmarkFor",
            },
            {
                source: "BERT",
                target: "language understanding",
                label: "appliedTo",
            },
            { source: "our model", target: "GPT", label: "isComparedTo" },
            { source: "BERT", target: "ELMo", label: "isComparedTo" },
            {
                source: "pre-training",
                target: "BERT",
                label: "usedFor",
            },
            {
                source: "question answering",
                target: "language understanding",
                label: "isHyponymOf",
            },
            {
                source: "BooksCorpus",
                target: "Smashwords",
                label: "sourcedFrom",
            },
            // GSAP-ERE specific
            { source: "MLM", target: "BERT", label: "usedFor" },
            { source: "BERT", target: "our model", label: "coreference" },
            {
                source: "BooksCorpus",
                target: "Zhu et al. 2015",
                label: "citation",
            },
            { source: "BooksCorpus", target: "hf.co/bookcorpus", label: "url" },
        ],
    },

    scier: {
        nodes: [
            // ── shared core ──────────────────────────────────────────
            { id: "BERT", type: "MLModel" },
            { id: "Transformer", type: "ModelArchitecture" },
            { id: "GPT", type: "MLModel" },
            { id: "ELMo", type: "MLModel" },
            { id: "BooksCorpus", type: "Dataset" },
            { id: "Wikipedia", type: "Dataset" },
            { id: "GLUE", type: "Dataset" },
            { id: "language understanding", type: "Task" },
            { id: "question answering", type: "Task" },
            { id: "pre-training", type: "Method" },
            // ── GSAP-ERE specific ────────────────────────────────────
            { id: "MLM", type: "Method" },
            {
                id: "General Language Understanding Evaluation",
                type: "Dataset",
            },
        ],
        edges: [
            {
                source: "General Language Understanding Evaluation",
                target: "GLUE",
                label: "Synonym-Of",
            },
            // shared semantic links (different relation labels per schema)
            { source: "BERT", target: "Transformer", label: "SubClass-Of" },
            { source: "BERT", target: "BooksCorpus", label: "Trained-With" },
            { source: "BERT", target: "SQuAD", label: "Evaluated-With" },
            { source: "BERT", target: "GLUE", label: "Evaluated-With" },
            {
                source: "GLUE",
                target: "language understanding",
                label: "Benchmark-For",
            },
            {
                source: "BERT",
                target: "language understanding",
                label: "Used-For",
            },
            { source: "BERT", target: "ELMo", label: "Compare-With" },
            {
                source: "question answering",
                target: "language understanding",
                label: "SubTask-Of",
            },
        ],
    },

    scinlp: {
        nodes: [
            // ── shared core ──────────────────────────────────────────
            { id: "BERT", type: "MLModel" },
            { id: "Transformer", type: "ModelArchitecture" },
            { id: "GPT", type: "MLModel" },
            { id: "ELMo", type: "MLModel" },
            { id: "BooksCorpus", type: "Dataset" },
            { id: "Wikipedia", type: "Dataset" },
            { id: "GLUE", type: "Dataset" },
            { id: "language understanding", type: "Task" },
            { id: "question answering", type: "Task" },
            { id: "pre-training", type: "Method" },
            // ── GSAP-ERE specific ────────────────────────────────────
            { id: "MLM", type: "Method" },
            // ── SciNLP specific: evaluation metrics ──────────────────
            { id: "F1 score", type: "metric" },
            {
                id: "General Language Understanding Evaluation",
                type: "Dataset",
            },
        ],
        edges: [
            {
                source: "General Language Understanding Evaluation",
                target: "GLUE",
                label: "similarWith",
            },
            // shared semantic links (different relation labels per schema)
            { source: "BERT", target: "Transformer", label: "enhancedBy" },
            { source: "BERT", target: "BooksCorpus", label: "trainedWith" },
            { source: "BERT", target: "SQuAD", label: "trainedWith" },
            { source: "BERT", target: "GLUE", label: "trainedWith" },
            {
                source: "GLUE",
                target: "language understanding",
                label: "Benchmark-For",
            },
            {
                source: "BERT",
                target: "language understanding",
                label: "UsedFor",
            },
            { source: "BERT", target: "ELMo", label: "Compare-With" },
            {
                source: "question answering",
                target: "language understanding",
                label: "subtaskOf",
            },
            {
                source: "BERT",
                target: "F1 score",
                label: "MeasuredBy",
            },
            {
                source: "question answering",
                target: "F1 score",
                label: "evaluatedBy",
            },
        ],
    },
};

// ── state ─────────────────────────────────────────────────────────────────────
const activeDs = ref("gsap-ere");
const semanticLayout = ref(true); // default ON for consistent comparison
const graphRef = ref(null);

const current = computed(() => schemas[activeDs.value]);
const currentEntityTypes = computed(() => [
    ...new Set(current.value.nodes.map((n) => n.type)),
]);
const currentRelationTypes = computed(() => [
    ...new Set(current.value.edges.map((e) => e.label)),
]);

watch(
    activeDs,
    () => {
        for (const e of current.value.edges) relColor(e.label);
    },
    { immediate: true },
);

function toggleSemanticLayout() {
    graphRef.value?.clearPositions();
    semanticLayout.value = !semanticLayout.value;
}

// ── graph props ───────────────────────────────────────────────────────────────
const graphNodes = computed(() =>
    current.value.nodes.map((n) => {
        const fs = 11,
            w = Math.max(44, n.id.length * 6.0 + 10),
            h = Math.round(fs * 1.85);
        const node = { id: n.id, color: nodeColor(n.type), w, h, fontSize: fs };
        if (semanticLayout.value) {
            const anchor = (SCHEMA_ANCHORS[activeDs.value] ?? {})[n.type];
            if (anchor) {
                node.anchorX = anchor.ax;
                node.anchorY = anchor.ay;
                node.anchorStrength = 0.011;
            }
        }
        return node;
    }),
);

const graphEdges = computed(() =>
    current.value.edges.map((e) => {
        const edge = {
            id: `${e.source}|${e.label}|${e.target}`,
            source: e.source,
            target: e.target,
            label: e.label,
            color: relColor(e.label),
        };
        if (
            semanticLayout.value &&
            activeDs.value === "gsap-ere" &&
            GSAP_ATTR_RELS.has(e.label)
        ) {
            edge.springStrength = 4.5;
            edge.linkLengthFactor = 0.4;
        }
        return edge;
    }),
);
</script>
