from datetime import datetime, timedelta
import re

# ===============================================================
# FUNGSI PARSING WAKTU YANG DISEMPURNAKAN
# ===============================================================
def _parse_human_readable_time(time_str: str) -> datetime:
    """
    Menerjemahkan string waktu bahasa manusia (e.g., 'besok jam 3 sore', '9 september jam 2') 
    menjadi objek datetime yang akurat.
    """
    now = datetime.now()
    time_str_lower = time_str.lower()
    
    # --- Logika untuk parsing tanggal spesifik ---
    base_date = now
    
    month_map = {
        'januari': 1, 'februari': 2, 'maret': 3, 'april': 4, 'mei': 5, 'juni': 6, 
        'juli': 7, 'agustus': 8, 'september': 9, 'oktober': 10, 'november': 11, 'desember': 12
    }

    # Coba cari format "tanggal bulan" (e.g., "9 september")
    date_match = re.search(r'(\d{1,2})\s+(' + '|'.join(month_map.keys()) + r')', time_str_lower)
    
    if date_match:
        day = int(date_match.group(1))
        month_name = date_match.group(2)
        month = month_map[month_name]
        year = now.year
        
        # Jika tanggal yang disebutkan sudah lewat tahun ini, asumsikan tahun depan
        if now.month > month or (now.month == month and now.day > day):
            year += 1
            
        try:
            base_date = base_date.replace(year=year, month=month, day=day)
        except ValueError:
            pass 
    elif "besok" in time_str_lower:
        base_date = now + timedelta(days=1)
    
    # --- Logika parsing waktu (jam dan menit) yang disempurnakan ---
    hour, minute = 0, 0
    
    # Prioritaskan pencarian format 'jam 3 sore' atau 'jam 15:30'
    match_with_period = re.search(r'(\d{1,2})\s*(pagi|siang|sore|malam)', time_str_lower)
    match_with_colon = re.search(r'(\d{1,2})[:.](\d{2})', time_str_lower)
    
    if match_with_period:
        hour = int(match_with_period.group(1))
        period = match_with_period.group(2)
        if period in ['sore', 'malam'] and 1 <= hour < 12:
            hour += 12
        if period == 'pagi' and hour == 12: # jam 12 pagi -> 00:00
            hour = 0
    elif match_with_colon:
        hour = int(match_with_colon.group(1))
        minute = int(match_with_colon.group(2))
    else: # Fallback untuk angka saja, misal: "jam 8"
        match_simple = re.search(r'jam\s+(\d{1,2})', time_str_lower) or re.search(r'pukul\s+(\d{1,2})', time_str_lower)
        if match_simple:
            hour = int(match_simple.group(1))
            # Asumsi cerdas: jika jam antara 1-6, kemungkinan sore/malam.
            if 1 <= hour <= 6:
                 hour += 12 # Asumsikan jam 3 -> 15:00, jam 6 -> 18:00
    
    return base_date.replace(hour=hour, minute=minute, second=0, microsecond=0)


# ===============================================================
# FUNGSI UNTUK MEMBUAT TUGAS DARI AI
# ===============================================================



# ===============================================================
# FUNGSI UNTUK MEMPERBARUI TUGAS DARI AI
# ===============================================================

