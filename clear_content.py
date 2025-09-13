from app import create_app, db
from app.models import Lesson

# Daftar judul lesson yang kontennya ingin Anda hapus
lessons_to_clear = [
    "Manajemen Konfigurasi dengan ConfigMap & Secret"
]

app = create_app()

with app.app_context():
    # Cari lesson berdasarkan judul di dalam daftar
    lessons = Lesson.query.filter(Lesson.title.in_(lessons_to_clear)).all()
    
    if not lessons:
        print("Tidak ada lesson yang ditemukan dengan judul tersebut.")
    else:
        print(f"Ditemukan {len(lessons)} lesson untuk dihapus kontennya:")
        for lesson in lessons:
            print(f"- Menghapus konten dari: {lesson.title}")
            lesson.content = None  # Setel konten menjadi kosong (None)
        
        db.session.commit()
        print("\n✅ Konten berhasil dihapus dari database.")