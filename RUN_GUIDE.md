# RUN_GUIDE.md — Cara Menjalankan YT-Short-Clipper (Mode Gratis, Tanpa API Berbayar)

Panduan ini dibuat agar AI agent atau siapa pun bisa menjalankan project ini langsung
dengan mengikuti langkah di bawah. Semua fitur berjalan **100% gratis tanpa API key**.

---

## 1. Prasyarat Sistem
- Python 3.10 atau lebih baru (`python --version`)
- Koneksi internet (untuk download dependency & video YouTube)
- File `cookies.txt` YouTube — WAJIB agar yt-dlp bisa mengakses video.
  Taruh di root project atau di `config/cookies.txt`.
  (Cara dapat cookies: lihat COOKIES.md / GUIDE.md di repo.)

## 2. Setup & Jalankan (Windows PowerShell)
```powershell
cd D:\Fikri\IT\yt-short-clipper

# Buat virtual environment (opsional tapi disarankan)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependensi Python
pip install -r requirements.txt

# Jalankan aplikasi (GUI CustomTkinter)
python app.py
```

Jika muncul error `Activation` karena execution policy:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## 3. Dependensi Eksternal (FFmpeg / yt-dlp / Deno)
App akan otomatis mendownload via `utils/dependency_manager.py` saat pertama kali
dijalankan. Jika gagal, pasang manual dan pastikan ada di PATH:
- FFmpeg
- yt-dlp (`pip install -r requirements.txt` sudah menyertakannya)
- Deno (untuk JS runtime yt-dlp)

## 4. Mode Gratis — Tanpa API Key Sama Sekali
JANGAN isi satupun API key di Settings. Dua alur gratis:

### A. Manual Mode (paling mudah)
1. Di home page, klik link **"✋ Manual Mode (no AI)"**.
2. Paste URL YouTube.
3. Klik **+ Add Clip**, isi:
   - Start: `HH:MM:SS`
   - End:   `HH:MM:SS`
   - Title: (bebas)
   - Hook:  (opsional, teks pembuka)
4. Aktifkan toggle "Add Captions" / "Add Hook Text" (gratis).
5. Klik **🎬 Process All Clips**.

### B. Find Highlights Otomatis (heuristik subtitle)
- Biarkan semua API key KOSONG.
- Tombol **Find Highlights** otomatis pakai deteksi lokal dari subtitle
  (tidak memanggil LLM).
- Hasil berupa daftar clip → pilih → Process.

## 5. Syarat Penting
- Video HARUS punya **subtitle bahasa `id`** (default `subtitle_language`).
  Ganti di Settings bila perlu (mis. `en`).
- Jika tidak ada subtitle:
  - Manual Mode → tetap jalan, caption dilewati.
  - Find Highlights otomatis → pesan "video tidak punya subtitle", gunakan Manual Mode.

## 6. Output
Clip hasil ada di `output/sessions/<timestamp>/clips/`.

## 7. Build Executable (opsional)
```powershell
pip install pyinstaller
pyinstaller build.spec
# Hasil: dist/YTShortClipper.exe
```

## 8. Troubleshooting Cepat
- **Gagal download video**: cek `cookies.txt` masih valid (cookies kadaluarsa).
- **Caption kosong/lewati**: video tidak punya subtitle bahasa dipilih.
- **GUI tidak muncul**: pastikan `customtkinter` terinstall di venv yang aktif.
- **ModuleNotFoundError cv2**: `pip install opencv-python` (sudah di requirements).
