import json
from app import create_app, db
from app.models import Module, Lesson, Project, Roadmap

# Buat instance aplikasi untuk mendapatkan konteks
app = create_app()

# Semua operasi database harus berada di dalam app_context
with app.app_context():
    # 1. Hapus data lama untuk memastikan kebersihan data
    print("Membersihkan data lama...")
    Project.query.delete()
    Lesson.query.delete()
    Module.query.delete()
    Roadmap.query.delete()
    db.session.commit()
    print("Data lama berhasil dibersihkan.")

    # 2. Buat satu Roadmap umum
    roadmap_umum = Roadmap(title='Roadmap Belajar Farsight', level='General')
    db.session.add(roadmap_umum)
    db.session.flush()
    print("Roadmap umum berhasil dibuat.")

    # 3. Definisikan struktur kurikulum baru yang 100% lengkap dan logis
    career_data = {
        'frontend': [
            # 10 Modul Lengkap untuk Frontend
            {
                'title': 'Fondasi Web - HTML & CSS', 'level': 'beginner', 'lessons': [
                    {'title': 'Cara Kerja Web & Internet', 'description': 'Memahami alur dari browser ke server.'},
                    {'title': 'Setup Local Environment', 'description': 'Menginstal VS Code, Node.js, dan Git.'},
                    {'title': 'HTML Fundamental: Struktur & Elemen Dasar', 'description': 'Mempelajari tag-tag dasar seperti h1, p, div.'},
                    {'title': 'HTML Semantik & Aksesibilitas', 'description': 'Menggunakan tag seperti <article>, <nav> untuk SEO.'},
                    {'title': 'Membangun Form dengan HTML', 'description': 'Membuat form input untuk interaksi pengguna.'},
                    {'title': 'CSS Fundamental: Selektor & Properti Dasar', 'description': 'Memberi gaya pada elemen HTML.'},
                ], 'projects': [{'title': 'Halaman Tribut Sederhana', 'difficulty': 'Beginner', 'tech_stack': 'HTML5, CSS3'}]
            },
            {
                'title': 'Layout & Desain Responsif', 'level': 'beginner', 'lessons': [
                    {'title': 'CSS Box Model: Margin, Padding, Border', 'description': 'Memahami bagaimana ruang di sekitar elemen bekerja.'},
                    {'title': 'Layouting dengan Flexbox', 'description': 'Membangun layout satu dimensi yang fleksibel.'},
                    {'title': 'Layouting dengan CSS Grid', 'description': 'Membangun layout dua dimensi yang kompleks.'},
                    {'title': 'CSS Positioning & Stacking Context', 'description': 'Mengontrol posisi elemen secara presisi.'},
                    {'title': 'Prinsip Desain Responsif & Media Queries', 'description': 'Membuat website beradaptasi di berbagai ukuran layar.'},
                    {'title': 'Unit Responsif: vw, vh, %, rem', 'description': 'Memahami unit-unit CSS untuk desain yang fleksibel.'},
                ], 'projects': [{'title': 'Website Portofolio Pribadi', 'difficulty': 'Beginner', 'tech_stack': 'HTML, CSS (Flexbox/Grid)'}]
            },
            {
                'title': 'Interaktivitas dengan JavaScript', 'level': 'intermediate', 'lessons': [
                    {'title': 'JavaScript Fundamental: Variabel, Tipe Data, Operator', 'description': 'Dasar-dasar bahasa pemrograman JavaScript.'},
                    {'title': 'Struktur Kontrol: Percabangan & Perulangan', 'description': 'Mengontrol alur eksekusi program.'},
                    {'title': 'Fungsi, Scope, & Closures', 'description': 'Membuat blok kode yang dapat digunakan kembali.'},
                    {'title': 'Struktur Data: Array & Objek', 'description': 'Mengelola kumpulan data.'},
                    {'title': 'Dasar DOM (Document Object Model)', 'description': 'Memahami representasi HTML di JavaScript.'},
                    {'title': 'Manipulasi DOM & Event Handling', 'description': 'Mengubah konten dan merespons aksi pengguna.'},
                ], 'projects': [
                    {'title': 'Aplikasi Kalkulator Sederhana', 'difficulty': 'Beginner', 'tech_stack': 'HTML, CSS, JavaScript'},
                    {'title': 'Aplikasi To-Do List Interaktif', 'difficulty': 'Intermediate', 'tech_stack': 'HTML, CSS, JavaScript (DOM)'},
                ]
            },
            {
                'title': 'JavaScript Modern & Asynchronous', 'level': 'intermediate', 'lessons': [
                    {'title': 'JavaScript Modern (ES6+): Arrow Functions, Destructuring, Spread Operator', 'description': 'Fitur-fitur baru yang membuat kode lebih ringkas.'},
                    {'title': 'Konsep Asynchronous: Callback, Promise', 'description': 'Menangani operasi yang membutuhkan waktu.'},
                    {'title': 'Async/Await untuk Kode Asynchronous yang Lebih Bersih', 'description': 'Sintaks modern untuk menangani Promise.'},
                    {'title': 'Interaksi dengan API: Fetch API', 'description': 'Mengambil data dari server eksternal.'},
                    {'title': 'Bekerja dengan JSON', 'description': 'Format data standar untuk komunikasi web.'},
                    {'title': 'Dasar-dasar NPM & Module Bundler (Vite)', 'description': 'Mengelola dependensi dan membangun proyek.'},
                ], 'projects': [{'title': 'Aplikasi Cuaca (Weather API)', 'difficulty': 'Intermediate', 'tech_stack': 'JavaScript, Fetch API'}]
            },
            {
                'title': 'Framework Modern - React.js', 'level': 'advanced', 'lessons': [
                    {'title': 'Berpikir dalam Komponen: JSX & Props', 'description': 'Membangun UI dengan blok-blok yang dapat digunakan kembali.'},
                    {'title': 'Manajemen State dengan Hooks: useState', 'description': 'Membuat komponen "mengingat" data.'},
                    {'title': 'Lifecycle & Side Effects dengan Hooks: useEffect', 'description': 'Menjalankan kode saat komponen dirender atau diperbarui.'},
                    {'title': 'Conditional Rendering & Lists', 'description': 'Menampilkan UI berdasarkan kondisi dan data.'},
                    {'title': 'Mengelola Form & Input Pengguna di React', 'description': 'Cara modern menangani form di React.'},
                    {'title': 'Client-Side Routing dengan React Router', 'description': 'Membangun aplikasi multi-halaman (SPA).'},
                ], 'projects': [{'title': 'Aplikasi Pencarian Film (Movie DB API)', 'difficulty': 'Intermediate', 'tech_stack': 'React.js, Fetch API'}]
            },
            {
                'title': 'Ekosistem React & Styling', 'level': 'advanced', 'lessons': [
                    {'title': 'Manajemen State Global dengan Redux Toolkit', 'description': 'Mengelola state yang kompleks di seluruh aplikasi.'},
                    {'title': 'Alternatif State Management: Zustand', 'description': 'Pendekatan yang lebih sederhana untuk state global.'},
                    {'title': 'Manajemen State Server dengan React Query', 'description': 'Menyederhanakan caching dan fetching data API.'},
                    {'title': 'Styling di React: CSS Modules', 'description': 'Styling komponen yang terisolasi.'},
                    {'title': 'CSS-in-JS dengan Styled-Components', 'description': 'Menulis CSS di dalam file JavaScript.'},
                    {'title': 'Utility-First Styling dengan Tailwind CSS', 'description': 'Mempercepat proses styling dengan kelas utilitas.'},
                ], 'projects': [{'title': 'Keranjang Belanja E-commerce', 'difficulty': 'Advanced', 'tech_stack': 'React.js, Redux Toolkit, Tailwind CSS'}]
            },
            {
                'title': 'Pengujian & Kualitas Kode', 'level': 'expert', 'lessons': [
                    {'title': 'Pengenalan TypeScript untuk Aplikasi React', 'description': 'Menambahkan keamanan tipe pada JavaScript.'},
                    {'title': 'Pengujian Unit (Unit Testing) dengan Vitest', 'description': 'Memastikan setiap fungsi kecil bekerja benar.'},
                    {'title': 'Pengujian Komponen dengan React Testing Library', 'description': 'Memastikan komponen UI bekerja sesuai harapan pengguna.'},
                    {'title': 'Pengujian End-to-End (E2E) dengan Cypress', 'description': 'Menguji alur kerja aplikasi secara keseluruhan.'},
                    {'title': 'Code Formatting & Linting (Prettier & ESLint)', 'description': 'Menjaga konsistensi dan kualitas kode secara otomatis.'},
                    {'title': 'Dasar-dasar Git Lanjutan: Branching & Merge', 'description': 'Kolaborasi tim yang efektif dengan Git.'},
                ], 'projects': [{'title': 'Refactor Aplikasi Film ke TypeScript & Tambah Testing', 'difficulty': 'Advanced', 'tech_stack': 'React.js, TypeScript, Vitest'}]
            },
            {
                'title': 'Performa & Aksesibilitas Web', 'level': 'expert', 'lessons': [
                    {'title': 'Optimasi Performa React: memo, useMemo, useCallback', 'description': 'Mencegah rendering yang tidak perlu.'},
                    {'title': 'Analisis Performa dengan Lighthouse & DevTools', 'description': 'Mengukur dan menemukan bottleneck performa.'},
                    {'title': 'Lazy Loading Komponen & Gambar', 'description': 'Mempercepat waktu muat halaman awal.'},
                    {'title': 'Prinsip Aksesibilitas Web (WCAG)', 'description': 'Memastikan aplikasi dapat digunakan oleh semua orang.'},
                    {'title': 'Implementasi ARIA Roles & Semantic HTML', 'description': 'Meningkatkan aksesibilitas untuk screen reader.'},
                    {'title': 'Internasionalisasi (i18n) di React', 'description': 'Membuat aplikasi yang mendukung berbagai bahasa.'},
                ], 'projects': [{'title': 'Audit & Optimasi Performa Website Portofolio', 'difficulty': 'Advanced', 'tech_stack': 'Lighthouse, React DevTools'}]
            },
            {
                'title': 'Framework Full-stack & Deployment', 'level': 'expert', 'lessons': [
                    {'title': 'Pengenalan Rendering Sisi Server (SSR)', 'description': 'Memahami perbedaan dengan Client-Side Rendering.'},
                    {'title': 'Membangun Aplikasi dengan Next.js', 'description': 'Framework React produksi untuk aplikasi full-stack.'},
                    {'title': 'File-based Routing di Next.js', 'description': 'Cara Next.js mengelola halaman dan rute.'},
                    {'title': 'Data Fetching di Next.js (SSR & SSG)', 'description': 'Mengambil data di sisi server untuk SEO dan performa.'},
                    {'title': 'Membuat API Routes di Next.js', 'description': 'Membangun backend langsung di dalam proyek Next.js Anda.'},
                    {'title': 'Deployment ke Vercel', 'description': 'Men-deploy aplikasi Next.js dengan mudah.'},
                ], 'projects': [{'title': 'Website Blog Full-stack dengan Next.js', 'difficulty': 'Expert', 'tech_stack': 'Next.js, React.js, TypeScript'}]
            },
            {
                'title': 'Persiapan Karier Frontend', 'level': 'expert', 'lessons': [
                    {'title': 'Membangun Portofolio yang Menjual', 'description': 'Menyajikan proyek Anda secara profesional.'},
                    {'title': 'Menulis CV & Profil LinkedIn yang Efektif', 'description': 'Meningkatkan visibilitas di mata rekruter.'},
                    {'title': 'Struktur Data & Algoritma untuk Wawancara', 'description': 'Persiapan untuk pertanyaan coding interview.'},
                    {'title': 'Wawancara Perilaku (Behavioral Interview)', 'description': 'Menjawab pertanyaan tentang kerja tim dan pengalaman.'},
                    {'title': 'Wawancara Sistem Desain Frontend', 'description': 'Merancang arsitektur aplikasi frontend dalam wawancara.'},
                    {'title': 'Berkontribusi pada Proyek Open Source', 'description': 'Mendapatkan pengalaman dunia nyata dan membangun jaringan.'},
                ], 'projects': [{'title': 'Simulasi Wawancara Teknis Langsung', 'difficulty': 'Expert', 'tech_stack': 'Komunikasi, Problem Solving'}]
            }
        ],
        'backend': [
            # 10 Modul Lengkap untuk Backend
            {
                'title': 'Fondasi Backend & Bahasa Pemrograman', 'level': 'beginner', 'lessons': [
                    {'title': 'Pengenalan Arsitektur Klien-Server & HTTP', 'description': 'Memahami bagaimana web bekerja dari sisi server.'},
                    {'title': 'Memilih Bahasa: Node.js vs Python vs Go', 'description': 'Kelebihan dan kekurangan setiap bahasa.'},
                    {'title': 'Dasar Pemrograman dengan Node.js & JavaScript', 'description': 'Mempelajari sintaks dasar dan konsep inti.'},
                    {'title': 'Setup Environment & Package Manager (NPM)', 'description': 'Mempersiapkan lingkungan pengembangan.'},
                    {'title': 'Asynchronous Programming di Node.js', 'description': 'Callback, Promise, dan Async/Await.'},
                    {'title': 'Manajemen Environment & Konfigurasi (.env)', 'description': 'Menyimpan kunci API dan kredensial dengan aman.'}
                ], 'projects': [{'title': 'Program CLI Sederhana', 'difficulty': 'Beginner', 'tech_stack': 'Node.js'}]
            },
            {
                'title': 'Membangun API dengan Express.js', 'level': 'beginner', 'lessons': [
                    {'title': 'Membangun Server Pertama dengan Express.js', 'description': 'Membuat endpoint API sederhana.'},
                    {'title': 'Prinsip Desain RESTful API', 'description': 'Merancang API yang terstruktur dan intuitif.'},
                    {'title': 'Routing & Controllers', 'description': 'Mengorganisir kode API.'},
                    {'title': 'Middleware di Express.js', 'description': 'Menjalankan kode di antara request dan response.'},
                    {'title': 'Menangani Request Body (JSON)', 'description': 'Menerima data dari klien.'},
                    {'title': 'Validasi Input & Penanganan Error', 'description': 'Membuat API yang andal dan aman.'}
                ], 'projects': [{'title': 'API Sederhana untuk To-Do List (In-Memory)', 'difficulty': 'Beginner', 'tech_stack': 'Node.js, Express.js'}]
            },
            {
                'title': 'Database Relasional & SQL', 'level': 'intermediate', 'lessons': [
                    {'title': 'Pengenalan Database Relasional', 'description': 'Memahami tabel, baris, dan kolom.'},
                    {'title': 'Dasar SQL: SELECT, WHERE, INSERT, UPDATE, DELETE', 'description': 'Bahasa untuk berkomunikasi dengan database.'},
                    {'title': 'Desain Skema Database & Normalisasi', 'description': 'Merancang database yang efisien.'},
                    {'title': 'JOIN & Relasi Antar Tabel', 'description': 'Menggabungkan data dari beberapa tabel.'},
                    {'title': 'Instalasi & Penggunaan PostgreSQL', 'description': 'Database relasional open source yang kuat.'},
                    {'title': 'Koneksi Database ke Aplikasi Node.js', 'description': 'Menghubungkan server dengan database.'}
                ], 'projects': [{'title': 'API Blog (CRUD) dengan PostgreSQL', 'difficulty': 'Intermediate', 'tech_stack': 'Node.js, Express.js, PostgreSQL'}]
            },
            {
                'title': 'ORM & Keamanan API', 'level': 'intermediate', 'lessons': [
                    {'title': 'Pengenalan Object-Relational Mapper (ORM)', 'description': 'Mengabstraksi query SQL dengan kode.'},
                    {'title': 'Menggunakan Prisma sebagai ORM Modern', 'description': 'Berinteraksi dengan database secara type-safe.'},
                    {'title': 'Autentikasi Berbasis Token dengan JWT', 'description': 'Mengamankan endpoint dengan login.'},
                    {'title': 'Password Hashing dengan Bcrypt', 'description': 'Menyimpan password pengguna dengan aman.'},
                    {'title': 'Otorisasi & Kontrol Akses Berbasis Peran', 'description': 'Mengontrol apa yang bisa dilakukan pengguna.'},
                    {'title': 'Keamanan Dasar API (CORS, Helmet.js)', 'description': 'Melindungi API dari serangan umum.'}
                ], 'projects': [{'title': 'API Blog dengan Sistem Login & Register', 'difficulty': 'Intermediate', 'tech_stack': 'Node.js, Express.js, JWT, Prisma'}]
            },
            {
                'title': 'Containerisasi & Docker', 'level': 'advanced', 'lessons': [
                    {'title': 'Pengenalan Container & Perbedaannya dengan VM', 'description': 'Memahami teknologi di balik Docker.'},
                    {'title': 'Menulis Dockerfile untuk Aplikasi Node.js', 'description': 'Mendefinisikan bagaimana aplikasi dibungkus.'},
                    {'title': 'Membangun & Menjalankan Docker Image', 'description': 'Membuat dan menjalankan kontainer.'},
                    {'title': 'Docker Networking & Volumes', 'description': 'Komunikasi antar kontainer dan persistensi data.'},
                    {'title': 'Menjalankan Aplikasi Multi-Container dengan Docker Compose', 'description': 'Mengelola aplikasi dan database secara bersamaan.'},
                    {'title': 'Optimasi Docker Image (Multi-stage builds)', 'description': 'Membuat image yang lebih kecil dan aman.'}
                ], 'projects': [{'title': 'Dockerize Aplikasi Blog Lengkap', 'difficulty': 'Advanced', 'tech_stack': 'Node.js, PostgreSQL, Docker, Docker Compose'}]
            },
            {
                'title': 'CI/CD & Deployment', 'level': 'advanced', 'lessons': [
                    {'title': 'Konsep Continuous Integration & Delivery (CI/CD)', 'description': 'Filosofi merilis software secara cepat dan andal.'},
                    {'title': 'Membangun Pipeline dengan GitHub Actions', 'description': 'Otomatisasi proses build, test, dan deploy.'},
                    {'title': 'Pengujian Otomatis dalam Pipeline (Unit & Integration)', 'description': 'Memastikan kualitas kode sebelum deployment.'},
                    {'title': 'Membangun dan Mendorong Docker Image dalam Pipeline', 'description': 'Mengintegrasikan Docker dengan CI/CD.'},
                    {'title': 'Deploy Aplikasi ke Cloud (Render/DigitalOcean)', 'description': 'Membuat aplikasi dapat diakses secara publik.'},
                    {'title': 'Logging & Monitoring Dasar di Produksi', 'description': 'Memantau kesehatan aplikasi setelah deploy.'}
                ], 'projects': [{'title': 'Membuat Pipeline CI/CD untuk API Blog', 'difficulty': 'Advanced', 'tech_stack': 'GitHub Actions, Docker'}]
            },
            {
                'title': 'Arsitektur Backend Tingkat Lanjut', 'level': 'expert', 'lessons': [
                    {'title': 'Pengenalan Arsitektur Microservices', 'description': 'Memecah aplikasi besar menjadi layanan-layanan kecil.'},
                    {'title': 'Komunikasi Antar Service (REST vs gRPC)', 'description': 'Memilih cara terbaik bagi service untuk berkomunikasi.'},
                    {'title': 'Komunikasi Asinkron dengan Message Broker (RabbitMQ)', 'description': 'Mengaktifkan komunikasi yang andal dan terpisah.'},
                    {'title': 'API Gateway sebagai Pintu Masuk Tunggal', 'description': 'Menyederhanakan akses ke arsitektur microservices.'},
                    {'title': 'Pola Desain Microservices (Saga, CQRS)', 'description': 'Pola-pola untuk mengatasi tantangan dalam microservices.'},
                    {'title': 'Service Discovery', 'description': 'Bagaimana service menemukan satu sama lain.'}
                ], 'projects': [{'title': 'Sistem Notifikasi dengan Microservices', 'difficulty': 'Expert', 'tech_stack': 'Node.js, Docker, RabbitMQ'}]
            },
            {
                'title': 'Database Tingkat Lanjut', 'level': 'expert', 'lessons': [
                    {'title': 'Pengenalan Database NoSQL (MongoDB)', 'description': 'Alternatif fleksibel untuk database relasional.'},
                    {'title': 'Desain Skema di MongoDB', 'description': 'Perbedaan dengan desain skema relasional.'},
                    {'title': 'Caching untuk Performa dengan Redis', 'description': 'Mempercepat respons API secara drastis.'},
                    {'title': 'Indeks Database & Optimasi Query', 'description': 'Membuat query database berjalan lebih cepat.'},
                    {'title': 'Transaksi Database', 'description': 'Memastikan konsistensi data.'},
                    {'title': 'Pengenalan Search Engine (Elasticsearch)', 'description': 'Fitur pencarian yang kuat untuk aplikasi.'}
                ], 'projects': [{'title': 'API E-commerce dengan MongoDB & Redis Cache', 'difficulty': 'Expert', 'tech_stack': 'Node.js, MongoDB, Redis'}]
            },
            {
                'title': 'Paradigma API Alternatif', 'level': 'expert', 'lessons': [
                    {'title': 'Membangun API dengan GraphQL', 'description': 'Memberi klien kekuatan untuk meminta data yang mereka butuhkan.'},
                    {'title': 'Skema & Resolver di GraphQL', 'description': 'Mendefinisikan dan mengimplementasikan API GraphQL.'},
                    {'title': 'Real-time Communication dengan WebSockets', 'description': 'Komunikasi dua arah antara klien dan server.'},
                    {'title': 'Membangun Aplikasi Chat dengan Socket.IO', 'description': 'Implementasi praktis dari WebSockets.'},
                    {'title': 'Pengenalan gRPC', 'description': 'Komunikasi performa tinggi untuk microservices.'},
                    {'title': 'Webhooks', 'description': 'Bagaimana sistem eksternal dapat memberi tahu aplikasi Anda.'}
                ], 'projects': [{'title': 'API GraphQL untuk Sistem Ulasan Produk', 'difficulty': 'Expert', 'tech_stack': 'Node.js, GraphQL, Apollo Server'}]
            },
            {
                'title': 'Persiapan Karier Backend', 'level': 'expert', 'lessons': [
                    {'title': 'Wawancara Sistem Desain (System Design Interview)', 'description': 'Merancang arsitektur sistem yang skalabel.'},
                    {'title': 'Skalabilitas Horizontal vs Vertikal', 'description': 'Strategi untuk menangani beban traffic yang besar.'},
                    {'title': 'Load Balancing', 'description': 'Mendistribusikan traffic ke beberapa server.'},
                    {'title': 'Prinsip SOLID & Clean Architecture', 'description': 'Menulis kode yang mudah dipelihara.'},
                    {'title': 'Struktur Data & Algoritma untuk Wawancara', 'description': 'Persiapan untuk pertanyaan coding interview.'},
                    {'title': 'Profil Profesional & Portofolio Backend', 'description': 'Menyajikan keahlian Anda kepada rekruter.'}
                ], 'projects': [{'title': 'Simulasi Wawancara Desain Sistem', 'difficulty': 'Expert', 'tech_stack': 'Problem Solving, Komunikasi'}]
            }
        ],
        'data-analyst': [
            # 10 Modul Lengkap untuk Data Analyst
            {
                'title': 'Fondasi Analisis Data', 'level': 'beginner', 'lessons': [
                    {'title': 'Pengenalan Ekosistem Data Science', 'description': 'Memahami peran dan tools seorang Data Analyst.'},
                    {'title': 'Statistik Deskriptif (Mean, Median, Modus)', 'description': 'Meringkas data menjadi informasi yang berguna.'},
                    {'title': 'Statistik Inferensial Dasar', 'description': 'Membuat kesimpulan dari sampel data.'},
                    {'title': 'Setup Environment (Anaconda & Jupyter Notebook)', 'description': 'Mempersiapkan alat kerja utama.'},
                    {'title': 'Dasar Pemrograman Python untuk Data', 'description': 'Sintaks dasar Python yang paling sering digunakan.'},
                    {'title': 'Komputasi Numerik dengan NumPy', 'description': 'Operasi matematika yang efisien pada data.'}
                ], 'projects': [{'title': 'Menghitung Statistik Dasar dari Dataset', 'difficulty': 'Beginner', 'tech_stack': 'Python, NumPy, Jupyter'}]
            },
            {
                'title': 'Manipulasi Data dengan Pandas', 'level': 'beginner', 'lessons': [
                    {'title': 'Struktur Data Pandas: Series & DataFrame', 'description': 'Objek inti dalam Pandas.'},
                    {'title': 'Membaca & Menulis Data (CSV, Excel)', 'description': 'Mengimpor dan mengekspor data.'},
                    {'title': 'Seleksi & Filtering Data (loc, iloc)', 'description': 'Mengambil data yang relevan dari DataFrame.'},
                    {'title': 'Teknik Data Cleaning & Preprocessing', 'description': 'Menangani nilai hilang, duplikat, dan outliers.'},
                    {'title': 'Grouping & Aggregation (groupby)', 'description': 'Meringkas data berdasarkan kategori.'},
                    {'title': 'Menggabungkan DataFrame (Merge & Concat)', 'description': 'Menggabungkan data dari berbagai sumber.'}
                ], 'projects': [{'title': 'Pembersihan & Pra-pemrosesan Data Titanic', 'difficulty': 'Beginner', 'tech_stack': 'Python, Pandas'}]
            },
            {
                'title': 'Query Database dengan SQL', 'level': 'intermediate', 'lessons': [
                    {'title': 'Pengenalan Database Relasional', 'description': 'Memahami tabel, kunci primer, dan kunci asing.'},
                    {'title': 'Query Data dengan SQL (SELECT, FROM, WHERE)', 'description': 'Mengambil data dari database.'},
                    {'title': 'Filtering & Sorting (ORDER BY, LIMIT, DISTINCT)', 'description': 'Mengatur dan membatasi hasil query.'},
                    {'title': 'Fungsi Agregat (COUNT, SUM, AVG)', 'description': 'Melakukan perhitungan pada data.'},
                    {'title': 'Menggabungkan Tabel dengan JOIN', 'description': 'Mengambil data dari beberapa tabel sekaligus.'},
                    {'title': 'Subqueries & Common Table Expressions (CTEs)', 'description': 'Menulis query yang kompleks dan mudah dibaca.'}
                ], 'projects': [{'title': 'Analisis Data Penjualan dengan SQL', 'difficulty': 'Intermediate', 'tech_stack': 'SQL, PostgreSQL'}]
            },
            {
                'title': 'Visualisasi Data Statis', 'level': 'intermediate', 'lessons': [
                    {'title': 'Prinsip Desain Visualisasi yang Efektif', 'description': 'Memilih grafik yang tepat untuk menceritakan sebuah kisah.'},
                    {'title': 'Pengenalan Matplotlib', 'description': 'Library dasar untuk visualisasi di Python.'},
                    {'title': 'Visualisasi Statistik dengan Seaborn', 'description': 'Membuat plot statistik yang indah dengan mudah.'},
                    {'title': 'Histogram & Box Plot', 'description': 'Memahami distribusi data.'},
                    {'title': 'Scatter Plot & Bar Chart', 'description': 'Memahami hubungan dan perbandingan antar variabel.'},
                    {'title': 'Kustomisasi Plot (Label, Judul, Warna)', 'description': 'Membuat visualisasi yang siap untuk presentasi.'}
                ], 'projects': [{'title': 'Analisis Eksplorasi Data (EDA) Penjualan Retail', 'difficulty': 'Intermediate', 'tech_stack': 'Python, Pandas, Matplotlib, Seaborn'}]
            },
            {
                'title': 'Business Intelligence & Dashboard Interaktif', 'level': 'advanced', 'lessons': [
                    {'title': 'Pengenalan Business Intelligence (BI)', 'description': 'Mengubah data menjadi keputusan bisnis.'},
                    {'title': 'Membangun Dashboard Interaktif dengan Tableau', 'description': 'Mengubah data menjadi insight yang interaktif.'},
                    {'title': 'Koneksi Data & Calculated Fields di Tableau', 'description': 'Mengolah data langsung di dalam Tableau.'},
                    {'title': 'Membangun Dashboard Alternatif dengan Looker Studio', 'description': 'Tools BI populer dari Google.'},
                    {'title': 'Teknik Storytelling with Data', 'description': 'Membangun narasi di sekitar temuan data Anda.'},
                    {'title': 'Key Performance Indicators (KPIs)', 'description': 'Mengukur keberhasilan bisnis dengan metrik yang tepat.'}
                ], 'projects': [{'title': 'Dashboard Analisis Pasar Properti di Tableau', 'difficulty': 'Intermediate', 'tech_stack': 'Tableau, SQL'}]
            },
            {
                'title': 'Statistik Terapan untuk Analis', 'level': 'advanced', 'lessons': [
                    {'title': 'Probabilitas & Teorema Bayes', 'description': 'Dasar dari pemodelan statistik.'},
                    {'title': 'Distribusi Probabilitas (Normal, Binomial)', 'description': 'Memahami pola dalam data acak.'},
                    {'title': 'Hypothesis Testing (Uji Hipotesis)', 'description': 'Memvalidasi asumsi dengan data secara ilmiah.'},
                    {'title': 'Analisis Regresi untuk Prediksi', 'description': 'Memahami hubungan antara variabel.'},
                    {'title': 'Pengenalan Time Series Analysis', 'description': 'Menganalisis data yang bergantung pada waktu.'},
                    {'title': 'Confidence Intervals', 'description': 'Mengukur ketidakpastian dalam estimasi.'}
                ], 'projects': [{'title': 'Prediksi Penjualan Bulanan (Time Series)', 'difficulty': 'Advanced', 'tech_stack': 'Python, Pandas, Statsmodels'}]
            },
            {
                'title': 'Analisis Bisnis & Produk', 'level': 'expert', 'lessons': [
                    {'title': 'Analisis Funnel & Konversi', 'description': 'Memahami perjalanan pelanggan.'},
                    {'title': 'Analisis Kohort & Retensi Pengguna', 'description': 'Mengukur loyalitas pelanggan dari waktu ke waktu.'},
                    {'title': 'Segmentasi Pelanggan (RFM Analysis)', 'description': 'Mengelompokkan pelanggan berdasarkan perilaku.'},
                    {'title': 'Menghitung Customer Lifetime Value (LTV)', 'description': 'Mengukur nilai jangka panjang seorang pelanggan.'},
                    {'title': 'Desain & Analisis A/B Testing', 'description': 'Mengukur dampak perubahan produk secara akurat.'},
                    {'title': 'Analisis Sentimen Dasar', 'description': 'Memahami opini pelanggan dari teks.'}
                ], 'projects': [{'title': 'Analisis Hasil A/B Test untuk Kampanye Marketing', 'difficulty': 'Advanced', 'tech_stack': 'Python, Pandas, SciPy'}]
            },
            {
                'title': 'Data Engineering Dasar untuk Analis', 'level': 'expert', 'lessons': [
                    {'title': 'Konsep ETL (Extract, Transform, Load)', 'description': 'Proses fundamental dalam rekayasa data.'},
                    {'title': 'Pengenalan Data Warehouse & Data Lake', 'description': 'Tempat penyimpanan data untuk analisis.'},
                    {'title': 'Web Scraping Dasar dengan BeautifulSoup', 'description': 'Mengambil data dari halaman web.'},
                    {'title': 'Pengenalan Git & Version Control', 'description': 'Mengelola kode dan analisis secara kolaboratif.'},
                    {'title': 'Otomatisasi Laporan dengan Papermill', 'description': 'Menjalankan Jupyter Notebook secara terprogram.'},
                    {'title': 'Dasar-dasar Cloud (AWS S3, Google BigQuery)', 'description': 'Menyimpan dan menganalisis data di cloud.'}
                ], 'projects': [{'title': 'Membangun Pipeline ETL Sederhana', 'difficulty': 'Advanced', 'tech_stack': 'Python, BeautifulSoup, PostgreSQL'}]
            },
            {
                'title': 'Alat & Teknik Lanjutan', 'level': 'expert', 'lessons': [
                    {'title': 'Visualisasi Geospasial', 'description': 'Membuat peta dari data lokasi.'},
                    {'title': 'Pengenalan Spreadsheets Lanjutan (Google Sheets/Excel)', 'description': 'Pivot tables, VLOOKUP, dan fungsi lainnya.'},
                    {'title': 'Analisis Teks & NLP Dasar', 'description': 'Mengolah dan menganalisis data teks.'},
                    {'title': 'Berinteraksi dengan API di Python', 'description': 'Mengambil data dari berbagai sumber online.'},
                    {'title': 'Dasar-dasar Machine Learning untuk Analis', 'description': 'Memahami model prediksi sederhana.'},
                    {'title': 'Etika Data & Privasi', 'description': 'Tanggung jawab dalam mengelola data.'}
                ], 'projects': [{'title': 'Analisis Sentimen Tweet dengan Python', 'difficulty': 'Expert', 'tech_stack': 'Python, NLTK/TextBlob, Pandas'}]
            },
            {
                'title': 'Persiapan Karier Analis Data', 'level': 'expert', 'lessons': [
                    {'title': 'Membangun Portofolio Analis Data yang Kuat', 'description': 'Menyajikan proyek Anda secara efektif.'},
                    {'title': 'Studi Kasus Bisnis (Business Case Study)', 'description': 'Latihan memecahkan masalah bisnis nyata.'},
                    {'title': 'Wawancara Teknis SQL', 'description': 'Persiapan untuk pertanyaan SQL dalam wawancara.'},
                    {'title': 'Wawancara Studi Kasus', 'description': 'Mendemonstrasikan pemikiran analitis Anda.'},
                    {'title': 'Presentasi & Komunikasi Data', 'description': 'Menyampaikan insight kepada audiens non-teknis.'},
                    {'title': 'Menulis Resume & Profil LinkedIn', 'description': 'Meningkatkan visibilitas di mata rekruter.'}
                ], 'projects': [{'title': 'Presentasi Studi Kasus End-to-End', 'difficulty': 'Expert', 'tech_stack': 'SQL, Python, Tableau, Komunikasi'}]
            }
        ],
        'ai-ml-engineer': [
            # 10 Modul Lengkap untuk AI/ML Engineer
            {
                'title': 'Fondasi Matematika & Python untuk ML', 'level': 'beginner', 'lessons': [
                    {'title': 'Aljabar Linear Intuitif (Vektor & Matriks)', 'description': 'Memahami objek matematika dasar dalam ML.'},
                    {'title': 'Kalkulus Intuitif (Gradien & Turunan)', 'description': 'Memahami bagaimana model "belajar".'},
                    {'title': 'Statistik & Probabilitas Esensial', 'description': 'Dasar untuk memahami ketidakpastian dalam data.'},
                    {'title': 'Python Lanjutan untuk ML', 'description': 'Struktur data dan OOP yang relevan.'},
                    {'title': 'Manipulasi Data Tingkat Lanjut dengan Pandas', 'description': 'Menyiapkan data kompleks untuk pemodelan.'},
                    {'title': 'Visualisasi Data untuk EDA dengan Seaborn', 'description': 'Menemukan pola dalam data sebelum pemodelan.'}
                ], 'projects': [{'title': 'Analisis Eksplorasi Data (EDA) Mendalam', 'difficulty': 'Beginner', 'tech_stack': 'Python, Pandas, Seaborn'}]
            },
            {
                'title': 'Algoritma Machine Learning Klasik', 'level': 'intermediate', 'lessons': [
                    {'title': 'Supervised Learning: Regresi (Linear, Ridge)', 'description': 'Memprediksi nilai numerik.'},
                    {'title': 'Supervised Learning: Klasifikasi (Logistic Regression, SVM)', 'description': 'Memprediksi kategori.'},
                    {'title': 'Model Berbasis Pohon: Decision Trees & Random Forest', 'description': 'Model yang kuat dan mudah diinterpretasi.'},
                    {'title': 'Gradient Boosting: XGBoost & LightGBM', 'description': 'Algoritma pemenang kompetisi untuk data tabular.'},
                    {'title': 'Unsupervised Learning: Clustering (K-Means)', 'description': 'Menemukan kelompok tersembunyi dalam data.'},
                    {'title': 'Reduksi Dimensi dengan PCA', 'description': 'Menyederhanakan data yang kompleks.'}
                ], 'projects': [
                    {'title': 'Prediksi Harga Rumah (Regresi)', 'difficulty': 'Intermediate', 'tech_stack': 'Python, Scikit-learn, Pandas'},
                    {'title': 'Klasifikasi Jenis Kanker (Klasifikasi)', 'difficulty': 'Intermediate', 'tech_stack': 'Python, Scikit-learn, XGBoost'}
                ]
            },
            {
                'title': 'Evaluasi Model & Feature Engineering', 'level': 'intermediate', 'lessons': [
                    {'title': 'Metrik Evaluasi untuk Regresi (MSE, MAE, R2)', 'description': 'Mengukur kesalahan model regresi.'},
                    {'title': 'Metrik Evaluasi untuk Klasifikasi (Akurasi, Presisi, Recall, F1, ROC-AUC)', 'description': 'Mengukur performa model klasifikasi.'},
                    {'title': 'Cross-Validation', 'description': 'Evaluasi model yang lebih andal.'},
                    {'title': 'Feature Engineering & Selection', 'description': 'Membuat fitur baru dan memilih yang terbaik.'},
                    {'title': 'Menangani Data Kategorikal & Numerik', 'description': 'Transformasi data untuk model.'},
                    {'title': 'Tuning Hyperparameter (Grid Search, Random Search)', 'description': 'Mencari konfigurasi model terbaik.'}
                ], 'projects': [{'title': 'Optimasi Model Prediksi Churn Pelanggan', 'difficulty': 'Intermediate', 'tech_stack': 'Scikit-learn, Pandas'}]
            },
            {
                'title': 'Pengenalan Deep Learning', 'level': 'advanced', 'lessons': [
                    {'title': 'Pengenalan Neural Networks', 'description': 'Dari Perceptron hingga Multi-Layer Perceptron.'},
                    {'title': 'Fungsi Aktivasi & Propagasi Balik (Backpropagation)', 'description': 'Mekanisme belajar dalam jaringan saraf.'},
                    {'title': 'Membangun Jaringan Saraf dengan TensorFlow & Keras', 'description': 'Framework deep learning populer.'},
                    {'title': 'Regularisasi & Optimisasi (Dropout, Adam)', 'description': 'Mencegah overfitting dan mempercepat training.'},
                    {'title': 'Pengenalan PyTorch', 'description': 'Framework deep learning alternatif yang populer.'},
                    {'title': 'Perbedaan TensorFlow vs PyTorch', 'description': 'Kapan harus memilih yang mana.'}
                ], 'projects': [{'title': 'Klasifikasi Gambar Fashion MNIST dengan Neural Network', 'difficulty': 'Advanced', 'tech_stack': 'TensorFlow, Keras'}]
            },
            {
                'title': 'Computer Vision', 'level': 'advanced', 'lessons': [
                    {'title': 'Dasar-dasar Pemrosesan Gambar', 'description': 'Pixel, channel, dan transformasi dasar.'},
                    {'title': 'Convolutional Neural Networks (CNN)', 'description': 'Arsitektur untuk memproses gambar.'},
                    {'title': 'Arsitektur CNN Populer (LeNet, AlexNet, VGG)', 'description': 'Evolusi arsitektur CNN.'},
                    {'title': 'Transfer Learning & Fine-tuning untuk Gambar', 'description': 'Memanfaatkan model raksasa untuk tugas spesifik.'},
                    {'title': 'Augmentasi Data Gambar', 'description': 'Memperbanyak data training secara artifisial.'},
                    {'title': 'Deteksi Objek (YOLO, Faster R-CNN)', 'description': 'Menemukan dan mengklasifikasikan objek dalam gambar.'}
                ], 'projects': [{'title': 'Klasifikasi Gambar Bunga (Transfer Learning)', 'difficulty': 'Advanced', 'tech_stack': 'TensorFlow, Keras'}]
            },
            {
                'title': 'Natural Language Processing (NLP)', 'level': 'expert', 'lessons': [
                    {'title': 'Preprocessing Teks (Tokenization, Stemming, Lemmatization)', 'description': 'Menyiapkan data teks untuk model.'},
                    {'title': 'Representasi Teks (Bag-of-Words, TF-IDF)', 'description': 'Mengubah teks menjadi angka.'},
                    {'title': 'Word Embeddings (Word2Vec, GloVe)', 'description': 'Representasi kata sebagai vektor yang bermakna.'},
                    {'title': 'Recurrent Neural Networks (RNN) & LSTM', 'description': 'Arsitektur untuk memproses data sekuensial.'},
                    {'title': 'Arsitektur Transformer & Self-Attention', 'description': 'Dasar dari model bahasa modern.'},
                    {'title': 'Model Bahasa Pra-terlatih (BERT & GPT)', 'description': 'Memanfaatkan model bahasa raksasa.'}
                ], 'projects': [{'title': 'Analisis Sentimen Ulasan Film dengan BERT', 'difficulty': 'Expert', 'tech_stack': 'Hugging Face Transformers, PyTorch'}]
            },
            {
                'title': 'Unsupervised Learning & Recommender Systems', 'level': 'advanced', 'lessons': [
                    {'title': 'Clustering Tingkat Lanjut (DBSCAN, Hierarchical)', 'description': 'Algoritma clustering alternatif.'},
                    {'title': 'Deteksi Anomali', 'description': 'Menemukan data yang tidak biasa.'},
                    {'title': 'Association Rule Mining (Apriori)', 'description': 'Menemukan hubungan antar item (Market Basket Analysis).'},
                    {'title': 'Pengenalan Sistem Rekomendasi', 'description': 'Collaborative vs Content-Based Filtering.'},
                    {'title': 'Collaborative Filtering (User-based, Item-based)', 'description': 'Merekomendasikan berdasarkan perilaku pengguna lain.'},
                    {'title': 'Matrix Factorization (SVD)', 'description': 'Teknik populer untuk sistem rekomendasi.'}
                ], 'projects': [{'title': 'Sistem Rekomendasi Film Sederhana', 'difficulty': 'Advanced', 'tech_stack': 'Python, Pandas, Surprise'}]
            },
            {
                'title': 'MLOps - Dari Model ke Produksi', 'level': 'expert', 'lessons': [
                    {'title': 'Serving Model sebagai REST API dengan FastAPI', 'description': 'Membuat model dapat diakses oleh aplikasi lain.'},
                    {'title': 'Containerisasi Model dengan Docker', 'description': 'Memastikan model berjalan konsisten di mana saja.'},
                    {'title': 'Experiment Tracking dengan MLflow', 'description': 'Mencatat dan membandingkan hasil eksperimen model.'},
                    {'title': 'Manajemen Model & Versioning', 'description': 'Mengelola berbagai versi model.'},
                    {'title': 'CI/CD untuk Machine Learning dengan GitHub Actions', 'description': 'Otomatisasi proses training dan deployment.'},
                    {'title': 'Monitoring Performa Model di Produksi', 'description': 'Mendeteksi degradasi performa model.'}
                ], 'projects': [{'title': 'Deploy Model Klasifikasi Kanker sebagai API', 'difficulty': 'Expert', 'tech_stack': 'Python, FastAPI, Docker, MLflow'}]
            },
            {
                'title': 'Topik Lanjutan & Tren AI', 'level': 'expert', 'lessons': [
                    {'title': 'Reinforcement Learning Dasar (Q-Learning)', 'description': 'Agen yang belajar dari trial and error.'},
                    {'title': 'Generative AI & GANs (Generative Adversarial Networks)', 'description': 'Model yang dapat menciptakan data baru.'},
                    {'title': 'Explainable AI (XAI) dengan SHAP & LIME', 'description': 'Memahami mengapa model membuat prediksi tertentu.'},
                    {'title': 'AI Ethics & Fairness', 'description': 'Tanggung jawab dalam membangun sistem AI.'},
                    {'title': 'Distributed Training', 'description': 'Melatih model pada banyak mesin.'},
                    {'title': 'Tren Terbaru: Large Language Models (LLMs)', 'description': 'Memahami arsitektur dan kemampuan GPT.'}
                ], 'projects': [{'title': 'Membuat Gambar Sederhana dengan GAN', 'difficulty': 'Expert', 'tech_stack': 'PyTorch/TensorFlow'}]
            },
            {
                'title': 'Persiapan Karier AI/ML', 'level': 'expert', 'lessons': [
                    {'title': 'Membangun Portofolio AI/ML yang Menonjol', 'description': 'Menyajikan proyek Anda secara efektif.'},
                    {'title': 'Struktur Data & Algoritma untuk Wawancara', 'description': 'Pertanyaan coding yang umum.'},
                    {'title': 'Wawancara Machine Learning System Design', 'description': 'Merancang sistem ML end-to-end.'},
                    {'title': 'Wawancara Statistik & Probabilitas', 'description': 'Menguji pemahaman fundamental Anda.'},
                    {'title': 'Menavigasi Peran: ML Engineer vs Data Scientist vs Applied Scientist', 'description': 'Memahami perbedaan dan memilih yang tepat.'},
                    {'title': 'Menulis Resume & Profil LinkedIn', 'description': 'Meningkatkan visibilitas di mata rekruter.'}
                ], 'projects': [{'title': 'Simulasi Wawancara Desain Sistem ML', 'difficulty': 'Expert', 'tech_stack': 'Problem Solving, Komunikasi'}]
            }
        ],
        'devops-engineer': [
            # 10 Modul Lengkap untuk DevOps Engineer
            {
                'title': 'Fondasi Sistem, Jaringan & Linux', 'level': 'beginner', 'lessons': [
                    {'title': 'Dasar Perintah Linux & Manajemen Sistem', 'description': 'Menguasai terminal untuk operasi server.'},
                    {'title': 'Manajemen User & Permissions di Linux', 'description': 'Mengontrol hak akses pada sistem.'},
                    {'title': 'Manajemen Proses & Services (systemd)', 'description': 'Mengelola aplikasi yang berjalan di server.'},
                    {'title': 'Shell Scripting (Bash) untuk Otomatisasi', 'description': 'Menulis skrip untuk tugas-tugas berulang.'},
                    {'title': 'Konsep Jaringan (TCP/IP, DNS, HTTP/S)', 'description': 'Memahami cara komputer berkomunikasi.'},
                    {'title': 'Dasar Keamanan Jaringan (Firewall & Ports)', 'description': 'Mengamankan server dari akses tidak sah.'}
                ], 'projects': [{'title': 'Automasi Backup File dengan Bash Script', 'difficulty': 'Beginner', 'tech_stack': 'Linux, Bash'}]
            },
            {
                'title': 'Web Server & Version Control', 'level': 'beginner', 'lessons': [
                    {'title': 'Pengenalan Web Server (Nginx vs Apache)', 'description': 'Memahami peran web server.'},
                    {'title': 'Instalasi & Konfigurasi Nginx Dasar', 'description': 'Menyajikan konten web ke pengguna.'},
                    {'title': 'Konfigurasi Nginx sebagai Reverse Proxy', 'description': 'Mengarahkan traffic ke aplikasi backend.'},
                    {'title': 'Mengamankan Web Server dengan SSL/TLS (HTTPS)', 'description': 'Enkripsi komunikasi antara klien dan server.'},
                    {'title': 'Dasar-dasar Git untuk Version Control', 'description': 'Melacak perubahan pada kode.'},
                    {'title': 'Kolaborasi dengan Git & GitHub (Branch, Merge, Pull Request)', 'description': 'Bekerja dalam tim menggunakan Git.'}
                ], 'projects': [{'title': 'Setup Web Server Nginx dengan HTTPS', 'difficulty': 'Beginner', 'tech_stack': 'Linux, Nginx'}]
            },
            {
                'title': 'Containerisasi dengan Docker', 'level': 'intermediate', 'lessons': [
                    {'title': 'Pengenalan Container & Perbedaannya dengan VM', 'description': 'Memahami teknologi di balik Docker.'},
                    {'title': 'Menulis Dockerfile untuk Berbagai Aplikasi', 'description': 'Mendefinisikan bagaimana aplikasi dibungkus.'},
                    {'title': 'Membangun & Menjalankan Docker Image', 'description': 'Membuat dan menjalankan kontainer.'},
                    {'title': 'Docker Networking & Volumes', 'description': 'Komunikasi antar kontainer dan persistensi data.'},
                    {'title': 'Orkestrasi Multi-Container dengan Docker Compose', 'description': 'Menjalankan aplikasi kompleks secara lokal.'},
                    {'title': 'Optimasi Docker Image (Multi-stage builds)', 'description': 'Membuat image yang lebih kecil dan aman.'}
                ], 'projects': [{'title': 'Containerize Aplikasi Web Multi-tier', 'difficulty': 'Intermediate', 'tech_stack': 'Docker, Docker Compose'}]
            },
            {
                'title': 'Infrastructure as Code (IaC)', 'level': 'intermediate', 'lessons': [
                    {'title': 'Pengenalan Infrastructure as Code', 'description': 'Mengelola infrastruktur melalui kode.'},
                    {'title': 'Provisioning Infrastruktur dengan Terraform', 'description': 'Mendefinisikan infrastruktur cloud sebagai kode.'},
                    {'title': 'State Management di Terraform', 'description': 'Melacak status infrastruktur yang dikelola.'},
                    {'title': 'Terraform Modules', 'description': 'Membuat kode IaC yang dapat digunakan kembali.'},
                    {'title': 'Manajemen Konfigurasi Server dengan Ansible', 'description': 'Otomatisasi instalasi dan konfigurasi software.'},
                    {'title': 'Ansible Playbooks & Roles', 'description': 'Mengorganisir tugas-tugas Ansible.'}
                ], 'projects': [{'title': 'Provisioning & Konfigurasi Server Otomatis', 'difficulty': 'Intermediate', 'tech_stack': 'Terraform, Ansible'}]
            },
            {
                'title': 'Continuous Integration (CI)', 'level': 'advanced', 'lessons': [
                    {'title': 'Konsep Continuous Integration & Delivery (CI/CD)', 'description': 'Filosofi merilis software secara cepat dan andal.'},
                    {'title': 'Membangun Pipeline CI dengan GitHub Actions', 'description': 'Otomatisasi proses build dan test.'},
                    {'title': 'Pengujian Otomatis dalam Pipeline (Linting, Unit Test)', 'description': 'Memastikan kualitas kode secara otomatis.'},
                    {'title': 'Analisis Kode Statis & Keamanan (SAST)', 'description': 'Menemukan kerentanan sebelum deployment.'},
                    {'title': 'Membangun Artefak (Docker Image) dalam Pipeline', 'description': 'Mengintegrasikan Docker dengan CI.'},
                    {'title': 'Manajemen Artefak dengan Container Registry', 'description': 'Menyimpan Docker image yang telah dibangun.'}
                ], 'projects': [{'title': 'Membuat Pipeline CI untuk Aplikasi Web', 'difficulty': 'Advanced', 'tech_stack': 'GitHub Actions, Docker'}]
            },
            {
                'title': 'Continuous Delivery/Deployment (CD)', 'level': 'advanced', 'lessons': [
                    {'title': 'Strategi Deployment (Blue-Green, Canary)', 'description': 'Cara merilis versi baru dengan aman.'},
                    {'title': 'Deployment Otomatis ke Server dengan GitHub Actions & SSH', 'description': 'Men-deploy ke VM secara otomatis.'},
                    {'title': 'Pengenalan Orkestrasi Kontainer (Kubernetes)', 'description': 'Mengapa kita membutuhkan Kubernetes.'},
                    {'title': 'Deployment ke Klaster Kubernetes', 'description': 'Menjalankan aplikasi di Kubernetes.'},
                    {'title': 'Secrets Management (HashiCorp Vault, AWS Secrets Manager)', 'description': 'Menyimpan kredensial dengan aman di produksi.'},
                    {'title': 'Manajemen Fitur dengan Feature Flags', 'description': 'Mengaktifkan/menonaktifkan fitur tanpa re-deploy.'}
                ], 'projects': [{'title': 'Membuat Pipeline CD ke Server VM', 'difficulty': 'Advanced', 'tech_stack': 'GitHub Actions, Docker, SSH'}]
            },
            {
                'title': 'Orkestrasi dengan Kubernetes', 'level': 'expert', 'lessons': [
                    {'title': 'Arsitektur & Komponen Inti Kubernetes', 'description': 'Control Plane dan Worker Nodes.'},
                    {'title': 'Objek Kubernetes: Pods, ReplicaSets, Deployments', 'description': 'Menjalankan aplikasi Anda.'},
                    {'title': 'Networking di Kubernetes: Services & Ingress', 'description': 'Mengekspos aplikasi ke dalam dan luar klaster.'},
                    {'title': 'Manajemen Konfigurasi dengan ConfigMap & Secret', 'description': 'Memisahkan konfigurasi dari aplikasi.'},
                    {'title': 'Penyimpanan Persisten dengan Volumes & PVCs', 'description': 'Menyimpan data stateful.'},
                    {'title': 'Manajemen Paket dengan Helm', 'description': 'Menyederhanakan deployment aplikasi di Kubernetes.'}
                ], 'projects': [{'title': 'Deploy Aplikasi Multi-tier ke Klaster Kubernetes', 'difficulty': 'Expert', 'tech_stack': 'Kubernetes, Docker, Helm'}]
            },
            {
                'title': 'Monitoring & Observability', 'level': 'expert', 'lessons': [
                    {'title': 'Tiga Pilar Observability (Metrics, Logs, Traces)', 'description': 'Memahami keadaan sistem Anda.'},
                    {'title': 'Monitoring Metrik dengan Prometheus', 'description': 'Mengumpulkan metrik dari aplikasi dan infrastruktur.'},
                    {'title': 'Manajemen Log Terpusat dengan Loki atau ELK Stack', 'description': 'Mengumpulkan dan menganalisis log.'},
                    {'title': 'Visualisasi Dashboard dengan Grafana', 'description': 'Membuat dashboard untuk memantau kesehatan sistem.'},
                    {'title': 'Sistem Peringatan (Alerting) dengan Alertmanager', 'description': 'Mendapatkan notifikasi jika terjadi masalah.'},
                    {'title': 'Distributed Tracing dengan Jaeger', 'description': 'Melacak request melalui arsitektur microservices.'}
                ], 'projects': [{'title': 'Setup Stack Monitoring (Prometheus & Grafana)', 'difficulty': 'Expert', 'tech_stack': 'Prometheus, Grafana, Docker'}]
            },
            {
                'title': 'Cloud & Keamanan (DevSecOps)', 'level': 'expert', 'lessons': [
                    {'title': 'Dasar-dasar Cloud Provider (AWS/GCP)', 'description': 'Memahami layanan-layanan inti di cloud.'},
                    {'title': 'Identity & Access Management (IAM)', 'description': 'Mengelola hak akses di cloud.'},
                    {'title': 'Keamanan Jaringan Cloud (VPC, Security Groups)', 'description': 'Mengisolasi dan melindungi infrastruktur.'},
                    {'title': 'Prinsip DevSecOps', 'description': 'Mengintegrasikan keamanan ke dalam siklus DevOps.'},
                    {'title': 'Pemindaian Keamanan Kontainer & Dependensi', 'description': 'Menemukan kerentanan secara otomatis.'},
                    {'title': 'Infrastructure as Code Security (tfsec, checkov)', 'description': 'Menganalisis kode Terraform untuk masalah keamanan.'}
                ], 'projects': [{'title': 'Infrastruktur Aman di Cloud dengan Terraform', 'difficulty': 'Expert', 'tech_stack': 'Terraform, AWS/GCP'}]
            },
            {
                'title': 'Persiapan Karier DevOps', 'level': 'expert', 'lessons': [
                    {'title': 'Wawancara Sistem Desain untuk DevOps', 'description': 'Merancang arsitektur CI/CD dan infrastruktur.'},
                    {'title': 'Troubleshooting Skenario Produksi', 'description': 'Mendiagnosis dan memperbaiki masalah di live environment.'},
                    {'title': 'Budaya & Praktik DevOps (Blameless Postmortems)', 'description': 'Lebih dari sekadar tools, ini tentang budaya.'},
                    {'title': 'Manajemen Biaya Cloud (FinOps)', 'description': 'Mengoptimalkan pengeluaran di cloud.'},
                    {'title': 'Tetap Relevan: Belajar Teknologi Baru', 'description': 'Bagaimana terus berkembang di bidang yang cepat berubah.'},
                    {'title': 'Membangun Brand Pribadi sebagai DevOps Engineer', 'description': 'Berbagi pengetahuan dan membangun jaringan.'}
                ], 'projects': [{'title': 'Simulasi Insiden & Postmortem', 'difficulty': 'Expert', 'tech_stack': 'Problem Solving, Komunikasi'}]
            }
        ],
        'cyber-security': [
            # 10 Modul Lengkap untuk Cybersecurity
            {
                'title': 'Fondasi Keamanan Siber & Jaringan', 'level': 'beginner', 'lessons': [
                    {'title': 'Prinsip Dasar Keamanan Informasi (CIA Triad)', 'description': 'Confidentiality, Integrity, Availability.'},
                    {'title': 'Konsep Jaringan Komputer (OSI & TCP/IP Model)', 'description': 'Memahami bagaimana data bergerak.'},
                    {'title': 'Protokol Jaringan Umum (HTTP, DNS, FTP, SMTP)', 'description': 'Bahasa yang digunakan di internet.'},
                    {'title': 'Dasar-dasar Sistem Operasi Linux', 'description': 'Sistem operasi yang dominan di server.'},
                    {'title': 'Perintah Dasar Linux untuk Keamanan', 'description': 'Navigasi, manajemen file, dan izin.'},
                    {'title': 'Pengenalan Virtualisasi & Containers', 'description': 'Membangun lingkungan lab yang aman.'}
                ], 'projects': [{'title': 'Analisis Paket Jaringan dengan Wireshark', 'difficulty': 'Beginner', 'tech_stack': 'Wireshark'}]
            },
            {
                'title': 'Kriptografi & Keamanan Data', 'level': 'beginner', 'lessons': [
                    {'title': 'Pengenalan Kriptografi', 'description': 'Seni mengamankan informasi.'},
                    {'title': 'Enkripsi Simetris (AES)', 'description': 'Satu kunci untuk enkripsi dan dekripsi.'},
                    {'title': 'Enkripsi Asimetris (RSA) & Public Key Infrastructure (PKI)', 'description': 'Dua kunci untuk komunikasi aman.'},
                    {'title': 'Fungsi Hash (SHA-256) & Integritas Data', 'description': 'Memastikan data tidak diubah.'},
                    {'title': 'Digital Signatures & Certificates (SSL/TLS)', 'description': 'Memverifikasi identitas dan mengamankan web.'},
                    {'title': 'Steganografi', 'description': 'Menyembunyikan data di dalam data lain.'}
                ], 'projects': [{'title': 'Enkripsi & Dekripsi File Menggunakan OpenSSL', 'difficulty': 'Beginner', 'tech_stack': 'OpenSSL, Command Line'}]
            },
            {
                'title': 'Keamanan Jaringan & Pertahanan', 'level': 'intermediate', 'lessons': [
                    {'title': 'Firewall & Tipe-tipenya', 'description': 'Benteng pertahanan pertama jaringan.'},
                    {'title': 'Intrusion Detection Systems (IDS) & Intrusion Prevention Systems (IPS)', 'description': 'Mendeteksi dan mencegah serangan.'},
                    {'title': 'Virtual Private Networks (VPN)', 'description': 'Membuat koneksi aman melalui jaringan publik.'},
                    {'title': 'Network Reconnaissance & Scanning (Nmap)', 'description': 'Memetakan jaringan dan menemukan celah.'},
                    {'title': 'Network Hardening', 'description': 'Mengamankan perangkat jaringan.'},
                    {'title': 'Analisis Log Jaringan', 'description': 'Mencari jejak aktivitas mencurigakan.'}
                ], 'projects': [{'title': 'Konfigurasi Firewall Dasar dengan UFW', 'difficulty': 'Intermediate', 'tech_stack': 'Linux, UFW'}]
            },
            {
                'title': 'Ethical Hacking & Penetration Testing', 'level': 'intermediate', 'lessons': [
                    {'title': 'Metodologi Penetration Testing', 'description': 'Langkah-langkah dalam melakukan uji penetrasi.'},
                    {'title': 'Information Gathering (Passive & Active)', 'description': 'Mengumpulkan informasi tentang target.'},
                    {'title': 'Vulnerability Scanning (Nessus/OpenVAS)', 'description': 'Mencari kelemahan yang diketahui.'},
                    {'title': 'Eksploitasi dengan Metasploit Framework', 'description': 'Memanfaatkan kelemahan untuk mendapatkan akses.'},
                    {'title': 'Password Cracking', 'description': 'Teknik untuk memecahkan kata sandi.'},
                    {'title': 'Web Application Hacking (OWASP Top 10)', 'description': 'Kerentanan paling umum pada aplikasi web.'}
                ], 'projects': [
                    {'title': 'Vulnerability Scan pada Mesin Virtual', 'difficulty': 'Intermediate', 'tech_stack': 'OpenVAS, Metasploitable'},
                    {'title': 'Menemukan Kerentanan SQL Injection pada Aplikasi Web Latihan', 'difficulty': 'Advanced', 'tech_stack': 'Burp Suite, DVWA'}
                ]
            },
            {
                'title': 'Keamanan Aplikasi Web', 'level': 'advanced', 'lessons': [
                    {'title': 'SQL Injection (SQLi)', 'description': 'Menyuntikkan query SQL melalui input pengguna.'},
                    {'title': 'Cross-Site Scripting (XSS)', 'description': 'Menyuntikkan skrip berbahaya ke halaman web.'},
                    {'title': 'Cross-Site Request Forgery (CSRF)', 'description': 'Memaksa pengguna melakukan aksi tanpa persetujuan.'},
                    {'title': 'Insecure Deserialization', 'description': 'Kerentanan dalam proses mengubah data menjadi objek.'},
                    {'title': 'Security Misconfigurations', 'description': 'Kesalahan konfigurasi yang membuka celah keamanan.'},
                    {'title': 'Secure Software Development Lifecycle (SSDLC)', 'description': 'Mengintegrasikan keamanan ke dalam proses pengembangan.'}
                ], 'projects': [{'title': 'Analisis & Patching OWASP Juice Shop', 'difficulty': 'Advanced', 'tech_stack': 'OWASP ZAP, Burp Suite'}]
            },
            {
                'title': 'Malware & Reverse Engineering', 'level': 'advanced', 'lessons': [
                    {'title': 'Tipe-tipe Malware (Virus, Worm, Trojan, Ransomware)', 'description': 'Memahami berbagai jenis perangkat lunak berbahaya.'},
                    {'title': 'Analisis Malware Statis', 'description': 'Menganalisis file tanpa menjalankannya.'},
                    {'title': 'Analisis Malware Dinamis (Sandbox)', 'description': 'Menjalankan malware di lingkungan terisolasi.'},
                    {'title': 'Dasar-dasar Reverse Engineering', 'description': 'Membongkar program untuk memahami cara kerjanya.'},
                    {'title': 'Pengenalan Assembly Language', 'description': 'Bahasa tingkat rendah yang penting untuk reverse engineering.'},
                    {'title': 'Menggunakan Disassembler & Debugger (Ghidra, GDB)', 'description': 'Alat untuk menganalisis biner.'}
                ], 'projects': [{'title': 'Analisis Statis Sampel Malware Sederhana', 'difficulty': 'Advanced', 'tech_stack': 'Ghidra, PEview'}]
            },
            {
                'title': 'Digital Forensics & Incident Response', 'level': 'expert', 'lessons': [
                    {'title': 'Proses Digital Forensics', 'description': 'Mengumpulkan, menganalisis, dan melaporkan bukti digital.'},
                    {'title': 'Forensik Memori (Volatility)', 'description': 'Menganalisis RAM untuk mencari jejak aktivitas.'},
                    {'title': 'Forensik Disk (Autopsy)', 'description': 'Menganalisis hard drive untuk bukti kejahatan.'},
                    {'title': 'Incident Response Lifecycle', 'description': 'Langkah-langkah dalam menangani insiden keamanan.'},
                    {'title': 'Threat Intelligence', 'description': 'Mengumpulkan informasi tentang ancaman dan penyerang.'},
                    {'title': 'Membuat Laporan Forensik', 'description': 'Mendokumentasikan temuan secara profesional.'}
                ], 'projects': [{'title': 'Investigasi Skenario Insiden dari Image Disk', 'difficulty': 'Expert', 'tech_stack': 'Autopsy, Volatility'}]
            },
            {
                'title': 'Keamanan Cloud', 'level': 'expert', 'lessons': [
                    {'title': 'Model Layanan Cloud (IaaS, PaaS, SaaS)', 'description': 'Memahami berbagai jenis layanan cloud.'},
                    {'title': 'Model Tanggung Jawab Bersama (Shared Responsibility Model)', 'description': 'Siapa yang bertanggung jawab atas keamanan di cloud.'},
                    {'title': 'Keamanan AWS: IAM, VPC, Security Groups', 'description': 'Mengamankan infrastruktur di Amazon Web Services.'},
                    {'title': 'Keamanan Azure: Azure AD, NSGs', 'description': 'Mengamankan infrastruktur di Microsoft Azure.'},
                    {'title': 'Keamanan GCP: Cloud IAM, VPC', 'description': 'Mengamankan infrastruktur di Google Cloud Platform.'},
                    {'title': 'Container Security di Cloud (Kubernetes Security)', 'description': 'Mengamankan aplikasi yang di-containerize.'}
                ], 'projects': [{'title': 'Audit Keamanan Konfigurasi Bucket S3', 'difficulty': 'Advanced', 'tech_stack': 'AWS CLI'}]
            },
            {
                'title': 'Scripting & Otomatisasi Keamanan', 'level': 'expert', 'lessons': [
                    {'title': 'Python untuk Keamanan Siber', 'description': 'Mengotomatiskan tugas-tugas keamanan dengan Python.'},
                    {'title': 'Interaksi dengan API untuk Keamanan', 'description': 'Mengambil data dari platform threat intelligence.'},
                    {'title': 'Menulis Skrip Nmap dengan Python', 'description': 'Mengotomatiskan pemindaian jaringan.'},
                    {'title': 'Security Orchestration, Automation, and Response (SOAR)', 'description': 'Mengotomatiskan respons terhadap insiden.'},
                    {'title': 'Pengenalan SIEM (Security Information and Event Management)', 'description': 'Mengagregasi dan menganalisis log keamanan.'},
                    {'title': 'Menulis Aturan Deteksi (Snort, YARA)', 'description': 'Membuat aturan kustom untuk mendeteksi ancaman.'}
                ], 'projects': [{'title': 'Membuat Port Scanner Sederhana dengan Python', 'difficulty': 'Advanced', 'tech_stack': 'Python'}]
            },
            {
                'title': 'Persiapan Karier Keamanan Siber', 'level': 'expert', 'lessons': [
                    {'title': 'Sertifikasi Keamanan (CompTIA Security+, CEH, OSCP)', 'description': 'Sertifikasi yang diakui industri.'},
                    {'title': 'Peran-peran dalam Keamanan Siber', 'description': 'Blue Team, Red Team, Purple Team.'},
                    {'title': 'Membangun Lab Keamanan Pribadi', 'description': 'Tempat untuk berlatih secara legal dan aman.'},
                    {'title': 'Wawancara Teknis Keamanan Siber', 'description': 'Pertanyaan yang sering muncul.'},
                    {'title': 'Hukum & Etika dalam Keamanan Siber', 'description': 'Batasan legal dan etis seorang profesional keamanan.'},
                    {'title': 'Menulis Laporan Penetration Testing', 'description': 'Mengkomunikasikan temuan kepada klien.'}
                ], 'projects': [{'title': 'Simulasi Wawancara Keamanan Siber', 'difficulty': 'Expert', 'tech_stack': 'Komunikasi, Problem Solving'}]
            }
        ],
        'network-engineer': [
            # 10 Modul Lengkap untuk Network Engineer
            {
                'title': 'Fondasi Jaringan Komputer', 'level': 'beginner', 'lessons': [
                    {'title': 'Pengenalan Jaringan Komputer', 'description': 'Apa itu jaringan dan mengapa itu penting.'},
                    {'title': 'Model Referensi OSI & TCP/IP', 'description': 'Memahami lapisan-lapisan komunikasi jaringan.'},
                    {'title': 'Perangkat Keras Jaringan (Router, Switch, Hub)', 'description': 'Fungsi dari setiap perangkat.'},
                    {'title': 'Topologi Jaringan (Bus, Star, Ring, Mesh)', 'description': 'Cara jaringan disusun secara fisik.'},
                    {'title': 'Media Transmisi (Kabel Tembaga, Fiber Optik, Nirkabel)', 'description': 'Cara sinyal dikirimkan.'},
                    {'title': 'Pengalamatan IP (IPv4 & Subnetting)', 'description': 'Memberi alamat unik ke setiap perangkat.'}
                ], 'projects': [{'title': 'Desain Jaringan Sederhana untuk Kantor Kecil', 'difficulty': 'Beginner', 'tech_stack': 'Packet Tracer'}]
            },
            {
                'title': 'Switching & LAN Technologies', 'level': 'beginner', 'lessons': [
                    {'title': 'Cara Kerja Switch Layer 2', 'description': 'Forwarding frame berdasarkan alamat MAC.'},
                    {'title': 'Virtual LANs (VLANs)', 'description': 'Segmentasi jaringan logis.'},
                    {'title': 'Trunking (802.1Q)', 'description': 'Membawa traffic beberapa VLAN antar switch.'},
                    {'title': 'Spanning Tree Protocol (STP)', 'description': 'Mencegah loop pada jaringan switched.'},
                    {'title': 'EtherChannel', 'description': 'Menggabungkan beberapa link fisik menjadi satu link logis.'},
                    {'title': 'Konfigurasi Dasar Switch Cisco', 'description': 'Perintah-perintah dasar IOS.'}
                ], 'projects': [{'title': 'Konfigurasi VLAN & Trunking di Packet Tracer', 'difficulty': 'Beginner', 'tech_stack': 'Packet Tracer, Cisco IOS'}]
            },
            {
                'title': 'Routing & WAN Technologies', 'level': 'intermediate', 'lessons': [
                    {'title': 'Cara Kerja Router & Routing Table', 'description': 'Membuat keputusan forwarding berdasarkan alamat IP.'},
                    {'title': 'Static Routing', 'description': 'Konfigurasi rute secara manual.'},
                    {'title': 'Dynamic Routing Protocols (RIP, EIGRP, OSPF)', 'description': 'Router berbagi informasi rute secara otomatis.'},
                    {'title': 'Access Control Lists (ACLs)', 'description': 'Memfilter traffic jaringan.'},
                    {'title': 'Network Address Translation (NAT)', 'description': 'Menerjemahkan alamat IP privat ke publik.'},
                    {'title': 'Pengenalan Wide Area Networks (WAN)', 'description': 'Menghubungkan jaringan yang terpisah secara geografis.'}
                ], 'projects': [
                    {'title': 'Konfigurasi Static & Dynamic Routing (OSPF) di Packet Tracer', 'difficulty': 'Intermediate', 'tech_stack': 'Packet Tracer, Cisco IOS'},
                    {'title': 'Implementasi ACL & NAT', 'difficulty': 'Intermediate', 'tech_stack': 'Packet Tracer, Cisco IOS'}
                ]
            },
            {
                'title': 'Layanan Jaringan', 'level': 'intermediate', 'lessons': [
                    {'title': 'Domain Name System (DNS)', 'description': 'Menerjemahkan nama domain menjadi alamat IP.'},
                    {'title': 'Dynamic Host Configuration Protocol (DHCP)', 'description': 'Memberikan alamat IP ke perangkat secara otomatis.'},
                    {'title': 'File Transfer Protocol (FTP) & Trivial FTP (TFTP)', 'description': 'Mentransfer file melalui jaringan.'},
                    {'title': 'Simple Network Management Protocol (SNMP)', 'description': 'Memantau perangkat jaringan.'},
                    {'title': 'Network Time Protocol (NTP)', 'description': 'Sinkronisasi waktu di seluruh jaringan.'},
                    {'title': 'Syslog', 'description': 'Mengumpulkan log dari perangkat jaringan.'}
                ], 'projects': [{'title': 'Konfigurasi DHCP & DNS Server di Packet Tracer', 'difficulty': 'Intermediate', 'tech_stack': 'Packet Tracer'}]
            },
            {
                'title': 'Jaringan Nirkabel (Wireless)', 'level': 'advanced', 'lessons': [
                    {'title': 'Standar Wi-Fi (802.11a/b/g/n/ac/ax)', 'description': 'Evolusi teknologi nirkabel.'},
                    {'title': 'Komponen Jaringan Nirkabel (AP, WLC)', 'description': 'Access Point dan Wireless LAN Controller.'},
                    {'title': 'Keamanan Nirkabel (WEP, WPA, WPA2, WPA3)', 'description': 'Mengamankan jaringan Wi-Fi.'},
                    {'title': 'Site Survey Nirkabel', 'description': 'Merencanakan penempatan Access Point.'},
                    {'title': 'Troubleshooting Masalah Nirkabel', 'description': 'Mendiagnosis masalah koneksi Wi-Fi.'},
                    {'title': 'Pengenalan Jaringan Seluler (4G/5G)', 'description': 'Bagaimana perangkat mobile terhubung ke internet.'}
                ], 'projects': [{'title': 'Konfigurasi Jaringan Nirkabel Aman dengan WPA2-Enterprise', 'difficulty': 'Advanced', 'tech_stack': 'Packet Tracer'}]
            },
            {
                'title': 'Keamanan Jaringan', 'level': 'advanced', 'lessons': [
                    {'title': 'Ancaman Keamanan Jaringan Umum', 'description': 'Denial-of-Service, Man-in-the-Middle, dll.'},
                    {'title': 'Keamanan Switch (Port Security, DHCP Snooping)', 'description': 'Mengamankan lapisan akses jaringan.'},
                    {'title': 'Virtual Private Networks (VPN) Lanjutan (IPSec & SSL)', 'description': 'Membangun terowongan aman.'},
                    {'title': 'Next-Generation Firewalls (NGFW) & Unified Threat Management (UTM)', 'description': 'Firewall modern dengan fitur canggih.'},
                    {'title': 'Pengenalan SIEM (Security Information and Event Management)', 'description': 'Mengagregasi dan menganalisis log keamanan.'},
                    {'title': 'Network Access Control (NAC)', 'description': 'Mengontrol siapa dan apa yang bisa terhubung ke jaringan.'}
                ], 'projects': [{'title': 'Implementasi VPN Site-to-Site dengan IPSec', 'difficulty': 'Advanced', 'tech_stack': 'Packet Tracer'}]
            },
            {
                'title': 'Jaringan Skala Besar & ISP', 'level': 'expert', 'lessons': [
                    {'title': 'Border Gateway Protocol (BGP)', 'description': 'Protokol routing yang menjalankan internet.'},
                    {'title': 'Multiprotocol Label Switching (MPLS)', 'description': 'Teknologi WAN yang efisien.'},
                    {'title': 'Quality of Service (QoS)', 'description': 'Memprioritaskan traffic penting.'},
                    {'title': 'Desain Jaringan Hierarkis (Core, Distribution, Access)', 'description': 'Model desain jaringan yang skalabel.'},
                    {'title': 'IPv6', 'description': 'Generasi baru pengalamatan IP.'},
                    {'title': 'Software-Defined Networking (SDN)', 'description': 'Memisahkan control plane dan data plane.'}
                ], 'projects': [{'title': 'Konfigurasi BGP Dasar Antar Autonomous Systems', 'difficulty': 'Expert', 'tech_stack': 'GNS3/EVE-NG'}]
            },
            {
                'title': 'Jaringan Cloud', 'level': 'expert', 'lessons': [
                    {'title': 'Pengenalan Jaringan di Cloud (AWS, Azure, GCP)', 'description': 'Bagaimana jaringan bekerja di lingkungan virtual.'},
                    {'title': 'Amazon VPC & Subnets', 'description': 'Membangun jaringan pribadi di AWS.'},
                    {'title': 'Azure VNet & Subnets', 'description': 'Jaringan virtual di Microsoft Azure.'},
                    {'title': 'AWS Security Groups & Network ACLs', 'description': 'Firewall di cloud AWS.'},
                    {'title': 'Menghubungkan Jaringan On-premise ke Cloud (VPN & Direct Connect)', 'description': 'Membangun jaringan hybrid.'},
                    {'title': 'Load Balancing di Cloud', 'description': 'Mendistribusikan traffic ke beberapa server di cloud.'}
                ], 'projects': [{'title': 'Desain & Implementasi VPC dengan Subnet Publik & Privat di AWS', 'difficulty': 'Expert', 'tech_stack': 'AWS Console/CLI'}]
            },
            {
                'title': 'Otomatisasi Jaringan', 'level': 'expert', 'lessons': [
                    {'title': 'Mengapa Otomatisasi Jaringan Penting?', 'description': 'Manfaat dari mengotomatiskan tugas-tugas jaringan.'},
                    {'title': 'Dasar-dasar Python untuk Otomatisasi Jaringan', 'description': 'Sintaks Python yang paling relevan.'},
                    {'title': 'Berinteraksi dengan Perangkat Jaringan via SSH (Paramiko/Netmiko)', 'description': 'Menjalankan perintah pada router/switch dari skrip Python.'},
                    {'title': 'Parsing Data Konfigurasi & Operasional', 'description': 'Mengambil dan mengolah output dari perangkat.'},
                    {'title': 'Pengenalan Ansible untuk Otomatisasi Jaringan', 'description': 'Otomatisasi berbasis playbook yang sederhana.'},
                    {'title': 'REST APIs & Postman untuk Perangkat Jaringan Modern', 'description': 'Berinteraksi dengan perangkat yang mendukung API.'}
                ], 'projects': [
                    {'title': 'Skrip Python untuk Backup Konfigurasi Perangkat Jaringan', 'difficulty': 'Expert', 'tech_stack': 'Python, Netmiko'},
                    {'title': 'Ansible Playbook untuk Konfigurasi VLAN di Banyak Switch', 'difficulty': 'Expert', 'tech_stack': 'Ansible, YAML'}
                ]
            },
            {
                'title': 'Persiapan Karier Insinyur Jaringan', 'level': 'expert', 'lessons': [
                    {'title': 'Sertifikasi Jaringan (CCNA, JNCIA, CompTIA Network+)', 'description': 'Sertifikasi yang diakui industri.'},
                    {'title': 'Troubleshooting Jaringan: Metodologi Top-Down & Bottom-Up', 'description': 'Pendekatan terstruktur untuk memecahkan masalah.'},
                    {'title': 'Menggunakan Alat Diagnostik Jaringan (ping, traceroute, nslookup)', 'description': 'Alat-alat dasar untuk troubleshooting.'},
                    {'title': 'Dokumentasi Jaringan', 'description': 'Pentingnya membuat dokumentasi yang baik.'},
                    {'title': 'Wawancara Teknis Insinyur Jaringan', 'description': 'Pertanyaan yang sering muncul.'},
                    {'title': 'Tren Masa Depan: 5G, IoT, & Edge Computing', 'description': 'Teknologi yang akan membentuk masa depan jaringan.'}
                ], 'projects': [{'title': 'Simulasi Skenario Troubleshooting Jaringan', 'difficulty': 'Expert', 'tech_stack': 'Problem Solving, Packet Tracer'}]
            }
        ]
    }
    
    # 4. Fungsi untuk mengisi data proyek dengan deskripsi default jika kosong
    def fill_project_defaults(project_data):
        project_data.setdefault('description', f"Proyek tantangan untuk mengaplikasikan skill {project_data.get('tech_stack', '')}.")
        project_data.setdefault('project_goals', 'Menerapkan konsep yang telah dipelajari dalam sebuah proyek nyata.')
        project_data.setdefault('evaluation_criteria', 'Fungsionalitas, kebersihan kode, dan penerapan konsep yang benar.')
        project_data.setdefault('resources', 'Dokumentasi resmi dan materi dari modul terkait.')
        return project_data

    # 5. Perulangan untuk membuat semua data
    modules_map = {}
    for career_path, modules in career_data.items():
        print(f"--- Menambahkan data untuk: {career_path.replace('-', ' ').title()} ---")
        for i, module_data in enumerate(modules, 1):
            new_module = Module(
                title=module_data['title'], 
                order=i, 
                career_path=career_path, 
                roadmap_id=roadmap_umum.id,
                level=module_data.get('level', 'beginner')
            )
            db.session.add(new_module)
            db.session.flush()
            modules_map[new_module.title] = new_module.id

            for j, lesson_data in enumerate(module_data['lessons'], 1):
                new_lesson = Lesson(
                    title=lesson_data['title'],
                    order=j,
                    module_id=new_module.id,
                    description=lesson_data.get('description', 'Deskripsi akan segera ditambahkan.'),
                    estimated_time=lesson_data.get('estimated_time', 30)
                )
                db.session.add(new_lesson)
            
            for project_data in module_data.get('projects', []):
                full_project_data = fill_project_defaults(project_data)
                new_project = Project(
                    title=full_project_data['title'], 
                    description=full_project_data.get('description'), 
                    difficulty=full_project_data['difficulty'],
                    module_id=new_module.id, 
                    project_goals=full_project_data.get('project_goals'), 
                    tech_stack=full_project_data['tech_stack'],
                    evaluation_criteria=full_project_data.get('evaluation_criteria'), 
                    resources=full_project_data.get('resources')
                )
                db.session.add(new_project)
    
    db.session.commit()
    
    # 5. Menambahkan proyek tantangan yang diperbarui
    print("--- Menambahkan Proyek Tantangan ---")
    challenges = [
        Project(title='Real-time Chat Application', description='Bangun aplikasi chat real-time menggunakan WebSocket. Pengguna bisa masuk ke dalam room dan mengirim pesan yang akan diterima oleh semua pengguna di room tersebut secara instan.', difficulty='Advanced', is_challenge=True, module_id=modules_map.get('Arsitektur Lanjutan & Pola Desain'), tech_stack="Node.js, Express.js, Socket.io, React.js"),
        Project(title='Platform E-learning Dashboard', description='Desain dan implementasikan dashboard interaktif untuk platform e-learning. Visualisasikan metrik seperti progres siswa, tingkat kelulusan kursus, dan waktu belajar rata-rata.', difficulty='Advanced', is_challenge=True, module_id=modules_map.get('Visualisasi & Storytelling Data'), tech_stack="Python, Plotly/Dash, Pandas"),
        Project(title='Music Player Web App', description='Buat aplikasi pemutar musik di web dengan React yang mengambil data dari API publik (misal: Spotify API). Fitur termasuk play, pause, next, previous, dan playlist.', difficulty='Intermediate', is_challenge=True, module_id=modules_map.get('Framework Modern: React.js'), tech_stack="React.js, Fetch API/Axios, Redux/Zustand"),
        Project(title='CI/CD Pipeline for Microservices', description='Buat CI/CD pipeline yang dapat mengelola proses build, test, dan deploy untuk dua microservice yang saling bergantung. Pipeline harus dapat men-deploy service secara independen.', difficulty='Expert', is_challenge=True, module_id=modules_map.get('CI/CD Pipelines & Monitoring'), tech_stack="GitHub Actions, Docker, Kubernetes, Helm"),
        Project(title='Recommender System API', description='Bangun dan deploy sebuah API yang dapat memberikan rekomendasi produk/film berdasarkan input dari user. Gunakan teknik seperti collaborative filtering.', difficulty='Expert', is_challenge=True, module_id=modules_map.get('MLOps: Deploy & Maintenance Model'), tech_stack="Python, FastAPI, Scikit-learn/Surprise, Docker")
    ]
    db.session.add_all(challenges)
    
    print("=" * 60)
    print("✅ SEMUA DATA KURIKULUM LENGKAP BERHASIL DITAMBAHKAN! ✅")
    print("=" * 60)

