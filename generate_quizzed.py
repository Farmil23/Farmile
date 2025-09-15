import time
import json
from app import create_app, db
from app.models import Lesson
from flask import current_app

app = create_app()

def generate_and_save_quizzes():
    """
    Script untuk men-generate soal latihan (kuis) dalam format JSON untuk setiap materi
    yang sudah memiliki konten tetapi belum memiliki kuis.
    """
    with app.app_context():
        local_ark_client = current_app.ark_client
        if not local_ark_client:
            print("❌ Klien AI tidak terinisialisasi. Pastikan ARK_API_KEY sudah benar di file .env Anda.")
            return

        # Ambil materi yang sudah punya konten TAPI kolom kuisnya masih kosong
        lessons_to_process = Lesson.query.filter(Lesson.content.isnot(None), Lesson.content != '', Lesson.quiz.is_(None)).all()
        
        if not lessons_to_process:
            print("✅ Semua materi yang memiliki konten sudah dilengkapi dengan kuis.")
            return

        print(f"📚 Menemukan {len(lessons_to_process)} materi yang perlu dibuatkan kuis. Memulai proses...")
        
        for i, lesson in enumerate(lessons_to_process, 1):
            print(f"[{i}/{len(lessons_to_process)}] Membuat kuis untuk: '{lesson.title}'...")
            
            try:
                # Prompt yang dirancang khusus untuk membuat soal dalam format JSON
                prompt = f"""
                Anda adalah seorang Ahli Desain Kurikulum yang bertugas membuat soal evaluasi.
                Berdasarkan KONTEN MATERI di bawah ini, buatlah 3 hingga 7 pertanyaan pilihan ganda yang relevan untuk menguji pemahaman pembaca.

                **ATURAN PENTING:**
                1.  **Format Output:** Jawaban Anda HARUS dan HANYA berupa format JSON yang valid, tanpa teks tambahan atau penjelasan di luar JSON.
                2.  **Struktur JSON:** Ikuti struktur berikut dengan tepat:
                    {{
                        "questions": [
                            {{
                                "question_text": "Teks pertanyaan di sini...",
                                "options": [
                                    "Teks pilihan A",
                                    "Teks pilihan B",
                                    "Teks pilihan C",
                                    "Teks pilihan D"
                                ],
                                "correct_answer": "Teks pilihan yang benar",
                                "explanation": "Penjelasan singkat mengapa jawaban ini benar dan yang lain salah."
                            }}
                        ]
                    }}
                3.  **Kualitas Pertanyaan:** Buat pertanyaan yang menguji pemahaman konsep inti dari materi, bukan hanya hafalan kata per kata. Opsi jawaban harus masuk akal namun hanya ada satu yang paling tepat.

                --- KONTEN MATERI UNTUK DIANALISIS ---
                {lesson.content}
                --- AKHIR KONTEN MATERI ---
                """

                completion = local_ark_client.chat.completions.create(
                    model=current_app.config['MODEL_ENDPOINT_ID'],
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"} # Memaksa output menjadi JSON
                )
                
                ai_response_json_str = completion.choices[0].message.content.strip()
                
                # Validasi sederhana untuk memastikan hasilnya adalah JSON
                json.loads(ai_response_json_str)

                lesson.quiz = ai_response_json_str
                db.session.commit()
                
                print(f"   -> Sukses! Kuis untuk '{lesson.title}' berhasil disimpan.")
                time.sleep(1) # Jeda singkat untuk menghindari rate limiting

            except Exception as e:
                print(f"   -> ❌ GAGAL saat membuat kuis untuk '{lesson.title}'. Error: {e}")
                db.session.rollback()
        
        print("\n🎉 Proses pembuatan kuis selesai!")

if __name__ == '__main__':
    generate_and_save_quizzes()