<template lang="pug">
v-container(fluid)
  .d-flex.align-center.mb-4
    h2.text-h5 Data Models — Relation Graph
    v-spacer
    v-btn-toggle(v-model="selectedExample" mandatory density="compact" variant="outlined" class="mr-2")
      v-btn(v-for="(ex, i) in examples" :key="i" :value="i" size="small") {{ ex.label }}
    v-btn(icon="mdi-restart" size="small" variant="text" title="Reset layout" @click="resetLayout")

  v-row
    v-col(cols="12" md="8")
      .graph-wrapper(
        ref="graphWrapper"
        style="height:520px;border:1px solid rgba(0,0,0,0.18);border-radius:8px;overflow:hidden;position:relative;"
      )
        svg(
          ref="svgEl"
          :width="svgW"
          :height="svgH"
          style="display:block;width:100%;height:100%;"
          @mousemove.prevent="onMouseMove"
          @mouseup="onMouseUp"
          @mouseleave="onMouseUp"
        )
          defs
            marker(
              id="rg-arrow"
              viewBox="0 -5 10 10"
              refX="12" refY="0"
              markerWidth="6" markerHeight="6"
              orient="auto"
            )
              path(d="M0,-5L10,0L0,5" fill="#999")

          //- Edges
          g(v-for="edge in simEdges" :key="edge.id")
            line(
              :x1="edge.sx" :y1="edge.sy"
              :x2="edge.tx" :y2="edge.ty"
              stroke="#aaa"
              :stroke-width="1.5"
              marker-end="url(#rg-arrow)"
            )
            text(
              :x="(edge.sx + edge.tx) / 2"
              :y="(edge.sy + edge.ty) / 2 - 6"
              text-anchor="middle"
              font-size="10"
              fill="#777"
              font-style="italic"
              pointer-events="none"
            ) {{ edge.label }}

          //- Nodes
          g(
            v-for="node in simNodes"
            :key="node.id"
            :transform="`translate(${Math.round(node.x)},${Math.round(node.y)})`"
            style="cursor:grab"
            @mousedown.prevent="startDrag(node, $event)"
          )
            rect(
              :x="-node.w / 2"
              :y="-node.h / 2"
              :width="node.w"
              :height="node.h"
              rx="4" ry="4"
              :fill="node.color"
              :stroke="node.isFocus ? '#fff' : 'transparent'"
              :stroke-width="node.isFocus ? 2 : 0"
              opacity="0.92"
            )
            text(
              text-anchor="middle"
              dominant-baseline="middle"
              :font-size="node.fontSize"
              fill="white"
              font-weight="bold"
              pointer-events="none"
            ) {{ node.id }}
            text(
              :y="node.h / 2 + 13"
              text-anchor="middle"
              font-size="10"
              :fill="node.color"
              pointer-events="none"
            ) {{ node.type }}

    v-col(cols="12" md="4")
      v-card(variant="outlined")
        v-card-text
          p.text-body-2.mb-3.font-italic "{{ examples[selectedExample].sentence }}"

          v-divider.mb-2

          p.text-caption.font-weight-bold.text-medium-emphasis.mb-1 ENTITIES
          .d-flex.flex-wrap.gap-1.mb-3
            v-chip(
              v-for="n in examples[selectedExample].nodes"
              :key="n.id"
              size="small"
              :style="`background:${typeColors[n.type]};color:white;`"
            ) {{ n.id }}
              span.ml-1(style="opacity:0.75;font-size:9px;") {{ n.type }}

          v-divider.mb-2

          p.text-caption.font-weight-bold.text-medium-emphasis.mb-1 RELATIONS
          v-list(density="compact" class="pa-0")
            v-list-item(
              v-for="e in examples[selectedExample].edges"
              :key="e.id"
              :prepend-icon="'mdi-arrow-right-thin'"
              density="compact"
              class="pa-0"
            )
              v-list-item-title(style="font-size:12px;")
                span(style="font-weight:600;") {{ e.source }}
                span.mx-1(style="color:#777;font-style:italic;") {{ e.label }}
                span(style="font-weight:600;") {{ e.target }}

          v-divider.mt-2.mb-2

          p.text-caption.text-medium-emphasis Legend
          .d-flex.flex-wrap.gap-1
            v-chip(
              v-for="(color, type) in typeColors"
              :key="type"
              size="x-small"
              :style="`background:${color};color:white;`"
            ) {{ type }}
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'

// ── color palette ────────────────────────────────────────────────────────────
const typeColors = {
  Method:  '#2563eb',
  Dataset: '#d97706',
  Metric:  '#15803d',
  Task:    '#b91c1c',
  Generic: '#6b7280',
  Focus:   '#374151',
}

function nodeColor(type, isFocus) {
  if (isFocus) return typeColors.Focus
  return typeColors[type] ?? typeColors.Generic
}