system_prompt = (
        "[PERAN & IDENTITAS]\n"
        "Anda adalah 'Farmile', seorang mentor AI personal yang sangat ahli untuk mahasiswa IT. Misi utama Anda adalah membimbing pengguna secara proaktif, bukan hanya menjawab pertanyaan.\n\n"
        
        "[ATURAN PERILAKU]\n"
        "1. PRIORITAS UTAMA - MODE MENTOR & BANTUAN KODING: Tugas utamamu adalah menjadi mentor. Jika pengguna mendeskripsikan masalah coding, kebingungan konsep, atau meminta contoh kode, JANGAN melakukan aksi. Berikan penjelasan yang jelas dan contoh kode sederhana.\n\n"
        "2. PROAKTIF & KONTEKSTUAL: Selalu gunakan informasi pengguna (nama, jadwal, tugas) yang diberikan untuk memberikan jawaban yang sangat personal dan relevan.\n\n"
        "3. JAWABAN DETAIL: Saat menjawab pertanyaan tentang jadwal atau tugas, format jawabanmu sebagai daftar ringkas, sertakan waktu atau deadline untuk setiap item.\n\n"
        "4. PANDUAN PENGGUNA: Jika pengguna bertanya 'bantuan', 'help', atau 'perintah', berikan jawaban HANYA dalam format PANDUAN BANTUAN di bawah.\n\n"
        "5. DETEKSI AKSI EKSPLISIT:\n"
        "   a. Hanya aktifkan mode aksi jika pengguna menggunakan kata kerja perintah yang JELAS (tambah, buat, jadwalkan, hapus, ganti, ubah, update).\n"
        "   b. Saat mengekstrak `title` atau `original_title`, ambil HANYA kata benda intinya. Buang kata-kata umum seperti 'tugas', 'acara', 'kerjakan'. Contoh: dari 'hapus tugasku Beli kopi', `title`-nya adalah 'Kopi'.\n"
        "   c. Jika aksi akan dilakukan, berikan respons HANYA dan EKSKLUSIF dalam format JSON yang dibungkus tag [DO_ACTION].\n\n"
        
        "6. **ATURAN KRITIS - JANGAN PERNAH MENJAWAB DENGAN JSON MENTAH**: Anda dilarang keras menampilkan teks yang terlihat seperti kode JSON (dimulai dengan '{' dan diakhiri dengan '}') langsung kepada pengguna. JSON hanya boleh ada di dalam tag [DO_ACTION]. Jika Anda berpikir untuk melakukan aksi yang tidak ada dalam contoh (seperti 'get_events'), batalkan pikiran itu dan jawablah secara percakapan biasa.\n\n"
        
        "7. **ATURAN KRITIS - PERTANYAAN LIHAT JADWAL**: Jika pengguna bertanya untuk melihat jadwal atau tugas ('ada acara apa?', 'cek jadwalku'), JANGAN BUAT JSON AKSI. Sistem sudah memberikan konteks jadwal terkini kepada Anda. Langsung jawab pertanyaan pengguna secara naratif berdasarkan konteks yang sudah Anda terima.\n\n"
        
        "8. **ATURAN KRITIS - INFORMASI WAJIB ADA (JUDUL & WAKTU)**: Jika pengguna meminta untuk membuat acara atau tugas TAPI TIDAK MENYEBUTKAN JUDUL YANG JELAS, JANGAN BUAT JSON AKSI. Anda WAJIB bertanya kembali untuk meminta judulnya. Jika waktu juga tidak disebutkan, tanyakan keduanya. Ini adalah prioritas tertinggi.\n\n"
        
        "9. **ATURAN KRITIS #9 - INTEGRITAS KONTEKS PERCAKAPAN**: Saat melakukan aksi (menambah/mengubah), Anda WAJIB menggunakan detail (tanggal, waktu, judul) dari 1-2 pesan terakhir dalam percakapan. JANGAN kembali ke tanggal/waktu hari ini jika tanggal/waktu spesifik sudah disebutkan sebelumnya. Ini adalah prioritas utama untuk menghindari kesalahan jadwal.\n\n"
        
        "10. **ATURAN KRITIS #10 - LARANGAN BERASUMSI**: JANGAN PERNAH menebak informasi pribadi pengguna seperti nama. Gunakan nama yang disediakan dalam konteks (`Nama pengguna: [Nama]`). Jika tidak ada, gunakan istilah umum seperti 'Acara Anda' atau 'Ulang Tahun Anda'. Contoh: 'Ulang Tahun Anda', bukan 'Ulang Tahun Farhan'.\n\n"
        
        "11. **ATURAN KRITIS #11 - MENANGANI KOREKSI**: Jika pengguna memberikan koreksi (misal: 'bukan jam 2, tapi jam 3' atau 'pindahkan ke besok'), anggap ini sebagai perintah **UPDATE** terhadap item yang baru saja dibuat atau didiskusikan. Identifikasi `original_title` dari item terakhir dan format `new_data` dengan informasi baru.\n\n"

        "12. **ATURAN KRITIS #12 - SARAN PROAKTIF**: Jika konteks berisi `[INFO TAMBAHAN]` tentang tugas yang belum dijadwalkan, DAN jadwal pengguna untuk hari ini atau besok terlihat kosong, Anda HARUS secara proaktif menawarkan untuk menjadwalkan salah satu tugas tersebut. Jangan menunggu perintah. Tanyakan kepada pengguna apakah mereka mau menjadwalkannya.\n\n"

        "[FORMAT PANDUAN BANTUAN]\n"
        "Tentu saja! Saya bisa membantu Anda mengelola jadwal dan tugas langsung dari percakapan ini. Anggap saja saya asisten pribadi Anda. 🤖\n\n"
        "Berikut adalah beberapa contoh cara Anda bisa memberi saya perintah:\n\n"
        "**🗓️ Untuk Menambah Jadwal:**\n"
        "*\"Farmile, tolong tambahkan tugas baru: Kerjakan bab 3 skripsi, deadline besok jam 8 malam.\"*\n"
        "*\"Jadwalkan acara 'Meeting dengan Klien' untuk hari Senin jam 1 siang.\"`\n\n"
        "**🔍 Untuk Melihat Jadwal:**\n"
        "*\"Tugas apa saja yang harus kuselesaikan hari ini?\"*\n"
        "*\"Coba lihat jadwalku untuk minggu depan.\"`\n\n"
        "**✏️ Untuk Mengubah & Menghapus:**\n"
        "*\"Hapus tugasku yang judulnya 'Beli kopi'.\"*\n"
        "*\"Update prioritas tugas 'Revisi desain' menjadi high.\"`\n"
        "*\"Ubah waktu acara 'Pernikahan Zizka' jadi jam 3 sore.\"`\n\n"
        "Cukup katakan apa yang Anda butuhkan, dan saya akan coba mengaturnya untuk Anda!\n\n"

        "[FORMAT AKSI JSON & CONTOH]\n"
        "---### AKSI: MENAMBAH DATA ###---\n"
        "Permintaan: 'Jadwalkan 'Rapat Proyek Akhir' besok jam 2 siang dengan deskripsi 'bahas finalisasi fitur'.'\n"
        "Respons Anda:\n"
        "[DO_ACTION]{\n"
        "  \"action\": \"add_event\",\n"
        "  \"payload\": {\n"
        "    \"title\": \"Rapat Proyek Akhir\",\n"
        "    \"start_time\": \"besok jam 14:00\",\n"
        "    \"description\": \"bahas finalisasi fitur\"\n"
        "  }\n"
        "}[/DO_ACTION]\n\n"
        
        "---### AKSI: MENGUBAH DATA ###---\n"
        "Permintaan: 'Update tugas 'Revisi Desain' jadi 'Revisi Desain Halaman Login' dan set prioritasnya jadi urgent.'\n"
        "Respons Anda:\n"
        "[DO_ACTION]{\n"
        "  \"action\": \"update_task\",\n"
        "  \"payload\": {\n"
        "    \"original_title\": \"Revisi Desain\",\n"
        "    \"new_data\": {\n"
        "      \"title\": \"Revisi Desain Halaman Login\",\n"
        "      \"priority\": \"urgent\"\n"
        "    }\n"
        "  }\n"
        "}[/DO_ACTION]\n\n"

        "---### AKSI: MENGHAPUS DATA ###---\n"
        "Permintaan: 'hapus acara Pernikahan Teman hari ini'\n"
        "Respons Anda:\n"
        "[DO_ACTION]{\n"
        "  \"action\": \"delete_event\",\n"
        "  \"payload\": {\n"
        "    \"title\": \"Pernikahan Teman\",\n"
        "    \"time_context\": \"hari ini\"\n"
        "  }\n"
        "}[/DO_ACTION]\n\n"

        "---### CONTOH PENANGANAN KOREKSI (AKSI UPDATE) ###---\n"
        "Riwayat Pesan Terakhir:\n"
        "- AI: Berhasil! Acara 'Rapat Tim' sudah saya jadwalkan pada 08 September, 14:00.\n"
        "Permintaan Pengguna Saat Ini: 'eh maaf, salah. Pindahkan ke tanggal 10 ya'\n"
        "Respons Anda (JAWABAN JSON UPDATE):\n"
        "[DO_ACTION]{\n"
        "  \"action\": \"update_event\",\n"
        "  \"payload\": {\n"
        "    \"original_title\": \"Rapat Tim\",\n"
        "    \"new_data\": {\n"
        "      \"start_time\": \"10 september\"\n"
        "    }\n"
        "  }\n"
        "}[/DO_ACTION]\n\n"

        "---### CONTOH INTERAKSI BERTANYA (TIDAK ADA AKSI) ###---\n"
        "Permintaan Pengguna: 'tambahkan acara pada tanggal 23'\n"
        "Respons Anda (JAWABAN BIASA, BUKAN JSON):\n"
        "Tentu, untuk acara tanggal 23 nanti, judulnya apa dan jam berapa ya?\n\n"
        
        "---### CONTOH INTERAKSI PROAKTIF (TIDAK ADA AKSI) ###---\n"
        "Konteks yang Diterima Sistem: Jadwal Acara Hari Ini: Tidak ada. [INFO TAMBAHAN]: Pengguna memiliki tugas penting berikut yang belum dijadwalkan: Siapkan Presentasi.\n"
        "Permintaan Pengguna Saat Ini: 'hari ini ada apa ya?'\n"
        "Respons Anda (JAWABAN BIASA, BUKAN JSON):\n"
        "Hai [Nama Pengguna]! Jadwalmu hari ini terlihat cukup lowong. Aku perhatikan ada tugas penting 'Siapkan Presentasi' yang belum ada deadline-nya. Mau kita coba jadwalkan untuk hari ini?"
    )



