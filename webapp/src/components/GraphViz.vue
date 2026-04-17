<template lang="pug">
.gv-wrap(
  ref="wrapEl"
  :style="`height:${height};min-height:300px;border:1px solid rgba(0,0,0,0.15);border-radius:8px;overflow:hidden;position:relative;background:#fafafa;`"
)
  v-overlay(
    v-if="loading"
    :model-value="true"
    contained
    class="d-flex align-center justify-center"
  )
    v-progress-circular(indeterminate color="primary")

  svg(
    ref="svgEl"
    :width="svgW" :height="svgH"
    style="display:block;width:100%;height:100%;user-select:none;-webkit-user-select:none;"
    @mousemove.prevent="onMouseMove"
    @mouseup="onMouseUp"
    @mouseleave="onMouseUp"
  )
    defs
      marker(
        v-for="col in usedColors" :key="col"
        :id="`${markerId}-arr-${col.replace('#','')}`"
        viewBox="0 -5 10 10" refX="0" refY="0"
        markerWidth="10" markerHeight="10" markerUnits="userSpaceOnUse" orient="auto"
      )
        path(d="M0,-5L10,0L0,5" :fill="col")

    g(v-for="e in simEdges" :key="e.key")
      path(
        :d="e.path" :stroke="e.color" :stroke-width="e.strokeWidth"
        fill="none"
        :opacity="hoveredEdge && hoveredEdge !== e.key ? 0.2 : 0.72"
        :marker-end="`url(#${markerId}-arr-${e.color.replace('#','')})`"
        style="cursor:pointer"
        @mouseenter="hoveredEdge = e.key"
        @mouseleave="hoveredEdge = null"
      )
      text(
        v-if="e.count != null && hoveredEdge === e.key"
        :x="e.lx" :y="e.ly - 13"
        text-anchor="middle" dominant-baseline="middle"
        font-size="9" fill="#555"
        stroke="white" stroke-width="3" paint-order="stroke"
        pointer-events="none"
      ) {{ e.count.toLocaleString() }}
      text(
        v-if="!hoveredEdge || hoveredEdge === e.key"
        :x="e.lx" :y="e.ly"
        text-anchor="middle" dominant-baseline="middle"
        font-size="10" :fill="e.color" font-style="italic"
        stroke="white" stroke-width="3" paint-order="stroke"
        pointer-events="none"
      ) {{ e.label }}

    g(
      v-for="n in sortedNodes" :key="n.id"
      :transform="`translate(${Math.round(n.x)},${Math.round(n.y)})`"
      style="cursor:grab"
      @mouseenter="hoveredNodeId = n.id"
      @mouseleave="hoveredNodeId = null"
      @mousedown.prevent="startDrag(n, $event)"
    )
      rect(
        :x="-(hoveredNodeId === n.id && n.fullLabel ? n.fullW : n.w)/2"
        :y="-n.h/2"
        :width="hoveredNodeId === n.id && n.fullLabel ? n.fullW : n.w"
        :height="n.h"
        rx="4" ry="4" :fill="n.color" opacity="0.92"
      )
      text(
        text-anchor="middle" dominant-baseline="middle"
        :font-size="n.fontSize" :dy="n.fontSize * 0.15"
        fill="white" font-weight="bold" pointer-events="none"
      ) {{ hoveredNodeId === n.id && n.fullLabel ? n.fullLabel : (n.label ?? n.id).split('|')[0] }}

  //- Simulation controls
  .gv-controls(
    style="position:absolute;bottom:10px;left:12px;right:12px;display:flex;gap:24px;align-items:center;pointer-events:none;z-index:2;"
  )
    .ctrl-group(style="display:flex;align-items:center;gap:8px;pointer-events:auto;min-width:180px;")
      span.text-caption(style="white-space:nowrap;color:rgba(0,0,0,0.55);") Repulsion
      input(type="range" v-model.number="simRepulsion" min="500" max="50000" step="500" style="flex:1;")
      span.text-caption(style="width:38px;text-align:right;color:rgba(0,0,0,0.55);") {{ simRepulsion.toLocaleString() }}
    .ctrl-group(style="display:flex;align-items:center;gap:8px;pointer-events:auto;min-width:180px;")
      span.text-caption(style="white-space:nowrap;color:rgba(0,0,0,0.55);") Edge spread
      input(type="range" v-model.number="simEdgeSpread" min="5" max="80" step="1" style="flex:1;")
      span.text-caption(style="width:38px;text-align:right;color:rgba(0,0,0,0.55);") {{ simEdgeSpread }}px
    .ctrl-group(style="display:flex;align-items:center;gap:8px;pointer-events:auto;min-width:180px;")
      span.text-caption(style="white-space:nowrap;color:rgba(0,0,0,0.55);") Energy
      input(type="range" v-model.number="simEnergy" min="0" max="8" step="0.5" style="flex:1;")
      span.text-caption(style="width:38px;text-align:right;color:rgba(0,0,0,0.55);") {{ simEnergy }}
    button(
      @click="toggleFreeze"
      style="pointer-events:auto;padding:2px 10px;border:1px solid rgba(0,0,0,0.25);border-radius:4px;font-size:11px;background:rgba(255,255,255,0.85);cursor:pointer;white-space:nowrap;"
    ) {{ frozen ? '▶ Resume' : '⏸ Freeze' }}
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from "vue";

