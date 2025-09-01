from flask import render_template, redirect, url_for, request, Blueprint, abort, flash, jsonify
from flask_login import current_user, login_required, login_user, logout_user
from app import db, oauth
from app.models import User, ProjectSubmission
from app import ark_client
from flask import current_app

# Membuat Blueprint bernama 'routes'
bp = Blueprint('routes', __name__)

# app/routes.py

@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('routes.dashboard'))
    return render_template('landing_page.html', title='Selamat Datang di FARSIGHT')

# app/routes.py

@bp.route('/profile')
@login_required
def profile():
    # Nantinya kita bisa tambahkan query untuk mengambil data badge
    return render_template('profile.html', title="Profil Saya")

# Buat rute dasbor placeholder
@bp.route('/dashboard')
@login_required
def dashboard():
    # Untuk sementara, kita buat halaman dasbor yang sederhana
    return render_template('dashboard.html', title='Dasbor Anda')

# --- Rute untuk Autentikasi ---
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
        user = User(
            google_id=user_info['sub'],
            name=user_info['name'],
            email=user_info['email'],
            profile_pic=user_info['picture']
        )
        db.session.add(user)
        db.session.commit()
    
    login_user(user)
    # Ganti baris 'return redirect(...)' dengan logika ini:
    if not current_user.has_completed_onboarding:
        return redirect(url_for('routes.onboarding'))
    else:
        return redirect(url_for('routes.dashboard'))

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.index'))


@bp.route('/paths')
@login_required
def paths():
    career_paths = [
        {'id': 'frontend', 'title': 'Frontend Developer', 'desc': 'Membangun antarmuka visual yang interaktif dan menarik bagi pengguna.'},
        {'id': 'backend', 'title': 'Backend Developer', 'desc': 'Merancang logika, database, dan API yang menjadi otak dari sebuah aplikasi.'},
        {'id': 'data-analyst', 'title': 'Data Analyst', 'desc': 'Menganalisis data untuk menemukan wawasan bisnis dan tren yang berharga.'}
    ]
    return render_template('paths.html', title="Pilih Jalur Karier", paths=career_paths)

@bp.route('/project/<path_name>')
@login_required
def project(path_name):
    project_details = {
        'frontend': {'title': 'Proyek Landing Page Interaktif', 'desc': 'Buat sebuah landing page untuk produk fiktif menggunakan HTML, CSS, dan JavaScript. Halaman harus responsif dan memiliki setidaknya satu elemen interaktif (misal: image slider, form validation).'},
        'backend': {'title': 'Proyek API Sederhana', 'desc': 'Rancang dan bangun sebuah REST API sederhana untuk "To-Do List". API harus memiliki endpoint untuk membuat, membaca, dan menghapus tugas.'},
        'data-analyst': {'title': 'Proyek Analisis Data Penjualan', 'desc': 'Analisis dataset penjualan fiktif menggunakan Python (Pandas & Matplotlib) untuk menemukan produk terlaris, tren penjualan bulanan, dan demografi pelanggan utama.'}
    }
    
    detail = project_details.get(path_name)
    if not detail:
        return redirect(url_for('routes.paths'))

    return render_template('project.html', title=detail['title'], detail=detail, path_name=path_name)


@bp.route('/interview/<path_name>')
@login_required
def interview(path_name):
    submission = ProjectSubmission.query.filter_by(author=current_user, path_name=path_name).first_or_404()
    
    # Keamanan tambahan: Pastikan submission ini benar-benar milik user yang login
    if submission.author != current_user:
        abort(403)

    return render_template('interview.html', title=f"Wawancara {submission.path_name.replace('-', ' ').title()}", submission=submission)


# app/routes.py

# ... (setelah fungsi interview) ...

# app/routes.py

@bp.route('/cancel-submission', methods=['POST'])
@login_required
def cancel_submission():
    path_name = request.form.get('path_name')
    origin = request.form.get('origin') # Ambil penanda 'origin'

    submission = ProjectSubmission.query.filter_by(author=current_user, path_name=path_name).first()

    if submission:
        db.session.delete(submission)
        db.session.commit()
        flash('Submission proyek berhasil dibatalkan.', 'success')

    # Jika origin adalah 'profile', kembali ke profil. Jika tidak, kembali ke paths.
    if origin == 'profile':
        return redirect(url_for('routes.profile'))
    
    return redirect(url_for('routes.paths'))


# app/routes.py

@bp.route('/edit-submission/<int:submission_id>', methods=['GET', 'POST'])
@login_required
def edit_submission(submission_id):
    submission = ProjectSubmission.query.get_or_404(submission_id)
    next_url = request.args.get('next') # Ambil 'next' dari URL saat GET

    if submission.author != current_user:
        abort(403)

    if request.method == 'POST':
        new_link = request.form.get('project_link')
        next_url_from_form = request.form.get('next_url') # Ambil 'next' dari form saat POST

        if new_link:
            submission.project_link = new_link
            db.session.commit()
            flash('Link proyek berhasil diperbarui!', 'success')
        
        # Jika ada next_url, kembali ke sana. Jika tidak, kembali ke profil.
        if next_url_from_form:
            return redirect(next_url_from_form)
        return redirect(url_for('routes.profile'))

    return render_template('edit_submission.html', title="Edit Link Proyek", submission=submission, next_url=next_url)

