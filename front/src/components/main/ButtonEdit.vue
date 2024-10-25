<script setup lang="ts">
// import { ref, defineEmits, defineProps, onMounted } from 'vue';
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

const defaultDelay = "100";
const delayMinMax = "100,5000";
const defaultRapidInterval = "100";
const basicOnkeepRapidMinMax = "5,5000";
const defaultCounInterval = "500";
const countIntervalMinMax = "100,2000";
const defaultLength = "500";
const lengthMinMax = "100,5000";

const comment = ref("");
const checkBoxes = ref(["switch-reset-anotherProfile"] as String[]);
const selectedAction = ref("none");
const basicOnPress = ref([] as any[]);
const basicOnKeep = ref("none");
const basicOnKeepRapid = ref([] as any[]);
const basicOnKeepRapidInterval = ref("100");
const basicOnKeepRapidDelay = ref("100");
const basicOnKeepAnotherProfile = ref({} as any);
const basicOnKeepAnotherProfileDelay = ref("100");
const basicOnRelease = ref([] as any[]);

const switchFunc = ref([] as any[]);
const switchDelay = ref("100");

const countFunc = ref([] as any[]);
const countInterval = ref("100");

const lengthTime = ref("100");
const lengthUnder = ref([] as any[]);
const lengthOver = ref([] as any[]);
const lengthOnRelease = ref([] as any[]);

const watchTargets = [comment, checkBoxes, selectedAction, basicOnPress, basicOnKeep, basicOnKeepRapid, basicOnKeepRapidInterval, basicOnKeepRapidDelay, basicOnKeepAnotherProfile, basicOnKeepAnotherProfileDelay, basicOnRelease, switchFunc, switchDelay, countFunc, countInterval, lengthTime, lengthUnder, lengthOver, lengthOnRelease];
watch(watchTargets, () => {
  element2Data();
}, { deep: true });


onMounted(() => {
  data2Element();
});

const itemProps = (item: { [key: string]: string } | any) => {
  return {
    title: item.name,
  }
};

const element2Data = () => {
  let args = {};
  let previewText = "なし";
  if (selectedAction.value == "basic") {
    const preview = [];
    const press = basicOnPress.value;
    let keep = { type: basicOnKeep.value, value: {} };
    const release = basicOnRelease.value;
    if (press.length > 0) {
      preview.push(`プレス=[${press.length}アクション]`);
    }
    if (basicOnKeep.value == "rapid") {
      if (basicOnKeepRapid.value.length > 0) {
        preview.push(`長押し=[連射 ${basicOnKeepRapidInterval.value}ms]`);
      }
      keep.value = {
        key: basicOnKeepRapid.value,
        interval: basicOnKeepRapidInterval,
        delay: checkBoxes.value.includes("basic-onKeep-rapid-delay"),
        delayTime: basicOnKeepRapidDelay.value
      };
    } else if (basicOnKeep.value == "another-profile") {
      if (basicOnKeepAnotherProfile.value.name != undefined) {
        preview.push(`長押し=[他プロファイル (${basicOnKeepAnotherProfile.value.name})]`);
      }
      keep.value = {
        profile: basicOnKeepAnotherProfile.value,
        delay: checkBoxes.value.includes("basic-onKeep-anotherProfile-delay"),
        delayTime: basicOnKeepAnotherProfileDelay.value
      };
    }
    if (release.length > 0) {
      preview.push(`リリース=[${release.length}アクション]`);
    }
    if (preview.length > 0) {
      previewText = preview.join(", ");
    }
    args = {
      press: press,
      keep: keep,
      release: release
    };
  } else if (selectedAction.value == "switch") {
    const isResetDelay = checkBoxes.value.includes("switch-reset-delay");
    const isResetAnotherProfile = checkBoxes.value.includes("switch-reset-anotherProfile");
    previewText = `切り替え=[${switchFunc.value.length}アクション]`;
    if (isResetDelay) {
      previewText += ` (${switchDelay.value}msでリセット)`;
    }
    if (isResetAnotherProfile) {
      previewText += " (他プロファイルでリセット)";
    }
    args = {
      functions: switchFunc.value,
      delay: isResetDelay,
      delayTime: switchDelay.value,
      reset: isResetAnotherProfile
    };
  } else if (selectedAction.value == "count") {
    previewText = `回数=[${countFunc.value.length}アクション] (認識間隔: ${countInterval.value}ms)`;
    args = {
      functions: countFunc.value,
      interval: countInterval.value
    };
  } else if (selectedAction.value == "length") {
    const preview = [`長さ: ${Number(lengthTime.value) / 1000}秒`];
    if (lengthUnder.value.length > 0) {
      preview.push(`以下=[${lengthUnder.value.length}アクション]`);
    }
    if (lengthOver.value.length > 0) {
      preview.push(`以上=[${lengthOver.value.length}アクション]`);
    }
    if (lengthOnRelease.value.length > 0) {
      preview.push(`リリース=[${lengthOnRelease.value.length}アクション]`);
    }
    previewText = preview.join(", ");
    args = {
      time: lengthTime.value,
      under: lengthUnder.value,
      over: lengthOver.value,
      release: lengthOnRelease.value
    };
  }
  const data = {
    actionType: selectedAction.value,
    data: args,
    preview: previewText,
    comment: comment.value
  }
  emit("update:modelValue", data);
};

