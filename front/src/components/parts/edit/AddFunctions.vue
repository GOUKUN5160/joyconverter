<script setup lang="ts">
import { ref, defineEmits, defineProps, watch } from "vue";
import FunctionSlot from "./FunctionSlot.vue";
import draggable from "vuedraggable";

const emits = defineEmits(["update:modelValue"]);

const props = defineProps({
  type: { type: String, required: false, default: "default" },
  modelValue: { type: Array<any>, required: true },
  otherProfiles: { type: Array<any>, required: true },
});

const functions = ref(props.modelValue);

const deleteFunction = (index: number) => {
  functions.value.splice(index, 1);
  emits("update:modelValue", functions.value);
};

const dragOptions = {
  animation: 200,
  group: "description",
  disabled: false,
  ghostClass: "ghost",
};
const drag = ref(false);
watch(
  functions,
  () => {
    emits("update:modelValue", functions.value);
  },
  { deep: true }
);
</script>

<template>
  <v-container class="mt-0" fluid>
    <v-row v-if="functions.length <= 0" class="mb-n6">
      <v-col>
        <strong>イベントがありません</strong>
      </v-col>
    </v-row>
    <draggable
      class="list-group"
      :component-data="{
        tag: 'ul',
        type: 'transition-group',
        name: !drag ? 'flip-list' : null,
      }"
      v-model="functions"
      v-bind="dragOptions"
      @start="drag = true"
      @end="drag = false"
      handle=".handle"
      item-key="id"
    >
      <template #item="{ element, index }">
        <v-row no-gutter style="height: 48px" :key="element.id">
          <v-col v-if="functions.length > 1" cols="1">
            <v-btn icon="mdi-menu" class="handle" size="small"></v-btn>
          </v-col>
          <v-col
            cols="1"
            v-if="props.type == 'count' || props.type == 'switch'"
          >
            <v-chip color="green" class="text-center mt-2">
              {{ index + 1 }}{{ props.type == "count" ? "回" : "番目" }}
            </v-chip>
          </v-col>
          <v-col
            :cols="
              (props.type == 'count' || props.type == 'switch' ? 11 : 12) -
              (functions.length > 1 ? 1 : 0)
            "
          >
            <FunctionSlot
              v-model="functions[index]"
              :otherProfiles="props.otherProfiles"
              :delete="() => deleteFunction(index)"
              :rapid-mode="props.type == 'keyboard'"
            ></FunctionSlot>
          </v-col>
        </v-row>
      </template>
    </draggable>
    <v-btn
      color="primary"
      dark
      v-bind="props"
      @click="functions.push({})"
      class="mt-6"
      :disabled="props.type == 'keyboard' && functions.length >= 1"
      >追加</v-btn
    >
  </v-container>
</template>

<style>
.noicon-select > div.v-input__control > div > div.v-field__append-inner {
  display: none !important;
}

.flip-list-move {
  transition: transform 0.5s;
}

.no-move {
  transition: transform 0s;
}

.ghost {
  opacity: 0.5;
  background: #c8ebfb;
}

.handle {
  float: left;
  padding-top: 8px;
  padding-bottom: 8px;
}
</style>
