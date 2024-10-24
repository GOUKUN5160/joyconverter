<script setup lang="ts">
import { defineProps } from 'vue';

const props = defineProps({
  title: { type: String, required: true },
  icon: { type: String, required: true },
  open: { type: Boolean, required: true },
});
</script>

<template>
  <div class="pa-4 text-center" v-if="open">
    <v-dialog :model-value="props.open" @update:model-value="newValue => $emit('update:open', newValue)" max-width="320"
      persistent>
      <v-list class="py-2" color="primary" elevation="12" rounded="lg">
        <v-list-item :prepend-icon=props.icon :title=props.title>
          <template v-slot:prepend>
            <div class="pe-4">
              <v-icon color="primary" size="x-large"></v-icon>
            </div>
          </template>

          <template v-slot:append>
            <v-progress-circular color="primary" indeterminate="disable-shrink" size="16"
              width="2"></v-progress-circular>
          </template>
        </v-list-item>
      </v-list>
    </v-dialog>
  </div>
</template>
