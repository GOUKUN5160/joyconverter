<script setup lang="ts">
import { ref, defineProps, onMounted, watch, nextTick } from 'vue';
import JoyConImage from '../parts/JoyConImage.vue';
import Stick from "../parts/edit/DrawStick.vue";
import Dialog from "../parts/CustomDialog.vue";

const props = defineProps({
  joycon: { type: Object, required: true },
});

const joyconName = ref("");
const snackbar = ref(false);
const snackMessage = ref("");
const calibrationDialog = ref(false);
const deleteDialog = ref(false);
const renameDialog = ref(false);
const defaultJoyConName = ref("");
let onDialogResponse: Function = (_: number) => { };
const renameJoyCon = () => {
  joyconName.value = props.joycon.name;
  const oldName = joyconName.value;
  defaultJoyConName.value = `JoyCon(${props.joycon.type})-${props.joycon.serial}`;
  onDialogResponse = (response: number) => {
    if (response == 1) {
      if (joyconName.value == "") {
        joyconName.value = defaultJoyConName.value;
      }
      if (joyconName.value == oldName) {
        return;
      }
      eel.rename_joycon(props.joycon.serial, joyconName.value)().then(() => {
        snackMessage.value = `表示名を変更しました (${oldName} → ${joyconName.value})`;
        snackbar.value = true;
      });
    }
    renameDialog.value = false;
  };
  renameDialog.value = true;
};
const deleteJoyCon = () => {
  const oldName = props.joycon.name;
  onDialogResponse = (response: number) => {
    if (response == 1) {
      eel.delete_joycon(props.joycon.serial)().then(() => {
        snackMessage.value = `削除しました (${oldName})`;
        snackbar.value = true;
      });
    }
    deleteDialog.value = false;
  };
  deleteDialog.value = true;
};

const buttonStatus = ref({} as { [key: string]: boolean });
const stickPosition = ref({} as { [key: string]: number });
const scale = ref(1);
const size = 200;
const calcScale = () => {
  const rects = document.getElementById("main-joycon-image")?.getClientRects() || [];
  for (const rect of rects) {
    scale.value = (rect.height - 100) / size;
  };
};

const startCalibration = () => {
  calibrationDialog.value = true;
  onDialogResponse = (response: number) => {
    if (response == 1) {
      eel.save_calibration(props.joycon.serial)();
    } else {
      eel.cancel_calibration()();
    }
    calibrationDialog.value = false;
  };
  eel.start_calibration(props.joycon.serial)();
};

const onStick = (serial: string, position: any) => {
  if (serial != props.joycon.serial) {
    return;
  }
  stickPosition.value = position;
};
const onButton = (serial: string, button: string, isPressed: boolean) => {
  if (serial != props.joycon.serial) {
    return;
  }
  switch (button) {
    case "stick_l_btn":
      button = "stick";
      break;
    case "stick_r_btn":
      button = "stick";
      break;
    case "left_sl":
      button = "sl";
      break;
    case "right_sl":
      button = "sr";
      break;
    case "left_sr":
      button = "sr";
      break;
    case "right_sr":
      button = "sr";
      break;
    default:
      break;
  }
  buttonStatus.value[button] = isPressed;
};

