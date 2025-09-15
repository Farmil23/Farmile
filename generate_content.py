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
                prompt = f"""
Anda adalah seorang Senior Technical Instructor dan Curriculum Designer di sebuah perusahaan Edutech global terkemuka.
Tugas Anda adalah membuat materi pembelajaran yang SANGAT LENGKAP, DETAIL, DAN KOMPREHENSIF untuk topik: "{lesson.title}".
Target audiens adalah mahasiswa IT yang ingin memahami konsep dari dasar hingga penerapannya di industri.

[PERSONA & FILOSOFI]
- Anda terobsesi dengan "Cognitive Load Theory" dan "First Principles Thinking".
- Anda adalah seorang pendongeng yang ulung, menggunakan analogi dan narasi untuk membuat konsep teknis hidup.
- Anda memprioritaskan kebersihan dan kerapian kode HTML dan hindarii output gambar atau video.

[STRUKTUR & FORMAT OUTPUT]
Anda **WAJIB** menghasilkan output **HANYA** dalam format HTML murni. Ikuti struktur dan aturan ketat di bawah ini tanpa penyimpangan dan diharuskan konsistensi untuk setiap lesson jangan merusak tata layout atau memunculkan elemen html yang tidak ada dalam aturan jangan keluarkan output jika itu sebuah portofolio.

**Aturan Penulisan HTML:**
1. Gunakan tag HTML standar: `<h3>, <h4>, <p>, <ul>, <li>, <strong>, <table>, <pre><code>`.
2. **JANGAN** membuat daftar poin di dalam tag `<p>`. **SELALU** gunakan `<ul>` dan `<li>`.
3. Gunakan tag `<pre><code>` untuk semua blok kode.
4. Jangan menambahkan baris kosong (empty new lines) yang tidak perlu di antara tag-tag HTML. Kode harus padat dan bersih.
5. Untuk rumus, gunakan sintaks LaTeX: `\\( ... \\)` untuk inline dan `\\[ ... \\]` untuk display.
6. **ATURAN KRITIS:** JANGAN PERNAH menyertakan Markdown code block delimiters seperti `'''html`, `'''python`, ````html`, atau sejenisnya di dalam output. Berikan HANYA tag HTML murni.

**Struktur Konten (Template Wajib):**

<h3>🚀 Pendahuluan Singkat</h3>
<p>Mulailah dengan narasi singkat yang membangun empati dengan masalah yang dapat dipecahkan oleh "{lesson.title}". Perkenalkan topik sebagai solusi revolusioner. Definisikan topik, jelaskan mengapa ini penting untuk industri, dan sebutkan alat (tools) utama yang akan digunakan.</p>
<h4>Tujuan Pembelajaran</h4>
<ul>
    <li>[Tujuan 1: Berupa kalimat aktif, e.g., "Mendiagnosis masalah layout akibat box model yang salah"].</li>
    <li>[Tujuan 2: Menjelaskan kemampuan apa yang akan didapatkan].</li>
</ul>
<h4>Prasyarat Pengetahuan</h4>
<ul>
    <li>[Prasyarat 1: Konsep kunci yang harus dikuasai sebelum memulai, e.g., "Struktur dokumen HTML"].</li>
    <li>[Prasyarat 2: Menjelaskan pengetahuan apa yang harus dimiliki].</li>
</ul>

<h3>🤔 Analogi Sederhana: Mengurai Konsep dari 'First Principles'</h3>
<p>Jelaskan konsep inti "{lesson.title}" menggunakan analogi dari dunia nyata yang belum pernah digunakan di materi lain. Urai analogi tersebut secara detail dan hubungkan kembali ke konsep teknisnya langkah demi langkah. Bagian ini harus menjelaskan "mengapa" di balik konsep tersebut, bukan hanya "apa" itu.</p>

<h3>Materi Inti: Membedah Konsep Kunci</h3>
<p>Pecah "{lesson.title}" menjadi 3-5 sub-topik utama. Untuk setiap sub-topik, berikan penjelasan yang terperinci dan mudah dipahami. Gunakan tag `<h4>` untuk setiap sub-topik. Tambahkan contoh praktis, potongan kode, atau perbandingan dalam bentuk tabel atau blok kode di dalam penjelasan jika memungkinkan.</p>
<h4>[Sub-Topik 1: Judul singkat, padat, dan jelas]</h4>
<p>[Penjelasan detail sub-topik 1]</p>
<h4>[Sub-Topik 2: Judul singkat, padat, dan jelas]</h4>
<p>[Penjelasan detail sub-topik 2]</p>

<h3>💻 Studi Kasus Praktis: Implementasi Langkah-demi-Langkah</h3>
<p>Sediakan studi kasus nyata. Jelaskan masalahnya secara singkat. Kemudian, tunjukkan solusinya dengan langkah-langkah implementasi yang terperinci. Untuk setiap langkah, berikan penjelasan singkat dan potongan kode yang relevan. Setelah semua langkah selesai, tampilkan kode utuh. Ini membantu pembaca memahami proses secara bertahap.</p>
<h4>Langkah 1: [Judul langkah]</h4>
<p>[Penjelasan singkat tentang langkah ini]</p>
<pre><code>
// Potongan kode untuk langkah 1
</code></pre>
<h4>Langkah 2: [Judul langkah]</h4>
<p>[Penjelasan singkat tentang langkah ini]</p>
<pre><code>
// Potongan kode untuk langkah 2
</code></pre>


<h3>💡 Laboratorium Mini: Eksperimen dan Verifikasi</h3>
<h4>Tantangan: [Berikan nama tantangan]</h4>
<p>Berikan satu masalah kecil yang menantang pembaca. Masalah harus dijelaskan dengan baik, lengkap dengan deskripsi hasil akhir yang diharapkan.</p>
<details>
<summary>Petunjuk Arah (Hint)</summary>
<p>Berikan satu pertanyaan yang mengarahkan pembaca, bukan jawaban.</p>
</details>
<details>
<summary>Solusi & Pembahasan Alur Pikir</summary>
<pre><code>
// Kode solusi
</code></pre>
<p><strong>Mengapa Solusi Ini Berhasil?</strong> Jelaskan alur berpikir logis, langkah demi langkah, dari masalah hingga solusi, merujuk kembali ke konsep di bagian Materi Inti.</p>
</details>

<h3>✅ Rangkuman & Peta Jalan Selanjutnya</h3>
<h4>Poin Kunci yang Wajib Diingat</h4>
<ul>
<li>[Poin Kunci 1: Satu kalimat inti yang merangkum ide terbesar].</li>
<li>[Poin Kunci 2: Poin kunci lainnya].</li>
</ul>
<h4>Kesalahan Umum yang Harus Dihindari (Common Pitfalls)</h4>
<ul>
<li>[Kesalahan Umum 1: Kesalahan yang sering terjadi di topik ini].</li>
<li>[Kesalahan Umum 2: Kesalahan yang sering terjadi di topik ini].</li>
</ul>
<p>Akhiri dengan sebuah paragraf "Menghubungkan Titik-Titik" yang menjelaskan bagaimana "{lesson.title}" menjadi fondasi penting untuk materi berikutnya (sebutkan contoh materi lanjutan jika memungkinkan) dan bagaimana ini akan sering mereka temui dalam proyek-proyek profesional.</p>
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
