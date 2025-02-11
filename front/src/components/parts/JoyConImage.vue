<script setup lang="ts">
// import { ref, defineProps } from 'vue';
// import { computed, defineProps } from 'vue';
import { ref, computed, defineProps } from 'vue';
import units from '../units';
const { randstr } = units();

const identifier = randstr(8);
const props = defineProps({
  serial: { type: String, default: "" },
  type: { type: String, required: true },
  bodyColor: { type: String, default: "#0AB9E6" },
  buttonColor: { type: String, default: "#000000" },
  status: { type: Object, required: true },
});

const hilightColor = ref("yellow")
const colors = computed(() => {
  return {
    btn: props.buttonColor,
    body: props.bodyColor,
  };
});
const colorBtn = computed(() => {
  return colors.value.btn;
});
const colorBody = computed(() => {
  return colors.value.body;
});
const buttonHilights = computed(() => {
  const status = JSON.parse(JSON.stringify(props.status));
  for (const key in status) {
    if ([1, true].includes(status[key])) {
      status[key] = hilightColor.value;
    } else {
      status[key] = "none";
    }
  }
  const hilights = {
    sl: status.sl || "none",
    sr: status.sr || "none",
    stick: status.stick || "none",
    left: status.left || "none",
    right: status.right || "none",
    down: status.down || "none",
    up: status.up || "none",
    capture: status.capture || "none",
    minus: status.minus || "none",
    l: status.l || "none",
    zl: status.zl || "none",
    a: status.a || "none",
    y: status.y || "none",
    b: status.b || "none",
    x: status.x || "none",
    home: status.home || "none",
    plus: status.plus || "none",
    r: status.r || "none",
    zr: status.zr || "none",
  };
  return hilights;
});
const buttonHilightsSl = computed(() => {
  return buttonHilights.value.sl;
});
const buttonHilightsSr = computed(() => {
  return buttonHilights.value.sr;
});
const buttonHilightsStick = computed(() => {
  return buttonHilights.value.stick;
});
const buttonHilightsLeft = computed(() => {
  return buttonHilights.value.left;
});
const buttonHilightsRight = computed(() => {
  return buttonHilights.value.right;
});
const buttonHilightsDown = computed(() => {
  return buttonHilights.value.down;
});
const buttonHilightsUp = computed(() => {
  return buttonHilights.value.up;
});
const buttonHilightsCapture = computed(() => {
  return buttonHilights.value.capture;
});
const buttonHilightsMinus = computed(() => {
  return buttonHilights.value.minus;
});
const buttonHilightsL = computed(() => {
  return buttonHilights.value.l == "none" ? colors.value.btn : buttonHilights.value.l;
});
const buttonHilightsZl = computed(() => {
  return buttonHilights.value.zl;
});
const buttonHilightsA = computed(() => {
  return buttonHilights.value.a;
});
const buttonHilightsY = computed(() => {
  return buttonHilights.value.y;
});
const buttonHilightsB = computed(() => {
  return buttonHilights.value.b;
});
const buttonHilightsX = computed(() => {
  return buttonHilights.value.x;
});
const buttonHilightsHome = computed(() => {
  return buttonHilights.value.home;
});
const buttonHilightsPlus = computed(() => {
  return buttonHilights.value.plus;
});
const buttonHilightsR = computed(() => {
  return buttonHilights.value.r == "none" ? colors.value.btn : buttonHilights.value.r;
});
const buttonHilightsZr = computed(() => {
  return buttonHilights.value.zr;
});
</script>

