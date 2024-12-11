# Dokumentasi Deployment untuk Layanan Picker

Layanan Picker ini bertujuan untuk melakukan prediksi dengan berintegrasi dengan Machine Learning melalui REST API. Layanan ini juga dapat dideploy lebih dari satu instance untuk memastikan tidak ada layanan yang menganggur, dengan jumlah layanan yang kurang atau sama dengan jumlah partisi pada topik Kafka yang akan dikonsumsi datanya.

## Persyaratan

- Docker
- docker-compose
- Git

## Langkah 1: Clone Repositori

Clone repositori layanan Picker ke mesin lokal Anda menggunakan perintah berikut:

```bash
git clone https://github.com/distributed-eews/picker.git
cd picker
```

## Langkah 2: Atur Variabel Lingkungan

Ubah nama file `.env.example` menjadi `.env` dan atur variabel lingkungan berikut sesuai konfigurasi Anda:

```plaintext
BOOTSTRAP_SERVERS=<Alamat Kafka>
TOPIC_CONSUMER=<Nama topik Kafka yang akan dikonsumsi>
TOPIC_PRODUCER=<Nama topik Kafka yang akan dikirimkan data>
ML_URL=<Base URL REST API Machine Learning>
REDIS_HOST=<Host Redis>
REDIS_PORT=<Port Redis>
```

## Langkah 3: Konfigurasi Docker Compose

Tambahkan konfigurasi untuk setiap layanan picker pada file `docker-compose.yaml`. Pastikan untuk menambahkan layanan sejumlah partisi pada topik Kafka yang akan dikonsumsi datanya:

```yaml
version: '3'
services:
  eews-picker-1:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: eews-picker-1
    env_file:
      - .env
  eews-picker-2:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: eews-picker-2
    env_file:
      - .env
  # Tambahkan layanan picker lainnya sesuai kebutuhan
```

## Langkah 4: Mulai Kontainer Docker

Gunakan docker-compose untuk memulai layanan picker:

```bash
docker-compose up -d
```

## Langkah 5: Verifikasi Deployment

Pastikan kontainer picker berjalan tanpa masalah:

```bash
docker-compose ps
```

## Langkah 6: Pemantauan dan Penyesuaian

- Periksa ketersediaan layanan picker untuk memastikan tidak ada layanan yang menganggur.
- Sesuaikan jumlah layanan picker sesuai kebutuhan dengan jumlah partisi pada topik Kafka yang akan dikonsumsi datanya.

Dengan langkah-langkah ini, Layanan Picker Anda seharusnya berhasil didaftarkan dan berjalan di lingkungan Anda. Pastikan untuk memantau kinerja dan melakukan penyesuaian sesuai kebutuhan.
