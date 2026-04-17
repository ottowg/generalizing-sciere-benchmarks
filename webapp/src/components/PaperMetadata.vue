<template lang="pug">
v-container(fluid)
  .d-flex.align-center.mb-3
    h2.text-h5 {{ viewTitle }}
    v-chip.ml-3(v-if="meta" size="small" variant="tonal" color="grey") {{ meta.outlet_list.length }} outlets · {{ totalPapers }} papers
    v-spacer
    v-btn(variant="text" prepend-icon="mdi-refresh" size="small" :loading="building" @click="rebuild") Rebuild

  v-alert(v-if="error" type="error" density="compact" closable class="mb-3") {{ error }}
  v-progress-linear(v-if="loading" indeterminate class="mb-3")

  div(v-if="!meta && !loading && !error" class="text-center text-disabled py-8")
    | No data — click Rebuild to generate.

  div(v-if="meta")
    //- ── Publication Statistics ─────────────────────────────────────────────
    div(v-if="activeTab === 'datasets'")
      v-row.mb-2(dense)
        v-col(cols="12" md="6")
          v-card(variant="outlined")
            v-card-title.text-subtitle-1 Publication Years
            v-card-text(style="height:260px;")
              Bar(:data="yearChartData" :options="groupedBarOpts")
        v-col(cols="12" md="6")
          v-card(variant="outlined")
            v-card-title.text-subtitle-1 Citation Count Distribution
            v-card-subtitle.mt-n2(v-if="meta.citation_stats")
              | {{ meta.citation_stats.n }} / {{ meta.citation_stats.total }} papers with citations · median {{ meta.citation_stats.median }} · max {{ meta.citation_stats.max.toLocaleString() }}
            v-card-text(style="height:220px;")
              Bar(:data="citationChartData" :options="groupedBarOpts")

      v-row.mb-2(dense)
        v-col(cols="12" md="5")
          v-card(variant="outlined")
            v-card-title.text-subtitle-1 Outlet Types
            v-card-text(style="height:260px;")
              Bar(:data="outletTypeChartData" :options="groupedBarOpts")
        v-col(cols="12" md="7")
          v-card(variant="outlined")
            v-card-title.text-subtitle-1 Top Outlets
            v-card-text(style="height:260px;")
              Bar(:data="topOutletChartData" :options="groupedBarOpts")

      v-row.mb-2(dense)
        v-col(cols="12" md="8")
          v-card(variant="outlined")
            v-card-title.text-subtitle-1 Citations vs. Year
            v-card-text(style="height:300px;")
              Scatter(:data="scatterChartData" :options="scatterOpts")
        v-col(cols="12" md="4")
          v-card(variant="outlined")
            v-card-title.text-subtitle-1 Identifier Availability
            v-card-text(style="max-height:310px; overflow:auto;")
              v-table(density="compact" fixed-header)
                thead
                  tr
                    th Dataset
                    th.text-right N
                    th.text-right(v-for="col in meta.identifier_cols" :key="col") {{ col }}
                tbody
                  tr(v-for="row in meta.identifier_avail" :key="row.dataset")
                    td {{ row.dataset }}
                    td.text-right {{ row.n_papers }}
                    td.text-right(v-for="col in meta.identifier_cols" :key="col")
                      | {{ row[col]?.pct ?? '—' }}

      v-row.mb-2(v-if="meta.topics" dense)
        v-col(cols="12")
          v-card(variant="outlined")
            v-card-title.text-subtitle-1 Top OpenAlex Topics
            v-card-text(style="height:300px;")
              Bar(:data="topicsChartData" :options="groupedBarOptsRotated")

      div(v-if="meta.entities")
        v-card.mb-2(variant="outlined")
          v-card-title.text-subtitle-1 Entity Co-citation
          v-card-text
            v-btn-toggle(v-model="entityType" density="compact" divided mandatory)
              v-btn(value="Task" size="small") Task
              v-btn(value="Dataset" size="small") Dataset
              v-btn(value="Method" size="small") Method
          v-card-text(style="height:300px;")
            Bar(:data="entityChartData" :options="groupedBarOptsRotated")

      v-expansion-panels.mt-2(v-if="meta.arxiv_without_venue?.length" variant="accordion")
        v-expansion-panel
          v-expansion-panel-title arXiv / unmatched papers ({{ meta.arxiv_without_venue.length }})
          v-expansion-panel-text
            v-data-table(
              :headers="arxivHeaders" :items="meta.arxiv_without_venue"
              :items-per-page="20" density="compact" hover
            )
              template(#item.arxiv_id="{ item }")
                a(v-if="item.arxiv_id" :href="`https://arxiv.org/abs/${item.arxiv_id}`" target="_blank") {{ item.arxiv_id }}
                span(v-else) —

    //- ── Outlet List tab ────────────────────────────────────────────────────
    div(v-if="activeTab === 'outlets'")
      .d-flex.align-center.mb-3
        span.text-body-2.text-medium-emphasis
          | {{ meta.outlet_list_meta.n_enriched }} / {{ meta.outlet_list_meta.n_total }} outlets enriched with OpenAlex data

      v-card.mb-4(variant="outlined")
        v-card-title.text-subtitle-1 Publications per Outlet
        v-card-text(:style="`height:${Math.max(300, outletPubLabels.length * 18 + 60)}px;`")
          Bar(:data="outletPubsChartData" :options="outletPubsOpts")

      v-data-table(
        :headers="outletHeaders" :items="meta.outlet_list"
        :sort-by="[{ key: 'h_index', order: 'desc' }]"
        :items-per-page="30" density="compact" hover
      )
        template(#item.abbr="{ item }")
          a(v-if="item.openalex_url" :href="item.openalex_url" target="_blank") {{ item.abbr }}
          span(v-else) {{ item.abbr }}
        template(#item.h_index="{ item }") {{ item.h_index ?? '—' }}
        template(#item.i10_index="{ item }") {{ item.i10_index ?? '—' }}
        template(#item.citedness_2yr="{ item }") {{ item.citedness_2yr ?? '—' }}
        template(#item.papers_gsap_ere="{ item }")
          v-chip(v-if="item.papers_gsap_ere" size="x-small" color="#636EFA" variant="tonal") {{ item.papers_gsap_ere }}
          span(v-else) —
        template(#item.papers_scier="{ item }")
          v-chip(v-if="item.papers_scier" size="x-small" color="#EF553B" variant="tonal") {{ item.papers_scier }}
          span(v-else) —
        template(#item.papers_scinlp="{ item }")
          v-chip(v-if="item.papers_scinlp" size="x-small" color="#00CC96" variant="tonal") {{ item.papers_scinlp }}
          span(v-else) —

    //- ── Publication Map ────────────────────────────────────────────────────
    div(v-if="activeTab === 'pub-map' && meta.paper_map")

      p.text-body-2.text-medium-emphasis.mb-3
        | UMAP projection of Specter2 embeddings for the {{ meta.paper_map.points.length }} publications
        | across the three ERE datasets (GSAP, SciER, SciNLP). Each point represents one paper;
        | proximity reflects semantic similarity of research content.

      //- Controls row
      v-row.mb-2(dense align="center")
        v-col(cols="auto")
          v-btn-toggle(v-model="pubMapLayout" density="compact" divided mandatory)
            v-btn(value="umap" size="small") UMAP
            v-btn(value="knn" size="small") KNN
        v-col(cols="auto")
          v-select(
            v-model="pubMapColorBy"
            :items="pubMapColorByItems"
            label="Color by"
            density="compact" variant="outlined" hide-details
            style="min-width:160px;"
          )
        v-col(cols="auto" v-if="selectedDocIds.size")
          v-chip(
            size="small" color="primary" variant="tonal"
            closable @click:close="clearPubSelection"
          ) {{ selectedDocIds.size }} selected
        v-col(cols="auto" v-if="selectedDocIds.size")
          v-btn(size="small" variant="text" @click="clearPubSelection") Clear

      //- Map + stats side-by-side
      v-row(dense)
        //- SVG Map
        v-col(cols="12" md="8")
          v-card(variant="outlined")
            v-card-text.pa-1
              .position-relative(
                ref="pubMapContainer"
                style="height:560px; user-select:none; cursor:crosshair;"
              )
                svg(
                  ref="pubMapSvgEl"
                  viewBox="0 0 1000 620"
                  preserveAspectRatio="xMidYMid meet"
                  style="width:100%;height:100%;display:block;"
                  @mousedown.prevent="onMapDown"
                  @mousemove="onMapMove"
                  @mouseup="onMapUp"
                  @mouseleave="onMapLeave"
                )
                  //- Points per color group
                  g(v-for="(group, colorVal) in pubMapScaled.groups" :key="colorVal")
                    circle(
                      v-for="pt in group.points" :key="pt.doc_id"
                      :cx="pt.sx" :cy="pt.sy"
                      :r="pointRadius(pt)"
                      :fill="group.color"
                      stroke="white" :stroke-width="hoveredEntity && _entityFreq(pt) ? 1.5 : 0.8"
                      :opacity="pointOpacity(pt)"
                      style="transition:r 0.15s ease, opacity 0.15s ease;"
                      @mouseenter="onPointHover(pt, $event)"
                      @mouseleave="pubMapTooltip = null"
                    )
                  //- Live selection rect
                  rect(
                    v-if="selRect"
                    :x="selRect.x" :y="selRect.y"
                    :width="selRect.w" :height="selRect.h"
                    fill="rgba(99,110,250,0.08)"
                    stroke="#636EFA"
                    stroke-width="1.5"
                    stroke-dasharray="6,3"
                    pointer-events="none"
                  )

                //- Hover tooltip
                .position-absolute(
                  v-if="pubMapTooltip && !isDragging"
                  :style="pubMapTooltip.style"
                  style="background:rgba(20,20,20,0.9);color:#fff;padding:6px 10px;border-radius:5px;font-size:12px;pointer-events:none;z-index:20;max-width:300px;line-height:1.5;"
                )
                  div(style="font-weight:600;") {{ pubMapTooltip.title }}
                  div {{ pubMapTooltip.year }} · {{ pubMapTooltip.outlet_abbr || '—' }}
                  div.text-caption(style="opacity:.8;") {{ pubMapTooltip.dataset_detail }} · {{ pubMapTooltip.split }}

          //- Legend
          .d-flex.flex-wrap.mt-2(style="gap:10px;")
            .d-flex.align-center(v-for="(color, label) in pubMapScaled.colorMap" :key="label")
              span.rounded-circle.mr-1(:style="`width:9px;height:9px;background:${color};display:inline-block;flex-shrink:0;`")
              span.text-caption {{ label }}

        //- Stats panel
        v-col(cols="12" md="4")
          v-card(variant="outlined" style="min-height:560px;")
            v-card-title.text-subtitle-2.d-flex.align-center.pa-3
              span(v-if="selectedDocIds.size") {{ selectedDocIds.size }} selected papers
              span(v-else style="color:rgba(0,0,0,0.4);") Draw a rectangle to select papers
            v-divider
            v-card-text.pa-3

              //- Dataset distribution
              .text-caption.font-weight-medium.mb-1 Dataset
              .rounded.overflow-hidden.mb-1(style="display:flex;height:18px;")
                .h-100(
                  v-for="seg in datasetDist" :key="seg.label"
                  :style="`flex:${seg.pct};background:${seg.color};`"
                  :title="`${seg.label}: ${seg.count} (${seg.pct.toFixed(0)}%)`"
                )
              .d-flex.flex-wrap.mb-3(style="gap:6px;")
                .d-flex.align-center(v-for="seg in datasetDist" :key="seg.label")
                  span.rounded-circle.mr-1(:style="`width:7px;height:7px;background:${seg.color};display:inline-block;flex-shrink:0;`")
                  span.text-caption {{ seg.label }} ({{ seg.count }})

              //- Outlet distribution
              .text-caption.font-weight-medium.mb-1 Outlet
              .rounded.overflow-hidden.mb-1(style="display:flex;height:18px;")
                .h-100(
                  v-for="seg in outletDist" :key="seg.label"
                  :style="`flex:${seg.pct};background:${seg.color};`"
                  :title="`${seg.label}: ${seg.count} (${seg.pct.toFixed(0)}%)`"
                )
              .d-flex.flex-wrap.mb-3(style="gap:6px;")
                .d-flex.align-center(v-for="seg in outletDist" :key="seg.label")
                  span.rounded-circle.mr-1(:style="`width:7px;height:7px;background:${seg.color};display:inline-block;flex-shrink:0;`")
                  span.text-caption {{ seg.label }} ({{ seg.count }})

              //- Entity frequencies
              .text-caption.font-weight-medium.mb-1 Entities
              v-btn-toggle.mb-2(
                v-model="activeEntityType"
                density="compact" divided mandatory
              )
                v-btn(value="Task" size="x-small" :color="ENTITY_COLORS.Task") Task
                v-btn(value="Dataset" size="x-small" :color="ENTITY_COLORS.Dataset") Dataset
                v-btn(value="Method" size="x-small" :color="ENTITY_COLORS.Method") Method
              v-text-field(
                v-model="entityFilter[activeEntityType]"
                density="compact" variant="outlined" hide-details clearable
                :placeholder="`Filter ${activeEntityType}s…`"
                class="mb-2" style="font-size:12px;"
              )
              .entity-list(style="max-height:260px;overflow-y:auto;")
                .d-flex.align-center.px-1.py-1(
                  v-for="e in filteredEntities" :key="e.term"
                  style="gap:8px;border-bottom:1px solid rgba(0,0,0,.06);cursor:default;border-radius:3px;"
                  :style="hoveredEntity?.term === e.term ? `background:${ENTITY_COLORS[activeEntityType]}22;` : ''"
                  @mouseenter="hoveredEntity = { term: e.term, etype: activeEntityType }"
                  @mouseleave="hoveredEntity = null"
                )
                  .d-flex.flex-column.align-end(style="min-width:36px;flex-shrink:0;line-height:1.1;")
                    span(
                      style="font-size:12px;font-weight:600;"
                      :style="`color:${ENTITY_COLORS[activeEntityType]};`"
                    ) {{ e.docCount }}
                    span(style="font-size:10px;opacity:0.55;") {{ e.totalCount }}
                  span.text-caption {{ e.term }}
                .text-caption.text-disabled.mt-1(v-if="!filteredEntities.length") No results.

      //- ── Paper list ───────────────────────────────────────────────────────
      v-card.mt-3(variant="outlined")
        v-card-title.text-subtitle-2.d-flex.align-center.pa-3(style="min-height:40px;")
          span(v-if="checkedPaperIds.size")
            | {{ checkedPaperIds.size }} pinned
            v-btn.ml-2(size="x-small" variant="text" icon="mdi-close" @click="checkedPaperIds = new Set()")
          span(v-else-if="hoveredEntity")
            | {{ emphasizedPoints.length }} papers mentioning
            strong.mx-1 "{{ hoveredEntity.term }}"
            v-chip(size="x-small" :color="ENTITY_COLORS[hoveredEntity.etype]" variant="tonal") {{ hoveredEntity.etype }}
          span(v-else-if="selectedDocIds.size") {{ emphasizedPoints.length }} selected papers
          span(v-else) All {{ emphasizedPoints.length }} papers
          v-spacer
          span.text-caption.text-medium-emphasis.font-weight-regular sorted by citations
        v-divider
        div(style="max-height:320px;overflow-y:auto;")
          v-table(density="compact" fixed-header)
            thead
              tr
                th(style="width:32px;padding:0 8px;")
                  input(
                    type="checkbox"
                    :checked="allCurrentChecked"
                    ref="headerCheckboxRef"
                    @change="toggleAllCheck"
                    style="cursor:pointer;"
                  )
                th.text-right(style="width:32px;") #
                th Title
                th.text-right(style="width:48px;") Year
                th(style="width:60px;") Split
                th(style="width:80px;") Outlet
                th(style="width:88px;") Dataset
                th.text-right(style="width:72px;") Citations
            tbody
              tr(
                v-for="(pt, i) in emphasizedPoints" :key="pt.doc_id"
                :style="hoveredPaper?.doc_id === pt.doc_id ? 'background:rgba(99,110,250,0.08);' : ''"
                style="cursor:default;"
                @mouseenter="hoveredPaper = pt"
                @mouseleave="hoveredPaper = null"
              )
                td(style="padding:0 8px;")
                  input(
                    type="checkbox"
                    :checked="checkedPaperIds.has(pt.doc_id)"
                    @change.stop="togglePaperCheck(pt.doc_id)"
                    style="cursor:pointer;"
                  )
                td.text-right.text-caption.text-medium-emphasis {{ i + 1 }}
                td.text-caption(:title="pt.title") {{ pt.title?.length > 80 ? pt.title.slice(0, 80) + '…' : pt.title }}
                td.text-right.text-caption {{ pt.year ?? '—' }}
                td.text-caption
                  v-chip(size="x-small" variant="tonal") {{ pt.split || '—' }}
                td.text-caption {{ pt.outlet_abbr || '—' }}
                td
                  v-chip(
                    size="x-small"
                    :color="DATASET_COLORS[pt.dataset_detail] ?? '#888'"
                    variant="tonal"
                  ) {{ pt.dataset_detail }}
                td.text-right.text-caption {{ pt.cited_by_count != null ? Number(pt.cited_by_count).toLocaleString() : '—' }}

    div(v-else-if="activeTab === 'pub-map'" class="text-center text-disabled py-8")
      | No publication map data — click Rebuild.

    //- ── Outlet Map tab ─────────────────────────────────────────────────────
    div(v-if="activeTab === 'outlet-map' && meta.outlet_map")
      v-row.mb-2(dense align="center")
        v-col(cols="auto")
          v-select(
            v-model="outletMapColorBy"
            :items="[{ title: 'Outlet type', value: 'outlet_type' }, { title: 'Topic area', value: 'outlet_topic' }]"
            label="Color by" density="compact" variant="outlined" hide-details
            style="min-width:160px;"
          )
        v-col(cols="auto" style="min-width:200px;")
          v-slider(
            v-model="minOutletShared"
            :min="0" :max="maxOutletShared" :step="1"
            label="Min shared topics" density="compact" hide-details thumb-label
          )

      v-card(variant="outlined")
        v-card-text.pa-2
          .position-relative(ref="outletMapContainer" style="height:580px;")
            svg(
              viewBox="0 0 800 580"
              style="width:100%;height:100%;display:block;overflow:visible;"
            )
              line(
                v-for="(e, i) in outletMapScaled.edges" :key="i"
                :x1="e.x1" :y1="e.y1" :x2="e.x2" :y2="e.y2"
                stroke="rgb(150,150,150)"
                :stroke-opacity="e.opacity" :stroke-width="e.width"
              )
              g(
                v-for="pt in outletMapScaled.points" :key="pt.outlet_id"
                style="cursor:pointer;"
                @mouseenter="onOutletHover(pt, $event)"
                @mouseleave="outletTooltip = null"
              )
                circle(:cx="pt.sx" :cy="pt.sy" r="6" :fill="pt.color" stroke="white" stroke-width="1.5")
                text(
                  :x="pt.sx + 8" :y="pt.sy + 4"
                  font-size="9" fill="currentColor" opacity="0.75"
                  style="pointer-events:none;user-select:none;"
                ) {{ pt.abbr }}

            .position-absolute(
              v-if="outletTooltip"
              :style="outletTooltipStyle"
              style="background:rgba(30,30,30,0.92);color:#fff;padding:6px 10px;border-radius:5px;font-size:12px;pointer-events:none;z-index:20;max-width:300px;line-height:1.5;"
            )
              div(style="font-weight:600;") {{ outletTooltip.name }}
              div {{ outletTooltip.outlet_type }} · {{ outletTooltip.outlet_topic }}
              div H-index: {{ outletTooltip.h_index ?? '—' }} · {{ outletTooltip.papers_total }} papers
              div(v-if="outletTooltip.topics_preview" style="opacity:0.8;font-size:11px;margin-top:2px;") {{ outletTooltip.topics_preview }}

      .d-flex.flex-wrap.mt-2(style="gap:12px;")
        .d-flex.align-center(v-for="(color, label) in outletMapScaled.colorMap" :key="label")
          span.rounded-circle.mr-1(:style="`width:9px;height:9px;background:${color};display:inline-block;flex-shrink:0;`")
          span.text-caption {{ label }}

    div(v-else-if="activeTab === 'outlet-map'" class="text-center text-disabled py-8")
      | No outlet map data — click Rebuild.
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import {
  Chart as ChartJS,
  Title, Tooltip, Legend,
  BarElement, CategoryScale, LinearScale,
  PointElement, LogarithmicScale,
} from 'chart.js'
import { Bar, Scatter } from 'vue-chartjs'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, PointElement, LogarithmicScale)

// ── Palette ──────────────────────────────────────────────────────────────────

const DATASET_COLORS = {
  gsap_hf: '#636EFA', gsap_arxiv: '#19D3F3',
  scier: '#EF553B', scier_ood: '#FF9F1C', scinlp: '#00CC96',
}

const ENTITY_COLORS = { Task: '#b91c1c', Dataset: '#d97706', Method: '#2563eb' }

const PALETTE = [
  '#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A',
  '#19D3F3', '#FF6692', '#B6E880', '#FF97FF', '#FECB52',
  '#E45756', '#72B7B2', '#54A24B', '#EECA3B', '#B279A2',
  '#FF9DA6', '#9D755D', '#BAB0AC',
]

function buildColorMap(values) {
  const unique = [...new Set(values)].sort()
  return Object.fromEntries(unique.map((v, i) => [v, PALETTE[i % PALETTE.length]]))
}

// ── Props ─────────────────────────────────────────────────────────────────────

const props = defineProps({
  view: { type: String, default: 'metadata-pub-map' },
})

const VIEW_TO_TAB = {
  'metadata-pub-map':    'pub-map',
  'metadata-stats':      'datasets',
  'metadata-overview':   'outlets',
  'metadata-outlet-map': 'outlet-map',
}

const activeTab = computed(() => VIEW_TO_TAB[props.view] ?? 'pub-map')

const VIEW_TITLES = {
  'metadata-pub-map':    'Publication Map',
  'metadata-stats':      'Publication Statistics',
  'metadata-overview':   'Overview',
  'metadata-outlet-map': 'Outlet Map',
}
const viewTitle = computed(() => VIEW_TITLES[props.view] ?? 'Metadata')

// ── Core state ───────────────────────────────────────────────────────────────

const meta       = ref(null)
const loading    = ref(false)
const building   = ref(false)
const error      = ref(null)
const entityType = ref('Task')          // Publication Statistics entity toggle

// ── Publication map state ────────────────────────────────────────────────────

const pubMapContainer = ref(null)
const pubMapSvgEl     = ref(null)
const pubMapLayout    = ref('umap')
const pubMapColorBy   = ref('dataset_detail')
const pubMapTooltip   = ref(null)

const pubMapColorByItems = [
  { title: 'Dataset',     value: 'dataset_detail' },
  { title: 'Outlet type', value: 'outlet_type'    },
  { title: 'Topic area',  value: 'outlet_topic'   },
]

// Rectangle selection
const selStartPt  = ref(null)   // {x, y} in SVG viewBox coords
const selCurrentPt = ref(null)
const isDragging  = ref(false)
const selectedDocIds = ref(new Set())

// Stats state
const activeEntityType = ref('Task')
const entityFilter  = reactive({ Task: '', Dataset: '', Method: '' })
const hoveredEntity = ref(null)   // { term, etype } | null

// Paper list state
const hoveredPaper    = ref(null)   // point object | null (row hover → temporary drill-down)
const checkedPaperIds = ref(new Set())  // persistent multi-selection via checkboxes

// Outlet map state
const outletMapColorBy   = ref('outlet_type')
const minOutletShared    = ref(2)
const outletTooltip      = ref(null)
const outletMapContainer = ref(null)

// ── Misc computed ────────────────────────────────────────────────────────────

const totalPapers = computed(() => {
  if (!meta.value) return 0
  return meta.value.sub_datasets.reduce((s, ds) => {
    const arr = meta.value.by_year[ds.key]
    return s + (arr ? arr.reduce((a, b) => a + b, 0) : 0)
  }, 0)
})

// ── Bar chart helpers ────────────────────────────────────────────────────────

function makeBarData(labels, subDatasets, byDs) {
  return {
    labels,
    datasets: subDatasets.map(ds => ({
      label: ds.label, data: byDs[ds.key] ?? [], backgroundColor: ds.color,
    })),
  }
}

const groupedBarOpts = {
  responsive: true, maintainAspectRatio: false,
  plugins: { legend: { position: 'bottom', labels: { boxWidth: 12 } } },
  scales:  { x: { stacked: false }, y: { stacked: false, beginAtZero: true } },
}
const groupedBarOptsRotated = { ...groupedBarOpts, indexAxis: 'y' }

// ── ERE Datasets chart data ──────────────────────────────────────────────────

const yearChartData = computed(() => {
  if (!meta.value) return { labels: [], datasets: [] }
  return makeBarData(meta.value.years, meta.value.sub_datasets, meta.value.by_year)
})
const citationChartData = computed(() => {
  if (!meta.value) return { labels: [], datasets: [] }
  return makeBarData(meta.value.citation_labels, meta.value.sub_datasets, meta.value.by_citation)
})
const outletTypeChartData = computed(() => {
  if (!meta.value) return { labels: [], datasets: [] }
  return makeBarData(meta.value.outlet_types, meta.value.sub_datasets, meta.value.by_outlet_type)
})
const topOutletChartData = computed(() => {
  if (!meta.value) return { labels: [], datasets: [] }
  return makeBarData(meta.value.top_outlet_labels, meta.value.sub_datasets, meta.value.by_top_outlet)
})

const scatterOpts = {
  responsive: true, maintainAspectRatio: false,
  plugins: {
    legend: { position: 'bottom', labels: { boxWidth: 12 } },
    tooltip: { callbacks: { label: ctx => {
      const pt = ctx.raw
      return `${Math.round(pt.x)} — ${pt.y} citations${pt.title ? ': ' + pt.title : ''}`
    }}},
  },
  scales: {
    x: { title: { display: true, text: 'Year' } },
    y: { type: 'logarithmic', title: { display: true, text: 'Citations (log)' }, min: 1 },
  },
}
const scatterChartData = computed(() => {
  if (!meta.value) return { datasets: [] }
  return {
    datasets: meta.value.sub_datasets.map(ds => ({
      label: ds.label,
      data: (meta.value.scatter[ds.key] ?? []).filter(p => p.y > 0),
      backgroundColor: ds.color + 'AA', pointRadius: 3,
    })),
  }
})

const topicsChartData = computed(() => {
  if (!meta.value?.topics) return { labels: [], datasets: [] }
  const t = meta.value.topics
  return makeBarData(t.labels, t.sub_datasets, t.by_ds)
})
const entityChartData = computed(() => {
  if (!meta.value?.entities) return { labels: [], datasets: [] }
  const info = meta.value.entities.types[entityType.value]
  if (!info) return { labels: [], datasets: [] }
  return makeBarData(info.labels, meta.value.entities.sub_datasets, info.by_ds)
})

// ── Outlet publications chart ────────────────────────────────────────────────

const MAX_OUTLET_PUB = 40

const outletPubLabels = computed(() => {
  if (!meta.value) return []
  const labels = meta.value.outlet_pubs.labels
  return labels.length > MAX_OUTLET_PUB ? labels.slice(-MAX_OUTLET_PUB) : labels
})
const outletPubsChartData = computed(() => {
  if (!meta.value) return { labels: [], datasets: [] }
  const op = meta.value.outlet_pubs
  const start = Math.max(0, op.labels.length - MAX_OUTLET_PUB)
  return {
    labels: op.labels.slice(start),
    datasets: op.datasets.map(ds => ({
      label: ds, data: (op.by_ds[ds] ?? []).slice(start),
      backgroundColor: op.colors[ds], stack: 'stack',
    })),
  }
})
const outletPubsOpts = {
  responsive: true, maintainAspectRatio: false, indexAxis: 'y',
  plugins: { legend: { position: 'bottom', labels: { boxWidth: 12 } } },
  scales: { x: { stacked: true, beginAtZero: true }, y: { stacked: true } },
}

// ── Table headers ────────────────────────────────────────────────────────────

const outletHeaders = [
  { title: 'Abbr',      key: 'abbr',            sortable: true },
  { title: 'Name',      key: 'name',            sortable: true },
  { title: 'Type',      key: 'type',            sortable: true },
  { title: 'Topic',     key: 'topic',           sortable: true },
  { title: 'H-index',  key: 'h_index',         sortable: true, align: 'end' },
  { title: 'i10',      key: 'i10_index',       sortable: true, align: 'end' },
  { title: '2yr cite.', key: 'citedness_2yr',  sortable: true, align: 'end' },
  { title: 'Total',    key: 'papers_total',    sortable: true, align: 'end' },
  { title: 'GSAP',     key: 'papers_gsap_ere', sortable: true, align: 'end' },
  { title: 'SciER',    key: 'papers_scier',    sortable: true, align: 'end' },
  { title: 'SciNLP',   key: 'papers_scinlp',   sortable: true, align: 'end' },
]
const arxivHeaders = [
  { title: 'doc_id', key: 'doc_id', sortable: true },
  { title: 'dataset', key: 'dataset', sortable: true },
  { title: 'split',   key: 'split',   sortable: true },
  { title: 'title',   key: 'title',   sortable: true },
  { title: 'year',    key: 'year',    sortable: true, align: 'end' },
  { title: 'arXiv',   key: 'arxiv_id', sortable: true },
]

// ── Publication map (SVG) ────────────────────────────────────────────────────

const PUB_W = 1000, PUB_H = 620, PUB_PAD = 35

const pubMapScaled = computed(() => {
  if (!meta.value?.paper_map) return { groups: {}, points: [], colorMap: {} }
  const pts       = meta.value.paper_map.points
  const xKey      = pubMapLayout.value === 'umap' ? 'x_umap' : 'x_knn'
  const yKey      = pubMapLayout.value === 'umap' ? 'y_umap' : 'y_knn'
  const colorField = pubMapColorBy.value
  const useFix    = colorField === 'dataset_detail'

  const xs = pts.map(p => p[xKey]), ys = pts.map(p => p[yKey])
  const xMin = Math.min(...xs), xMax = Math.max(...xs)
  const yMin = Math.min(...ys), yMax = Math.max(...ys)
  const xRange = xMax - xMin || 1, yRange = yMax - yMin || 1

  const sx = x => PUB_PAD + (x - xMin) / xRange * (PUB_W - 2 * PUB_PAD)
  const sy = y => PUB_H - PUB_PAD - (y - yMin) / yRange * (PUB_H - 2 * PUB_PAD)

  const colorVals = pts.map(p => (p[colorField] ?? 'unknown').toString() || 'unknown')
  const dynMap    = useFix ? null : buildColorMap(colorVals)
  const colorMap  = useFix
    ? Object.fromEntries(
        [...new Set(colorVals)].map(v => [v, DATASET_COLORS[v] ?? '#888'])
      )
    : dynMap

  const groups = {}
  const points = pts.map((p, i) => {
    const cv    = colorVals[i]
    const color = (useFix ? DATASET_COLORS[cv] : dynMap[cv]) ?? '#888'
    if (!groups[cv]) groups[cv] = { color, points: [] }
    const scaled = { ...p, sx: sx(p[xKey]), sy: sy(p[yKey]), color, colorVal: cv }
    groups[cv].points.push(scaled)
    return scaled
  })

  return { groups, points, colorMap }
})

// Clear selection when layout changes (coords shift)
watch(pubMapLayout, () => { selectedDocIds.value = new Set() })

// Clear entity hover when tab switches (different term namespace)
watch(activeEntityType, () => { hoveredEntity.value = null })

// ── SVG mouse coordinate conversion ─────────────────────────────────────────

function svgCoords(event) {
  const svg = pubMapSvgEl.value
  if (!svg) return { x: 0, y: 0 }
  const pt = svg.createSVGPoint()
  pt.x = event.clientX
  pt.y = event.clientY
  const inv = svg.getScreenCTM()?.inverse()
  if (!inv) return { x: 0, y: 0 }
  const { x, y } = pt.matrixTransform(inv)
  return { x, y }
}

// ── Map mouse handlers ───────────────────────────────────────────────────────

function onMapDown(event) {
  if (event.button !== 0) return
  const pos = svgCoords(event)
  selStartPt.value   = pos
  selCurrentPt.value = pos
  isDragging.value   = true
}

function onMapMove(event) {
  if (!isDragging.value) return
  selCurrentPt.value = svgCoords(event)
}

function onMapUp() {
  if (!isDragging.value) return
  isDragging.value = false

  const s = selStartPt.value, c = selCurrentPt.value
  if (!s || !c) return

  const dx = Math.abs(c.x - s.x), dy = Math.abs(c.y - s.y)
  if (dx < 4 && dy < 4) {
    // Tiny drag → clear selection
    selectedDocIds.value = new Set()
  } else {
    const x0 = Math.min(s.x, c.x), x1 = Math.max(s.x, c.x)
    const y0 = Math.min(s.y, c.y), y1 = Math.max(s.y, c.y)
    selectedDocIds.value = new Set(
      pubMapScaled.value.points
        .filter(p => p.sx >= x0 && p.sx <= x1 && p.sy >= y0 && p.sy <= y1)
        .map(p => p.doc_id)
    )
  }
  selStartPt.value   = null
  selCurrentPt.value = null
}

function onMapLeave() {
  if (!isDragging.value) return
  isDragging.value   = false
  selStartPt.value   = null
  selCurrentPt.value = null
}

function clearPubSelection() {
  selectedDocIds.value = new Set()
}

// ── Point hover ──────────────────────────────────────────────────────────────

function onPointHover(pt, event) {
  if (isDragging.value) return
  if (!pubMapContainer.value) return
  const rect = pubMapContainer.value.getBoundingClientRect()
  const left = Math.min(event.clientX - rect.left + 14, rect.width - 310)
  const top  = Math.max(event.clientY - rect.top  - 14, 0)
  pubMapTooltip.value = { ...pt, style: `top:${top}px;left:${left}px;` }
}

// ── Selection rect (live, during drag) ──────────────────────────────────────

const selRect = computed(() => {
  if (!isDragging.value || !selStartPt.value || !selCurrentPt.value) return null
  const s = selStartPt.value, c = selCurrentPt.value
  return {
    x: Math.min(s.x, c.x),
    y: Math.min(s.y, c.y),
    w: Math.abs(c.x - s.x),
    h: Math.abs(c.y - s.y),
  }
})

// ── Point appearance (opacity + radius) ─────────────────────────────────────

const MIN_R = 5, MAX_R = 14, LOG_SCALE = 3.2

function _entityFreq(pt) {
  if (!hoveredEntity.value) return null
  const { term, etype } = hoveredEntity.value
  return meta.value?.paper_map?.entity_freq?.[pt.doc_id]?.[etype]?.[term] ?? null
}

function pointRadius(pt) {
  if (!hoveredEntity.value) return MIN_R
  const freq = _entityFreq(pt)
  if (!freq) return 2.5
  return Math.min(MAX_R, MIN_R + Math.log(freq + 1) * LOG_SCALE)
}

function pointOpacity(pt) {
  // Paper row hover → temporary single-paper emphasis (highest priority)
  if (hoveredPaper.value) {
    return hoveredPaper.value.doc_id === pt.doc_id ? 1.0 : 0.1
  }
  // Checked papers → persistent multi-selection
  if (checkedPaperIds.value.size) {
    return checkedPaperIds.value.has(pt.doc_id) ? 1.0 : 0.15
  }
  // Entity hover → size + opacity based on in-doc frequency
  if (hoveredEntity.value) {
    return _entityFreq(pt) ? 1.0 : 0.12
  }
  // Rectangle selection
  if (selectedDocIds.value.size) {
    return selectedDocIds.value.has(pt.doc_id) ? 1.0 : 0.18
  }
  return 0.85
}

// ── Stats computeds ──────────────────────────────────────────────────────────

const statsPoints = computed(() => {
  // Row-hover gives a temporary single-paper drill-down (highest priority)
  if (hoveredPaper.value) return [hoveredPaper.value]
  const pts = pubMapScaled.value.points
  if (checkedPaperIds.value.size) return pts.filter(p => checkedPaperIds.value.has(p.doc_id))
  if (selectedDocIds.value.size)  return pts.filter(p => selectedDocIds.value.has(p.doc_id))
  return pts
})

const datasetDist = computed(() => {
  const pts = statsPoints.value
  const counts = {}
  for (const pt of pts) {
    const k = pt.dataset_detail || 'unknown'
    counts[k] = (counts[k] ?? 0) + 1
  }
  const total = pts.length || 1
  return Object.entries(counts)
    .sort((a, b) => b[1] - a[1])
    .map(([label, count]) => ({
      label, count,
      pct: count / total * 100,
      color: DATASET_COLORS[label] ?? '#888',
    }))
})

const outletDist = computed(() => {
  const pts = statsPoints.value
  const counts = {}
  for (const pt of pts) {
    const k = pt.outlet_abbr || 'Unknown'
    counts[k] = (counts[k] ?? 0) + 1
  }
  const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1])
  const total  = pts.length || 1
  const top    = sorted.slice(0, 9)
  const otherN = sorted.slice(9).reduce((s, [, n]) => s + n, 0)
  const rows   = top.map(([label, count], i) => ({
    label, count, pct: count / total * 100, color: PALETTE[i % PALETTE.length],
  }))
  if (otherN) rows.push({ label: 'Other', count: otherN, pct: otherN / total * 100, color: '#ccc' })
  return rows
})

const entityFreqs = computed(() => {
  const pts = statsPoints.value
  const es  = meta.value?.paper_map?.entity_sets ?? {}
  const ef  = meta.value?.paper_map?.entity_freq ?? {}
  const result = {}
  for (const etype of ['Task', 'Dataset', 'Method']) {
    const docCount   = {}   // # papers (in selection) containing this entity
    const totalCount = {}   // total occurrences across those papers
    for (const pt of pts) {
      for (const ent of (es[pt.doc_id]?.[etype] ?? [])) {
        docCount[ent] = (docCount[ent] ?? 0) + 1
      }
      for (const [ent, cnt] of Object.entries(ef[pt.doc_id]?.[etype] ?? {})) {
        totalCount[ent] = (totalCount[ent] ?? 0) + cnt
      }
    }
    // Union of all entity terms seen in either set
    const allTerms = new Set([...Object.keys(docCount), ...Object.keys(totalCount)])
    result[etype] = [...allTerms]
      .map(term => ({
        term,
        docCount:   docCount[term]   ?? 0,
        totalCount: totalCount[term] ?? 0,
      }))
      .sort((a, b) => b.docCount - a.docCount || b.totalCount - a.totalCount)
  }
  return result
})

const filteredEntities = computed(() => {
  const etype = activeEntityType.value
  const q   = (entityFilter[etype] ?? '').toLowerCase()
  const all = entityFreqs.value[etype] ?? []
  const filtered = q ? all.filter(e => e.term.toLowerCase().includes(q)) : all
  return filtered.slice(0, 40)
})

// ── Paper list (emphasized = entity-hover or selection or all) ───────────────

const emphasizedPoints = computed(() => {
  // Checked papers take priority over entity/selection for the paper list
  const pts = pubMapScaled.value.points
  let subset

  if (checkedPaperIds.value.size) {
    subset = pts.filter(p => checkedPaperIds.value.has(p.doc_id))
  } else if (hoveredEntity.value) {
    const { term, etype } = hoveredEntity.value
    const ef = meta.value?.paper_map?.entity_freq ?? {}
    subset = pts.filter(p => ef[p.doc_id]?.[etype]?.[term])
  } else if (selectedDocIds.value.size) {
    subset = pts.filter(p => selectedDocIds.value.has(p.doc_id))
  } else {
    subset = pts
  }

  return [...subset].sort((a, b) => (b.cited_by_count ?? -1) - (a.cited_by_count ?? -1))
})

// Checkbox helpers
const headerCheckboxRef = ref(null)

function togglePaperCheck(docId) {
  const s = new Set(checkedPaperIds.value)
  s.has(docId) ? s.delete(docId) : s.add(docId)
  checkedPaperIds.value = s
}

const allCurrentChecked = computed(() =>
  emphasizedPoints.value.length > 0 &&
  emphasizedPoints.value.every(p => checkedPaperIds.value.has(p.doc_id))
)
const someCurrentChecked = computed(() =>
  !allCurrentChecked.value &&
  emphasizedPoints.value.some(p => checkedPaperIds.value.has(p.doc_id))
)

watch(someCurrentChecked, val => {
  if (headerCheckboxRef.value) headerCheckboxRef.value.indeterminate = val
})

function toggleAllCheck() {
  if (allCurrentChecked.value) {
    checkedPaperIds.value = new Set()
  } else {
    checkedPaperIds.value = new Set(emphasizedPoints.value.map(p => p.doc_id))
  }
}

// ── Outlet map ───────────────────────────────────────────────────────────────

const SVG_W = 800, SVG_H = 580, SVG_PAD = 48

const maxOutletShared = computed(() => {
  if (!meta.value?.outlet_map?.edges?.length) return 10
  return Math.max(...meta.value.outlet_map.edges.map(e => e.shared))
})

const outletMapScaled = computed(() => {
  if (!meta.value?.outlet_map) return { points: [], edges: [], colorMap: {} }
  const { points, edges } = meta.value.outlet_map

  const xs = points.map(p => p.x), ys = points.map(p => p.y)
  const xMin = Math.min(...xs), xMax = Math.max(...xs)
  const yMin = Math.min(...ys), yMax = Math.max(...ys)
  const xRange = xMax - xMin || 1, yRange = yMax - yMin || 1

  const sx = x => SVG_PAD + (x - xMin) / xRange * (SVG_W - 2 * SVG_PAD)
  const sy = y => SVG_H - SVG_PAD - (y - yMin) / yRange * (SVG_H - 2 * SVG_PAD)

  const colorField = outletMapColorBy.value
  const colorMap   = buildColorMap(points.map(p => p[colorField] ?? 'unknown'))

  const scaled = points.map((p, idx) => ({
    ...p, idx,
    sx:    sx(p.x), sy: sy(p.y),
    color: colorMap[p[colorField] ?? 'unknown'] ?? '#888',
  }))

  const minS = minOutletShared.value, maxS = maxOutletShared.value || 1
  const scaledEdges = edges
    .filter(e => e.shared >= minS)
    .map(e => {
      const pi = scaled[e.i], pj = scaled[e.j]
      const frac = e.shared / maxS
      return {
        x1: pi.sx, y1: pi.sy, x2: pj.sx, y2: pj.sy,
        opacity: 0.08 + frac * 0.35,
        width:   frac < 0.33 ? 0.5 : frac < 0.66 ? 1.2 : 2.0,
      }
    })

  return { points: scaled, edges: scaledEdges, colorMap }
})

function onOutletHover(pt, event) {
  if (!outletMapContainer.value) return
  const rect = outletMapContainer.value.getBoundingClientRect()
  outletTooltip.value = {
    ...pt,
    px: event.clientX - rect.left + 14,
    py: event.clientY - rect.top  - 14,
  }
}

const outletTooltipStyle = computed(() => {
  if (!outletTooltip.value) return ''
  const { px, py } = outletTooltip.value
  return `top:${py}px;left:${Math.min(px, SVG_W - 310)}px;`
})

// ── API ──────────────────────────────────────────────────────────────────────

async function load() {
  loading.value = true
  error.value   = null
  try {
    const r = await fetch('/api/paper-metadata')
    if (r.status === 404) { meta.value = null; return }
    if (!r.ok) throw new Error(`HTTP ${r.status}`)
    meta.value = await r.json()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function rebuild() {
  building.value = true
  error.value    = null
  try {
    const r = await fetch('/api/paper-metadata/build', { method: 'POST' })
    const d = await r.json()
    if (!d.ok) throw new Error(d.stderr || 'Build failed')
    await load()
  } catch (e) {
    error.value = e.message
  } finally {
    building.value = false
  }
}

onMounted(load)
</script>
