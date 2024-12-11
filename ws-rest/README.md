# Dokumentasi Deployment untuk Layanan WS-REST

Layanan WS-REST berfungsi sebagai gateway untuk mengakses microservices. Hanya ada satu instance layanan WS-REST yang dideploy. Layanan ini membutuhkan layanan producer untuk berfungsi dan pastikan bahwa layanan producer dapat dihubungi oleh layanan ini.

## Persyaratan

- Docker
- docker-compose
- Git

## Langkah 1: Clone Repositori

Clone repositori layanan WS-REST ke mesin lokal Anda menggunakan perintah berikut:

```bash
git clone https://github.com/nama-pengguna-anda/ws-rest.git
cd ws-rest
```

## Langkah 2: Atur Variabel Lingkungan

Ubah nama file `.env.example` menjadi `.env` dan atur variabel lingkungan berikut sesuai konfigurasi Anda:

```plaintext
BOOTSTRAP_SERVERS=<Alamat Kafka>
TOPIC_CONSUMERS=<Daftar topik yang akan dikonsumsi dipisahkan dengan koma, tanpa spasi>
PORT=<Port layanan WS-REST>
PRODUCER_SERVICE=<Alamat layanan producer/load balancer nginx>
REDIS_HOST=<Alamat Redis>
```

## Langkah 3: Mulai Kontainer Docker

Gunakan docker-compose untuk memulai layanan WS-REST:

```bash
docker-compose up -d
```

## Langkah 4: Verifikasi Deployment

Pastikan kontainer WS-REST berjalan tanpa masalah:

```bash
docker-compose ps
```

## Langkah 5: Pemantauan dan Penyesuaian

- Pastikan layanan producer dapat diakses oleh layanan WS-REST.
- Periksa ketersediaan layanan WS-REST untuk memastikan layanan tersebut berfungsi sebagai gateway untuk mengakses microservices dengan baik.

Dengan langkah-langkah ini, Layanan WS-REST Anda seharusnya berhasil didaftarkan dan berjalan di lingkungan Anda. Pastikan untuk memantau kinerja dan melakukan penyesuaian sesuai kebutuhan.
