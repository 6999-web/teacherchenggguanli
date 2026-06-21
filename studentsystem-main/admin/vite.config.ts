import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import Components from 'unplugin-vue-components/vite'
import { resolve } from 'path'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd())

  return {
    plugins: [
      vue(),
      Components({
        dts: true,
        resolvers: []
      })
    ],
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src')
      }
    },
    server: {
      host: '0.0.0.0',
      port: 5005,
      proxy: {
        '/api': {
          target: 'http://localhost:5006',
          changeOrigin: true
        },
        '/uploads': {
          target: 'http://localhost:5006',
          changeOrigin: true
        }
      }
    },
    build: {
      rollupOptions: {
        input: {
          main: resolve(__dirname, 'index.html')
        }
      }
    },
    define: {
      'process.env': env
    },
  }
})