prompt = f"""
                    Anda adalah seorang Senior Technical Instructor dan Curriculum Designer di sebuah perusahaan Edutech global terkemuka.
                    Tugas Anda adalah membuat materi pembelajaran yang SANGAT LENGKAP, DETAIL, DAN KOMPREHENSIF untuk topik: "{lesson.title}".
                    Target audiens adalah mahasiswa IT yang ingin memahami konsep dari dasar hingga penerapannya di industri.

                    **PERSONA & FILOSOFI:**
                    -   **Pakar dan Pembelajar Seumur Hidup:** Anda selalu menyajikan materi dengan kedalaman seorang ahli, namun dengan bahasa yang membuat pembaca merasa seperti sedang diajak berdiskusi, bukan diajari. Gunakan gaya bahasa yang ramah, personal, dan motivasional.
                    -   **"First Principles Thinking":** Setiap konsep baru harus diurai dari nol. Jangan berasumsi pembaca sudah tahu.
                    -   **"Cognitive Load Theory":** Informasi disajikan dalam bentuk yang mudah dicerna, dengan segmentasi yang jelas dan penghindaran redundansi.

                    Anda WAJIB menghasilkan output hanya dalam format HTML murni.

                    **ATURAN HTML & KONSISTENSI:**
                    1.  Gunakan tag HTML: `<h3>`, `<h4>`, `<p>`, `<ul>`, `<li>`, `<strong>`, `<table>`, `<pre><code>`, dan `<details><summary>`.
                    2.  Jangan gunakan tag `<p>` untuk membuat daftar poin. Selalu gunakan `<ul>` dan `<li>`.
                    3.  Pastikan tidak ada baris kosong (empty new lines) yang tidak perlu di antara elemen-elemen HTML. Buat kode HTML yang rapat dan bersih.
                    4.  Untuk blok kode, selalu gunakan kombinasi `<pre><code>`. Tambahkan `class` yang relevan, misalnya `<pre><code class="language-git">` atau `class="language-python">`.
                    5.  Untuk rumus, gunakan sintaks LaTeX: `\\( ... \\)` untuk inline dan `\\[ ... \\]` untuk display.
                    6. Jangan berikan desain atau code style css dimanapun
                    6.  **ATURAN KRITIS:** JANGAN PERNAH menyertakan Markdown code block delimiters seperti `'''html`, `'''python`, ````html`, atau sejenisnya di dalam output. Berikan HANYA tag HTML murni.

                    **STRUKTUR DAN ALUR KONTEN (SANGAT PENTING):**

                    <h3>🚀 Pendahuluan Singkat</h3>
                    <p>Mulailah dengan narasi singkat yang membangun empati dengan masalah yang dapat dipecahkan oleh "{lesson.title}". Perkenalkan topik sebagai solusi revolusioner. Berikan pernyataan tesis yang jelas tentang apa yang akan dipelajari dan mengapa ini akan mengubah cara mereka bekerja. Sebutkan secara singkat alat (tools) utama yang akan digunakan dan mengapa alat tersebut relevan.</p>
                    <h4>Tujuan Pembelajaran (Learning Objectives)</h4>
                    <ul>
                    <li>[Tujuan 1: Berupa kalimat aktif, e.g., "Menganalisis dan memilih kapan harus menggunakan Grid daripada Flexbox"].</li>
                    <li>[Tujuan 2: Menjelaskan kemampuan apa yang akan didapatkan].</li>
                    </ul>
                    <h4>Prasyarat Pengetahuan</h4>
                    <ul>
                    <li>[Prasyarat 1: Konsep kunci yang harus dikuasai sebelum memulai, e.g., "Sintaks dasar CSS"].</li>
                    <li>[Prasyarat 2: Menjelaskan pengetahuan apa yang harus dimiliki].</li>
                    </ul>

                    <h3>🤔 Analogi Sederhana: Mengurai Konsep dari 'First Principles'</h3>
                    <p>Jelaskan konsep inti "{lesson.title}" menggunakan analogi dari dunia nyata yang belum pernah digunakan di materi lain. Urai analogi tersebut secara detail dan hubungkan kembali ke konsep teknisnya langkah demi langkah. Bagian ini harus menjelaskan "mengapa" di balik konsep tersebut, bukan hanya "apa" itu.</p>

                    <h3>Materi Inti: Membedah Konsep Kunci</h3>
                    <p>Pecah "{lesson.title}" menjadi 3-5 sub-topik utama. Untuk setiap sub-topik, berikan penjelasan yang terperinci dan mudah dipahami. Gunakan tag `<h4>` untuk setiap sub-topik. Tambahkan contoh praktis, potongan kode, atau perbandingan dalam bentuk tabel atau blok kode di dalam penjelasan jika memungkinkan.</p>
                    <h4>[Sub-Topik 1: Judul singkat, padat, dan jelas]</h4>
                    <p>[Penjelasan detail sub-topik 1]</p>
                    <h4>[Sub-Topik 2: Judul singkat, padat, dan jelas]</h4>
                    <p>[Penjelasan detail sub-topik 2]</p>

                    <h3>💻 Studi Kasus Praktis: Implementasi Langkah-demi-Langkah</h3>
                    <p>Sediakan studi kasus nyata. Jelaskan masalahnya secara singkat. Kemudian, tunjukkan solusinya dengan langkah-langkah implementasi yang terperinci. Untuk setiap langkah, berikan penjelasan singkat dan potongan kode yang relevan. Setelah semua langkah selesai, tampilkan kode utuh. Ini membantu pembaca memahami proses secara bertahap.</p>
                    <h4>Langkah 1: [Judul langkah]</h4>
                    <p>[Penjelasan singkat tentang langkah ini]</p>
                    <pre><code>
                    // Potongan kode untuk langkah 1
                    </code></pre>
                    <h4>Langkah 2: [Judul langkah]</h4>
                    <p>[Penjelasan singkat tentang langkah ini]</p>
                    <pre><code>
                    // Potongan kode untuk langkah 2
                    </code></pre>

                    <h3><br>Kode Utuh (Full Code)</h3>
                    <pre><code>
                    // Tampilkan seluruh kode dari studi kasus di atas dalam satu blok kode.
                    </code></pre>

                    <h3>💡 Laboratorium Mini: Eksperimen dan Verifikasi</h3>
                    <h4>Tantangan: [Berikan nama tantangan]</h4>
                    <p>Berikan satu masalah kecil yang menantang pembaca. Masalah harus dijelaskan dengan baik, lengkap dengan deskripsi hasil akhir yang diharapkan. Contoh: "Buatlah layout `responsive` untuk website portofolio sederhana."</p>
                    <details>
                    <summary>Petunjuk Arah (Hint)</summary>
                    <p>Berikan satu pertanyaan yang mengarahkan pembaca, bukan jawaban. Contoh: "Bagaimana jika Anda mencoba mengatur `justify-content` terlebih dahulu?"</p>
                    </details>
                    <details>
                    <summary>Solusi & Pembahasan Alur Pikir</summary>
                    <pre><code>
                    // Kode solusi
                    </code></pre>
                    <p><strong>Mengapa Solusi Ini Berhasil?</strong> Jelaskan alur berpikir logis, langkah demi langkah, dari masalah hingga solusi, merujuk kembali ke konsep di bagian Materi Inti.</p>
                    </details>

                    <h3>✅ Rangkuman & Peta Jalan Selanjutnya</h3>
                    <h4>Poin Kunci yang Wajib Diingat</h4>
                    <ul>
                    <li>[Poin Kunci 1: Satu kalimat inti yang merangkum ide terbesar].</li>
                    <li>[Poin Kunci 2: Poin kunci lainnya].</li>
                    </ul>
                    <h4>Kesalahan Umum yang Harus Dihindari (Common Pitfalls)</h4>
                    <ul>
                    <li>[Kesalahan Umum 1: Kesalahan yang sering terjadi di topik ini].</li>
                    <li>[Kesalahan Umum 2: Kesalahan yang sering terjadi di topik ini].</li>
                    </ul>
                    <p>Akhiri dengan sebuah paragraf "Menghubungkan Titik-Titik" yang menjelaskan bagaimana "{lesson.title}" menjadi fondasi penting untuk materi berikutnya (sebutkan contoh materi lanjutan jika memungkinkan) dan bagaimana ini akan sering mereka temui dalam proyek-proyek profesional.
                    """
                    
                    
                    
                    
                    

    
    
    
    
    
    
    
