<script setup lang="ts">
import { ref, watch, defineEmits, defineProps, onMounted } from 'vue';
import Radio from '../parts/edit/CustomRadioButton.vue';
import Check from '../parts/edit/CustomCheckButton.vue';
import AddFunctions from '../parts/edit/AddFunctions.vue';
import Nest from '../parts/edit/NestedDiv.vue';
import Input from '../parts/edit/CustomInput.vue';

const emit = defineEmits(["update:modelValue"]);

const props = defineProps({
  modelValue: { type: Object, required: true },
  otherProfiles: { type: Array<any>, required: true },
});

const defaultKeyboardSpeed = "20";
const keyboardSpeedMinMax = "10,100";
const defaultKeyboardConstantSpeed = "100";
const keyboardSpeedConstantMinMax = "50,2000";
const defaultKeyboardThreshold = "30";
const keyboardThresholdMinMax = "5,100";
const defaultCursorSpeed = "5";
const cursorSpeedMinMax = "1,10";
const defaultCursorAccel = "35";
const cursorAccelMinMax = "10,50";
const defaultWheelSpeed = "20";
const wheelSpeedMinMax = "10,30";
const defaultWheelAccel = "30";
const wheelAccelMinMax = "25,35";

const comment = ref("");
const checkBox = ref([] as string[]);
const selectedAction = ref("none");
const keyboardUp = ref([] as any[]);
const keyboardDown = ref([] as any[]);
const keyboardLeft = ref([] as any[]);
const keyboardRight = ref([] as any[]);
const keyboardSpeed = ref("20");
const keyboardThreshold = ref("30");
const cursorSpeed = ref("5");
const cursorAccel = ref("35");
const wheelSpeed = ref("20");
const wheelAccel = ref("30");
const wheelDirection = ref("wheelBoth");

const whileInit = ref(false);

const watchTargets = [comment, checkBox, selectedAction, keyboardUp, keyboardDown, keyboardLeft, keyboardRight, keyboardSpeed, keyboardThreshold, cursorSpeed, cursorAccel, wheelSpeed, wheelAccel, wheelDirection];
watch(watchTargets, () => {
  element2Data();
}, { deep: true });

watch(checkBox, (newVal: string[], oldVal: string[]) => {
  if (whileInit.value) {
    whileInit.value = false;
    return;
  }
  if (newVal.includes("keyboardNoaccel") && !oldVal.includes("keyboardNoaccel")) {
    keyboardSpeed.value = defaultKeyboardConstantSpeed;
  } else if (!newVal.includes("keyboardNoaccel") && oldVal.includes("keyboardNoaccel")) {
    keyboardSpeed.value = defaultKeyboardSpeed;
  }
}, { deep: true });

onMounted(() => {
  data2Element();
})

const element2Data = () => {
  const action = selectedAction.value;
  const isCardinal = checkBox.value.includes("cardinal");
  let previewText = "なし";
  let args: any = {};
  if (action == "none") {
  } else if (action == "keyboard") {
    const preview = [];
    args = {
      up: keyboardUp.value,
      down: keyboardDown.value,
      left: keyboardLeft.value,
      right: keyboardRight.value,
      speed: keyboardSpeed.value,
      noaccel: checkBox.value.includes("keyboardNoaccel"),
      threshold: keyboardThreshold.value,
    };
    if (args.up.length > 0) {
      preview.push("上");
    }
    if (args.down.length > 0) {
      preview.push("下");
    }
    if (args.left.length > 0) {
      preview.push("左");
    }
    if (args.right.length > 0) {
      preview.push("右");
    }
    if (preview.length > 0) {
      previewText = `キーボード=[${preview.join(", ")}]`;
    }
  } else if (action == "cursor") {
    args = {
      speed: cursorSpeed.value,
      accel: cursorAccel.value,
    };
    previewText = `カーソル (スピード: ${args.speed})`;
  } else if (action == "wheel") {
    args = {
      speed: wheelSpeed.value,
      accel: wheelAccel.value,
      direction: wheelDirection.value,
    };
    previewText = `スクロール (方向: ${args.direction == "wheelBoth" ? "上下左右" : args.direction == "wheelVertical" ? "上下" : "左右"}, スピード: ${args.speed})`;
  }
  if (isCardinal) {
    previewText += " (十字)";
  }
  const data = {
    actionType: action,
    data: args,
    preview: previewText,
    comment: comment.value,
    cardinal: isCardinal,
  };
  emit("update:modelValue", data);
};

