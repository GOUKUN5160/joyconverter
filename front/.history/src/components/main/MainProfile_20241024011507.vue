<script setup lang="ts">
import { ref, watch, defineProps, onMounted } from "vue";
import Axios from "axios";
import EditList from "../main/EditList.vue";
import CustomLoader from "../parts/CustomLoader.vue";
import Dialog from "../parts/CustomDialog.vue";
import Led from "../parts/Led.vue";
import units from "../units";
const { randstr } = units();

const props = defineProps({
  path: { type: String, required: true },
});

const LED_PATTERN = [
  "0000",
  "1000",
  "0100",
  "1100",
  "0010",
  "1010",
  "0110",
  "1110",
  "0001",
  "1001",
  "0101",
  "1101",
  "0011",
  "1011",
  "0111",
  "1111",
];

const loading = ref(false);
const snackbarError = ref(false);
const snackbarErrorMessage = ref("");
const snackbarOK = ref(false);
const snackbarOkMessage = ref("");
const renameDialog = ref(false);
const dialogMessage = ref("");
const defaultProfileName = ref("");
const profileName = ref("");
const confirmDialog = ref(false);
const confirmDialogMessage = ref("");
let onDialogResponse: Function = (_: number) => {};
const profiles = ref([] as any);
const selectedProfile = ref("");
const selectedProfileIndex = ref(0);
const otherProfiles = ref([] as any);
const availableJoyCons = ref([] as any);
const selectedJoyCon = ref([] as any);
const isAllJoyCon = ref({ l: false, r: false } as { [key: string]: boolean });
const selectedLedPattern = ref("1000");

const sortFunc = (f: any, s: any) => {
  if (f.type.toLowerCase() == "r") {
    if (s.type.toLowerCase() == "r") {
      return 0;
    } else {
      return 1;
    }
  } else {
    if (s.type.toLowerCase() == "r") {
      return -1;
    } else {
      return 0;
    }
  }
};

const allJoyCon = (joyconType: string) => {
  isAllJoyCon.value[joyconType] = !isAllJoyCon.value[joyconType];
  if (isAllJoyCon.value[joyconType]) {
    selectedJoyCon.value.unshift({
      name: `全てのJoyCon(${joyconType.toUpperCase()})`,
      serial: `all-${joyconType}`,
      type: "none",
    });
  } else {
    selectedJoyCon.value = selectedJoyCon.value.filter(
      (joycon: any) => joycon.serial != `all-${joyconType}`
    );
  }
};

watch(
  () => props.path,
  () => {
    init();
  }
);
watch(selectedLedPattern, () => {
  console.log("LEDパターンが変更されました", selectedLedPattern.value);
  const index = LED_PATTERN.indexOf(selectedLedPattern.value);
  profiles.value[selectedProfileIndex.value].led = index;
});
watch(
  [profiles, selectedJoyCon],
  () => {
    const useJoyCon = {
      l: {
        isAll: isAllJoyCon.value.l,
        list: selectedJoyCon.value.filter(
          (joycon: any) => joycon.type.toLowerCase() == "l"
        ),
      },
      r: {
        isAll: isAllJoyCon.value.r,
        list: selectedJoyCon.value.filter(
          (joycon: any) => joycon.type.toLowerCase() == "r"
        ),
      },
    };
    eel
      .set_convert_info(props.path, profiles.value, useJoyCon)()
      .then((result: any) => {
        console.log("save_convert_info", result);
        if (!result) {
          snackbarErrorMessage.value = "セーブに失敗しました";
          snackbarError.value = true;
          return;
        }
      });
  },
  { deep: true }
);
watch(selectedProfile, () => {
  otherProfiles.value = profiles.value.filter(
    (profile: any) => profile.value != selectedProfile.value
  );
  console.log("他のプロファイル", otherProfiles.value);
  selectedProfileIndex.value = profiles.value.findIndex(
    (profile: any) => profile.value == selectedProfile.value
  );
  selectedLedPattern.value =
    LED_PATTERN[profiles.value[selectedProfileIndex.value].led];
  console.log("選択されたプロファイルが変更されました", selectedProfile.value);
});

