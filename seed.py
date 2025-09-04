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

    # 3. Definisikan struktur data kurikulum yang kaya
    career_data = {
        'frontend': [
            {
                'title': 'Dasar-Dasar Frontend',
                'lessons': [
                    {'title': 'HTML5 Semantic Elements', 'lesson_type': 'article', 'url': 'https://www.w3schools.com/html/html5_semantic_elements.asp', 'estimated_time': 30},
                    {'title': 'CSS Flexbox & Grid', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=K74l26pE4A0', 'estimated_time': 60},
                    {'title': 'Dasar JavaScript & DOM Manipulation', 'lesson_type': 'article', 'url': 'https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model/Introduction', 'estimated_time': 90},
                    {'title': 'Asynchronous JavaScript (Async/Await)', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=V_Kr9OSfDeU', 'estimated_time': 45},
                ],
                'project': {
                    'title': 'Personal Portfolio Website', 'description': 'Buat website portofolio statis yang responsif menggunakan HTML & CSS.', 'difficulty': 'Beginner',
                    'project_goals': 'Mempraktikkan layout dengan CSS. Menampilkan diri dan karya secara profesional.', 'tech_stack': 'HTML5, CSS3, JavaScript',
                    'evaluation_criteria': 'Desain responsif, penggunaan elemen semantik, interaktivitas dasar.', 'resources': 'MDN Web Docs, CSS-Tricks.'
                }
            },
            {
                'title': 'Framework Modern: React.js',
                'lessons': [
                    {'title': 'Component & Props', 'lesson_type': 'article', 'url': 'https://reactjs.org/docs/components-and-props.html', 'estimated_time': 45},
                    {'title': 'State & Lifecycle', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=nL2b6s_3a_w', 'estimated_time': 60},
                    {'title': 'React Hooks (useState, useEffect)', 'lesson_type': 'article', 'url': 'https://reactjs.org/docs/hooks-intro.html', 'estimated_time': 75},
                    {'title': 'Client-Side Routing dengan React Router', 'lesson_type': 'article', 'url': 'https://reactrouter.com/en/main/start/tutorial', 'estimated_time': 60},
                ],
                'project': {
                    'title': 'Aplikasi To-Do List dengan React', 'description': 'Buat aplikasi CRUD sederhana untuk mengelola daftar tugas.', 'difficulty': 'Intermediate',
                    'project_goals': 'Memahami cara kerja state dan props. Mampu melakukan operasi CRUD.', 'tech_stack': 'React.js, JavaScript (ES6), CSS',
                    'evaluation_criteria': 'Fungsionalitas CRUD berjalan sempurna, penggunaan Hooks yang tepat, komponen terstruktur.', 'resources': 'Dokumentasi resmi React.'
                }
            },
            {
                'title': 'Manajemen State & Styling Lanjutan',
                'lessons': [
                    {'title': 'Global State dengan Redux Toolkit', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=bbkBuqC1rU4', 'estimated_time': 90},
                    {'title': 'Alternatif State Management: Zustand', 'lesson_type': 'article', 'url': 'https://zustand-demo.pmnd.rs/', 'estimated_time': 45},
                    {'title': 'Utility-First Styling dengan Tailwind CSS', 'lesson_type': 'article', 'url': 'https://tailwindcss.com/docs/utility-first', 'estimated_time': 75},
                ],
                'project': {
                    'title': 'Clone Tampilan Tokopedia', 'description': 'Buat ulang halaman utama Tokopedia (hanya tampilan) dengan React & Tailwind.', 'difficulty': 'Intermediate',
                    'project_goals': 'Mampu mengimplementasikan desain kompleks menjadi kode. Mempraktikkan layout menggunakan Tailwind CSS.', 'tech_stack': 'React.js, Tailwind CSS',
                    'evaluation_criteria': 'Akurasi desain sesuai referensi, penggunaan kelas utilitas Tailwind yang efisien.', 'resources': 'Halaman utama Tokopedia, dokumentasi Tailwind CSS.'
                }
            },
        ],
        'backend': [
            {
                'title': 'Dasar-Dasar Backend & Database',
                'lessons': [
                    {'title': 'Pengenalan HTTP & REST API', 'lesson_type': 'article', 'url': 'https://www.restapitutorial.com/', 'estimated_time': 45},
                    {'title': 'Dasar SQL & Relational Database', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=HXV3zeQKqGY', 'estimated_time': 90},
                    {'title': 'Setup Server dengan Node.js & Express', 'lesson_type': 'article', 'url': 'https://expressjs.com/en/starter/hello-world.html', 'estimated_time': 60},
                    {'title': 'Manajemen Environment Variables (.env)', 'lesson_type': 'article', 'url': 'https://www.npmjs.com/package/dotenv', 'estimated_time': 20},
                ],
                'project': {
                    'title': 'API Sederhana untuk Blog', 'description': 'Buat endpoint CRUD untuk artikel blog.', 'difficulty': 'Beginner',
                    'project_goals': 'Membuat API dengan endpoint dasar (GET, POST, PUT, DELETE). Memahami konsep rute dan controller.', 'tech_stack': 'Node.js, Express.js, SQLite/PostgreSQL',
                    'evaluation_criteria': 'Endpoint berfungsi dengan benar, respons HTTP sesuai, struktur kode terorganisir.', 'resources': 'Dokumentasi Express.js.'
                }
            },
            {
                'title': 'Autentikasi & Keamanan',
                'lessons': [
                    {'title': 'Autentikasi dengan JWT', 'lesson_type': 'article', 'url': 'https://jwt.io/introduction/', 'estimated_time': 60},
                    {'title': 'Password Hashing dengan Bcrypt', 'lesson_type': 'article', 'url': 'https://www.npmjs.com/package/bcrypt', 'estimated_time': 30},
                    {'title': 'Middleware untuk Otorisasi', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=lY6icfhap2o', 'estimated_time': 45},
                ],
                'project': {
                    'title': 'API dengan Sistem Login & Register', 'description': 'Tambahkan fitur autentikasi pada API blog.', 'difficulty': 'Intermediate',
                    'project_goals': 'Mengimplementasikan sistem login dan register. Memahami cara kerja JWT dan otorisasi.', 'tech_stack': 'Node.js, Express.js, JWT, Bcrypt',
                    'evaluation_criteria': 'Autentikasi berfungsi dengan aman, password di-hash, penanganan error yang baik.', 'resources': 'Dokumentasi JWT, tutorial Bcrypt.'
                }
            },
            {
                'title': 'Arsitektur & Deployment Backend',
                'lessons': [
                    {'title': 'Dasar-Dasar Docker untuk Development', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=3c-iBn73dDE', 'estimated_time': 90},
                    {'title': 'Menggunakan ORM (Prisma/Sequelize)', 'lesson_type': 'article', 'url': 'https://www.prisma.io/docs/getting-started', 'estimated_time': 75},
                    {'title': 'Deploy API ke Cloud (Render/Heroku)', 'lesson_type': 'article', 'url': 'https://render.com/docs/deploy-node-express-app', 'estimated_time': 60},
                ],
                'project': {
                    'title': 'API E-commerce (Product & Order)', 'description': 'Rancang API untuk mengelola produk dan pesanan.', 'difficulty': 'Advanced',
                    'project_goals': 'Merancang skema database untuk e-commerce. Membangun relasi antar tabel.', 'tech_stack': 'Node.js, Express.js, PostgreSQL, Prisma',
                    'evaluation_criteria': 'Desain database normalisasi, endpoint relasional berfungsi, kode modular.', 'resources': 'Panduan desain skema e-commerce.'
                }
            },
        ],
        'data-analyst': [
            {
                'title': 'Fondasi Analisis Data',
                'lessons': [
                    {'title': 'Dasar-Dasar Statistik Deskriptif', 'lesson_type': 'article', 'url': 'https://www.scribbr.com/statistics/descriptive-statistics/', 'estimated_time': 60},
                    {'title': 'Query SQL Lanjutan (JOIN, Subquery, CTE)', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=D-S1gV-eOY4', 'estimated_time': 75},
                    {'title': 'Pengenalan Python dengan Pandas', 'lesson_type': 'article', 'url': 'https://pandas.pydata.org/docs/user_guide/10min.html', 'estimated_time': 90},
                    {'title': 'Teknik Data Cleaning dengan Pandas', 'lesson_type': 'article', 'url': 'https://realpython.com/python-data-cleaning-numpy-pandas/', 'estimated_time': 75},
                ],
                'project': {
                    'title': 'Analisis Data Penjualan Retail', 'description': 'Analisis dataset penjualan untuk menemukan tren produk dan perilaku konsumen.', 'difficulty': 'Beginner',
                    'project_goals': 'Melakukan data cleaning. Mengidentifikasi tren data. Membuat visualisasi sederhana.', 'tech_stack': 'Python, Pandas, Matplotlib/Seaborn',
                    'evaluation_criteria': 'Visualisasi yang jelas, insight yang logis, dan kode yang bersih.', 'resources': 'Dataset penjualan dari Kaggle.'
                }
            },
            {
                'title': 'Visualisasi & Storytelling Data',
                'lessons': [
                    {'title': 'Prinsip Desain Visualisasi Data', 'lesson_type': 'article', 'url': 'https://www.tableau.com/learn/articles/data-visualization-best-practices', 'estimated_time': 45},
                    {'title': 'Membuat Dashboard dengan Tableau/Looker', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=zOR0-nyie_A', 'estimated_time': 120},
                    {'title': 'Visualisasi Geospasial (Peta)', 'lesson_type': 'article', 'url': 'https://plotly.com/python/maps/', 'estimated_time': 60},
                    {'title': 'Storytelling with Data', 'lesson_type': 'article', 'url': 'http://www.storytellingwithdata.com/blog', 'estimated_time': 60},
                ],
                'project': {
                    'title': 'Dashboard Interaktif Covid-19', 'description': 'Buat dashboard untuk memvisualisasikan data kasus Covid-19 secara global.', 'difficulty': 'Intermediate',
                    'project_goals': 'Membuat dashboard yang interaktif. Menggunakan berbagai jenis visualisasi untuk menceritakan \'kisah\' dari data.', 'tech_stack': 'Tableau/Looker Studio',
                    'evaluation_criteria': 'Desain dashboard yang intuitif, alur cerita yang jelas, dan penggunaan filter yang efektif.', 'resources': 'Dataset Covid-19 dari Our World in Data.'
                }
            },
            {
                'title': 'Statistik dan Business Acumen',
                'lessons': [
                    {'title': 'Dasar Probabilitas & Distribusi', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=uzkc-qNVoOk', 'estimated_time': 75},
                    {'title': 'Hypothesis Testing & A/B Testing', 'lesson_type': 'article', 'url': 'https://hbr.org/2017/06/a-refresher-on-ab-testing', 'estimated_time': 90},
                    {'title': 'Analisis Kohort & Retensi Pengguna', 'lesson_type': 'article', 'url': 'https://amplitude.com/blog/cohort-analysis', 'estimated_time': 60},
                ],
                'project': {
                    'title': 'Analisis Hasil A/B Test Website', 'description': 'Analisis data hasil A/B test untuk menentukan versi halaman web mana yang lebih baik.', 'difficulty': 'Advanced',
                    'project_goals': 'Memahami signifikansi statistik. Membuat rekomendasi bisnis berdasarkan data.', 'tech_stack': 'Python, Pandas, Scipy',
                    'evaluation_criteria': 'Metodologi statistik yang benar, kesimpulan yang didukung data, visualisasi perbandingan.', 'resources': 'Dataset A/B testing dari Kaggle.'
                }
            },
        ],
        'ai-ml-engineer': [
            {
                'title': 'Python untuk Machine Learning',
                'lessons': [
                    {'title': 'Numpy untuk Komputasi Numerik', 'lesson_type': 'article', 'url': 'https://numpy.org/doc/stable/user/quickstart.html', 'estimated_time': 90},
                    {'title': 'Pandas untuk Manipulasi Data', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=e60Itwl_3nA', 'estimated_time': 120},
                    {'title': 'Visualisasi dengan Matplotlib & Seaborn', 'lesson_type': 'article', 'url': 'https://seaborn.pydata.org/tutorial.html', 'estimated_time': 75},
                ],
                'project': {
                    'title': 'Prediksi Harga Rumah', 'description': 'Buat model regresi untuk memprediksi harga rumah berdasarkan fitur-fitur seperti luas, lokasi, dll.', 'difficulty': 'Beginner',
                    'project_goals': 'Melakukan data cleaning dan feature engineering. Melatih model regresi linear. Mengevaluasi model dengan MSE/RMSE.', 'tech_stack': 'Python, Scikit-learn, Pandas, Numpy',
                    'evaluation_criteria': 'Akurasi model, proses preprocessing data yang terdokumentasi, interpretasi hasil.', 'resources': 'Dataset "Boston Housing" dari Scikit-learn.'
                }
            },
            {
                'title': 'Algoritma Inti Machine Learning',
                'lessons': [
                    {'title': 'Supervised Learning: Regresi & Klasifikasi', 'lesson_type': 'article', 'url': 'https://www.ibm.com/cloud/learn/supervised-learning', 'estimated_time': 90},
                    {'title': 'Unsupervised Learning: Clustering (K-Means)', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=4b5d3muwGtl', 'estimated_time': 75},
                    {'title': 'Decision Trees & Random Forests', 'lesson_type': 'article', 'url': 'https://towardsdatascience.com/understanding-random-forest-58381e0602d2', 'estimated_time': 75},
                ],
                'project': {
                    'title': 'Prediksi Churn Pelanggan Telekomunikasi', 'description': 'Buat model klasifikasi untuk memprediksi pelanggan mana yang kemungkinan besar akan berhenti berlangganan.', 'difficulty': 'Intermediate',
                    'project_goals': 'Membandingkan beberapa model klasifikasi (Logistic Regression, Random Forest). Menangani data tidak seimbang (imbalanced data).', 'tech_stack': 'Python, Scikit-learn, Pandas',
                    'evaluation_criteria': 'Akurasi, presisi, recall, F1-score. Justifikasi pilihan model.', 'resources': 'Dataset "Telco Customer Churn" dari Kaggle.'
                }
            },
            {
                'title': 'Deep Learning dan MLOps',
                'lessons': [
                    {'title': 'Pengenalan Deep Learning & Neural Networks', 'lesson_type': 'article', 'url': 'https://www.tensorflow.org/guide/keras/sequential_model', 'estimated_time': 120},
                    {'title': 'Transfer Learning dengan Pre-trained Models', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=B_Pl_m4AkbY', 'estimated_time': 90},
                    {'title': 'Serving Models dengan Flask/FastAPI', 'lesson_type': 'article', 'url': 'https://www.freecodecamp.org/news/how-to-deploy-a-machine-learning-model-using-flask-859235e10b15/', 'estimated_time': 75},
                ],
                'project': {
                    'title': 'Deploy Model Klasifikasi Gambar sebagai API', 'description': 'Ambil model klasifikasi gambar (misal: dari Fashion MNIST) dan deploy sebagai REST API.', 'difficulty': 'Advanced',
                    'project_goals': 'Mampu "membungkus" model terlatih ke dalam sebuah service API. Memahami cara menerima input (gambar) dan mengembalikan prediksi (JSON).', 'tech_stack': 'Python, TensorFlow/Keras, Flask/FastAPI, Docker',
                    'evaluation_criteria': 'Endpoint API berfungsi dengan benar, respons cepat, penanganan error input.', 'resources': 'Dokumentasi Flask/FastAPI.'
                }
            },
        ],
        'devops-engineer': [
            {
                'title': 'Fondasi Sistem & Jaringan',
                'lessons': [
                    {'title': 'Dasar Perintah Linux & Shell Scripting', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=oJKkk4JjNno', 'estimated_time': 120},
                    {'title': 'Konsep Jaringan (IP, DNS, HTTP/S)', 'lesson_type': 'article', 'url': 'https://www.cloudflare.com/learning/dns/what-is-dns/', 'estimated_time': 75},
                    {'title': 'Virtualisasi vs Containerisasi (Docker)', 'lesson_type': 'article', 'url': 'https://www.docker.com/resources/what-container/', 'estimated_time': 60},
                ],
                'project': {
                    'title': 'Setup Web Server Nginx Sederhana di VM', 'description': 'Gunakan Vagrant atau cloud VM untuk menginstal dan mengkonfigurasi server Nginx dari awal.', 'difficulty': 'Beginner',
                    'project_goals': 'Memahami proses setup server. Mengerti konfigurasi dasar Nginx. Mempraktikkan perintah-perintah Linux.', 'tech_stack': 'Linux (Ubuntu), Nginx, Bash Script',
                    'evaluation_criteria': 'Server Nginx berjalan dan menyajikan halaman HTML sederhana, proses didokumentasikan.', 'resources': 'Dokumentasi DigitalOcean, tutorial Nginx.'
                }
            },
            {
                'title': 'Infrastructure as Code (IaC) & Otomasi',
                'lessons': [
                    {'title': 'Pengenalan Terraform untuk Provisioning', 'lesson_type': 'article', 'url': 'https://developer.hashicorp.com/terraform/intro', 'estimated_time': 90},
                    {'title': 'Manajemen Konfigurasi dengan Ansible', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=goclfp6a2VY', 'estimated_time': 120},
                    {'title': 'Container Orchestration dengan Docker Compose', 'lesson_type': 'article', 'url': 'https://docs.docker.com/compose/', 'estimated_time': 75},
                ],
                'project': {
                    'title': 'Otomatisasi Setup Server dengan Ansible', 'description': 'Buat Ansible playbook untuk menginstal Nginx, database, dan dependensi lain secara otomatis.', 'difficulty': 'Intermediate',
                    'project_goals': 'Menulis playbook Ansible yang idempotent. Mengelola variabel dan template. Menjalankan playbook pada target server.', 'tech_stack': 'Ansible, YAML, Linux',
                    'evaluation_criteria': 'Playbook berjalan tanpa error, server terkonfigurasi sesuai spesifikasi.', 'resources': 'Dokumentasi Ansible, contoh-contoh playbook.'
                }
            },
            {
                'title': 'CI/CD Pipelines & Monitoring',
                'lessons': [
                    {'title': 'Prinsip Continuous Integration & Delivery', 'lesson_type': 'article', 'url': 'https://www.atlassian.com/continuous-delivery/principles/continuous-integration-vs-delivery-vs-deployment', 'estimated_time': 60},
                    {'title': 'Membangun Pipeline dengan GitHub Actions', 'lesson_type': 'video', 'url': 'https://www.youtube.com/watch?v=R8_veQiYhIc', 'estimated_time': 90},
                    {'title': 'Dasar Monitoring dengan Prometheus & Grafana', 'lesson_type': 'article', 'url': 'https://grafana.com/docs/grafana/latest/getting-started/what-is-grafana/', 'estimated_time': 90},
                ],
                'project': {
                    'title': 'Membuat Pipeline CI/CD untuk Aplikasi Web', 'description': 'Buat pipeline di GitHub Actions yang secara otomatis melakukan testing dan deploy aplikasi sederhana setiap kali ada push ke main branch.', 'difficulty': 'Advanced',
                    'project_goals': 'Mengerti alur kerja CI/CD. Menulis file workflow YAML. Mengintegrasikan testing dan deployment steps.', 'tech_stack': 'GitHub Actions, Docker, YAML',
                    'evaluation_criteria': 'Pipeline berjalan otomatis dan berhasil, setiap step berfungsi (test, build, deploy).', 'resources': 'Dokumentasi GitHub Actions, contoh workflow.'
                }
            },
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
    
    # 5. Menambahkan proyek tantangan
    print("--- Menambahkan Proyek Tantangan ---")
    challenges = [
        Project(title='Real-time Chat Application', description='Bangun aplikasi chat real-time menggunakan WebSocket.', difficulty='Advanced', is_challenge=True, module_id=modules_map.get('Dasar-Dasar Backend & Database'), tech_stack="Node.js, Express.js, Socket.io"),
        Project(title='Platform E-learning Dashboard', description='Desain dan implementasikan dashboard interaktif untuk platform e-learning.', difficulty='Advanced', is_challenge=True, module_id=modules_map.get('Fondasi Analisis Data'), tech_stack="Python, Plotly/Dash"),
        Project(title='Music Player Web App', description='Buat aplikasi pemutar musik di web dengan React yang mengambil data dari API publik.', difficulty='Intermediate', is_challenge=True, module_id=modules_map.get('Dasar-Dasar Frontend'), tech_stack="React.js, Fetch API/Axios")
    ]
    db.session.add_all(challenges)
    
    # 6. Commit final
    db.session.commit()
    print("=" * 60)
    print("✅ SEMUA DATA YANG DIPERBANYAK BERHASIL DITAMBAHKAN! ✅")
    print("=" * 60)