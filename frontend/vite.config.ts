import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";

export default defineConfig({
  plugins: [react()],
  base: "./", // Use relative paths for assets in production
  server: {
    port: 5173,
    proxy: {
      "/chat": {
        target: "http://localhost:8000",
        changeOrigin: true
      },
      "/index_library": {
        target: "http://localhost:8000",
        changeOrigin: true
      },
      "/index_status": {
        target: "http://localhost:8000",
        changeOrigin: true
      },
      "/index_stats": {
        target: "http://localhost:8000",
        changeOrigin: true
      },
      "/index_cancel": {
        target: "http://localhost:8000",
        changeOrigin: true
      },
      "/open_pdf": {
        target: "http://localhost:8000",
        changeOrigin: true
      },
      "/search_items": {
        target: "http://localhost:8000",
        changeOrigin: true
      },
      "/ollama_status": {
        target: "http://localhost:8000",
        changeOrigin: true
      },
      "/providers": {
        target: "http://localhost:8000",
        changeOrigin: true
      },
      "/settings": {
        target: "http://localhost:8000",
        changeOrigin: true
      },
      "/db_health": {
        target: "http://localhost:8000",
        changeOrigin: true
      },
      "/embedding_models": {
        target: "http://localhost:8000",
        changeOrigin: true
      },
      "/profiles": {
        target: "http://localhost:8000",
        changeOrigin: true
      }
    }
  }
});
