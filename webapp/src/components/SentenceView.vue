<template lang="pug">
.sentence-view
  .sentence-text.text-body-1.py-3.px-1(style="line-height: 2.2; word-spacing: 2px")
    template(v-for="(seg, i) in segments" :key="i")
      span(v-if="i > 0 && !isPunct(seg.tokens[0])") &nbsp;
      //- Plain text
      span(v-if="seg.role === 'text'") {{ seg.tokens.join(' ') }}
      //- Annotated span
      span.annotated-span(
        v-else
        :class="spanClass(seg.role)"
        :title="seg.label"
      )
        span.span-text {{ seg.tokens.join(' ') }}
        span.span-label
          span.span-role(v-if="seg.role === 'subject'") SUBJ&nbsp;·&nbsp;
          span.span-role(v-else-if="seg.role === 'object'") OBJ&nbsp;·&nbsp;
          | {{ seg.label }}

  //- Mention summary (single-span annotation)
  .mention-arc.d-flex.align-center.gap-2.mt-2.px-1(v-if="isMention")
    v-chip(label size="small" color="primary" variant="tonal")
      | {{ sample.label }}: "{{ sample.text }}"

  //- Relation arc (subject → label → object)
  .relation-arc.d-flex.align-center.gap-2.mt-2.px-1(v-else-if="sample.subject")
    v-chip(label size="small" :color="SUBJECT_COLOR" variant="tonal")
      | {{ sample.subject.label }}: "{{ sample.subject.text }}"
    .arc-line.flex-grow-0.text-caption.text-medium-emphasis.mx-2
      | ──&nbsp;{{ sample.label }}&nbsp;──▶
    v-chip(label size="small" :color="OBJECT_COLOR" variant="tonal")
      | {{ sample.object.label }}: "{{ sample.object.text }}"
</template>

<script setup>
import { computed } from 'vue'

const SUBJECT_COLOR = 'blue'
const OBJECT_COLOR = 'green'

const props = defineProps({
  sample: { type: Object, required: true },
})

const PUNCT = new Set(['.', ',', '!', '?', ';', ':', ')', ']', '}', "'s", "n't", "'re", "'ve", "'ll", "'d"])
function isPunct(token) { return PUNCT.has(token) }

const isMention = computed(() => !props.sample?.subject)

const segments = computed(() => {
  if (!props.sample) return []
  const { sentence, tokens: rawTokens, subject, object, begin_token, end_token, label, context_spans = [] } = props.sample
  const tokens = (rawTokens && rawTokens.length) ? rawTokens : sentence.split(' ')

  // Per-token role assignment (text < context < object < subject)
  const roles = tokens.map(() => ({ role: 'text', label: '' }))

  for (const span of context_spans) {
    for (let i = span.begin_token; i <= span.end_token; i++) {
      if (i < tokens.length) roles[i] = { role: 'context', label: span.label }
    }
  }

  if (subject) {
    for (let i = object.begin_token; i <= object.end_token; i++) {
      if (i < tokens.length) roles[i] = { role: 'object', label: object.label }
    }
    for (let i = subject.begin_token; i <= subject.end_token; i++) {
      if (i < tokens.length) roles[i] = { role: 'subject', label: subject.label }
    }
  } else {
    for (let i = begin_token; i <= end_token; i++) {
      if (i < tokens.length) roles[i] = { role: 'subject', label }
    }
  }

  // Group consecutive tokens with same role+label into segments
  const segs = []
  for (let i = 0; i < tokens.length; i++) {
    const { role, label } = roles[i]
    const last = segs[segs.length - 1]
    if (last && last.role === role && last.label === label) {
      last.tokens.push(tokens[i])
    } else {
      segs.push({ role, label, tokens: [tokens[i]] })
    }
  }
  return segs
})

function spanClass(role) {
  return {
    'span-subject': role === 'subject',
    'span-object': role === 'object',
    'span-context': role === 'context',
  }
}
</script>

<style scoped>
.annotated-span {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  vertical-align: bottom;
  border-radius: 3px;
  padding: 1px 3px 0;
  line-height: 1.4;
}
.span-text {
  display: block;
}
.span-label {
  display: block;
  font-size: 0.6rem;
  font-weight: 600;
  letter-spacing: 0.03em;
  line-height: 1;
  padding-bottom: 2px;
  opacity: 0.85;
  white-space: nowrap;
}
.span-subject {
  background-color: rgba(var(--v-theme-primary), 0.18);
  border-bottom: 2px solid rgb(var(--v-theme-primary));
}
.span-subject .span-label { color: rgb(var(--v-theme-primary)); }
.span-role { opacity: 0.7; }

.span-object {
  background-color: rgba(25, 160, 100, 0.15);
  border-bottom: 2px solid rgb(25, 160, 100);
}
.span-object .span-label { color: rgb(25, 160, 100); }

.span-context {
  background-color: rgba(0, 0, 0, 0.06);
  border-bottom: 1px solid rgba(0, 0, 0, 0.2);
  opacity: 0.6;
}
.span-context .span-label { color: rgba(0, 0, 0, 0.4); }
</style>
