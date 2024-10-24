<script setup lang="ts">
import { ref, defineProps, defineEmits, watch } from 'vue';
const emit = defineEmits(["update:modelValue"]);

const props = defineProps({
  type: { type: String, required: false, default: "number" },
  numberMinMax: { type: String, required: false, default: "" },
  required: { type: String, required: false, default: "" },
  label: { type: String, required: false, default: "" },
  beforeText: { type: String, required: false, default: "" },
  afterText: { type: String, required: false, default: "" },
  modelValue: { type: String, required: false, default: "" },
  maxWidth: { type: String, required: false, default: "10%" },
  readonly: { type: Boolean, required: false, default: false },
});

watch(() => props.modelValue, (value) => {
  text.value = value;
});

const text = ref(props.modelValue);
const rules = {
  required: (value: string) => !!value || "必須項目",
  number: (value: string) => {
    if (!value) return true;
    if (value === "") return true;
    if (!/^-?[0-9]+$/.test(value)) {
      text.value = text.value.replace(/[^0-9]/g, '');
      return "数字のみ可";
    }
    return true;
  },
};

const onFocusChange = (focused: boolean) => {
  const prev = text.value;
  if (!focused && text.value == "") {
    text.value = props.required;
  }
  if (!focused && props.numberMinMax != "") {
    const obj = props.numberMinMax.split(",");
    if (obj[0] != "" && Number(text.value) < Number(obj[0])) {
      text.value = obj[0];
    } else if (obj[1] != "" && Number(text.value) > Number(obj[1])) {
      text.value = obj[1];
    }
  }
  if (!focused && props.type == "number") {
    text.value = Number(text.value).toString();
  }
  if (prev != text.value) {
    emit("update:modelValue", text.value);
  }
};

const currentRules: any[] = [];
if (props.required == "") {
  currentRules.push(rules.required);
}
if (props.type == "number") {
  currentRules.push(rules.number);
}
</script>

<template>
  <div class="d-flex align-center mb-n6 pb-n6">
    <span style="font-size: large;" class="mr-2 mb-4" v-if="props.beforeText != ''">{{ props.beforeText }}</span>
    <v-text-field v-model="text" @input="emit('update:modelValue', text)" @update:focused="onFocusChange" :label="props.label" density="compact"
      variant="outlined" :rules="currentRules" :max-width="props.maxWidth" reverse :readonly="props.readonly"></v-text-field>
    <span style="font-size: large;" class="ml-2 mb-4" v-if="props.afterText != ''">{{ props.afterText }}</span>
  </div>
</template>
