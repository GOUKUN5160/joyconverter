<script setup lang="ts">
import { ref, defineEmits, defineProps } from 'vue';
import ButtonEdit from "./ButtonEdit.vue";
import StickEdit from './StickEdit.vue';
import GyroEdit from './GyroEdit.vue';
import Dialog from '../parts/CustomDialog.vue';

const emit = defineEmits(["update:modelValue", "update:open"]);

const props = defineProps({
  modelValue: { type: Object, required: true },
  input: { type: Object, required: true },
  open: { type: Boolean, required: false, default: false },
  otherProfiles: { type: Array<any>, required: true },
});


const value = ref(JSON.parse(JSON.stringify(props.modelValue)));

const dialog = ref(props.open);
const confirmDialog = ref(false);
const snackbar = ref(false);
const onResponse = (response: number) => {
  confirmDialog.value = false;
  if (response == 1) {

    dialog.value = false;
    emit("update:open", false);
  } else {
    ;
  }
};

const saveBack = () => {
  if (JSON.stringify(value.value) != JSON.stringify(props.modelValue)) {
    snackbar.value = true;
    console.log("save", value.value);
    emit("update:modelValue", value.value);
  }
  dialog.value = false;
  emit("update:open", false);
};

</script>

<template>
  <div class="pa-4">
    <v-dialog v-model="dialog" transition="dialog-bottom-transition" fullscreen persistent>
      <template v-slot:activator="{ props: activatorProps }">
        <v-btn v-bind="activatorProps" @click="value = JSON.parse(JSON.stringify(props.modelValue))" class="py-5 wide-button"
          size="x-large" variant="outlined" block>
          <v-row style="max-width: 100%;">
            <v-col cols="auto" class="text-left">
              <span>
                <v-chip :color="props.input.lr == 'l' ? 'blue' : 'red'">
                  {{ props.input.name }}
                </v-chip>
              </span>
            </v-col>
            <v-col cols="auto" class="text-left">
              <span>
                <v-chip :color="props.input.type == 'button' ? undefined : props.input.type == 'stick' ? 'purple' : 'green'">
                  {{ props.input.type == 'button' ? 'ボタン' : props.input.type == 'stick' ? 'スティック' : 'ジャイロ' }}
                </v-chip>
              </span>
            </v-col>
            <v-col style="overflow: hidden;" class="mt-1">
              <span v-if="value.comment" style="font-weight: bold; border-right: 1px solid #114215;" class="mr-2 pr-2">
                {{ value.comment }}
              </span>
              <span style="color: darkgray;">
                {{ value.preview }}
              </span>
            </v-col>
          </v-row>
        </v-btn>
      </template>
      <v-card>
        <v-toolbar class="fixed-bar">
          <v-btn icon="mdi-arrow-left" @click="saveBack"></v-btn>
          <v-toolbar-title>「{{ props.input.name }}」{{ props.input.type == 'button' ? 'ボタン' : props.input.type == 'stick' ? 'スティック' : '' }}の設定</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-btn text="キャンセル" @click="confirmDialog = true"></v-btn>
        </v-toolbar>
        <ButtonEdit v-if="props.input.type == 'button'" :other-profiles="props.otherProfiles" v-model="value"></ButtonEdit>
        <StickEdit v-if="props.input.type == 'stick'" :other-profiles="props.otherProfiles" v-model="value"></StickEdit>
        <GyroEdit v-if="props.input.type == 'gyro'" v-model="value"></GyroEdit>
      </v-card>
    </v-dialog>
  </div>
  <Dialog v-model="confirmDialog" title="編集のキャンセル" text="行った変更は保存されません。キャンセルしますか？" :on-dialog-response="onResponse"
    icon="mdi-alert-circle-outline" ok-text="はい" ng-text="いいえ"></Dialog>
  <v-snackbar v-model="snackbar" :timeout=2000>保存しました</v-snackbar>
</template>

<style>
.v-toolbar.fixed-bar {
  position: sticky;
  position: -webkit-sticky;
  z-index: 2;
  top: 0;
}

.wide-button>span.v-btn__content {
  width: 100%;
  overflow: hidden;
}
</style>
