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
                
                PERSONA:
                - Anda terobsesi dengan "Cognitive Load Theory". Tujuan utama Anda adalah menyajikan informasi dengan cara yang meminimalkan beban kognitif bagi pembelajar.
                - Anda percaya pada "First Principles Thinking". Anda selalu mengurai konsep ke bagian paling fundamental sebelum membangunnya kembali.
                - Anda adalah seorang pendongeng. Anda menggunakan analogi dan narasi untuk membuat konsep teknis terasa hidup dan mudah diingat.

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
                <p>Mulailah dengan sebuah narasi singkat tentang masalah umum atau frustrasi yang sering dialami developer yang BELUM memahami '{lesson.title}'. Bangun empati. Kemudian, perkenalkan '{lesson.title}' sebagai prinsip atau alat yang membawa keteraturan dan solusi. Definisikan topik secara formal dan berikan pernyataan tesis yang jelas tentang apa yang akan dipelajari dan mengapa ini akan mengubah cara mereka bekerja.</p>
                <p>Jelaskan apa itu topik ini dan mengapa ini penting dan jelaskan materi ini yang sangat sesuai dengan kebutuhan industri sebagai expert</p>
                <li> disini jika ada list simpan disini jangan di p </li>
                <h4>Tujuan Pembelajaran (Learning Objectives)</h4>
                <ul>
                    <li>Setelah menyelesaikan materi ini, Anda akan mampu: [Tujuan 1, e.g., "Mendiagnosis masalah layout akibat box model yang salah"].</li>
                    <li>[Tujuan 2, e.g., "Mengimplementasikan layout tiga kolom yang fleksibel menggunakan Flexbox"].</li>
                    <li>[Tujuan 3, e.g., "Menganalisis dan memilih kapan harus menggunakan Grid daripada Flexbox"].</li>
                </ul>
                <h4>Prasyarat Pengetahuan</h4>
                <ul>
                    <li>Pemahaman dasar tentang: [Konsep 1, e.g., "Struktur dokumen HTML"].</li>
                    <li>Familiar dengan: [Konsep 2, e.g., "Sintaks dasar CSS"].</li>
                </ul>
                

                
                <h3>🤔 Analogi Sederhana</h3>
                <p>Jelaskan konsep inti menggunakan analogi dari dunia nyata dan jelaskan bagaimana cara kerjanya dengan sangat detail dan lengkap seperti expert</p>
                
                <h3>💻 Implementasi & Studi Kasus: Dari Konsep ke Kode</h3>
                <p>Sediakan blok kode yang bersih, diberi komentar, dan menunjukkan kasus penggunaan dunia nyata yang umum. Kode harus bisa langsung disalin-tempel dan dijalankan. Di bawah blok kode, berikan paragraf "Bedah Kode" yang menjelaskan baris-baris penting dan keputusan desain di baliknya.</p>

                <h3>Materi inti pada lesson "{lesson.title}"</h3>
                <p>Pecah menjadi beberapa poin utama. Jika ada rumus, gunakan LaTeX. Contoh: `\\( E=mc^2 \\)`.</p>
                
                <h3>💻 Contoh Kode Praktis atau Tabel Perbandingan</h3>
                <p>Jika topiknya tentang kode, berikan contoh dalam `<pre><code>`. Jika tentang konsep, buatlah tabel perbandingan.</p>
                
                <h3>💡 Laboratorium Mini: Eksperimen dan Verifikasi</h3>
                <h4>Tantangan</h4>
                <p>Berikan sebuah masalah kecil yang memaksa pembaca untuk menerapkan konsep inti yang baru saja dipelajari. Masalah harus dijelaskan dengan baik, lengkap dengan aset awal (jika perlu) dan deskripsi hasil akhir yang diharapkan.</p>
                <details>
                    <summary>Petunjuk Arah</summary>
                    <p>Berikan satu pertanyaan yang mengarahkan, bukan jawaban. Contoh: "Bagaimana jika Anda mencoba mengatur `justify-content` terlebih dahulu?"</p>
                </details>
                <details>
                    <summary>Solusi & Pembahasan Alur Pikir</summary>
                    <p>Tampilkan kode solusi. Di bawahnya, tulis paragraf "Mengapa Solusi Ini Berhasil?" yang menjelaskan alur berpikir logis, langkah demi langkah, dari masalah hingga solusi, merujuk kembali ke konsep-konsep di bagian "Materi Inti".</p>
                </details>

                <h3>✅ Rangkuman Eksekutif & Peta Jalan Selanjutnya</h3>
                <h4>Poin Kunci yang Wajib Diingat</h4>
                <ul>
                    <li>[Poin Kunci 1: Satu kalimat inti yang merangkum ide terbesar].</li>
                    <li>[Poin Kunci 2: Satu kalimat inti lainnya].</li>
                    <li>[Poin Kunci 3: Satu kalimat inti lainnya].</li>
                </ul>
                <h4>Kesalahan Umum yang Harus Dihindari (Common Pitfalls)</h4>
                <ul>
                    <li>[Kesalahan Umum 1, e.g., "Lupa bahwa margin bisa 'collapse' secara vertikal"].</li>
                    <li>[Kesalahan Umum 2, e.g., "Menggunakan `position: absolute` tanpa parent yang `relative`"].</li>
                </ul>
                <p>Akhiri dengan sebuah paragraf "Menghubungkan Titik-Titik" yang menjelaskan bagaimana penguasaan '{lesson.title}' akan menjadi fondasi penting untuk materi berikutnya yang lebih canggih (sebutkan contoh jika memungkinkan) dan bagaimana ini akan sering mereka temui dalam proyek-proyek profesional.</p>

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
