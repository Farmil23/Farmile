# nama file: generate/seed_llm_research.py

from app import db
from app.models import Roadmap, Module, Lesson

# Kunci ini harus sama agar generator AI bisa menemukannya
CAREER_PATH_SLUG = "llm-research-papers"
ROADMAP_TITLE = "Riset Lanjutan AI: 10 Modul Mendalam (LLM, Visi & Agen)"

def seed_llm_research():
    """
    (Versi 10 Modul)
    Menambahkan roadmap dan 10 modul riset mendalam
    untuk 'Riset Lanjutan AI' (llm-research-papers).
    """
    print(f"Memulai seeding (versi 10 Modul) untuk career path: '{CAREER_PATH_SLUG}'...")

    try:
        # 1. Cek atau Buat Roadmap
        roadmap = Roadmap.query.filter_by(title=ROADMAP_TITLE).first()
        if not roadmap:
            roadmap = Roadmap(
                title=ROADMAP_TITLE,
                description="Kurikulum riset komprehensif 10 modul, membedah paper SOTA di LLM, Agen, Multimodalitas, dan lainnya untuk ide skripsi & tesis.",
                level="Expert"
            )
            db.session.add(roadmap)
            db.session.flush()
            print(f"-> Roadmap baru dibuat: '{roadmap.title}'")
        else:
            print(f"-> Roadmap '{roadmap.title}' sudah ada.")

        # --- Daftar 10 Modul & Paper Pilihan ---
        
        modules_data = [
            # Modul 1: Fondasi Arsitektur (Era Pra-LLM & Awal LLM)
            ("Modul 1: Fondasi Arsitektur & Model Fundamental", [
                ("Bedah Paper: 'Attention Is All You Need' (Transformers)", "Dasar dari semua model LLM modern."),
                ("Bedah Paper: 'BERT: Pre-training of Deep Bidirectional Transformers'", "Memahami konteks dua arah (bidirectional)."),
                ("Bedah Paper: 'GPT-1: Improving Language Understanding by Generative Pre-Training'", "Kekuatan pre-training generatif."),
                ("Bedah Paper: 'GPT-2: Language Models are Unsupervised Multitask Learners'", "Konsep zero-shot learning & bahaya model besar."),
                ("Bedah Paper: 'T5: Exploring the Limits of Transfer Learning'", "Framework Text-to-Text Transfer Transformer."),
            ]),
            
            # Modul 2: Era LLM Skala Besar (Scaling Laws & Model Kunci)
            ("Modul 2: Era LLM Skala Besar & Scaling Laws", [
                ("Bedah Paper: 'GPT-3: Language Models are Few-Shot Learners'", "Era model raksasa dan in-context learning."),
                ("Bedah Paper: 'Scaling Laws for Neural Language Models'", "Hubungan matematis antara data, parameter, dan performa."),
                ("Bedah Paper: 'PaLM: Scaling Language Modeling with Pathways'", "Arsitektur Pathways dan scaling model ke 540B."),
                ("Bedah Paper: 'LLaMA: Open and Efficient Foundation Language Models'", "Model open-source efisien yang mengubah lanskap riset."),
                ("Bedah Paper: 'Chinchilla: Training Compute-Optimal Large Language Models'", "Menemukan bahwa data lebih penting daripada parameter."),
            ]),

            # Modul 3: Teknik Prompting & Penalaran (Reasoning)
            ("Modul 3: Teknik Prompting & Penalaran (Reasoning)", [
                ("Bedah Paper: 'Chain-of-Thought Prompting Elicits Reasoning'", "Cara membuat LLM 'berpikir' selangkah demi selangkah."),
                ("Bedah Paper: 'Tree of Thoughts: Deliberate Problem Solving with LLMs'", "Eksplorasi berbagai jalur penalaran."),
                ("Bedah Paper: 'Self-Consistency Improves Chain of Thought Reasoning'", "Mengambil 'suara mayoritas' dari beberapa CoT."),
                ("Bedah Paper: 'Least-to-Most Prompting'", "Memecah masalah kompleks menjadi sub-masalah."),
            ]),

            # Modul 4: Efisiensi & Fine-Tuning (PEFT)
            ("Modul 4: Efisiensi Model & Parameter-Efficient Fine-Tuning (PEFT)", [
                ("Bedah Paper: 'LoRA: Low-Rank Adaptation of Large Language Models'", "Teknik fine-tuning yang sangat efisien."),
                ("Bedah Paper: 'QLoRA: Quantized-LoRA'", "Menjalankan fine-tuning model besar di hardware terbatas (consumer GPU)."),
                ("Bedah Paper: 'DistilBERT, a distilled version of BERT'", "Konsep *knowledge distillation* untuk model yang lebih kecil."),
                ("Bedah Paper: 'FlashAttention: Fast and Memory-Efficient Exact Attention'", "Inovasi algoritma untuk mempercepat training Transformer."),
            ]),

            # Modul 5: Alignment, Safety & Ethics
            ("Modul 5: Alignment, Safety & Etika", [
                ("Bedah Paper: 'Learning to Summarize from Human Feedback (RLHF)'", "Paper awal mula penggunaan Reinforcement Learning from Human Feedback."),
                ("Bedah Paper: 'Constitutional AI: Harmlessness from AI Feedback'", "Melatih AI untuk aman tanpa feedback manusia (prinsip 'konstitusi')."),
                ("Bedah Paper: 'DPO: Direct Preference Optimization'", "Alternatif modern yang lebih sederhana dan stabil selain RLHF."),
                ("Bedah Paper: 'Red Teaming Language Models to Reduce Harms'", "Metodologi untuk mencari kelemahan dan bias pada LLM."),
            ]),

            # Modul 6: Retrieval-Augmented Generation (RAG)
            ("Modul 6: Retrieval-Augmented Generation (RAG) & LLM Berbasis Pengetahuan", [
                ("Bedah Paper: 'RAG: Retrieval-Augmented Generation for Knowledge-Intensive Tasks'", "Paper orisinal yang menggabungkan LLM dengan database eksternal."),
                ("Bedah Paper: 'Dense Passage Retrieval (DPR) for Open-Domain Q&A'", "Cara 'retriever' menemukan dokumen yang relevan."),
                ("Bedah Paper: 'Self-RAG: Learning to Retrieve, Generate, and Critique'", "Membuat LLM memutuskan kapan harus mengambil data."),
                ("Bedah Paper: 'Corrective RAG (CRAG)'", "Memperbaiki dokumen yang diambil jika tidak relevan."),
            ]),

            # Modul 7: Agen AI & Penggunaan Tools (LLM as Agents)
            ("Modul 7: Agen AI & Penggunaan Tools (LLM as Agents)", [
                ("Bedah Paper: 'ReAct: Synergizing Reasoning and Acting in LLMs'", "Pola *Reasoning* (CoT) dan *Action* (Tools) untuk agen."),
                ("Bedah Paper: 'Toolformer: Language Models Can Teach Themselves to Use Tools'", "Cara LLM belajar memanggil API (Kalkulator, Search Engine)."),
                ("Bedah Paper: 'Generative Agents: Interactive Simulacra of Human Behavior'", "Simulasi agen AI kompleks ('The Sims' dengan LLM)."),
                ("Bedah Paper: 'Gorilla: Large Language Model Connected to Massive APIs'", "Melatih LLM untuk menulis panggilan API yang akurat."),
            ]),

            # Modul 8: Multimodalitas (Visi & Bahasa)
            ("Modul 8: Multimodalitas (Visi & Bahasa)", [
                ("Bedah Paper: 'CLIP: Learning Transferable Visual Models From Natural Language'", "Menghubungkan teks dan gambar untuk zero-shot image classification."),
                ("Bedah Paper: 'BLIP-2: Bootstrapping Language-Image Pre-training'", "Teknik Visi-Bahasa yang efisien (Q-Former)."),
                ("Bedah Paper: 'Flamingo: a Visual Language Model'", "Arsitektur VLM untuk few-shot learning pada gambar & video."),
                ("Bedah Paper: 'GPT-4V(ision): Laporan Teknis'", "Menganalisis kemampuan model multimodal SOTA."),
            ]),

            # Modul 9: Model Generatif di Luar Teks (Gambar, Audio, 3D)
            ("Modul 9: Model Generatif di Luar Teks (Gambar, Audio, 3D)", [
                ("Bedah Paper: 'Denoising Diffusion Probabilistic Models (DDPM)'", "Dasar dari model generator gambar (Stable Diffusion, DALL-E 2)."),
                ("Bedah Paper: 'Stable Diffusion: High-Resolution Image Synthesis'", "Menggunakan *latent space* untuk difusi yang efisien."),
                ("Bedah Paper: 'NeRF: Neural Radiance Fields'", "Merepresentasikan adegan 3D yang kompleks dari gambar 2D."),
                ("Bedah Paper: 'AudioLM: a Language Modeling Approach to Audio Generation'", "Menggunakan teknik LLM untuk menghasilkan audio (musik, ucapan)."),
            ]),

            # Modul 10: Evaluasi, Benchmarking & Masa Depan
            ("Modul 10: Evaluasi, Benchmarking & Tantangan Masa Depan", [
                ("Bedah Paper: 'BLEU: a Method for Automatic Evaluation of Machine Translation'", "Metrik evaluasi klasik untuk generasi teks."),
                ("Bedah Paper: 'HELM: Holistic Evaluation of Language Models'", "Benchmark komprehensif untuk mengukur LLM secara adil."),
                ("Bedah Paper: 'RAGAS: Automated Evaluation of RAG Pipelines'", "Metrik modern untuk mengevaluasi sistem RAG."),
                ("Bedah Paper: 'Hallucination in LLMs: A Survey'", "Tinjauan komprehensif tentang masalah halusinasi dan solusinya."),
            ]),
        ]

        module_order = 1
        for module_title, papers in modules_data:
            
            # 2. Cek atau Buat Module
            module = Module.query.filter_by(title=module_title, roadmap_id=roadmap.id).first()
            if not module:
                module = Module(
                    roadmap_id=roadmap.id,
                    title=module_title,
                    order=module_order,
                    career_path=CAREER_PATH_SLUG, # KUNCI untuk generator AI
                    level="Expert"
                )
                db.session.add(module)
                db.session.flush() 
                print(f"-> Module baru dibuat: '{module.title}'")
            else:
                print(f"-> Module '{module.title}' sudah ada.")
            
            module_order += 1
            
            # 3. Definisikan dan Tambahkan Lessons (masih kosong)
            lesson_order = 1
            for title, desc in papers:
                if not Lesson.query.filter_by(title=title, module_id=module.id).first():
                    lesson = Lesson(
                        module_id=module.id,
                        title=title,
                        description=desc,
                        order=lesson_order,
                        lesson_type="article",
                        estimated_time=75, # Waktu estimasi lebih lama
                        content="" # Dibiarkan kosong untuk diisi AI
                    )
                    db.session.add(lesson)
                    print(f"   -> Menambahkan lesson (kosong): '{title}'")
                    lesson_order += 1
                else:
                    print(f"   -> Lesson '{title}' sudah ada, dilewati.")
        
        db.session.commit()
        print(f"✅ Seeding (versi 10 Modul) untuk '{CAREER_PATH_SLUG}' selesai.")

    except Exception as e:
        db.session.rollback()
        print(f"❌ Terjadi error saat seeding '{CAREER_PATH_SLUG}': {e}")