<script setup lang="ts">
import { defineProps } from 'vue';

const props = defineProps({
  ledData: { type: String, required: true },
  ledPattern: { type: Array<String>, required: true },
});


const isOn = (index: number) => {
  return props.ledData.substring(index - 1, index) == "1";
};
</script>

<template>
  <v-row no-gutters>
    <v-col style="text-align: center;">
      パターン{{ props.ledPattern.indexOf(ledData) + 1 }}
    </v-col>
    <v-col>
      <div style="text-align: center;">
        <v-chip class="mr-3">SL</v-chip>
        <v-icon v-for="i in 4" :icon="isOn(i) ? 'mdi-square' : 'mdi-square-outline'"
          :color="isOn(i) ? '#ffc50b' : undefined"></v-icon>
        <v-icon icon="mdi-circle-medium"></v-icon>
        <v-chip class="ml-1">SR</v-chip>
      </div>
    </v-col>
  </v-row>
</template>
