# nama file: generate_gen_ai_content.py
import time
import json
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

def generate_gen_ai_content():
    """
    Script untuk men-generate konten materi HANYA UNTUK CAREER PATH 'generative-ai'.
    """
    with app.app_context():
        local_ark_client = current_app.ark_client
        if not local_ark_client:
            print("❌ Klien AI tidak terinisialisasi. Pastikan ARK_API_KEY sudah benar di file .env Anda.")
            return

        # --- Kueri Khusus: Hanya ambil materi dari career path 'generative-ai' ---
        lessons_to_process = Lesson.query.join(Module).filter(
            Module.career_path == 'generative-ai',
            (Lesson.content.is_(None) | (Lesson.content == ''))
        ).all()
        
        if not lessons_to_process:
            print("✅ Semua materi di jalur Generative AI sudah memiliki konten.")
            return

        print(f"📚 Menemukan {len(lessons_to_process)} materi Generative AI yang perlu diisi kontennya. Memulai proses...")
        
        for i, lesson in enumerate(lessons_to_process, 1):
            print(f"[{i}/{len(lessons_to_process)}] Men-generate konten untuk: '{lesson.title}'...")
            
            try:
                # --- PROMPT FINAL DENGAN PENJELASAN KODE ---
                prompt = f"""
                Anda adalah seorang Distinguished AI Research Scientist & Educator dari sebuah laboratorium riset AI terkemuka (seperti Google DeepMind atau FAIR). Anda memiliki hasrat untuk mendemistifikasi konsep Generative AI yang kompleks dan membuatnya dapat diakses oleh generasi engineer berikutnya.

                Tugas Anda adalah membuat materi pembelajaran yang mendalam, berwawasan, dan sangat praktis untuk topik: "{lesson.title}".

                **FILOSOFI & GAYA PENULISAN:**
                -   **Clarity over Complexity:** Prioritaskan kejelasan dan intuisi. Gunakan bahasa yang sederhana untuk menjelaskan ide-ide yang rumit.
                -   **Intuition First, Formalism Second:** Selalu mulai dengan analogi atau penjelasan konseptual tingkat tinggi sebelum masuk ke detail teknis, matematika, atau kode.
                -   **Practicality is Key:** Setiap konsep harus dihubungkan dengan implementasi praktis menggunakan library modern (Hugging Face, LangChain, PyTorch/TensorFlow, Diffusers).
                -   **Visual Storytelling:** Gunakan diagram ASCII sederhana di dalam blok `<pre>` untuk memvisualisasikan arsitektur atau alur proses yang kompleks.

                **ATURAN OUTPUT (SANGAT KETAT):**
                1.  **HANYA FRAGMENT HTML**: Output HARUS berupa fragment HTML. JANGAN PERNAH menyertakan tag `<!DOCTYPE html>`, `<html>`, `<head>`, atau `<body>`. Mulai output Anda langsung dari tag `<h3>`.
                2.  **KODE YANG BERKUALITAS**: Semua contoh kode HARUS relevan, modern, dan bisa langsung dijalankan. Gunakan `<pre><code class="language-python">`.
                3.  **PENJELASAN KODE**: SETELAH SETIAP BLOK KODE `<pre><code>`, WAJIB tambahkan `<h4>Penjelasan Kode</h4>` diikuti dengan `<ul>` yang menjelaskan setiap baris atau bagian penting dari kode tersebut.
                4.  **TANPA CSS/MARKDOWN**: Jangan menyertakan style CSS inline atau markdown ````.

                **STRUKTUR KONTEN HTML (WAJIB DIIKUTI SECARA PRESISI):**

                <h3>🚀 Pengantar: Mengapa "{lesson.title}" Penting?</h3>
                <p>Mulailah dengan sebuah "hook" yang menarik—sebuah masalah atau pertanyaan yang memprovokasi pemikiran. Jelaskan mengapa topik ini menjadi pilar penting dalam ekosistem Generative AI saat ini dan apa terobosan yang dimungkinkannya.</p>
                
                <h3>🤔 Intuisi di Balik Konsep: Sebuah Analogi</h3>
                <p>Jelaskan ide inti di balik "{lesson.title}" menggunakan analogi yang NOVEL dan mudah dipahami. Urai analogi tersebut secara detail dan tunjukkan bagaimana setiap bagian dari analogi tersebut berhubungan dengan komponen teknisnya.</p>
                
                <h3>⚙️ Technical Deep Dive: Cara Kerjanya</h3>
                <p>Pecah konsep teknis menjadi beberapa sub-bagian yang logis menggunakan `<h4>`. Jelaskan setiap bagian secara terperinci dengan bahasa yang jelas.</p>

                <h3>💻 Implementasi Praktis: Dari Teori ke Kode</h3>
                <p>Tunjukkan cara mengimplementasikan konsep tersebut dengan contoh kode Python yang lengkap dan bisa langsung dijalankan. Berikan penjelasan detail untuk setiap blok kode.</p>
                <pre><code class="language-python">
# Tahap 1: Install library yang dibutuhkan
# !pip install -q transformers torch

from transformers import pipeline

# Tahap 2: Inisialisasi pipeline
generator = pipeline('text-generation', model='gpt2')

# Tahap 3: Jalankan inferensi
result = generator("Di dunia Generative AI, konsep yang paling penting adalah", max_length=50)

# Tahap 4: Tampilkan hasil
print(result[0]['generated_text'])
</code></pre>
                <h4>Penjelasan Kode</h4>
                <ul>
                    <li><strong>Baris 4:</strong> Kita mengimpor fungsi `pipeline` dari library `transformers` milik Hugging Face. Ini adalah cara termudah untuk menggunakan model-model canggih.</li>
                    <li><strong>Baris 7:</strong> Kita membuat sebuah `generator` dengan memanggil `pipeline('text-generation', model='gpt2')`. Ini memberitahu Hugging Face untuk memuat model 'gpt2' yang sudah dilatih untuk tugas generasi teks.</li>
                    <li><strong>Baris 10:</strong> Kita memanggil `generator` dengan teks awal (prompt) dan `max_length=50` untuk membatasi panjang output agar tidak terlalu panjang.</li>
                    <li><strong>Baris 13:</strong> Hasilnya adalah sebuah list, jadi kita mengakses elemen pertama `[0]` dan mengambil nilai dari kunci `'generated_text'` untuk mendapatkan teks lengkapnya.</li>
                </ul>

                <h3>💡 Mengapa Ini Penting? (Koneksi ke Dunia Nyata)</h3>
                <p>Jelaskan di mana konsep "{lesson.title}" digunakan di industri. Sebutkan 2-3 contoh produk atau fitur nyata yang menggunakan teknologi ini.</p>
                
                <h3>⚠️ Kesalahan Umum (Common Pitfalls)</h3>
                <p>Sebutkan 2-3 kesalahan umum yang sering dilakukan pemula saat bekerja dengan "{lesson.title}" dan berikan tips singkat tentang cara menghindarinya.</p>
                
                <h3>✅ Rangkuman & Langkah Selanjutnya</h3>
                <p>Akhiri dengan rangkuman poin-poin kunci dalam format `<ul>` dan paragraf penutup yang menghubungkan topik ini dengan materi selanjutnya.</p>
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
        
        print("\n🎉 Proses pembuatan konten untuk jalur Generative AI selesai!")

if __name__ == '__main__':
    generate_gen_ai_content()