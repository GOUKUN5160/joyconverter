<script setup lang="ts">
import { defineProps } from 'vue';

const props = defineProps({
  value: { type: String, required: true },
  label: { type: String, required: true },
  modelValue: { type: String, required: true },
});

</script>

<template>
  <v-radio :label="props.label" :value="props.value"></v-radio>
  <div v-if="props.modelValue === props.value" class="ml-6">
    <slot></slot>
  </div>
</template>
