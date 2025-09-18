# nama file: generate_gamedev_content.py
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

def generate_gamedev_content():
    """
    Script untuk men-generate konten materi HANYA UNTUK CAREER PATH 'game-developer'.
    """
    with app.app_context():
        local_ark_client = current_app.ark_client
        if not local_ark_client:
            print("❌ Klien AI tidak terinisialisasi.")
            return

        # Kueri Khusus: Hanya ambil materi dari career path 'game-developer'
        lessons_to_process = Lesson.query.join(Module).filter(
            Module.career_path == 'game-developer',
            (Lesson.content.is_(None) | (Lesson.content == ''))
        ).all()
        
        if not lessons_to_process:
            print("✅ Semua materi di jalur Game Developer sudah memiliki konten.")
            return

        print(f"📚 Menemukan {len(lessons_to_process)} materi Game Developer yang perlu diisi kontennya. Memulai proses...")
        
        for i, lesson in enumerate(lessons_to_process, 1):
            print(f"[{i}/{len(lessons_to_process)}] Men-generate konten untuk: '{lesson.title}'...")
            
            try:
                # --- PROMPT KHUSUS UNTUK GAME DEVELOPER ---
                prompt = f"""
                Anda adalah seorang Senior Gameplay Programmer dan Technical Director di sebuah studio game AAA. Anda sangat berpengalaman dalam Unity Engine dan C# dan mampu menjelaskan konsep kompleks dengan cara yang sangat praktis dan mudah dipahami oleh pemula.

                Tugas Anda adalah membuat materi pembelajaran yang mendalam dan sangat detail untuk topik: "{lesson.title}".

                **PERSONA & GAYA PENULISAN:**
                -   **Hands-on & Praktis:** Fokus pada implementasi nyata di dalam Unity. Semua penjelasan harus bisa langsung dipraktikkan.
                -   **Dari Konsep ke Script:** Jelaskan konsep game development (misal: 'Player Controller', 'State Machine') lalu langsung tunjukkan bagaimana cara mengimplementasikannya dalam script C#.
                -   **Gunakan Analogi Game:** Jelaskan konsep sulit dengan analogi dari game terkenal. Contoh: "Sistem State Machine pada musuh ini mirip seperti perilaku Goomba di Super Mario...".

                **ATURAN OUTPUT (SANGAT KETAT):**
                1.  **HANYA FRAGMENT HTML**: Output HARUS berupa fragment HTML. JANGAN PERNAH menyertakan tag `<!DOCTYPE html>`, `<html>`, `<head>`, atau `<body>`. Mulai output langsung dari tag `<h3>`.
                2.  **KODE C# UNTUK UNITY**: Semua contoh kode HARUS dalam bahasa C# dan relevan untuk digunakan di dalam Unity Engine. Gunakan `<pre><code class="language-csharp">`.

                **STRUKTUR KONTEN HTML (WAJIB DIIKUTI):**

                <h3>🚀 Misi Hari Ini: Menguasai "{lesson.title}"</h3>
                <p>Mulailah dengan menjelaskan peran "{lesson.title}" dalam proses pembuatan sebuah game. Kaitkan topik ini dengan sebuah fitur atau mekanik game yang keren untuk membangkitkan semangat belajar. Jelaskan apa yang akan bisa dibuat oleh pengguna setelah menguasai materi ini.</p>

                <h3>🤔 Konsep Inti di Balik Gameplay</h3>
                <p>Jelaskan konsep fundamental di balik "{lesson.title}". Jika ini tentang 'Player Controller', jelaskan apa itu input, state, dan bagaimana game meresponsnya. Gunakan analogi yang relevan.</p>
                
                <h3>⚙️ Implementasi di Unity Engine</h3>
                <p>Pecah proses implementasi menjadi beberapa sub-bagian menggunakan `<h4>`. Berikan panduan langkah demi langkah yang detail, baik untuk setup di Unity Editor maupun untuk penulisan kode.</p>
                
                <h4>Langkah 1: Setup di Unity Editor</h4>
                <p>Jelaskan komponen apa saja yang perlu ditambahkan ke sebuah GameObject di Unity. Contoh: "Buat sebuah GameObject baru, tambahkan komponen `Rigidbody2D` dan `BoxCollider2D`."</p>

                <h4>Langkah 2: Menulis Script C#</h4>
                <p>Berikan contoh script C# yang lengkap untuk mengimplementasikan fungsionalitas. Beri komentar pada bagian-bagian kode yang penting.</p>
                <pre><code class="language-csharp">
// Nama File: PlayerController.cs
using UnityEngine;

public class PlayerController : MonoBehaviour
{{
    public float moveSpeed = 5f;
    private Rigidbody2D rb;

    // Start dipanggil sebelum frame pertama update
    void Start()
    {{
        rb = GetComponent<Rigidbody2D>(); // Mengambil komponen Rigidbody2D
    }}

    // Update dipanggil sekali setiap frame
    void Update()
    {{
        // Logika pergerakan pemain akan ditulis di sini
        float moveInput = Input.GetAxisRaw("Horizontal");
        rb.velocity = new Vector2(moveInput * moveSpeed, rb.velocity.y);
    }}
}}
</code></pre>

                <h3>🎮 Uji Coba & Debugging</h3>
                <p>Berikan instruksi tentang cara menguji fungsionalitas yang baru dibuat di dalam Unity Editor. Berikan juga tips tentang masalah umum yang mungkin terjadi dan cara mengatasinya (misal: "Jika karakter menembus lantai, pastikan collider-nya tidak di-set sebagai Trigger.").</p>

                <h3>✅ Rangkuman Misi & Poin Penting</h3>
                <h4>Checkpoints</h4>
                <ul>
                    <li>Poin kunci pertama: Satu kalimat yang merangkum hal terpenting.</li>
                    <li>Poin kunci kedua.</li>
                </ul>
                <h4>Common Bugs & Pitfalls</h4>
                <ul>
                    <li>[Bug 1]: Jelaskan bug umum, contoh: "Lupa meng-assign referensi komponen di Inspector."</li>
                    <li>[Bug 2]: Jelaskan kesalahan logika yang sering terjadi.</li>
                </ul>
                <p>Akhiri dengan sebuah paragraf yang menghubungkan skill ini dengan pembuatan game yang lebih kompleks di materi selanjutnya.</p>
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
        
        print("\n🎉 Proses pembuatan konten untuk jalur Game Developer selesai!")

if __name__ == '__main__':
    generate_gamedev_content()