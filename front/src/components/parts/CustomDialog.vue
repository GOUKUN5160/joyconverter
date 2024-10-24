<script setup lang="ts">
import { ref, defineProps, defineEmits, watch } from 'vue';

const emit = defineEmits(["update:modelValue"]);

const props = defineProps({
  modelValue: { type: Boolean, required: true },
  onDialogResponse: { type: Function, required: true },
  title: { type: String, required: true },
  text: { type: String, required: true },
  icon: { type: String, required: false, default: "" },
  okText: { type: String, required: false, default: "OK" },
  ngText: { type: String, required: false, default: "キャンセル" },
  persistent: { type: Boolean, required: false, default: false },
});

const open = ref(props.modelValue);

watch(() => props.modelValue, () => {
  console.log("customdialog changed", props.modelValue);
  open.value = props.modelValue;
});

const onClosed = () => {
  console.log("closed", props.modelValue, open.value);
  emit("update:modelValue", false);
};

const closeDialog = (index: number) => {
  emit("update:modelValue", false);
  props.onDialogResponse(index);
};
</script>

<template>
  <div class="text-center pa-4" v-if="props.modelValue">
    <v-dialog v-model="open" max-width="400" @after-leave="onClosed" :persistent="props.persistent">
      <v-card :prepend-icon=props.icon :text=props.text :title=props.title>
        <v-card-text v-if="$slots.default">
          <slot></slot>
        </v-card-text>
        <template v-slot:actions>
          <v-spacer></v-spacer>

          <v-btn @click="closeDialog(0)">
            {{ props.ngText }}
          </v-btn>

          <v-btn @click="closeDialog(1)">
            {{ props.okText }}
          </v-btn>
        </template>
      </v-card>
    </v-dialog>
  </div>
</template>
