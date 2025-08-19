import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  appType: "spa",
  root: ".",     
  base: "/",     
  server: {
    host: "0.0.0.0",
    port: 5174,
    strictPort: true,
    proxy: {
      "/api": {
        target: "http://localhost:8800",  // ver de poner el servicio fastapi:8800
        changeOrigin: true,
        rewrite: p => p.replace(/^\/api/, ""),
      },
    },
  },
});