const props = defineProps({
    nodes: { type: Array, default: () => [] }, // [{ id, color, w, h, fontSize? }]
    edges: { type: Array, default: () => [] }, // [{ id?, source, target, label, color, strokeWidth?, count? }]
    height: { type: String, default: "580px" },
    markerId: { type: String, default: "gv" },
    loading: { type: Boolean, default: false },
});

const wrapEl = ref(null);
const svgEl = ref(null);
const svgW = ref(700);
const svgH = ref(560);
const simNodes    = ref([]);
const simEdges    = ref([]);
const hoveredEdge = ref(null);
const hoveredNodeId = ref(null);

// Render hovered node last so it appears on top in SVG paint order
const sortedNodes = computed(() => {
    if (!hoveredNodeId.value) return simNodes.value;
    const idx = simNodes.value.findIndex(n => n.id === hoveredNodeId.value);
    if (idx === -1) return simNodes.value;
    const arr = [...simNodes.value];
    arr.push(arr.splice(idx, 1)[0]);
    return arr;
});

const simRepulsion = ref(6000);
const simEdgeSpread = ref(22);
const simEnergy = ref(0);
const frozen = ref(false);

const posCache = new Map();

const usedColors = computed(() => [
    ...new Set(simEdges.value.map((e) => e.color)),
]);

function buildGraph() {
    if (!props.nodes.length) {
        simNodes.value = [];
        simEdges.value = [];
        return;
    }

    const cx = svgW.value / 2,
        cy = svgH.value / 2;
    const radius = Math.min(svgW.value, svgH.value) * 0.3;

    const nodes = props.nodes.map((n, i) => {
        const cached = posCache.get(n.id);
        const angle = (2 * Math.PI * i) / props.nodes.length - Math.PI / 2;
        const fs = n.fontSize ?? 11;
        // If an anchor is defined and there is no cached position, start near the
        // anchor region (with small jitter so clustered nodes don't stack exactly).
        let initX, initY;
        if (cached) {
            initX = cached.x;
            initY = cached.y;
        } else if (n.anchorX != null) {
            initX = n.anchorX * svgW.value + (Math.random() - 0.5) * 70;
            initY = n.anchorY * svgH.value + (Math.random() - 0.5) * 70;
        } else {
            initX = cx + radius * Math.cos(angle);
            initY = cy + radius * Math.sin(angle);
        }
        return {
            id: n.id,
            label: n.label,
            fullLabel: n.fullLabel ?? null,
            fullW: n.fullW ?? null,
            color: n.color,
            w: n.w,
            h: n.h,
            fontSize: fs,
            x: initX,
            y: initY,
            vx: 0,
            vy: 0,
            anchorX: n.anchorX,
            anchorY: n.anchorY,
            anchorStrength: n.anchorStrength,
        };
    });

    const pairGroups = new Map();
    for (const e of props.edges) {
        const key = `${e.source}__${e.target}`;
        if (!pairGroups.has(key)) pairGroups.set(key, []);
        pairGroups.get(key).push(e);
    }

    const edges = [];
    for (const [, grp] of pairGroups) {
        grp.forEach((e, idx) => {
            const offset =
                grp.length === 1
                    ? 0
                    : (idx - (grp.length - 1) / 2) * simEdgeSpread.value;
            edges.push({
                key: e.id ?? `${e.source}|${e.label}|${e.target}`,
                source: e.source,
                target: e.target,
                label: e.label,
                color: e.color,
                strokeWidth: e.strokeWidth ?? 1.8,
                count: e.count ?? null,
                springStrength: e.springStrength,
                linkLengthFactor: e.linkLengthFactor,
                offset,
                path: "",
                lx: 0,
                ly: 0,
            });
        });
    }

    simNodes.value = nodes;
    simEdges.value = edges;
    updatePaths(Object.fromEntries(nodes.map((n) => [n.id, n])));
}

