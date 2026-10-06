import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  build: {
    outDir: "dist/client",
    rollupOptions: {output: {manualChunks(id) {
      if (id.includes('node_modules')) {
        // Both three chunks load lazily, in parallel, with the 3D cut viewer.
        // The WebGL renderer and its shaders alone exceed Vite's 500 KB warning,
        // so this split keeps each request under it; total bytes are unchanged.
        if (id.includes('/three/build/three.module.js')) return 'three-renderer';
        if (id.includes('/three/')) return 'three';
        if (/recharts|d3-|victory-vendor|decimal.js/.test(id)) return 'charts';
        return 'runtime';
      }
    }}},
  },
  optimizeDeps: {
    include: ["react", "react-dom/client"],
  },
  server: {
    host: "127.0.0.1",
    allowedHosts: ["terminal.local"],
    proxy: { "/api": "http://127.0.0.1:4174" },
    warmup: {
      clientFiles: ["./src/main.jsx"],
    },
  },
  plugins: [react()],
});
