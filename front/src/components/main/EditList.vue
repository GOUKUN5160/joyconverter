<script setup lang="ts">
import { ref, watch, defineProps } from "vue";
import { useTheme } from "vuetify";
import EditSlot from "./EditSlot.vue";
import Dialog from "../parts/CustomDialog.vue";

const props = defineProps({
  modelValue: { type: Array<any>, required: true },
  otherProfiles: { type: Array<any>, required: true },
  pressingButton: { type: Array<String>, required: true },
});
const theme = useTheme();

const JOYCON_INPUTS = [
  { name: "Lスティック", value: "left_stick", type: "l" },
  { name: "Lスティック押し込み", value: "stick_l_btn", type: "l" },
  { name: "L", value: "l", type: "l" },
  { name: "ZL", value: "zl", type: "l" },
  { name: "マイナス", value: "minus", type: "l" },
  { name: "↑", value: "up", type: "l" },
  { name: "↓", value: "down", type: "l" },
  { name: "←", value: "left", type: "l" },
  { name: "→", value: "right", type: "l" },
  { name: "SL", value: "left_sl", type: "l" },
  { name: "SR", value: "left_sr", type: "l" },
  { name: "キャプチャ", value: "capture", type: "l" },
  { name: "ジャイロ", value: "left_gyro", type: "l" },

  { name: "Rスティック", value: "right_stick", type: "r" },
  { name: "Rスティック押し込み", value: "stick_r_btn", type: "r" },
  { name: "R", value: "r", type: "r" },
  { name: "ZR", value: "zr", type: "r" },
  { name: "プラス", value: "plus", type: "r" },
  { name: "A", value: "a", type: "r" },
  { name: "B", value: "b", type: "r" },
  { name: "X", value: "x", type: "r" },
  { name: "Y", value: "y", type: "r" },
  { name: "SL", value: "right_sl", type: "r" },
  { name: "SR", value: "right_sr", type: "r" },
  { name: "ホーム", value: "home", type: "r" },
  { name: "ジャイロ", value: "right_gyro", type: "r" },
];

const snackbarOK = ref(false);
const snackbarOkMessage = ref("");
const confirmDialog = ref(false);
const confirmDialogMessage = ref("");
let onDialogResponse: Function = (_: number) => {};
const inputs = ref(props.modelValue);
const addSelection = ref([] as { name: string; value: string; type: string }[]);

const pressingColor = ref("");
const changeColor = () => {
  pressingColor.value = theme.global.name.value == "dark" ? "rgb(204 120 0)" : "rgb(245 221 187)";
};
watch(theme.global.name, () => {
  changeColor()
}, { immediate: true });

watch(
  () => props.modelValue,
  () => {
    inputs.value = props.modelValue;
  },
  { deep: true }
);
watch(
  inputs,
  () => {
    addSelection.value = JOYCON_INPUTS.filter(
      (obj) => !inputs.value.map((obj) => obj.input.value).includes(obj.value)
    );
  },
  { deep: true, immediate: true }
);

const addInput = (input: { name: string; value: string; type: string }) => {
  const type = ["left_stick", "right_stick"].includes(input.value)
    ? "stick"
    : ["left_gyro", "right_gyro"].includes(input.value)
    ? "gyro"
    : "button";
  inputs.value.push({
    input: { name: input.name, value: input.value, type: type, lr: input.type },
    value: {},
    open: true,
  });
};
const deleteInput = (index: number) => {
  confirmDialogMessage.value = `${inputs.value[index].input.name}${
    inputs.value[index].input.type == "button"
      ? "ボタン"
      : inputs.value[index].input.type == "stick"
      ? "スティック"
      : ""
  }の設定を削除しますか？復元することはできません。`;
  confirmDialog.value = true;
  onDialogResponse = (response: number) => {
    if (response == 1) {
      inputs.value.splice(index, 1);
      snackbarOkMessage.value = "削除しました";
      snackbarOK.value = true;
    }
  };
};
</script>

<template>
  <v-row v-if="inputs.length <= 0" justify="center" class="text-center">
    <v-col>
      <strong>設定がありません</strong>
    </v-col>
  </v-row>
  <div v-for="(item, i) in inputs" class="mb-n5 pb-n5">
    <v-row no-gutters>
      <v-col cols="11">
        <EditSlot
          v-model="item.value"
          v-model:open="item.open"
          :input="item.input"
          :otherProfiles="otherProfiles"
          :style="props.pressingButton.includes(item.input.value) ? `background-color: ${pressingColor};` : undefined"
          :key="item.input.value + (item.value.comment ? item.value.comment : '') + (item.value.preview ? item.value.preview : '')"
        >
        </EditSlot>
      </v-col>
      <v-col cols="1">
        <v-btn
          icon="mdi-close"
          class="mt-4"
          @click="() => deleteInput(i)"
        ></v-btn>
      </v-col>
    </v-row>
  </div>
  <div class="text-center">
    <v-menu open-on-hover>
      <template v-slot:activator="{ props }">
        <v-btn
          variant="outlined"
          class="mt-5"
          v-bind="props"
          :disabled="addSelection.length <= 0"
        >
          追加
        </v-btn>
      </template>
      <v-list>
        <v-list-item
          v-for="item in addSelection"
          :key="item.value"
          :style="props.pressingButton.includes(item.value) ? `background-color: ${pressingColor};` : undefined"
          @click="() => addInput(item)"
        >
          <v-list-item-title>
            <v-chip :color="item.type == 'l' ? 'blue' : 'red'" class="mr-2">
              {{ item.type.toUpperCase() }}
            </v-chip>
            {{ item.name }}
          </v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>
  </div>
  <Dialog
    v-model="confirmDialog"
    title="設定の削除"
    icon="mdi-alert-circle-outline"
    :text="confirmDialogMessage"
    :onDialogResponse="onDialogResponse"
  >
  </Dialog>
  <v-snackbar v-model="snackbarOK" :timeout="2000">{{
    snackbarOkMessage
  }}</v-snackbar>
</template>
