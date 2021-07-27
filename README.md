# Multiple Scraper with Airflow

## About
Implementasi Airflow untuk penjadwalan multiple scraper dengan docker container. Aplikasi ini dibuat untuk mengotomasi jalannya scraper yang menghasilkan berbagai jenis output ke *Data Lake* (`Extract`) , Ingest data dari *Data Lake* ke MariaDB sebagai *Data Warehouse* (`Load`), dan transformasi data untuk kebutuhan publikasi dan visualisasi (`Transform`).

Komponen yang digunakan:
- Ubuntu Container sebagai container utama : 
    -   **Apache Airflow**
    -   **Python**
    -   **Chrome Browser**
    -   **PHP**
- MariaDB Database Container
- Phpmyadmin Container
<br>

---

## Setup
1. Rename `.env.example` menjadi `.env` dan pastikan semua variabel nya sudah terisi dengan benar.
2. Tambahkan *python libraries* yang dibutuhkan di file `libraries_`
3. Run semua container dengan docker daemon melalui perintah 
    ```sh
    docker-compose up -d
    ```
    Jika run pertama kali kemungkinan akan memakan waktu beberapa menit karena harus download *docker image* terlebih dahulu.

4. masuk ke container Ubuntu melalui <br>
    ```sh
    docker exec -it ubuntu_server_1 bash
    ```

5. selanjutnya aktivasi airflow melalui script <br>
    ```sh
    sh /home/settings/activate.sh`
    ```

---

## Dashboard
Setelah proses setup selesai, maka dashboard dapat diakses melalui

| Service  | Port |
| :---: | :---: |
| Web  | 8000 |
| Airflow Dashboard | 8080 |
| Phpmyadmin | 8082 |