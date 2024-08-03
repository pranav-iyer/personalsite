import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import {promises as fs} from "node:fs";

const CSS_CACHE_KEY =
  "92a1899ea9a7749a2434f7f7115a8bf7adfd1c87b2f259016181e68e9bdcc94b";

const injectCssPlugin = async (baseUrl: string) => {
  const data = await fs.readFile(
    'compress_info.json',
    "utf8",
  );
  const compress_info = JSON.parse(data)
  return {
    name: 'inject-css',
    transformIndexHtml: () => compress_info.stylesheets.map(s => ({
      tag: 'link',
      attrs: {
        media: 'screen',
        rel: 'stylesheet',
        href: `${baseUrl}${s}`
      }
    })),
  }
}

// https://vitejs.dev/config/
export default defineConfig(async ({ command, mode }) => {
  const env = loadEnv(mode, process.cwd());
  return {
    plugins: [react(), injectCssPlugin(env.VITE_API_BASE_URL)],
    server: {
      proxy: {
        '/pranav-tracker': 'http://localhost:8000',
        '/search': 'http://localhost:8000'
      }
    }
  };
});
