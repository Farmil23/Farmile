# app/routes.py (Versi Final, Lengkap, dan Terstruktur)
from flask import (render_template, redirect, url_for, request, Blueprint, 
                   abort, flash, jsonify, current_app)
from flask_login import current_user, login_required, login_user, logout_user
from app import db, oauth, ark_client
from app.models import (User, Project, ProjectSubmission, ChatMessage, 
                        ChatSession, Module, Lesson, UserProgress)

bp = Blueprint('routes', __name__)


# ===============================================
# RUTE PUBLIK & INTI APLIKASI
# ===============================================
@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('routes.dashboard'))
    return render_template('landing_page.html', title='Selamat Datang di FARSIGHT')

@bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', title='Dasbor Anda')


# ===============================================
# RUTE AUTENTIKASI & ONBOARDING
# ===============================================
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
# RUTE ROADMAP BELAJAR
# ===============================================
@bp.route('/roadmap')
@login_required
def roadmap():
    if not current_user.career_path:
        flash('Selesaikan onboarding untuk menentukan jalur karier Anda.', 'warning')
        return redirect(url_for('routes.onboarding'))
    modules = Module.query.filter_by(career_path=current_user.career_path).order_by(Module.order).all()
    completed_lessons_query = db.session.query(UserProgress.lesson_id).filter_by(user_id=current_user.id)
    completed_lesson_ids = {item[0] for item in completed_lessons_query.all()}
    total_lessons = Lesson.query.join(Module).filter(Module.career_path==current_user.career_path).count()
    progress_percentage = int((len(completed_lesson_ids) / total_lessons) * 100) if total_lessons > 0 else 0
    return render_template('roadmap.html', title="Roadmap Belajar", modules=modules, 
                           completed_lesson_ids=completed_lesson_ids, progress=progress_percentage)

@bp.route('/complete-lesson/<int:lesson_id>', methods=['POST'])
@login_required
def complete_lesson(lesson_id):
    progress = UserProgress.query.filter_by(user_id=current_user.id, lesson_id=lesson_id).first()
    if not progress:
        new_progress = UserProgress(user_id=current_user.id, lesson_id=lesson_id)
        db.session.add(new_progress)
        db.session.commit()
    return jsonify({'status': 'success'})


# ===============================================
# RUTE PROYEK & WAWANCARA
# ===============================================
@bp.route('/my-projects')
@login_required
def my_projects():
    submissions = ProjectSubmission.query.filter_by(author=current_user).order_by(ProjectSubmission.id.desc()).all()
    return render_template('my_projects.html', title="Proyek Saya", submissions=submissions)

@bp.route('/select-project')
@login_required
def select_project():
    if not current_user.career_path:
        flash('Selesaikan onboarding untuk menentukan jalur karier.', 'warning')
        return redirect(url_for('routes.dashboard'))
    submitted_project_ids = [sub.project_id for sub in current_user.submissions]
    available_projects = Project.query.filter(
        Project.career_path == current_user.career_path, 
        Project.id.notin_(submitted_project_ids)
    ).all()
    return render_template('select_project.html', title="Pilih Proyek Baru", projects=available_projects)

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
    if submission.author != current_user: abort(403)
    return render_template('interview.html', title=f"Wawancara {submission.project.title}", submission=submission)

@bp.route('/cancel-submission/<int:submission_id>', methods=['POST'])
@login_required
def cancel_submission(submission_id):
    submission = ProjectSubmission.query.get_or_404(submission_id)
    if submission.author != current_user: abort(403)
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
    latest_session = ChatSession.query.filter_by(author=current_user).order_by(ChatSession.timestamp.desc()).first()
    if latest_session:
        return redirect(url_for('routes.chatbot_session', session_id=latest_session.id))
    else:
        new_session = ChatSession(author=current_user, title="Percakapan Pertama")
        db.session.add(new_session)
        db.session.commit()
        return redirect(url_for('routes.chatbot_session', session_id=new_session.id))

@bp.route('/chatbot/new', methods=['POST'])
@login_required
def new_chat_session():
    new_session = ChatSession(author=current_user, title="Percakapan Baru")
    db.session.add(new_session)
    db.session.commit()
    return redirect(url_for('routes.chatbot_session', session_id=new_session.id))

@bp.route('/chatbot/<int:session_id>')
@login_required
def chatbot_session(session_id):
    session = ChatSession.query.get_or_404(session_id)
    if session.author != current_user:
        abort(403)
    all_sessions = ChatSession.query.filter_by(author=current_user).order_by(ChatSession.timestamp.desc()).all()
    messages = session.messages.order_by(ChatMessage.timestamp.asc()).all()
    return render_template('chatbot.html', title=session.title, 
                           current_session=session, all_sessions=all_sessions, history=messages)


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

# app/routes.py

@bp.route('/rename-session/<int:session_id>', methods=['POST'])
@login_required
def rename_session(session_id):
    session = ChatSession.query.get_or_404(session_id)
    if session.author != current_user:
        abort(403)
    
    new_title = request.get_json().get('title')
    if new_title and len(new_title.strip()) > 0:
        session.title = new_title.strip()
        db.session.commit()
        return jsonify({'status': 'success', 'new_title': session.title})
    
    return jsonify({'status': 'error', 'message': 'Nama tidak boleh kosong'}), 400

# ===============================================
# RUTE API UNTUK AI
# ===============================================
@bp.route('/chat-ai/<int:session_id>', methods=['POST'])
@login_required
def chat_ai(session_id):
    if not ark_client:
        return jsonify({'error': 'Layanan AI saat ini tidak tersedia.'}), 503
    
    session = ChatSession.query.get_or_404(session_id)
    if session.author != current_user:
        abort(403)
    
    user_message_content = request.get_json().get('message')
    if not user_message_content:
        return jsonify({'error': 'Pesan tidak boleh kosong'}), 400

    user_message = ChatMessage(session_id=session.id, author=current_user, role='user', content=user_message_content)
    db.session.add(user_message)
    
    recent_history = session.messages.order_by(ChatMessage.timestamp.desc()).limit(10).all()
    recent_history.reverse()

    completed_lessons_count = UserProgress.query.filter_by(user_id=current_user.id).count()
    user_context = (
        f"Nama pengguna: {current_user.name}, seorang mahasiswa semester {current_user.semester}. "
        f"Fokus karier yang ia minati adalah {current_user.career_path}. "
        f"Progres belajar saat ini: sudah menyelesaikan {completed_lessons_count} materi di roadmap."
    )
    system_prompt = (
        "Anda adalah Farmile, seorang mentor karier AI yang ahli, ramah, dan suportif. "
        "Selalu gunakan informasi konteks pengguna untuk memberikan jawaban yang personal dan relevan. "
        f"Konteks Pengguna: {user_context}"
    )
    
    messages = [{"role": "system", "content": system_prompt}]
    for msg in recent_history:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": user_message_content})
    
    try:
        completion = ark_client.chat.completions.create(
            model=current_app.config['MODEL_ENDPOINT_ID'],
            messages=messages
        )
        ai_response_content = completion.choices[0].message.content
        
        ai_message = ChatMessage(session_id=session.id, author=current_user, role='assistant', content=ai_response_content)
        db.session.add(ai_message)
        db.session.commit()
        
        return jsonify({'response': ai_response_content})

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"BytePlus API Error: {e}")
        return jsonify({'error': 'Gagal menghubungi layanan AI, silakan coba lagi.'}), 500