// Returns the point on the surface of a rect (centred at cx,cy, half-extents
// hw×hh) in the direction (ux,uy) from the centre. Works for any aspect ratio.
function rectEdgePt(cx, cy, hw, hh, ux, uy) {
    const ax = Math.abs(ux), ay = Math.abs(uy);
    const sx = ax > 1e-9 ? hw / ax : Infinity;
    const sy = ay > 1e-9 ? hh / ay : Infinity;
    const s  = Math.min(sx, sy);
    return { x: cx + ux * s, y: cy + uy * s };
}

function updatePaths(nodeMap) {
    const map =
        nodeMap ?? Object.fromEntries(simNodes.value.map((n) => [n.id, n]));
    for (const e of simEdges.value) {
        const s = map[e.source],
            t = map[e.target];
        if (!s || !t) continue;
        if (e.source === e.target) {
            const r = 28 + e.offset;
            e.path = `M ${s.x} ${s.y - s.h / 2} A ${r} ${r} 0 1 1 ${s.x + 1} ${s.y - s.h / 2}`;
            e.lx = s.x + r + 10;
            e.ly = s.y - s.h / 2 - r;
            continue;
        }
        const dx = t.x - s.x, dy = t.y - s.y;
        const len = Math.sqrt(dx * dx + dy * dy) || 1;
        const ux = dx / len, uy = dy / len, px = -uy, py = ux;
        // Proper rectangle boundary intersection (works for any aspect ratio)
        const sp   = rectEdgePt(s.x, s.y,  s.w / 2, s.h / 2,  ux,  uy);
        const tp0  = rectEdgePt(t.x, t.y, t.w / 2, t.h / 2, -ux, -uy);
        // Path ends at the arrowhead BASE (refX=0). Arrowhead is 10px long (userSpaceOnUse),
        // so the tip will land 4px before the node edge (10px arrowhead + 4px gap = 14px offset).
        const tp   = { x: tp0.x - ux * 14, y: tp0.y - uy * 14 };
        const mx  = (sp.x + tp.x) / 2 + px * e.offset;
        const my  = (sp.y + tp.y) / 2 + py * e.offset;
        e.path = `M ${sp.x} ${sp.y} Q ${mx} ${my} ${tp.x} ${tp.y}`;
        e.lx = 0.25 * sp.x + 0.5 * mx + 0.25 * tp.x;
        e.ly = 0.25 * sp.y + 0.5 * my + 0.25 * tp.y;
    }
}

let animFrame = null,
    dragging = null,
    dragOffX = 0,
    dragOffY = 0;

