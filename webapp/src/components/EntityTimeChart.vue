<template lang="pug">
div
  Line(:data="chartData" :options="chartOptions" style="max-height:380px")
</template>

<script setup>
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, PointElement, LineElement,
  Title, Tooltip, Legend, Filler,
} from 'chart.js'
import { entityColor } from '../utils/entityColors.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

const props = defineProps({
  // { year_str: { n_papers, total_mean, by_label: { label: mean } } }
  byYear: { type: Object, required: true },
  showTotal: { type: Boolean, default: true },
})

const TOTAL_COLOR = '#374151'

const labels = computed(() => Object.keys(props.byYear).sort())

const allLabels = computed(() => {
  const s = new Set()
  for (const y of Object.values(props.byYear))
    for (const lbl of Object.keys(y.by_label)) s.add(lbl)
  return [...s].sort()
})

const xLabels = computed(() =>
  labels.value.map(y => {
    const n = props.byYear[y]?.n_papers ?? 0
    return `${y} (n=${n})`
  })
)

const chartData = computed(() => {
  const datasets = allLabels.value.map(lbl => ({
    label: lbl,
    data: labels.value.map(y => props.byYear[y]?.by_label?.[lbl] ?? null),
    borderColor: entityColor(lbl),
    backgroundColor: entityColor(lbl) + '22',
    tension: 0.3,
    pointRadius: 4,
    pointHoverRadius: 6,
    spanGaps: true,
  }))

  if (props.showTotal) {
    datasets.unshift({
      label: 'Total',
      data: labels.value.map(y => props.byYear[y]?.total_mean ?? null),
      borderColor: TOTAL_COLOR,
      backgroundColor: TOTAL_COLOR + '18',
      borderWidth: 2,
      tension: 0.3,
      pointRadius: 4,
      pointHoverRadius: 6,
      spanGaps: true,
    })
  }

  return { labels: xLabels.value, datasets }
})

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: true,
  interaction: { mode: 'index', intersect: false },
  plugins: {
    legend: { position: 'top', labels: { boxWidth: 12, font: { size: 11 } } },
    tooltip: {
      callbacks: {
        title: (items) => items[0]?.label ?? '',
        label: (ctx) => ` ${ctx.dataset.label}: ${ctx.parsed.y?.toFixed(1) ?? '–'}`,
      },
    },
  },
  scales: {
    x: {
      ticks: { font: { size: 10 }, maxRotation: 45 },
    },
    y: {
      title: { display: true, text: 'Mean entities per paper', font: { size: 11 } },
      beginAtZero: true,
    },
  },
}))
</script>
