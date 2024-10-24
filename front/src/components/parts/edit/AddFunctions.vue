<script setup lang="ts">
import { ref, defineEmits, defineProps } from 'vue';
import FunctionSlot from './FunctionSlot.vue';

const emits = defineEmits(["update:functions"]);

const props = defineProps({
  type: { type: String, required: false, default: "default" },
  modelValue: { type: Array<any>, required: true },
  otherProfiles: { type: Array<any>, required: true },
});

const functions = ref(props.modelValue);

const deleteFunction = (index: number) => {
  functions.value.splice(index, 1);
  emits("update:functions", functions.value);
};

</script>

<template>
  <v-container class="mt-0" fluid>
    <v-row v-if="functions.length <= 0" class="mb-n6">
      <v-col>
        <strong>イベントがありません</strong>
      </v-col>
    </v-row>
    <v-row v-for="(data, i) in functions" :key="data.id" no-gutter class="mb-n12 pb-n12">
      <v-col cols="1" v-if="props.type == 'count' || props.type == 'switch'">
        <v-chip color="green" class="text-center mt-2">
          {{ i + 1 }}{{ props.type == 'count' ? "回" : "番目" }}
        </v-chip>
      </v-col>
      <v-col :cols="props.type == 'count' || props.type == 'switch' ? 11 : 12">
        <FunctionSlot v-model="functions[i]" :otherProfiles="props.otherProfiles" :delete="() => deleteFunction(i)"
          :rapid-mode="props.type == 'keyboard'"></FunctionSlot>
      </v-col>
    </v-row>
    <v-btn color="primary" dark v-bind="props" @click="functions.push({})" class="mt-6" :disabled="(props.type == 'keyboard') && functions.length >= 1">追加</v-btn>
  </v-container>
</template>

<style>
.noicon-select>div.v-input__control>div>div.v-field__append-inner {
  display: none !important;
}
</style>
