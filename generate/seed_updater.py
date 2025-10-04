# nama file: seed_green_tech.py
from app import create_app, db
from app.models import GreenCareerPath, GreenModule, ProjectPartner, GreenProject

app = create_app()

with app.app_context():
    # ====================================================================
    # BAGIAN 1: SEEDING GREEN CAREER PATHS & MODULES
    # ====================================================================
    print("=" * 60)
    print("Memulai proses seeding untuk Green Career Paths...")
    print("=" * 60)

    # Definisikan HANYA struktur kurikulum GREEN TECH BARU
    green_career_data = {
        'renewable-energy-engineer': {
            'title': 'Renewable Energy Engineer',
            'description': 'Fokus pada desain, pengembangan, dan implementasi teknologi energi terbarukan seperti surya, angin, dan air untuk masa depan yang berkelanjutan.',
            'modules': [
                {'title': 'Dasar-dasar Energi Terbarukan', 'description': 'Pengenalan panel surya, turbin angin, dan hidroelektrik.'},
                {'title': 'Manajemen Proyek Energi', 'description': 'Belajar merencanakan dan mengeksekusi proyek energi skala besar.'},
                {'title': 'Analisis Kebijakan Energi', 'description': 'Memahami regulasi pemerintah terkait energi bersih di Indonesia.'},
            ]
        },
        'sustainability-analyst': {
            'title': 'Sustainability Analyst',
            'description': 'Menganalisis data untuk membantu perusahaan mengurangi jejak karbon, meningkatkan efisiensi, dan memenuhi standar lingkungan (ESG).',
            'modules': [
                {'title': 'Pengantar ESG', 'description': 'Memahami pilar Environmental, Social, and Governance dalam bisnis.'},
                {'title': 'Analisis Jejak Karbon', 'description': 'Teknik mengukur dan menganalisis emisi gas rumah kaca perusahaan.'},
                {'title': 'Pelaporan Keberlanjutan', 'description': 'Menyusun laporan dampak lingkungan sesuai standar global.'},
            ]
        },
        'agri-tech-specialist': {
            'title': 'Agri-Tech Specialist',
            'description': 'Mengembangkan dan menerapkan teknologi modern seperti IoT, drone, dan AI untuk menciptakan sistem pertanian yang lebih efisien dan berkelanjutan.',
            'modules': [
                {'title': 'Smart Farming & IoT', 'description': 'Menggunakan sensor untuk memantau kondisi tanah dan tanaman secara real-time.'},
                {'title': 'Pertanian Presisi', 'description': 'Pemanfaatan drone dan citra satelit untuk optimasi panen.'},
                {'title': 'Manajemen Rantai Pasok Pangan', 'description': 'Teknologi untuk melacak produk dari ladang hingga ke meja makan.'},
            ]
        },
        # --- PENAMBAHAN BARU DI SINI ---
        'green-it-specialist': {
            'title': 'Green IT Specialist',
            'description': 'Mengoptimalkan penggunaan teknologi informasi untuk mengurangi dampak lingkungan, mulai dari efisiensi energi di data center hingga pengembangan perangkat lunak yang ramah lingkungan.',
            'modules': [
                {'title': 'Pengantar Green IT dan Komputasi Berkelanjutan', 'description': 'Memahami konsep dasar Green IT, dampaknya terhadap lingkungan, dan pentingnya efisiensi energi dalam infrastruktur digital.'},
                {'title': 'Efisiensi Energi pada Data Center', 'description': 'Teknik untuk mengurangi konsumsi daya pada server, sistem pendingin, dan jaringan di pusat data skala besar.'},
                {'title': 'Perangkat Lunak Berkelanjutan (Sustainable Software)', 'description': 'Prinsip dan praktik pengembangan perangkat lunak yang meminimalkan jejak karbon, dari algoritma yang efisien hingga desain arsitektur.'},
                {'title': 'Ekonomi Sirkular untuk Perangkat Keras IT', 'description': 'Strategi untuk memperpanjang siklus hidup perangkat keras, mulai dari perbaikan, penggunaan kembali, hingga daur ulang yang bertanggung jawab (e-waste management).'},
                {'title': 'Monitoring dan Pelaporan Dampak IT', 'description': 'Menggunakan alat untuk mengukur, menganalisis, dan melaporkan konsumsi energi serta jejak karbon dari operasional IT.'}
            ]
        }
        # --- AKHIR PENAMBAHAN ---
    }

    # Perulangan cerdas untuk menambah HANYA data baru
    for slug, path_data in green_career_data.items():
        print(f"\n--- Memeriksa data untuk: {path_data['title']} ---")
        
        # Cek atau buat GreenCareerPath
        existing_path = GreenCareerPath.query.filter_by(slug=slug).first()
        if not existing_path:
            print(f" -> Menambahkan Green Career Path: '{path_data['title']}'")
            new_path = GreenCareerPath(
                slug=slug,
                title=path_data['title'],
                description=path_data['description']
            )
            db.session.add(new_path)
            db.session.flush() # flush untuk mendapatkan ID dari path baru
            path_id = new_path.id
        else:
            print(f" -> Green Career Path '{path_data['title']}' sudah ada.")
            path_id = existing_path.id

        # Cek atau buat modul-modul di dalamnya
        for i, module_data in enumerate(path_data['modules'], 1):
            existing_module = GreenModule.query.filter_by(
                title=module_data['title'],
                career_path_id=path_id
            ).first()

            if existing_module:
                print(f"    -> Modul '{module_data['title']}' sudah ada, dilewati.")
                continue
            
            print(f"    -> Menambahkan modul baru: '{module_data['title']}'")
            new_module = GreenModule(
                title=module_data['title'],
                description=module_data['description'],
                order=i,
                career_path_id=path_id
            )
            db.session.add(new_module)
            
    # Commit semua perubahan untuk Green Careers
    db.session.commit()

    # ====================================================================
    # BAGIAN 2: SEEDING GREEN IMPACT PROJECTS & PARTNERS
    # ====================================================================
    print("\n" + "=" * 60)
    print("Memulai proses seeding untuk Green Impact Projects...")
    print("=" * 60)

    partners_and_projects = [
        {
            'partner': {'name': 'PT Energi Terbarukan Nusantara', 'type': 'Perusahaan Energi'},
            'project': {
                'title': 'Algoritma Optimasi Penempatan Panel Surya',
                'description': 'Buat algoritma machine learning yang dapat merekomendasikan lokasi paling optimal untuk instalasi panel surya di area perkotaan berdasarkan data citra satelit, data cuaca historis, dan sudut atap.'
            }
        },
        {
            'partner': {'name': 'Dinas Lingkungan Hidup Hijau', 'type': 'Pemerintah'},
            'project': {
                'title': 'Aplikasi Crowdsourcing Lapor Sampah Liar',
                'description': 'Kembangkan aplikasi mobile sederhana yang memungkinkan warga untuk melaporkan lokasi tumpukan sampah liar menggunakan GPS dan foto, lalu visualisasikan data tersebut di sebuah peta interaktif.'
            }
        },
        {
            'partner': {'name': 'Yayasan Konservasi Hutan Lestari', 'type': 'NGO Konservasi'},
            'project': {
                'title': 'Computer Vision untuk Menghitung Populasi Orangutan',
                'description': 'Gunakan model computer vision untuk menganalisis gambar dari drone dan secara otomatis menghitung serta mengidentifikasi individu orangutan untuk keperluan konservasi.'
            }
        }
    ]

    for item in partners_and_projects:
        partner_data = item['partner']
        project_data = item['project']

        # Cek atau buat Partner
        existing_partner = ProjectPartner.query.filter_by(name=partner_data['name']).first()
        if not existing_partner:
            print(f" -> Menambahkan Partner baru: '{partner_data['name']}'")
            new_partner = ProjectPartner(
                name=partner_data['name'],
                partner_type=partner_data['type']
            )
            db.session.add(new_partner)
            db.session.flush() # flush untuk mendapatkan ID
            partner_id = new_partner.id
        else:
            print(f" -> Partner '{partner_data['name']}' sudah ada.")
            partner_id = existing_partner.id
        
        # Cek atau buat Project
        existing_project = GreenProject.query.filter_by(title=project_data['title']).first()
        if not existing_project:
            print(f"    -> Menambahkan Proyek baru: '{project_data['title']}'")
            new_project = GreenProject(
                title=project_data['title'],
                description=project_data['description'],
                partner_id=partner_id
            )
            db.session.add(new_project)
        else:
            print(f"    -> Proyek '{project_data['title']}' sudah ada, dilewati.")

    # Commit semua perubahan untuk Projects
    db.session.commit()

    print("\n" + "=" * 60)
    print("✅ PROSES SEEDING GREEN TECH SELESAI! ✅")
    print("Hanya data Green Tech baru yang ditambahkan. Data lama Anda aman.")
    print("=" * 60)