# --- Rute Tes untuk Error 500 ---
@bp.route('/test500')
def test_500():
    raise RuntimeError("Ini adalah error tes internal!")

# --- Error Handlers (terdaftar di __init__.py, tapi bisa diletakkan di sini jika menggunakan blueprint error handler) ---
# Untuk sekarang, error handler tetap di __init__.py agar bersifat global.


# app/routes.py

@bp.route('/onboarding')
@login_required
def onboarding():
    if current_user.has_completed_onboarding:
        return redirect(url_for('routes.dashboard'))
    return render_template('onboarding.html', title='Selamat Datang')



# app/routes.py

# app/routes.py
@bp.route('/complete-onboarding', methods=['POST'])
@login_required
def complete_onboarding():
    data = request.get_json()
    
    # Ambil semua data baru dari frontend
    user_name = data.get('user_name')
    semester = data.get('semester')
    career_focus = data.get('career_focus')

    # Update profil pengguna di database
    if user_name:
        current_user.name = user_name
    if semester:
        current_user.semester = int(semester)
    if career_focus:
        current_user.career_path = career_focus
    
    current_user.has_completed_onboarding = True
    db.session.commit()
    
    return jsonify({'status': 'success', 'redirect_url': url_for('routes.dashboard')})

import json


@bp.route('/onboarding-chat', methods=['POST'])
@login_required
def onboarding_chat():
    # Pastikan klien AI sudah siap
    if not ark_client:
        return jsonify({'error': 'Layanan AI saat ini tidak tersedia.'}), 503

    data = request.get_json()
    message = data.get('message')
    conversation_history = data.get('history', [])

    if not message:
        return jsonify({'error': 'Pesan tidak boleh kosong'}), 400

    # Tentukan instruksi untuk AI (system prompt)
    system_prompt = ""
    # ... (logika system_prompt yang sudah ada tetap sama) ...
    if not conversation_history: 
        if "belum" in message.lower() or "bingung" in message.lower():
            system_prompt = "Anda adalah seorang konsultan karier AI yang ramah. Tugas Anda adalah membantu pengguna yang bingung menemukan minat kariernya. Mulai dengan menanyakan tentang mata kuliah atau hobi yang paling ia nikmati."
        else:
            system_prompt = "Anda adalah seorang konsultan karier AI yang suportif. Pengguna sudah memiliki fokus karier. Tugas Anda adalah bertanya lebih dalam tentang pemahamannya di bidang itu untuk melengkapi profilnya. Mulai dengan menanyakan materi atau teknologi apa saja yang sudah ia pelajari."
    else:
        system_prompt = "Anda adalah seorang konsultan karier AI yang ramah. Lanjutkan percakapan dengan pengguna secara natural untuk menggali lebih dalam jawaban mereka."

    # Siapkan format pesan
    messages = [{"role": "system", "content": system_prompt}]
    for turn in conversation_history:
        messages.append({"role": "user", "content": turn['user']})
        messages.append({"role": "assistant", "content": turn['ai']})
    messages.append({"role": "user", "content": message})

    try:
        # PANGGIL API DENGAN METODE BARU
        completion = ark_client.chat.completions.create(
            model=current_app.config['MODEL_ENDPOINT_ID'],
            messages=messages,
        )
        ai_response = completion.choices[0].message.content

    except Exception as e:
        current_app.logger.error(f"BytePlus API Error: {e}")
        ai_response = "Maaf, sepertinya ada sedikit masalah dengan AI. Boleh coba ulangi lagi?"
        return jsonify({'response': ai_response}), 500

    return jsonify({'response': ai_response})

# app/routes.py

@bp.route('/my-projects')
@login_required
def my_projects():
    submissions = ProjectSubmission.query.filter_by(author=current_user).order_by(ProjectSubmission.id.desc()).all()
    return render_template('my_projects.html', title="Proyek Saya", submissions=submissions)

# app/routes.py

# RUTE BARU: Untuk menampilkan halaman pemilihan proyek
@bp.route('/select-project')
@login_required
def select_project():
    if not current_user.career_path:
        flash('Silakan selesaikan onboarding untuk menentukan jalur karier Anda.', 'warning')
        return redirect(url_for('routes.dashboard'))

    # Cari proyek yang sudah pernah disubmit oleh user
    submitted_project_ids = [sub.project_id for sub in current_user.submissions]
    
    # Ambil semua proyek yang tersedia untuk jalur karier user, KECUALI yang sudah disubmit
    available_projects = Project.query.filter(
        Project.career_path == current_user.career_path,
        Project.id.notin_(submitted_project_ids)
    ).all()

    return render_template('select_project.html', title="Pilih Proyek Baru", projects=available_projects)


# MODIFIKASI RUTE submit_project
# Hapus rute /submit-project yang lama dan ganti dengan ini
@bp.route('/submit-project/<int:project_id>', methods=['POST'])
@login_required
def submit_project(project_id):
    project = Project.query.get_or_404(project_id)
    project_link = request.form.get('project_link')

    # Validasi...
    
    submission = ProjectSubmission(
        project_id=project.id,
        user_id=current_user.id,
        project_link=project_link
    )
    db.session.add(submission)
    db.session.commit()
    
    flash(f"Proyek '{project.title}' berhasil disubmit!", 'success')
    return redirect(url_for('routes.my_projects'))

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

