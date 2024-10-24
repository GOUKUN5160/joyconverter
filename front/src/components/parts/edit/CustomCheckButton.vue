<script setup lang="ts">
import { defineProps, defineEmits } from 'vue';
const emit = defineEmits(["update:modelValue"]);

const props = defineProps({
  label: { type: String, required: true },
  value: { type: String, required: true },
  modelValue: { type: Array<String>, required: true },
});
</script>

<template>
  <v-selection-control-group v-model="props.modelValue"
    @update:model-value="emit('update:modelValue', props.modelValue)">
    <v-checkbox :label="props.label" :value="props.value" class="mb-n8 pb-n8"></v-checkbox>
  </v-selection-control-group>
  <div v-if="props.modelValue.includes(props.value)" class="ml-6">
    <slot></slot>
  </div>
</template>