const data2Element = () => {
  const data = props.modelValue;
  if (JSON.stringify(data) == JSON.stringify({})) {
    element2Data();
    return;
  }
  comment.value = data.comment ?? "";
  selectedAction.value = data.actionType;
  if (data.actionType == "none") {
    ;
  } else if (data.actionType == "basic") {
    basicOnPress.value = data.data.press;
    basicOnKeep.value = data.data.keep.type;
    if (data.data.keep.type == "none") {
      ;
    } else if (data.data.keep.type == "rapid") {
      basicOnKeepRapid.value = data.data.keep.value.key;
      basicOnKeepRapidInterval.value = data.data.keep.value.interval;
      if (data.data.keep.value.delay) {
        checkBoxes.value.push("basic-onKeep-rapid-delay");
        basicOnKeepRapidDelay.value = data.data.keep.value.delayTime;
      }
    } else if (data.data.keep.type == "another-profile") {
      basicOnKeepAnotherProfile.value = data.data.keep.value.profile;
      if (data.data.keep.value.delay) {
        checkBoxes.value.push("basic-onKeep-anotherProfile-delay");
        basicOnKeepAnotherProfileDelay.value = data.data.keep.value.delayTime;
      }
    }
    basicOnRelease.value = data.data.release;
  } else if (data.actionType == "switch") {
    switchFunc.value = data.data.functions;
    if (data.data.delay) {
      checkBoxes.value.push("switch-reset-delay");
      switchDelay.value = data.data.delayTime;
    }
    if (data.data.reset) {
      checkBoxes.value.push("switch-reset-anotherProfile");
    }
  } else if (data.actionType == "count") {
    countFunc.value = data.data.functions;
    countInterval.value = data.data.interval;
  } else if (data.actionType == "length") {
    lengthTime.value = data.data.time;
    lengthUnder.value = data.data.under;
    lengthOver.value = data.data.over;
    lengthOnRelease.value = data.data.release;
  }
};

</script>