const convertUseJoyConData = (data: any) => {
  selectedJoyCon.value = [];
  isAllJoyCon.value = { l: false, r: false };
  if (Object.keys(data).length <= 0) {
    return;
  }
  const availableLeft = data.l.list.filter((joycon: any) => {
    const availableSerials = availableJoyCons.value.map(
      (joycon: any) => joycon.serial
    );
    return availableSerials.includes(joycon.serial);
  });
  const availableRight = data.r.list.filter((joycon: any) => {
    const availableSerials = availableJoyCons.value.map(
      (joycon: any) => joycon.serial
    );
    return availableSerials.includes(joycon.serial);
  });
  const names = {} as { [key: string]: string };
  availableJoyCons.value.forEach((joycon: any) => {
    names[joycon.serial] = joycon.name;
  });
  selectedJoyCon.value = selectedJoyCon.value
    .concat(availableLeft, availableRight)
    .map((joycon: any) => {
      joycon.name = names[joycon.serial];
      return joycon;
    });
  if (data.r.isAll) {
    allJoyCon("r");
  }
  if (data.l.isAll) {
    allJoyCon("l");
  }
};

onMounted(() => {
  init();
});

const itemProps = (item: { [key: string]: string } | any) => {
  if (item.main) {
    return { title: "[メイン] " + item.name };
  }
  return { title: item.name };
};

const createProfile = () => {
  console.log("ここか？！", profiles.value);
  profiles.value.push({
    name: "プロファイル" + (profiles.value.length + 1),
    value: randstr(10),
    main: false,
    led: 1,
    convert: [],
  });
  selectedProfile.value = profiles.value[profiles.value.length - 1].value;
};

const deleteProfile = () => {
  if (profiles.value[selectedProfileIndex.value].main) {
    snackbarErrorMessage.value = "メインプロファイルは削除できません";
    snackbarError.value = true;
    return;
  }
  if (profiles.value.length <= 1) {
    snackbarErrorMessage.value = "プロファイルは1つ以上必要です";
    snackbarError.value = true;
    return;
  }
  confirmDialogMessage.value = `${
    profiles.value[selectedProfileIndex.value].name
  }を削除しますか？設定を復元することはできません。`;
  confirmDialog.value = true;
  onDialogResponse = (index: number) => {
    if (index == 1) {
      profiles.value.splice(selectedProfileIndex.value, 1);
      selectedProfile.value =
        profiles.value[selectedProfileIndex.value - 1].value;
      snackbarOkMessage.value = "プロファイルを削除しました";
      snackbarOK.value = true;
    }
  };
};
const setMain = () => {
  if (profiles.value[selectedProfileIndex.value].main) {
    snackbarErrorMessage.value = "既にメインプロファイルです";
    snackbarError.value = true;
    return;
  }
  profiles.value.forEach((profile: any) => {
    profile.main = false;
  });
  profiles.value[selectedProfileIndex.value].main = true;
  snackbarOkMessage.value = "メインプロファイルを変更しました";
  snackbarOK.value = true;
};
const renameProfile = () => {
  console.log("rename", selectedProfileIndex.value);
  dialogMessage.value = "新しい名前を入力してください";
  renameDialog.value = true;
  const oldName = profiles.value[selectedProfileIndex.value].name;
  profileName.value = oldName;
  defaultProfileName.value = `プロファイル${selectedProfileIndex.value + 1}`;
  onDialogResponse = (index: number) => {
    if (index == 1) {
      let newName = profileName.value;
      if (newName == "") {
        newName = defaultProfileName.value;
      }
      if (newName == oldName) {
        return;
      }
      profiles.value[selectedProfileIndex.value].name = newName;
      snackbarOkMessage.value = "プロファイル名を変更しました";
      snackbarOK.value = true;
    }
  };
};
const duplicateProfile = () => {
  const profile = profiles.value[selectedProfileIndex.value];
  const newProfile = JSON.parse(JSON.stringify(profile));
  newProfile.value = randstr(10);
  newProfile.name += " (コピー)";
  newProfile.main = false;
  profiles.value.push(newProfile);
  selectedProfile.value = newProfile.value;
  snackbarOkMessage.value = "プロファイルを複製しました";
  snackbarOK.value = true;
};

const exportProfile = () => {
  console.log("エクスポート");
  eel
    .export_profile(profiles.value[selectedProfileIndex.value])()
    .then((result: any) => {
      console.log("エクスポート結果", result);
      if (!result) {
        snackbarErrorMessage.value = "エクスポートに失敗しました";
        snackbarError.value = true;
        return;
      }
      downloadItem(result[0], result[1]);
    });
};
const downloadItem = (url: string, label: string) => {
  const link = document.createElement("a");
  link.href = url;
  link.download = label;
  console.log("ダウンロード", link, url, label);
  link.click();
  // link.click();
  return;
  Axios.get(url, { responseType: "blob" })
    .then((response: any) => {
      const blob = new Blob([response.data], {
        type: "application/octet-stream",
      });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = label;
      link.click();
      URL.revokeObjectURL(link.href);
    })
    .catch(console.error);
};

