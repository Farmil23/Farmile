from flask import render_template, redirect, url_for, request, Blueprint, abort, flash
from flask_login import current_user, login_required, login_user, logout_user
from app import db, oauth
from app.models import User, ProjectSubmission

# Membuat Blueprint bernama 'routes'
bp = Blueprint('routes', __name__)

# --- Rute Utama ---
@bp.route('/')
def index():
    return render_template('index.html', title='Selamat Datang')

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
    return redirect(url_for('routes.profile'))

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.index'))

# --- Rute untuk Alur Pengguna Inti ---
@bp.route('/profile')
@login_required
def profile():
    submissions = ProjectSubmission.query.filter_by(author=current_user).all()
    return render_template('profile.html', user=current_user, submissions=submissions)

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

@bp.route('/submit-project', methods=['POST'])
@login_required
def submit_project():
    path_name = request.form.get('path_name')
    project_link = request.form.get('project_link')

    if not path_name or not project_link:
        return redirect(url_for('routes.paths'))

    submission = ProjectSubmission(
        path_name=path_name,
        project_link=project_link,
        author=current_user
    )
    db.session.add(submission)
    db.session.commit()
    
    return redirect(url_for('routes.interview', path_name=path_name))

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

@bp.route('/cancel-submission', methods=['POST'])
@login_required
def cancel_submission():
    path_name = request.form.get('path_name')

    # Cari submission yang sesuai dengan user dan path_name
    submission = ProjectSubmission.query.filter_by(author=current_user, path_name=path_name).first()

    # Jika submission ditemukan, hapus dari database
    if submission:
        db.session.delete(submission)
        db.session.commit()
        # Anda bisa menambahkan flash message di sini untuk notifikasi
        # flash('Submission proyek Anda telah berhasil dibatalkan.')

    # Arahkan pengguna kembali ke halaman pemilihan jalur
    return redirect(url_for('routes.paths'))


@bp.route('/edit-submission/<int:submission_id>', methods=['GET', 'POST'])
@login_required
def edit_submission(submission_id):
    submission = ProjectSubmission.query.get_or_404(submission_id)

    if submission.author != current_user:
        abort(403)

    if request.method == 'POST':
        new_link = request.form.get('project_link')
        if new_link:
            submission.project_link = new_link
            db.session.commit()
            # TAMBAHKAN BARIS INI
            flash('Link proyek berhasil diperbarui!', 'success')
            return redirect(url_for('routes.profile'))

    return render_template('edit_submission.html', title="Edit Link Proyek", submission=submission)


# --- Rute Tes untuk Error 500 ---
@bp.route('/test500')
def test_500():
    raise RuntimeError("Ini adalah error tes internal!")

# --- Error Handlers (terdaftar di __init__.py, tapi bisa diletakkan di sini jika menggunakan blueprint error handler) ---
# Untuk sekarang, error handler tetap di __init__.py agar bersifat global.