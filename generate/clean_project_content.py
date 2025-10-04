import re
from app import create_app, db
from app.models import Project

# Script ini untuk membersihkan konten yang sudah ada di database.

app = create_app()

with app.app_context():
    print("--- Memulai Proses Pembersihan Konten Proyek ---")
    
    # Ambil semua proyek yang memiliki konten
    projects_to_clean = Project.query.filter(Project.generated_content.isnot(None)).all()
    
    cleaned_count = 0
    for project in projects_to_clean:
        if project.generated_content and project.generated_content.strip().startswith('<!DOCTYPE html'):
            # Gunakan regular expression untuk mengekstrak hanya konten di dalam <body>
            body_content_match = re.search(r'<body[^>]*>(.*)</body>', project.generated_content, re.DOTALL)
            
            if body_content_match:
                cleaned_html = body_content_match.group(1).strip()
                project.generated_content = cleaned_html
                print(f"✅ Membersihkan konten untuk Proyek ID: {project.id} ('{project.title}')")
                cleaned_count += 1
            else:
                print(f"⚠️  Konten untuk Proyek ID: {project.id} tidak memiliki tag <body>, dilewati.")

    if cleaned_count > 0:
        db.session.commit()
        print(f"\n🎉 Berhasil membersihkan dan menyimpan {cleaned_count} konten proyek.")
    else:
        print("\nℹ️  Tidak ada konten yang perlu dibersihkan.")