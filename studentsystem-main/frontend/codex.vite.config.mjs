import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import Components from 'unplugin-vue-components/vite'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue(), Components({ dts: true, resolvers: [] })],
  resolve: { alias: { '@': resolve(process.cwd(), 'src') } },
  server: {
    host: '127.0.0.1',
    port: 5004,
    proxy: {
      '/api': { target: 'http://127.0.0.1:5006', changeOrigin: true },
      '/uploads': { target: 'http://127.0.0.1:5006', changeOrigin: true }
    }
  },
  optimizeDeps: { include: ['@tabler/icons-vue'] }
})