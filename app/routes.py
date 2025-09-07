from flask import (render_template, redirect, url_for, request, Blueprint, 
                   abort, flash, jsonify, current_app)
from flask_login import current_user, login_required, logout_user, login_user
import json
from app import db, oauth, ark_client
from app.models import (User, Project, ProjectSubmission, ChatMessage, 
                        ChatSession, Module, Lesson, UserProgress, 
                        InterviewMessage, Task, Event, Note) # <-- Model baru diimpor
from sqlalchemy.orm import subqueryload
# File: app/routes.py
from datetime import datetime, timedelta
import re
import pytz
    # Tambahkan ini di app/routes.py
from flask import session # Pastikan session diimpor dari flask
    
from sqlalchemy import or_
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



# GANTI FUNGSI LAMA DENGAN VERSI BARU YANG JAUH LEBIH PINTAR INI
def _parse_human_readable_time(time_str: str) -> datetime:
    """
    Menerjemahkan string waktu bahasa manusia (e.g., 'besok jam 3 sore', '9 september jam 2') 
    menjadi objek datetime yang akurat.
    """
    now = datetime.now()
    time_str_lower = time_str.lower()
    
    # --- LOGIKA BARU UNTUK PARSING TANGGAL SPESIFIK ---
    base_date = now
    
    month_map = {
        'januari': 1, 'februari': 2, 'maret': 3, 'april': 4, 'mei': 5, 'juni': 6, 
        'juli': 7, 'agustus': 8, 'september': 9, 'oktober': 10, 'november': 11, 'desember': 12
    }

    # Coba cari format "tanggal bulan" (e.g., "9 september")
    date_match = re.search(r'(\d{1,2})\s+(' + '|'.join(month_map.keys()) + r')', time_str_lower)
    
    if date_match:
        day = int(date_match.group(1))
        month_name = date_match.group(2)
        month = month_map[month_name]
        year = now.year
        
        # Jika tanggal yang disebutkan sudah lewat tahun ini, asumsikan tahun depan
        if now.month > month or (now.month == month and now.day > day):
            year += 1
            
        try:
            base_date = base_date.replace(year=year, month=month, day=day)
        except ValueError:
            # Menangani tanggal tidak valid seperti 31 Februari
            pass 
    elif "besok" in time_str_lower:
        base_date = now + timedelta(days=1)
    # Jika tidak ada tanggal spesifik atau "besok", maka default-nya adalah hari ini (base_date = now)

    # --- Logika parsing waktu (jam dan menit) yang sudah ada ---
    match = re.search(r'(\d{1,2})[:.]?(\d{2})?|(\d{1,2})\s?(pagi|siang|sore|malam)', time_str_lower)
    if not match:
        # Jika tidak ada jam, set default ke jam 9 pagi
        return base_date.replace(hour=9, minute=0, second=0, microsecond=0)

    hour, minute = 0, 0
    g = match.groups()
    if g[0]:
        hour = int(g[0])
        minute = int(g[1]) if g[1] else 0
    elif g[2]:
        hour = int(g[2])
        period = g[3]
        if period in ['sore', 'malam'] and hour < 12:
            hour += 12
        if period == 'pagi' and hour == 12: hour = 0
        if period == 'malam' and hour == 12:
             hour = 0
             base_date += timedelta(days=1)

    return base_date.replace(hour=hour, minute=minute, second=0, microsecond=0)

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

# app/routes.py

# app/routes.py

# app/routes.py
# app/routes.py

@bp.route('/project/<int:project_id>')
@login_required
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)

    
    # Logika otorisasi
    if project.module.career_path != current_user.career_path and (project.module.user_id != current_user.id and project.module.user_id is not None):
        abort(403)
    
    # Ambil sesi chat yang sudah ada, tapi jangan alihkan
    chat_session = ChatSession.query.filter_by(
        user_id=current_user.id,
        project_id=project.id
    ).first()

    # Perubahan utama: Render halaman detail proyek dan lewati data
    # Perubahan utama: kirim data coding_session juga
    return render_template(
        'project_detail.html',
        project=project,
        chat_session=chat_session,
    )


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



@bp.route('/edit-submission/<int:submission_id>', methods=['GET', 'POST'])
@login_required
def edit_submission(submission_id):
    # Ambil data submission dari database
    submission = ProjectSubmission.query.get_or_404(submission_id)

    # Pastikan pengguna hanya bisa mengedit submission miliknya sendiri
    if submission.author != current_user:
        abort(403)

    # Jika pengguna mengirimkan form (metode POST)
    if request.method == 'POST':
        new_link = request.form.get('project_link')
        if new_link:
            submission.project_link = new_link
            db.session.commit()
            flash('Link proyek berhasil diperbarui!', 'success')
            return redirect(url_for('routes.my_projects'))
        else:
            flash('Link proyek tidak boleh kosong.', 'danger')

    # Jika pengguna hanya membuka halaman (metode GET)
    return render_template('edit_submission.html', 
                           title=f"Edit Proyek: {submission.project.title}", 
                           submission=submission)





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


# app/routes.py

@bp.route('/submit-project/<int:project_id>', methods=['POST'])
@login_required
def submit_project(project_id):
    project = Project.query.get_or_404(project_id)
    project_link = request.form.get('project_link')
    
    # Cek apakah pengguna sudah submit proyek ini
    existing_submission = ProjectSubmission.query.filter_by(
        user_id=current_user.id,
        project_id=project.id
    ).first()

    if existing_submission:
        flash(f"Anda sudah mengajukan proyek '{project.title}' sebelumnya.", 'warning')
        return redirect(url_for('routes.my_projects'))
        
    submission = ProjectSubmission(project_id=project.id, user_id=current_user.id, project_link=project_link)
    db.session.add(submission)
    db.session.commit()
    flash(f"Proyek '{project.title}' berhasil disubmit!", 'success')
    return redirect(url_for('routes.my_projects'))




