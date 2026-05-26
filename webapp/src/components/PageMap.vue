<template lang="pug">
v-container(fluid style="max-width:900px;")
  h2.text-h5.mb-1 Page Map
  p.text-body-2.text-medium-emphasis.mb-5
    | UnifiedSciERE compares three scientific Entity and Relation Extraction datasets —
    | GSAP-ERE, SciER, and SciNLP — covering Machine Learning, NLP, Computer Vision, and related fields.
    | Use the sections below to find what you need.

  v-row(dense)
    //- ── Metadata ──────────────────────────────────────────────────────────
    v-col(cols="12" md="6")
      v-card(variant="outlined" class="mb-3")
        v-card-title.text-subtitle-1.d-flex.align-center(style="gap:8px;")
          v-icon(color="primary") mdi-database-outline
          | Metadata
        v-card-text.pa-0
          v-list(density="compact")
            v-list-item(
              prepend-icon="mdi-map-marker-path"
              title="Publication Map"
              subtitle="UMAP scatter of 260+ papers; colour by dataset, outlet, topic cluster, or split"
              @click="emit('set-view', 'metadata-pub-map')"
              style="cursor:pointer;"
            )
            v-list-item(
              prepend-icon="mdi-chart-bar"
              title="Publication Statistics"
              subtitle="Year distribution, citation counts, outlet types, top venues"
              @click="emit('set-view', 'metadata-stats')"
              style="cursor:pointer;"
            )
            v-list-item(
              prepend-icon="mdi-graph-outline"
              title="Outlet Map"
              subtitle="Force-directed graph of venues connected by shared papers"
              @click="emit('set-view', 'metadata-outlet-map')"
              style="cursor:pointer;"
            )
            v-list-item(
              prepend-icon="mdi-format-list-bulleted"
              title="Outlet Statistics"
              subtitle="Table of all publication venues with h-index, citation metrics, and paper counts"
              @click="emit('set-view', 'metadata-overview')"
              style="cursor:pointer;"
            )
            v-list-item(
              prepend-icon="mdi-chart-bubble"
              title="Topic Coverage"
              subtitle="Heatmap of topic clusters × dataset × split — shows which topics are dataset-specific"
              @click="emit('set-view', 'metadata-topic-distr')"
              style="cursor:pointer;"
            )
            v-list-item(
              prepend-icon="mdi-download-outline"
              title="Download"
              subtitle="Export paper metadata and outlet data as JSON or CSV"
              @click="emit('set-view', 'metadata-download')"
              style="cursor:pointer;"
            )

    //- ── Data Models ───────────────────────────────────────────────────────
    v-col(cols="12" md="6")
      v-card(variant="outlined" class="mb-3")
        v-card-title.text-subtitle-1.d-flex.align-center(style="gap:8px;")
          v-icon(color="primary") mdi-cube-outline
          | Data Models
        v-card-text.pa-0
          v-list(density="compact")
            v-list-item(
              prepend-icon="mdi-graph-outline"
              title="Relation Signatures"
              subtitle="Subject→Predicate→Object triples that actually occur in the data"
              @click="emit('set-view', 'quality-signatures')"
              style="cursor:pointer;"
            )
            v-list-item(
              prepend-icon="mdi-book-open-variant-outline"
              title="Schema Preview"
              subtitle="Browse entity and relation types per dataset"
              @click="emit('set-view', 'data-models-schema')"
              style="cursor:pointer;"
            )
            v-list-item(
              prepend-icon="mdi-label"
              title="Label Statistics"
              subtitle="Distribution and co-occurrence of entity/relation labels across datasets"
              @click="emit('set-view', 'unification-label-stats')"
              style="cursor:pointer;"
            )

    //- ── Unification ───────────────────────────────────────────────────────
    v-col(cols="12" md="6")
      v-card(variant="outlined" class="mb-3")
        v-card-title.text-subtitle-1.d-flex.align-center(style="gap:8px;")
          v-icon(color="primary") mdi-pipe
          | Unification
        v-card-text.pa-0
          v-list(density="compact")
            v-list-item(
              prepend-icon="mdi-pipe"
              title="Pipeline"
              subtitle="Step-by-step view of the label-mapping and correction pipeline"
              @click="emit('set-view', 'unification-pipeline')"
              style="cursor:pointer;"
            )
            v-list-item(
              prepend-icon="mdi-chart-bar"
              title="Retention Stats"
              subtitle="How many mentions/relations survive each unification step"
              @click="emit('set-view', 'unification-retention')"
              style="cursor:pointer;"
            )
            v-list-item(
              prepend-icon="mdi-table-arrow-right"
              title="Label Mapping"
              subtitle="Explicit mapping table from original dataset labels to the unified schema"
              @click="emit('set-view', 'unification-label-mapping')"
              style="cursor:pointer;"
            )

    //- ── Results ───────────────────────────────────────────────────────────
    v-col(cols="12" md="6")
      v-card(variant="outlined" class="mb-3")
        v-card-title.text-subtitle-1.d-flex.align-center(style="gap:8px;")
          v-icon(color="primary") mdi-chart-line
          | Results
        v-card-text.pa-0
          v-list(density="compact")
            v-list-item(
              prepend-icon="mdi-replay"
              title="Reproduce Results"
              subtitle="In-distribution model results vs. numbers reported in original papers"
              @click="emit('set-view', 'performance-reproduce')"
              style="cursor:pointer;"
            )
            v-list-item(
              prepend-icon="mdi-table-arrow-right"
              title="Cross-Dataset"
              subtitle="All train→test combinations evaluated in the unified label space"
              @click="emit('set-view', 'performance-cross-dataset')"
              style="cursor:pointer;"
            )
            v-list-item(
              prepend-icon="mdi-layers-triple-outline"
              title="MultiSciERE"
              subtitle="Multi-head models (trained on 2–3 datasets) vs. single-dataset baselines; radar Δ F1 charts"
              @click="emit('set-view', 'performance-multi-sciere')"
              style="cursor:pointer;"
            )
            v-list-item(
              prepend-icon="mdi-table-pivot"
              title="Confusion Matrices"
              subtitle="Label-level confusion across model/dataset combinations"
              @click="emit('set-view', 'performance-coreference')"
              style="cursor:pointer;"
            )

    //- ── Test Set Samples ──────────────────────────────────────────────────
    v-col(cols="12" md="6")
      v-card(variant="outlined" class="mb-3")
        v-card-title.text-subtitle-1.d-flex.align-center(style="gap:8px;")
          v-icon(color="primary") mdi-file-document-outline
          | Test Set Samples
        v-card-text.pa-0
          v-list(density="compact")
            v-list-item(
              prepend-icon="mdi-graph-outline"
              title="Graph View"
              subtitle="Force-directed entity–relation graph for individual test papers; filter by label"
              @click="emit('set-view', 'quality-example-paper')"
              style="cursor:pointer;"
            )
            v-list-item(
              prepend-icon="mdi-tag-multiple-outline"
              title="Entity View"
              subtitle="Search-engine-style cards for each entity type; hover to see source sentence"
              @click="emit('set-view', 'quality-example-paper')"
              style="cursor:pointer;"
            )
</template>

<script setup>
const emit = defineEmits(['set-view'])
</script>