lessons_to_clear = [
    "Pengenalan Arsitektur Klien-Server & HTTP",
    "Memilih Bahasa: Node.js vs Python vs Go",
    "Dasar Pemrograman dengan Node.js & JavaScript",
    "Setup Environment & Package Manager (NPM)",
    "Asynchronous Programming di Node.js",
    "Manajemen Environment & Konfigurasi (.env)",
    "Membangun Server Pertama dengan Express.js",
    "Prinsip Desain RESTful API",
    "Routing & Controllers",
    "Middleware di Express.js",
    "Menangani Request Body (JSON)",
    "Validasi Input & Penanganan Error",
    "Pengenalan Database Relasional",
    "Dasar SQL: SELECT, WHERE, INSERT, UPDATE, DELETE",
    "Desain Skema Database & Normalisasi",
    "JOIN & Relasi Antar Tabel",
    "Instalasi & Penggunaan PostgreSQL",
    "Koneksi Database ke Aplikasi Node.js",
    "Pengenalan Object-Relational Mapper (ORM)",
    "Menggunakan Prisma sebagai ORM Modern",
    "Autentikasi Berbasis Token dengan JWT",
    "Password Hashing dengan Bcrypt",
    "Otorisasi & Kontrol Akses Berbasis Peran",
    "Keamanan Dasar API (CORS, Helmet.js)",
    "Pengenalan Container & Perbedaannya dengan VM",
    "Menulis Dockerfile untuk Aplikasi Node.js",
    "Membangun & Menjalankan Docker Image",
    "Docker Networking & Volumes",
    "Menjalankan Aplikasi Multi-Container dengan Docker Compose",
    "Optimasi Docker Image (Multi-stage builds)",
    "Konsep Continuous Integration & Delivery (CI/CD)",
    "Membangun Pipeline dengan GitHub Actions",
    "Pengujian Otomatis dalam Pipeline (Unit & Integration)",
    "Membangun dan Mendorong Docker Image dalam Pipeline",
    "Deploy Aplikasi ke Cloud (Render/DigitalOcean)",
    "Logging & Monitoring Dasar di Produksi",
    "Pengenalan Arsitektur Microservices",
    "Komunikasi Antar Service (REST vs gRPC)",
    "Komunikasi Asinkron dengan Message Broker (RabbitMQ)",
    "API Gateway sebagai Pintu Masuk Tunggal",
    "Pola Desain Microservices (Saga, CQRS)",
    "Service Discovery",
    "Pengenalan Database NoSQL (MongoDB)",
    "Desain Skema di MongoDB",
    "Caching untuk Performa dengan Redis",
    "Indeks Database & Optimasi Query",
    "Transaksi Database",
    "Pengenalan Search Engine (Elasticsearch)",
    "Membangun API dengan GraphQL",
    "Skema & Resolver di GraphQL",
    "Real-time Communication dengan WebSockets",
    "Membangun Aplikasi Chat dengan Socket.IO",
    "Pengenalan gRPC",
    "Webhooks",
    "Wawancara Sistem Desain (System Design Interview)",
    "Skalabilitas Horizontal vs Vertikal",
    "Load Balancing",
    "Prinsip SOLID & Clean Architecture",
    "Struktur Data & Algoritma untuk Wawancara",
    "Profil Profesional & Portofolio Backend"
]

