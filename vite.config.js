import { defineConfig } from 'vite'
import { resolve } from 'path'

export default defineConfig({
  root: '.',
  build: {
    outDir: 'static/dist',
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'assets', 'main.js')
      }
    }
  }
})