const importProfile = () => {
  console.log("インポート");
  const input = document.getElementById("import-profile") as HTMLInputElement;
  input.click();
};
const selectedFile = () => {
  const input = document.getElementById("import-profile") as HTMLInputElement;
  const file = input.files?.item(0);
  input.value = "";
  if (!file) {
    console.log("ファイルが選択されていません");
    return;
  }
  const reader = new FileReader();
  reader.onload = () => {
    const data = reader.result;
    const importedProfile = JSON.parse(atob(data as string));
    console.log("インポートデータ", importedProfile);
    if (!importedProfile) {
      snackbarErrorMessage.value = "インポートに失敗しました";
      snackbarError.value = true;
      return;
    }
    importedProfile.value = randstr(10);
    importedProfile.main = false;
    profiles.value.push(importedProfile);
    selectedProfile.value = profiles.value[profiles.value.length - 1].value;
    snackbarOkMessage.value = "プロファイルをインポートしました";
    snackbarOK.value = true;
  };
  reader.readAsText(file);
};

const updateAvailableJoyCon = () => {
  eel
    .get_joycons()()
    .then((result: { [key: string]: { [key: string]: any } }[]) => {
      console.log("はぁぁぁあｌ！！");
      const calibratedJoyCons = result.filter((joycon) => joycon.is_calibrated);
      availableJoyCons.value = calibratedJoyCons.map((joycon) => {
        return { name: joycon.name, serial: joycon.serial, type: joycon.type };
      });
      availableJoyCons.value.sort(sortFunc);
      console.log("利用可能なJoyCon", availableJoyCons.value);
    });
};

const init = () => {
  if (props.path == "") {
    return;
  }
  updateAvailableJoyCon();
  loading.value = true;
  eel
    .get_convert_info(props.path)()
    .then((data: any) => {
      const convert = data[0];
      const useJoyCon = data[1];
      if (!convert) {
        snackbarErrorMessage.value =
          "プロファイルの取得に失敗しました。アプリを削除してやり直してください。";
        snackbarError.value = true;
        loading.value = false;
        return;
      }
      console.log("get_convert_info", convert, useJoyCon);
      convertUseJoyConData(useJoyCon);
      if (convert.length <= 0) {
        profiles.value = [
          {
            name: "プロファイル1",
            value: randstr(10),
            main: true,
            led: 1,
            convert: [],
          },
        ];
        selectedProfile.value = profiles.value[0].value;
        console.log("新規作成", profiles.value);
      } else {
        console.log("既存のプロファイル", convert);
        profiles.value = convert;
        let flag = false;
        profiles.value.forEach((profile: any) => {
          if (profile.main) {
            selectedProfile.value = profile.value;
            flag = true;
          }
        });
        if (!flag) {
          profiles.value[0].main = true;
          selectedProfile.value = profiles.value[0].value;
        }
      }
      loading.value = false;
    });
};
</script>