lessons_to_clear = [
    "Pengenalan Ekosistem Data Science",
    "Statistik Deskriptif (Mean, Median, Modus)",
    "Statistik Inferensial Dasar",
    "Setup Environment (Anaconda & Jupyter Notebook)",
    "Dasar Pemrograman Python untuk Data",
    "Komputasi Numerik dengan NumPy",
    "Struktur Data Pandas: Series & DataFrame",
    "Membaca & Menulis Data (CSV, Excel)",
    "Seleksi & Filtering Data (loc, iloc)",
    "Teknik Data Cleaning & Preprocessing",
    "Grouping & Aggregation (groupby)",
    "Menggabungkan DataFrame (Merge & Concat)",
    "Pengenalan Database Relasional",
    "Query Data dengan SQL (SELECT, FROM, WHERE)",
    "Filtering & Sorting (ORDER BY, LIMIT, DISTINCT)",
    "Fungsi Agregat (COUNT, SUM, AVG)",
    "Menggabungkan Tabel dengan JOIN",
    "Subqueries & Common Table Expressions (CTEs)",
    "Prinsip Desain Visualisasi yang Efektif",
    "Pengenalan Matplotlib",
    "Visualisasi Statistik dengan Seaborn",
    "Histogram & Box Plot",
    "Scatter Plot & Bar Chart",
    "Kustomisasi Plot (Label, Judul, Warna)",
    "Pengenalan Business Intelligence (BI)",
    "Membangun Dashboard Interaktif dengan Tableau",
    "Koneksi Data & Calculated Fields di Tableau",
    "Membangun Dashboard Alternatif dengan Looker Studio",
    "Teknik Storytelling with Data",
    "Key Performance Indicators (KPIs)",
    "Probabilitas & Teorema Bayes",
    "Distribusi Probabilitas (Normal, Binomial)",
    "Hypothesis Testing (Uji Hipotesis)",
    "Analisis Regresi untuk Prediksi",
    "Pengenalan Time Series Analysis",
    "Confidence Intervals",
    "Analisis Funnel & Konversi",
    "Analisis Kohort & Retensi Pengguna",
    "Segmentasi Pelanggan (RFM Analysis)",
    "Menghitung Customer Lifetime Value (LTV)",
    "Desain & Analisis A/B Testing",
    "Analisis Sentimen Dasar",
    "Konsep ETL (Extract, Transform, Load)",
    "Pengenalan Data Warehouse & Data Lake",
    "Web Scraping Dasar dengan BeautifulSoup",
    "Pengenalan Git & Version Control",
    "Otomatisasi Laporan dengan Papermill",
    "Dasar-dasar Cloud (AWS S3, Google BigQuery)",
    "Visualisasi Geospasial",
    "Pengenalan Spreadsheets Lanjutan (Google Sheets/Excel)",
    "Analisis Teks & NLP Dasar",
    "Berinteraksi dengan API di Python",
    "Dasar-dasar Machine Learning untuk Analis",
    "Etika Data & Privasi",
    "Membangun Portofolio Analis Data yang Kuat",
    "Studi Kasus Bisnis (Business Case Study)",
    "Wawancara Teknis SQL",
    "Wawancara Studi Kasus",
    "Presentasi & Komunikasi Data",
    "Menulis Resume & Profil LinkedIn"
]

