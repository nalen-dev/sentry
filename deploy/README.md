# Deployment Panduan DTS Cloud SCADA (VPS)

Panduan ini menjelaskan cara melakukan deploy backend, database, dan frontend web sistem DTS SCADA ke Virtual Private Server (VPS).

---

## 1. Arsitektur Komponen di VPS

1. **PostgreSQL 16**: Database cloud untuk master segmen, kondisi live terkini, agregat historis (1 menit & 1 jam), serta log alarm.
2. **`dts-api` (Rust Axum)**: Backend performa tinggi yang menangani:
   - Ingest data dari Site Agent via `X-API-Key`
   - Autentikasi JWT login Web (`/api/v1/auth/login`)
   - REST API data Web Dashboard, Chart, Spatial, & Logs
3. **Caddy Reverse Proxy**:
   - Menyajikan Single Page Application (SPA) React Web (`dist-web`)
   - Reverse-proxy request `/api/*` langsung ke `dts-api:8080`
   - Otomatis mengelola sertifikat SSL/TLS HTTPS gratis dari Let's Encrypt jika domain dimasukkan ke `Caddyfile`.

---

## 2. Persyaratan VPS

- **Sistem Operasi**: Ubuntu 22.04 LTS / Debian 12 / sejenisnya
- **Spesifikasi Minimal**:
  - 1 vCPU
  - 1 GB - 2 GB RAM
  - 20 GB Disk SSD
- **Software**: Docker dan Docker Compose (`docker compose version`)

---

## 3. Langkah Instalasi di VPS

### A. Clone / Upload Repository ke VPS
```bash
git clone <repository_url> DTS-Reader
cd DTS-Reader
```

### B. Siapkan File Konfigurasi Domain (Opsional tapi Direkomendasikan)
Jika Anda memiliki nama domain (misal: `dts.perusahaan.com`), edit file `deploy/Caddyfile`:

```caddy
dts.perusahaan.com {
    encode gzip zstd

    handle /api/* {
        reverse_proxy api:8080
    }

    handle {
        root * /srv
        try_files {path} /index.html
        file_server
    }
}
```
*Catatan: Caddy akan otomatis mengaktifkan HTTPS tanpa perlu konfigurasi certbot manual.*

### C. Build Frontend Web
Sebelum menjalankan container (atau jika menggunakan volume `dist-web`):
```bash
cd app
npm install
npm run build:web
cd ..
```

### D. Jalankan Layanan dengan Docker Compose
```bash
cd deploy
docker compose up -d --build
```

Periksa status container:
```bash
docker compose ps
docker compose logs -f api
```

---

## 4. Setup Awal: Pembuatan API Key untuk Unit Site (Agent)

Setelah `dts-api` menyala di VPS, buat API Key khusus untuk unit DTS lokal di site tambang/pabrik:

```bash
docker compose exec api /app/dts-api create-key SITE_UTAMA agent
```

Output akan memberikan key (contoh: `dts_a1b2c3d4...`).
**Simpan key ini** untuk dikonfigurasikan pada environment variable `dts-agent` di komputer lokal site:

```bash
# Pada unit komputer lokal di site:
export DTS_CLOUD_URL="https://dts.perusahaan.com/api/v1"
export DTS_API_KEY="<key_dari_output_di_atas>"
./dts-agent
```

---

## 5. Akun Pengguna Default Web

Ketika database pertama kali dibuat, akun default berikut otomatis diinisialisasi:

| Username | Password | Role | Akses |
|---|---|---|---|
| `admin` | `admin123` | ADMINISTRATOR | Full Dashboard, Chart, Logs, Settings |
| `operator` | `operator123` | OPERATOR | Dashboard, Chart, Logs |

*Token JWT berlaku selama 7 hari sebelum pengguna diminta login ulang secara otomatis.*

---

## 6. Pemeliharaan & Backup Database

Untuk melakukan backup database PostgreSQL:
```bash
docker compose exec -T db pg_dump -U dts_user dts | gzip > backup_$(date +%Y%m%d).sql.gz
```

Untuk me-restore database dari backup:
```bash
gunzip -c backup_20261012.sql.gz | docker compose exec -T db psql -U dts_user -d dts
```