const batteryIcon = ref("");
watch(() => props.joycon, () => {
  stickPosition.value = {};
  buttonStatus.value = {
    up: false,
    down: false,
    left: false,
    right: false,
    a: false,
    b: false,
    x: false,
    y: false,
    l: false,
    r: false,
    zl: false,
    zr: false,
    minus: false,
    plus: false,
    home: false,
    capture: false,
    sl: false,
    sr: false,
    stick: false
  };
  if (Object.keys(props.joycon).length <= 0) {
    eel.set_is_send_joycon_data("", [])();
  } else {
    eel.set_is_send_joycon_data(props.joycon.serial, ["button", "stick"])();
    eel.expose(onButton, "onJoyConButton");
    eel.expose(onStick, "onJoyConStick");
  }
  nextTick(() => {
    calcScale();
  });
  if (props.joycon.is_battery_charging) {
    switch (props.joycon.battery_level) {
      case 0:
        batteryIcon.value = "mdi-battery-charging-20";
        break;
      case 1:
        batteryIcon.value = "mdi-battery-charging-40";
        break;
      case 2:
        batteryIcon.value = "mdi-battery-charging-60";
        break;
      case 3:
        batteryIcon.value = "mdi-battery-charging-80";
        break;
      case 4:
        batteryIcon.value = "mdi-battery-charging-100";
        break;
      default:
        batteryIcon.value = "mdi-battery-remove-outline";
        break;
    }
  } else {
    switch (props.joycon.battery_level) {
      case 0:
        batteryIcon.value = "mdi-battery-20";
        break;
      case 1:
        batteryIcon.value = "mdi-battery-40";
        break;
      case 2:
        batteryIcon.value = "mdi-battery-60";
        break;
      case 3:
        batteryIcon.value = "mdi-battery-80";
        break;
      case 4:
        batteryIcon.value = "mdi-battery";
        break;
      default:
        batteryIcon.value = "mdi-battery-remove-outline";
        break;
    }
  }
}, { deep: true, immediate: true });

onMounted(() => {
  window.addEventListener("resize", calcScale);
});
</script>

<template>
  <v-row v-if="Object.keys(props.joycon).length <= 0">
    <v-col>
      <strong>JoyConが選択されていません</strong>
    </v-col>
  </v-row>
  <template v-if="Object.keys(props.joycon).length > 0">
    <v-row>
      <v-col>
        <v-text-field :model-value="props.joycon.name" append-inner-icon="mdi-rename" density="compact" variant="solo"
          hide-details single-line @click:append-inner="renameJoyCon()" readonly></v-text-field>
      </v-col>
      <v-col cols="1">
        <v-row style="text-align: center;" no-gutters>
          <v-col v-if="!props.joycon.is_connected">
            <v-btn @click="deleteJoyCon">削除</v-btn>
          </v-col>
          <v-col v-if="props.joycon.is_connected">
            <v-icon :icon="batteryIcon" size="40"></v-icon>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
    <v-row class="full-height">
      <v-col>
        <div id="main-joycon-image" :class="`full-container${props.joycon.is_connected ? '' : ' disabled'}`">
          <JoyConImage :serial="props.joycon.serial" :type="props.joycon.type.toLowerCase()" :status="buttonStatus"
            :body-color="props.joycon.color_body" :button-color="props.joycon.color_btn"></JoyConImage>
        </div>
      </v-col>
      <v-col style="text-align: center;" :class="`${props.joycon.is_connected ? '' : 'disabled'}`">
        <Stick :position="stickPosition" :splitted-num="40" :scale="scale"></Stick>
        <v-btn class="mt-2" @click="startCalibration" :disabled="!props.joycon.is_connected" variant="elevated"
          color="primary">スティックを補正</v-btn>
      </v-col>
    </v-row>
  </template>
  <Dialog v-model="deleteDialog" title="削除しますか？" icon="mdi-alert-circle-outline" text="スティックの補正データなどは復元できません。"
    :onDialogResponse="onDialogResponse">
  </Dialog>
  <Dialog v-model="renameDialog" title="表示名の変更" icon="mdi-rename" text="新しい名前を入力してください"
    :onDialogResponse="onDialogResponse">
    <v-text-field v-model="joyconName" :placeholder="defaultJoyConName"
      @keydown.enter="onDialogResponse(1); renameDialog = false;"></v-text-field>
  </Dialog>
  <Dialog v-model="calibrationDialog" title="スティックの補正" icon="mdi-target" text="マークが正しく動くようになるまでスティックを回してください。"
    persistent :onDialogResponse="onDialogResponse">
    <div style="width: 100%; text-align: center;">
      <Stick :position="stickPosition" :splitted-num="40"></Stick>
    </div>
  </Dialog>
  <v-snackbar v-model="snackbar" :timeout=2000>{{ snackMessage }}</v-snackbar>
</template>

<style scoped>
.full-height {
  height: 100%;
}

.full-container {
  height: calc(100vh - (64px + (16px * 2)) - (64px + (16px * 2)));
}

.disabled {
  opacity: 0.5;
}
</style>