const data2Element = () => {
  const data = props.modelValue;
  if (JSON.stringify(data) == JSON.stringify({})) {
    element2Data();
    return;
  }
  const args = data.data;
  checkBox.value = [];
  if (data.actionType == "none") {
    selectedAction.value = "none";
  } else if (data.actionType == "keyboard") {
    selectedAction.value = "keyboard";
    keyboardUp.value = args.up;
    keyboardDown.value = args.down;
    keyboardLeft.value = args.left;
    keyboardRight.value = args.right;
    if (args.noaccel) {
      checkBox.value.push("keyboardNoaccel");
      whileInit.value = true;
    }
    keyboardThreshold.value = args.threshold;
    keyboardSpeed.value = args.speed;
  } else if (data.actionType == "cursor") {
    selectedAction.value = "cursor";
    cursorSpeed.value = args.speed;
    cursorAccel.value = args.accel;
  } else if (data.actionType == "wheel") {
    selectedAction.value = "wheel";
    wheelSpeed.value = args.speed;
    wheelAccel.value = args.accel;
    wheelDirection.value = args.direction;
  }
  comment.value = data.comment ?? "";
  if (data.cardinal) {
    checkBox.value.push("cardinal");
  }
};
</script>

<template>
  <v-container fluid>
    <v-text-field v-model="comment" label="コメント" variant="underlined"></v-text-field>
    <v-radio-group v-model="selectedAction">
      <Radio label="なし" value="none" :modelValue="selectedAction"></Radio>
      <Radio label="キーボード" value="keyboard" :modelValue="selectedAction">
        <Nest label="上">
          <AddFunctions v-model="keyboardUp" :other-profiles="props.otherProfiles" type="keyboard"></AddFunctions>
        </Nest>
        <Nest label="下">
          <AddFunctions v-model="keyboardDown" :other-profiles="props.otherProfiles" type="keyboard"></AddFunctions>
        </Nest>
        <Nest label="左">
          <AddFunctions v-model="keyboardLeft" :other-profiles="props.otherProfiles" type="keyboard"></AddFunctions>
        </Nest>
        <Nest label="右">
          <AddFunctions v-model="keyboardRight" :other-profiles="props.otherProfiles" type="keyboard"></AddFunctions>
        </Nest>
        <Input beforeText="スピード" v-model="keyboardSpeed" :number-min-max="checkBox.includes('keyboardNoaccel') ? keyboardSpeedConstantMinMax : keyboardSpeedMinMax" :required="checkBox.includes('keyboardNoaccel') ? defaultKeyboardConstantSpeed : defaultKeyboardSpeed"></Input>
        <Check label="アクセルなし" value="keyboardNoaccel" v-model="checkBox">
          <Input afterText="%を超えたら入力" v-model="keyboardThreshold" :number-min-max="keyboardThresholdMinMax" :required="defaultKeyboardThreshold"></Input>
        </Check>
      </Radio>
      <Radio label="マウスカーソル" value="cursor" :modelValue="selectedAction">
        <Input beforeText="スピード" v-model="cursorSpeed" :number-min-max="cursorSpeedMinMax" :required="defaultCursorSpeed"></Input>
        <Input beforeText="アクセル値" v-model="cursorAccel" :number-min-max="cursorAccelMinMax" :required="defaultCursorAccel"></Input>
      </Radio>
      <Radio label="マウスホイール" value="wheel" :modelValue="selectedAction">
        <Input beforeText="スピード" v-model="wheelSpeed" :number-min-max="wheelSpeedMinMax" :required="defaultWheelSpeed"></Input>
        <Input beforeText="アクセル値" v-model="wheelAccel" :number-min-max="wheelAccelMinMax" :required="defaultWheelAccel"></Input>
        <v-selection-control-group v-model="wheelDirection">
          <v-radio label="両方" value="wheelBoth"></v-radio>
          <v-radio label="上下だけ" value="wheelVertical"></v-radio>
          <v-radio label="左右だけ" value="wheelHorizontal"></v-radio>
        </v-selection-control-group>
      </Radio>
    </v-radio-group>
    <Check label="十字方向のみ" value="cardinal" v-model="checkBox"></Check>
  </v-container>
</template>
