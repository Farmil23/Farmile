# File: app/seed_data.py

from . import db
from .models import GreenCareerPath, GreenModule, ProjectPartner, GreenProject

def seed_all():
    """Fungsi utama untuk menjalankan semua proses seeding."""
    print("Memulai proses seeding data...")
    seed_green_careers()
    seed_green_projects()
    print("\nProses seeding data telah selesai!")

def seed_green_careers():
    """Menambahkan data awal untuk Green Career Paths & Modules."""
    print("Mengecek dan menambahkan Green Career Paths...")
    
    try:
        # 1. Renewable Energy Engineer
        path1_slug = "renewable-energy-engineer"
        if not GreenCareerPath.query.filter_by(slug=path1_slug).first():
            path1 = GreenCareerPath(
                title="Renewable Energy Engineer",
                slug=path1_slug,
                description="Fokus pada desain, pengembangan, dan implementasi teknologi energi terbarukan seperti surya, angin, dan air untuk masa depan yang berkelanjutan."
            )
            db.session.add(path1)
            db.session.flush() # Mendapatkan ID path1 sebelum commit
            
            modules1 = [
                GreenModule(career_path_id=path1.id, order=1, title="Dasar-dasar Energi Terbarukan", description="Pengenalan panel surya, turbin angin, dan hidroelektrik."),
                GreenModule(career_path_id=path1.id, order=2, title="Manajemen Proyek Energi", description="Belajar merencanakan dan mengeksekusi proyek energi skala besar."),
                GreenModule(career_path_id=path1.id, order=3, title="Analisis Kebijakan Energi", description="Memahami regulasi pemerintah terkait energi bersih di Indonesia."),
            ]
            db.session.bulk_save_objects(modules1)
            print(f"-> Menambahkan '{path1.title}' beserta modulnya.")

        # 2. Sustainability Analyst
        path2_slug = "sustainability-analyst"
        if not GreenCareerPath.query.filter_by(slug=path2_slug).first():
            path2 = GreenCareerPath(
                title="Sustainability Analyst",
                slug=path2_slug,
                description="Menganalisis data untuk membantu perusahaan mengurangi jejak karbon, meningkatkan efisiensi, dan memenuhi standar lingkungan (ESG)."
            )
            db.session.add(path2)
            db.session.flush()
            
            modules2 = [
                GreenModule(career_path_id=path2.id, order=1, title="Pengantar ESG", description="Memahami pilar Environmental, Social, and Governance dalam bisnis."),
                GreenModule(career_path_id=path2.id, order=2, title="Analisis Jejak Karbon", description="Teknik mengukur dan menganalisis emisi gas rumah kaca perusahaan."),
                GreenModule(career_path_id=path2.id, order=3, title="Pelaporan Keberlanjutan", description="Menyusun laporan dampak lingkungan sesuai standar global."),
            ]
            db.session.bulk_save_objects(modules2)
            print(f"-> Menambahkan '{path2.title}' beserta modulnya.")
            
        # 3. Agri-Tech Specialist
        path3_slug = "agri-tech-specialist"
        if not GreenCareerPath.query.filter_by(slug=path3_slug).first():
            path3 = GreenCareerPath(
                title="Agri-Tech Specialist",
                slug=path3_slug,
                description="Mengembangkan dan menerapkan teknologi modern seperti IoT, drone, dan AI untuk menciptakan sistem pertanian yang lebih efisien dan berkelanjutan."
            )
            db.session.add(path3)
            db.session.flush()

            modules3 = [
                GreenModule(career_path_id=path3.id, order=1, title="Smart Farming & IoT", description="Menggunakan sensor untuk memantau kondisi tanah dan tanaman secara real-time."),
                GreenModule(career_path_id=path3.id, order=2, title="Pertanian Presisi", description="Pemanfaatan drone dan citra satelit untuk optimasi panen."),
                GreenModule(career_path_id=path3.id, order=3, title="Manajemen Rantai Pasok Pangan", description="Teknologi untuk melacak produk dari ladang hingga ke meja makan."),
            ]
            db.session.bulk_save_objects(modules3)
            print(f"-> Menambahkan '{path3.title}' beserta modulnya.")

        db.session.commit()
        print("Selesai menambahkan Green Career Paths.")
    except Exception as e:
        db.session.rollback()
        print(f"Error saat seeding green careers: {e}")


def seed_green_projects():
    """Menambahkan data awal untuk Project Partners & Green Projects."""
    print("\nMengecek dan menambahkan Project Partners & Green Projects...")
    
    try:
        # 1. Partner: Perusahaan Energi
        partner1_name = "PT Energi Terbarukan Nusantara"
        partner1 = ProjectPartner.query.filter_by(name=partner1_name).first()
        if not partner1:
            partner1 = ProjectPartner(
                name=partner1_name,
                partner_type="Perusahaan Energi",
                website="https://energinusantara.com"
            )
            db.session.add(partner1)
            print(f"-> Menambahkan Partner: '{partner1.name}'")

        # 2. Partner: Dinas Lingkungan Hidup
        partner2_name = "Dinas Lingkungan Hidup Hijau"
        partner2 = ProjectPartner.query.filter_by(name=partner2_name).first()
        if not partner2:
            partner2 = ProjectPartner(
                name=partner2_name,
                partner_type="Pemerintah",
                website="https://dlh.go.id"
            )
            db.session.add(partner2)
            print(f"-> Menambahkan Partner: '{partner2.name}'")
            
        db.session.commit() # Commit partner dulu untuk mendapatkan ID

        # Proyek 1
        project1_title = "Algoritma Optimasi Penempatan Panel Surya"
        if not GreenProject.query.filter_by(title=project1_title).first():
            project1 = GreenProject(
                title=project1_title,
                description="Buat algoritma machine learning yang dapat merekomendasikan lokasi paling optimal untuk instalasi panel surya di area perkotaan berdasarkan data citra satelit, data cuaca historis, dan sudut atap.",
                partner_id=partner1.id
            )
            db.session.add(project1)
            print(f"-> Menambahkan Proyek: '{project1.title}'")

        # Proyek 2
        project2_title = "Aplikasi Crowdsourcing Lapor Sampah Liar"
        if not GreenProject.query.filter_by(title=project2_title).first():
            project2 = GreenProject(
                title=project2_title,
                description="Kembangkan aplikasi mobile sederhana yang memungkinkan warga untuk melaporkan lokasi tumpukan sampah liar menggunakan GPS dan foto, lalu visualisasikan data tersebut di sebuah peta interaktif.",
                partner_id=partner2.id
            )
            db.session.add(project2)
            print(f"-> Menambahkan Proyek: '{project2.title}'")

        db.session.commit()
        print("Selesai menambahkan Green Projects.")
    except Exception as e:
        db.session.rollback()
        print(f"Error saat seeding green projects: {e}")