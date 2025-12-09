import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5174,
    proxy: {
      // /api로 시작하는 모든 요청을 API 서버로 프록시
      '/api': {
        target: 'http://192.168.1.252:22450',
        changeOrigin: true,
        secure: false,
        ws: true,
      }
    }
  },  
})
