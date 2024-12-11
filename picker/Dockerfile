FROM python:3.11

# Menyalin kode Anda ke dalam container
WORKDIR /app
COPY . /app

# Menginstal dependensi
RUN pip install -r requirements.txt

# Menjalankan skrip saat container dijalankan
CMD ["python", "main.py"]
