<script setup lang="ts">
import { ref, watch, defineProps, onMounted, onUnmounted } from 'vue';
import { useTheme } from "vuetify";
import AddApp from "../parts/AddApp.vue";
import Dialog from "../parts/CustomDialog.vue";
import ProfileMain from '../main/MainProfile.vue';

const props = defineProps({
  drawer: { type: Boolean, required: true },
});

const theme = useTheme();
const selectedColor = ref("");

watch(theme.global.name, () => {
  changeColor()
});

onMounted(() => {
  getApps();
  changeColor();
  eel.reload_joycon()();
  console.log("mounted: profiles");
});

onUnmounted(() => {
  console.log("unmounted: profiles");
});

const selectedApp = ref("");
const apps = ref([] as { [key: string]: string }[]);
const addApp = ref(false);
const snackbar = ref(false);
const snackMessage = ref("");
const deleteDialog = ref(false);
const renameDialog = ref(false);
const dialogMessage = ref("");
const dialogHint = ref("");
const defaultAppName = ref("");
const appName = ref("");
const appPath = ref("");

const changeColor = () => {
  selectedColor.value = theme.global.name.value == "dark" ? "rgb(204 120 0)" : "rgb(245 221 187)";
};
const changeAddAppState = (state: boolean) => {
  addApp.value = state;
};

let onDialogResponse: Function = (_: number) => { };

const getApps = () => {
  eel.get_app_list()().then((result: { [key: string]: string }[]) => {
    apps.value = [];
    result.forEach((app) => {
      if (app["icon_path"] == "") {
        app["icon_path"] = "/default.png";
      }
      apps.value.push({
        text: app["name"],
        path: app["path"],
        default: app["default"],
        iconPath: app["icon_path"],
      });
    });
  });
};


const renameApp = (path: string, name: string, defaultName: string) => {
  defaultAppName.value = defaultName;
  appName.value = name;
  appPath.value = path;
  dialogMessage.value = "新しい名前を入力してください";
  renameDialog.value = true;
  onDialogResponse = (index: number) => {
    console.log("rename", path);
    if (index == 1) {
      let newName = appName.value;
      if (newName == "") {
        newName = defaultAppName.value;
      }
      console.log("remane", path, newName);
      eel.rename_app(path, newName)().then(() => {
        getApps();
        snackMessage.value = `アプリ名を変更しました (${name} → ${newName})`;
        snackbar.value = true;
      });
    }
  };
};

const deleteApp = (path: string, name: string) => {
  dialogMessage.value = name + "を削除しますか？ 設定は復元できません。";
  deleteDialog.value = true;
  onDialogResponse = (index: number) => {
    console.log("delete", path);
    if (index == 1) {
      eel.delete_app(path)().then(() => {
        getApps();
        if (selectedApp.value == path) {
          selectedApp.value = "";
        }
        snackMessage.value = `アプリを削除しました (${name})`;
        snackbar.value = true;
      });
    }
  };
};
</script>

<template>
  <v-navigation-drawer v-if="props.drawer" permanent @keydown.esc="selectedApp = ''" disable-resize-watcher mobile>
    <div v-for="(item, i) in apps" :value="item" :key="i">
      <v-list-item :title="item.text" link @click="selectedApp = item.path" height="50px"
        :style="(selectedApp == item.path) ? `background-color: ${selectedColor};` : undefined">
        <template v-slot:prepend>
          <img :src="item.iconPath" class="mx-2" width="32" height="32" /> </template>
        <template v-slot:append>
          <v-menu location="end">
            <template v-slot:activator="{ props }" v-if="item.path != 'ALL'">
              <v-btn density="compact" icon="mdi-dots-vertical" v-bind="props"></v-btn>
            </template>

            <v-list>
              <v-list-item title="名前の変更" @click="renameApp(item.path, item.text, item.default)"></v-list-item>
              <v-list-item title="削除" @click="deleteApp(item.path, item.text)"></v-list-item>
            </v-list>
          </v-menu>
        </template>
      </v-list-item>
      <v-divider v-if="item.path == 'ALL'"></v-divider>
    </div>
    <template v-slot:append>
      <v-divider></v-divider>
      <v-list-item link prepend-icon="mdi-plus" title="アプリを追加" class="ml-2 py-5" @click="addApp = true"></v-list-item>
    </template>
  </v-navigation-drawer>

  <v-main>
    <v-container fluid>
      <ProfileMain :path="selectedApp"></ProfileMain>
    </v-container>
    <AddApp :open="addApp" :changeState="changeAddAppState" :reloadList="getApps"></AddApp>
    <Dialog v-model="deleteDialog" title="削除しますか？" icon="mdi-alert-circle-outline" :text="dialogMessage"
      :onDialogResponse="onDialogResponse">
    </Dialog>
    <Dialog v-model="renameDialog" title="アプリ名の変更" icon="mdi-rename" :text="dialogMessage"
      :onDialogResponse="onDialogResponse">
      <v-text-field v-model="appName" :placeholder="defaultAppName" :hint="dialogHint"
        @keydown.enter="onDialogResponse(1); renameDialog = false;"></v-text-field>
      <small>アプリパス: {{ appPath }}</small>
    </Dialog>
    <v-snackbar v-model="snackbar" :timeout=2000>{{ snackMessage }}</v-snackbar>
  </v-main>
  <!-- <v-footer color="primary" app> Footer </v-footer> -->
</template>