<template>
  <div :id="props.serial" class="joycon-image" v-if="props.type == 'l'">
    <svg viewBox="0 0 507 1404" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
      xml:space="preserve" overflow="hidden">
      <defs>
        <filter id="fx0" x="-10%" y="-10%" width="120%" height="120%" filterUnits="userSpaceOnUse"
          primitiveUnits="userSpaceOnUse">
          <feComponentTransfer color-interpolation-filters="sRGB">
            <feFuncR type="discrete" tableValues="0 0" />
            <feFuncG type="discrete" tableValues="0 0" />
            <feFuncB type="discrete" tableValues="0 0" />
            <feFuncA type="linear" slope="1" intercept="0" />
          </feComponentTransfer>
          <feGaussianBlur stdDeviation="5.35773 5.34722" />
        </filter>
        <clipPath :id="`clip${props.serial}${identifier}`">
          <rect x="641" y="760" width="507" height="1404" />
        </clipPath>
      </defs>
      <g :clip-path="`url(#clip${props.serial}${identifier})`" transform="translate(-641 -760)">
        <path class="btn"
          d="M1112 852.843C1112 849.616 1114.62 847 1117.84 847L1141.21 847C1144.44 847 1147.06 849.616 1147.06 852.843L1147.06 2003.16C1147.06 2006.38 1144.44 2009 1141.21 2009L1117.84 2009C1114.62 2009 1112 2006.38 1112 2003.16Z"
          fill-rule="evenodd" />
        <g filter="url(#fx0)" transform="matrix(1.99608 0 0 2 639 759)">
          <g>
            <path
              d="M17.2788 576.165 17.2788 126.835C17.2788 66.0806 66.6265 16.8298 127.5 16.8298L233.639 16.8298C235.893 16.8298 237.721 18.654 237.721 20.9041L237.721 682.096C237.721 684.346 235.893 686.17 233.639 686.17L127.5 686.17C66.6265 686.17 17.2788 636.919 17.2788 576.165Z"
              fill="#0AB9E6" fill-rule="evenodd" />
          </g>
        </g>
        <path class="body" :style="colors.body"
          d="M669 1920.5 669 1003.5C669 879.512 769.512 779 893.5 779L1109.68 779C1114.28 779 1118 782.723 1118 787.315L1118 2136.69C1118 2141.28 1114.28 2145 1109.68 2145L893.5 2145C769.512 2145 669 2044.49 669 1920.5Z"
          fill="#0AB9E6" fill-rule="evenodd" />
        <path id="stick" class="btn"
          d="M806.5 1124C806.5 1071.81 849.033 1029.5 901.5 1029.5 953.967 1029.5 996.5 1071.81 996.5 1124 996.5 1176.19 953.967 1218.5 901.5 1218.5 849.033 1218.5 806.5 1176.19 806.5 1124Z"
          stroke="#000000" stroke-width="8" stroke-miterlimit="8" fill-rule="evenodd" />
        <path id="left" class="btn"
          d="M757.5 1539.5C757.5 1516.86 775.633 1498.5 798 1498.5 820.367 1498.5 838.5 1516.86 838.5 1539.5 838.5 1562.14 820.367 1580.5 798 1580.5 775.633 1580.5 757.5 1562.14 757.5 1539.5Z"
          stroke="#000000" stroke-width="8" stroke-miterlimit="8" fill-rule="evenodd" />
        <path id="right" class="btn"
          d="M947.5 1539.5C947.5 1516.86 965.632 1498.5 988 1498.5 1010.37 1498.5 1028.5 1516.86 1028.5 1539.5 1028.5 1562.14 1010.37 1580.5 988 1580.5 965.632 1580.5 947.5 1562.14 947.5 1539.5Z"
          stroke="#000000" stroke-width="8" stroke-miterlimit="8" fill-rule="evenodd" />
        <path id="down" class="btn"
          d="M854 1635.5C854 1613.13 872.132 1595 894.5 1595 916.867 1595 935 1613.13 935 1635.5 935 1657.87 916.867 1676 894.5 1676 872.132 1676 854 1657.87 854 1635.5Z"
          stroke="#000000" stroke-width="8" stroke-miterlimit="8" fill-rule="evenodd" />
        <path id="up" class="btn"
          d="M854 1448.5C854 1426.13 872.132 1408 894.5 1408 916.867 1408 935 1426.13 935 1448.5 935 1470.87 916.867 1489 894.5 1489 872.132 1489 854 1470.87 854 1448.5Z"
          stroke="#000000" stroke-width="8" stroke-miterlimit="8" fill-rule="evenodd" />
        <path id="capture" class="btn"
          d="M935 1763C935 1755.27 941.268 1749 949 1749L1005 1749C1012.73 1749 1019 1755.27 1019 1763L1019 1820C1019 1827.73 1012.73 1834 1005 1834L949 1834C941.268 1834 935 1827.73 935 1820Z"
          stroke="#000000" stroke-width="8" stroke-miterlimit="8" fill-rule="evenodd" />
        <path id="minus" class="btn"
          d="M997 893.5C997 891.567 998.567 890 1000.5 890L1077.5 890C1079.43 890 1081 891.567 1081 893.5L1081 907.5C1081 909.433 1079.43 911 1077.5 911L1000.5 911C998.567 911 997 909.433 997 907.5Z"
          stroke="#000000" stroke-width="8" stroke-miterlimit="8" fill-rule="evenodd" />
        <path id="l" class="btn-stroke" d="M687.603 907.307C732.535 823.233 820.609 771.242 915.928 772.523"
          stroke="#000000" stroke-width="20.625" stroke-miterlimit="8" fill="none" fill-rule="evenodd" />
        <path id="sl" class="btn body" :style="colors.body"
          d="M1129 1093.83C1129 1092.27 1130.27 1091 1131.83 1091L1143.17 1091C1144.73 1091 1146 1092.27 1146 1093.83L1146 1162.17C1146 1163.73 1144.73 1165 1143.17 1165L1131.83 1165C1130.27 1165 1129 1163.73 1129 1162.17Z"
          fill="#0AB9E6" stroke-width="8" stroke-miterlimit="8" fill-rule="evenodd" />
        <path id="sr" class="btn body" :style="colors.body"
          d="M1130 1706.67C1130 1705.19 1131.19 1704 1132.67 1704L1143.33 1704C1144.81 1704 1146 1705.19 1146 1706.67L1146 1774.33C1146 1775.81 1144.81 1777 1143.33 1777L1132.67 1777C1131.19 1777 1130 1775.81 1130 1774.33Z"
          fill="#0AB9E6" stroke-width="8" stroke-miterlimit="8" fill-rule="evenodd" />
        <path id="zl" d="M726.909 940.728C767.748 866.616 846.936 820.904 932.551 822.02" stroke-width="64.1667"
          stroke-miterlimit="8" fill="none" fill-rule="evenodd" />
      </g>
    </svg>
  </div>
  <div :id="props.serial" class="joycon-image" v-if="props.type == 'r'">
    <svg viewBox="0 0 506 1404" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
      xml:space="preserve" overflow="hidden">
      <defs>
        <filter id="fx0" x="-10%" y="-10%" width="120%" height="120%" filterUnits="userSpaceOnUse"
          primitiveUnits="userSpaceOnUse">
          <feComponentTransfer color-interpolation-filters="sRGB">
            <feFuncR type="discrete" tableValues="0 0" />
            <feFuncG type="discrete" tableValues="0 0" />
            <feFuncB type="discrete" tableValues="0 0" />
            <feFuncA type="linear" slope="1" intercept="0" />
          </feComponentTransfer>
          <feGaussianBlur stdDeviation="5.35773 5.34722" />
        </filter>
        <clipPath :id="`clip${props.serial}${identifier}`">
          <rect x="1313" y="759" width="506" height="1404" />
        </clipPath>
      </defs>
      <g :clip-path="`url(#clip${props.serial}${identifier})`" transform="translate(-1313 -759)">
        <path class="btn"
          d="M0 5.83287C-1.15581e-15 2.61147 2.61156 0 5.83307 0L29.1666 0C32.3881-1.15577e-15 34.9997 2.61147 34.9997 5.83287L34.9997 1156.17C34.9997 1159.39 32.3881 1162 29.1666 1162L5.83307 1162C2.61156 1162 0 1159.39 0 1156.17Z"
          fill-rule="evenodd" transform="matrix(-1 0 0 1 1348 846)" />
        <g filter="url(#fx0)" transform="matrix(1.99608 0 0 2 1312 758)">
          <g>
            <path
              d="M110.005 0 559.335 0C620.089-2.1304e-14 669.34 49.2509 669.34 110.005L669.34 215.936C669.34 218.186 667.516 220.01 665.266 220.01L4.07431 220.01C1.82413 220.01 0 218.186 0 215.936L0 110.005C-2.1304e-14 49.2509 49.2508-2.1304e-14 110.005-4.2608e-14Z"
              fill="#FF3C28" fill-rule="evenodd"
              transform="matrix(-6.13526e-17 -1 -1.00196 6.12323e-17 237.721 686.17)" />
          </g>
        </g>
        <path class="body" :style="colors.body"
          d="M224.5 0 1141.5 0C1265.49-4.34776e-14 1366 100.512 1366 224.5L1366 440.685C1366 445.277 1362.28 449 1357.69 449L8.31491 449C3.72271 449 0 445.277 0 440.685L0 224.5C-4.34775e-14 100.512 100.512-4.34776e-14 224.5-8.69551e-14Z"
          fill="#FF3C28" fill-rule="evenodd" transform="matrix(-6.12323e-17 -1 -1 6.12323e-17 1791 2144)" />
        <path id="stick" class="btn"
          d="M0 94.5C-1.20948e-14 42.3091 42.533-1.20311e-14 95-2.40622e-14 147.467-4.81245e-14 190 42.3091 190 94.5 190 146.691 147.467 189 95 189 42.533 189-6.04739e-14 146.691 0 94.5Z"
          stroke="#000000" stroke-width="8" stroke-miterlimit="8" fill-rule="evenodd"
          transform="matrix(-1 0 0 1 1654.5 1444.5)" />
        <path id="a" class="btn"
          d="M0 40.5001C-5.1562e-15 18.1325 18.1325-5.1562e-15 40.5001-1.03124e-14 62.8676-2.06248e-14 81.0001 18.1325 81.0001 40.5001 81.0001 62.8676 62.8676 81.0001 40.5001 81.0001 18.1325 81.0001-2.5781e-14 62.8676 0 40.5001Z"
          stroke="#000000" stroke-width="8" stroke-miterlimit="8" fill-rule="evenodd"
          transform="matrix(-1 0 0 1 1703.5 1083.5)" />
        <path id="y" class="btn"
          d="M0 40.5001C-5.1562e-15 18.1325 18.1325-5.1562e-15 40.5001-1.03124e-14 62.8676-2.06248e-14 81.0001 18.1325 81.0001 40.5001 81.0001 62.8676 62.8676 81.0001 40.5001 81.0001 18.1325 81.0001-2.5781e-14 62.8676 0 40.5001Z"
          stroke="#000000" stroke-width="8" stroke-miterlimit="8" fill-rule="evenodd"
          transform="matrix(-1 0 0 1 1513.5 1083.5)" />
        <path id="b" class="btn"
          d="M0 40.4999C-5.1562e-15 18.1324 18.1325-5.15618e-15 40.5001-1.03124e-14 62.8676-2.06247e-14 81.0001 18.1324 81.0001 40.4999 81.0001 62.8674 62.8676 80.9998 40.5001 80.9998 18.1325 80.9998-2.5781e-14 62.8674 0 40.4999Z"
          stroke="#000000" stroke-width="8" stroke-miterlimit="8" fill-rule="evenodd"
          transform="matrix(-1 0 0 1 1606 1179)" />
        <path id="x" class="btn"
          d="M0 40.4999C-5.1562e-15 18.1324 18.1325-5.15618e-15 40.5001-1.03124e-14 62.8676-2.06247e-14 81.0001 18.1324 81.0001 40.4999 81.0001 62.8674 62.8676 80.9998 40.5001 80.9998 18.1325 80.9998-2.5781e-14 62.8674 0 40.4999Z"
          stroke="#000000" stroke-width="8" stroke-miterlimit="8" fill-rule="evenodd"
          transform="matrix(-1 0 0 1 1606 992)" />
        <path id="home" class="btn"
          d="M0 51.5001C-6.55665e-15 23.0574 23.0574-6.55665e-15 51.5001-1.31133e-14L51.5001 0C79.9428-1.31133e-14 103 23.0574 103 51.5001L103 51.5001C103 79.9428 79.9428 103 51.5001 103L51.5001 103C23.0574 103 0 79.9428 0 51.5001Z"
          stroke="#000000" stroke-width="8" stroke-miterlimit="8" fill-rule="evenodd"
          transform="matrix(-1 0 0 1 1533 1741)" />
        <path id="plus" class="btn"
          d="M1382.5 893.993 1413.99 893.993 1413.99 862.5 1427.01 862.5 1427.01 893.993 1458.5 893.993 1458.5 908.007 1427.01 908.007 1427.01 939.5 1413.99 939.5 1413.99 908.007 1382.5 908.007Z"
          stroke="#000000" stroke-width="8" stroke-miterlimit="8" fill-rule="evenodd" />
        <path id="r" class="btn-stroke" d="M375.193 30.1031C459.267 75.035 511.258 163.109 509.977 258.427"
          stroke="#000000" stroke-width="20.625" stroke-miterlimit="8" fill="none" fill-rule="evenodd"
          transform="matrix(-6.12323e-17 -1 -1 6.12323e-17 1803.5 1281.5)" />
        <path id="sr" class="btn body" :style="colors.body"
          d="M0 2.66668C0 1.19391 1.19392-1.16173e-15 2.66669-1.16173e-15L13.3331 0C14.8059 -5.80866e-16 15.9998 1.19391 15.9998 2.66668L15.9998 70.3332C15.9998 71.806 14.8059 72.9999 13.3331 72.9999L2.66669 72.9999C1.19392 72.9999 0 71.806 0 70.3332Z"
          stroke-width="8" stroke-miterlimit="8" fill="#FF3C28" fill-rule="evenodd"
          transform="matrix(-1 0 0 1 1330 1091)" />
        <path id="sl" class="btn body" :style="colors.body"
          d="M0 2.6667C0 1.19392 1.19392-1.16174e-15 2.6667-1.16174e-15L13.3332 0C14.806 -5.80869e-16 15.9999 1.19392 15.9999 2.6667L15.9999 70.3335C15.9999 71.8063 14.806 73.0002 13.3332 73.0002L2.6667 73.0002C1.19392 73.0002 0 71.8063 0 70.3335Z"
          stroke-width="8" stroke-miterlimit="8" fill="#FF3C28" fill-rule="evenodd"
          transform="matrix(-1 0 0 1 1330 1703)" />
        <path id="zr" d="M335.272 27.9091C409.384 68.7482 455.096 147.936 453.98 233.551" stroke-width="64.1667"
          stroke-miterlimit="8" fill="none" fill-rule="evenodd"
          transform="matrix(-6.12323e-17 -1 -1 6.12323e-17 1761 1275)" />
      </g>
    </svg>
  </div>
