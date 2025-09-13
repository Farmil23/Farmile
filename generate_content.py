import time
from app import create_app, db
from app.models import Lesson
from flask import current_app

app = create_app()

def generate_and_save_content():
    """
    Script untuk men-generate konten materi dalam format HTML murni,
    termasuk dukungan untuk tabel dan rumus matematika (LaTeX).
    """
    with app.app_context():
        local_ark_client = current_app.ark_client
        if not local_ark_client:
            print("❌ Klien AI tidak terinisialisasi. Pastikan ARK_API_KEY sudah benar di file .env Anda.")
            return

        lessons_to_process = Lesson.query.filter(Lesson.content.is_(None) | (Lesson.content == '')).all()
        
        if not lessons_to_process:
            print("✅ Semua materi sudah memiliki konten. Tidak ada yang perlu digenerate.")
            return

        print(f"📚 Menemukan {len(lessons_to_process)} materi yang perlu diisi kontennya. Memulai proses...")
        
        for i, lesson in enumerate(lessons_to_process, 1):
            print(f"[{i}/{len(lessons_to_process)}] Men-generate konten HTML untuk: '{lesson.title}'...")
            
            try:
                # Prompt final dengan instruksi kebersihan kode
                prompt = f"""
                Anda adalah seorang Senior Technical Instructor dan Curriculum Designer di sebuah perusahaan Edutech global terkemuka.
                Tugas Anda adalah membuat materi pembelajaran yang SANGAT LENGKAP, DETAIL, DAN KOMPREHENSIF untuk topik: "{lesson.title}".
                Target audiens adalah mahasiswa IT yang ingin memahami konsep dari dasar hingga penerapannya di industri.

                Anda WAJIB menghasilkan output hanya dalam format HTML murni dan setiap lesson memiliki format yang sama dan konsisten, tidak ada perbedaan diantara lesson hanya materi yang berbeda.
                
                
                Gunakan tag HTML standar: <h3>, <p>, <ul>, <li>, <strong>, dan <pre><code>.

                **ATURAN PENTING**: JANGAN tambahkan baris kosong (empty new lines) yang tidak perlu di antara elemen-elemen HTML. Buat kode HTML yang rapat dan bersih.
                
                **ATURAN STRUKTUR HTML (SANGAT PENTING):**
                1.  **JANGAN** membuat daftar bernomor di dalam satu tag `<p>`.
                2.  **SELALU** gunakan tag `<ul>` dan `<li>` untuk membuat daftar poin.
                3. jika sudah ada li, jangan gunakan li::marked

                **KEMAMPUAN TAMBAHAN:**
                1.  **Tabel**: Jika perlu, gunakan tag `<table>`, `<thead>`, `<tbody>`, `<tr>`, `<th>`, dan `<td>`.
                2.  **Rumus Matematika**: Jika perlu, tulis rumus menggunakan sintaks LaTeX. Gunakan `\\( ... \\)` untuk inline dan `\\[ ... \\]` untuk display.

                Struktur HTML yang harus Anda hasilkan adalah sebagai berikut:
                
                <h3>🚀 Pendahuluan Singkat</h3>
                <p>Jelaskan tools apa saja yang akan digunakan nanti saat latihan dan juga jelaskan singkat tentang tools ini</p>
                <p>Jelaskan apa itu topik ini dan mengapa ini penting dan jelaskan materi ini yang sangat sesuai dengan kebutuhan industri sebagai expert</p>
                <li> disini jika ada list simpan disini jangan di p </li>
                
                <h3>🤔 Analogi Sederhana</h3>
                <p>Jelaskan konsep inti menggunakan analogi dari dunia nyata dan jelaskan bagaimana cara kerjanya dengan sangat detail dan lengkap seperti expert</p>

                <h3>Materi inti pada lesson "{lesson.title}"</h3>
                <p>Pecah menjadi beberapa poin utama. Jika ada rumus, gunakan LaTeX. Contoh: `\\( E=mc^2 \\)`.</p>
                
                <h3>💻 Contoh Kode Praktis atau Tabel Perbandingan</h3>
                <p>Jika topiknya tentang kode, berikan contoh dalam `<pre><code>`. Jika tentang konsep, buatlah tabel perbandingan.</p>
                
                <h3>💡 Tantangan Mini</h3>
                <p>Buat satu soal latihan kecil dan latihan ini harus sesuai dengan materi yanga sudah diberikan dan kasih pengetahuan dimana, tools yang akan digunakan apa dan bagaimana cara mengerjakannya</p>
                <details>
                    <summary>Lihat Solusi</summary>
                    <p>Solusi tantangan di sini jelaskan dengan lengkap, jika ada code berikan saja codenya dengan format yang sesuai.</p>
                </details>

                <h3>✅ Kesimpulan</h3>
                <p>Rangkum poin-poin kunci.</p>
                """

                completion = local_ark_client.chat.completions.create(
                    model=current_app.config['MODEL_ENDPOINT_ID'],
                    messages=[{"role": "user", "content": prompt}]
                )
                
                ai_response_html = completion.choices[0].message.content.strip()
                
                lesson.content = ai_response_html
                db.session.commit()
                
                print(f"   -> Sukses! Konten HTML untuk '{lesson.title}' berhasil disimpan.")
                time.sleep(1)

            except Exception as e:
                print(f"   -> ❌ GAGAL saat men-generate konten untuk '{lesson.title}'. Error: {e}")
                db.session.rollback()
        
        print("\n🎉 Proses pembuatan konten HTML selesai!")

if __name__ == '__main__':
    generate_and_save_content()
