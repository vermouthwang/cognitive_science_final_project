import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/logo-generator': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/collaborator': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/evaluator': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/consultant': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
