<template lang="pug">
.verdict-form

  //- Level 1: Correct / Wrong / Uncertain
  .d-flex.flex-wrap.gap-2
    v-btn(
      v-for="v in TOP_OPTIONS" :key="v.value"
      size="small"
      :variant="topVerdict === v.value ? 'elevated' : 'tonal'"
      :color="topVerdict === v.value ? v.color : undefined"
      @click="topVerdict = v.value"
    ) {{ v.label }}

  //- Level 2: Which part is wrong?
  template(v-if="topVerdict === 'wrong'")

    //- Mention: flat single-level issue
    template(v-if="type === 'mentions'")
      .mt-3
        .text-caption.text-medium-emphasis.mb-1 What is wrong?
        .d-flex.flex-wrap.gap-2
          v-btn(
            v-for="o in MENTION_ISSUES" :key="o.value"
            size="x-small"
            :variant="mentionIssue === o.value ? 'elevated' : 'tonal'"
            :color="mentionIssue === o.value ? 'warning' : undefined"
            @click="mentionIssue = o.value"
          ) {{ o.label }}
        v-combobox.mt-2(
          v-if="mentionIssue === 'entity_label'"
          v-model="mentionCorrectLabel"
          :items="entityLabels"
          label="Correct label"
          density="compact"
          variant="outlined"
          hide-details
        )

    //- Relation: multi-part (subject / relation / object)
    template(v-else)
      .mt-3
        .text-caption.text-medium-emphasis.mb-1 What is wrong?
        v-chip-group(v-model="wrongParts" multiple)
          v-chip(value="subject"  filter label size="small") Subject
          v-chip(value="relation" filter label size="small") Relation
          v-chip(value="object"   filter label size="small") Object

    //- Subject detail
    template(v-if="type !== 'mentions' && wrongParts.includes('subject')")
      .mt-3.pl-3.border-s
        .text-caption.text-medium-emphasis.mb-1 Subject issue
        .d-flex.flex-wrap.gap-2
          v-btn(
            v-for="o in MENTION_ISSUES" :key="o.value"
            size="x-small"
            :variant="subjectIssue === o.value ? 'elevated' : 'tonal'"
            :color="subjectIssue === o.value ? 'warning' : undefined"
            @click="subjectIssue = o.value"
          ) {{ o.label }}
        v-combobox.mt-2(
          v-if="subjectIssue === 'entity_label'"
          v-model="subjectCorrectLabel"
          :items="entityLabels"
          label="Correct subject label"
          density="compact"
          variant="outlined"
          hide-details
        )

    //- Relation detail
    template(v-if="type !== 'mentions' && wrongParts.includes('relation')")
      .mt-3.pl-3.border-s
        .text-caption.text-medium-emphasis.mb-1 Relation issue
        v-chip-group(v-model="relationIssues" multiple selected-class="text-warning")
          v-chip(v-for="o in RELATION_ISSUES" :key="o.value" :value="o.value" filter label size="small") {{ o.label }}
        v-combobox.mt-2(
          v-if="relationIssues.includes('wrong_label')"
          v-model="relationCorrectLabel"
          :items="relationLabels"
          label="Correct relation label"
          density="compact"
          variant="outlined"
          hide-details
        )

    //- Object detail
    template(v-if="type !== 'mentions' && wrongParts.includes('object')")
      .mt-3.pl-3.border-s
        .text-caption.text-medium-emphasis.mb-1 Object issue
        .d-flex.flex-wrap.gap-2
          v-btn(
            v-for="o in MENTION_ISSUES" :key="o.value"
            size="x-small"
            :variant="objectIssue === o.value ? 'elevated' : 'tonal'"
            :color="objectIssue === o.value ? 'warning' : undefined"
            @click="objectIssue = o.value"
          ) {{ o.label }}
        v-combobox.mt-2(
          v-if="objectIssue === 'entity_label'"
          v-model="objectCorrectLabel"
          :items="entityLabels"
          label="Correct object label"
          density="compact"
          variant="outlined"
          hide-details
        )
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'

const props = defineProps({
  type:           { type: String, default: 'relations' },  // 'mentions' | 'relations'
  previous:       { type: Object, default: null },
  entityLabels:   { type: Array,  default: () => [] },
  relationLabels: { type: Array,  default: () => [] },
})

const emit = defineEmits(['update:modelValue'])

const TOP_OPTIONS = [
  { value: 'correct',   label: 'Correct',   color: 'success' },
  { value: 'wrong',     label: 'Wrong',     color: 'error'   },
  { value: 'uncertain', label: 'Uncertain', color: 'grey'    },
]

