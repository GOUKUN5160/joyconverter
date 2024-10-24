<script setup lang="ts">
import { ref, watch, defineEmits, defineProps, onMounted } from 'vue';
import units from '../../units';
const { randstr } = units();
import Input from './CustomInput.vue';

const emit = defineEmits(["update:modelValue"]);
const props = defineProps({
  modelValue: { type: Object, required: true },
  otherProfiles: { type: Array<Object>, required: true },
  delete: { type: Function, required: false, default: () => { } },
  rapidMode: { type: Boolean, required: false, default: false },
});

onMounted(() => {
  data2Element();
});

const ACTION_TYPES = [
  { name: "キーボード", value: "keyboard" },
  { name: "マウス", value: "mouse" },
  { name: "その他", value: "other" }
];
if (props.rapidMode) {
  ACTION_TYPES.splice(2, 1);
}
const KEYBOARD_ACTIONS = [
  { name: "タッチ", value: "touch" },
  { name: "プレス", value: "press" },
  { name: "リリース", value: "release" },
]
if (props.rapidMode) {
  KEYBOARD_ACTIONS.splice(1, 2);
}
const MOUSE_ACTIONS = [
  { name: "左クリック", value: "leftClick" },
  { name: "右クリック", value: "rightClick" },
  { name: "中クリック", value: "middleClick" },
  { name: "スクロール", value: "scroll" },
  { name: "移動(絶対座標)", value: "moveAbsolute" },
  { name: "移動(相対座標)", value: "moveRelative" },
];
if (props.rapidMode) {
  MOUSE_ACTIONS.splice(4, 1);
}
const MOUSE_CLICK_MODE = [
  { name: "クリック", value: "click" },
  { name: "プレス", value: "press" },
  { name: "リリース", value: "release" },
];
if (props.rapidMode) {
  MOUSE_CLICK_MODE.splice(1, 2);
}
const START_STOP_KEY = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"];
const SCROLL_MINMAX = { min: 0, max: 5 };
const SLEEP_MINMAX = { min: 0, max: 10000 };
const RUMBLE_MINMAX = { min: 50, max: 5000 };
const OTHER_ACTIONS = [
  { name: "待機", value: "sleep" },
  { name: "プロファイル切り替え", value: "changeProfile" },
  { name: "ジャイロリセット", value: "resetGyro" },
  { name: "バイブレーション(非同期実行)", value: "rumble" },
];

const itemProps = (item: { [key: string]: string } | any) => {
  return {
    title: item.name,
  }
};

const elmId = ref(randstr(8));
const selectedType = ref("keyboard");
const selectedKeyboardActionType = ref("touch");
const selectedKeyboardAction = ref([] as { [key: string]: string }[]);
const selectedMouseAction = ref("leftClick");
const selectedMouseClickMode = ref("click");
const selectedOtherAction = ref("sleep");
const selectedOtherProfile = ref("");
const scrollValues = ref({ up: "0", down: "0", left: "0", right: "0" });
const absoluteMove = ref({ x: "0", y: "0" } as { [key: string]: string });
const relativeMove = ref({ x: "0", y: "0" } as { [key: string]: string });
const startStopKey = ref("A");
const temporaryClickData = ref([] as { [key: string]: string }[]);
const temporarySelectedData = ref([] as { [key: string]: string | number[] }[]);
const temporaryCalcedData = ref({ x: "", y: "" } as { [key: string]: string });
const sleepTime = ref("0");
const rumbleTime = ref("0");
const KeyInputFocused = ref("");
const mouseInputFocused = ref("");
const emittedData = ref("");

const watchTargets = [selectedType, selectedKeyboardActionType, selectedKeyboardAction, selectedMouseAction, selectedMouseClickMode, selectedOtherAction, selectedOtherProfile, scrollValues, absoluteMove, relativeMove, sleepTime, rumbleTime];
watch(watchTargets, () => {
  element2Data();
}, { deep: true });

const element2Data = () => {
  let args = "";
  if (selectedType.value == "keyboard") {
    args = JSON.stringify({ action: selectedKeyboardActionType.value, value: selectedKeyboardAction.value });
  } else if (selectedType.value == "mouse") {
    if (["leftClick", "rightClick", "middleClick"].includes(selectedMouseAction.value)) {
      args = JSON.stringify({ action: selectedMouseAction.value, value: selectedMouseClickMode.value });
    } else if (selectedMouseAction.value == "scroll") {
      args = JSON.stringify({ action: "scroll", value: scrollValues.value });
    } else if (selectedMouseAction.value == "moveAbsolute") {
      args = JSON.stringify({ action: "moveAbsolute", value: absoluteMove.value });
    } else if (selectedMouseAction.value == "moveRelative") {
      args = JSON.stringify({ action: "moveRelative", value: relativeMove.value });
    }
  } else if (selectedType.value == "other") {
    if (selectedOtherAction.value == "sleep") {
      args = JSON.stringify({ action: "sleep", value: sleepTime.value });
    } else if (selectedOtherAction.value == "changeProfile") {
      args = JSON.stringify({ action: "changeProfile", value: selectedOtherProfile.value });
    } else if (selectedOtherAction.value == "resetGyro") {
      args = JSON.stringify({ action: "resetGyro" });
    } else if (selectedOtherAction.value == "rumble") {
      args = JSON.stringify({ action: "rumble", value: rumbleTime.value });
    }
  }
  const data = { type: selectedType.value, args: args, id: elmId.value };
  const dataStr = JSON.stringify(data);
  if (emittedData.value == dataStr) {
    return;
  }
  emit("update:modelValue", data);
  emittedData.value = dataStr;
};

