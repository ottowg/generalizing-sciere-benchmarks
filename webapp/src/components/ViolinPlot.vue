<template lang="pug">
svg(:width="width" :height="height" style="overflow:visible")
  template(v-if="hasData")
    //- Violin body
    path(v-if="vPath" :d="vPath" :fill="color" opacity="0.55" :stroke="color" stroke-width="0.5" stroke-opacity="0.8")
    //- IQR box
    rect(
      :x="cx - halfW * 0.25"
      :y="Math.min(yQ1, yQ3)"
      :width="halfW * 0.5"
      :height="Math.max(Math.abs(yQ1 - yQ3), 1)"
      fill="white"
      fill-opacity="0.5"
      stroke="#444"
      stroke-width="0.7"
    )
    //- Median line
    line(
      :x1="cx - halfW * 0.38" :x2="cx + halfW * 0.38"
      :y1="yMedian" :y2="yMedian"
      stroke="#222" stroke-width="1.5"
    )
    //- Mean dot
    circle(:cx="cx" :cy="yMean" r="2.5" fill="#222")
    //- Y-axis extremes
    text(x="2" :y="padTop" font-size="7" fill="#999" dominant-baseline="hanging") {{ maxV }}
    text(x="2" :y="height - padBot" font-size="7" fill="#999" dominant-baseline="auto") {{ minV }}
  text(v-else :x="width/2" :y="height/2" text-anchor="middle" font-size="9" fill="#bbb") n/a
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data:   { type: Array,  default: () => [] },
  color:  { type: String, default: '#7c4dff' },
  width:  { type: Number, default: 84 },
  height: { type: Number, default: 130 },
})

const padTop = 8
const padBot = 8

const cx    = computed(() => props.width / 2)
const halfW = computed(() => props.width * 0.38)

const sorted  = computed(() => [...props.data].sort((a, b) => a - b))
const hasData = computed(() => sorted.value.length >= 3)

const minV = computed(() => sorted.value[0] ?? 0)
const maxV = computed(() => sorted.value[sorted.value.length - 1] ?? 1)

function yScale(v) {
  const range = Math.max(maxV.value - minV.value, 1)
  const plotH = props.height - padTop - padBot
  return padTop + plotH - ((v - minV.value) / range) * plotH
}

function quantile(p) {
  const idx = Math.floor(p * (sorted.value.length - 1))
  return sorted.value[idx]
}

const yQ1     = computed(() => yScale(quantile(0.25)))
const yQ3     = computed(() => yScale(quantile(0.75)))
const yMedian = computed(() => yScale(quantile(0.5)))
const yMean   = computed(() => {
  const mean = props.data.reduce((s, v) => s + v, 0) / props.data.length
  return yScale(mean)
})

// Epanechnikov kernel
function epanechnikov(bw) {
  return v => {
    const u = v / bw
    return Math.abs(u) <= 1 ? 0.75 * (1 - u * u) / bw : 0
  }
}

const vPath = computed(() => {
  if (!hasData.value) return null
  const data = sorted.value
  const range = maxV.value - minV.value
  if (range === 0) return null
  const bw = Math.max(range * 0.15, 0.5)
  const N  = 50
  const thresholds = Array.from({ length: N + 1 }, (_, i) => minV.value + (i / N) * range)
  const kernel = epanechnikov(bw)
  const density = thresholds.map(x => [x, data.reduce((s, v) => s + kernel(x - v), 0) / data.length])
  const maxD = Math.max(...density.map(d => d[1]))
  if (maxD === 0) return null
  const cxV = cx.value
  const hw  = halfW.value
  const right = density.map(([v, d]) => [cxV + (d / maxD) * hw, yScale(v)])
  const left  = [...right].reverse().map(([px, py]) => [cxV - (px - cxV), py])
  const pts   = [...right, ...left]
  return pts.map(([px, py], i) => `${i === 0 ? 'M' : 'L'}${px.toFixed(1)},${py.toFixed(1)}`).join('') + 'Z'
})
</script>
