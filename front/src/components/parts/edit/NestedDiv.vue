<script setup lang="ts">
import { defineProps } from 'vue';

const props = defineProps({
  label: { type: String, required: true },
});
</script>


<template>
  <!-- <v-container>
        <slot></slot>
    </v-container> -->
  <div class="mb-4">
    <span class="nest-title">{{ props.label }}</span>
    <blockquote class="nest-block">
      <slot></slot>
    </blockquote>
  </div>
</template>

<style scoped>
.nest-block {
  margin-left: 10px;
  border-left: 4px solid #7e7e7e;
}
</style>
