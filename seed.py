import json
from app import create_app, db
from app.models import Module, Lesson, Project, Roadmap, User

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
    db.session.flush() # flush() diperlukan untuk mendapatkan ID sebelum commit
    print("Roadmap umum berhasil dibuat.")

    # 3. Definisikan struktur data kurikulum yang kaya dan diperbarui
    career_data = {
        'frontend': [
            {
                'title': 'Dasar-Dasar Frontend',
                'lessons': [
                    {'title': 'Pengenalan Cara Kerja Web & Version Control', 'lesson_type': 'article', 'url': 'https://developer.mozilla.org/en-US/docs/Learn/Getting_started_with_the_web/How_the_Web_works', 'estimated_time': 45},
                    {'title': 'HTML5 Semantic Elements & Forms', 'lesson_type': 'article', 'url': 'https://www.freecodecamp.org/news/semantic-html5-elements/', 'estimated_time': 60},
                    {'title': 'CSS Box Model, Flexbox, & Grid', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=R_mokrBfjI8', 'estimated_time': 90},
                    {'title': 'Dasar JavaScript (ES6+), Tipe Data, & DOM Manipulation', 'lesson_type': 'article', 'url': 'https://javascript.info/', 'estimated_time': 120},
                    {'title': 'Asynchronous JavaScript (Callbacks, Promises, Async/Await)', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=V_Kr9OSfDeU', 'estimated_time': 60},
                ],
                'project': {
                    'title': 'Personal Portfolio Website', 'description': 'Buat website portofolio statis yang sepenuhnya responsif dan interaktif menggunakan HTML, CSS, dan JavaScript murni. Proyek ini menguji pemahaman fundamental Anda dalam membangun struktur, layout, dan fungsionalitas dasar web.', 'difficulty': 'Beginner',
                    'project_goals': 'Menerapkan layout responsif dengan Flexbox/Grid. Menggunakan JavaScript untuk interaktivitas (misal: dark mode toggle, smooth scrolling). Menampilkan profil dan proyek secara profesional.', 'tech_stack': 'HTML5, CSS3, JavaScript (ES6+)',
                    'evaluation_criteria': 'Desain responsif di berbagai perangkat, penggunaan elemen HTML semantik yang benar, kode JavaScript yang bersih dan efisien, dan fungsionalitas interaktif berjalan tanpa bug.', 'resources': 'MDN Web Docs, CSS-Tricks, JavaScript.info.'
                }
            },
            {
                'title': 'Framework Modern: React.js',
                'lessons': [
                    {'title': 'Thinking in React: Component, Props, & JSX', 'lesson_type': 'article', 'url': 'https://react.dev/learn/thinking-in-react', 'estimated_time': 60},
                    {'title': 'State Management: State, Lifecycle, & Hooks (useState, useEffect)', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=O6P86uwfdR0', 'estimated_time': 90},
                    {'title': 'Handling Events & Conditional Rendering', 'lesson_type': 'article', 'url': 'https://react.dev/learn/responding-to-events', 'estimated_time': 45},
                    {'title': 'Client-Side Routing dengan React Router', 'lesson_type': 'article', 'url': 'https://reactrouter.com/en/main/start/tutorial', 'estimated_time': 60},
                    {'title': 'Interaksi dengan API (Fetch/Axios)', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=66afc2-u_ac', 'estimated_time': 60},
                ],
                'project': {
                    'title': 'Aplikasi Pencarian Film', 'description': 'Buat aplikasi web yang memungkinkan pengguna mencari film menggunakan API publik (misal: The Movie Database API). Aplikasi harus menampilkan daftar film, detail film, dan memiliki fitur pencarian.', 'difficulty': 'Intermediate',
                    'project_goals': 'Memahami arsitektur berbasis komponen. Mengelola state aplikasi yang kompleks (data, loading, error). Melakukan operasi CRUD sederhana (Create/Read).', 'tech_stack': 'React.js, JavaScript (ES6+), CSS, Fetch/Axios API',
                    'evaluation_criteria': 'Fungsionalitas pencarian dan penampilan data berjalan sempurna, penggunaan Hooks yang tepat, komponen terstruktur dan dapat digunakan kembali (reusable).', 'resources': 'Dokumentasi resmi React, The Movie Database (TMDB) API.'
                }
            },
            {
                'title': 'Manajemen State & Styling Lanjutan',
                'lessons': [
                    {'title': 'Global State dengan Redux Toolkit', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=bbkBuqC1rU4', 'estimated_time': 90},
                    {'title': 'Server State Management dengan React Query/TanStack Query', 'lesson_type': 'article', 'url': 'https://tanstack.com/query/latest/docs/react/overview', 'estimated_time': 75},
                    {'title': 'Utility-First Styling dengan Tailwind CSS', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=dFgzHOX84xQ', 'estimated_time': 75},
                    {'title': 'CSS-in-JS dengan Styled Components/Emotion', 'lesson_type': 'article', 'url': 'https://styled-components.com/docs/basics', 'estimated_time': 60},
                ],
                'project': {
                    'title': 'Keranjang Belanja E-commerce', 'description': 'Implementasikan fitur keranjang belanja untuk sebuah toko online fiktif. Pengguna harus dapat menambahkan produk, melihat isi keranjang, mengubah jumlah, dan menghapus item. State keranjang harus dikelola secara global.', 'difficulty': 'Intermediate',
                    'project_goals': 'Mengelola state global yang persisten. Mempraktikkan styling kompleks dan konsisten. Mengintegrasikan manajemen state server dan klien.', 'tech_stack': 'React.js, Redux Toolkit, React Query, Tailwind CSS/Styled Components',
                    'evaluation_criteria': 'Akurasi logika bisnis (perhitungan total, update item), state tidak hilang saat refresh (menggunakan persist), desain UI yang rapi dan konsisten.', 'resources': 'Dokumentasi Redux Toolkit, TanStack Query, FakeStoreAPI.'
                }
            },
            {
                'title': 'TypeScript, Pengujian, dan Kualitas Kode',
                'lessons': [
                    {'title': 'TypeScript untuk Aplikasi React', 'lesson_type': 'article', 'url': 'https://www.typescriptlang.org/docs/handbook/react.html', 'estimated_time': 90},
                    {'title': 'Unit Testing dengan Vitest & React Testing Library', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=D_9_L4g_dGY', 'estimated_time': 90},
                    {'title': 'End-to-End (E2E) Testing dengan Cypress/Playwright', 'lesson_type': 'article', 'url': 'https://docs.cypress.io/guides/end-to-end-testing/writing-your-first-end-to-end-test', 'estimated_time': 75},
                    {'title': 'Code Formatting & Linting (Prettier & ESLint)', 'lesson_type': 'article', 'url': 'https://www.freecodecamp.org/news/how-to-set-up-eslint-and-prettier-in-react/', 'estimated_time': 45},
                ],
                'project': {
                    'title': 'Refactor Aplikasi Film ke TypeScript & Tambah Testing', 'description': 'Migrasikan aplikasi pencarian film yang sudah dibuat ke TypeScript. Tambahkan unit test untuk komponen-komponen kritis (misal: komponen search bar, card film) dan buat satu alur E2E test untuk memvalidasi fungsionalitas pencarian.', 'difficulty': 'Advanced',
                    'project_goals': 'Memahami manfaat static typing untuk mencegah bug. Menulis tes yang andal dan mudah dipelihara. Mengotomatiskan pengecekan kualitas kode.', 'tech_stack': 'React.js, TypeScript, Vitest, React Testing Library, Cypress',
                    'evaluation_criteria': 'Kode sepenuhnya "type-safe" tanpa error, cakupan tes (test coverage) yang baik untuk logika inti, pipeline CI/CD sederhana yang menjalankan tes secara otomatis.', 'resources': 'Dokumentasi TypeScript, React Testing Library, Cypress.'
                }
            },
            {
                'title': 'Framework Lanjutan, Performa & Aksesibilitas',
                'lessons': [
                    {'title': 'Konsep SSR & SSG dengan Next.js', 'lesson_type': 'article', 'url': 'https://nextjs.org/docs/basic-features/pages', 'estimated_time': 90},
                    {'title': 'Web Performance Optimization (Lighthouse, Code Splitting)', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=0s_6K_dtr00', 'estimated_time': 75},
                    {'title': 'Aksesibilitas Web (WCAG) & ARIA Roles', 'lesson_type': 'article', 'url': 'https://developer.mozilla.org/en-US/docs/Web/Accessibility', 'estimated_time': 60},
                ],
                'project': {
                    'title': 'Website Blog Full-stack dengan Next.js', 'description': 'Buat aplikasi blog lengkap dengan halaman yang di-render di server (SSR) dan dibuat statis (SSG). Terapkan praktik terbaik performa dan pastikan website dapat diakses oleh pengguna dengan kebutuhan khusus.', 'difficulty': 'Advanced',
                    'project_goals': 'Mengimplementasikan rendering sisi server dan statis. Mengoptimalkan performa web untuk skor Lighthouse yang tinggi. Memastikan kepatuhan terhadap standar aksesibilitas.', 'tech_stack': 'Next.js, React.js, TypeScript, Tailwind CSS, Vercel',
                    'evaluation_criteria': 'Performa loading halaman yang cepat (Skor Lighthouse >90), fungsionalitas API berjalan baik, lolos audit aksesibilitas dasar (misal: navigasi keyboard, kontras warna).', 'resources': 'Dokumentasi resmi Next.js, web.dev/measure, A11Y Project.'
                }
            }
        ],
        'backend': [
            {
                'title': 'Dasar-Dasar Backend & Database',
                'lessons': [
                    {'title': 'Pengenalan HTTP, REST API, & Arsitektur Klien-Server', 'lesson_type': 'article', 'url': 'https://www.freecodecamp.org/news/rest-api-design-best-practices-build-a-rest-api/', 'estimated_time': 60},
                    {'title': 'Dasar SQL & Desain Database Relasional (PostgreSQL)', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=qw--VYLpxG4', 'estimated_time': 120},
                    {'title': 'Membangun Server dengan Node.js & Express.js', 'lesson_type': 'article', 'url': 'https://expressjs.com/en/starter/hello-world.html', 'estimated_time': 75},
                    {'title': 'Manajemen Environment & Konfigurasi (.env)', 'lesson_type': 'article', 'url': 'https://www.npmjs.com/package/dotenv', 'estimated_time': 30},
                ],
                'project': {
                    'title': 'API Sederhana untuk Blog', 'description': 'Rancang dan bangun serangkaian endpoint RESTful API untuk mengelola postingan blog (artikel). API ini harus mendukung operasi CRUD (Create, Read, Update, Delete) penuh pada data artikel yang disimpan dalam database PostgreSQL.', 'difficulty': 'Beginner',
                    'project_goals': 'Membuat API dengan endpoint yang terstruktur (GET, POST, PUT, DELETE). Merancang skema database yang efisien. Memahami alur request-response HTTP.', 'tech_stack': 'Node.js, Express.js, PostgreSQL',
                    'evaluation_criteria': 'Semua endpoint CRUD berfungsi sesuai spesifikasi, respons HTTP (status code, body) sesuai standar REST, struktur kode terorganisir (routes, controllers, models).', 'resources': 'Dokumentasi Express.js, Dokumentasi PostgreSQL.'
                }
            },
            {
                'title': 'Autentikasi, Keamanan, & ORM',
                'lessons': [
                    {'title': 'Autentikasi berbasis Token dengan JWT', 'lesson_type': 'article', 'url': 'https://jwt.io/introduction/', 'estimated_time': 60},
                    {'title': 'Password Hashing (Bcrypt) & Middleware Otorisasi', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=lY6icfhap2o', 'estimated_time': 60},
                    {'title': 'Interaksi Database dengan ORM (Prisma)', 'lesson_type': 'article', 'url': 'https://www.prisma.io/docs/getting-started/quickstart', 'estimated_time': 90},
                    {'title': 'Validasi Input & Penanganan Error', 'lesson_type': 'article', 'url': 'https://expressjs.com/en/guide/error-handling.html', 'estimated_time': 45},
                ],
                'project': {
                    'title': 'API Blog dengan Sistem Login & Register', 'description': 'Tambahkan sistem autentikasi dan otorisasi ke API Blog. Pengguna bisa mendaftar, login untuk mendapatkan token JWT, dan hanya pengguna yang terautentikasi yang dapat membuat atau memodifikasi postingan mereka sendiri.', 'difficulty': 'Intermediate',
                    'project_goals': 'Mengimplementasikan alur registrasi dan login yang aman. Melindungi endpoint dengan middleware. Mengelola relasi data (user dan post) menggunakan ORM.', 'tech_stack': 'Node.js, Express.js, JWT, Bcrypt, Prisma, PostgreSQL',
                    'evaluation_criteria': 'Alur autentikasi aman dan berfungsi, password di-hash dengan benar, endpoint terlindungi secara efektif, penanganan error untuk input tidak valid atau akses tidak sah.', 'resources': 'Dokumentasi Prisma, The JWT Handbook.'
                }
            },
            {
                'title': 'Arsitektur, Containerisasi & Deployment',
                'lessons': [
                    {'title': 'Containerisasi Aplikasi dengan Docker & Docker Compose', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=3c-iBn73dDE', 'estimated_time': 120},
                    {'title': 'Prinsip Desain API Lanjutan (Versioning, Pagination)', 'lesson_type': 'article', 'url': 'https://restfulapi.net/versioning/', 'estimated_time': 60},
                    {'title': 'Deploy Aplikasi ke Cloud (Render/Fly.io)', 'lesson_type': 'article', 'url': 'https://render.com/docs/deploy-node-express-app', 'estimated_time': 75},
                    {'title': 'Logging & Monitoring Dasar', 'lesson_type': 'article', 'url': 'https://www.loggly.com/ultimate-guide/node-js-logging-basics/', 'estimated_time': 45},
                ],
                'project': {
                    'title': 'Dockerize & Deploy API E-commerce', 'description': 'Rancang API untuk mengelola produk dan pesanan. Setelah itu, buat Dockerfile untuk men-containerize aplikasi Node.js dan Docker Compose untuk menjalankan aplikasi beserta databasenya secara lokal. Terakhir, deploy aplikasi ke platform cloud.', 'difficulty': 'Advanced',
                    'project_goals': 'Memahami siklus hidup development dari lokal ke produksi. Mampu membuat lingkungan development yang terisolasi dan konsisten. Mempraktikkan proses deployment modern.', 'tech_stack': 'Node.js, Express.js, PostgreSQL, Prisma, Docker, Render',
                    'evaluation_criteria': 'Aplikasi dapat berjalan dengan `docker-compose up`, Docker image teroptimasi (multi-stage build), proses deployment berhasil dan aplikasi dapat diakses secara publik.', 'resources': 'Dokumentasi Docker, Panduan Deployment Render.'
                }
            },
            {
                'title': 'Database Lanjutan & Paradigma Berbeda',
                'lessons': [
                    {'title': 'Pengenalan Database NoSQL (MongoDB & Mongoose)', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=ofme2o29ngU', 'estimated_time': 90},
                    {'title': 'Caching untuk Performa dengan Redis', 'lesson_type': 'article', 'url': 'https://redis.io/docs/getting-started/', 'estimated_time': 75},
                    {'title': 'Membangun API dengan GraphQL', 'lesson_type': 'article', 'url': 'https://graphql.org/learn/', 'estimated_time': 90},
                    {'title': 'Pengenalan gRPC untuk Komunikasi Antar Service', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=YwSEgYvVp6g', 'estimated_time': 75},
                ],
                'project': {
                    'title': 'API GraphQL untuk Sistem Ulasan Produk', 'description': 'Bangun sebuah server GraphQL yang mengelola data produk dan ulasan. Klien harus bisa mengambil data produk beserta ulasannya dalam satu query, dan juga bisa menambahkan ulasan baru. Gunakan MongoDB sebagai database.', 'difficulty': 'Advanced',
                    'project_goals': 'Memahami perbedaan dan keunggulan GraphQL dibandingkan REST. Merancang skema GraphQL yang efisien. Mengimplementasikan resolver untuk operasi query dan mutation.', 'tech_stack': 'Node.js, Apollo Server, GraphQL, MongoDB, Mongoose',
                    'evaluation_criteria': 'Skema GraphQL terdefinisi dengan baik, query dan mutation berfungsi sesuai ekspektasi, penanganan relasi data (produk dan ulasan) yang benar.', 'resources': 'Dokumentasi Apollo Server, Dokumentasi MongoDB.'
                }
            },
            {
                'title': 'Arsitektur Lanjutan & Pola Desain',
                'lessons': [
                    {'title': 'Arsitektur Microservices: Konsep & Pola Desain', 'lesson_type': 'article', 'url': 'https://microservices.io/patterns/microservices.html', 'estimated_time': 90},
                    {'title': 'Komunikasi Asinkron dengan Message Broker (RabbitMQ)', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=h-Kcw_s4-s4', 'estimated_time': 90},
                    {'title': 'API Gateway sebagai Pintu Masuk Tunggal', 'lesson_type': 'article', 'url': 'https://www.nginx.com/learn/api-gateway/', 'estimated_time': 60},
                    {'title': 'Testing Lanjutan (Integration & E2E Testing)', 'lesson_type': 'article', 'url': 'https://www.freecodecamp.org/news/api-integration-testing/', 'estimated_time': 75},
                ],
                'project': {
                    'title': 'Sistem Notifikasi dengan Microservices', 'description': 'Buat dua service terpisah (misal: Service User dan Service Notifikasi) yang berkomunikasi secara asinkron melalui RabbitMQ. Saat user baru mendaftar di Service User, sebuah pesan dikirim ke antrian, yang kemudian akan diproses oleh Service Notifikasi untuk mengirim email selamat datang.', 'difficulty': 'Expert',
                    'project_goals': 'Mempraktikkan dekomposisi sistem menjadi service yang lebih kecil. Mengimplementasikan komunikasi antar service yang andal dan tidak saling memblokir (non-blocking).', 'tech_stack': 'Node.js, Express.js, Docker, RabbitMQ',
                    'evaluation_criteria': 'Setiap service dapat di-deploy dan berjalan secara independen, pesan terkirim dan diterima dengan sukses melalui message broker, penggunaan Docker Compose untuk mensimulasikan lingkungan multi-service.', 'resources': 'Dokumentasi RabbitMQ, artikel tentang pola desain microservices.'
                }
            }
        ],
        'data-analyst': [
            {
                'title': 'Fondasi Analisis Data',
                'lessons': [
                    {'title': 'Statistik Deskriptif & Inferensial Dasar', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=xxpc-HPKN28', 'estimated_time': 90},
                    {'title': 'Advanced SQL (Window Functions, CTEs, Case Statements)', 'lesson_type': 'article', 'url': 'https://learnsql.com/blog/sql-window-functions-tutorial/', 'estimated_time': 90},
                    {'title': 'Manipulasi & Analisis Data dengan Python (Pandas & NumPy)', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=e_n9pCgM_Hk', 'estimated_time': 120},
                    {'title': 'Teknik Data Cleaning & Preprocessing', 'lesson_type': 'article', 'url': 'https://www.kdnuggets.com/2021/04/data-cleaning-preprocessing-guide.html', 'estimated_time': 75},
                ],
                'project': {
                    'title': 'Analisis Eksplorasi Data (EDA) Penjualan Retail', 'description': 'Lakukan analisis eksplorasi mendalam pada dataset penjualan retail. Bersihkan data, identifikasi tren penjualan, temukan produk terlaris, dan analisis perilaku pelanggan berdasarkan demografi atau lokasi.', 'difficulty': 'Beginner',
                    'project_goals': 'Menguasai teknik data cleaning. Menerapkan statistik deskriptif untuk mendapatkan insight. Membuat visualisasi data yang informatif.', 'tech_stack': 'Python, Pandas, NumPy, Matplotlib, Seaborn, Jupyter Notebook',
                    'evaluation_criteria': 'Proses cleaning data terdokumentasi dengan baik, insight yang dihasilkan logis dan didukung oleh data, visualisasi jelas dan mudah dipahami.', 'resources': 'Dataset Superstore Sales dari Kaggle.'
                }
            },
            {
                'title': 'Visualisasi & Storytelling Data',
                'lessons': [
                    {'title': 'Prinsip Desain Visualisasi yang Efektif', 'lesson_type': 'article', 'url': 'https://www.tableau.com/learn/articles/data-visualization-best-practices', 'estimated_time': 60},
                    {'title': 'Membuat Dashboard Interaktif dengan Tableau / Looker Studio', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=9yJDaLp0a_Q', 'estimated_time': 120},
                    {'title': 'Teknik Storytelling with Data', 'lesson_type': 'article', 'url': 'http://www.storytellingwithdata.com/blog', 'estimated_time': 60},
                ],
                'project': {
                    'title': 'Dashboard Analisis Pasar Properti', 'description': 'Buat dashboard interaktif menggunakan Tableau atau Looker Studio untuk menganalisis data pasar properti (misal: harga, lokasi, tipe). Dashboard harus memungkinkan pengguna memfilter dan menjelajahi data untuk menemukan pola dan tren.', 'difficulty': 'Intermediate',
                    'project_goals': 'Mengubah data mentah menjadi dashboard yang informatif dan menarik secara visual. Menerapkan praktik terbaik visualisasi untuk menceritakan sebuah "kisah" dari data.', 'tech_stack': 'Tableau / Google Looker Studio',
                    'evaluation_criteria': 'Desain dashboard yang intuitif dan mudah digunakan, penggunaan filter dan interaktivitas yang efektif, alur cerita atau narasi yang jelas dari visualisasi yang ditampilkan.', 'resources': 'Dataset Real Estate dari Kaggle, dokumentasi Tableau Public.'
                }
            },
            {
                'title': 'Statistik, Business Acumen & A/B Testing',
                'lessons': [
                    {'title': 'Probabilitas & Teorema Bayes', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=U_h_EtsR_sM', 'estimated_time': 75},
                    {'title': 'Hypothesis Testing & Signifikansi Statistik', 'lesson_type': 'article', 'url': 'https://www.scribbr.com/statistics/hypothesis-testing/', 'estimated_time': 90},
                    {'title': 'Desain & Analisis A/B Testing', 'lesson_type': 'article', 'url': 'https://hbr.org/2017/06/a-refresher-on-ab-testing', 'estimated_time': 75},
                    {'title': 'Analisis Kohort & LTV (Lifetime Value)', 'lesson_type': 'article', 'url': 'https://amplitude.com/blog/cohort-analysis', 'estimated_time': 60},
                ],
                'project': {
                    'title': 'Analisis Hasil A/B Test untuk Kampanye Marketing', 'description': 'Analisis dataset hasil A/B test dari sebuah kampanye marketing. Tentukan apakah versi baru (B) memiliki performa yang secara statistik signifikan lebih baik daripada versi kontrol (A) berdasarkan metrik seperti conversion rate.', 'difficulty': 'Advanced',
                    'project_goals': 'Menerapkan metodologi hypothesis testing yang benar. Menginterpretasikan p-value dan confidence interval. Memberikan rekomendasi bisnis yang kuat berdasarkan hasil analisis statistik.', 'tech_stack': 'Python, Pandas, Matplotlib, SciPy',
                    'evaluation_criteria': 'Pemilihan uji statistik yang tepat, perhitungan yang akurat, kesimpulan yang didukung oleh bukti statistik, dan kemampuan mengkomunikasikan hasil kepada audiens non-teknis.', 'resources': 'Dataset A/B Testing dari Kaggle.'
                }
            },
            {
                'title': 'ETL & Data Engineering Dasar',
                'lessons': [
                    {'title': 'Konsep ETL (Extract, Transform, Load)', 'lesson_type': 'article', 'url': 'https://www.talend.com/resources/what-is-etl/', 'estimated_time': 60},
                    {'title': 'Pengenalan Data Warehouse & Data Lake', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=r_b4rTUn2aU', 'estimated_time': 75},
                    {'title': 'Otomatisasi Alur Kerja Data dengan Airflow', 'lesson_type': 'article', 'url': 'https://airflow.apache.org/docs/apache-airflow/stable/tutorial.html', 'estimated_time': 120},
                ],
                'project': {
                    'title': 'Membangun Pipeline ETL Sederhana', 'description': 'Buat sebuah pipeline data menggunakan Python yang mengambil data cuaca dari API publik (misal: OpenWeatherMap), melakukan transformasi sederhana (misal: konversi suhu), dan memuatnya ke dalam sebuah tabel di database PostgreSQL atau BigQuery.', 'difficulty': 'Advanced',
                    'project_goals': 'Memahami alur kerja ETL end-to-end. Mempraktikkan pengambilan data dari API, pemrosesan data, dan pemuatan ke database/data warehouse.', 'tech_stack': 'Python, Pandas, PostgreSQL/Google BigQuery, Requests',
                    'evaluation_criteria': 'Pipeline dapat dijalankan secara terjadwal (disimulasikan), data berhasil dimuat dengan skema yang benar, kode bersih, modular, dan memiliki penanganan error dasar.', 'resources': 'Dokumentasi OpenWeatherMap API, Dokumentasi Psycopg2 (untuk Postgres).'
                }
            }
        ],
        'ai-ml-engineer': [
            {
                'title': 'Python & Fondasi Matematika untuk Machine Learning',
                'lessons': [
                    {'title': 'Komputasi Numerik dengan NumPy', 'lesson_type': 'article', 'url': 'https://numpy.org/doc/stable/user/quickstart.html', 'estimated_time': 90},
                    {'title': 'Manipulasi Data dengan Pandas', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=e_n9pCgM_Hk', 'estimated_time': 120},
                    {'title': 'Visualisasi Data dengan Matplotlib & Seaborn', 'lesson_type': 'article', 'url': 'https://seaborn.pydata.org/tutorial.html', 'estimated_time': 75},
                    {'title': 'Refresh Konsep Kalkulus & Aljabar Linear', 'lesson_type': 'video', 'url': 'https://www.youtube.com/playlist?list=PLZHQObOWTQDMsr9K-rj53DwVRMYO3t57w', 'estimated_time': 120},
                ],
                'project': {
                    'title': 'Prediksi Harga Rumah (Regresi)', 'description': 'Bangun model machine learning untuk memprediksi harga rumah berdasarkan berbagai fitur (misal: jumlah kamar, luas, lokasi). Proyek ini mencakup seluruh siklus dasar: pembersihan data, feature engineering, pelatihan model, dan evaluasi.', 'difficulty': 'Beginner',
                    'project_goals': 'Melakukan data cleaning dan feature engineering. Melatih dan mengevaluasi beberapa model regresi (Linear Regression, Ridge, Lasso). Menginterpretasikan hasil dan koefisien model.', 'tech_stack': 'Python, Scikit-learn, Pandas, NumPy, Matplotlib',
                    'evaluation_criteria': 'Akurasi model dievaluasi dengan metrik yang tepat (MSE/RMSE, R-squared), proses preprocessing data terdokumentasi, justifikasi pemilihan model akhir.', 'resources': 'Dataset "Ames Housing" dari Kaggle.'
                }
            },
            {
                'title': 'Algoritma Inti Machine Learning',
                'lessons': [
                    {'title': 'Supervised Learning: Regresi & Klasifikasi', 'lesson_type': 'article', 'url': 'https://www.ibm.com/cloud/learn/supervised-learning', 'estimated_time': 90},
                    {'title': 'Model Berbasis Pohon (Decision Trees, Random Forest, Gradient Boosting/XGBoost)', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=gK43gtGh49o', 'estimated_time': 90},
                    {'title': 'Unsupervised Learning: Clustering (K-Means) & Reduksi Dimensi (PCA)', 'lesson_type': 'article', 'url': 'https://scikit-learn.org/stable/modules/clustering.html', 'estimated_time': 75},
                    {'title': 'Evaluasi Model: Cross-Validation, Confusion Matrix, ROC-AUC', 'lesson_type': 'article', 'url': 'https://scikit-learn.org/stable/modules/cross_validation.html', 'estimated_time': 60},
                ],
                'project': {
                    'title': 'Klasifikasi Jenis Kanker (Klasifikasi)', 'description': 'Bangun model klasifikasi untuk memprediksi apakah sebuah tumor bersifat ganas (malignant) atau jinak (benign) berdasarkan data medis. Bandingkan performa beberapa algoritma klasifikasi.', 'difficulty': 'Intermediate',
                    'project_goals': 'Membandingkan performa model (Logistic Regression, Random Forest, SVM, XGBoost). Menangani data yang mungkin tidak seimbang. Melakukan tuning hyperparameter untuk optimasi model.', 'tech_stack': 'Python, Scikit-learn, Pandas, XGBoost',
                    'evaluation_criteria': 'Metrik evaluasi yang komprehensif (Akurasi, Presisi, Recall, F1-score, ROC-AUC). Justifikasi pemilihan model terbaik berdasarkan masalah bisnis.', 'resources': 'Dataset "Breast Cancer Wisconsin" dari Scikit-learn atau Kaggle.'
                }
            },
            {
                'title': 'Deep Learning & Jaringan Saraf Tiruan',
                'lessons': [
                    {'title': 'Pengenalan Neural Networks dengan TensorFlow/PyTorch', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=aircAruvnKk', 'estimated_time': 120},
                    {'title': 'Computer Vision: Convolutional Neural Networks (CNN)', 'lesson_type': 'article', 'url': 'https://cs231n.github.io/convolutional-networks/', 'estimated_time': 90},
                    {'title': 'NLP: Recurrent Neural Networks (RNN) & LSTM', 'lesson_type': 'article', 'url': 'https://colah.github.io/posts/2015-08-Understanding-LSTMs/', 'estimated_time': 90},
                    {'title': 'Transfer Learning dengan Pre-trained Models', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=B_Pl_m4AkbY', 'estimated_time': 75},
                ],
                'project': {
                    'title': 'Klasifikasi Gambar Bunga (Computer Vision)', 'description': 'Gunakan transfer learning dengan model pre-trained (misal: MobileNetV2, ResNet50) untuk membuat model yang dapat mengklasifikasikan berbagai jenis bunga. Lakukan fine-tuning pada model untuk meningkatkan akurasi.', 'difficulty': 'Intermediate',
                    'project_goals': 'Memahami cara kerja transfer learning. Mengimplementasikan pipeline deep learning dari preprocessing gambar hingga pelatihan. Mengevaluasi model klasifikasi gambar.', 'tech_stack': 'Python, TensorFlow/PyTorch, Keras, Matplotlib',
                    'evaluation_criteria': 'Akurasi model pada validation set yang tinggi, proses fine-tuning yang efektif, kemampuan memvisualisasikan prediksi model.', 'resources': 'Dataset "Flowers" dari TensorFlow Datasets.'
                }
            },
            {
                'title': 'Spesialisasi: Natural Language Processing (NLP)',
                'lessons': [
                    {'title': 'Preprocessing Teks & Word Embeddings (Word2Vec)', 'lesson_type': 'article', 'url': 'https://www.kdnuggets.com/2018/03/text-data-preprocessing-walkthrough-python.html', 'estimated_time': 75},
                    {'title': 'Arsitektur Transformer & Model BERT', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=TQQlZhbC5ps', 'estimated_time': 120},
                    {'title': 'Fine-tuning Model Bahasa dengan Hugging Face', 'lesson_type': 'article', 'url': 'https://huggingface.co/docs/transformers/training', 'estimated_time': 90},
                ],
                'project': {
                    'title': 'Analisis Sentimen Ulasan Film IMDb', 'description': 'Gunakan model pre-trained berbasis Transformer (misal: DistilBERT) dari Hugging Face untuk melakukan klasifikasi sentimen (positif/negatif) pada dataset ulasan film IMDb. Lakukan fine-tuning untuk menyesuaikan model dengan data spesifik.', 'difficulty': 'Advanced',
                    'project_goals': 'Menerapkan state-of-the-art model NLP. Menggunakan library Hugging Face untuk pipeline NLP. Mengevaluasi performa model teks.', 'tech_stack': 'Python, PyTorch/TensorFlow, Hugging Face (Transformers, Datasets)',
                    'evaluation_criteria': 'Akurasi klasifikasi yang tinggi, proses fine-tuning yang benar, penanganan input teks yang efisien.', 'resources': 'Hugging Face Hub, dataset IMDb dari Hugging Face Datasets.'
                }
            },
            {
                'title': 'MLOps: Deploy & Maintenance Model',
                'lessons': [
                    {'title': 'Serving Model sebagai REST API (Flask/FastAPI)', 'lesson_type': 'article', 'url': 'https://www.freecodecamp.org/news/how-to-deploy-a-machine-learning-model-using-flask-859235e10b15/', 'estimated_time': 75},
                    {'title': 'Containerisasi Model dengan Docker', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=5_ADc_v-f8o', 'estimated_time': 75},
                    {'title': 'Experiment Tracking dengan MLflow/Weights & Biases', 'lesson_type': 'article', 'url': 'https://mlflow.org/docs/latest/getting-started/intro-quickstart/index.html', 'estimated_time': 90},
                    {'title': 'CI/CD untuk Machine Learning (GitHub Actions)', 'lesson_type': 'article', 'url': 'https://www.datacamp.com/tutorial/ci-cd-for-machine-learning', 'estimated_time': 90},
                ],
                'project': {
                    'title': 'Deploy Model Klasifikasi Kanker sebagai API', 'description': 'Ambil model klasifikasi kanker terbaik yang sudah Anda latih, "bungkus" dalam sebuah API menggunakan FastAPI, containerize dengan Docker, dan deploy ke platform cloud. API harus bisa menerima data pasien baru dan mengembalikan prediksi.', 'difficulty': 'Expert',
                    'project_goals': 'Memahami siklus hidup model dari notebook ke produksi. Mampu membuat API yang andal untuk melayani prediksi. Menerapkan praktik DevOps ke dalam machine learning.', 'tech_stack': 'Python, Scikit-learn, FastAPI, Docker, Render/Fly.io',
                    'evaluation_criteria': 'Endpoint API berfungsi dengan benar dan mengembalikan prediksi yang valid, Docker image teroptimasi, proses deployment berhasil, API memiliki dokumentasi dasar (via FastAPI).', 'resources': 'Dokumentasi FastAPI, Dokumentasi Docker, panduan deployment platform cloud.'
                }
            }
        ],
        'devops-engineer': [
            {
                'title': 'Fondasi Sistem, Jaringan & Linux',
                'lessons': [
                    {'title': 'Dasar Perintah Linux & Manajemen Sistem', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=sWbUDq4S6Y8', 'estimated_time': 120},
                    {'title': 'Shell Scripting (Bash) untuk Otomatisasi', 'lesson_type': 'article', 'url': 'https://www.shellscript.sh/', 'estimated_time': 90},
                    {'title': 'Konsep Jaringan (TCP/IP, DNS, HTTP/S, Firewall)', 'lesson_type': 'article', 'url': 'https://www.comptia.org/content/guides/what-is-tcp-ip', 'estimated_time': 75},
                ],
                'project': {
                    'title': 'Setup Web Server & Reverse Proxy Nginx', 'description': 'Konfigurasikan sebuah server Linux (bisa di VM lokal atau cloud) untuk menjalankan Nginx. Buat konfigurasi untuk menyajikan sebuah website statis dan konfigurasikan Nginx sebagai reverse proxy untuk sebuah aplikasi backend sederhana.', 'difficulty': 'Beginner',
                    'project_goals': 'Menguasai perintah dasar Linux. Memahami konfigurasi Nginx. Mempraktikkan konsep-konsep jaringan seperti port dan proxy.', 'tech_stack': 'Linux (Ubuntu), Nginx, Bash Script',
                    'evaluation_criteria': 'Server Nginx berjalan dan dapat diakses, website statis tersaji dengan benar, reverse proxy berhasil meneruskan request ke aplikasi backend.', 'resources': 'Dokumentasi DigitalOcean, tutorial Nginx.'
                }
            },
            {
                'title': 'Infrastructure as Code (IaC) & Otomatisasi Konfigurasi',
                'lessons': [
                    {'title': 'Provisioning Infrastruktur dengan Terraform', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=SLB_c_KZN2I', 'estimated_time': 120},
                    {'title': 'Manajemen Konfigurasi Server dengan Ansible', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=goclfp6a2VY', 'estimated_time': 120},
                    {'title': 'Containerisasi dengan Docker & Docker Compose', 'lesson_type': 'article', 'url': 'https://docs.docker.com/get-started/', 'estimated_time': 90},
                ],
                'project': {
                    'title': 'Provisioning & Konfigurasi Server Otomatis', 'description': 'Gunakan Terraform untuk membuat sebuah instance VM di cloud provider (AWS/GCP/DigitalOcean). Setelah VM dibuat, gunakan Ansible untuk secara otomatis menginstal Nginx, database, dan dependensi lainnya ke dalam VM tersebut.', 'difficulty': 'Intermediate',
                    'project_goals': 'Mengotomatiskan seluruh proses dari pembuatan infrastruktur hingga konfigurasi. Memahami prinsip IaC dan idempotency.', 'tech_stack': 'Terraform, Ansible, AWS/GCP, YAML',
                    'evaluation_criteria': 'Proses berjalan end-to-end dengan satu perintah, server terkonfigurasi sesuai spesifikasi dalam playbook Ansible, kode Terraform dan Ansible modular dan dapat digunakan kembali.', 'resources': 'Dokumentasi Terraform, Dokumentasi Ansible.'
                }
            },
            {
                'title': 'CI/CD Pipelines & Monitoring',
                'lessons': [
                    {'title': 'Konsep Continuous Integration & Delivery (CI/CD)', 'lesson_type': 'article', 'url': 'https://www.atlassian.com/continuous-delivery/principles/continuous-integration-vs-delivery-vs-deployment', 'estimated_time': 60},
                    {'title': 'Membangun Pipeline dengan GitHub Actions / GitLab CI', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=R8_veQiYhIc', 'estimated_time': 90},
                    {'title': 'Monitoring Metrik dengan Prometheus', 'lesson_type': 'article', 'url': 'https://prometheus.io/docs/introduction/overview/', 'estimated_time': 75},
                    {'title': 'Visualisasi Dashboard dengan Grafana', 'lesson_type': 'article', 'url': 'https://grafana.com/docs/grafana/latest/getting-started/what-is-grafana/', 'estimated_time': 75},
                ],
                'project': {
                    'title': 'Pipeline CI/CD untuk Aplikasi Web', 'description': 'Buat pipeline CI/CD menggunakan GitHub Actions untuk sebuah aplikasi web sederhana. Pipeline harus otomatis menjalankan tes, membangun Docker image, mem-push image ke container registry (Docker Hub/GitHub Packages), dan men-deploy-nya ke server.', 'difficulty': 'Advanced',
                    'project_goals': 'Mengotomatiskan seluruh alur kerja dari kode hingga deployment. Mengintegrasikan berbagai tahapan (test, build, deploy) dalam satu pipeline.', 'tech_stack': 'GitHub Actions, Docker, YAML, Shell Script',
                    'evaluation_criteria': 'Pipeline berjalan otomatis setiap ada push ke branch main, setiap tahap (job) berhasil, Docker image ter-tag dengan benar, deployment berhasil memperbarui aplikasi di server.', 'resources': 'Dokumentasi GitHub Actions, contoh-contoh workflow.'
                }
            },
            {
                'title': 'Orkestrasi Kontainer dengan Kubernetes',
                'lessons': [
                    {'title': 'Arsitektur & Objek Inti Kubernetes (Pod, Service, Deployment)', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=X48VuDVv0do', 'estimated_time': 120},
                    {'title': 'Manajemen Konfigurasi & Secret (ConfigMap, Secret)', 'lesson_type': 'article', 'url': 'https://kubernetes.io/docs/concepts/configuration/', 'estimated_time': 60},
                    {'title': 'Manajemen Paket Aplikasi dengan Helm', 'lesson_type': 'article', 'url': 'https://helm.sh/docs/intro/quickstart/', 'estimated_time': 75},
                    {'title': 'Ingress & Service Mesh (Istio) Dasar', 'lesson_type': 'article', 'url': 'https://kubernetes.io/docs/concepts/services-networking/ingress/', 'estimated_time': 60},
                ],
                'project': {
                    'title': 'Deploy Aplikasi Multi-container ke Klaster Kubernetes', 'description': 'Deploy aplikasi web yang terdiri dari frontend, backend, dan database ke dalam klaster Kubernetes (bisa menggunakan Minikube/kind untuk lokal). Setiap bagian harus berjalan dalam Pod-nya sendiri, berkomunikasi melalui Services, dan diekspos ke luar melalui Ingress.', 'difficulty': 'Advanced',
                    'project_goals': 'Memahami cara kerja arsitektur berbasis Kubernetes. Mampu menulis file manifest YAML untuk berbagai objek Kubernetes. Men-debug aplikasi yang berjalan di dalam klaster.', 'tech_stack': 'Kubernetes, kubectl, Docker, YAML, Minikube/kind, Helm',
                    'evaluation_criteria': 'Aplikasi berjalan dengan benar di klaster, semua service dapat berkomunikasi, aplikasi dapat diakses dari luar klaster melalui Ingress, manifest YAML terstruktur dengan baik.', 'resources': 'Dokumentasi Kubernetes, tutorial Minikube.'
                }
            },
            {
                'title': 'Manajemen Cloud & Keamanan (DevSecOps)',
                'lessons': [
                    {'title': 'Dasar-dasar Cloud Provider (AWS/GCP/Azure)', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=SOTamWd_2iI', 'estimated_time': 90},
                    {'title': 'Identity & Access Management (IAM)', 'lesson_type': 'article', 'url': 'https://aws.amazon.com/iam/', 'estimated_time': 60},
                    {'title': 'Keamanan Jaringan Cloud (VPC, Security Groups)', 'lesson_type': 'article', 'url': 'https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html', 'estimated_time': 75},
                    {'title': 'Prinsip DevSecOps & Pemindaian Keamanan', 'lesson_type': 'article', 'url': 'https://snyk.io/learn/container-security/', 'estimated_time': 60},
                ],
                'project': {
                    'title': 'Infrastruktur Aman di Cloud dengan Terraform', 'description': 'Tulis skrip Terraform untuk membuat infrastruktur jaringan yang aman di AWS, termasuk VPC dengan subnet publik dan privat, security group yang ketat, dan sebuah EC2 instance di subnet privat yang hanya bisa diakses melalui bastion host di subnet publik.', 'difficulty': 'Expert',
                    'project_goals': 'Menerapkan prinsip "least privilege" dalam desain infrastruktur. Mengotomatiskan pembuatan infrastruktur cloud yang aman dan sesuai best practices.', 'tech_stack': 'Terraform, AWS, IAM',
                    'evaluation_criteria': 'Infrastruktur berhasil dibuat, aturan firewall (security group) membatasi akses secara efektif, penggunaan subnet privat dan publik yang benar, kode Terraform modular.', 'resources': 'Dokumentasi Terraform AWS Provider, AWS Well-Architected Framework.'
                }
            }
        ]
    }

    # 4. Perulangan untuk membuat semua data
    modules_map = {}
    for career_path, modules in career_data.items():
        print(f"--- Menambahkan data untuk: {career_path.replace('-', ' ').title()} ---")
        for i, module_data in enumerate(modules, 1):
            new_module = Module(
                title=module_data['title'], order=i, career_path=career_path, roadmap_id=roadmap_umum.id
            )
            db.session.add(new_module)
            db.session.flush()
            modules_map[new_module.title] = new_module.id

            for j, lesson_data in enumerate(module_data['lessons'], 1):
                new_lesson = Lesson(
                    title=lesson_data['title'], order=j, module_id=new_module.id,
                    lesson_type=lesson_data.get('lesson_type', 'article'),
                    url=lesson_data.get('url'),
                    estimated_time=lesson_data.get('estimated_time', 30)
                )
                db.session.add(new_lesson)
            
            project_data = module_data['project']
            new_project = Project(
                title=project_data['title'], description=project_data['description'], difficulty=project_data['difficulty'],
                module_id=new_module.id, project_goals=project_data['project_goals'], tech_stack=project_data['tech_stack'],
                evaluation_criteria=project_data['evaluation_criteria'], resources=project_data['resources']
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
    
    # 6. Commit final
    db.session.commit()
    print("=" * 60)
    print("✅ SEMUA DATA YANG DIPERBARUI DAN DIPERKAYA BERHASIL DITAMBAHKAN! ✅")
    print("=" * 60)