<template lang="pug">
.d-flex.flex-column
  .text-caption.text-medium-emphasis.mb-1(v-if="label") {{ label }}
  v-btn-toggle(
    :model-value="modelValue"
    :mandatory="mandatory"
    density="compact"
    variant="outlined"
    :color="color"
    @update:model-value="emit('update:modelValue', $event)"
  )
    v-btn(
      v-for="item in normalizedItems"
      :key="item.value"
      :value="item.value"
      size="small"
    ) {{ item.title }}
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label:      { type: String,          default: '' },
  modelValue: { type: [String, Number], default: null },
  items:      { type: Array,           default: () => [] },
  color:      { type: String,          default: 'primary' },
  mandatory:  { type: Boolean,         default: true },
})
const emit = defineEmits(['update:modelValue'])

const normalizedItems = computed(() =>
  props.items.map(i => typeof i === 'string' ? { title: i, value: i } : i)
)
</script>