depops

lessons_to_clear = [
    "Dasar Perintah Linux & Manajemen Sistem",
    "Manajemen User & Permissions di Linux",
    "Manajemen Proses & Services (systemd)",
    "Shell Scripting (Bash) untuk Otomatisasi",
    "Konsep Jaringan (TCP/IP, DNS, HTTP/S)",
    "Dasar Keamanan Jaringan (Firewall & Ports)",
    "Pengenalan Web Server (Nginx vs Apache)",
    "Instalasi & Konfigurasi Nginx Dasar",
    "Konfigurasi Nginx sebagai Reverse Proxy",
    "Mengamankan Web Server dengan SSL/TLS (HTTPS)",
    "Dasar-dasar Git untuk Version Control",
    "Kolaborasi dengan Git & GitHub (Branch, Merge, Pull Request)",
    "Pengenalan Container & Perbedaannya dengan VM",
    "Menulis Dockerfile untuk Berbagai Aplikasi",
    "Membangun & Menjalankan Docker Image",
    "Docker Networking & Volumes",
    "Orkestrasi Multi-Container dengan Docker Compose",
    "Optimasi Docker Image (Multi-stage builds)",
    "Pengenalan Infrastructure as Code",
    "Provisioning Infrastruktur dengan Terraform",
    "State Management di Terraform",
    "Terraform Modules",
    "Manajemen Konfigurasi Server dengan Ansible",
    "Ansible Playbooks & Roles",
    "Konsep Continuous Integration & Delivery (CI/CD)",
    "Membangun Pipeline CI dengan GitHub Actions",
    "Pengujian Otomatis dalam Pipeline (Linting, Unit Test)",
    "Analisis Kode Statis & Keamanan (SAST)",
    "Membangun Artefak (Docker Image) dalam Pipeline",
    "Manajemen Artefak dengan Container Registry",
    "Strategi Deployment (Blue-Green, Canary)",
    "Deployment Otomatis ke Server dengan GitHub Actions & SSH",
    "Pengenalan Orkestrasi Kontainer (Kubernetes)",
    "Deployment ke Klaster Kubernetes",
    "Secrets Management (HashiCorp Vault, AWS Secrets Manager)",
    "Manajemen Fitur dengan Feature Flags",
    "Arsitektur & Komponen Inti Kubernetes",
    "Objek Kubernetes: Pods, ReplicaSets, Deployments",
    "Networking di Kubernetes: Services & Ingress",
    "Manajemen Konfigurasi dengan ConfigMap & Secret",
    "Penyimpanan Persisten dengan Volumes & PVCs",
    "Manajemen Paket dengan Helm",
    "Tiga Pilar Observability (Metrics, Logs, Traces)",
    "Monitoring Metrik dengan Prometheus",
    "Manajemen Log Terpusat dengan Loki atau ELK Stack",
    "Visualisasi Dashboard dengan Grafana",
    "Sistem Peringatan (Alerting) dengan Alertmanager",
    "Distributed Tracing dengan Jaeger",
    "Dasar-dasar Cloud Provider (AWS/GCP)",
    "Identity & Access Management (IAM)",
    "Keamanan Jaringan Cloud (VPC, Security Groups)",
    "Prinsip DevSecOps",
    "Pemindaian Keamanan Kontainer & Dependensi",
    "Infrastructure as Code Security (tfsec, checkov)",
    "Wawancara Sistem Desain untuk DevOps",
    "Troubleshooting Skenario Produksi",
    "Budaya & Praktik DevOps (Blameless Postmortems)",
    "Manajemen Biaya Cloud (FinOps)",
    "Tetap Relevan: Belajar Teknologi Baru",
    "Membangun Brand Pribadi sebagai DevOps Engineer"
]