<template>
  <v-container fluid>
    <v-text-field v-model="comment" label="コメント" variant="underlined"></v-text-field>
    <v-radio-group v-model="selectedAction">
      <Radio label="なし" value="none" :modelValue="selectedAction"></Radio>
      <Radio label="基本" value="basic" :modelValue="selectedAction">
        <Nest label="押したとき">
          <AddFunctions v-model="basicOnPress" :other-profiles="props.otherProfiles"></AddFunctions>
        </Nest>
        <Nest label="押されているとき">
          <v-radio-group v-model="basicOnKeep">
            <Radio label="なし" value="none" :modelValue="basicOnKeep"></Radio>
            <Radio label="連射" value="rapid" :modelValue="basicOnKeep">
              <AddFunctions type="keyboard" v-model="basicOnKeepRapid" :other-profiles="props.otherProfiles">
              </AddFunctions>
              <Input beforeText="間隔" afterText="ms" v-model="basicOnKeepRapidInterval"
                :number-min-max="basicOnkeepRapidMinMax" :required="defaultRapidInterval"></Input>
              <Check label="一定時間経ってから" value="basic-onKeep-rapid-delay" v-model="checkBoxes">
                <Input beforeText="時間" afterText="ms" v-model="basicOnKeepRapidDelay" :number-min-max="delayMinMax"
                  :required="defaultDelay"></Input>
              </Check>
            </Radio>
            <Radio label="押されている間一時的に他のプロファイルを使う" value="another-profile" :modelValue="basicOnKeep">
              <v-select v-model="basicOnKeepAnotherProfile" label="プロファイル" density="compact" :item-props="itemProps"
                :items="props.otherProfiles" no-data-text="他のプロファイルがありません" return-object></v-select>
              <Check label="一定時間経ってから" value="basic-onKeep-anotherProfile-delay" v-model="checkBoxes">
                <Input beforeText="時間" afterText="ms" v-model="basicOnKeepAnotherProfileDelay"
                  :number-min-max="delayMinMax" :required="defaultDelay"></Input>
              </Check>
              <small style="display: block; padding-top: 8px;">※このボタンのプロファイルは変わりません</small>
            </Radio>
          </v-radio-group>
        </Nest>
        <Nest label="離したとき">
          <AddFunctions v-model="basicOnRelease" :other-profiles="props.otherProfiles"></AddFunctions>
        </Nest>
      </Radio>
      <Radio label="ボタンが押されるたびに切り替える" value="switch" :modelValue="selectedAction">
        <AddFunctions type="switch" v-model="switchFunc" :other-profiles="props.otherProfiles"></AddFunctions>
        <Check label="一定時間経ったらリセット" value="switch-reset-delay" v-model="checkBoxes">
          <Input beforeText="時間" afterText="ms" v-model="switchDelay" :number-min-max="delayMinMax"
            :required="defaultDelay"></Input>
        </Check>
        <Check label="別プロファイルに移行したらリセット" value="switch-reset-anotherProfile" v-model="checkBoxes">
          <small>※「一時的に他のプロファイルを使う」ではリセットされません</small>
        </Check>
      </Radio>
      <Radio label="連続して押された回数によって切り替える" value="count" :modelValue="selectedAction">
        <AddFunctions type="count" v-model="countFunc" :other-profiles="props.otherProfiles"></AddFunctions>
        <Input beforeText="認識間隔" afterText="ms" v-model="countInterval" :number-min-max="countIntervalMinMax"
          :required="defaultCounInterval"></Input>
      </Radio>
      <Radio label="ボタンが押される長さによって切り替える" value="length" :modelValue="selectedAction">
        <Input beforeText="時間" afterText="ms" v-model="lengthTime" :number-min-max="lengthMinMax"
          :required="defaultLength"></Input>
        <Nest :label="`${Number(lengthTime) / 1000}秒未満`" class="mt-2">
          <AddFunctions v-model="lengthUnder" :other-profiles="props.otherProfiles"></AddFunctions>
        </Nest>
        <Nest :label="`${Number(lengthTime) / 1000}秒以上`">
          <AddFunctions v-model="lengthOver" :other-profiles="props.otherProfiles"></AddFunctions>
        </Nest>
        <Nest label="離したとき">
          <AddFunctions v-model="lengthOnRelease" :other-profiles="props.otherProfiles"></AddFunctions>
        </Nest>
      </Radio>
    </v-radio-group>
  </v-container>
</template>
