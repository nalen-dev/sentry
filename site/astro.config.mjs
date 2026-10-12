import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://sentrydashboard.com',
  trailingSlash: 'never',
  build: { format: 'file' },
  server: { port: 4321 },
  vite: {
    server: {
      // Dev convenience: forward API + SPA routes to the other dev servers
      proxy: {
        '/api': 'http://127.0.0.1:8080',
      },
    },
  },
});
