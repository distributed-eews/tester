# Dokumentasi Deployment untuk Layanan Seeder

Layanan Seeder bertujuan untuk mengisi data stasiun gempa pada Redis. Layanan ini hanya akan dijalankan sekali saja untuk melakukan populasi awal data. Layanan ini membutuhkan alamat host dan port Redis untuk berfungsi.

## Persyaratan

- Docker
- Git

## Langkah 1: Clone Repositori

Clone repositori layanan Seeder ke mesin lokal Anda menggunakan perintah berikut:

```bash
git clone https://github.com/distributed-eews/seeder.git
cd seeder
```

## Langkah 2: Atur Variabel Lingkungan

Ubah nama file `.env.example` menjadi `.env` dan atur variabel lingkungan berikut sesuai konfigurasi Anda:

```plaintext
REDIS_HOST=<Alamat Redis>
REDIS_PORT=<Port Redis>
```

## Langkah 3: Mulai Kontainer Docker

Gunakan docker-compose untuk memulai layanan Seeder:

```bash
cd seeder
docker-compose up -d
```

## Langkah 4: Verifikasi Deployment

Pastikan kontainer Seeder berjalan tanpa masalah:

```bash
docker-compose ps
```

## Langkah 5: Pemantauan dan Penyesuaian

- Pastikan layanan Seeder hanya dijalankan sekali untuk melakukan populasi awal data.
- Periksa ketersediaan data pada Redis untuk memastikan populasi telah berhasil.

Dengan langkah-langkah ini, Layanan Seeder Anda seharusnya berhasil melakukan populasi data stasiun gempa pada Redis. Pastikan untuk memantau kinerja dan melakukan penyesuaian sesuai kebutuhan.
