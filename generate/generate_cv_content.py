# nama file: generate_cv_content.py
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

def generate_cv_content():
    """
    Script untuk men-generate konten materi HANYA UNTUK CAREER PATH 'computer-vision-engineer'.
    """
    with app.app_context():
        local_ark_client = current_app.ark_client
        if not local_ark_client:
            print("❌ Klien AI tidak terinisialisasi.")
            return

        # Kueri Khusus: Hanya ambil materi dari career path 'computer-vision-engineer'
        lessons_to_process = Lesson.query.join(Module).filter(
            Module.career_path == 'computer-vision-engineer',
            (Lesson.content.is_(None) | (Lesson.content == ''))
        ).all()
        
        if not lessons_to_process:
            print("✅ Semua materi di jalur Computer Vision Engineer sudah memiliki konten.")
            return

        print(f"📚 Menemukan {len(lessons_to_process)} materi Computer Vision yang perlu diisi kontennya...")
        
        for i, lesson in enumerate(lessons_to_process, 1):
            print(f"[{i}/{len(lessons_to_process)}] Men-generate konten untuk: '{lesson.title}'...")
            
            try:
                # --- PROMPT FINAL DAN LENGKAP UNTUK COMPUTER VISION ENGINEER ---
                prompt = f"""
                Anda adalah seorang Senior Computer Vision Scientist dari perusahaan teknologi terdepan (seperti Tesla atau Google Photos). Anda ahli dalam mengubah gambar dan video menjadi data yang bisa dipahami mesin dan memiliki kemampuan untuk menjelaskan proses visual yang rumit menjadi langkah-langkah praktis.

                Tugas Anda adalah membuat materi pembelajaran yang mendalam, sangat visual, dan relevan dengan industri untuk topik: "{lesson.title}".

                **PERSONA & GAYA PENULISAN:**
                -   **Visual First:** Selalu mulai dengan penjelasan konseptual tentang BAGAIMANA manusia melihat dan bagaimana kita bisa menirunya dengan komputer. Gunakan analogi visual yang kuat.
                -   **Hands-on with OpenCV & TensorFlow/PyTorch:** Fokus pada implementasi praktis menggunakan library standar industri. Contoh kode harus menunjukkan proses dari input gambar hingga visualisasi output yang diharapkan.
                -   **Connecting to Real-World Applications:** Kaitkan setiap konsep dengan aplikasi nyata yang canggih (misal: "Deteksi tepi adalah langkah pertama dalam sistem mobil otonom untuk mendeteksi jalur...").

                **ATURAN OUTPUT (SANGAT KETAT):**
                1.  **HANYA FRAGMENT HTML**: Output HARUS berupa fragment HTML. JANGAN PERNAH menyertakan tag `<!DOCTYPE html>`, `<html>`, `<head>`, atau `<body>`. Mulai output langsung dari tag `<h3>`.
                2.  **KODE PYTHON UNTUK CV**: Semua contoh kode HARUS dalam bahasa Python dan menggunakan library yang relevan (OpenCV, TensorFlow, PyTorch). Gunakan `<pre><code class="language-python">`.
                3.  **PENJELASAN KODE**: Setelah setiap blok kode, WAJIB tambahkan `<h4>Penjelasan Kode</h4>` dan `<ul>` yang menjelaskan fungsi-fungsi kunci, parameter penting, dan logika di balik setiap langkah dalam kode tersebut.

                **STRUKTUR KONTEN HTML (WAJIB DIIKUTI):**

                <h3>🚀 Misi Visual: Menguasai "{lesson.title}"</h3>
                <p>Mulailah dengan menjelaskan masalah visual yang bisa dipecahkan dengan menguasai "{lesson.title}". Berikan contoh aplikasi industri yang sangat bergantung pada teknologi ini (misal: quality control di pabrik, diagnosis medis dari citra, atau augmented reality) untuk menunjukkan dampak nyatanya.</p>

                <h3>🤔 Intuisi di Balik Piksel: Cara "Melihat" ala Komputer</h3>
                <p>Jelaskan ide utama di balik "{lesson.title}" dari sudut pandang pemrosesan gambar. Gunakan analogi yang kuat. Contoh: "Bayangkan operasi konvolusi seperti sebuah senter kecil (disebut kernel) yang kita geser di atas seluruh permukaan gambar. Setiap kali senter berhenti, ia hanya melihat area kecil di bawahnya dan melakukan perhitungan sederhana untuk mendeteksi fitur tertentu seperti garis vertikal, sudut, atau perubahan warna. Hasil dari semua perhitungan ini akan membentuk 'peta fitur' baru yang menyorot bagian-bagian penting dari gambar asli."</p>
                
                <h3>⚙️ Algoritma Inti dan Cara Kerjanya</h3>
                <p>Pecah konsep teknis menjadi beberapa sub-bagian menggunakan `<h4>`. Jelaskan algoritma atau arsitektur utamanya secara visual atau konseptual.</p>
                
                <h4>[Sub-Topik Teknis 1: Contoh: Kernel dan Konvolusi]</h4>
                <p>Penjelasan detail tentang bagaimana sebuah kernel (matriks kecil) bekerja untuk mengekstrak fitur dari sebuah gambar. Tunjukkan contoh kernel untuk deteksi tepi atau blur.</p>

                <h3>💻 Implementasi Praktis dengan OpenCV</h3>
                <p>Tunjukkan cara mengimplementasikan konsep tersebut dengan contoh kode Python yang bisa langsung dijalankan. Asumsikan pengguna memiliki file gambar bernama `input.jpg` di folder yang sama.</p>
                <pre><code class="language-python">
# Mengimpor library yang dibutuhkan
import cv2
import numpy as np
from matplotlib import pyplot as plt

# Membaca gambar dari file dalam mode grayscale (hitam putih)
# Mode grayscale menyederhanakan proses deteksi fitur berbasis intensitas cahaya.
image = cv2.imread('input.jpg', cv2.IMREAD_GRAYSCALE)

# Menerapkan Canny Edge Detection, salah satu algoritma deteksi tepi paling populer.
# Angka 100 dan 200 adalah nilai ambang batas bawah dan atas.
edges = cv2.Canny(image, 100, 200)

# Menyiapkan tampilan untuk membandingkan gambar asli dan hasilnya
plt.figure(figsize=(10, 5)) # Membuat ukuran figure lebih besar

plt.subplot(121) # Plot pertama (1 baris, 2 kolom, posisi ke-1)
plt.imshow(image, cmap='gray')
plt.title('Gambar Asli')
plt.xticks([]), plt.yticks([]) # Menghilangkan sumbu x dan y

plt.subplot(122) # Plot kedua (1 baris, 2 kolom, posisi ke-2)
plt.imshow(edges, cmap='gray')
plt.title('Hasil Deteksi Tepi')
plt.xticks([]), plt.yticks([])

plt.show() # Menampilkan plot
</code></pre>
                <h4>Penjelasan Kode</h4>
                <ul>
                    <li><strong>Baris 6:</strong> Kita memuat gambar menggunakan `cv2.imread`. Parameter kedua, `cv2.IMREAD_GRAYSCALE`, mengubah gambar menjadi hitam putih karena deteksi tepi lebih mudah dilakukan pada intensitas piksel daripada warna.</li>
                    <li><strong>Baris 10:</strong> Ini adalah baris inti di mana kita memanggil fungsi `cv2.Canny`. Fungsi ini secara otomatis melakukan Gaussian blur, menghitung gradien intensitas, dan menerapkan *hysteresis thresholding* dengan nilai ambang 100 dan 200 untuk menghasilkan tepi yang bersih.</li>
                    <li><strong>Baris 13-22:</strong> Kode ini menggunakan library `matplotlib` untuk menampilkan dua gambar (asli dan hasil) secara berdampingan. Ini adalah praktik terbaik dalam computer vision untuk memvisualisasikan dan membandingkan hasil dari sebuah operasi.</li>
                </ul>

                <h3>💡 Aplikasi di Dunia Nyata</h3>
                <p>Jelaskan di mana konsep "{lesson.title}" digunakan di industri. Berikan 2-3 contoh spesifik dan jelaskan bagaimana teknik ini memberikan nilai bisnis. Contoh: "Di mobil otonom, deteksi tepi digunakan untuk mengidentifikasi marka jalan. Di bidang medis, ia membantu mensegmentasi organ dari gambar CT scan."</p>
                
                <h3>✅ Rangkuman & Checklist untuk Engineer</h3>
                <h4>Poin Kunci</h4>
                <ul>
                    <li>Poin rangkuman teknis pertama yang paling penting.</li>
                    <li>Poin rangkuman kedua yang relevan dengan implementasi.</li>
                </ul>
                <p>Akhiri dengan sebuah paragraf yang menghubungkan skill ini dengan peran seorang Computer Vision Engineer dan bagaimana ini akan menjadi fondasi untuk topik yang lebih canggih seperti Object Detection atau Image Segmentation.</p>
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
        
        print("\n🎉 Proses pembuatan konten untuk jalur Computer Vision Engineer selesai!")

if __name__ == '__main__':
    generate_cv_content()