# seed.py

from app import create_app, db
from app.models import Module, Lesson, Project, Roadmap, User

# Buat objek app dari fungsi create_app
app = create_app()

# Pastikan semua operasi database berada di dalam konteks aplikasi.
with app.app_context():
    # Hapus data lama (opsional, untuk memastikan database bersih)
    Project.query.delete()
    Lesson.query.delete()
    Module.query.delete()
    Roadmap.query.delete()
    db.session.commit()
    print("Membersihkan data lama...")

    # --- Buat satu Roadmap umum untuk semua modul ---
    roadmap_umum = Roadmap(title='Roadmap Belajar Farsight', level='General')
    db.session.add(roadmap_umum)
    db.session.flush()
    print("Roadmap umum berhasil dibuat...")

    # ====================================================================
    # ✅ INI ADALAH PERUBAHAN UTAMA: STRUKTUR DATA YANG LEBIH EFISIEN
    # ====================================================================
    career_data = {
        'frontend': [
            {
                'title': 'Dasar-Dasar Frontend',
                'lessons': [
                    {'title': 'HTML5 Semantic Elements'},
                    {'title': 'CSS Flexbox & Grid'},
                    {'title': 'Dasar-Dasar JavaScript (ES6)'},
                ],
                'project': {
                    'title': 'Personal Portfolio Website',
                    'description': 'Buat website portofolio statis menggunakan HTML & CSS.',
                    'difficulty': 'Beginner',
                    'project_goals': 'Membuat halaman portofolio yang dapat menampilkan diri Anda dan karya-karya Anda secara profesional. Mempraktikkan layout dengan CSS Flexbox/Grid.',
                    'tech_stack': 'HTML5, CSS3',
                    'evaluation_criteria': 'Desain responsif, penggunaan elemen semantik yang benar, struktur folder yang rapi.',
                    'resources': 'Panduan Flexbox dari CSS-Tricks, referensi HTML5 dari MDN.'
                }
            },
            {
                'title': 'Framework Modern: React.js',
                'lessons': [
                    {'title': 'Component & Props'},
                    {'title': 'State & Lifecycle'},
                    {'title': 'React Hooks (useState, useEffect)'},
                ],
                'project': {
                    'title': 'Aplikasi To-Do List dengan React',
                    'description': 'Buat aplikasi CRUD sederhana untuk mengelola daftar tugas.',
                    'difficulty': 'Intermediate',
                    'project_goals': 'Memahami cara kerja state dan props di React. Mampu membuat, membaca, memperbarui, dan menghapus data (CRUD).',
                    'tech_stack': 'React.js, JavaScript (ES6), CSS',
                    'evaluation_criteria': 'Fungsionalitas CRUD berjalan sempurna, penggunaan Hooks yang tepat, komponen terstruktur dengan baik.',
                    'resources': 'Dokumentasi resmi React, tutorial To-Do App dari FreeCodeCamp.'
                }
            },
            {
                'title': 'Tools & Ekosistem Frontend',
                'lessons': [
                    {'title': 'Manajemen State dengan Redux Toolkit'},
                    {'title': 'Styling dengan Tailwind CSS'},
                    {'title': 'Deploy Aplikasi ke Vercel/Netlify'},
                ],
                'project': {
                    'title': 'Clone Tampilan Tokopedia',
                    'description': 'Buat ulang halaman utama Tokopedia (hanya tampilan) dengan React & Tailwind.',
                    'difficulty': 'Advanced',
                    'project_goals': 'Mampu mengimplementasikan desain kompleks menjadi kode. Mempraktikkan layout menggunakan Tailwind CSS.',
                    'tech_stack': 'React.js, Tailwind CSS',
                    'evaluation_criteria': 'Akurasi desain sesuai referensi, penggunaan kelas utilitas Tailwind yang efisien.',
                    'resources': 'Desain halaman utama Tokopedia, dokumentasi resmi Tailwind CSS.'
                }
            }
        ],
        'backend': [
            {
                'title': 'Dasar-Dasar Backend & Database',
                'lessons': [
                    {'title': 'Pengenalan HTTP & REST API'},
                    {'title': 'Dasar SQL & Relational Database'},
                    {'title': 'Setup Server dengan Node.js & Express'},
                ],
                'project': {
                    'title': 'API Sederhana untuk Blog',
                    'description': 'Buat endpoint CRUD untuk artikel blog.',
                    'difficulty': 'Beginner',
                    'project_goals': 'Membuat API dengan endpoint dasar (GET, POST, PUT, DELETE). Memahami konsep rute dan controller.',
                    'tech_stack': 'Node.js, Express.js, SQLite/PostgreSQL',
                    'evaluation_criteria': 'Endpoint berfungsi dengan benar, respons HTTP sesuai, struktur kode terorganisir.',
                    'resources': 'Dokumentasi Express.js, panduan REST API.'
                }
            },
            {
                'title': 'Autentikasi & Database Lanjutan',
                'lessons': [
                    {'title': 'Autentikasi dengan JWT (JSON Web Token)'},
                    {'title': 'Menggunakan ORM (Sequelize/Prisma)'},
                    {'title': 'Password Hashing dengan Bcrypt'},
                ],
                'project': {
                    'title': 'API dengan Sistem Login & Register',
                    'description': 'Tambahkan fitur autentikasi pada API blog.',
                    'difficulty': 'Intermediate',
                    'project_goals': 'Mengimplementasikan sistem login dan register. Memahami cara kerja JWT dan otorisasi.',
                    'tech_stack': 'Node.js, Express.js, JWT, Bcrypt',
                    'evaluation_criteria': 'Autentikasi berfungsi dengan aman, password di-hash, penanganan error yang baik.',
                    'resources': 'Dokumentasi JWT, tutorial autentikasi dengan Bcrypt.'
                }
            },
            {
                'title': 'Deployment & Arsitektur Backend',
                'lessons': [
                    {'title': 'Dasar-Dasar Docker'},
                    {'title': 'Konsep Microservices'},
                    {'title': 'Deploy API ke Cloud (Render/Heroku)'},
                ],
                'project': {
                    'title': 'API E-commerce (Product & Order)',
                    'description': 'Rancang API untuk mengelola produk dan pesanan.',
                    'difficulty': 'Advanced',
                    'project_goals': 'Merancang skema database untuk e-commerce. Membangun relasi antar tabel.',
                    'tech_stack': 'Node.js, Express.js, PostgreSQL/MongoDB, Sequelize/Mongoose',
                    'evaluation_criteria': 'Desain database normalisasi, endpoint relasional berfungsi, kode modular.',
                    'resources': 'Panduan desain skema e-commerce, tutorial API e-commerce.'
                }
            }
        ],
        'data-analyst': [
            {
                'title': 'Fondasi Analisis Data',
                'lessons': [
                    {'title': 'Dasar-Dasar Statistik Deskriptif'},
                    {'title': 'Query SQL Lanjutan (JOIN, Subquery)'},
                    {'title': 'Pengenalan Python dengan Pandas'},
                ],
                'project': {
                    'title': 'Analisis Data Penjualan Retail',
                    'description': 'Analisis dataset penjualan untuk menemukan tren produk.',
                    'difficulty': 'Beginner',
                    'project_goals': 'Mengidentifikasi tren data. Menghitung metrik dasar seperti rata-rata dan total penjualan. Membuat visualisasi sederhana.',
                    'tech_stack': 'Python, Pandas, Matplotlib/Seaborn',
                    'evaluation_criteria': 'Visualisasi yang jelas, insight yang logis, dan kode yang bersih.',
                    'resources': 'Tutorial Pandas, dataset penjualan dari Kaggle.'
                }
            },
            {
                'title': 'Visualisasi & Storytelling Data',
                'lessons': [
                    {'title': 'Prinsip Desain Visualisasi Data'},
                    {'title': 'Membuat Dashboard dengan Tableau/Looker'},
                    {'title': 'Storytelling with Data'},
                ],
                'project': {
                    'title': 'Dashboard Interaktif Covid-19',
                    'description': 'Buat dashboard untuk memvisualisasikan data kasus Covid-19.',
                    'difficulty': 'Intermediate',
                    'project_goals': 'Membuat dashboard yang interaktif. Menggunakan berbagai jenis visualisasi untuk menceritakan sebuah \'kisah\' dari data.',
                    'tech_stack': 'Tableau/Looker Studio',
                    'evaluation_criteria': 'Desain dashboard yang intuitif, alur cerita yang jelas, dan penggunaan filter yang efektif.',
                    'resources': 'Dataset Covid-19 dari Our World in Data, galeri dashboard Tableau.'
                }
            },
            {
                'title': 'Business Acumen & Tools',
                'lessons': [
                    {'title': 'A/B Testing untuk Produk Digital'},
                    {'title': 'Analisis Kohort & Retensi Pengguna'},
                    {'title': 'Menggunakan Google Analytics'},
                ],
                'project': {
                    'title': 'Analisis Sentimen Review Produk',
                    'description': 'Analisis ulasan produk dari marketplace menggunakan Python.',
                    'difficulty': 'Advanced',
                    'project_goals': 'Menerapkan analisis sentimen sederhana. Mengidentifikasi kata kunci positif dan negatif dalam ulasan. Menghitung skor sentimen.',
                    'tech_stack': 'Python, NLTK/TextBlob, Pandas',
                    'evaluation_criteria': 'Akurasi sentimen, dokumentasi proses analisis, dan hasil analisis yang jelas.',
                    'resources': 'Tutorial analisis sentimen dengan Python, dataset ulasan produk.'
                }
            }
        ]
    }

    # ====================================================================
    # ✅ PERULANGAN UNTUK MEMBUAT DATA SECARA OTOMATIS
    # ====================================================================
    for career_path, modules in career_data.items():
        print(f"Menambahkan data untuk jalur karier: {career_path.title()}")
        order_module = 1
        for module_data in modules:
            new_module = Module(
                title=module_data['title'],
                order=order_module,
                career_path=career_path,
                roadmap_id=roadmap_umum.id
            )
            db.session.add(new_module)
            db.session.flush() # Ambil ID modul
            
            # Buat lesson
            order_lesson = 1
            for lesson_data in module_data['lessons']:
                new_lesson = Lesson(
                    title=lesson_data['title'],
                    order=order_lesson,
                    module_id=new_module.id
                )
                db.session.add(new_lesson)
                order_lesson += 1
            
            # Buat project
            project_data = module_data['project']
            new_project = Project(
                title=project_data['title'],
                description=project_data['description'],
                difficulty=project_data['difficulty'],
                module_id=new_module.id,
                project_goals=project_data['project_goals'],
                tech_stack=project_data['tech_stack'],
                evaluation_criteria=project_data['evaluation_criteria'],
                resources=project_data['resources']
            )
            db.session.add(new_project)
            order_module += 1
    
    # Menambahkan data proyek tantangan secara terpisah
    print("Menambahkan data Proyek Tantangan...")
    challenge_1 = Project(
        title='Real-time Chat Application',
        description='Bangun aplikasi chat real-time menggunakan WebSocket (Socket.io).',
        difficulty='Advanced',
        is_challenge=True,
        module_id=Module.query.filter_by(title='Dasar-Dasar Backend & Database').first().id,
        project_goals="Membangun koneksi real-time. Mengelola multiple connections. Memahami konsep event-driven architecture.",
        tech_stack="Node.js, Express.js, Socket.io",
        evaluation_criteria="Fungsi chat real-time, penanganan koneksi, penanganan error.",
        resources="Dokumentasi Socket.io, tutorial chat app real-time."
    )
    challenge_2 = Project(
        title='Platform E-learning Dashboard',
        description='Desain dan implementasikan dashboard interaktif untuk platform e-learning.',
        difficulty='Advanced',
        is_challenge=True,
        module_id=Module.query.filter_by(title='Fondasi Analisis Data').first().id,
        project_goals="Menerjemahkan kebutuhan bisnis menjadi visualisasi data. Membuat dashboard dengan metrik kunci seperti progres pengguna dan engagement.",
        tech_stack="Python, Plotly/Dash",
        evaluation_criteria="Dashboard interaktif, insight yang relevan, kode yang modular.",
        resources="Contoh dashboard e-learning, dokumentasi Plotly/Dash."
    )
    challenge_3 = Project(
        title='Music Player Web App',
        description='Buat aplikasi pemutar musik di web dengan React yang mengambil data dari API publik (misal: Spotify API).',
        difficulty='Intermediate',
        is_challenge=True,
        module_id=Module.query.filter_by(title='Dasar-Dasar Frontend').first().id,
        project_goals="Mengintegrasikan API eksternal. Mengelola state aplikasi yang kompleks (misal: status putar, trek saat ini).",
        tech_stack="React.js, JavaScript, Fetch API/Axios",
        evaluation_criteria="Fungsionalitas dasar pemutar musik (putar, jeda, berikutnya), integrasi API yang lancar, tampilan yang responsif.",
        resources="Dokumentasi Spotify API, tutorial fetch data dengan React."
    )
    db.session.add_all([challenge_1, challenge_2, challenge_3])
    
    # Commit semua perubahan ke database
    db.session.commit()
    print("======================================================")
    print("✅ SEMUA DATA BERHASIL DITAMBAHKAN KE DATABASE! ✅")
    print("======================================================")