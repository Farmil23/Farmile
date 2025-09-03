# app/routes.py (Versi Final, Lengkap, dan Terstruktur)
from flask import (render_template, redirect, url_for, request, Blueprint, 
                   abort, flash, jsonify, current_app)
from flask_login import current_user, login_required, login_user, logout_user
import json
from app import db, oauth, ark_client
from app.models import (User, Project, ProjectSubmission, ChatMessage, 
                        ChatSession, Module, Lesson, UserProgress)


# app/routes.py -> di bagian atas
from sqlalchemy.orm import subqueryload
bp = Blueprint('routes', __name__)


# --- Helper Function untuk Generate Roadmap ---
def _generate_roadmap_for_user(user):
    """Fungsi internal untuk membuat roadmap menggunakan AI."""
    # Hapus roadmap lama jika ada untuk path yang sama
    Module.query.filter_by(user_id=user.id, career_path=user.career_path).delete()
    db.session.commit()
    
    prompt = f"""
    Anda adalah seorang desainer kurikulum ahli untuk mahasiswa IT. Buat roadmap belajar detail untuk mahasiswa semester {user.semester} dengan fokus karier "{user.career_path}".
    Roadmap harus terdiri dari 3 hingga 5 modul utama. Setiap modul harus berisi 3 hingga 5 materi (lesson) yang relevan.
    Berikan jawaban HANYA dalam format JSON yang valid, dengan struktur seperti ini:
    {{"modules": [{{"title": "Judul Modul", "order": 1, "lessons": [{{"title": "Judul Materi", "order": 1, "lesson_type": "article", "estimated_time": 30}}]}}]}}
    """
    try:
        completion = ark_client.chat.completions.create(
            model=current_app.config['MODEL_ENDPOINT_ID'],
            messages=[{"role": "user", "content": prompt}]
        )
        ai_response_str = completion.choices[0].message.content
        if "```json" in ai_response_str:
            ai_response_str = ai_response_str.split("```json")[1].split("```")[0].strip()
        
        roadmap_data = json.loads(ai_response_str)

        for module_data in roadmap_data.get('modules', []):
            new_module = Module(title=module_data['title'], order=module_data['order'],
                                career_path=user.career_path, user_id=user.id)
            db.session.add(new_module)
            db.session.flush() 
            for lesson_data in module_data.get('lessons', []):
                new_lesson = Lesson(
                    title=lesson_data.get('title', 'Materi Baru'),
                    order=lesson_data.get('order', 1),
                    lesson_type=lesson_data.get('lesson_type', 'article'),
                    estimated_time=lesson_data.get('estimated_time', 30),
                    module_id=new_module.id
                )
                db.session.add(new_lesson)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Gagal membuat roadmap: {e}")
        return False

# ===============================================
# RUTE UTAMA & ONBOARDING
# ===============================================
@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('routes.dashboard'))
    return render_template('landing_page.html', title='Selamat Datang di FARSIGHT')

@bp.route('/dashboard')
@login_required
def dashboard():
    # --- LOGIKA PERHITUNGAN STATISTIK (DIPERBAIKI) ---
    completed_lessons_count = current_user.user_progress.count()
    
    # Menghitung total materi dengan cara yang benar
    modules_for_path = Module.query.join(User).filter(User.id==current_user.id, User.career_path==current_user.career_path).all()

    total_lessons = db.session.query(Lesson).join(Module).filter(Module.id.in_([m.id for m in modules_for_path])).count()
    
    progress_percentage = 0
    if total_lessons > 0:
        progress_percentage = int((completed_lessons_count / total_lessons) * 100)

    # Mengambil data untuk kartu "Aktivitas Terbaru"
    recent_sessions = current_user.chat_sessions.order_by(ChatSession.timestamp.desc()).limit(1).all()
    recent_submissions = current_user.submissions.order_by(ProjectSubmission.id.desc()).limit(1).all()
    recent_progress = current_user.user_progress.order_by(UserProgress.completed_at.desc()).limit(1).all()
    
    return render_template(
        'dashboard.html', 
        title='Dasbor Anda',
        progress_percentage=progress_percentage,
        recent_sessions=recent_sessions,
        recent_submissions=recent_submissions,
        recent_progress=recent_progress,
        Lesson=Lesson
    )

