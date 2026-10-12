#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

PG_DIR="$DIR/.local_postgres_data"
PG_BIN="/usr/lib/postgresql/16/bin"
PG_PORT=54329
PG_USER="$USER"
DB_NAME="dts"

cleanup() {
    echo ""
    echo "==========================================="
    echo "🛑 Menghentikan seluruh proses lokal..."
    echo "==========================================="
    if [ -n "$AGENT_PID" ] && kill -0 "$AGENT_PID" 2>/dev/null; then kill "$AGENT_PID" 2>/dev/null || true; fi
    if [ -n "$API_PID" ] && kill -0 "$API_PID" 2>/dev/null; then kill "$API_PID" 2>/dev/null || true; fi
    if [ -n "$GW_PID" ] && kill -0 "$GW_PID" 2>/dev/null; then kill "$GW_PID" 2>/dev/null || true; fi
    if [ -n "$WEB_PID" ] && kill -0 "$WEB_PID" 2>/dev/null; then kill "$WEB_PID" 2>/dev/null || true; fi
    if [ -f "$PG_DIR/postmaster.pid" ]; then
        "$PG_BIN/pg_ctl" -D "$PG_DIR" stop -m fast >/dev/null 2>&1 || true
    fi
    echo "✅ Semua proses berhasil dihentikan."
}
trap cleanup EXIT INT TERM

echo "==========================================="
echo "🚀 Sentry DTS Cloud & Web - Local Test Lab"
echo "==========================================="

# 1. Pastikan PostgreSQL lokal cluster siap
if [ ! -d "$PG_DIR" ]; then
    echo "📦 Menginisialisasi database PostgreSQL lokal di .local_postgres_data..."
    "$PG_BIN/initdb" -D "$PG_DIR" -A trust >/dev/null 2>&1
fi

if ! [ -f "$PG_DIR/postmaster.pid" ]; then
    echo "🐘 Menjalankan PostgreSQL lokal (port $PG_PORT)..."
    "$PG_BIN/pg_ctl" -D "$PG_DIR" -o "-p $PG_PORT -k /tmp" -l "$PG_DIR/pg.log" start -w
fi

# Buat database jika belum ada
psql -h 127.0.0.1 -p $PG_PORT -U "$PG_USER" -d postgres -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || \
psql -h 127.0.0.1 -p $PG_PORT -U "$PG_USER" -d postgres -qc "CREATE DATABASE $DB_NAME"

export DATABASE_URL="postgres://$PG_USER@127.0.0.1:$PG_PORT/$DB_NAME"
export BIND_ADDR="127.0.0.1:8080"

# 2. Build & Generate API Key
echo "🔨 Mengompilasi dts-api dan dts-agent..."
cargo build -q -p dts-api -p dts-agent

echo "🔑 Membuat/Mengambil API Key untuk agent..."
AGENT_KEY=$(target/debug/dts-api create-key LOCAL_SITE agent | tail -n 1)

# 3. Jalankan dts-api
echo "🌐 Menjalankan Backend Cloud API di http://127.0.0.1:8080..."
target/debug/dts-api > /tmp/dts_api.log 2>&1 &
API_PID=$!
sleep 2

# 4. Jalankan dts-agent (jika MySQL lokal aktif)
if mysql -udbeaver -p"Admin!12345Dbeaver" -h127.0.0.1 -e "SELECT 1" >/dev/null 2>&1; then
    echo "📡 Menjalankan Sync Agent (membaca data dari MySQL dtscontroler)..."
    export DTS_CLOUD_URL="http://127.0.0.1:8080/api/v1"
    export DTS_API_KEY="$AGENT_KEY"
    export DTS_QUEUE_PATH="$DIR/.local_agent_queue.db"
    export DTS_LIVE_INTERVAL_SECS=3
    export DTS_MYSQL_HOST="127.0.0.1"
    export DTS_MYSQL_PORT="3306"
    export DTS_MYSQL_USER="dbeaver"
    export DTS_MYSQL_PASS="Admin!12345Dbeaver"
    export DTS_MYSQL_NAME="dtscontroler"

    target/debug/dts-agent > /tmp/dts_agent.log 2>&1 &
    AGENT_PID=$!
    echo "✅ Agent aktif! Data live dialirkan dari MySQL ke Cloud."
else
    echo "⚠️  MySQL lokal tidak terdeteksi aktif. Agent dilewati (API & Web tetap bisa dites)."
fi

# 5. Jalankan Web Frontend
echo "💻 Menjalankan Web Frontend di http://localhost:1420..."
cd app
npm run dev:web > /tmp/dts_web.log 2>&1 &
WEB_PID=$!
cd ..

echo "🏠 Build situs statis (homepage/docs/login) + gateway di http://localhost:3000..."
(cd site && ([ -d node_modules ] || npm install >/dev/null 2>&1) && npm run build >/dev/null 2>&1)
node dev-gateway.mjs > /tmp/dts_gateway.log 2>&1 &
GW_PID=$!

sleep 3

echo ""
echo "=========================================================="
echo "🎉 SISTEM SIAP DIUJI DI BROWSER!"
echo "=========================================================="
echo "👉 Buka Browser Anda di : http://localhost:3000   (homepage -> /login -> /main -> /app)"
echo "👉 Akun Login Admin     : admin / admin123"
echo "👉 Akun Login Operator  : operator / operator123"
echo "👉 Backend API Health   : http://localhost:8080/health"
echo "👉 Log API              : tail -f /tmp/dts_api.log"
echo "👉 Log Agent            : tail -f /tmp/dts_agent.log"
echo "=========================================================="
echo "Tekan [Ctrl + C] kapan saja untuk menghentikan seluruh layanan."
echo ""

wait
