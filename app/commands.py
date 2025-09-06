# Di dalam file app/commands.py

import click
from flask.cli import with_appcontext
from app import db
from app.models import User

@click.command('ensure-admin')
@click.option('--email', prompt='Masukkan email admin', help='Email pengguna yang akan dijadikan admin.')
@with_appcontext
def ensure_admin(email):
    """Mencari pengguna berdasarkan email dan menjadikannya admin."""
    
    # Cari pengguna di database
    user = User.query.filter_by(email=email).first()
    
    if not user:
        click.echo(f"Error: Pengguna dengan email '{email}' tidak ditemukan.")
        return

    if user.is_admin:
        click.echo(f"Info: Pengguna '{user.name}' ({user.email}) sudah menjadi admin.")
        return

    # Jadikan pengguna sebagai admin
    user.is_admin = True
    db.session.commit()
    
    click.echo(f"Sukses! Pengguna '{user.name}' ({user.email}) sekarang adalah admin.")