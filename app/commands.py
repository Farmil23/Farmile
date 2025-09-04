import click
from flask.cli import with_appcontext
from . import db
from .models import User

@click.command(name='ensure_admin')
@with_appcontext
def ensure_admin():
    """
    Memastikan user admin ada dan memiliki status admin.
    Jika user tidak ada, user akan dibuat.
    Jika user ada tetapi bukan admin, statusnya akan diupdate.
    """
    admin_email = 'farmiljobs@gmail.com'
    user = User.query.filter_by(email=admin_email).first()

    if not user:
        # Jika user sama sekali tidak ada, buat baru
        print(f"User dengan email {admin_email} tidak ditemukan. Membuat user baru...")
        admin = User(
            name="Admin Farmil",
            email=admin_email,
            is_admin=True,
            has_completed_onboarding=True, # Sesuaikan field ini jika perlu
            google_id='admin_manual_id'      # Tambahkan nilai placeholder ini
        )
        db.session.add(admin)
        db.session.commit()
        print(f"Admin '{admin_email}' berhasil dibuat.")
    elif not user.is_admin:
        # Jika user ada tapi bukan admin, update statusnya
        print(f"User '{admin_email}' ditemukan, mengubah status menjadi admin...")
        user.is_admin = True
        db.session.commit()
        print(f"User '{admin_email}' berhasil diupdate menjadi admin.")
    else:
        # Jika user sudah ada dan sudah menjadi admin
        print(f"User '{admin_email}' sudah menjadi admin.")