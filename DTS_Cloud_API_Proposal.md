# Proposal Pengembangan Sistem DTS: Web Access & REST API Integration

Berikut adalah draf materi presentasi yang dapat Anda gunakan. Struktur ini dirancang agar mudah dipahami oleh klien (baik dari sisi manajemen maupun teknis).

---

## SLIDE 1: Judul
**Sentry DTS SCADA: Next-Generation Cloud & API Integration**
*Transformasi dari Sistem Lokal menuju Ekosistem Terpusat dan Terbuka*

---

## SLIDE 2: Latar Belakang & Objektif
**Kondisi Saat Ini:**
- Sistem berjalan secara terisolasi (lokal) di area *site*.
- Akses data terbatas hanya dari PC Operator (Desktop App).
- Tidak ada jalur standar untuk berbagi data sensor dengan platform/sistem lain.

**Tujuan Pengembangan:**
1. **Aksesibilitas Tinggi:** Memungkinkan *monitoring* secara langsung dari mana saja melalui Web Browser tanpa harus berada di *site*.
2. **Integrasi Terbuka:** Menyediakan jalur REST API standar agar data suhu dan alarm dapat ditarik oleh sistem pihak ketiga (contoh: Sistem ERP, Dashboard Terpusat Perusahaan, dll).
3. **Keamanan Ekstra:** Memisahkan data *public* (Cloud) dengan data operasional *site* (Lokal) agar unit fisik DTS terhindar dari risiko serangan siber.

---

## SLIDE 3: Topologi Arsitektur Baru (Cloud Sync)

Pendekatan yang kita gunakan adalah **Cloud Synchronization (Push Method)**. Unit lokal tidak pernah membuka jalur untuk diakses dari luar (lebih aman). Sebaliknya, unit lokal yang akan aktif mengirimkan data ke Cloud.

```mermaid
flowchart TD
  subgraph OnPremise [Lokal / Site]
    direction TB
    DTS[DTS Unit Fisik] -->|Kabel FO| Sensor
    DTS -->|TCP/IP| LocalDB[(Local MySQL\n192.168.1.64)]
    Sync[Rust Sync Agent] -->|Membaca Data Baru| LocalDB
  end

  subgraph Cloud [Cloud Infrastructure]
    direction TB
    Sync -->|HTTPS Push / WSS| CloudAPI[Rust Backend API]
    CloudAPI <--> CloudDB[(Cloud Database)]
  end

  subgraph EndUsers [Akses Pengguna]
    direction TB
    WebApp[Web Dashboard\n(React/Vite)] <-->|Membaca Data via API| CloudAPI
    ThirdParty[Sistem Eksternal / Klien] <-->|Tarik Data via REST API| CloudAPI
  end
  
  classDef local fill:#e2f0d9,stroke:#548235,stroke-width:2px;
  classDef cloud fill:#ddebf7,stroke:#2e75b6,stroke-width:2px;
  classDef users fill:#fff2cc,stroke:#d6b656,stroke-width:2px;
  
  class OnPremise local;
  class Cloud cloud;
  class EndUsers users;
```

---

## SLIDE 4: Pilihan Teknologi & Keamanan
Kami merancang sistem ini dengan standar performa dan keamanan industri kelas atas.

**Teknologi Utama:**
- **Backend (API & Sync):** Menggunakan bahasa pemrograman **RUST**. Rust menjamin performa super cepat (sekelas C++) namun dengan jaminan keamanan memori (anti-kebocoran data/memori), sangat cocok untuk pemrosesan data sensor *real-time*.
- **Frontend (Web):** React.js (TypeScript) untuk antarmuka yang sangat responsif layaknya aplikasi desktop.
- **Database:** Relational Database tersinkronisasi.

**Sistem Keamanan:**
- **Web App:** Dilengkapi sistem *Otentikasi (Login)* dan *Role-Based Access Control* (Level Admin, Operator, Viewer).
- **REST API:** Dilindungi dengan **API Key** dan **Rate Limiting** (membatasi jumlah permintaan agar server tidak *down*).
- **Enkripsi:** Seluruh aliran data dari *site* ke cloud, dan cloud ke *user* dilindungi oleh enkripsi SSL/TLS (HTTPS).

---

## SLIDE 5: Gambaran REST API (Untuk Developer Klien)
Sistem Sentry DTS akan menyediakan spesifikasi API modern berbasis JSON yang siap dikonsumsi oleh *developer* sistem klien.

### Endpoint Utama yang Disediakan:

#### 1. Mendapatkan Status Suhu Terkini (*Live*)
`GET /api/v1/temperatures/live`
Mengembalikan data suhu terakhir dari seluruh segmen/zona yang telah dikonfigurasi.

**Contoh Response:**
```json
{
  "status": "success",
  "timestamp": "2026-09-30T15:45:00Z",
  "data": [
    {
      "segment": "TN TCM 1",
      "group": "TCM16",
      "temperature": 34.5,
      "status": "NORMAL"
    },
    {
      "segment": "ASection32",
      "group": "BC4 A",
      "temperature": 45.2,
      "status": "WARNING"
    }
  ]
}
```

#### 2. Menarik Data Historis (*History*)
`GET /api/v1/temperatures/history?group=TCM16&start=2026-09-01T00:00:00Z&end=2026-09-30T00:00:00Z`
Mendapatkan rekap suhu pada rentang waktu tertentu untuk keperluan *reporting* atau analisis *Big Data* pihak klien.

#### 3. Memantau Alarm (*Alarms*)
`GET /api/v1/alarms/active`
Menampilkan daftar peringatan (Warning/Critical) yang saat ini sedang aktif dan belum tertangani.

---

## SLIDE 6: Keuntungan Finansial & Operasional (Value Proposition)
1. **Skalabilitas:** Jika ada penambahan area (*site*) baru, manajemen pusat bisa memantaunya dalam satu Dashboard Web yang sama.
2. **Efisiensi Waktu:** Pihak eksternal (misal divisi *maintenance*) dapat menarik data kerusakan langsung ke aplikasi mereka via API tanpa harus menelepon operator di lapangan.
3. **Kesiapan Industri 4.0:** Sistem yang memiliki REST API otomatis menjadikan infrastruktur perusahaan siap untuk diintegrasikan dengan AI, *Machine Learning*, atau *Big Data Analytics* di masa depan.
