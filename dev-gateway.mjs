#!/usr/bin/env node
// Local dev gateway mimicking deploy/Caddyfile (no dependencies).
//   /api/*                      -> dts-api         (127.0.0.1:8080)
//   /main, /app/*, vite assets  -> SPA dev server  (127.0.0.1:1420)
//   everything else             -> static site/dist (built Astro site)
import http from 'node:http';
import net from 'node:net';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.dirname(fileURLToPath(import.meta.url));
const SITE = path.join(ROOT, 'site', 'dist');
const PORT = Number(process.env.GATEWAY_PORT || 3000);
const API = { host: '127.0.0.1', port: 8080 };
const SPA = { host: '127.0.0.1', port: 1420 };

const SPA_PREFIXES = ['/main', '/app', '/assets', '/src', '/node_modules', '/@vite', '/@react-refresh', '/@id', '/@fs', '/vite.svg'];
const isSpa = (p) => SPA_PREFIXES.some((x) => p === x || p.startsWith(x + '/') || p.startsWith(x + '?'));
const target = (url) => {
  const p = new URL(url, 'http://x').pathname;
  if (p.startsWith('/api/')) return API;
  if (isSpa(p)) return SPA;
  return null;
};

const MIME = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.svg': 'image/svg+xml', '.ico': 'image/x-icon', '.json': 'application/json' };

function serveStatic(req, res) {
  let p = decodeURIComponent(new URL(req.url, 'http://x').pathname);
  if (p.length > 1 && p.endsWith('/')) p = p.slice(0, -1);
  const candidates = [p, p + '.html', path.join(p, 'index.html')];
  for (const c of candidates) {
    const f = path.join(SITE, c);
    if (!f.startsWith(SITE)) continue;
    if (fs.existsSync(f) && fs.statSync(f).isFile()) {
      res.writeHead(200, { 'Content-Type': MIME[path.extname(f)] || 'application/octet-stream' });
      return fs.createReadStream(f).pipe(res);
    }
  }
  res.writeHead(404, { 'Content-Type': 'text/plain' });
  res.end('Not found (did you run `npm run build` in site/ ?)');
}

const server = http.createServer((req, res) => {
  const t = target(req.url);
  if (!t) return serveStatic(req, res);
  const up = http.request({ ...t, path: req.url, method: req.method, headers: req.headers }, (r) => {
    res.writeHead(r.statusCode, r.headers);
    r.pipe(res);
  });
  up.on('error', () => { res.writeHead(502); res.end('Bad gateway: ' + t.port); });
  req.pipe(up);
});

// WebSocket upgrade (Vite HMR)
server.on('upgrade', (req, socket, head) => {
  const t = target(req.url) || SPA;
  const up = net.connect(t.port, t.host, () => {
    up.write(`${req.method} ${req.url} HTTP/1.1\r\n` + Object.entries(req.headers).map(([k, v]) => `${k}: ${v}`).join('\r\n') + '\r\n\r\n');
    if (head?.length) up.write(head);
    socket.pipe(up).pipe(socket);
  });
  up.on('error', () => socket.destroy());
  socket.on('error', () => up.destroy());
});

server.listen(PORT, () => console.log(`gateway on http://localhost:${PORT}`));
