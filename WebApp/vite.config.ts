import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/webapp/',
  server: {
    allowedHosts: ['social-stirred-polliwog.ngrok-free.app'],
    host: true,
    port: 5173
  },
})