@bp.route('/login')
def login():
    redirect_uri = url_for('routes.auth', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@bp.route('/auth')
def auth():
    token = oauth.google.authorize_access_token()
    user_info = token.get('userinfo')
    user = User.query.filter_by(google_id=user_info['sub']).first()
    if not user:
        user = User(google_id=user_info['sub'], name=user_info['name'], 
                    email=user_info['email'], profile_pic=user_info['picture'])
        db.session.add(user)
        db.session.commit()
    login_user(user)
    if not current_user.has_completed_onboarding:
        return redirect(url_for('routes.onboarding'))
    return redirect(url_for('routes.dashboard'))

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.index'))

@bp.route('/onboarding')
@login_required
def onboarding():
    if current_user.has_completed_onboarding:
        return redirect(url_for('routes.dashboard'))
    return render_template('onboarding.html', title='Selamat Datang')

@bp.route('/complete-onboarding', methods=['POST'])
@login_required
def complete_onboarding():
    data = request.get_json()
    current_user.name = data.get('user_name', current_user.name)
    current_user.semester = int(data.get('semester', 1))
    current_user.career_path = data.get('career_focus')
    current_user.has_completed_onboarding = True
    db.session.commit()
    return jsonify({'status': 'success', 'redirect_url': url_for('routes.dashboard')})


# ===============================================
# RUTE ROADMAP BELAJAR (VERSI DIPERBAIKI)
# ===============================================
# app/routes.py

@bp.route('/roadmap')
@login_required
def roadmap():
    if not current_user.career_path:
        flash('Selesaikan onboarding untuk menentukan jalur karier Anda.', 'warning')
        return redirect(url_for('routes.onboarding'))

    all_modules = Module.query.filter(
        ((Module.user_id == current_user.id) | (Module.user_id == None)),
        (Module.career_path == current_user.career_path)
    ).options(
        subqueryload(Module.lessons), 
        subqueryload(Module.projects)
    ).order_by(Module.order).all()
    
    # --- LOGIKA PROGRES BARU ---
    all_lesson_ids = {lesson.id for module in all_modules for lesson in module.lessons}
    
    completed_progress = UserProgress.query.filter(
        UserProgress.user_id == current_user.id,
        UserProgress.lesson_id.in_(all_lesson_ids)
    ).all()
    completed_lesson_ids = {p.lesson_id for p in completed_progress}

    total_lessons = len(all_lesson_ids)
    progress_percentage = int((len(completed_lesson_ids) / total_lessons) * 100) if total_lessons > 0 else 0
    
    return render_template('roadmap.html', 
                           title="Roadmap Belajar", 
                           modules=all_modules,
                           completed_lesson_ids=completed_lesson_ids, # Kirim ID pelajaran yang selesai
                           progress=progress_percentage)
# app/routes.py

@bp.route('/lesson/<int:lesson_id>')
@login_required
def lesson_detail(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    # Pastikan lesson ini bagian dari roadmap user
    if lesson.module.career_path != current_user.career_path and (lesson.module.user_id != current_user.id and lesson.module.user_id is not None):
        abort(403)
        
    # Cek apakah lesson ini sudah diselesaikan oleh user
    progress = UserProgress.query.filter_by(user_id=current_user.id, lesson_id=lesson.id).first()
    is_completed = True if progress else False
    
    return render_template('lesson_detail.html', 
                           title=lesson.title, 
                           lesson=lesson, 
                           is_completed=is_completed)

# app/routes.py -> Tambahkan ini di bagian RUTE PROYEK

@bp.route('/project/<int:project_id>')
@login_required
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    # Pastikan proyek ini bagian dari roadmap user
    if project.module.career_path != current_user.career_path and (project.module.user_id != current_user.id and project.module.user_id is not None):
        abort(403)
    return render_template('project_detail.html', title=project.title, project=project)

# app/routes.py -> Ubah fungsi complete_lesson yang sudah ada

# app/routes.py

@bp.route('/complete-lesson/<int:lesson_id>', methods=['POST'])
@login_required
def complete_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    progress = UserProgress.query.filter_by(user_id=current_user.id, lesson_id=lesson.id).first()

    if not progress:
        new_progress = UserProgress(user_id=current_user.id, module_id=lesson.module_id, lesson_id=lesson.id)
        db.session.add(new_progress)
        db.session.commit()
        flash('Materi berhasil ditandai selesai!', 'success')
    
    # --- LOGIKA REDIRECT BARU ---
    source = request.form.get('source')
    if source == 'roadmap':
        return redirect(url_for('routes.roadmap'))
    else: # Default-nya kembali ke halaman detail
        return redirect(url_for('routes.lesson_detail', lesson_id=lesson_id))
# app/routes.py -> Tambahkan fungsi baru ini

# app/routes.py

@bp.route('/uncomplete-lesson/<int:lesson_id>', methods=['POST'])
@login_required
def uncomplete_lesson(lesson_id):
    progress = UserProgress.query.filter_by(user_id=current_user.id, lesson_id=lesson_id).first()
    if progress:
        db.session.delete(progress)
        db.session.commit()
        flash('Materi ditandai belum selesai.', 'info')

    # --- LOGIKA REDIRECT BARU ---
    source = request.form.get('source')
    if source == 'roadmap':
        return redirect(url_for('routes.roadmap'))
    else: # Default-nya kembali ke halaman detail
        return redirect(url_for('routes.lesson_detail', lesson_id=lesson_id))

# app/routes.py

# Tambahkan fungsi baru ini di mana saja (misalnya, setelah 'complete_onboarding')

@bp.route('/change-career-path', methods=['POST'])
@login_required
def change_career_path():
    new_path = request.form.get('new_path')
    
    # Validasi sederhana
    if new_path in ['frontend', 'backend', 'data-analyst']:
        current_user.career_path = new_path
        db.session.commit()
        flash(f"Jalur karier berhasil diubah ke {new_path.replace('-', ' ').title()}!", 'success')
    else:
        flash("Jalur karier tidak valid.", 'danger')
        
    return redirect(url_for('routes.roadmap'))


"""
@bp.route('/generate-roadmap', methods=['POST'])
@login_required
def generate_roadmap():
    if _generate_roadmap_for_user(current_user):
        flash('Roadmap belajar personal Anda berhasil dibuat ulang oleh AI!', 'success')
    else:
        flash('Maaf, AI gagal membuat roadmap. Coba lagi.', 'danger')
    return redirect(url_for('routes.roadmap'))
""" 

# ===============================================
# RUTE PROYEK & WAWANCARA
# ===============================================
@bp.route('/my-projects')
@login_required
def my_projects():
    submissions = ProjectSubmission.query.filter_by(user_id=current_user.id).order_by(ProjectSubmission.id.desc()).all()
    return render_template('my_projects.html', title="Proyek Saya", submissions=submissions)

# app/routes.py

@bp.route('/select-project')
@login_required
def select_project():
    if not current_user.career_path:
        flash('Selesaikan onboarding untuk menentukan jalur karier.', 'warning')
        return redirect(url_for('routes.dashboard'))
    
    # Ambil ID proyek yang sudah disubmit oleh user
    submitted_project_ids = [sub.project_id for sub in current_user.submissions]
    
    # --- LOGIKA BARU ---
    # Ambil proyek yang ada di roadmap user, BUKAN challenge, dan belum disubmit
    available_projects = Project.query.join(Module).filter(
        Module.career_path == current_user.career_path,
        Project.is_challenge == False,  # Hanya tampilkan proyek roadmap biasa
        Project.id.notin_(submitted_project_ids)
    ).all()
    
    return render_template('select_project.html', title="Pilih Proyek dari Roadmap", projects=available_projects)


# app/routes.py

@bp.route('/challenges')
@login_required
def challenge_projects():
    # Ambil ID proyek yang sudah disubmit oleh user
    submitted_project_ids = [sub.project_id for sub in current_user.submissions]

    # Ambil semua proyek yang ditandai sebagai challenge dan belum disubmit
    challenge_projects = Project.query.filter(
        Project.is_challenge == True,
        Project.id.notin_(submitted_project_ids)
    ).order_by(Project.difficulty).all() # Urutkan berdasarkan kesulitan

    return render_template('challenge_projects.html', title="Tantangan Proyek", projects=challenge_projects)


@bp.route('/submit-project/<int:project_id>', methods=['POST'])
@login_required
def submit_project(project_id):
    project = Project.query.get_or_404(project_id)
    project_link = request.form.get('project_link')
    submission = ProjectSubmission(project_id=project.id, user_id=current_user.id, project_link=project_link)
    db.session.add(submission)
    db.session.commit()
    flash(f"Proyek '{project.title}' berhasil disubmit!", 'success')
    return redirect(url_for('routes.my_projects'))

@bp.route('/interview/<int:submission_id>')
@login_required
def interview(submission_id):
    submission = ProjectSubmission.query.get_or_404(submission_id)
    if submission.user_id != current_user.id: 
        abort(403)
    return render_template('interview.html', title=f"Wawancara {submission.project.title}", submission=submission)

@bp.route('/cancel-submission/<int:submission_id>', methods=['POST'])
@login_required
def cancel_submission(submission_id):
    submission = ProjectSubmission.query.get_or_404(submission_id)
    if submission.user_id != current_user.id: 
        abort(403)
    db.session.delete(submission)
    db.session.commit()
    flash('Submission proyek berhasil dibatalkan.', 'success')
    return redirect(url_for('routes.my_projects'))


# ===============================================
# RUTE CHATBOT
# ===============================================
@bp.route('/chatbot')
@login_required
def chatbot():
    # Ambil session terbaru milik user
    latest_session = (
        ChatSession.query
        .filter_by(user_id=current_user.id)
        .order_by(ChatSession.timestamp.desc())
        .first()
    )

    if latest_session:
        # Kalau belum ada pesan → tambahin welcome message
        if not latest_session.messages:
            welcome_message = ChatMessage(
                session_id=latest_session.id,
                user_id=current_user.id,
                role='assistant',
                content=(
                    f"Halo {current_user.name.split()[0]}! 😎✌️\n"
                    f"Welcome back di dashboard Alur Belajar "
                    f"{current_user.career_path.replace('-', ' ').title() if current_user.career_path else 'Explorer'}! 🎉\n\n"
                    f"Kamu sekarang ada di semester "
                    f"{current_user.semester if current_user.semester else 'misterius 🤔'}.\n"
                    f"Keep going, jangan lupa tiap progress kecil itu berarti banget! 💡🔥\n\n"
                    f"Mau lanjut ngulik apa hari ini?"
                )
            )
            db.session.add(welcome_message)
            db.session.commit()

        return redirect(url_for('routes.chatbot_session', session_id=latest_session.id))

    else:
        # Kalau belum ada session sama sekali → buat baru
        new_session = ChatSession(user_id=current_user.id, title="Perkenalan")
        db.session.add(new_session)
        db.session.flush()

        welcome_message = ChatMessage(
            session_id=new_session.id,
            user_id=current_user.id,
            role='assistant',
            content=(
                f"Halo {current_user.name.split()[0]}! 👋 Aku Farmile, mentor AI kamu.\n\n"
                f"Aku lihat kamu lagi di jalur **{current_user.career_path.replace('-', ' ').title() if current_user.career_path else 'Explorer'}** "
                f"dan sekarang ada di semester **{current_user.semester if current_user.semester else 'belum ditentukan'}**. 🎓\n\n"
                f"Siap bantuin apa hari ini? 🚀"
            )
        )

        db.session.add(welcome_message)
        db.session.commit()

        return redirect(url_for('routes.chatbot_session', session_id=new_session.id))


@bp.route('/chatbot/new', methods=['POST'])
@login_required
def new_chat_session():
    new_session = ChatSession(user_id=current_user.id, title="Percakapan Baru")
    db.session.add(new_session)
    db.session.flush()  # <-- supaya new_session.id tersedia

    new_topic_message = ChatMessage(
        session_id=new_session.id, 
        user_id=current_user.id, 
        role='assistant', 
        content="Yeay, topik baru dibuka! 🎉 Mau ngobrol soal apa dulu nih?"
    )

    db.session.add(new_topic_message)
    db.session.commit()
    return redirect(url_for('routes.chatbot_session', session_id=new_session.id))


@bp.route('/chatbot/<int:session_id>')
@login_required
def chatbot_session(session_id):
    session = ChatSession.query.get_or_404(session_id)
    if session.user_id != current_user.id:
        abort(403)
    all_sessions = ChatSession.query.filter_by(user_id=current_user.id).order_by(ChatSession.timestamp.desc()).all()
    messages = session.messages.order_by(ChatMessage.timestamp.asc()).all()
    return render_template('chatbot.html', title=session.title, 
                           current_session=session, all_sessions=all_sessions, history=messages)

@bp.route('/rename-session/<int:session_id>', methods=['POST'])
@login_required
def rename_session(session_id):
    session = ChatSession.query.get_or_404(session_id)
    if session.user_id != current_user.id:
        abort(403)
    new_title = request.get_json().get('title', '').strip()
    if new_title:
        session.title = new_title
        db.session.commit()
        return jsonify({'status': 'success', 'new_title': session.title})
    return jsonify({'status': 'error', 'message': 'Nama tidak boleh kosong'}), 400

@bp.route('/chatbot/new/lesson/<int:lesson_id>', methods=['POST'])
@login_required
def new_chat_for_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)

    new_session = ChatSession(user_id=current_user.id, title=f"Diskusi: {lesson.title}")
    db.session.add(new_session)
    db.session.flush()  # <-- id langsung keluar

    welcome_message_content = (
        f"Selamat datang di materi **{lesson.title}**. 📘✨\n\n"
        f"Kamu bisa mulai belajar dari sumber berikut: {lesson.url if lesson.url else 'Belum ada link, tapi jangan khawatir, materinya akan segera siap untukmu.'}\n\n"
        f"Kenapa topik ini penting? Karena pemahaman di sini bakal jadi kunci untuk menguasai langkah berikutnya. 🔑\n"
        f"Kalau ada bagian yang bikin kamu bingung atau justru bikin penasaran, ayo kita bahas bareng supaya makin jelas dan seru 🚀"
    )

    welcome_message = ChatMessage(
        session_id=new_session.id, 
        user_id=current_user.id, 
        role='assistant', 
        content=welcome_message_content
    )
    db.session.add(welcome_message)
    db.session.commit()

    return redirect(url_for('routes.chatbot_session', session_id=new_session.id))
# ===============================================
# RUTE PENGATURAN & PROFIL
# ===============================================
@bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', title="Profil Saya")

@bp.route('/settings/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.name = request.form.get('name')
        current_user.semester = int(request.form.get('semester'))
        db.session.commit()
        flash('Profil berhasil diperbarui!', 'success')
        return redirect(url_for('routes.profile'))
    return render_template('edit_profile.html', title="Edit Profil")


# ===============================================
# RUTE API UNTUK AI
# ===============================================
@bp.route('/chat-ai/<int:session_id>', methods=['POST'])
@login_required
def chat_ai(session_id):
    if not ark_client:
        return jsonify({'error': 'Layanan AI saat ini tidak tersedia.'}), 503
    
    session = ChatSession.query.get_or_404(session_id)
    if session.user_id != current_user.id:
        abort(403)
    
    user_message_content = request.get_json().get('message', '').strip()
    if not user_message_content:
        return jsonify({'error': 'Pesan tidak boleh kosong'}), 400

    # Logika untuk "Perintah Cepat"
    if user_message_content == '/buatkan_roadmap':
        if _generate_roadmap_for_user(current_user):
            ai_response_content = "Tentu! Saya telah membuatkan roadmap belajar personal baru untukmu. Silakan cek halaman 'Roadmap Belajar' untuk melihat hasilnya."
        else:
            ai_response_content = "Maaf, sepertinya saya gagal membuat roadmap saat ini. Coba lagi beberapa saat."
        user_message = ChatMessage(session_id=session.id, user_id=current_user.id, role='user', content=user_message_content)
        ai_message = ChatMessage(session_id=session.id, user_id=current_user.id, role='assistant', content=ai_response_content)
        db.session.add_all([user_message, ai_message])
        db.session.commit()
        return jsonify({'response': ai_response_content})

    user_message = ChatMessage(session_id=session.id, user_id=current_user.id, role='user', content=user_message_content)
    db.session.add(user_message)
    
    recent_history = session.messages.order_by(ChatMessage.timestamp.desc()).limit(10).all()
    recent_history.reverse()

    completed_lessons_count = UserProgress.query.filter_by(user_id=current_user.id).count()
    user_context = (
        f"Nama pengguna: {current_user.name}, seorang mahasiswa semester {current_user.semester}. "
        f"Fokus karier yang ia minati adalah {current_user.career_path}. "
        f"Progres belajar saat ini: sudah menyelesaikan {completed_lessons_count} modul di roadmap."
    )
    system_prompt = (
        "Anda adalah Farmile, seorang mentor karier AI yang berpengalaman, ramah, dan suportif. Bayangkan diri Anda sebagai mentor yang sudah membimbing banyak generasi profesional AI, sehingga jawaban Anda selalu penuh wawasan, empati, dan motivasi.  Tugas Anda: 1. Berikan arahan karier di bidang AI yang jelas, praktis, dan sesuai dengan kondisi nyata industri.  2. Gunakan informasi konteks pengguna untuk membuat jawaban terasa personal, relevan, dan spesifik.  3. Jelaskan konsep atau saran dengan bahasa yang mudah dipahami, hindari jargon berlebihan, dan berikan contoh nyata atau analogi bila perlu.  4. Selalu dorong pengguna agar percaya diri, termotivasi, dan merasa didukung dalam perjalanan mereka.  5. Tunjukkan sikap mentor berpengalaman: sabar, bijak, dan visioner.  Nada komunikasi:  - Ramah dan hangat, seperti seorang mentor yang ingin melihat muridnya sukses.  - Positif dan membangun semangat, tanpa menggurui.  - Fokus pada peluang, solusi, dan langkah nyata.  Konteks Pengguna: {user_context}"
    )
    
    messages = [{"role": "system", "content": system_prompt}]
    for msg in recent_history:
        messages.append({"role": msg.role, "content": msg.content})
    
    try:
        completion = ark_client.chat.completions.create(
            model=current_app.config['MODEL_ENDPOINT_ID'],
            messages=messages
        )
        ai_response_content = completion.choices[0].message.content
        
        ai_message = ChatMessage(session_id=session.id, user_id=current_user.id, role='assistant', content=ai_response_content)
        db.session.add(ai_message)
        db.session.commit()
        
        return jsonify({'response': ai_response_content})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"BytePlus API Error: {e}")
        return jsonify({'error': 'Gagal menghubungi layanan AI, silakan coba lagi.'}), 500