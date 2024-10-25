<script setup lang="ts">
import { ref, computed, watch, onMounted, defineProps } from 'vue';
import { useTheme } from "vuetify";
import JoyConImage from '../parts/JoyConImage.vue';
import DeviceMain from '../main/MainDevice.vue';
import AppLoader from "../parts/CustomLoader.vue";

const props = defineProps({
  drawer: { type: Boolean, required: true },
});


onMounted(() => {
  eel.expose(onUpdatedJoyconList, "onUpdatedJoyconList");
  eel.get_joycons()().then((result: { [key: string]: { [key: string]: any } }[]) => {
    onUpdatedJoyconList(result);
  });
});

const theme = useTheme();
const selectedColor = computed(() => {
  return theme.global.name.value == "dark" ? "rgb(204 120 0)" : "rgb(245 221 187)";
});
const selectedJoyCon = ref({} as { [key: string]: any });
const previousSelectedJoyCon = ref({} as { [key: string]: any });
const joycons = ref([] as { [key: string]: any }[]);
const loader = ref(false);
const snackbar = ref(false);
const snackbarMessage = ref("");
const snackbarColor = ref("success");

watch(() => props.drawer, () => {
  if (props.drawer) {
    selectedJoyCon.value = previousSelectedJoyCon.value;
  } else {
    previousSelectedJoyCon.value = selectedJoyCon.value;
    selectedJoyCon.value = {};
  }
});


const onUpdatedJoyconList = (joyconList: { [key: string]: { [key: string]: any } }[]) => {
  joycons.value = joyconList;
  const newSerials = joycons.value.map((joycon) => { return joycon.serial });
  if (selectedJoyCon.value.serial && newSerials.includes(selectedJoyCon.value.serial)) {
    selectedJoyCon.value = joycons.value.filter((joycon) => { return joycon.serial == selectedJoyCon.value.serial })[0];
  } else {
    selectedJoyCon.value = {};
  }
};
const reloadList = () => {
  loader.value = true;
  eel.reload_joycon()().then((result: boolean) => {
    loader.value = false;
    if (!result) {
      snackbarMessage.value = "通信エラーが発生しました。間隔を空けて再度お試しください。";
      snackbarColor.value = "error";
      snackbar.value = true;
    }
  });
};
</script>

<template>
  <v-navigation-drawer v-if="props.drawer" @keydown.esc="selectedJoyCon = {}" permanent disable-resize-watcher mobile>
    <v-list-item title="JoyCon一覧"
      :subtitle="`利用可能: ${joycons.filter(joycon => { return joycon.is_calibrated }).length}`"></v-list-item>
    <v-divider></v-divider>
    <div v-for="item in joycons" :key="item.serial">
      <v-list-item link @click="selectedJoyCon = item"
        :style="(selectedJoyCon == item) ? `background-color: ${selectedColor};` : undefined">
        <template v-slot:prepend v-if="item.is_connected">
          <div style="width: 20px;" class="mr-2"
            :title="item.is_connected ? item.is_calibrated ? '使用可能です' : 'スティックの補正を行ってください' : '接続されていません'">
            <v-icon :icon="item.is_calibrated ? 'mdi-play' : 'mdi-pause'"
              :color="item.is_calibrated ? 'success' : 'red'"></v-icon>
          </div>
        </template>
        <v-list-item-title :style="item.is_connected ? '' : 'color: darkgray;'">{{ item.name }}</v-list-item-title>
        <template v-slot:append>
          <div
            :class="`joycon-list-wrapper joycon-list-${item.type.toLowerCase()}${item.is_connected ? '' : ' disabled'}`">
            <JoyConImage :serial=item.serial :type=item.type.toLowerCase() :status="{}" :body-color="item.color_body"
              :button-color="item.color_btn"></JoyConImage>
          </div>
        </template>
      </v-list-item>
    </div>
    <template v-slot:append>
      <v-divider></v-divider>
      <v-list-item link prepend-icon="mdi-reload" title="リストを更新" class="ml-2 py-5" @click="reloadList"></v-list-item>
    </template>
  </v-navigation-drawer>
  <v-main>
    <v-container fluid>
      <!-- <v-container fluid class="full-container"> -->
      <!-- <v-layout fill-height> -->
      <DeviceMain :joycon="selectedJoyCon"></DeviceMain>
      <!-- </v-layout> -->
    </v-container>
  </v-main>
  <AppLoader title="JoyConを検索中..." icon="mdi-magnify" :open="loader"></AppLoader>
  <v-snackbar v-model="snackbar" :timeout="2000" :color="snackbarColor">{{ snackbarMessage }}</v-snackbar>
</template>

<style scoped>
.joycon-list-wrapper {
  height: 50px;
}

.joycon-list-r {
  transform: rotate(45deg);
}

.joycon-list-l {
  transform: rotate(-45deg);
}

.disabled {
  opacity: 0.5;
}
</style>
