from app import create_app, db
from app.models import Project

# Script ini hanya untuk debugging, aman untuk dijalankan.
# Tujuannya adalah untuk memeriksa isi kolom 'generated_content' di database.

app = create_app()

with app.app_context():
    print("--- Memeriksa Konten Proyek di Database ---")
    
    # Ambil semua proyek dari database
    all_projects = Project.query.all()
    
    if not all_projects:
        print("Tidak ada proyek yang ditemukan di database.")
    else:
        print(f"Menemukan {len(all_projects)} total proyek. Menganalisis konten...")
        print("-" * 40)
        
        projects_with_content = 0
        
        for project in all_projects:
            content_preview = ""
            status = ""
            
            # Periksa apakah kolom generated_content ada isinya
            if project.generated_content and project.generated_content.strip() != "":
                # Jika ada, ambil 100 karakter pertama sebagai preview
                content_preview = project.generated_content.strip()[:100].replace('\n', ' ') + "..."
                status = "✅ ADA KONTEN"
                projects_with_content += 1
            else:
                # Jika kosong atau None
                content_preview = "Tidak ada konten."
                status = "❌ KOSONG"
            
            print(f"ID Proyek: {project.id}")
            print(f"Judul    : {project.title}")
            print(f"Status   : {status}")
            print(f"Preview  : {content_preview}")
            print("-" * 40)
            
        print("\n--- Ringkasan ---")
        print(f"Total Proyek: {len(all_projects)}")
        print(f"Proyek dengan Konten: {projects_with_content}")
        print(f"Proyek Tanpa Konten : {len(all_projects) - projects_with_content}")
        print("Pemeriksaan selesai.")