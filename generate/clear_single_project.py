from app import create_app, db
from app.models import Project

# -----------------------------------------------------------
# GANTI JUDUL DI BAWAH INI DENGAN JUDUL PROYEK YANG INGIN DIHAPUS KONTENNYA
# Pastikan judulnya sama persis seperti yang ada di database.
# -----------------------------------------------------------
project_title_to_clear = "API Blog (CRUD) dengan PostgreSQL"
# -----------------------------------------------------------

app = create_app()

with app.app_context():
    print(f"--- Mencari proyek dengan judul: '{project_title_to_clear}' ---")
    
    # Cari proyek berdasarkan judul yang spesifik
    project = Project.query.filter_by(title=project_title_to_clear).first()
    
    if not project:
        print(f"❌ GAGAL: Proyek dengan judul tersebut tidak ditemukan di database.")
    elif not project.generated_content:
        print(f"ℹ️  INFO: Konten untuk proyek '{project.title}' memang sudah kosong.")
    else:
        print(f"✅ Ditemukan! Menghapus konten dari proyek: '{project.title}' (ID: {project.id})")
        # Setel kolom generated_content menjadi kosong (None)
        project.generated_content = None
        
        db.session.commit()
        print("\n🎉 Konten proyek berhasil dihapus dari database.")