</template>

<style scoped>
.joycon-image {
  width: 100%;
  height: 100%;
}

.joycon-image svg {
  height: 100%;
}

.btn {
  fill: v-bind(colorBtn);
}

.body {
  fill: v-bind(colorBody);
}

#sl {
  stroke: v-bind(buttonHilightsSl);
}

#sr {
  stroke: v-bind(buttonHilightsSr);
}

#stick {
  stroke: v-bind(buttonHilightsStick);
}

#left {
  stroke: v-bind(buttonHilightsLeft);
}

#right {
  stroke: v-bind(buttonHilightsRight);
}

#down {
  stroke: v-bind(buttonHilightsDown);
}

#up {
  stroke: v-bind(buttonHilightsUp);
}

#capture {
  stroke: v-bind(buttonHilightsCapture);
}

#minus {
  stroke: v-bind(buttonHilightsMinus);
}

#l {
  stroke: v-bind(buttonHilightsL);
}

#zl {
  stroke: v-bind(buttonHilightsZl);
}

#a {
  stroke: v-bind(buttonHilightsA);
}

#y {
  stroke: v-bind(buttonHilightsY);
}

#b {
  stroke: v-bind(buttonHilightsB);
}

#x {
  stroke: v-bind(buttonHilightsX);
}

#home {
  stroke: v-bind(buttonHilightsHome);
}

#plus {
  stroke: v-bind(buttonHilightsPlus);
}

#r {
  stroke: v-bind(buttonHilightsR);
}

#zr {
  stroke: v-bind(buttonHilightsZr);
}
</style>
