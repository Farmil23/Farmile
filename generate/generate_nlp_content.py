# nama file: generate_nlp_content.py
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

def generate_nlp_content():
    """
    Script untuk men-generate konten materi HANYA UNTUK CAREER PATH 'nlp-engineer'.
    """
    with app.app_context():
        local_ark_client = current_app.ark_client
        if not local_ark_client:
            print("❌ Klien AI tidak terinisialisasi.")
            return

        # Kueri Khusus: Hanya ambil materi dari career path 'nlp-engineer'
        lessons_to_process = Lesson.query.join(Module).filter(
            Module.career_path == 'nlp-engineer',
            (Lesson.content.is_(None) | (Lesson.content == ''))
        ).all()
        
        if not lessons_to_process:
            print("✅ Semua materi di jalur NLP Engineer sudah memiliki konten.")
            return

        print(f"📚 Menemukan {len(lessons_to_process)} materi NLP yang perlu diisi kontennya. Memulai proses...")
        
        for i, lesson in enumerate(lessons_to_process, 1):
            print(f"[{i}/{len(lessons_to_process)}] Men-generate konten untuk: '{lesson.title}'...")
            
            try:
                # --- PROMPT KHUSUS UNTUK NLP ENGINEER (DIPERBAIKI) ---
                prompt = f"""
                Anda adalah seorang Applied Scientist spesialis NLP di sebuah perusahaan teknologi besar. Anda memiliki pengalaman membangun dan mendeploy sistem NLP skala besar, dari search engine hingga chatbots. Anda sangat ahli dalam menerjemahkan teori riset menjadi solusi praktis.

                Tugas Anda adalah membuat materi pembelajaran yang mendalam dan relevan dengan industri untuk topik: "{lesson.title}".

                **PERSONA & GAYA PENULISAN:**
                -   **Relevansi Industri:** Selalu mulai dengan menjelaskan MENGAPA topik ini penting dan DI MANA ia digunakan di industri (contoh: "Klasifikasi teks adalah tulang punggung dari sistem filtering spam di Gmail...").
                -   **Intuisi & Visualisasi:** Gunakan analogi dan diagram ASCII sederhana untuk menjelaskan konsep-konsep seperti 'attention' atau 'vector space'.
                -   **Hands-on & Tool-Oriented:** Fokus pada implementasi praktis menggunakan library standar industri seperti Hugging Face Transformers, spaCy, NLTK, dan Scikit-learn.

                **ATURAN OUTPUT (SANGAT KETAT):**
                1.  **HANYA FRAGMENT HTML**: Output HARUS berupa fragment HTML. JANGAN PERNAH menyertakan tag `<!DOCTYPE html>`, `<html>`, `<head>`, atau `<body>`. Mulai output langsung dari tag `<h3>`.
                2.  **KODE PYTHON UNTUK NLP**: Semua contoh kode HARUS dalam bahasa Python dan menggunakan library yang relevan. Gunakan `<pre><code class="language-python">`.
                3.  **PENJELASAN KODE**: Setelah setiap blok kode, WAJIB tambahkan `<h4>Penjelasan Kode</h4>` dan `<ul>` yang menjelaskan logika di balik kode tersebut.

                **STRUKTUR KONTEN HTML (WAJIB DIIKUTI):**

                <h3>🚀 Misi: Menguasai "{lesson.title}" untuk Aplikasi Nyata</h3>
                <p>Mulailah dengan menjelaskan masalah nyata yang bisa dipecahkan dengan menguasai "{lesson.title}". Berikan contoh 1-2 aplikasi terkenal yang menggunakan teknologi ini sebagai intinya.</p>

                <h3>🤔 Intuisi di Balik Konsep</h3>
                <p>Jelaskan ide utama di balik "{lesson.title}" menggunakan analogi. Contoh: "Bayangkan Word Embeddings seperti memberikan setiap kata sebuah koordinat di peta makna...". Jelaskan mengapa pendekatan ini lebih baik dari metode sebelumnya.</p>
                
                <h3>⚙️ Cara Kerja Teknis & Algoritma Kunci</h3>
                <p>Pecah konsep teknis menjadi beberapa sub-bagian menggunakan `<h4>`. Jelaskan algoritma atau arsitektur utamanya.</p>
                <h4>[Sub-Topik Teknis 1: Contoh: Representasi Teks]</h4>
                <p>Penjelasan detail tentang TF-IDF, BoW, atau Embeddings.</p>
                <h4>[Sub-Topik Teknis 2: Contoh: Arsitektur Model]</h4>
                <p>Penjelasan detail tentang arsitektur seperti LSTM atau Transformer.</p>

                <h3>💻 Implementasi Praktis dengan Hugging Face/spaCy</h3>
                <p>Tunjukkan cara mengimplementasikan konsep tersebut dengan contoh kode Python yang bisa langsung dijalankan.</p>
                <pre><code class="language-python">
# Install library yang dibutuhkan
# !pip install -q transformers torch

from transformers import pipeline

# Inisialisasi pipeline untuk tugas yang relevan
classifier = pipeline('sentiment-analysis')

# Contoh penggunaan
text = "Farmile adalah platform belajar AI yang luar biasa!"
result = classifier(text)

# Menampilkan hasil dengan cara yang aman untuk f-string
print("Teks:", text)
print("Hasil Analisis:", result)
</code></pre>
                <h4>Penjelasan Kode</h4>
                <ul>
                    <li><strong>Baris 4:</strong> Kita mengimpor fungsi `pipeline` dari library `transformers`, cara termudah untuk mengakses model-model canggih.</li>
                    <li><strong>Baris 7:</strong> Kita menginisialisasi `pipeline` untuk tugas 'sentiment-analysis'. Hugging Face akan otomatis mengunduh model default yang cocok untuk tugas ini.</li>
                    <li><strong>Baris 10-11:</strong> Kita menjalankan analisis pada sebuah contoh teks dan menyimpan hasilnya.</li>
                    <li><strong>Baris 14-15:</strong> Kita mencetak hasil analisis yang terstruktur. Hasilnya adalah sebuah list yang berisi dictionary dengan 'label' (POSITIVE/NEGATIVE) dan 'score' kepercayaan.</li>
                </ul>

                <h3>⚠️ Tantangan & Keterbatasan di Dunia Nyata</h3>
                <p>Jelaskan 1-2 tantangan praktis saat mengimplementasikan teknologi ini di industri. Contoh: "Meskipun BERT sangat kuat, ia membutuhkan sumber daya komputasi yang besar untuk fine-tuning" atau "Menangani bahasa gaul dan typo adalah tantangan utama dalam analisis sentimen."</p>

                <h3>✅ Rangkuman & Checklist untuk Engineer</h3>
                <h4>Poin Kunci</h4>
                <ul>
                    <li>Poin rangkuman teknis pertama yang paling penting.</li>
                    <li>Poin rangkuman kedua yang relevan dengan implementasi.</li>
                </ul>
                <p>Akhiri dengan sebuah paragraf yang menghubungkan skill ini dengan peran seorang NLP Engineer dan bagaimana ini akan menjadi fondasi untuk materi selanjutnya seperti membangun sistem dialog atau machine translation.</p>
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
        
        print("\n🎉 Proses pembuatan konten untuk jalur NLP Engineer selesai!")

if __name__ == '__main__':
    generate_nlp_content()