const data2Element = () => {
  emittedData.value = JSON.stringify(props.modelValue);
  const data = props.modelValue;
  let args: any = {};
  try {
    args = JSON.parse(data.args);
  } catch (e) {
    element2Data();
    return;
  }
  selectedType.value = data.type;
  elmId.value = data.id;
  if (data.type == "keyboard") {
    selectedKeyboardActionType.value = args.action;
    selectedKeyboardAction.value = args.value;
  } else if (data.type == "mouse") {
    selectedMouseAction.value = args.action;
    if (args.action == "leftClick" || args.action == "rightClick" || args.action == "middleClick") {
      selectedMouseClickMode.value = args.value;
    } else if (args.action == "scroll") {
      scrollValues.value = args.value;
    } else if (args.action == "moveAbsolute") {
      absoluteMove.value = args.value;
    } else if (args.action == "moveRelative") {
      relativeMove.value = args.value;
    }
  } else if (data.type == "other") {
    selectedOtherAction.value = args.action;
    if (args.action == "sleep") {
      sleepTime.value = args.value;
    } else if (args.action == "changeProfile") {
      selectedOtherProfile.value = args.value;
    } else if (args.action == "rumble") {
      rumbleTime.value = args.value;
    }
  }
};

const calc2Point = (startPoint: number[] | string[], endPoint: number[] | string[]) => {
  const x = Number(endPoint[0]) - Number(startPoint[0]);
  const y = Number(endPoint[1]) - Number(startPoint[1]);
  return { x: x.toString(), y: y.toString() };
};

const onKeyUp = (keyName: string, keyId: string) => {
  if (KeyInputFocused.value == "keyboard") {
    selectedKeyboardAction.value.push({ name: keyName.toUpperCase(), id: keyId });
  } else if (KeyInputFocused.value == "moveRelative" && keyName.toLowerCase() == startStopKey.value.toLowerCase()) {
    if (mouseInputFocused.value == "moveRelative") {
      mouseInputFocused.value = "";
    } else {
      mouseInputFocused.value = "moveRelative";
    }
  }
};
const onMouseClick = (x: number, y: number, button: string, pressed: boolean) => {
  if (mouseInputFocused.value == "moveAbsolute") {
    absoluteMove.value = { x: x.toString(), y: y.toString() };
    mouseInputFocused.value = "";
    setMouseMoveFocused(false);
    setMouseClickFocused(false);
    element2Data();
  } else if (mouseInputFocused.value == "moveRelative") {
    let buttonName = "不明";
    switch (button) {
      case "left":
        buttonName = "左クリック";
        break;
      case "right":
        buttonName = "右クリック";
        break;
      case "middle":
        buttonName = "中クリック";
        break;
    }
    temporaryClickData.value.push({ id: (temporaryClickData.value.length + 1).toString(), button: buttonName, event: pressed ? "プレス" : "リリース", x: x.toString(), y: y.toString() });
  }
};
const onMouseMove = (x: number, y: number) => {
  if (mouseInputFocused.value == "moveAbsolute") {
    absoluteMove.value = { x: x.toString(), y: y.toString() };
  }
};

