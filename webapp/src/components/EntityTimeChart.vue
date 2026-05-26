<template lang="pug">
div
  Bar(:data="chartData" :options="chartOptions" style="max-height:400px")
</template>

<script setup>
import { ref, computed } from 'vue'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, BarElement,
  Title, Tooltip, Legend,
} from 'chart.js'
import { entityColor } from '../utils/entityColors.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const props = defineProps({
  // { year_str: { n_papers, total_mean, by_label: { label: mean } } }
  byYear:   { type: Object,   required: true },
  colorFn:  { type: Function, default: entityColor },
  yLabel:   { type: String,   default: 'Mean count per paper' },
})

const hoveredIndex = ref(null)

const years = computed(() => Object.keys(props.byYear).sort())

const allLabels = computed(() => {
  const s = new Set()
  for (const y of Object.values(props.byYear))
    for (const lbl of Object.keys(y.by_label)) s.add(lbl)
  return [...s].sort()
})

const xLabels = computed(() =>
  years.value.map(y => {
    const n = props.byYear[y]?.n_papers ?? 0
    return `${y} (n=${n})`
  })
)

const chartData = computed(() => ({
  labels: xLabels.value,
  datasets: allLabels.value.map((lbl, i) => {
    const dimmed = hoveredIndex.value !== null && hoveredIndex.value !== i
    return {
      label: lbl,
      data: years.value.map(y => props.byYear[y]?.by_label?.[lbl] ?? 0),
      backgroundColor: props.colorFn(lbl) + (dimmed ? '28' : 'bb'),
      borderColor:     props.colorFn(lbl) + (dimmed ? '44' : 'ff'),
      borderWidth: 1,
      borderRadius: 2,
    }
  }),
}))

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: true,
  interaction: { mode: 'index', intersect: false },
  plugins: {
    legend: {
      position: 'top',
      labels: { boxWidth: 12, font: { size: 11 } },
      onHover(event, legendItem) {
        hoveredIndex.value = legendItem.datasetIndex
        if (event.native?.target) event.native.target.style.cursor = 'pointer'
      },
      onLeave(event) {
        hoveredIndex.value = null
        if (event.native?.target) event.native.target.style.cursor = 'default'
      },
    },
    tooltip: {
      callbacks: {
        title: (items) => items[0]?.label ?? '',
        label: (ctx) => ` ${ctx.dataset.label}: ${ctx.parsed.y?.toFixed(1) ?? '–'}`,
      },
    },
  },
  scales: {
    x: { ticks: { font: { size: 10 }, maxRotation: 45 } },
    y: {
      title: { display: true, text: props.yLabel, font: { size: 11 } },
      beginAtZero: true,
    },
  },
}))
</script>