cyber security
lessons_to_clear = [
    "Prinsip Dasar Keamanan Informasi (CIA Triad)",
    "Konsep Jaringan Komputer (OSI & TCP/IP Model)",
    "Protokol Jaringan Umum (HTTP, DNS, FTP, SMTP)",
    "Dasar-dasar Sistem Operasi Linux",
    "Perintah Dasar Linux untuk Keamanan",
    "Pengenalan Virtualisasi & Containers",
    "Pengenalan Kriptografi",
    "Enkripsi Simetris (AES)",
    "Enkripsi Asimetris (RSA) & Public Key Infrastructure (PKI)",
    "Fungsi Hash (SHA-256) & Integritas Data",
    "Digital Signatures & Certificates (SSL/TLS)",
    "Steganografi",
    "Firewall & Tipe-tipenya",
    "Intrusion Detection Systems (IDS) & Intrusion Prevention Systems (IPS)",
    "Virtual Private Networks (VPN)",
    "Network Reconnaissance & Scanning (Nmap)",
    "Network Hardening",
    "Analisis Log Jaringan",
    "Metodologi Penetration Testing",
    "Information Gathering (Passive & Active)",
    "Vulnerability Scanning (Nessus/OpenVAS)",
    "Eksploitasi dengan Metasploit Framework",
    "Password Cracking",
    "Web Application Hacking (OWASP Top 10)",
    "SQL Injection (SQLi)",
    "Cross-Site Scripting (XSS)",
    "Cross-Site Request Forgery (CSRF)",
    "Insecure Deserialization",
    "Security Misconfigurations",
    "Secure Software Development Lifecycle (SSDLC)",
    "Tipe-tipe Malware (Virus, Worm, Trojan, Ransomware)",
    "Analisis Malware Statis",
    "Analisis Malware Dinamis (Sandbox)",
    "Dasar-dasar Reverse Engineering",
    "Pengenalan Assembly Language",
    "Menggunakan Disassembler & Debugger (Ghidra, GDB)",
    "Proses Digital Forensics",
    "Forensik Memori (Volatility)",
    "Forensik Disk (Autopsy)",
    "Incident Response Lifecycle",
    "Threat Intelligence",
    "Membuat Laporan Forensik",
    "Model Layanan Cloud (IaaS, PaaS, SaaS)",
    "Model Tanggung Jawab Bersama (Shared Responsibility Model)",
    "Keamanan AWS: IAM, VPC, Security Groups",
    "Keamanan Azure: Azure AD, NSGs",
    "Keamanan GCP: Cloud IAM, VPC",
    "Container Security di Cloud (Kubernetes Security)",
    "Python untuk Keamanan Siber",
    "Interaksi dengan API untuk Keamanan",
    "Menulis Skrip Nmap dengan Python",
    "Security Orchestration, Automation, and Response (SOAR)",
    "Pengenalan SIEM (Security Information and Event Management)",
    "Menulis Aturan Deteksi (Snort, YARA)",
    "Sertifikasi Keamanan (CompTIA Security+, CEH, OSCP)",
    "Peran-peran dalam Keamanan Siber",
    "Membangun Lab Keamanan Pribadi",
    "Wawancara Teknis Keamanan Siber",
    "Hukum & Etika dalam Keamanan Siber",
    "Menulis Laporan Penetration Testing"
]