// ── example data ─────────────────────────────────────────────────────────────
const examples = [
  {
    label: 'NLP Benchmark',
    sentence: 'BERT achieves state-of-the-art results on the SQuAD reading comprehension benchmark, reaching an F1 score of 93.2.',
    focus: 'BERT',
    nodes: [
      { id: 'BERT',    type: 'Method'  },
      { id: 'SQuAD',   type: 'Dataset' },
      { id: 'F1',      type: 'Metric'  },
      { id: 'reading comprehension', type: 'Task' },
    ],
    edges: [
      { id: 'e1', source: 'BERT', label: 'used-for',  target: 'reading comprehension' },
      { id: 'e2', source: 'BERT', label: 'eval-on',   target: 'SQuAD'  },
      { id: 'e3', source: 'BERT', label: 'achieves',  target: 'F1'     },
      { id: 'e4', source: 'F1',   label: 'measures',  target: 'reading comprehension' },
    ],
  },
  {
    label: 'Computer Vision',
    sentence: 'ResNet-50 is pre-trained on ImageNet and fine-tuned for object detection, evaluated using mAP on COCO.',
    focus: 'ResNet-50',
    nodes: [
      { id: 'ResNet-50',        type: 'Method'  },
      { id: 'ImageNet',         type: 'Dataset' },
      { id: 'COCO',             type: 'Dataset' },
      { id: 'mAP',              type: 'Metric'  },
      { id: 'object detection', type: 'Task'    },
      { id: 'fine-tuning',      type: 'Generic' },
    ],
    edges: [
      { id: 'e1', source: 'ResNet-50',   label: 'trained-on', target: 'ImageNet'         },
      { id: 'e2', source: 'ResNet-50',   label: 'used-for',   target: 'object detection' },
      { id: 'e3', source: 'ResNet-50',   label: 'eval-on',    target: 'COCO'             },
      { id: 'e4', source: 'mAP',         label: 'measures',   target: 'object detection' },
      { id: 'e5', source: 'fine-tuning', label: 'applied-to', target: 'ResNet-50'        },
    ],
  },
  {
    label: 'Cross-dataset',
    sentence: 'A GSAP-trained model is evaluated on SciER and SciNLP, revealing label-space mismatches and annotation divergence.',
    focus: 'GSAP model',
    nodes: [
      { id: 'GSAP model',    type: 'Method'  },
      { id: 'GSAP',          type: 'Dataset' },
      { id: 'SciER',         type: 'Dataset' },
      { id: 'SciNLP',        type: 'Dataset' },
      { id: 'label mismatch',type: 'Generic' },
      { id: 'F1 macro',      type: 'Metric'  },
    ],
    edges: [
      { id: 'e1', source: 'GSAP model', label: 'trained-on', target: 'GSAP'          },
      { id: 'e2', source: 'GSAP model', label: 'eval-on',    target: 'SciER'         },
      { id: 'e3', source: 'GSAP model', label: 'eval-on',    target: 'SciNLP'        },
      { id: 'e4', source: 'GSAP model', label: 'achieves',   target: 'F1 macro'      },
      { id: 'e5', source: 'SciER',      label: 'causes',     target: 'label mismatch'},
      { id: 'e6', source: 'SciNLP',     label: 'causes',     target: 'label mismatch'},
    ],
  },
]

// ── sim state ─────────────────────────────────────────────────────────────────
const selectedExample = ref(0)
const graphWrapper    = ref(null)
const svgEl           = ref(null)
const svgW            = ref(600)
const svgH            = ref(520)

// Node simulation objects: { id, type, isFocus, x, y, vx, vy, w, h, fontSize, color }
const simNodes = ref([])
// Edge render objects: { id, source, target, label, sx, sy, tx, ty }
const simEdges = ref([])

let animFrame = null
let dragging  = null
let dragOffX  = 0
let dragOffY  = 0

// ── node geometry helpers ─────────────────────────────────────────────────────
function estimateWidth(text, fontSize) {
  return Math.max(60, text.length * fontSize * 0.62 + 20)
}

// ── build sim from example ────────────────────────────────────────────────────
function buildSim(exIdx) {
  const ex = examples[exIdx]
  const cx = svgW.value / 2
  const cy = svgH.value / 2
  const n  = ex.nodes.length

  const nodes = ex.nodes.map((nd, i) => {
    const isFocus  = nd.id === ex.focus
    const fontSize = isFocus ? 16 : 13
    const w        = estimateWidth(nd.id, fontSize)
    const h        = fontSize * 1.8
    // spread around center
    const angle    = (2 * Math.PI * i) / n
    const r        = 140
    return {
      id:      nd.id,
      type:    nd.type,
      isFocus,
      fontSize,
      w, h,
      color:   nodeColor(nd.type, isFocus),
      x:       isFocus ? cx : cx + r * Math.cos(angle),
      y:       isFocus ? cy : cy + r * Math.sin(angle),
      vx: 0, vy: 0,
    }
  })

  const nodeMap = Object.fromEntries(nodes.map(nd => [nd.id, nd]))

  const edges = ex.edges.map(e => ({
    id:     e.id,
    source: e.source,
    target: e.target,
    label:  e.label,
    sx: 0, sy: 0, tx: 0, ty: 0,
  }))

  simNodes.value = nodes
  simEdges.value = edges
  updateEdgePositions(nodeMap)
}