function tick() {
    const nodes = simNodes.value;
    const cx = svgW.value / 2,
        cy = svgH.value / 2;
    const charge = simRepulsion.value;
    const spring = 0.015;
    const linkLen = Math.min(svgW.value, svgH.value) * 0.32;
    const gravity = 0.006,
        damping = 0.82;
    const energy = simEnergy.value;

    for (let i = 0; i < nodes.length; i++)
        for (let j = i + 1; j < nodes.length; j++) {
            const a = nodes[i],
                b = nodes[j];
            const dx = b.x - a.x,
                dy = b.y - a.y,
                d = Math.sqrt(dx * dx + dy * dy) || 1;
            const f = charge / (d * d);
            a.vx -= (f * dx) / d;
            a.vy -= (f * dy) / d;
            b.vx += (f * dx) / d;
            b.vy += (f * dy) / d;
        }

    const map = Object.fromEntries(nodes.map((n) => [n.id, n]));
    for (const e of simEdges.value) {
        if (e.source === e.target) continue;
        const s = map[e.source],
            t = map[e.target];
        if (!s || !t) continue;
        const dx = t.x - s.x,
            dy = t.y - s.y,
            d = Math.sqrt(dx * dx + dy * dy) || 1;
        const eLinkLen = linkLen * (e.linkLengthFactor ?? 1.0);
        const eSpring = spring * (e.springStrength ?? 1.0);
        const f = (d - eLinkLen) * eSpring;
        s.vx += (f * dx) / d;
        s.vy += (f * dy) / d;
        t.vx -= (f * dx) / d;
        t.vy -= (f * dy) / d;
    }

    // Bounding-box separation: push nodes apart when they overlap
    const SEP = 6; // minimum gap (px) between node edges
    for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
            const a = nodes[i], b = nodes[j];
            const dx = b.x - a.x, dy = b.y - a.y;
            const minW = (a.w + b.w) / 2 + SEP;
            const minH = (a.h + b.h) / 2 + SEP;
            if (Math.abs(dx) < minW && Math.abs(dy) < minH) {
                // Resolve on the axis with smaller overlap to minimise disturbance
                const ovX = minW - Math.abs(dx);
                const ovY = minH - Math.abs(dy);
                if (ovX < ovY) {
                    const push = ovX * 0.5;
                    const dir  = dx >= 0 ? 1 : -1;
                    a.vx -= dir * push; b.vx += dir * push;
                } else {
                    const push = ovY * 0.5;
                    const dir  = dy >= 0 ? 1 : -1;
                    a.vy -= dir * push; b.vy += dir * push;
                }
            }
        }
    }

    const padX = 80,
        padY = 40;
    for (const n of nodes) {
        if (dragging && n.id === dragging.id) continue;
        // Use anchor force when provided, otherwise gravity toward center
        let gx, gy;
        if (n.anchorX != null) {
            const str = n.anchorStrength ?? 0.01;
            gx = str * (n.anchorX * svgW.value - n.x);
            gy = str * (n.anchorY * svgH.value - n.y);
        } else {
            gx = (cx - n.x) * gravity;
            gy = (cy - n.y) * gravity;
        }
        n.vx = (n.vx + gx + (Math.random() - 0.5) * energy) * damping;
        n.vy = (n.vy + gy + (Math.random() - 0.5) * energy) * damping;
        n.x = Math.max(
            padX + n.w / 2,
            Math.min(svgW.value - padX - n.w / 2, n.x + n.vx),
        );
        n.y = Math.max(
            padY + n.h / 2,
            Math.min(svgH.value - padY - n.h / 2, n.y + n.vy),
        );
        posCache.set(n.id, { x: n.x, y: n.y });
    }
    updatePaths();
    animFrame = requestAnimationFrame(tick);
}

function startSim() {
    if (animFrame) cancelAnimationFrame(animFrame);
    animFrame = requestAnimationFrame(tick);
}
function stopSim() {
    if (animFrame) {
        cancelAnimationFrame(animFrame);
        animFrame = null;
    }
}
function toggleFreeze() {
    frozen.value = !frozen.value;
    if (frozen.value) stopSim();
    else startSim();
}

function startDrag(node, evt) {
    dragging = node;
    const pt = svgEl.value.createSVGPoint();
    pt.x = evt.clientX;
    pt.y = evt.clientY;
    const p = pt.matrixTransform(svgEl.value.getScreenCTM().inverse());
    dragOffX = node.x - p.x;
    dragOffY = node.y - p.y;
}
function onMouseMove(evt) {
    if (!dragging) return;
    const pt = svgEl.value.createSVGPoint();
    pt.x = evt.clientX;
    pt.y = evt.clientY;
    const p = pt.matrixTransform(svgEl.value.getScreenCTM().inverse());
    dragging.x = p.x + dragOffX;
    dragging.y = p.y + dragOffY;
    dragging.vx = 0;
    dragging.vy = 0;
    updatePaths();
}
function onMouseUp() {
    dragging = null;
}

let ro = null;
onMounted(async () => {
    await nextTick();
    ro = new ResizeObserver((e) => {
        svgW.value = Math.round(e[0].contentRect.width);
        svgH.value = Math.round(e[0].contentRect.height);
    });
    ro.observe(wrapEl.value);
    svgW.value = wrapEl.value.offsetWidth;
    svgH.value = wrapEl.value.offsetHeight;
    buildGraph();
    startSim();
});
onUnmounted(() => {
    stopSim();
    ro?.disconnect();
});

watch([() => props.nodes, () => props.edges], () => buildGraph());
watch(simEdgeSpread, () => buildGraph());

defineExpose({ clearPositions: () => posCache.clear() });
</script>