<template>
  <v-row v-if="props.path == ''">
    <v-col>
      <strong>アプリが選択されていません</strong>
    </v-col>
  </v-row>
  <template v-if="props.path != ''">
    <v-select
      v-model="selectedJoyCon"
      @update:focused="(val: boolean) => { if (val) updateAvailableJoyCon(); }"
      class="mb-5"
      :item-props="(item: any) => { return { title: item.name, value: item.serial, type: item.type }; }"
      :items="availableJoyCons"
      label="使用するJoyCon"
      multiple
      variant="outlined"
      return-object
      chips
      no-data-text="JoyConを接続して補正してください。"
    >
      <template v-slot:chip="{ item }">
        <v-chip
          v-if="!isAllJoyCon[Object(item.raw).type.toLowerCase()]"
          :color="
            Object(item.raw).type.toLowerCase() == 'l'
              ? 'blue'
              : Object(item.raw).type.toLowerCase() == 'r'
              ? 'red'
              : undefined
          "
        >
          {{ item.title }}
        </v-chip>
      </template>
      <template v-slot:prepend-item>
        <v-list-item title="全てのJoyCon(L)" @click="allJoyCon('l')">
          <template v-slot:prepend>
            <v-checkbox-btn :model-value="isAllJoyCon.l"></v-checkbox-btn>
          </template>
        </v-list-item>
        <v-list-item title="全てのJoyCon(R)" @click="allJoyCon('r')">
          <template v-slot:prepend>
            <v-checkbox-btn :model-value="isAllJoyCon.r"></v-checkbox-btn>
          </template>
        </v-list-item>
        <v-divider class="mt-2"></v-divider>
      </template>
      <template v-slot:item="{ props, item }">
        <v-list-item
          v-bind="props"
          :disabled="isAllJoyCon[Object(item.raw).type.toLowerCase()]"
          :title="Object(item.raw).name"
          @click="console.log('これだぁ！', props, item, Object(item.raw))"
        >
          <template v-slot:prepend>
            <v-checkbox-btn
              :color="
                Object(item.raw).type.toLowerCase() == 'l'
                  ? 'blue'
                  : Object(item.raw).type.toLowerCase() == 'r'
                  ? 'red'
                  : undefined
              "
              :model-value="selectedJoyCon.map((joycon: any) => { return joycon.serial }).includes(Object(item.raw).serial)"
            >
            </v-checkbox-btn>
          </template>
        </v-list-item>
      </template>
    </v-select>
    <v-card border class="pa-5">
      <v-select
        v-model="selectedProfile"
        :items="profiles"
        :item-props="itemProps"
        label="プロファイル"
        density="compact"
        no-data-text="エラーです。アプリを削除してやり直してください。"
      ></v-select>
      <div
        v-if="profiles[selectedProfileIndex] != undefined"
        class="text-center"
      >
        <v-row justify="center">
          <v-col>
            <v-btn color="primary" dark @click="createProfile">作成</v-btn>
          </v-col>
          <v-col>
            <v-btn
              color="red"
              dark
              @click="deleteProfile"
              :disabled="profiles[selectedProfileIndex].main"
              >削除</v-btn
            >
          </v-col>
          <v-col>
            <v-btn color="#FF33FF" dark @click="renameProfile">名前変更</v-btn>
          </v-col>
          <v-col>
            <v-btn
              color="green"
              dark
              @click="setMain"
              :disabled="profiles[selectedProfileIndex].main"
              >メインに設定</v-btn
            >
          </v-col>
          <v-col>
            <v-btn color="purple" dark @click="duplicateProfile">複製</v-btn>
          </v-col>
          <v-col>
            <v-btn color="#FF6600" dark @click="importProfile"
              >インポート</v-btn
            >
          </v-col>
          <v-col>
            <v-btn color="#FF6600" dark @click="exportProfile"
              >エクスポート</v-btn
            >
          </v-col>
        </v-row>
      </div>
    </v-card>
    <div id="led-select">
      <v-select
        label="LEDパターン"
        v-model="selectedLedPattern"
        :items="LED_PATTERN"
        class="mx-10 mt-5"
        variant="solo-filled"
        hide-details
      >
        <template v-slot:selection="{ item }">
          <Led :led-data="item.title" :led-pattern="LED_PATTERN"></Led>
        </template>
        <template v-slot:item="{ props }">
          <v-list-item v-bind="props">
            <template v-slot:title>
              <Led
                :led-data="String(props.title)"
                :led-pattern="LED_PATTERN"
              ></Led>
            </template>
          </v-list-item>
        </template>
      </v-select>
    </div>
    <v-divider class="my-8"></v-divider>
    <EditList
      v-if="profiles[selectedProfileIndex] != undefined"
      v-model="profiles[selectedProfileIndex].convert"
      :other-profiles="otherProfiles"
    ></EditList>
    <CustomLoader
      title="ローディング中..."
      icon="mdi-clock-time-nine-outline"
      :open="loading"
    ></CustomLoader>
    <v-snackbar
      v-model="snackbarError"
      :timeout="2000"
      color="red"
      elevation="24"
      >{{ snackbarErrorMessage }}</v-snackbar
    >
    <v-snackbar v-model="snackbarOK" :timeout="2000">{{
      snackbarOkMessage
    }}</v-snackbar>
  </template>
  <Dialog
    v-model="renameDialog"
    title="アプリ名の変更"
    icon="mdi-rename"
    :text="dialogMessage"
    :onDialogResponse="onDialogResponse"
  >
    <v-text-field
      v-model="profileName"
      :placeholder="defaultProfileName"
      @keydown.enter="
        onDialogResponse(1);
        renameDialog = false;
      "
    ></v-text-field>
  </Dialog>
  <Dialog
    v-model="confirmDialog"
    title="プロファイルの削除"
    icon="mdi-alert-circle-outline"
    :text="confirmDialogMessage"
    :onDialogResponse="onDialogResponse"
  >
  </Dialog>
  <input
    style="display: none"
    id="import-profile"
    type="file"
    accept=".jcp"
    @change="selectedFile()"
  />
</template>

<style>
#led-select > div > div > div > div > div .v-select__selection {
  width: 100%;
}
</style>
