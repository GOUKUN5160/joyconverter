import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { version } from "./package.json";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  build: {
    outDir: '../web',
    emptyOutDir: true
  },
  define: {
    '__APP_VERSION__': JSON.stringify(version),
  },
})
