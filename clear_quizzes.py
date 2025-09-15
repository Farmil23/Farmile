from app import create_app, db
from app.models import Lesson

# Daftar judul lesson yang kuisnya ingin Anda hapus
lessons_to_clear_quiz = [
    "Cara Kerja Web & Internet",
    "HTML Fundamental: Struktur & Elemen Dasar",
    # Tambahkan judul-judul pelajaran lain di sini jika diperlukan
]

app = create_app()

with app.app_context():
    print("Mencari lesson untuk menghapus konten kuis...")
    
    # Cari lesson berdasarkan judul di dalam daftar
    lessons = Lesson.query.filter(Lesson.title.in_(lessons_to_clear_quiz)).all()
    
    if not lessons:
        print("Tidak ada lesson yang ditemukan dengan judul tersebut.")
    else:
        print(f"Ditemukan {len(lessons)} lesson untuk dihapus konten kuisnya:")
        for lesson in lessons:
            print(f"- Menghapus kuis dari: {lesson.title}")
            lesson.quiz = None  # Setel konten kuis menjadi kosong (None)
        
        db.session.commit()
        print("\n✅ Konten kuis berhasil dihapus dari database.")