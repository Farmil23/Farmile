# nama file: generate/generate_llm_research_content.py
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

def generate_llm_research_content():
    """
    (Versi Upgrade)
    Script untuk men-generate konten HANYA UNTUK CAREER PATH 'llm-research-papers'.
    Fokusnya adalah membedah paper secara mendalam dan memberikan ide skripsi/tesis.
    """
    with app.app_context():
        local_ark_client = current_app.ark_client
        if not local_ark_client:
            print("❌ Klien AI tidak terinisialisasi. Pastikan ARK_API_KEY sudah benar di file .env Anda.")
            return

        # --- Kueri Khusus: Hanya ambil materi dari career path 'llm-research-papers' ---
        lessons_to_process = Lesson.query.join(Module).filter(
            Module.career_path == 'llm-research-papers', # <-- Kunci yang sama
            (Lesson.content.is_(None) | (Lesson.content == ''))
        ).all()
        
        if not lessons_to_process:
            print("✅ Semua materi di jalur 'LLM Research Papers' sudah memiliki konten.")
            return

        print(f"📚 Menemukan {len(lessons_to_process)} materi 'LLM Research Papers' yang perlu diisi kontennya. Memulai proses...")
        
        for i, lesson in enumerate(lessons_to_process, 1):
            print(f"[{i}/{len(lessons_to_process)}] Men-generate konten untuk: '{lesson.title}'...")
            
            try:
                # --- PROMPT UPGRADE UNTUK ANALISIS MENDALAM & IDE TESIS ---
                prompt = f"""
                Anda adalah seorang Senior Research Scientist dan Pembimbing Tesis/Disertasi (PhD Advisor) di bidang AI/ML. Anda sangat ahli dalam membedah paper 'State-of-the-Art' (SOTA).
                
                Tugas Anda adalah membuat materi pembelajaran komprehensif yang membedah paper berjudul: "{lesson.title}".

                Audiens adalah mahasiswa tingkat akhir atau S2 yang sedang mencari topik riset. Materi Anda harus teknis, mendalam, dan yang terpenting, memicu ide-ide riset baru.

                **FILOSOFI & GAYA PENULISAN:**
                -   **Kekakuan Teknis (Technical Rigor):** Jangan menyederhanakan secara berlebihan. Jelaskan arsitektur, fungsi kerugian (loss function), atau algoritma inti.
                -   **Intuisi Matematis:** Jika ada konsep matematika inti (misal: 'dot-product attention'), berikan intuisi di baliknya.
                -   **Kesadaran SOTA:** Selalu posisikan paper ini dalam konteks: "Apa yang ada sebelumnya?" dan "Apa yang diinspirasinya sesudahnya?"

                **ATURAN OUTPUT (SANGAT KETAT):**
                1.  **HANYA FRAGMENT HTML**: Output HARUS berupa fragment HTML. JANGAN PERNAH menyertakan tag `<!DOCTYPE html>`, `<html>`, `<head>`, atau `<body>`. Mulai output Anda langsung dari tag `<h3>`.
                2.  **KODE (Jika Ada):** Gunakan `<pre><code class="language-python">` untuk pseudocode atau cuplikan implementasi kunci.
                3.  **TANPA CSS/MARKDOWN**: Jangan menyertakan style CSS inline atau markdown ````.

                **STRUKTUR KONTEN HTML (WAJIB DIIKUTI SECARA PRESISI):**

                <h3>Ringkasan Eksekutif & Konteks Riset</h3>
                <p>Mulai dengan 2-3 paragraf: Apa masalah (problem gap) yang ada *sebelum* paper '{lesson.title}' ini muncul? Apa kontribusi ilmiah (scientific contribution) utama yang mereka ajukan? Dan mengapa paper ini dianggap penting (impactful)?</p>
                
                <h3>🔬 Bedah Teknis Mendalam & Kontribusi Ilmiah</h3>
                <p>Ini adalah inti dari materi. Uraikan 3-4 kontribusi teknis utama. Gunakan `<h4>` untuk setiap sub-bagian. Jelaskan secara detail.</p>
                
                <h4>1. [Kontribusi Kunci Pertama, misal: 'Arsitektur Encoder-Decoder Cross-Attention']</h4>
                <p>Penjelasan mendalam tentang arsitektur ini. Bagaimana data mengalir? Apa bedanya dengan arsitektur sebelumnya?</p>
                
                <h4>2. [Kontribusi Kunci Kedua, misal: 'Mekanisme Scaled Dot-Product Attention']</h4>
                <p>Jelaskan formula intinya (jika ada). Mengapa 'scaled' itu penting? Berikan intuisi di balik Q, K, V (Query, Key, Value).</p>
                <pre>
                Attention(Q, K, V) = softmax( (Q * K^T) / sqrt(d_k) ) * V
                </pre>
                
                <h4>3. [Kontribusi Kunci Ketiga, misal: 'Metodologi Pre-training/Fine-tuning']</h4>
                <p>Jelaskan bagaimana model ini dilatih. Apa datasetnya? Apa objective function (misal: Masked Language Model, Causal Language Model)?</p>

                <h3>🔥 5 Ide Topik Riset (Skripsi/Tesis) Mendalam</h3>
                <p>Ini adalah bagian terpenting. Berikan 5 ide topik riset yang konkret, spesifik, dan *dapat dikerjakan* (feasible) oleh mahasiswa, yang terinspirasi langsung dari paper ini. Gunakan format list `<ul>` dengan struktur detail.</p>
                
                <ul>
                    <li>
                        <strong>Judul Topik 1:</strong> [Contoh: "Adaptasi Arsitektur [NAMA DARI PAPER] untuk Deteksi Sarkasme Kontekstual pada Ulasan Berbahasa Indonesia"]
                        <br>
                        <strong>Rumusan Masalah:</strong> [Jelaskan mengapa sarkasme sulit dan mengapa model ini mungkin cocok].
                        <br>
                        <strong>Metodologi yang Diusulkan:</strong> [Jelaskan dataset (misal: dari Twitter/Tokopedia), baseline model (misal: IndoBERT), dan bagaimana model dari paper ini akan diadaptasi].
                        <br>
                        <strong>Tantangan & Ruang Lingkup:</strong> [Sebutkan tantangan (misal: data labeling) dan batasi ruang lingkup (misal: fokus hanya pada 1 domain ulasan)].
                    </li>
                    <li>
                        <strong>Judul Topik 2:</strong> [Contoh: "Analisis Efisiensi Parameter: Studi Komparatif Metode LoRA vs QLoRA pada Fine-Tuning Model [NAMA MODEL] untuk Tugas Klasifikasi Teks Hukum"]
                        <br>
                        <strong>Rumusan Masalah:</strong> [Fine-tuning model besar mahal. Paper ini menawarkan efisiensi. Seberapa efisien perbandingannya pada kasus spesifik (hukum)?].
                        <br>
                        <strong>Metodologi yang Diusulkan:</strong> [Gunakan dataset teks hukum Indonesia. Lakukan fine-tuning dengan 3 metode: Full fine-tuning, LoRA, QLoRA. Bandingkan metrik (Akurasi, F1) vs. Waktu Training vs. Penggunaan Memori GPU].
                        <br>
                        <strong>Tantangan & Ruang Lingkup:</strong> [Tantangannya adalah setup environment yang konsisten untuk perbandingan. Ruang lingkup: 1 model dasar (misal: Llama 2 7B) dan 1 dataset].
                    </li>
                    <li>
                        <strong>Judul Topik 3:</strong> [Contoh: "Penerapan Retrieval-Augmented Generation (RAG) Menggunakan [TEKNIK DARI PAPER] untuk Sistem Tanya Jawab (Q&A) Dokumen Akademik Internal"]
                        <br>
                        <strong>Rumusan Masalah:</strong> [LLM sering 'halusinasi'. RAG adalah solusi. Bagaimana implementasi RAG yang optimal untuk korpus dokumen akademik (PDF) internal universitas?].
                        <br>
                        <strong>Metodologi yang Diusulkan:</strong> [Bangun pipeline RAG: PDF parsing, text splitting, embedding (misal: FAISS), dan LLM (misal: GPT-3.5). Fokus pada evaluasi: Gunakan metrik RAGAS atau buat set Q&A manual untuk mengukur akurasi jawaban].
                        <br>
                        <strong>Tantangan & Ruang Lingkup:</strong> [Tantangan utama adalah evaluasi. Ruang lingkup: Batasi pada 1-2 Jurnal/Fakultas sebagai sumber dokumen].
                    </li>
                    <li>
                        <strong>Judul Topik 4:</strong> [Ide spesifik keempat...]
                    </li>
                    <li>
                        <strong>Judul Topik 5:</strong> [Ide spesifik kelima...]
                    </li>
                </ul>

                <h3>📚 Referensi Kunci & Implementasi Kode</h3>
                <p>Sediakan link ke paper aslinya (WAJIB ArXiv, ACL, atau link resmi) dan link ke implementasi kode (jika ada, misal: di GitHub Hugging Face atau repositori resmi).</p>
                <p><strong>Paper Utama (Wajib):</strong> <a href="[URL_PAPER_RESMI_DI_ARXIV_DLL]" target="_blank">{lesson.title}</a></jika>
                <p><strong>Implementasi Kode (Jika Ada):</strong> <a href="[URL_GITHUB_IMPLEMENTASI]" target="_blank">Repositori Kode Resmi / Implementasi Hugging Face</a></p>
                <p><strong>Bacaan Lanjutan (Paper yang Diinspirasi):</strong></p>
                <ul>
                    <li>[Sebutkan 1-2 paper yang merupakan kelanjutan atau perbaikan dari paper ini]</li>
                </ul>
                """

                completion = local_ark_client.chat.completions.create(
                    model=current_app.config['MODEL_ENDPOINT_ID'],
                    messages=[{"role": "user", "content": prompt}]
                )
                
                ai_response_html = clean_html_from_markdown(completion.choices[0].message.content)
                
                lesson.content = ai_response_html
                db.session.commit()
                
                print(f"   -> Sukses! Konten untuk '{lesson.title}' berhasil disimpan.")
                time.sleep(3) # Memberi jeda lebih lama karena prompt lebih kompleks

            except Exception as e:
                print(f"   -> ❌ GAGAL saat men-generate konten untuk '{lesson.title}'. Error: {e}")
                db.session.rollback()
        
        print("\n🎉 Proses pembuatan konten (versi upgrade) untuk jalur 'LLM Research Papers' selesai!")

if __name__ == '__main__':
    generate_llm_research_content()