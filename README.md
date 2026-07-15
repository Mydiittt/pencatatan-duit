# MoneyWise — Personal Finance Manager

Aplikasi desktop untuk mengatur keuangan pribadi, dibangun 100% dengan
**Python + Tkinter** (tidak ada dependensi eksternal) menggunakan arsitektur
**MVC (Model - View - Controller)**.

## Fitur Utama

1. **Dashboard** — ringkasan saldo, pemasukan/pengeluaran bulan ini, grafik tren 6 bulan, transaksi terbaru.
2. **Pemasukan** — catat, edit, dan hapus pemasukan dengan kategori kustom.
3. **Pengeluaran** — catat, edit, dan hapus pengeluaran dengan kategori kustom.
4. **Penganggaran (Budgeting)** — atur batas anggaran per kategori per bulan, lengkap dengan progress bar dan status (Aman / Mendekati batas / Melebihi anggaran).
5. **Analisis & Laporan** — pie chart komposisi kategori, ringkasan bulanan (income/expense/net), dan rincian per kategori — semuanya digambar manual menggunakan `tkinter.Canvas` (tanpa matplotlib).

## Cara Menjalankan

Syarat: **Python 3.8+** (tkinter biasanya sudah termasuk secara default di instalasi Python standar).

```bash
cd money_manager
python main.py
```

Jika di Linux dan tkinter belum tersedia:

```bash
sudo apt-get install python3-tk
```

Database SQLite (`money_manager.db`) akan dibuat otomatis di folder yang sama saat pertama kali dijalankan, lengkap dengan kategori bawaan.

## Struktur Proyek (MVC)

```
money_manager/
├── main.py                        # Entry point
├── config.py                      # Warna, font, konstanta global
├── database/
│   └── db.py                      # Koneksi SQLite & skema tabel
├── models/                        # MODEL — akses & logika data
│   ├── transaction_model.py       # Pemasukan & pengeluaran
│   ├── budget_model.py            # Anggaran
│   └── category_model.py          # Kategori
├── controllers/                   # CONTROLLER — jembatan View <-> Model
│   ├── transaction_controller.py
│   ├── budget_controller.py
│   └── report_controller.py
├── views/                         # VIEW — tampilan tkinter
│   ├── main_view.py                # Jendela utama + sidebar navigasi
│   ├── dashboard_view.py
│   ├── income_expense_view.py
│   ├── budget_view.py
│   ├── report_view.py
│   └── components.py               # Widget custom (Card, Button, dll.)
└── money_manager.db                # Database (dibuat otomatis)
```

## Alur MVC

- **Model** (`models/`) hanya berurusan dengan data: query SQL, validasi struktur data, dan kalkulasi agregat (total, breakdown, dsb). Model tidak tahu apa-apa tentang tampilan.
- **Controller** (`controllers/`) menerima input dari View, memvalidasi (misal jumlah harus angka positif), lalu memanggil Model. Controller mengembalikan hasil (sukses/gagal + pesan error) ke View.
- **View** (`views/`) murni tkinter: menampilkan form, tabel, grafik, dan meneruskan aksi pengguna (klik tombol, submit form) ke Controller. View tidak pernah mengakses database secara langsung.

## Catatan Desain

- Tema warna modern (sidebar gelap + konten terang) dengan aksen biru `#4C6FFF`.
- Semua ikon menggunakan emoji Unicode bawaan (tidak perlu file gambar eksternal).
- Grafik batang, pie chart, dan progress bar digambar manual dengan `tkinter.Canvas` — tidak ada dependensi seperti matplotlib.
- Kategori pemasukan/pengeluaran bisa ditambah bebas oleh pengguna langsung dari form.

Selamat mengatur keuangan! 💰