@bp.route('/create-project-chat/<int:project_id>', methods=['GET'])
@login_required
def create_project_chat(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Check if a chat session for this project already exists for the user
    chat_session = ChatSession.query.filter_by(
        user_id=current_user.id,
        project_id=project.id
    ).first()

    # If not, create a new one
    if not chat_session:
        new_session = ChatSession(
            user_id=current_user.id,
            title=f"Diskusi Proyek: {project.title}",
            project_id=project.id
        )
        
        # Buat pesan sambutan yang lengkap
        welcome_content = (
            f"Halo! Selamat datang di ruang diskusi untuk proyek '{project.title}'.\n\n"
            f"**Deskripsi Proyek:**\n{project.description if project.description else 'Tidak ada deskripsi.'}\n\n"
            f"**Tujuan Proyek:**\n{project.project_goals if project.project_goals else 'Tidak ada tujuan.'}\n\n"
            f"**Teknologi:**\n{project.tech_stack if project.tech_stack else 'Tidak disebutkan.'}\n\n"
            f"**Kriteria Penilaian:**\n{project.evaluation_criteria if project.evaluation_criteria else 'Tidak disebutkan.'}\n\n"
            f"**Sumber Daya:**\n{project.resources if project.resources else 'Tidak disebutkan.'}\n\n"
            f"Aku di sini untuk membantumu. Apa ada bagian dari brief proyek ini yang ingin kamu diskusikan lebih dulu?"
        )
        
        welcome_message = ChatMessage(
            session=new_session,
            user_id=current_user.id,
            role='assistant',
            content=welcome_content
        )
        
        db.session.add(new_session)
        db.session.add(welcome_message)
        db.session.commit()
        chat_session = new_session

    # Redirect to the main chatbot session page
    return redirect(url_for('routes.chatbot_session', session_id=chat_session.id))




@bp.route('/interview/<int:submission_id>')
@login_required
def interview(submission_id):
    submission = ProjectSubmission.query.get_or_404(submission_id)
    if submission.author != current_user: 
        abort(403)
    
    # Ambil semua riwayat pesan untuk submission ini
    messages = submission.interview_messages.order_by(InterviewMessage.timestamp.asc()).all()

    return render_template('interview.html', 
                           title=f"Wawancara {submission.project.title}", 
                           submission=submission,
                           messages=messages) # Kirim messages ke template
# app/routes.py -> Tambahkan ini di bagian RUTE API UNTUK AI

@bp.route('/interview-ai/<int:submission_id>', methods=['POST'])
@login_required
def interview_ai(submission_id):
    submission = ProjectSubmission.query.get_or_404(submission_id)
    if submission.author != current_user:
        abort(403)

    user_message_content = request.get_json().get('message', '').strip()
    if not user_message_content:
        return jsonify({'error': 'Pesan tidak boleh kosong'}), 400

    # 1. Simpan pesan pengguna ke database
    user_message = InterviewMessage(submission_id=submission_id, role='user', content=user_message_content)
    db.session.add(user_message)
    
    submitted_code_content = ""
    if 'code_submission' in submission.project_link:
        session_id = int(submission.project_link.split('/')[4])
        coding_session = CodingSession.query.get(session_id)
        if coding_session:
            files = coding_session.files.all()
            for file in files:
                submitted_code_content += f"\n--- {file.filename} ---\n{file.content}\n"
    
    
    # 2. Siapkan prompt untuk AI dengan konteks proyek
    project_context = f"""
    Judul Proyek: {submission.project.title}
    Deskripsi Proyek: {submission.project.description}
    Link Proyek Pengguna: {submission.project_link}
    """

    system_prompt = (
        "Anda adalah seorang rekruter teknis senior yang sedang mewawancarai seorang kandidat junior "
        "mengenai proyek portofolio mereka. Jadilah kritis, tajam, tapi tetap suportif. "
        "Tujuan Anda adalah untuk menguji pemahaman teknis dan proses berpikir kandidat. "
        "Selalu ajukan pertanyaan terbuka yang relevan dengan detail proyek di bawah ini. "
        "Jangan menjawab pertanyaan umum, fokuslah pada wawancara.\n\n"
        f"--- KONTEKS PROYEK ---\n{project_context}"
    )
    
    # Ambil 5 pesan terakhir untuk histori
    history = submission.interview_messages.order_by(InterviewMessage.timestamp.desc()).limit(5).all()
    history.reverse()
    
    messages_for_ai = [{"role": "system", "content": system_prompt}]
    for msg in history:
        messages_for_ai.append({"role": msg.role, "content": msg.content})

    try:
        # 3. Panggil API AI
        completion = ark_client.chat.completions.create(
            model=current_app.config['MODEL_ENDPOINT_ID'],
            messages=messages_for_ai
        )
        ai_response_content = completion.choices[0].message.content
        
        # 4. Simpan balasan AI ke database
        ai_message = InterviewMessage(submission_id=submission_id, role='assistant', content=ai_response_content)
        db.session.add(ai_message)
        db.session.commit()
        
        return jsonify({'response': ai_response_content})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Interview AI Error: {e}")
        return jsonify({'error': 'Gagal menghubungi layanan AI.'}), 500

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
# app/routes.py

# app/routes.py
# --- ROUTE BARU: Menerima data dari Personal Hub dan me-redirect ---
@bp.route('/hub/ask-ai', methods=['POST'])
@login_required
def ask_ai_from_hub():
    events_json = request.form.get('events', '[]')
    tasks_json = request.form.get('tasks', '[]')
    
    # Simpan konteks jadwal di session untuk digunakan oleh route chatbot
    session['hub_context_prompt'] = {
        "events": json.loads(events_json),
        "tasks": json.loads(tasks_json)
    }
    
    return redirect(url_for('routes.chatbot'))

# Di dalam app/routes.py

# Pastikan semua import yang relevan sudah ada di bagian atas file Anda
from flask import session, redirect, url_for, current_app
from app import db
from app.models import ChatSession, ChatMessage
from datetime import datetime

# ...

# Di dalam app/routes.py
# Di dalam app/routes.py

@bp.route('/chatbot')
@login_required
def chatbot():
    # --- Skenario 1: Pengguna datang dari Personal Hub ---
    if 'hub_context_prompt' in session:
        context = session.pop('hub_context_prompt')
        events = context.get('events', [])
        tasks = context.get('tasks', [])
        
        # Cari sesi "Saran Jadwal dari Hub" yang sudah ada
        hub_session = ChatSession.query.filter_by(
            user_id=current_user.id, 
            title="Saran Jadwal dari Hub"
        ).first()

        # Jika sesi tersebut tidak ada, buat baru
        if not hub_session:
            hub_session = ChatSession(user_id=current_user.id, title="Saran Jadwal dari Hub")
            db.session.add(hub_session)
            # SOLUSI KUNCI: Paksa database untuk membuat ID untuk sesi baru ini SEKARANG JUGA
            db.session.flush() 
        
        # Buat prompt untuk AI
        event_list_str = "\n- ".join(events) if events else "Tidak ada acara."
        task_list_str = "\n- ".join(tasks) if tasks else "Tidak ada tugas."
        prompt = f"""
        Sapa pengguna, sebutkan bahwa Anda melihat mereka meminta saran dari Personal Hub.
        Rangkum jadwal mereka hari ini secara singkat (berdasarkan data di bawah).
        Akhiri dengan pertanyaan terbuka untuk memulai percakapan.
        Data jadwal: Acara: {event_list_str}. Tugas: {task_list_str}.
        """
        
        ai_response_content = ""
        try:
            completion = ark_client.chat.completions.create(
                model=current_app.config['MODEL_ENDPOINT_ID'],
                messages=[{"role": "user", "content": prompt}]
            )
            ai_response_content = completion.choices[0].message.content
        except Exception as e:
            current_app.logger.error(f"AI Hub Context Error: {e}")
            ai_response_content = f"Halo {current_user.name.split()[0]}! Sepertinya ada sedikit masalah saat saya mencoba melihat jadwalmu. Ada yang bisa kubantu?"

        help_hint = "\n\n*(Ketik 'bantuan' untuk melihat contoh perintah.)*"
        final_welcome_message = ai_response_content + help_hint

        # Buat pesan baru. Sekarang `hub_session.id` dijamin memiliki nilai.
        welcome_message = ChatMessage(session_id=hub_session.id, user_id=current_user.id, role='assistant', content=final_welcome_message)
        db.session.add(welcome_message)
        
        # Simpan semua perubahan (sesi baru jika ada, dan pesan baru)
        db.session.commit()
        
        return redirect(url_for('routes.chatbot_session', session_id=hub_session.id))

    # --- Skenario 2: Pengguna mengakses chatbot secara langsung ---
    latest_session = ChatSession.query.filter_by(user_id=current_user.id).order_by(ChatSession.timestamp.desc()).first()

    if latest_session:
        return redirect(url_for('routes.chatbot_session', session_id=latest_session.id))
    else:
        # Untuk pengguna yang benar-benar baru, logika ini sudah benar
        new_session = ChatSession(user_id=current_user.id, title="Percakapan Umum")
        db.session.add(new_session)
        db.session.flush()
        
        welcome_message = ChatMessage(
            session_id=new_session.id, user_id=current_user.id, role='assistant',
            content=(
                f"Halo {current_user.name.split()[0]}! 👋 Aku Farmile, mentor AI kamu.\n\n"
                f"Siap bantuin apa hari ini? 🚀\n\n"
                f"**(Pssst... kamu bisa ketik 'bantuan' untuk melihat semua perintah keren yang bisa aku lakukan!)**"
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


# --- Rute untuk menampilkan sesi chat spesifik ---
@bp.route('/chatbot/<int:session_id>')
@login_required
def chatbot_session(session_id):
    session_data = ChatSession.query.get_or_404(session_id)
    if session_data.user_id != current_user.id:
        abort(403)
    all_sessions = ChatSession.query.filter_by(user_id=current_user.id).order_by(ChatSession.timestamp.desc()).all()
    messages = session_data.messages.order_by(ChatMessage.timestamp.asc()).all()
    return render_template('chatbot.html', title=session_data.title, 
                           current_session=session_data, all_sessions=all_sessions, history=messages)

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


#===============================================
# FUNGSI-FUNGSI HELPER UNTUK AKSI AI
# ===============================================
def _execute_ai_action(user, action_data):
    """Fungsi pusat untuk memproses semua jenis aksi dari AI."""
    action = action_data.get("action")
    payload = action_data.get("payload", {})

    if action == "add_task":
        task = _create_task_from_ai(user, payload)
        if task:
            due_date_info = f" dengan deadline {task.due_date.strftime('%d %B, %H:%M')}." if task.due_date else "."
            return f"✅ Siap! Tugas '{task.title}' sudah saya tambahkan ke Personal Hub{due_date_info}"
        return "Maaf, terjadi kesalahan. Pastikan Anda menyebutkan judul untuk tugas yang ingin ditambahkan."

    elif action == "add_event":
        event = _create_event_from_ai(user, payload)
        if event:
            time_info = f" pada {event.start_time.strftime('%d %B, %H:%M')}."
            return f"✅ Berhasil! Acara '{event.title}' sudah saya jadwalkan di kalender Anda{time_info}"
        return "Maaf, terjadi kesalahan. Pastikan Anda menyebutkan judul untuk acara yang ingin dijadwalkan."

    elif action == "update_task":
        task = _update_task_from_ai(user, payload)
        if task:
            return f"✏️ Tugas '{task.title}' berhasil diperbarui."
        return f"Maaf, saya tidak dapat menemukan tugas '{payload.get('original_title')}' untuk diperbarui."

    elif action == "update_event":
        event = _update_event_from_ai(user, payload)
        if event:
            return f"✅ Sip! Jadwal untuk '{event.title}' sudah diubah ke {event.start_time.strftime('%d %B, %H:%M')}."
        return f"Maaf, saya tidak dapat menemukan acara '{payload.get('original_title')}' untuk diubah."

    elif action == "delete_task":
        success, title = _delete_task_from_ai(user, payload)
        if success:
            return f"🗑️ Oke, tugas '{title}' sudah berhasil saya hapus."
        return f"Maaf, saya tidak dapat menemukan tugas dengan judul '{title}' untuk dihapus."

    elif action == "delete_event":
        success, title = _delete_event_from_ai(user, payload)
        if success:
            return f"🗑️ Oke, acara '{title}' sudah berhasil saya hapus dari jadwal Anda."
        return f"Maaf, saya tidak dapat menemukan acara dengan judul '{title}' untuk dihapus."

    # Respons fallback jika aksi tidak dikenali
    return "Saya mendeteksi sebuah aksi, tapi saya belum bisa melakukannya saat ini."

def _create_task_from_ai(user, payload):
    """Membuat Task dari payload AI dengan validasi dan parsing waktu yang lebih baik."""
    try:
        title = payload.get('title')
        if not title: return None

        description = payload.get('description')
        priority = payload.get('priority', 'medium').lower()
        if priority not in ['low', 'medium', 'high', 'urgent']: priority = 'medium'

        due_date_str = payload.get('due_date')
        due_date = None
        if due_date_str:
            # Mencoba parse format YYYY-MM-DD HH:MM
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d %H:%M')
            except ValueError:
                # Fallback untuk parsing "besok jam HH:MM"
                if "besok" in due_date_str.lower() and "jam" in due_date_str.lower():
                    time_parts = due_date_str.lower().split("jam")[1].strip().split(":")
                    hour = int(time_parts[0]) if time_parts[0].isdigit() else 0
                    minute = int(time_parts[1]) if len(time_parts) > 1 and time_parts[1].isdigit() else 0
                    due_date = (datetime.now() + timedelta(days=1)).replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        new_task = Task(author=user, title=title, description=description, priority=priority, due_date=due_date, status='todo')
        db.session.add(new_task)
        db.session.commit()
        return new_task
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Gagal membuat tugas dari AI: {e}")
        return None

def _create_event_from_ai(user, payload):
    """Membuat Event dari payload AI dengan validasi dan parsing waktu yang lebih baik."""
    try:
        title = payload.get('title')
        if not title: return None

        description = payload.get('description')
        start_time_str = payload.get('start_time') # Contoh: "besok jam 17:00"
        start_time = datetime.now() # Default jika waktu tidak valid

        if start_time_str:
            if "besok" in start_time_str.lower() and "jam" in start_time_str.lower():
                time_parts = start_time_str.lower().split("jam")[1].strip().split(":")
                hour = int(time_parts[0]) if time_parts[0].isdigit() else 0
                minute = int(time_parts[1]) if len(time_parts) > 1 and time_parts[1].isdigit() else 0
                start_time = (datetime.now() + timedelta(days=1)).replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        new_event = Event(author=user, title=title, description=description, start_time=start_time)
        db.session.add(new_event)
        db.session.commit()
        return new_event
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Gagal membuat event dari AI: {e}")
        return None


# GANTI FUNGSI LAMA DENGAN VERSI BARU YANG LEBIH CERDAS INI
def _delete_task_from_ai(user, payload):
    """
    Menghapus Task secara fleksibel, membersihkan input dari AI 
    dan menangani konteks waktu.
    """
    title_raw = payload.get('title')
    time_context = payload.get('time_context')
    
    if not title_raw: 
        return False, ""
    
    # 1. Cerdaskan ekstraksi kata kunci dari judul mentah
    # Daftar kata-kata umum yang harus diabaikan
    stop_words = ["tugas", "acara", "hapus", "kerjakan", "itu", "ini", "dari", "jadwal", "saya", "aku"]
    
    # Bersihkan judul dari stop words
    cleaned_title_words = [word for word in title_raw.lower().split() if word not in stop_words]
    
    if not cleaned_title_words:
        # Jika tidak ada kata kunci tersisa setelah dibersihkan
        return False, title_raw
        
    # Ambil kata kunci utama (biasanya kata pertama setelah dibersihkan)
    keyword = cleaned_title_words[0]

    # 2. Lakukan query ke database dengan kata kunci yang sudah bersih
    query = Task.query.filter(
        Task.author == user,
        Task.title.ilike(f"%{keyword}%")  # Cari tugas yang mengandung kata kunci
    )
    
    # 3. Tambahkan filter waktu jika ada
    if time_context == "hari ini":
        today = datetime.utcnow().date()
        query = query.filter(db.func.date(Task.due_date) == today)
    
    # Ambil tugas terbaru yang cocok dengan kriteria
    task_to_delete = query.order_by(Task.id.desc()).first()
    
    if task_to_delete:
        original_title = task_to_delete.title
        db.session.delete(task_to_delete)
        db.session.commit()
        return True, original_title # Kembalikan judul asli untuk konfirmasi
        
    return False, keyword # Kembalikan kata kunci jika tidak ditemukan


def _delete_event_from_ai(user, payload):
    """Menghapus Event berdasarkan judul dan konteks waktu (jika ada)."""
    title = payload.get('title')
    time_context = payload.get('time_context')  # e.g., "hari ini"
    
    if not title:
        return False, ""
    
    # Mulai query dasar dengan pencarian judul yang fleksibel
    query = Event.query.filter(
        Event.author == user,
        Event.title.ilike(f"%{title}%")
    )
    
    # Tambahkan filter waktu jika pengguna menyediakannya
    if time_context == "hari ini":
        today = datetime.utcnow().date()
        query = query.filter(db.func.date(Event.start_time) == today)
        
    # Ambil acara terbaru yang cocok dengan kriteria
    event_to_delete = query.order_by(Event.id.desc()).first()
    
    if event_to_delete:
        original_title = event_to_delete.title
        db.session.delete(event_to_delete)
        db.session.commit()
        return True, original_title  # Kembalikan judul asli untuk konfirmasi
        
    return False, title

# GANTI FUNGSI LAMA DI routes.py DENGAN VERSI LENGKAP INI

def _update_task_from_ai(user, payload):
    """
    Mengupdate Task berdasarkan judul asli, sekarang dengan kemampuan
    untuk mengubah judul, prioritas, dan tanggal jatuh tempo (due_date).
    """
    original_title = payload.get('original_title')
    new_data = payload.get('new_data', {})
    
    if not original_title or not new_data: 
        return None

    # Gunakan .ilike() untuk pencarian judul yang tidak case-sensitive dan lebih fleksibel
    task_to_update = Task.query.filter(
        Task.author == user, 
        Task.title.ilike(f"%{original_title}%")
    ).order_by(Task.id.desc()).first()
    
    if task_to_update:
        # Update atribut yang ada di payload
        task_to_update.title = new_data.get('title', task_to_update.title)
        task_to_update.priority = new_data.get('priority', task_to_update.priority)
        
        # --- INI BAGIAN YANG HILANG DAN SEKARANG DITAMBAHKAN ---
        if 'due_date' in new_data:
            # Menggunakan parser waktu cerdas yang sudah kita buat sebelumnya
            due_date_str = new_data['due_date']
            if due_date_str:
                task_to_update.due_date = _parse_human_readable_time(due_date_str)
        # ---------------------------------------------------------
        
        db.session.commit()
        return task_to_update
        
    return None
def _update_event_from_ai(user, payload):
    """Mengupdate Event berdasarkan judul asli."""
    original_title = payload.get('original_title')
    new_data = payload.get('new_data', {})
    if not original_title or not new_data: return None

    # Cari event terakhir dengan judul yang cocok (paling relevan)
    event_to_update = Event.query.filter(
        Event.author == user, 
        Event.title.ilike(f"%{original_title}%")
    ).order_by(Event.id.desc()).first()

    if event_to_update:
        # Update data yang ada di payload
        if 'title' in new_data:
            event_to_update.title = new_data['title']
        if 'start_time' in new_data:
            event_to_update.start_time = _parse_human_readable_time(new_data['start_time'])

        db.session.commit()
        return event_to_update
    return None
    
    
    
# Di dalam file app/routes.py

@bp.route('/chat-ai/<int:session_id>', methods=['POST'])
@login_required
def chat_ai(session_id):
    # Validasi sesi dan pengguna
    session_data = ChatSession.query.get_or_404(session_id)
    if session_data.user_id != current_user.id:
        abort(403)
    
    # Ambil dan validasi pesan dari pengguna
    user_message_content = request.get_json().get('message', '').strip()
    if not user_message_content:
        return jsonify({'error': 'Pesan tidak boleh kosong'}), 400

    # Simpan pesan pengguna ke database
    user_message = ChatMessage(session_id=session_data.id, user_id=current_user.id, role='user', content=user_message_content)
    db.session.add(user_message)

    # [1. Dapatkan Konteks Pengguna Secara Real-time dengan Timezone DINAMIS]
    
    # Ambil timezone dari profil pengguna, fallback ke Jakarta jika tidak ada
    user_timezone_str = current_user.timezone or 'Asia/Jakarta'
    local_tz = pytz.timezone(user_timezone_str)
    
    # Dapatkan waktu saat ini dalam UTC, lalu konversikan ke waktu lokal pengguna
    now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)
    now_local = now_utc.astimezone(local_tz)
    today_local = now_local.date()

    # Gunakan tanggal lokal untuk semua query database
    todays_events = Event.query.filter(db.func.date(Event.start_time) == today_local, Event.user_id == current_user.id).all()
    relevant_tasks = Task.query.filter(
        Task.user_id == current_user.id, Task.status != 'done',
        or_(db.func.date(Task.due_date) <= today_local, Task.due_date == None)
    ).all()
    
    # Pastikan waktu yang ditampilkan juga dikonversi ke timezone lokal
    event_list_str = "\n- ".join([f"{e.title} (pukul {e.start_time.astimezone(local_tz).strftime('%H:%M')})" for e in todays_events]) or "Tidak ada"
    task_list_str = "\n- ".join([f"{t.title} (deadline: {t.due_date.astimezone(local_tz).strftime('%d %b, %H:%M') if t.due_date else 'N/A'})" for t in relevant_tasks]) or "Tidak ada"
    
    # Buat string tanggal yang diformat dengan benar untuk AI
    nama_hari = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
    formatted_date_str = f"{nama_hari[now_local.weekday()]}, {now_local.strftime('%d %B')}"
    
    user_context_string = (
        f"Nama pengguna: {current_user.name}.\n"
        f"Hari dan Tanggal Saat Ini (Zona Waktu Pengguna): {formatted_date_str}.\n"
        f"Jadwal Acara Hari Ini:\n- {event_list_str}\n"
        f"Daftar Tugas Aktif:\n- {task_list_str}"
    )
    # [2. Definisikan Persona & Aturan Aksi untuk AI]
    system_prompt = (
        "[PERAN & IDENTITAS]\n"
        "Anda adalah 'Farmile', seorang mentor AI personal yang sangat ahli untuk mahasiswa IT. Misi utama Anda adalah membimbing pengguna secara proaktif, bukan hanya menjawab pertanyaan.\n\n"
        
        "[ATURAN PERILAKU]\n"
        "1. PRIORITAS UTAMA - MODE MENTOR & BANTUAN KODING: Tugas utamamu adalah menjadi mentor. Jika pengguna mendeskripsikan masalah coding, kebingungan konsep, atau meminta contoh kode, JANGAN melakukan aksi. Berikan penjelasan yang jelas dan contoh kode sederhana.\n\n"
        "2. PROAKTIF & KONTEKSTUAL: Selalu gunakan informasi pengguna (nama, jadwal, tugas) yang diberikan untuk memberikan jawaban yang sangat personal dan relevan.\n\n"
        "3. JAWABAN DETAIL: Saat menjawab pertanyaan tentang jadwal atau tugas, format jawabanmu sebagai daftar ringkas, sertakan waktu atau deadline untuk setiap item.\n\n"
        "4. PANDUAN PENGGUNA: Jika pengguna bertanya 'bantuan', 'help', atau 'perintah', berikan jawaban HANYA dalam format PANDUAN BANTUAN di bawah.\n\n"
        "5. DETEKSI AKSI EKSPLISIT:\n"
        "   a. Hanya aktifkan mode aksi jika pengguna menggunakan kata kerja perintah yang JELAS (tambah, buat, jadwalkan, hapus, ganti, ubah, update).\n"
        "   b. Saat mengekstrak `title` atau `original_title`, ambil HANYA kata benda intinya. Buang kata-kata umum seperti 'tugas', 'acara', 'kerjakan'. Contoh: dari 'hapus tugasku Beli kopi', `title`-nya adalah 'Kopi'.\n"
        "   c. Jika aksi akan dilakukan, berikan respons HANYA dan EKSKLUSIF dalam format JSON yang dibungkus tag [DO_ACTION].\n\n"
        
        "6. **ATURAN KRITIS - JANGAN PERNAH MENJAWAB DENGAN JSON MENTAH**: Anda dilarang keras menampilkan teks yang terlihat seperti kode JSON (dimulai dengan '{' dan diakhiri dengan '}') langsung kepada pengguna. JSON hanya boleh ada di dalam tag [DO_ACTION]. Jika Anda berpikir untuk melakukan aksi yang tidak ada dalam contoh (seperti 'get_events'), batalkan pikiran itu dan jawablah secara percakapan biasa.\n\n"
        
        "7. **ATURAN KRITIS - PERTANYAAN LIHAT JADWAL**: Jika pengguna bertanya untuk melihat jadwal atau tugas ('ada acara apa?', 'cek jadwalku'), JANGAN BUAT JSON AKSI. Sistem sudah memberikan konteks jadwal terkini kepada Anda. Langsung jawab pertanyaan pengguna secara naratif berdasarkan konteks yang sudah Anda terima.\n\n"

        "[FORMAT PANDUAN BANTUAN]\n"
        "Tentu saja! Saya bisa membantu Anda mengelola jadwal dan tugas langsung dari percakapan ini. Anggap saja saya asisten pribadi Anda. 🤖\n\n"
        "Berikut adalah beberapa contoh cara Anda bisa memberi saya perintah:\n\n"
        "**🗓️ Untuk Menambah Jadwal:**\n"
        "*\"Farmile, tolong tambahkan tugas baru: Kerjakan bab 3 skripsi, deadline besok jam 8 malam.\"*\n"
        "*\"Jadwalkan acara 'Meeting dengan Klien' untuk hari Senin jam 1 siang.\"`\n\n"
        "**🔍 Untuk Melihat Jadwal:**\n"
        "*\"Tugas apa saja yang harus kuselesaikan hari ini?\"*\n"
        "*\"Coba lihat jadwalku untuk minggu depan.\"`\n\n"
        "**✏️ Untuk Mengubah & Menghapus:**\n"
        "*\"Hapus tugasku yang judulnya 'Beli kopi'.\"*\n"
        "*\"Update prioritas tugas 'Revisi desain' menjadi high.\"`\n"
        "*\"Ubah waktu acara 'Pernikahan Zizka' jadi jam 3 sore.\"`\n\n"
        "Cukup katakan apa yang Anda butuhkan, dan saya akan coba mengaturnya untuk Anda!\n\n"

        "[FORMAT AKSI JSON & CONTOH]\n"
        "---### AKSI: MENAMBAH DATA ###---\n"
        "Permintaan: 'Jadwalkan 'Rapat Proyek Akhir' besok jam 2 siang dengan deskripsi 'bahas finalisasi fitur'.'\n"
        "Respons Anda:\n"
        "[DO_ACTION]{\n"
        "  \"action\": \"add_event\",\n"
        "  \"payload\": {\n"
        "    \"title\": \"Rapat Proyek Akhir\",\n"
        "    \"start_time\": \"besok jam 14:00\",\n"
        "    \"description\": \"bahas finalisasi fitur\"\n"
        "  }\n"
        "}[/DO_ACTION]\n\n"
        "Permintaan: 'tambahin tugas 'laporan mingguan' deadline hari ini jam 11 malam, prioritasnya medium'\n"
        "Respons Anda:\n"
        "[DO_ACTION]{\n"
        "  \"action\": \"add_task\",\n"
        "  \"payload\": {\n"
        "    \"title\": \"laporan mingguan\",\n"
        "    \"due_date\": \"hari ini jam 23:00\",\n"
        "    \"priority\": \"medium\"\n"
        "  }\n"
        "}[/DO_ACTION]\n\n"
        
        "---### AKSI: MENGUBAH DATA ###---\n"
        "Permintaan: 'ubah acara 'pernikahan zizka' jadi jam 4 sore'\n"
        "Respons Anda:\n"
        "[DO_ACTION]{\n"
        "  \"action\": \"update_event\",\n"
        "  \"payload\": {\n"
        "    \"original_title\": \"pernikahan zizka\",\n"
        "    \"new_data\": {\n"
        "      \"start_time\": \"hari ini jam 16:00\"\n"
        "    }\n"
        "  }\n"
        "}[/DO_ACTION]\n\n"
        "Permintaan: 'Update tugas 'Revisi Desain' jadi 'Revisi Desain Halaman Login' dan set prioritasnya jadi urgent.'\n"
        "Respons Anda:\n"
        "[DO_ACTION]{\n"
        "  \"action\": \"update_task\",\n"
        "  \"payload\": {\n"
        "    \"original_title\": \"Revisi Desain\",\n"
        "    \"new_data\": {\n"
        "      \"title\": \"Revisi Desain Halaman Login\",\n"
        "      \"priority\": \"urgent\"\n"
        "    }\n"
        "  }\n"
        "}[/DO_ACTION]\n\n"

        "---### AKSI: MENGHAPUS DATA ###---\n"
        "Permintaan: 'hapus acara Pernikahan Teman hari ini'\n"
        "Respons Anda:\n"
        "[DO_ACTION]{\n"
        "  \"action\": \"delete_event\",\n"
        "  \"payload\": {\n"
        "    \"title\": \"Pernikahan Teman\",\n"
        "    \"time_context\": \"hari ini\"\n"
        "  }\n"
        "}[/DO_ACTION]\n\n"
        "Permintaan: 'Tolong hapus tugas 'Laporan Mingguan'.'\n"
        "Respons Anda:\n"
        "[DO_ACTION]{\n"
        "  \"action\": \"delete_task\",\n"
        "  \"payload\": {\n"
        "    \"title\": \"Laporan Mingguan\"\n"
        "  }\n"
        "}[/DO_ACTION]"
    )
    
    # [3. Bangun Riwayat Pesan dengan Konteks yang Disuntikkan]
    # [3. Bangun Riwayat Pesan dengan Konteks yang Disuntikkan]
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Konteks saya saat ini: {user_context_string}"},
        {"role": "assistant", "content": "Baik, konteks Anda sudah saya pahami. Siap membantu."}
    ]
    recent_history = session_data.messages.order_by(ChatMessage.timestamp.desc()).limit(10).all()
    recent_history.reverse()
    for msg in recent_history:
        messages.append({"role": msg.role, "content": msg.content})
        
        
     # ===================================================
    print("="*20 + " DEBUGGING INFO " + "="*20)
    api_key_status = "ADA dan disembunyikan" if ark_client.api_key else "TIDAK ADA (None)"
    print(f"--> Status Kunci API: {api_key_status}")
    print(f"--> Model Endpoint ID: {current_app.config.get('MODEL_ENDPOINT_ID')}")
    print("Mencoba menghubungi server AI...")
    # ===================================================

    # [4. Panggil API AI dan Proses Respons]
    try:
        completion = ark_client.chat.completions.create(model=current_app.config['MODEL_ENDPOINT_ID'], messages=messages)
        ai_response_content = completion.choices[0].message.content.strip()

        final_response_to_user = ""
        
        # [5. Parser Cerdas untuk Deteksi dan Eksekusi Aksi]
        action_match = re.search(r"\[DO_ACTION\](.*?)\[/DO_ACTION\]", ai_response_content, re.DOTALL)
        
        if action_match:
            try:
                action_json_str = action_match.group(1).strip()
                action_data = json.loads(action_json_str)
                final_response_to_user = _execute_ai_action(current_user, action_data)
            except Exception as e:
                current_app.logger.error(f"Gagal parsing aksi AI: {e}")
                final_response_to_user = "Maaf, saya sedikit bingung dengan format aksi. Bisa ulangi permintaan Anda?"
        else:
            final_response_to_user = ai_response_content

        # Simpan balasan final ke database dan kirim ke pengguna
        ai_message = ChatMessage(session_id=session_data.id, user_id=current_user.id, role='assistant', content=final_response_to_user)
        db.session.add(ai_message)
        db.session.commit()
        
        return jsonify({'response': final_response_to_user})

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Chat AI Error: {e}")
        return jsonify({'error': 'Gagal menghubungi layanan AI, silakan coba lagi.'}), 500
# ===============================================
# RUTE PERSONAL HUB
# ===============================================

@bp.route('/hub')
@login_required
def personal_hub():
    """Menampilkan halaman Personal Productivity Hub."""
    return render_template('personal_hub.html', title="Personal Hub")

# ===============================================
# API UNTUK PERSONAL HUB (FARSIGHT OS)
# ===============================================

# --- Helper Functions untuk Serialisasi ---
def event_to_dict(event):
    event_color = event.color or '#5484ed' 
    return {
        'id': str(event.id), 'title': event.title, 'description': event.description,
        'start': event.start_time.isoformat(), 'end': event.end_time.isoformat() if event.end_time else None,
        'link': event.link, 'backgroundColor': event_color, 'borderColor': event_color
    }

def task_to_dict(task):
    return {
        'id': task.id, 'title': task.title, 'description': task.description,
        'due_date': task.due_date.isoformat() if task.due_date else None,
        'priority': task.priority, 'status': task.status
    }
# GANTI FUNGSI get_events DI app/routes.py DENGAN VERSI LENGKAP INI

@bp.route('/api/hub/events', methods=['GET'])
@login_required
def get_events():
    start_str = request.args.get('start')
    end_str = request.args.get('end')
    
    combined_items = []
    
    if start_str and end_str:
        try:
            start_date = datetime.fromisoformat(start_str)
            end_date = datetime.fromisoformat(end_str)

            # 1. Ambil semua ACARA dalam rentang tanggal
            events = Event.query.filter(
                Event.user_id == current_user.id,
                Event.start_time.between(start_date, end_date)
            ).all()
            
            for event in events:
                combined_items.append({
                    'id': f"event-{event.id}",
                    'title': event.title,
                    'start': event.start_time.isoformat(),
                    'end': event.end_time.isoformat() if event.end_time else None,
                    'backgroundColor': event.color or '#3B82F6', # Biru untuk acara
                    'borderColor': event.color or '#3B82F6',
                    'extendedProps': {
                        'item_type': 'event', # <-- Label jelas
                        'description': event.description,
                        'link': event.link
                    }
                })

            # 2. Ambil semua TUGAS yang jatuh tempo dalam rentang tanggal
            tasks = Task.query.filter(
                Task.user_id == current_user.id,
                Task.due_date.between(start_date, end_date)
            ).all()

            for task in tasks:
                combined_items.append({
                    'id': f"task-{task.id}",
                    'title': f"Deadline: {task.title}", # Beri prefiks agar jelas
                    'start': task.due_date.isoformat(),
                    'allDay': True, # Tugas biasanya dianggap seharian pada tanggal deadline
                    'backgroundColor': '#10B981', # Hijau untuk tugas
                    'borderColor': '#10B981',
                    'extendedProps': {
                        'item_type': 'task', # <-- Label jelas
                        'original_task': task_to_dict(task) 
                    }
                })
        except Exception as e:
            current_app.logger.error(f"Error getting calendar items: {e}")
            
    return jsonify(combined_items)



@bp.route('/api/hub/events', methods=['POST'])
@login_required
def create_event():
    data = request.get_json()
    if not data or not data.get('title') or not data.get('start'):
        return jsonify({'status': 'error', 'message': 'Judul dan waktu mulai wajib diisi.'}), 400
    try:
        start_time = datetime.fromisoformat(data['start'])
        end_time = datetime.fromisoformat(data['end']) if data.get('end') else None
        event = Event(author=current_user, title=data['title'], description=data.get('description'),
                      start_time=start_time, end_time=end_time, link=data.get('link'),
                      color=data.get('color', '#3788d8'))
        db.session.add(event)
        db.session.commit()
        return jsonify(event_to_dict(event)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Terjadi kesalahan: {str(e)}'}), 500

@bp.route('/api/hub/events/<int:event_id>', methods=['PUT'])
@login_required
def update_event(event_id):
    try:
        event = Event.query.filter_by(id=event_id, author=current_user).first_or_404()
        data = request.get_json()
        event.title = data.get('title', event.title)
        event.description = data.get('description', event.description)
        event.link = data.get('link', event.link)
        event.color = data.get('color', event.color)
        if data.get('start'): event.start_time = datetime.fromisoformat(data['start'])
        if data.get('end'): event.end_time = datetime.fromisoformat(data['end'])
        else: event.end_time = None
        db.session.commit()
        return jsonify(event_to_dict(event))
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Terjadi kesalahan: {str(e)}'}), 500

@bp.route('/api/hub/events/<int:event_id>', methods=['DELETE'])
@login_required
def delete_event(event_id):
    event = Event.query.filter_by(id=event_id, author=current_user).first_or_404()
    db.session.delete(event)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Acara berhasil dihapus.'})


# Di dalam app/routes.py
@bp.route('/api/hub/tasks', methods=['GET'])
@login_required
def get_tasks():
    filter_type = request.args.get('filter')
    query = Task.query.filter_by(author=current_user)

    if filter_type == 'today_and_overdue':
        today = datetime.utcnow().date()
        # LOGIKA QUERY BARU YANG LEBIH ROBUST
        query = query.filter(
            Task.status != 'done',
            or_(
                db.func.date(Task.due_date) <= today, # Kondisi 1: Jatuh tempo hari ini atau terlewat
                Task.due_date == None               # Kondisi 2: Tidak punya tanggal jatuh tempo
            )
        )
    else:
        # Logika lama untuk saat mengklik tanggal spesifik di kalender (ini sudah benar)
        date_str = request.args.get('date')
        if date_str:
            try:
                selected_date = datetime.fromisoformat(date_str).date()
                query = query.filter(db.func.date(Task.due_date) == selected_date)
            except (ValueError, TypeError): pass
            
    tasks = query.order_by(Task.due_date.asc()).all()
    return jsonify([task_to_dict(task) for task in tasks])

@bp.route('/api/hub/tasks', methods=['POST'])
@login_required
def create_task():
    """Membuat tugas baru dengan penanganan error."""
    data = request.get_json()
    if not data or not data.get('title'):
        return jsonify({'status': 'error', 'message': 'Judul tugas wajib diisi.'}), 400
    
    try:
        due_date = None
        # PERBAIKAN: Hanya proses tanggal jika ada dan tidak kosong
        if data.get('due_date'):
            due_date = datetime.fromisoformat(data['due_date'])
        
        task = Task(author=current_user, title=data['title'], description=data.get('description'),
                    due_date=due_date, priority=data.get('priority', 'medium'), status='todo')
        db.session.add(task)
        db.session.commit()
        return jsonify(task_to_dict(task)), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Gagal membuat tugas: {e}")
        return jsonify({'status': 'error', 'message': f'Terjadi kesalahan: {str(e)}'}), 500

@bp.route('/api/hub/tasks/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    """Mengedit tugas yang ada dengan penanganan error."""
    try:
        task = Task.query.filter_by(id=task_id, author=current_user).first_or_404()
        data = request.get_json()
        
        task.title = data.get('title', task.title)
        task.description = data.get('description', task.description)
        task.priority = data.get('priority', task.priority)
        task.status = data.get('status', task.status)
        
        # PERBAIKAN: Hanya proses tanggal jika ada dan tidak kosong
        if data.get('due_date'):
            task.due_date = datetime.fromisoformat(data['due_date'])
        else:
            task.due_date = None
            
        db.session.commit()
        return jsonify(task_to_dict(task))
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Gagal update tugas {task_id}: {e}")
        return jsonify({'status': 'error', 'message': f'Terjadi kesalahan: {str(e)}'}), 500

@bp.route('/api/hub/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id, author=current_user).first_or_404()
    db.session.delete(task)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Tugas berhasil dihapus.'})


# ===============================================
# API UNTUK AI ORGANIZER
# ===============================================

@bp.route('/api/hub/ai-organizer', methods=['POST'])
@login_required
def ai_organizer():
    """Menerima jadwal harian dan meminta saran dari AI."""
    data = request.get_json()
    events = data.get('events', [])
    tasks = data.get('tasks', [])
    
    if not events and not tasks:
        return jsonify({'suggestion': 'Tidak ada jadwal untuk hari ini. Waktu yang tepat untuk bersantai atau merencanakan hal baru!'})

    # Membuat prompt yang jelas untuk AI
    prompt = f"""
    Anda adalah Farmile, seorang mentor produktivitas AI yang sangat suportif.
    Seorang mahasiswa bernama {current_user.name} memiliki jadwal hari ini sebagai berikut:
    
    Acara terjadwal: {json.dumps(events, indent=2)}
    Tugas yang perlu dikerjakan: {json.dumps(tasks, indent=2)}
    
    Berikan saran strategi yang singkat, cerdas, dan memotivasi dalam format poin-poin agar dia bisa menjalani hari ini dengan super produktif. Sapa dia dengan ramah.
    """
    
    try:
        # Panggil AI Client Anda (sesuaikan dengan 'ark_client' yang kamu punya)
        completion = ark_client.chat.completions.create(
            model=current_app.config['MODEL_ENDPOINT_ID'],
            messages=[{"role": "user", "content": prompt}]
        )
        ai_response_content = completion.choices[0].message.content
        return jsonify({'suggestion': ai_response_content})

    except Exception as e:
        current_app.logger.error(f"AI Organizer Error: {e}")
        return jsonify({'error': 'Gagal menghubungi mentor AI saat ini.'}), 500
    
    