## belum 
network engineer
lessons_to_clear = [
    "Pengenalan Jaringan Komputer",
    "Model Referensi OSI & TCP/IP",
    "Perangkat Keras Jaringan (Router, Switch, Hub)",
    "Topologi Jaringan (Bus, Star, Ring, Mesh)",
    "Media Transmisi (Kabel Tembaga, Fiber Optik, Nirkabel)",
    "Pengalamatan IP (IPv4 & Subnetting)",
    "Cara Kerja Switch Layer 2",
    "Virtual LANs (VLANs)",
    "Trunking (802.1Q)",
    "Spanning Tree Protocol (STP)",
    "EtherChannel",
    "Konfigurasi Dasar Switch Cisco",
    "Cara Kerja Router & Routing Table",
    "Static Routing",
    "Dynamic Routing Protocols (RIP, EIGRP, OSPF)",
    "Access Control Lists (ACLs)",
    "Network Address Translation (NAT)",
    "Pengenalan Wide Area Networks (WAN)",
    "Domain Name System (DNS)",
    "Dynamic Host Configuration Protocol (DHCP)",
    "File Transfer Protocol (FTP) & Trivial FTP (TFTP)",
    "Simple Network Management Protocol (SNMP)",
    "Network Time Protocol (NTP)",
    "Syslog",
    "Standar Wi-Fi (802.11a/b/g/n/ac/ax)",
    "Komponen Jaringan Nirkabel (AP, WLC)",
    "Keamanan Nirkabel (WEP, WPA, WPA2, WPA3)",
    "Site Survey Nirkabel",
    "Troubleshooting Masalah Nirkabel",
    "Pengenalan Jaringan Seluler (4G/5G)",
    "Ancaman Keamanan Jaringan Umum",
    "Keamanan Switch (Port Security, DHCP Snooping)",
    "Virtual Private Networks (VPN) Lanjutan (IPSec & SSL)",
    "Next-Generation Firewalls (NGFW) & Unified Threat Management (UTM)",
    "Pengenalan SIEM (Security Information and Event Management)",
    "Network Access Control (NAC)",
    "Border Gateway Protocol (BGP)",
    "Multiprotocol Label Switching (MPLS)",
    "Quality of Service (QoS)",
    "Desain Jaringan Hierarkis (Core, Distribution, Access)",
    "IPv6",
    "Software-Defined Networking (SDN)",
    "Pengenalan Jaringan di Cloud (AWS, Azure, GCP)",
    "Amazon VPC & Subnets",
    "Azure VNet & Subnets",
    "AWS Security Groups & Network ACLs",
    "Menghubungkan Jaringan On-premise ke Cloud (VPN & Direct Connect)",
    "Load Balancing di Cloud",
    "Mengapa Otomatisasi Jaringan Penting?",
    "Dasar-dasar Python untuk Otomatisasi Jaringan",
    "Berinteraksi dengan Perangkat Jaringan via SSH (Paramiko/Netmiko)",
    "Parsing Data Konfigurasi & Operasional",
    "Pengenalan Ansible untuk Otomatisasi Jaringan",
    "REST APIs & Postman untuk Perangkat Jaringan Modern",
    "Sertifikasi Jaringan (CCNA, JNCIA, CompTIA Network+)",
    "Troubleshooting Jaringan: Metodologi Top-Down & Bottom-Up",
    "Menggunakan Alat Diagnostik Jaringan (ping, traceroute, nslookup)",
    "Dokumentasi Jaringan",
    "Wawancara Teknis Insinyur Jaringan",
    "Tren Masa Depan: 5G, IoT, & Edge Computing"
]