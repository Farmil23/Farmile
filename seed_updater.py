# nama file: seed_updater.py
import json
from app import create_app, db
from app.models import Module, Lesson, Project, Roadmap

app = create_app()

with app.app_context():
    # Langkah 1: Cek atau buat Roadmap umum (tidak akan menghapus yang sudah ada)
    roadmap_umum = Roadmap.query.filter_by(level='General').first()
    if not roadmap_umum:
        print("Membuat Roadmap umum...")
        roadmap_umum = Roadmap(title='Roadmap Belajar Farsight', level='General')
        db.session.add(roadmap_umum)
        db.session.commit()
    else:
        print("Roadmap umum sudah ada.")

    # Langkah 2: Definisikan HANYA struktur kurikulum BARU
    new_career_data = {
        'game-developer': [
            {'title': 'Fondasi Game Development & C#', 'level': 'beginner', 'lessons': [
                {'title': 'Pengenalan Industri Game & Peran Game Developer'}, {'title': 'Setup Unity & Visual Studio'},
                {'title': 'Dasar Pemrograman C#: Variabel, Tipe Data, dan Kondisi'}, {'title': 'Struktur Kontrol: Looping dan Fungsi di C#'},
                {'title': 'Object-Oriented Programming (OOP) di C#'}, {'title': 'Struktur Data Dasar: Array dan List'},
                {'title': 'Debugging Dasar di Visual Studio'}
            ], 'projects': [{'title': 'Game Teka-Teki Teks Sederhana', 'difficulty': 'Beginner', 'tech_stack': 'C#, .NET Console'}]},
            {'title': 'Pengenalan Unity Engine', 'level': 'beginner', 'lessons': [
                {'title': 'Memahami Antarmuka Unity: Scene, Hierarchy, Inspector'}, {'title': 'GameObjects dan Components'},
                {'title': 'Transformasi: Posisi, Rotasi, Skala'}, {'title': 'Scripting di Unity: MonoBehaviour Lifecycle'},
                {'title': 'Input Handling: Keyboard dan Mouse'}, {'title': 'Bekerja dengan Prefabs'},
                {'title': 'Dasar Fisika 2D: Rigidbody dan Collider'}
            ], 'projects': [{'title': 'Prototipe Game Platformer 2D Sederhana', 'difficulty': 'Beginner', 'tech_stack': 'Unity, C#'}]},
            {'title': 'Gameplay Mechanics & UI', 'level': 'intermediate', 'lessons': [
                {'title': 'Membangun Sistem Player Controller'}, {'title': 'Scripting Mekanisme Gameplay (Lompat, Tembak)'},
                {'title': 'Pengenalan Unity UI: Canvas, Text, Button'}, {'title': 'Membuat Menu Utama dan HUD (Heads-Up Display)'},
                {'title': 'Manajemen Scene dan Transisi'}, {'title': 'Audio di Unity: Background Music & Sound Effects'},
                {'title': 'Coroutines untuk Operasi Berwaktu'}
            ], 'projects': [
                {'title': 'Game Space Shooter 2D', 'difficulty': 'Intermediate', 'tech_stack': 'Unity, C#'},
                {'title': 'Game Endless Runner 3D', 'difficulty': 'Intermediate', 'tech_stack': 'Unity, C#'}
            ]},
            {'title': 'Grafis & Animasi', 'level': 'intermediate', 'lessons': [
                {'title': 'Dasar Material dan Shader di Unity'}, {'title': 'Sistem Partikel untuk Efek Visual'},
                {'title': 'Lighting: Realtime vs Baked Lighting'}, {'title': 'Sistem Animasi Unity: Animator Controller'},
                {'title': 'Membuat State Machine untuk Animasi Karakter'}, {'title': 'Timeline untuk Cutscenes dan Sekuens'},
                {'title': 'Post-Processing Effects'}
            ], 'projects': [{'title': 'Membuat Level Game dengan Aset Visual & Animasi', 'difficulty': 'Intermediate', 'tech_stack': 'Unity'}]},
            {'title': 'Kecerdasan Buatan (AI) untuk Game', 'level': 'advanced', 'lessons': [
                {'title': 'Konsep AI dalam Game'}, {'title': 'NavMesh untuk Pathfinding Musuh'},
                {'title': 'Finite State Machines (FSM) untuk Perilaku AI'}, {'title': 'Behavior Trees sebagai Alternatif FSM'},
                {'title': 'Menciptakan AI Musuh Sederhana (Mengejar & Menyerang)'}, {'title': 'Dasar-dasar Procedural Content Generation (PCG)'}
            ], 'projects': [{'title': 'Implementasi AI Musuh di Game Platformer', 'difficulty': 'Advanced', 'tech_stack': 'Unity, C#'}]},
            {'title': 'Multiplayer & Jaringan', 'level': 'advanced', 'lessons': [
                {'title': 'Konsep Dasar Jaringan Game'}, {'title': 'Pengenalan Netcode for GameObjects (Unity)'},
                {'title': 'Sinkronisasi State Pemain (Player State Synchronization)'}, {'title': 'Remote Procedure Calls (RPCs)'},
                {'title': 'Membangun Lobi Game Sederhana'}, {'title': 'Menangani Lag dan Latency'}
            ], 'projects': [{'title': 'Prototipe Game Multiplayer Sederhana', 'difficulty': 'Advanced', 'tech_stack': 'Unity, Netcode for GameObjects'}]},
            {'title': 'Optimisasi & Performa', 'level': 'expert', 'lessons': [
                {'title': 'Unity Profiler untuk Menganalisis Performa'}, {'title': 'Optimisasi Rendering: Draw Calls & Batching'},
                {'title': 'Manajemen Memori dan Garbage Collection'}, {'title': 'Object Pooling untuk Efisiensi'},
                {'title': 'Level of Detail (LOD) untuk Model 3D'}, {'title': 'Optimisasi Fisika'}
            ], 'projects': [{'title': 'Menganalisis dan Mengoptimalkan Scene Game', 'difficulty': 'Expert', 'tech_stack': 'Unity Profiler'}]},
            {'title': 'Desain Game & Narasi', 'level': 'expert', 'lessons': [
                {'title': 'Prinsip-prinsip Desain Game'}, {'title': 'Game Loops dan Player Engagement'},
                {'title': 'Desain Level (Level Design)'}, {'title': 'Dasar-dasar Desain Narasi'},
                {'title': 'Monetisasi dalam Game (IAP, Ads)'}, {'title': 'Playtesting dan Feedback Loop'}
            ], 'projects': [{'title': 'Membuat Game Design Document (GDD)', 'difficulty': 'Expert', 'tech_stack': 'Design Thinking'}]},
            {'title': 'Struktur Data & Algoritma untuk Game', 'level': 'expert', 'lessons': [
                {'title': 'Pentingnya Algoritma dalam Game'}, {'title': 'Analisis Big O Notation'},
                {'title': 'Spatial Partitioning (Quadtrees, Octrees)'}, {'title': 'A* Pathfinding Algorithm'},
                {'title': 'Shader Programming Dasar (HLSL/GLSL)'}, {'title': 'Version Control dengan Git untuk Proyek Unity'}
            ], 'projects': [{'title': 'Implementasi A* Pathfinding dari Nol', 'difficulty': 'Expert', 'tech_stack': 'Unity, C#'}]},
            {'title': 'Publikasi & Karier', 'level': 'expert', 'lessons': [
                {'title': 'Membangun Portofolio Game Developer'}, {'title': 'Proses Publikasi ke Steam, App Store, Play Store'},
                {'title': 'Game Jams dan Komunitas'}, {'title': 'Wawancara Teknis untuk Game Developer'},
                {'title': 'Peran-peran dalam Studio Game'}, {'title': 'Masa Depan Game Development (Cloud Gaming, VR/AR)'}
            ], 'projects': [{'title': 'Mengikuti Game Jam dan Membuat Game dalam 48 Jam', 'difficulty': 'Expert', 'tech_stack': 'Unity, C#'}]}
        ],
        'ui-ux-designer': [
            {'title': 'Fondasi Desain UI/UX', 'level': 'beginner', 'lessons': [
                {'title': 'Perbedaan UI dan UX'}, {'title': 'Prinsip Dasar Desain Visual (Warna, Tipografi, Kontras)'},
                {'title': 'Hukum-hukum UX (Hick, Fitts, Miller)'}, {'title': 'Pengenalan Design Thinking Process'},
                {'title': 'Setup Tools: Figma'}, {'title': 'Dasar-dasar User Research'},
                {'title': 'Membuat User Persona'}
            ], 'projects': [{'title': 'Analisis Kompetitor dan Membuat User Persona', 'difficulty': 'Beginner', 'tech_stack': 'Figma, Miro'}]},
            {'title': 'Riset dan Arsitektur Informasi', 'level': 'beginner', 'lessons': [
                {'title': 'Metode Riset Kualitatif dan Kuantitatif'}, {'title': 'Membuat Empathy Map dan User Journey Map'},
                {'title': 'Arsitektur Informasi: Sitemap dan Card Sorting'}, {'title': 'Membuat User Flow Diagram'},
                {'title': 'Prinsip Usability Heuristics dari Nielsen'}, {'title': 'Struktur Navigasi dan Hierarki Konten'}
            ], 'projects': [{'title': 'Membuat User Flow dan Sitemap untuk Aplikasi E-commerce', 'difficulty': 'Beginner', 'tech_stack': 'Figma, FigJam'}]},
            {'title': 'Wireframing', 'level': 'intermediate', 'lessons': [
                {'title': 'Sketsa (Low-Fidelity Wireframing)'}, {'title': 'Membuat Digital Wireframe (Mid-Fidelity)'},
                {'title': 'Menggunakan Komponen dan Auto Layout di Figma'}, {'title': 'Desain untuk Berbagai Ukuran Layar (Responsive Design)'},
                {'title': 'Atomic Design Principle'}, {'title': 'Membuat Wireflow'}
            ], 'projects': [{'title': 'Wireframe Lengkap untuk Aplikasi Mobile', 'difficulty': 'Intermediate', 'tech_stack': 'Figma'}]},
            {'title': 'Desain Visual (UI)', 'level': 'intermediate', 'lessons': [
                {'title': 'Teori Warna dan Psikologi Warna'}, {'title': 'Tipografi untuk Web dan Mobile'},
                {'title': 'Membuat Moodboard dan Style Guide'}, {'title': 'Membangun Desain Sistem (Design System)'},
                {'title': 'Prinsip Grid dan Layout'}, {'title': 'Ikonografi dan Ilustrasi'},
                {'title': 'Aksesibilitas dalam Desain (WCAG)'}
            ], 'projects': [
                {'title': 'Membuat Desain Sistem Sederhana', 'difficulty': 'Intermediate', 'tech_stack': 'Figma'},
                {'title': 'Redesain Halaman Web dengan Fokus pada UI', 'difficulty': 'Intermediate', 'tech_stack': 'Figma'}
            ]},
            {'title': 'Prototyping Interaktif', 'level': 'advanced', 'lessons': [
                {'title': 'Dasar Prototyping di Figma'}, {'title': 'Smart Animate untuk Transisi Halus'},
                {'title': 'Membuat Prototipe Interaktif (High-Fidelity)'}, {'title': 'Prototyping untuk Berbagai Device'},
                {'title': 'Menggunakan Variabel dan Kondisional Logic'}, {'title': 'Berbagi dan Mengumpulkan Feedback pada Prototipe'}
            ], 'projects': [{'title': 'Prototipe Interaktif untuk Aplikasi Booking', 'difficulty': 'Advanced', 'tech_stack': 'Figma'}]},
            {'title': 'Usability Testing', 'level': 'advanced', 'lessons': [
                {'title': 'Apa itu Usability Testing?'}, {'title': 'Merencanakan Sesi Testing'},
                {'title': 'Moderated vs Unmoderated Testing'}, {'title': 'Membuat Skenario dan Tugas untuk Pengguna'},
                {'title': 'Menganalisis Hasil Testing'}, {'title': 'Membuat Laporan dan Rekomendasi Desain'}
            ], 'projects': [{'title': 'Melakukan Usability Testing pada Prototipe', 'difficulty': 'Advanced', 'tech_stack': 'Figma, Maze'}]},
            {'title': 'Desain untuk Platform Spesifik', 'level': 'expert', 'lessons': [
                {'title': 'Human Interface Guidelines (iOS)'}, {'title': 'Material Design (Android)'},
                {'title': 'Desain untuk Web vs Mobile'}, {'title': 'Desain untuk Wearables dan Smart TV'},
                {'title': 'Dark Mode Design'}, {'title': 'Animasi dan Microinteractions'}
            ], 'projects': [{'title': 'Merancang Aplikasi dengan Prinsip Material Design 3', 'difficulty': 'Expert', 'tech_stack': 'Figma'}]},
            {'title': 'Handoff ke Developer', 'level': 'expert', 'lessons': [
                {'title': 'Menyiapkan File Desain untuk Developer'}, {'title': 'Menggunakan Fitur Dev Mode di Figma'},
                {'title': 'Dokumentasi Desain yang Efektif'}, {'title': 'Kolaborasi dengan Tim Engineering'},
                {'title': 'Memahami Batasan Teknis'}, {'title': 'Quality Assurance (QA) dari Sisi Desain'}
            ], 'projects': [{'title': 'Melakukan Handoff Desain Lengkap', 'difficulty': 'Expert', 'tech_stack': 'Figma'}]},
            {'title': 'UX Writing', 'level': 'expert', 'lessons': [
                {'title': 'Prinsip-prinsip UX Writing'}, {'title': 'Voice and Tone'},
                {'title': 'Menulis untuk Komponen UI (Tombol, Form)'}, {'title': 'Pesan Error dan Notifikasi yang Efektif'},
                {'title': 'Onboarding dan Empty States'}, {'title': 'Lokalisasi dan Internasionalisasi'}
            ], 'projects': [{'title': 'Audit dan Perbaikan UX Writing pada Aplikasi', 'difficulty': 'Expert', 'tech_stack': 'Content Strategy'}]},
            {'title': 'Karier & Portofolio', 'level': 'expert', 'lessons': [
                {'title': 'Membangun Portofolio UI/UX yang Kuat'}, {'title': 'Studi Kasus: Dari Masalah hingga Solusi'},
                {'title': 'Wawancara UI/UX (Whiteboard Challenge)'}, {'title': 'Bekerja dengan Product Manager dan Stakeholder'},
                {'title': 'Metrik UX untuk Mengukur Keberhasilan Desain'}, {'title': 'Tren Masa Depan di Dunia UI/UX'}
            ], 'projects': [{'title': 'Membuat Studi Kasus Portofolio Lengkap', 'difficulty': 'Expert', 'tech_stack': 'Storytelling'}]}
        ],
        'generative-ai': [
            {'title': 'Fondasi Generative AI & LLMs', 'level': 'beginner', 'lessons': [
                {'title': 'Apa itu Generative AI?'}, {'title': 'Sejarah Singkat: Dari RNN ke Transformers'},
                {'title': 'Arsitektur Transformer Secara Intuitif'}, {'title': 'Large Language Models (LLMs): GPT, Llama, Gemini'},
                {'title': 'Konsep Embeddings dan Vector Space'}, {'title': 'Tokenization: BPE, WordPiece'},
                {'title': 'Setup Environment: Python, Hugging Face, dan API Keys'}, {'title': 'Etika dan Keamanan Dasar pada GenAI'}
            ], 'projects': [{'title': 'Eksplorasi Model dan Tokenizer di Hugging Face', 'difficulty': 'Beginner', 'tech_stack': 'Hugging Face'}]},
            {'title': 'Prompt Engineering & Interaksi Model', 'level': 'beginner', 'lessons': [
                {'title': 'Anatomi sebuah Prompt yang Efektif'}, {'title': 'Zero-shot, One-shot, dan Few-shot Prompting'},
                {'title': 'Teknik Prompting: Chain-of-Thought (CoT)'}, {'title': 'Teknik Prompting Tingkat Lanjut (Self-Consistency, Tree of Thoughts)'},
                {'title': 'Menggunakan LLM via API (OpenAI/Gemini/Anthropic)'}, {'title': 'Mengontrol Output: Temperature, Top-p, Max Tokens'},
                {'title': 'Menghindari Bias dan Konten Berbahaya'}, {'title': 'Prompt Chaining untuk Tugas Kompleks'}
            ], 'projects': [
                {'title': 'Membangun Chatbot Sederhana dengan API LLM', 'difficulty': 'Beginner', 'tech_stack': 'Python, OpenAI/Gemini API'},
                {'title': 'Membuat Aplikasi Rangkuman Teks', 'difficulty': 'Intermediate', 'tech_stack': 'Python, API LLM'}
            ]},
            {'title': 'Retrieval-Augmented Generation (RAG)', 'level': 'intermediate', 'lessons': [
                {'title': 'Masalah Halusinasi dan Knowledge Cutoff pada LLM'}, {'title': 'Konsep RAG: Memberi LLM Pengetahuan Eksternal'},
                {'title': 'Vector Databases (ChromaDB, Pinecone, FAISS)'}, {'title': 'Document Loading dan Text Chunking Strategies'},
                {'title': 'Model Embeddings (Sentence-Transformers)'}, {'title': 'Membangun Pipeline RAG Sederhana dengan LangChain'},
                {'title': 'Evaluasi Sederhana pada Sistem RAG (RAGAS)'}, {'title': 'Teknik Re-ranking untuk Hasil Lebih Baik'}
            ], 'projects': [{'title': 'Membangun Q&A Bot untuk Dokumen PDF', 'difficulty': 'Intermediate', 'tech_stack': 'Python, LangChain, ChromaDB'}]},
            {'title': 'Fine-Tuning LLMs', 'level': 'intermediate', 'lessons': [
                {'title': 'Kapan dan Mengapa Melakukan Fine-Tuning?'}, {'title': 'Persiapan Dataset untuk Fine-Tuning (Instruction Tuning)'},
                {'title': 'Full Fine-Tuning vs Parameter-Efficient Fine-Tuning (PEFT)'}, {'title': 'Konsep LoRA dan QLoRA'},
                {'title': 'Melakukan Fine-Tuning Model (e.g., GPT-2/Llama) dengan Hugging Face TRL'}, {'title': 'Menyimpan, Memuat, dan Menggabungkan Adapter LoRA'},
                {'title': 'Evaluasi Model yang Telah di-Fine-Tune'}
            ], 'projects': [{'title': 'Fine-Tune Model untuk Klasifikasi Teks Gaya Tertentu', 'difficulty': 'Advanced', 'tech_stack': 'Python, Hugging Face Transformers, PEFT'}]},
            {'title': 'Generasi Gambar dengan Diffusion Models', 'level': 'advanced', 'lessons': [
                {'title': 'Konsep Intuitif Diffusion Models (Stable Diffusion)'}, {'title': 'Text-to-Image Generation dan Negative Prompts'},
                {'title': 'Image-to-Image Generation (img2img) dan Denoising Strength'}, {'title': 'Inpainting dan Outpainting untuk Edit Gambar'},
                {'title': 'Menggunakan ControlNet untuk Kontrol Presisi (Pose, Depth, Canny)'}, {'title': 'Fine-tuning Diffusion Models (Dreambooth & LoRA)'},
                {'title': 'Membangun UI Sederhana untuk Stable Diffusion'}
            ], 'projects': [
                {'title': 'Membuat Gambar Konseptual dengan Stable Diffusion', 'difficulty': 'Intermediate', 'tech_stack': 'Python, Diffusers'},
                {'title': 'Melatih LoRA untuk Style Gambar Tertentu', 'difficulty': 'Advanced', 'tech_stack': 'Python, Diffusers'}
            ]},
            {'title': 'Multimodality: Menggabungkan Teks, Gambar, dan Audio', 'level': 'advanced', 'lessons': [
                {'title': 'Apa itu Model Multimodal? (CLIP, BLIP, LLaVA)'}, {'title': 'Visual Question Answering (VQA)'},
                {'title': 'Image Captioning Otomatis'}, {'title': 'Text-to-Speech (TTS) dan Speech-to-Text (STT) dengan Model Modern'},
                {'title': 'Generasi Video dari Teks (Sora, Kling)'}, {'title': 'Menganalisis Audio dengan Model AI'}
            ], 'projects': [{'title': 'Membangun Aplikasi Deskripsi Gambar Otomatis', 'difficulty': 'Advanced', 'tech_stack': 'Python, Hugging Face Transformers, Gradio'}]},
            {'title': 'Dasar-dasar AI Agents', 'level': 'expert', 'lessons': [
                {'title': 'Pergeseran dari Model ke Agent'}, {'title': 'Arsitektur Agent: LLM sebagai Otak (Controller)'},
                {'title': 'Planning: Teknik ReAct (Reasoning and Acting)'}, {'title': 'Memory pada Agent (Short-term, Long-term, Vector-based)'},
                {'title': 'Tool Use: Memberi Agent Kemampuan untuk Menggunakan API dan Fungsi'}, {'title': 'Membangun Agent Sederhana dengan LangChain'},
                {'title': 'Mengamati Proses Berpikir Agent (LangSmith)'}
            ], 'projects': [{'title': 'Membangun Agent Riset Sederhana Menggunakan SerpAPI', 'difficulty': 'Expert', 'tech_stack': 'Python, LangChain, SerpAPI'}]},
            {'title': 'Multi-Agent Systems & Agentic Workflows', 'level': 'expert', 'lessons': [
                {'title': 'Konsep Multi-Agent Systems untuk Tugas Kompleks'}, {'title': 'Pola Kolaborasi Agent (Hierarki, Debat, Lelang)'},
                {'title': 'Membangun Sistem Multi-Agent dengan LangGraph'}, {'title': 'Membangun Sistem Multi-Agent dengan Microsoft Autogen'},
                {'title': 'Human-in-the-loop: Supervisi dan Intervensi Agent'}, {'title': 'Agentic Workflows: Merangkai Agent untuk Tugas Multi-langkah'},
                {'title': 'Evaluasi dan Debugging Sistem Multi-Agent'}
            ], 'projects': [
                {'title': 'Membangun Tim Agent untuk Menulis Artikel (Penulis, Editor, Kritikus)', 'difficulty': 'Expert', 'tech_stack': 'Python, LangGraph'},
                {'title': 'Simulasi Tim Software Development dengan AI Agents (PM, Coder, Tester)', 'difficulty': 'Expert', 'tech_stack': 'Python, Autogen'}
            ]},
            {'title': 'Deployment & MLOps untuk GenAI', 'level': 'expert', 'lessons': [
                {'title': 'Tantangan Deployment Model Generatif'}, {'title': 'Containerisasi Aplikasi GenAI dengan Docker'},
                {'title': 'Men-deploy LLM dengan vLLM atau TGI'}, {'title': 'Serverless GPU untuk Inferensi'},
                {'title': 'Monitoring Drift pada Aplikasi RAG'}, {'title': 'Keamanan Aplikasi LLM (Prompt Injection, Data Poisoning)'}
            ], 'projects': [{'title': 'Men-deploy Aplikasi RAG sebagai Web App di Hugging Face Spaces', 'difficulty': 'Expert', 'tech_stack': 'Python, LangChain, Docker'}]},
            {'title': 'Etika dan Masa Depan GenAI', 'level': 'expert', 'lessons': [
                {'title': 'Bias dalam Model Generatif dan Cara Menguranginya'}, {'title': 'Deepfakes, Misinformasi, dan Deteksinya'},
                {'title': 'Hak Cipta (Copyright) dan Data Training'}, {'title': 'Dampak Lingkungan dari Training dan Inferensi LLM'},
                {'title': 'Masa Depan Pekerjaan dengan Kehadiran Agent AI'}, {'title': 'Jalan Menuju Artificial General Intelligence (AGI)'}
            ], 'projects': [{'title': 'Analisis dan Presentasi tentang Isu Etika GenAI Terkini', 'difficulty': 'Advanced', 'tech_stack': 'Riset, Presentasi'}]}
        ],
        'nlp-engineer': [
            {'title': 'Fondasi NLP dan Linguistik Komputasi', 'level': 'beginner', 'lessons': [
                {'title': 'Apa itu Natural Language Processing?'}, {'title': 'Sejarah NLP: Dari Aturan ke Statistik'},
                {'title': 'Konsep Linguistik Dasar (Morfologi, Sintaks, Semantik)'}, {'title': 'Setup Environment: Python, NLTK, spaCy'},
                {'title': 'Regular Expressions (Regex) untuk Pemrosesan Teks'}, {'title': 'Tantangan dalam NLP (Ambiguitas, Konteks)'}
            ], 'projects': [{'title': 'Ekstraksi Informasi dari Teks menggunakan Regex', 'difficulty': 'Beginner', 'tech_stack': 'Python, Regex'}]},
            {'title': 'Text Preprocessing dan Representasi Fitur', 'level': 'beginner', 'lessons': [
                {'title': 'Tokenization (Word & Sentence)'}, {'title': 'Stop Word Removal'},
                {'title': 'Stemming vs Lemmatization'}, {'title': 'Part-of-Speech (POS) Tagging'},
                {'title': 'Named Entity Recognition (NER)'}, {'title': 'Representasi Teks: Bag-of-Words (BoW)'},
                {'title': 'Representasi Teks: TF-IDF'}
            ], 'projects': [{'title': 'Membangun Pipeline Preprocessing Teks dengan NLTK/spaCy', 'difficulty': 'Beginner', 'tech_stack': 'Python, NLTK, spaCy'}]},
            {'title': 'Model NLP Klasik', 'level': 'intermediate', 'lessons': [
                {'title': 'Klasifikasi Teks dengan Naive Bayes'}, {'title': 'Klasifikasi Teks dengan Logistic Regression & SVM'},
                {'title': 'Analisis Sentimen sebagai Tugas Klasifikasi'}, {'title': 'Topic Modeling dengan Latent Dirichlet Allocation (LDA)'},
                {'title': 'N-grams dan Language Modeling Statistik'}, {'title': 'Evaluasi Model Klasifikasi (Akurasi, Presisi, Recall, F1)'}
            ], 'projects': [
                {'title': 'Klasifikasi Spam Email', 'difficulty': 'Intermediate', 'tech_stack': 'Python, Scikit-learn'},
                {'title': 'Analisis Sentimen Ulasan Produk', 'difficulty': 'Intermediate', 'tech_stack': 'Python, Scikit-learn'}
            ]},
            {'title': 'Word Embeddings', 'level': 'intermediate', 'lessons': [
                {'title': 'Keterbatasan Representasi One-Hot'}, {'title': 'Ide di Balik Distribusional Semantik'},
                {'title': 'Word2Vec (CBOW & Skip-gram)'}, {'title': 'GloVe: Global Vectors for Word Representation'},
                {'title': 'FastText untuk Kata-kata Langka'}, {'title': 'Visualisasi Word Embeddings dengan t-SNE'},
                {'title': 'Menggunakan Pre-trained Word Embeddings'}
            ], 'projects': [{'title': 'Mencari Analogi Kata dengan Word2Vec', 'difficulty': 'Intermediate', 'tech_stack': 'Python, Gensim'}]},
            {'title': 'Deep Learning untuk NLP: RNN & CNN', 'level': 'advanced', 'lessons': [
                {'title': 'Pengenalan Jaringan Saraf Tiruan untuk Teks'}, {'title': 'Recurrent Neural Networks (RNNs)'},
                {'title': 'Masalah Vanishing/Exploding Gradients'}, {'title': 'Long Short-Term Memory (LSTM) dan Gated Recurrent Unit (GRU)'},
                {'title': 'Arsitektur Encoder-Decoder dan Attention Mechanism'}, {'title': 'Convolutional Neural Networks (CNNs) untuk Klasifikasi Teks'}
            ], 'projects': [{'title': 'Klasifikasi Teks dengan LSTM menggunakan TensorFlow/PyTorch', 'difficulty': 'Advanced', 'tech_stack': 'Python, TensorFlow/PyTorch'}]},
            {'title': 'Arsitektur Transformer', 'level': 'advanced', 'lessons': [
                {'title': 'Keterbatasan RNN untuk Sekuens Panjang'}, {'title': 'Self-Attention: The "I am thinking about you" mechanism'},
                {'title': 'Multi-Head Attention'}, {'title': 'Positional Encodings'},
                {'title': 'Arsitektur Encoder-Decoder Transformer (Secara Rinci)'}, {'title': 'Revolusi Model Berbasis Transformer'}
            ], 'projects': [{'title': 'Membangun Transformer dari Awal (Bagian Encoder)', 'difficulty': 'Advanced', 'tech_stack': 'Python, TensorFlow/PyTorch'}]},
            {'title': 'Model Bahasa Pra-terlatih (BERT & GPT)', 'level': 'expert', 'lessons': [
                {'title': 'Konsep Transfer Learning di NLP'}, {'title': 'BERT: Bidirectional Encoder Representations from Transformers'},
                {'title': 'Tugas Pre-training BERT (Masked LM & Next Sentence Prediction)'}, {'title': 'Fine-tuning BERT untuk Tugas Downstream (Klasifikasi, NER)'},
                {'title': 'Arsitektur GPT dan Decoder-only Models'}, {'title': 'Perbedaan antara BERT dan GPT'},
                {'title': 'Menggunakan Hugging Face Transformers Library'}
            ], 'projects': [
                {'title': 'Fine-tuning BERT untuk Analisis Sentimen', 'difficulty': 'Expert', 'tech_stack': 'Python, Hugging Face'},
                {'title': 'Question Answering dengan Model Pra-terlatih', 'difficulty': 'Expert', 'tech_stack': 'Python, Hugging Face'}
            ]},
            {'title': 'Aplikasi NLP Tingkat Lanjut', 'level': 'expert', 'lessons': [
                {'title': 'Machine Translation'}, {'title': 'Text Summarization (Ekstraktif vs Abstraktif)'},
                {'title': 'Sistem Dialog dan Chatbots'}, {'title': 'Information Retrieval dan Search Engines'},
                {'title': 'Speech Recognition (ASR)'}, {'title': 'Text-to-Speech (TTS)'}
            ], 'projects': [{'title': 'Membangun Chatbot Sederhana berbasis Aturan dan Retrieval', 'difficulty': 'Expert', 'tech_stack': 'Python'}]},
            {'title': 'MLOps untuk NLP', 'level': 'expert', 'lessons': [
                {'title': 'Tantangan Deployment Model NLP'}, {'title': 'Menggunakan ONNX untuk Optimisasi Inferensi'},
                {'title': 'Men-deploy Model sebagai REST API dengan FastAPI'}, {'title': 'Containerisasi dengan Docker'},
                {'title': 'Monitoring Performa Model (Data Drift, Concept Drift)'}, {'title': 'Versioning Dataset dan Model'}
            ], 'projects': [{'title': 'Men-deploy Model Analisis Sentimen ke Docker', 'difficulty': 'Expert', 'tech_stack': 'Python, FastAPI, Docker'}]},
            {'title': 'Karier & Wawancara NLP', 'level': 'expert', 'lessons': [
                {'title': 'Membangun Portofolio NLP'}, {'title': 'Struktur Data & Algoritma untuk Wawancara'},
                {'title': 'Pertanyaan Wawancara Spesifik NLP'}, {'title': 'Desain Sistem untuk Aplikasi NLP (Contoh: Sistem Rekomendasi Artikel)'},
                {'title': 'Tetap Update dengan Riset Terbaru (ACL, EMNLP)'}, {'title': 'Etika dalam NLP (Bias, Fairness)'}
            ], 'projects': [{'title': 'Simulasi Wawancara Desain Sistem NLP', 'difficulty': 'Expert', 'tech_stack': 'Problem Solving'}]}
        ],
        'computer-vision-engineer': [
            {'title': 'Fondasi Computer Vision & Pemrosesan Gambar', 'level': 'beginner', 'lessons': [
                {'title': 'Apa itu Computer Vision?'}, {'title': 'Representasi Gambar Digital (Piksel, Channel, Grayscale)'},
                {'title': 'Histogram Gambar'}, {'title': 'Transformasi Geometris (Translasi, Rotasi, Skala)'},
                {'title': 'Operasi Piksel dan Filtering (Blur, Sharpen)'}, {'title': 'Deteksi Tepi (Edge Detection) dengan Canny'},
                {'title': 'Setup Environment: Python, OpenCV, Matplotlib'}
            ], 'projects': [{'title': 'Manipulasi Gambar Dasar dengan OpenCV', 'difficulty': 'Beginner', 'tech_stack': 'Python, OpenCV'}]},
            {'title': 'Feature Detection & Matching', 'level': 'beginner', 'lessons': [
                {'title': 'Konsep Fitur dalam Gambar'}, {'title': 'Deteksi Sudut (Harris Corner Detection)'},
                {'title': 'Scale-Invariant Feature Transform (SIFT)'}, {'title': 'Speeded Up Robust Features (SURF)'},
                {'title': 'Oriented FAST and Rotated BRIEF (ORB)'}, {'title': 'Feature Matching dengan Brute-Force Matcher'},
                {'title': 'Membuat Panorama Gambar Sederhana'}
            ], 'projects': [{'title': 'Image Stitching untuk Membuat Panorama', 'difficulty': 'Intermediate', 'tech_stack': 'Python, OpenCV'}]},
            {'title': 'Deep Learning & Convolutional Neural Networks (CNNs)', 'level': 'intermediate', 'lessons': [
                {'title': 'Keterbatasan Metode Klasik'}, {'title': 'Pengenalan Jaringan Saraf Tiruan'},
                {'title': 'Operasi Konvolusi'}, {'title': 'Layer-layer dalam CNN (Convolution, Pooling, Fully Connected)'},
                {'title': 'Membangun CNN Sederhana dengan TensorFlow/PyTorch'}, {'title': 'Fungsi Aktivasi (ReLU)'},
                {'title': 'Mencegah Overfitting (Dropout, Augmentasi Data)'}
            ], 'projects': [{'title': 'Klasifikasi Gambar (CIFAR-10) dengan CNN dari Awal', 'difficulty': 'Intermediate', 'tech_stack': 'Python, TensorFlow/PyTorch'}]},
            {'title': 'Arsitektur CNN Tingkat Lanjut', 'level': 'intermediate', 'lessons': [
                {'title': 'LeNet, AlexNet, VGGNet'}, {'title': 'GoogLeNet (Inception Modules)'},
                {'title': 'ResNet (Residual Connections)'}, {'title': 'DenseNet'},
                {'title': 'MobileNet & EfficientNet (Model Efisien)'}, {'title': 'Vision Transformers (ViT)'}
            ], 'projects': [{'title': 'Membandingkan Performa Arsitektur CNN yang Berbeda', 'difficulty': 'Intermediate', 'tech_stack': 'Python, TensorFlow/PyTorch'}]},
            {'title': 'Transfer Learning & Fine-Tuning', 'level': 'advanced', 'lessons': [
                {'title': 'Konsep Transfer Learning'}, {'title': 'Menggunakan Model Pra-terlatih (Pre-trained Models)'},
                {'title': 'Feature Extraction'}, {'title': 'Fine-Tuning: Melatih Sebagian atau Seluruh Layer'},
                {'title': 'Strategi Learning Rate untuk Fine-Tuning'}, {'title': 'Augmentasi Data untuk Computer Vision'}
            ], 'projects': [
                {'title': 'Klasifikasi Ras Anjing', 'difficulty': 'Advanced', 'tech_stack': 'Python, TensorFlow/PyTorch'},
                {'title': 'Deteksi Penyakit Daun Tanaman', 'difficulty': 'Advanced', 'tech_stack': 'Python, TensorFlow/PyTorch'}
            ]},
            {'title': 'Object Detection', 'level': 'advanced', 'lessons': [
                {'title': 'Tugas Object Detection (Klasifikasi + Lokalisasi)'}, {'title': 'Metrik Evaluasi (Intersection over Union - IoU, mAP)'},
                {'title': 'Model Berbasis Region Proposal (R-CNN, Fast R-CNN, Faster R-CNN)'}, {'title': 'Model Single-Shot (YOLO, SSD)'},
                {'title': 'Menggunakan YOLO untuk Deteksi Objek Real-time'}, {'title': 'Non-Maximum Suppression (NMS)'}
            ], 'projects': [{'title': 'Deteksi Objek pada Gambar Kustom dengan YOLO', 'difficulty': 'Advanced', 'tech_stack': 'Python, YOLO'}]},
            {'title': 'Image Segmentation', 'level': 'expert', 'lessons': [
                {'title': 'Semantic Segmentation'}, {'title': 'Instance Segmentation'},
                {'title': 'Panoptic Segmentation'}, {'title': 'Arsitektur Fully Convolutional Networks (FCN)'},
                {'title': 'U-Net untuk Segmentasi Medis'}, {'title': 'Mask R-CNN untuk Instance Segmentation'},
                {'title': 'DeepLab untuk Semantic Segmentation'}
            ], 'projects': [{'title': 'Segmentasi Jalan pada Gambar Satelit', 'difficulty': 'Expert', 'tech_stack': 'Python, TensorFlow/PyTorch, U-Net'}]},
            {'title': 'Generative Models untuk Gambar', 'level': 'expert', 'lessons': [
                {'title': 'Autoencoders'}, {'title': 'Variational Autoencoders (VAEs)'},
                {'title': 'Generative Adversarial Networks (GANs)'}, {'title': 'Arsitektur DCGAN'},
                {'title': 'Conditional GANs'}, {'title': 'Image Style Transfer'},
                {'title': 'Diffusion Models untuk Generasi Gambar (DALL-E, Midjourney)'}
            ], 'projects': [{'title': 'Generasi Digit Tulisan Tangan dengan GAN', 'difficulty': 'Expert', 'tech_stack': 'Python, TensorFlow/PyTorch'}]},
            {'title': 'Aplikasi CV & MLOps', 'level': 'expert', 'lessons': [
                {'title': 'Facial Recognition'}, {'title': 'Optical Character Recognition (OCR)'},
                {'title': 'Analisis Video dan Action Recognition'}, {'title': 'Computer Vision di Edge Devices (TensorFlow Lite)'},
                {'title': 'Deployment Model CV sebagai API'}, {'title': 'Data Annotation Tools (LabelImg, CVAT)'}
            ], 'projects': [
                {'title': 'Sistem Absensi dengan Deteksi Wajah', 'difficulty': 'Expert', 'tech_stack': 'Python, OpenCV, Dlib'},
                {'title': 'Men-deploy Model Klasifikasi Gambar ke Web', 'difficulty': 'Expert', 'tech_stack': 'Python, FastAPI, Docker'}
            ]},
            {'title': 'Karier & Wawancara CV', 'level': 'expert', 'lessons': [
                {'title': 'Membangun Portofolio Computer Vision'}, {'title': 'Struktur Data & Algoritma untuk Wawancara'},
                {'title': 'Pertanyaan Wawancara Spesifik Computer Vision'}, {'title': 'Desain Sistem untuk Aplikasi CV (Contoh: Sistem Monitoring Lalu Lintas)'},
                {'title': 'Tetap Update dengan Riset Terbaru (CVPR, ICCV)'}, {'title': 'Etika dalam Computer Vision (Bias, Privasi)'}
            ], 'projects': [{'title': 'Simulasi Wawancara Desain Sistem CV', 'difficulty': 'Expert', 'tech_stack': 'Problem Solving'}]}
        ]
    }
    
    def fill_project_defaults(project_data):
        project_data.setdefault('description', f"Proyek tantangan untuk mengaplikasikan skill {project_data.get('tech_stack', '')}.")
        project_data.setdefault('project_goals', 'Menerapkan konsep yang telah dipelajari dalam sebuah proyek nyata.')
        project_data.setdefault('evaluation_criteria', 'Fungsionalitas, kebersihan kode, dan penerapan konsep yang benar.')
        project_data.setdefault('resources', 'Dokumentasi resmi dan materi dari modul terkait.')
        return project_data

    # Langkah 3: Perulangan cerdas untuk menambah HANYA data baru
    for career_path, modules in new_career_data.items():
        print(f"--- Memeriksa data untuk: {career_path.replace('-', ' ').title()} ---")
        for i, module_data in enumerate(modules, 1):
            existing_module = Module.query.filter_by(title=module_data['title'], career_path=career_path).first()
            
            if existing_module:
                print(f"   -> Modul '{module_data['title']}' sudah ada, dilewati.")
                continue

            print(f"   -> Menambahkan modul baru: '{module_data['title']}'")
            new_module = Module(
                title=module_data['title'], 
                order=i, 
                career_path=career_path, 
                roadmap_id=roadmap_umum.id,
                level=module_data.get('level', 'beginner')
            )
            db.session.add(new_module)
            db.session.flush()

            for j, lesson_data in enumerate(module_data.get('lessons', []), 1):
                new_lesson = Lesson(
                    title=lesson_data['title'],
                    order=j,
                    module_id=new_module.id,
                    description=lesson_data.get('description', 'Deskripsi akan segera ditambahkan.'),
                    estimated_time=lesson_data.get('estimated_time', 30)
                )
                db.session.add(new_lesson)
            
            for project_data in module_data.get('projects', []):
                full_project_data = fill_project_defaults(project_data)
                new_project = Project(
                    title=full_project_data['title'], 
                    description=full_project_data.get('description'), 
                    difficulty=full_project_data['difficulty'],
                    module_id=new_module.id, 
                    project_goals=full_project_data.get('project_goals'), 
                    tech_stack=full_project_data['tech_stack'],
                    evaluation_criteria=full_project_data.get('evaluation_criteria'), 
                    resources=full_project_data.get('resources')
                )
                db.session.add(new_project)
    
    db.session.commit()
    
    print("\n" + "=" * 60)
    print("✅ PROSES SEEDING SELESAI! ✅")
    print("Hanya career path baru yang ditambahkan. Data lama Anda aman.")
    print("=" * 60)