const setKeyInputFocused = (isFocus: boolean) => {
  if (isFocus) {
    eel.expose(onKeyUp, "onKeyUp");
    if (KeyInputFocused.value == "keyboard") {
      eel.set_is_send_data("keyPrevent", isFocus)();
    } else if (KeyInputFocused.value == "moveRelative") {
      eel.set_is_send_data("keyboard", isFocus)();
    }
  } else {
    eel.set_is_send_data("keyPrevent", false)();
  }
};
const setMouseMoveFocused = (isFocus: boolean) => {
  if (isFocus) {
    eel.expose(onMouseMove, "onMouseMove");
  }
  eel.set_is_send_data("mouseMove", isFocus)();
};
const setMouseClickFocused = (isFocus: boolean) => {
  if (isFocus) {
    eel.expose(onMouseClick, "onMouseClick");
  }
  eel.set_is_send_data("mouseClick", isFocus)();
};
</script>
<template>
  <v-row>
    <v-col cols="2">
      <v-select v-model="selectedType" label="タイプ" density="compact" :item-props="itemProps"
        :items="ACTION_TYPES"></v-select>
    </v-col>
    <template v-if="selectedType == 'keyboard'">
      <v-col cols="2">
        <v-select v-model="selectedKeyboardActionType" label="アクション" density="compact" :item-props="itemProps"
          :items="KEYBOARD_ACTIONS"></v-select>
      </v-col>
      <v-col cols="7">
        <v-select v-model="selectedKeyboardAction" :item-props="itemProps" density="compact" variant="outlined" readonly
          chips multiple clearable class="noicon-select" placeholder="順番にキーを押してください（1つずつ入力してください）"
          @update:focused="(isFocused: boolean) => { if (isFocused) { KeyInputFocused = 'keyboard'; } else { KeyInputFocused = ''; } setKeyInputFocused(isFocused); }"></v-select>
      </v-col>
    </template>
    <template v-if="selectedType == 'mouse'">
      <v-col cols="3">
        <v-select v-model="selectedMouseAction" label="アクション" density="compact" :item-props="itemProps"
          :items="MOUSE_ACTIONS"></v-select>
      </v-col>
      <template v-if="['leftClick', 'rightClick', 'middleClick'].includes(selectedMouseAction)">
        <v-col cols="6">
          <v-select v-model="selectedMouseClickMode" label="モード" density="compact" :item-props="itemProps"
            :items="MOUSE_CLICK_MODE"></v-select>
        </v-col>
      </template>
      <template v-if="selectedMouseAction == 'scroll'">
        <v-col cols="1.5">
          <Input before-text="上" max-width="100%" v-model="scrollValues.up" required="0"
            :number-min-max="`${SCROLL_MINMAX.min},${SCROLL_MINMAX.max}`"
            @update:model-value="scrollValues.down = '0'"></Input>
        </v-col>
        <v-col cols="1.5">
          <Input before-text="下" max-width="100%" v-model="scrollValues.down" required="0"
            :number-min-max="`${SCROLL_MINMAX.min},${SCROLL_MINMAX.max}`"
            @update:model-value="scrollValues.up = '0'"></Input>
        </v-col>
        <v-col cols="1.5">
          <Input before-text="左" max-width="100%" v-model="scrollValues.left" required="0"
            :number-min-max="`${SCROLL_MINMAX.min},${SCROLL_MINMAX.max}`"
            @update:model-value="scrollValues.right = '0'"></Input>
        </v-col>
        <v-col cols="1.5">
          <Input before-text="右" max-width="100%" v-model="scrollValues.right" required="0"
            :number-min-max="`${SCROLL_MINMAX.min},${SCROLL_MINMAX.max}`"
            @update:model-value="scrollValues.left = '0'"></Input>
        </v-col>
      </template>
      <template v-if="selectedMouseAction == 'moveAbsolute'">
        <v-col cols="2">
          <Input before-text="X" max-width="100%" v-model="absoluteMove.x" required="0"
            :readonly="mouseInputFocused == 'moveAbsolute'"></Input>
        </v-col>
        <v-col cols="2">
          <Input before-text="Y" max-width="100%" v-model="absoluteMove.y" required="0"
            :readonly="mouseInputFocused == 'moveAbsolute'"></Input>
        </v-col>
        <v-col cols="2">
          <v-btn @click="mouseInputFocused = 'moveAbsolute'; setMouseMoveFocused(true); setMouseClickFocused(true);"
            :text="mouseInputFocused == 'moveAbsolute' ? 'クリックして確定' : '取得'"
            :disabled="mouseInputFocused == 'moveAbsolute'"></v-btn>
        </v-col>
      </template>
      <template v-if="selectedMouseAction == 'moveRelative'">
        <v-col cols="2">
          <Input before-text="X" after-text="px" max-width="100%" v-model="relativeMove.x" required="0"></Input>
        </v-col>
        <v-col cols="2">
          <Input before-text="Y" after-text="px" max-width="100%" v-model="relativeMove.y" required="0"></Input>
        </v-col>
        <v-col cols="2">
          <v-dialog max-width="500" persistent>
            <template v-slot:activator="{ props: activatorProps }">
              <v-btn v-bind="activatorProps"
                @click="temporaryClickData = []; temporarySelectedData = []; temporaryCalcedData = { x: '', y: '' }; KeyInputFocused = 'moveRelative'; setMouseClickFocused(true); setKeyInputFocused(true);"
                :text="mouseInputFocused == 'moveRelative' ? '測定中' : '距離を測定'"
                :disabled="mouseInputFocused == 'moveRelative'"></v-btn>
            </template>
            <template v-slot:default="{ isActive }">
              <v-card :title="mouseInputFocused == 'moveRelative' ? '測定中' : '相対座標を計算'">
                <v-card-text>
                  2点を選択してください
                  <v-row justify="space-around">
                    <v-col>
                      <v-selection-control-group :model-value="true">
                        <v-checkbox label="始点" color="blue" class="mb-n5 pb-n5" readonly></v-checkbox>
                      </v-selection-control-group>
                    </v-col>
                    <v-col>
                      <v-selection-control-group :model-value="true">
                        <v-checkbox label="終点" color="red" class="mb-n5 pb-n5" readonly></v-checkbox>
                      </v-selection-control-group>
                    </v-col>
                    <v-col>
                      <v-select v-model="startStopKey" :label="mouseInputFocused == 'moveRelative' ? '停止キー' : '開始キー'"
                        density="compact" :items="START_STOP_KEY.map((key: string) => key.toUpperCase())"></v-select>
                    </v-col>
                  </v-row>
                  結果: <template v-if="temporaryCalcedData.x != '' && temporaryCalcedData.y != ''">({{
                    temporaryCalcedData.x }}, {{ temporaryCalcedData.y }})</template>
                  <v-data-table-virtual id="pointTable" :items="temporaryClickData" hide-default-header
                    hide-default-footer height="400" no-data-text="記録を開始してからポイントをクリックしてください">
                    <template v-slot:item.id="{ item }">
                      <v-selection-control-group v-model="temporarySelectedData"
                        @update:model-value="() => { if (Object.keys(temporarySelectedData).length >= 2) { temporaryCalcedData = calc2Point(temporarySelectedData[0].position as any, temporarySelectedData[1].position as any); } else { temporaryCalcedData = { x: '', y: '' }; } }">
                        <v-checkbox-btn :value="{ id: item.id, position: [item.x, item.y] }"
                          :readonly="Object.keys(temporarySelectedData).length >= 2 && !temporarySelectedData.map(d => d.id).includes(item.id)"
                          :color="temporarySelectedData.map(d => d.id).indexOf(item.id) == 1 ? 'red' : 'blue'"></v-checkbox-btn>
                      </v-selection-control-group>
                    </template>
                  </v-data-table-virtual>
                </v-card-text>

                <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-row>
                    <v-col class="me-auto" cols="auto">
                      <v-btn text="クリア" @click="temporaryClickData = []" variant="tonal"></v-btn>
                    </v-col>
                    <v-col cols="auto">
                      <v-btn text="キャンセル"
                        @click="mouseInputFocused = ''; KeyInputFocused = ''; setMouseClickFocused(false); setKeyInputFocused(false); isActive.value = false;"></v-btn>
                      <v-btn text="確定" color="primary" variant="flat"
                        @click="mouseInputFocused = ''; KeyInputFocused = ''; setMouseClickFocused(false); setKeyInputFocused(false); isActive.value = false; relativeMove = temporaryCalcedData; element2Data();"
                        :disabled="temporaryCalcedData.x == '' || temporaryCalcedData.y == ''"></v-btn>
                    </v-col>
                  </v-row>
                </v-card-actions>
              </v-card>
            </template>
          </v-dialog>
        </v-col>
      </template>

    </template>
    <template v-if="selectedType == 'other'">
      <v-col cols="4">
        <v-select v-model="selectedOtherAction" label="アクション" density="compact" :item-props="itemProps"
          :items="OTHER_ACTIONS"></v-select>
      </v-col>
      <v-col cols="5" v-if="selectedOtherAction == 'sleep'">
        <Input before-text="時間" :after-text="`ms （${Number(sleepTime) / 1000}秒）`" v-model="sleepTime" required="0"
          :number-min-max="`${SLEEP_MINMAX.min},${SLEEP_MINMAX.max}`" max-width="50%"></Input>
      </v-col>
      <v-col cols="5" v-if="selectedOtherAction == 'changeProfile'">
        <v-select v-model="selectedOtherProfile" label="プロファイル" density="compact" :item-props="itemProps"
          :items="props.otherProfiles" no-data-text="他のプロファイルがありません"></v-select>
      </v-col>
      <v-col cols="5" v-if="selectedOtherAction == 'resetGyro'"></v-col>
      <v-col cols="5" v-if="selectedOtherAction == 'rumble'">
        <Input before-text="振動時間" :after-text="`ms （${Number(rumbleTime) / 1000}秒）`" v-model="rumbleTime" required="100"
          :number-min-max="`${RUMBLE_MINMAX.min},${RUMBLE_MINMAX.max}`" max-width="50%"></Input>
      </v-col>
    </template>
    <v-col cols="1">
      <v-btn @click="props.delete" icon="mdi-close" size="small"></v-btn>
    </v-col>
  </v-row>
</template>
