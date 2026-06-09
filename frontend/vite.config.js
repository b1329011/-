import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
	const env = loadEnv(mode, process.cwd(), "");
	const apiBase = env.VITE_API_BASE_URL || "http://localhost:8000/api/";
	// 取出 origin (去掉 /api/ 路徑)
	const apiOrigin = new URL(apiBase).origin;

	return {
		plugins: [react()],
		base: "/nojo/",
		server: {
			allowedHosts: true,
			proxy: {
				"/api": {
					target: apiOrigin,
					changeOrigin: true,
					secure: false,
				},
			},
		},
	};
});
