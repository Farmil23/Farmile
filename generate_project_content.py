import time
from app import create_app, db
from app.models import Project
from flask import current_app
import re

app = create_app()

def clean_html_from_markdown(raw_html):
    """Membersihkan ```html, ```, dan tag markdown lainnya dari output AI."""
    cleaned_html = re.sub(r'^\s*```[a-zA-Z]*\n', '', raw_html)
    cleaned_html = re.sub(r'\n```\s*$', '', cleaned_html)
    return cleaned_html.strip()

def generate_and_save_content():
    with app.app_context():
        local_ark_client = current_app.ark_client
        if not local_ark_client:
            print("❌ Klien AI tidak terinisialisasi.")
            return

        projects_to_process = Project.query.filter(Project.generated_content.is_(None) | (Project.generated_content == '')).all()
        
        if not projects_to_process:
            print("✅ Semua proyek sudah memiliki konten panduan.")
            return

        print(f"📚 Menemukan {len(projects_to_process)} proyek yang perlu dibuatkan kontennya...")
        
        for i, project in enumerate(projects_to_process, 1):
            print(f"[{i}/{len(projects_to_process)}] Men-generate konten untuk: '{project.title}'...")
            
            try:
                # PROMPT BARU YANG LEBIH CERDAS DAN ADAPTIF
                prompt = f"""
                Anda adalah seorang Mentor Teknis Senior multi-disiplin (Software, Data, Jaringan, Keamanan).
                Tugas Anda adalah membuat panduan pengerjaan proyek yang sangat detail, ramah untuk pemula, dan relevan secara teknis untuk proyek: '{project.title}'.

                **KONTEKS PROYEK:**
                - Judul: {project.title}
                - Deskripsi: {project.description}
                - Teknologi/Tools: {project.tech_stack}

                **ATURAN KETAT:**
                1.  **ANALISIS DULU, BARU BUAT KONTEN**: Pertama, identifikasi tipe proyek ini (Coding, Analisis Data, Desain Jaringan, Konfigurasi Keamanan, dll.). Kemudian, buat panduan yang sesuai. JANGAN gunakan template coding untuk proyek non-coding.
                2.  **OUTPUT HTML MURNI**: Hasilkan output HANYA dalam format FRAGMENT HTML. JANGAN sertakan tag `<!DOCTYPE html>`, `<html>`, `<head>`, atau `<body>`. Mulai output langsung dari tag `<h3>` untuk list gunakan (titik) .
                3.  **KODE YANG RELEVAN**: Jika ada blok kode, pastikan bahasanya (`language-xxxx`) sesuai dengan teknologi yang disebutkan. Untuk perintah terminal/bash, gunakan `language-bash`. Untuk proyek non-coding, ganti blok kode dengan daftar langkah-langkah konfigurasi atau analisis.

                **STRUKTUR KONTEN HTML (WAJIB DIIKUTI DAN DIADAPTASI):**

                <h3>🚀 Latar Belakang & Konteks Proyek</h3>
                <p>Jelaskan masalah dunia nyata yang coba diselesaikan oleh proyek ini. Terangkan mengapa proyek ini adalah portofolio yang bagus dan skill spesifik apa (sesuai `tech_stack`) yang akan terbukti setelah menyelesaikannya.</p>

                <h3>📋 Langkah-Langkah Pengerjaan</h3>
                <p>Berikan panduan langkah demi langkah yang jelas. **Adaptasikan langkah-langkah ini sesuai tipe proyek!**</p>
                
                <h4>Langkah 1: Persiapan Awal (Setup Environment & Tools)</h4>
                <p>Deskripsikan apa saja yang perlu di-install atau disiapkan. Contoh: 'Install Wireshark dari situs resminya' atau 'Pastikan Anda memiliki akses ke Packet Tracer'.</p>
                
                <h4>Langkah 2: [Judul Langkah Teknis Spesifik]</h4>
                <p>
                    Deskripsi langkah teknis kedua. 
                    - **Untuk Proyek Coding:** Berikan contoh kode yang relevan.
                    - **Untuk Proyek Jaringan/DevOps:** Berikan contoh perintah konsol atau langkah konfigurasi GUI.
                    - **Untuk Proyek Keamanan:** Jelaskan tool yang digunakan dan apa yang harus dicari.
                    - **Untuk Proyek Analisis Data:** Jelaskan cara memuat data atau metrik apa yang harus dianalisis.
                </p>
                
                <h4>Langkah 3: [Judul Langkah Teknis Berikutnya]</h4>
                <p>Lanjutkan dengan 2-3 langkah teknis lainnya hingga fungsionalitas inti proyek tercapai.</p>

                <h3>🚀 Cara Mengumpulkan Proyek</h3>
                <p>Berikan panduan tentang cara mendokumentasikan dan membagikan hasil proyek ini.</p>
                <ul>
                    <li><strong>Dokumentasi Hasil:</strong> Jelaskan apa yang perlu didokumentasikan. Contoh: 'Ambil screenshot dari konfigurasi firewall Anda' atau 'Buat laporan analisis dalam format PDF/Word yang berisi visualisasi data dan insight Anda'.</li>
                    <li><strong>Upload ke GitHub:</strong> Sarankan untuk membuat repository di GitHub yang berisi file konfigurasi, laporan, dan file `README.md` yang menjelaskan proyek dan temuan Anda.</li>
                    <li><strong>Link Repository:</strong> Ingatkan pengguna untuk menyalin URL repository GitHub mereka dan menempelkannya di form submission.</li>
                </ul>

                <h3>🏆 Tantangan Bonus (Opsional)</h3>
                <p>Berikan 1-2 ide fitur/analisis tambahan yang relevan dengan bidang proyek (misal: 'Coba deteksi anomali trafik pada hasil capture Wireshark' atau 'Otomatiskan proses deployment menggunakan script bash').</p>
                """

                completion = local_ark_client.chat.completions.create(
                    model=current_app.config['MODEL_ENDPOINT_ID'],
                    messages=[{"role": "user", "content": prompt}]
                )
                
                raw_html = completion.choices[0].message.content
                ai_response_html = clean_html_from_markdown(raw_html)
                
                project.generated_content = ai_response_html
                db.session.commit()
                
                print(f"   -> Sukses! Konten untuk '{project.title}' berhasil disimpan.")
                time.sleep(2)

            except Exception as e:
                print(f"   -> ❌ GAGAL saat men-generate konten untuk '{project.title}'. Error: {e}")
                db.session.rollback()
        
        print("\n🎉 Proses pembuatan konten proyek selesai!")

if __name__ == '__main__':
    generate_and_save_content()