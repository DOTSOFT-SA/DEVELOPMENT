import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

// Load environment variables
export default defineConfig(({ mode }) => {
  // Load .env file based on the current mode
  const env = loadEnv(mode, process.cwd(), "");

  return {
    plugins: [react()],
    server: {
      port: parseInt(env.VITE_FRONTEND_PROJECT_PORT) || 5173, // Read VITE_PORT safely
    },
  };
});