function updateEdgePositions(nodeMap) {
  const map = nodeMap ?? Object.fromEntries(simNodes.value.map(n => [n.id, n]))
  for (const e of simEdges.value) {
    const s = map[e.source]
    const t = map[e.target]
    if (!s || !t) continue
    // offset endpoints to edge of rect
    const dx  = t.x - s.x
    const dy  = t.y - s.y
    const len = Math.sqrt(dx * dx + dy * dy) || 1
    const ux  = dx / len
    const uy  = dy / len
    e.sx = s.x + ux * s.w / 2
    e.sy = s.y + uy * s.h / 2
    e.tx = t.x - ux * (t.w / 2 + 4)
    e.ty = t.y - uy * (t.h / 2 + 4)
  }
}

// ── force simulation ──────────────────────────────────────────────────────────
function tick() {
  const nodes   = simNodes.value
  const edges   = simEdges.value
  const cx      = svgW.value / 2
  const cy      = svgH.value / 2
  const charge  = 4000
  const spring  = 0.04
  const linkLen = 160
  const gravity = 0.008
  const damping = 0.82

  // Repulsion between all node pairs
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const a  = nodes[i]
      const b  = nodes[j]
      const dx = b.x - a.x
      const dy = b.y - a.y
      const d2 = dx * dx + dy * dy
      const d  = Math.sqrt(d2) || 1
      const f  = charge / d2
      a.vx -= f * dx / d
      a.vy -= f * dy / d
      b.vx += f * dx / d
      b.vy += f * dy / d
    }
  }

  // Spring forces along edges
  const nodeMap = Object.fromEntries(nodes.map(n => [n.id, n]))
  for (const e of edges) {
    const s = nodeMap[e.source]
    const t = nodeMap[e.target]
    if (!s || !t) continue
    const dx = t.x - s.x
    const dy = t.y - s.y
    const d  = Math.sqrt(dx * dx + dy * dy) || 1
    const f  = (d - linkLen) * spring
    s.vx += f * dx / d
    s.vy += f * dy / d
    t.vx -= f * dx / d
    t.vy -= f * dy / d
  }

  // Gravity toward center + integrate
  const padX = 60
  const padY = 40
  for (const n of nodes) {
    if (dragging && n.id === dragging.id) continue
    n.vx = (n.vx + (cx - n.x) * gravity) * damping
    n.vy = (n.vy + (cy - n.y) * gravity) * damping
    n.x = Math.max(padX + n.w / 2, Math.min(svgW.value - padX - n.w / 2, n.x + n.vx))
    n.y = Math.max(padY + n.h / 2, Math.min(svgH.value - padY - n.h / 2, n.y + n.vy))
  }

  updateEdgePositions()
  animFrame = requestAnimationFrame(tick)
}

function startSim() {
  if (animFrame) cancelAnimationFrame(animFrame)
  animFrame = requestAnimationFrame(tick)
}

function stopSim() {
  if (animFrame) cancelAnimationFrame(animFrame)
  animFrame = null
}

// ── drag ──────────────────────────────────────────────────────────────────────
function startDrag(node, event) {
  dragging = node
  const svg    = svgEl.value
  const pt     = svg.createSVGPoint()
  pt.x = event.clientX
  pt.y = event.clientY
  const svgPos = pt.matrixTransform(svg.getScreenCTM().inverse())
  dragOffX = node.x - svgPos.x
  dragOffY = node.y - svgPos.y
}

function onMouseMove(event) {
  if (!dragging) return
  const svg = svgEl.value
  const pt  = svg.createSVGPoint()
  pt.x = event.clientX
  pt.y = event.clientY
  const svgPos = pt.matrixTransform(svg.getScreenCTM().inverse())
  dragging.x = svgPos.x + dragOffX
  dragging.y = svgPos.y + dragOffY
  dragging.vx = 0
  dragging.vy = 0
  updateEdgePositions()
}

function onMouseUp() {
  dragging = null
}

// ── resize ────────────────────────────────────────────────────────────────────
let ro = null
function setupResize() {
  if (!graphWrapper.value) return
  ro = new ResizeObserver(entries => {
    const { width, height } = entries[0].contentRect
    svgW.value = Math.round(width)
    svgH.value = Math.round(height)
  })
  ro.observe(graphWrapper.value)
}

// ── reset ─────────────────────────────────────────────────────────────────────
function resetLayout() {
  buildSim(selectedExample.value)
}

// ── lifecycle ─────────────────────────────────────────────────────────────────
watch(selectedExample, (i) => {
  buildSim(i)
})

onMounted(async () => {
  await nextTick()
  setupResize()
  if (graphWrapper.value) {
    svgW.value = graphWrapper.value.offsetWidth
    svgH.value = graphWrapper.value.offsetHeight
  }
  buildSim(selectedExample.value)
  startSim()
})

onUnmounted(() => {
  stopSim()
  ro?.disconnect()
})
</script>
