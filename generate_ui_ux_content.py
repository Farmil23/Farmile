# nama file: generate_uiux_content.py
import time
from app import create_app, db
from app.models import Lesson, Module
from flask import current_app
import re

app = create_app()

def clean_html_from_markdown(raw_html):
    """Membersihkan ```html, ```, dan tag markdown lainnya dari output AI."""
    cleaned_html = re.sub(r'^\s*```[a-zA-Z]*\n', '', raw_html)
    cleaned_html = re.sub(r'\n```\s*$', '', cleaned_html)
    return cleaned_html.strip()

def generate_uiux_content():
    """
    Script untuk men-generate konten materi HANYA UNTUK CAREER PATH 'ui-ux-designer'.
    """
    with app.app_context():
        local_ark_client = current_app.ark_client
        if not local_ark_client:
            print("❌ Klien AI tidak terinisialisasi.")
            return

        # Kueri Khusus: Hanya ambil materi dari career path 'ui-ux-designer'
        lessons_to_process = Lesson.query.join(Module).filter(
            Module.career_path == 'ui-ux-designer',
            (Lesson.content.is_(None) | (Lesson.content == ''))
        ).all()
        
        if not lessons_to_process:
            print("✅ Semua materi di jalur UI/UX Designer sudah memiliki konten.")
            return

        print(f"📚 Menemukan {len(lessons_to_process)} materi UI/UX yang perlu diisi kontennya. Memulai proses...")
        
        for i, lesson in enumerate(lessons_to_process, 1):
            print(f"[{i}/{len(lessons_to_process)}] Men-generate konten untuk: '{lesson.title}'...")
            
            try:
                # --- PROMPT KHUSUS UNTUK UI/UX DESIGNER ---
                prompt = f"""
                Anda adalah seorang Lead Product Designer di sebuah perusahaan teknologi ternama. Anda sangat ahli dalam menjelaskan konsep desain yang abstrak menjadi panduan yang praktis dan mudah diikuti.

                Tugas Anda adalah membuat materi pembelajaran yang mendalam dan visual untuk topik: "{lesson.title}".

                **PERSONA & GAYA PENULISAN:**
                -   **Visual dan Berbasis Contoh:** Gunakan analogi dari dunia nyata dan studi kasus dari aplikasi terkenal (misal: Gojek, Tokopedia, Spotify) untuk menjelaskan konsep.
                -   **Berorientasi pada Aksi:** Setiap penjelasan harus diikuti dengan tugas praktis atau "Latihan Coba Sendiri" yang bisa dilakukan pengguna di Figma.
                -   **Fokus pada "Mengapa":** Jelaskan alasan (reasoning) di balik setiap keputusan desain, bukan hanya "apa" yang harus dilakukan.

                **ATURAN OUTPUT (SANGAT KETAT):**
                1.  **HANYA FRAGMENT HTML**: Output HARUS berupa fragment HTML. JANGAN PERNAH menyertakan tag `<!DOCTYPE html>`, `<html>`, `<head>`, atau `<body>`. Mulai output langsung dari tag `<h3>`.
                2.  **Gunakan Tag Spesifik:** Gunakan `<h3>`, `<h4>`, `<p>`, `<ul>`, `<li>`, `<strong>`, dan `<blockquote>` untuk kutipan penting. JANGAN gunakan blok kode `<pre><code>`.

                **STRUKTUR KONTEN HTML (WAJIB DIIKUTI):**

                <h3>🚀 Pengantar: Memahami Esensi dari "{lesson.title}"</h3>
                <p>Mulailah dengan sebuah masalah umum yang sering dihadapi pengguna aplikasi dan bagaimana "{lesson.title}" adalah kunci untuk menyelesaikannya. Jelaskan secara singkat apa yang akan dipelajari dan mengapa skill ini sangat penting dalam proses desain produk digital.</p>

                <h3>🤔 Studi Kasus di Dunia Nyata</h3>
                <p>Gunakan contoh dari aplikasi populer untuk mengilustrasikan konsep "{lesson.title}". Misalnya, untuk topik "User Flow", Anda bisa menganalisis alur pemesanan makanan di aplikasi Gojek. Jelaskan bagaimana penerapan konsep yang baik (atau buruk) pada aplikasi tersebut mempengaruhi pengalaman pengguna.</p>
                
                <h3>⚙️ Konsep Inti & Prinsip Utama</h3>
                <p>Pecah topik "{lesson.title}" menjadi beberapa prinsip atau komponen utama menggunakan `<h4>`. Jelaskan setiap prinsip secara detail.</p>
                <h4>[Prinsip atau Komponen 1]</h4>
                <p>Penjelasan mendalam tentang komponen pertama.</p>
                <h4>[Prinsip atau Komponen 2]</h4>
                <p>Penjelasan mendalam tentang komponen kedua.</p>

                <h3>🎨 Latihan Praktis: Coba di Figma!</h3>
                <p>Berikan tugas atau latihan langkah demi langkah yang bisa diikuti oleh pengguna langsung di Figma. Buat instruksi yang sangat jelas.</p>
                <ul>
                    <li><strong>Langkah 1:</strong> Siapkan kanvas Anda di Figma dengan membuat frame baru (ukuran iPhone 14).</li>
                    <li><strong>Langkah 2:</strong> Buat sebuah komponen tombol sederhana menggunakan Auto Layout.</li>
                    <li><strong>Langkah 3:</strong> [Instruksi langkah praktis berikutnya...]</li>
                </ul>

                <h3>✅ Rangkuman & Checklist</h3>
                <h4>Poin Kunci untuk Diingat</h4>
                <ul>
                    <li>Poin rangkuman pertama: satu kalimat yang merangkum ide terbesar.</li>
                    <li>Poin rangkuman kedua.</li>
                </ul>
                <h4>Kesalahan Umum yang Harus Dihindari</h4>
                <ul>
                    <li>[Kesalahan 1]: Jelaskan kesalahan yang sering dilakukan pemula terkait topik ini.</li>
                    <li>[Kesalahan 2]: Jelaskan kesalahan lainnya.</li>
                </ul>
                <p>Akhiri dengan sebuah paragraf yang menghubungkan topik ini dengan materi selanjutnya dalam roadmap UI/UX, dan bagaimana skill ini akan digunakan dalam proyek portofolio mereka.</p>
                """

                completion = local_ark_client.chat.completions.create(
                    model=current_app.config['MODEL_ENDPOINT_ID'],
                    messages=[{"role": "user", "content": prompt}]
                )
                
                ai_response_html = clean_html_from_markdown(completion.choices[0].message.content)
                
                lesson.content = ai_response_html
                db.session.commit()
                
                print(f"   -> Sukses! Konten untuk '{lesson.title}' berhasil disimpan.")
                time.sleep(2)

            except Exception as e:
                print(f"   -> ❌ GAGAL saat men-generate konten untuk '{lesson.title}'. Error: {e}")
                db.session.rollback()
        
        print("\n🎉 Proses pembuatan konten untuk jalur UI/UX Designer selesai!")

if __name__ == '__main__':
    generate_uiux_content()