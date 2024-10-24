<script setup lang="ts">
import { ref, defineProps, watch, onMounted } from "vue";
import { useTheme } from "vuetify";
import units from "../../units";
const { randstr } = units();

const identifier = randstr(10);

const props = defineProps({
  size: { type: Number, required: false, default: 200 },
  thickness: { type: Number, required: false, default: 5 },
  stickRatio: { type: Number, required: false, default: 6 },
  position: { type: Object, required: true },
  splittedNum: { type: Number, required: true },
  scale: { type: Number, required: false, default: 1 },
});

let ctx: any;
const theme = useTheme();
const stickRadius = ref(0);
const wholeSize = ref(0);
const percentageX = ref(-810);
const percentageY = ref(-810);

watch(theme.global.name, () => {
  setValues();
  update();
});
watch(() => [props.size, props.thickness, props.stickRatio], () => {
  stickRadius.value = props.size / props.stickRatio;
  wholeSize.value = props.size - (stickRadius.value * 2) - props.thickness;
  setValues();
  update();
});

const setValues = () => {
  stickRadius.value = props.size / props.stickRatio;
  wholeSize.value = props.size - (stickRadius.value * 2) - props.thickness;
  ctx.lineWidth = props.thickness;
  const color = theme.global.name.value == "dark" ? "rgb(190 190 190)" : "rgb(20 20 20)";
  ctx.strokeStyle = color;
  ctx.fillStyle = color;
};

onMounted(() => {
  const canvas: any = document.querySelector(`#canvas${identifier}`);
  ctx = canvas.getContext("2d");
  setValues();
  init();
  update();
});



const init = () => {
  ctx.clearRect(0, 0, props.size, props.size);
  _drawCircle(props.size / 2, props.size / 2, props.size / 2 - ctx.lineWidth, false);
};

const update = () => {
  if (!(props.position.horizontal == undefined || props.position.vertical == undefined)) {
    const x = (wholeSize.value / props.splittedNum) * props.position.horizontal;
    const y = (wholeSize.value / props.splittedNum) * props.position.vertical;
    drawCircle(x + stickRadius.value + (props.thickness / 2), wholeSize.value - y + stickRadius.value + (props.thickness / 2), stickRadius.value, true);
    percentageX.value = calcPercentage(props.position.horizontal - props.splittedNum / 2);
    percentageY.value = calcPercentage(props.position.vertical - props.splittedNum / 2);
  } else {
    init();
    percentageX.value = -810;
    percentageY.value = -810;
  }
};
watch(() => props.position, update);

const calcPercentage = (num: number) => {
  return num * 100 / (props.splittedNum / 2);
};

const drawCircle = (x: number, y: number, radius: number, fill: boolean) => {
  init();
  _drawCircle(x, y, radius, fill);
};
const _drawCircle = (x: number, y: number, radius: number, fill: boolean) => {
  ctx.beginPath();
  ctx.arc(x, y, radius, 0, 2 * Math.PI);
  ctx.closePath();
  if (fill) {
    ctx.fill();
  } else {
    ctx.stroke();
  }
};
</script>

<template>
  <div id="stick-wrapper">
    <canvas :id="`canvas${identifier}`" :width="props.size" :height="props.size"></canvas>
    <div style="text-align: center;">
      X: {{ percentageX != -810 ? percentageX : "--" }}%, Y: {{ percentageY != -810 ? percentageY : "--" }}%
    </div>
  </div>
</template>

<style scoped>
#stick-wrapper {
  /* transform-origin: top center; */
  /* transform: scale(v-bind(scale)); */
  zoom: v-bind(props.scale);
  display: inline-block;
  width: v-bind(`${props.size}px`);
}
</style>
