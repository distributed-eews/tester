# Dokumentasi Deployment untuk Layanan Queue

Layanan Queue ini bertujuan untuk mengonsumsi data dari topik Kafka yang akan diproses. Layanan ini dapat dideploy lebih dari satu instance untuk memastikan tidak ada layanan yang menganggur, dengan jumlah layanan yang kurang atau sama dengan jumlah partisi pada topik Kafka yang akan dikonsumsi datanya.

## Persyaratan

- Docker
- docker-compose
- Git

## Langkah 1: Clone Repositori

Clone repositori layanan Queue ke mesin lokal Anda menggunakan perintah berikut:

```bash
git clone https://github.com/distributed-eews/queue.git
cd queue
```

## Langkah 2: Atur Variabel Lingkungan

Ubah nama file `.env.example` menjadi `.env` dan atur variabel lingkungan berikut sesuai konfigurasi Anda:

```plaintext
BOOTSTRAP_SERVERS=<Alamat Kafka>
TOPIC_CONSUMER=<Nama topik Kafka yang akan dikonsumsi>
TOPIC_PRODUCER=<Nama topik Kafka yang akan dikirimkan data>
```

## Langkah 3: Konfigurasi Docker Compose

Tambahkan konfigurasi untuk setiap layanan queue pada file `docker-compose.yaml`. Pastikan untuk menambahkan layanan sejumlah partisi pada topik Kafka yang akan dikonsumsi datanya:

```yaml
version: '3'
services:
  eews-queue-1:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: eews-queue-1
    env_file:
      - .env
  eews-queue-2:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: eews-queue-2
    env_file:
      - .env
  # Tambahkan layanan queue lainnya sesuai kebutuhan
```

## Langkah 4: Mulai Kontainer Docker

Gunakan docker-compose untuk memulai layanan queue:

```bash
docker-compose up -d
```

## Langkah 5: Verifikasi Deployment

Pastikan kontainer queue berjalan tanpa masalah:

```bash
docker-compose ps
```

## Langkah 6: Pemantauan dan Penyesuaian

- Periksa ketersediaan layanan queue untuk memastikan tidak ada layanan yang menganggur.
- Sesuaikan jumlah layanan queue sesuai kebutuhan dengan jumlah partisi pada topik Kafka yang akan dikonsumsi datanya.

Dengan langkah-langkah ini, Layanan Queue Anda seharusnya berhasil didaftarkan dan berjalan di lingkungan Anda. Pastikan untuk memantau kinerja dan melakukan penyesuaian sesuai kebutuhan.
