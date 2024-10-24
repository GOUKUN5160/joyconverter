<script setup lang="ts">
import { ref, watch, defineEmits, defineProps, onMounted } from 'vue';
import Radio from '../parts/edit/CustomRadioButton.vue';
import Input from '../parts/edit/CustomInput.vue';

const emit = defineEmits(["update:modelValue"]);

const props = defineProps({
  modelValue: { type: Object, required: true },
});

const defaultCursorSpeed = "1000";
const cursorSpeedMinMax = "500,3000";
const cursorSpeed = ref("1000");
const comment = ref("");
const selectedAction = ref("none");

const watchTargets = [comment, selectedAction];
watch(watchTargets, () => {
  element2Data();
});


onMounted(() => {
  data2Element();
})

const element2Data = () => {
  const data = {
    actionType: selectedAction.value,
    data: {
      cursorSpeed: cursorSpeed.value,
    },
    comment: comment.value,
    preview: selectedAction.value == "cursor" ? `マウスカーソル=[スピード ${cursorSpeed.value}]` : "なし",
  };
  emit("update:modelValue", data);
};

const data2Element = () => {
  const data = props.modelValue;
  if (JSON.stringify(data) == JSON.stringify({})) {
    element2Data();
    return;
  }
  selectedAction.value = data.actionType;
  cursorSpeed.value = data.data.cursorSpeed ?? defaultCursorSpeed;
  comment.value = data.comment ?? "";
};
</script>

<template>
  <v-container fluid>
    <v-text-field v-model="comment" label="コメント" variant="underlined"></v-text-field>
    <v-radio-group v-model="selectedAction">
      <Radio label="なし" value="none" :modelValue="selectedAction"></Radio>
      <Radio label="マウスカーソル" value="cursor" :modelValue="selectedAction">
        <Input beforeText="スピード" v-model="cursorSpeed" :number-min-max="cursorSpeedMinMax" :required="defaultCursorSpeed"></Input>
      </Radio>
    </v-radio-group>
    <small>※試験的な機能</small>
  </v-container>
</template>
