import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',  // Allow external connections
    port: 5173,       // Default Vite port (can adjust as needed)
    proxy: {
      '/api': {
        target: 'http://192.168.1.185:8000',
        changeOrigin: true,
      },
    },
  }
})
