<script setup lang="ts">
import { ref, onMounted, defineProps } from 'vue';
import AppLoader from "./CustomLoader.vue";

const props = defineProps({
  open: { type: Boolean, required: true },
  changeState: { type: Function, required: true },
  reloadList: { type: Function, required: true },
});

onMounted(() => {
  reloadList(true);
});

const loader = ref(false);
const snackbar = ref(false);
const runningApps = ref([] as { [key: string]: string }[]);
const selected = ref({} as { [key: string]: string });
const message = ref("");

const reloadList = (silent: boolean = false) => {
  if (!(silent === true)) {
    loader.value = true;
  }
  eel.get_open_apps()().then((result: { [name: string]: string }) => {
    runningApps.value = [];
    for (let key in result) {
      runningApps.value.push({ name: key, path: result[key] });
    }
    if (!(silent === true)) {
      loader.value = false;
    }
  });
};

const itemProps = (item: { [key: string]: string }) => {
  return {
    title: item.name,
    subtitle: item.path,
  }
};

const registApp = () => {
  if (selected.value.path == undefined) {
    message.value = "アプリを選択してください";
    return;
  }
  eel.regist_app(selected.value.path, selected.value.name == "" ? null : selected.value.name)().then((result: boolean) => {
    if (result) {
      snackbar.value = true;
      props.changeState(false);
      props.reloadList();
    } else {
      message.value = "既に追加されています";
    }
    reloadList(true);
  });
};

const onClosed = () => {
  selected.value = {};
  message.value = "";
  props.changeState(false);
};
</script>

<template>
  <div class="pa-4 text-center">
    <v-dialog v-model="props.open" max-width="600" @after-leave="onClosed">
      <v-card prepend-icon="mdi-plus" title="アプリを追加">
        <v-card-text class="text-center">
          <v-row class="mt-2">
            <v-select v-model="selected" :item-props="itemProps" :items="runningApps" :hint="message" label="実行中のアプリ" no-data-text="アプリが見つかりません"
              persistent-hint class="mr-2"></v-select>
            <v-btn :disabled="loader" icon="mdi-refresh" text="reload" @click="reloadList(false);" class="mt-1"></v-btn>
          </v-row>
        </v-card-text>

        <v-divider></v-divider>

        <v-card-actions>
          <v-spacer></v-spacer>

          <v-btn text="キャンセル" variant="plain" @click="props.changeState(false)"></v-btn>
          <v-btn color="primary" text="追加" variant="tonal" @click="registApp"></v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <AppLoader title="リストを更新中" icon="mdi-format-list-bulleted" :open="loader"></AppLoader>
    <v-snackbar v-model="snackbar" :timeout=2000>追加しました</v-snackbar>
  </div>
</template>
