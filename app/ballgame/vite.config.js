import path from "path"
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from 'tailwindcss'
import { env } from "process"
import http from "https";
// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
  },
  server: {
    proxy:{
      '/login':{
        target:env.VITE_API_BASE_URL,
        changeOrigin:true,
        secure:false,
      },
      '/api':{
        target:env.VITE_API_BASE_URL,
        changeOrigin:true,
        secure:false
      }
    }
  },
})