const MENTION_ISSUES = [
  { value: 'span',              label: 'Span'             },
  { value: 'entity_label',      label: 'Entity Label'     },
  { value: 'no_valid_mention',  label: 'No Valid Mention' },
]

const RELATION_ISSUES = [
  { value: 'wrong_label',       label: 'Wrong Label'       },
  { value: 'inverse_relation',  label: 'Inverse Relation'  },
  { value: 'no_valid_relation', label: 'No Valid Relation' },
]

const topVerdict           = ref(null)
const mentionIssue         = ref(null)
const mentionCorrectLabel  = ref('')
const wrongParts           = ref([])
const subjectIssue         = ref(null)
const subjectCorrectLabel  = ref('')
const relationIssues       = ref([])
const relationCorrectLabel = ref('')
const objectIssue          = ref(null)
const objectCorrectLabel   = ref('')

// Clear sub-state when a part is removed from wrongParts
watch(wrongParts, (next, prev) => {
  if (prev && !next.includes('subject'))  { subjectIssue.value = null;   subjectCorrectLabel.value  = '' }
  if (prev && !next.includes('relation')) { relationIssues.value = [];   relationCorrectLabel.value = '' }
  if (prev && !next.includes('object'))   { objectIssue.value = null;    objectCorrectLabel.value   = '' }
})
watch(mentionIssue,  v => { if (v !== 'entity_label') mentionCorrectLabel.value  = '' })
watch(subjectIssue,  v => { if (v !== 'entity_label') subjectCorrectLabel.value  = '' })
watch(relationIssues, v => { if (!v.includes('wrong_label')) relationCorrectLabel.value = '' })
watch(objectIssue,   v => { if (v !== 'entity_label') objectCorrectLabel.value   = '' })

// Build judgement; null = incomplete (disables save button in parent)
const judgement = computed(() => {
  if (!topVerdict.value) return null
  if (topVerdict.value !== 'wrong') return { top: topVerdict.value }

  // Mention path: single flat issue
  if (props.type === 'mentions') {
    if (!mentionIssue.value) return null
    const mention = { type: mentionIssue.value }
    if (mentionIssue.value === 'entity_label' && mentionCorrectLabel.value)
      mention.correctLabel = mentionCorrectLabel.value
    return { top: 'wrong', issues: { mention } }
  }

  if (!wrongParts.value.length) return null
  if (wrongParts.value.includes('subject')  && !subjectIssue.value)        return null
  if (wrongParts.value.includes('relation') && !relationIssues.value.length) return null
  if (wrongParts.value.includes('object')   && !objectIssue.value)          return null

  const issues = {}
  if (wrongParts.value.includes('subject')) {
    issues.subject = { type: subjectIssue.value }
    if (subjectIssue.value === 'entity_label' && subjectCorrectLabel.value)
      issues.subject.correctLabel = subjectCorrectLabel.value
  }
  if (wrongParts.value.includes('relation')) {
    issues.relation = { types: [...relationIssues.value] }
    if (relationIssues.value.includes('wrong_label') && relationCorrectLabel.value)
      issues.relation.correctLabel = relationCorrectLabel.value
  }
  if (wrongParts.value.includes('object')) {
    issues.object = { type: objectIssue.value }
    if (objectIssue.value === 'entity_label' && objectCorrectLabel.value)
      issues.object.correctLabel = objectCorrectLabel.value
  }
  return { top: 'wrong', issues }
})

watch(judgement, v => emit('update:modelValue', v), { immediate: true })

// Restore from a previous judgement on mount (parent uses :key to remount on sample change)
onMounted(() => {
  const p = props.previous
  if (!p) return
  topVerdict.value = p.top ?? null
  if (p.issues?.mention) {
    mentionIssue.value        = p.issues.mention.type ?? null
    mentionCorrectLabel.value = p.issues.mention.correctLabel ?? ''
  }
  if (p.issues && !p.issues.mention) {
    wrongParts.value = Object.keys(p.issues)
    if (p.issues.subject)  { subjectIssue.value  = p.issues.subject.type;  subjectCorrectLabel.value  = p.issues.subject.correctLabel  ?? '' }
    if (p.issues.relation) { relationIssues.value = p.issues.relation.types ?? []; relationCorrectLabel.value = p.issues.relation.correctLabel ?? '' }
    if (p.issues.object)   { objectIssue.value   = p.issues.object.type;   objectCorrectLabel.value   = p.issues.object.correctLabel   ?? '' }
  }
})
</script>
