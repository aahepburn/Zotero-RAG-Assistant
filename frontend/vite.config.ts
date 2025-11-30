import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";

export default defineConfig({
  plugins: [react()],
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
      }
    }
  }
});
