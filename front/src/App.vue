<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useTheme } from "vuetify";
import Profiles from "./components/tabs/TabProfiles.vue";
import Devices from "./components/tabs/TabDevices.vue";
import Others from "./components/tabs/TabOthers.vue";

const isClosed = ref(false);
const snackbar = ref(false);
const snackMessage = ref("");
const snackColor = ref("success");

onMounted(() => {
  const closeWindow = () => {
    window.close();
  };
  eel.expose(closeWindow, "closeWindow");
  const onMessage = (message: string, color: string="success") => {
    snackMessage.value = message;
    snackColor.value = color;
    snackbar.value = true;
  };
  eel.expose(onMessage, "onMessage");
  eel.get_theme()().then((currentTheme: String) => {
    darkTheme.value = currentTheme == "dark" ? true : false;
    changeTheme();
  });
  eel.onEnd = () => {
    isClosed.value = true;
  }
});
const darkTheme = ref(false);
const theme = useTheme();
const tab = ref("first");

const changeTheme = () => {
  theme.global.name.value = darkTheme.value ? "dark" : "light";
  eel.set_theme(theme.global.name.value)();
};
const closeWindow = () => {
  window.close();
};
</script>

<template>
  <v-app>
    <v-app-bar color="primary">
      <v-app-bar-title>
        <v-tabs v-model="tab" bg-color="primary">
          <v-tab value="first">アプリ</v-tab>
          <v-tab value="second">JoyCon</v-tab>
          <v-tab value="third">その他</v-tab>
        </v-tabs>
      </v-app-bar-title>
      <template v-slot:append>
        <v-switch v-model="darkTheme" @update:model-value="changeTheme"
          :prepend-icon="darkTheme ? 'mdi-weather-night' : 'mdi-weather-sunny'" hide-details inset class="mr-auto" />
      </template>
    </v-app-bar>

    <v-card-text>
      <v-tabs-window v-model="tab">
        <v-tabs-window-item value="first">
          <Profiles :drawer="tab == 'first'"></Profiles>
        </v-tabs-window-item>

        <v-tabs-window-item value="second">
          <Devices :drawer="tab == 'second'"></Devices>
        </v-tabs-window-item>

        <v-tabs-window-item value="third">
          <Others :drawer="tab == 'third'"></Others>
        </v-tabs-window-item>
      </v-tabs-window>
    </v-card-text>
  </v-app>
  <v-dialog v-model="isClosed" max-width="400" persistent>
      <v-card
      prepend-icon="mdi-close-circle-outline"
      title="切断されました"
      text="このタブを閉じ、再度設定画面を開いてください。"
    >
      <template v-slot:actions>
        <v-spacer></v-spacer>
        <v-btn @click="closeWindow">
          閉じる
        </v-btn>
      </template>
    </v-card>
  </v-dialog>
  <v-snackbar v-model="snackbar" :timeout=2000 :color="snackColor">{{ snackMessage }}</v-snackbar>
</template>
