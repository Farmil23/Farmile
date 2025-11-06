# Di dalam file app/commands.py

import click
from flask.cli import with_appcontext
from app import db
from app.models import User
from generate.seed_llm_research import seed_llm_research

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
    
# --- PASTIKAN FUNGSI DI BAWAH INI ADA ---
@click.command('seed-llm')
@with_appcontext
def seed_llm_command():
    """Menambahkan data awal 10 modul untuk jalur karir 'LLM Research Papers'."""
    click.echo("Memulai seeder untuk 10 Modul Riset LLM...")
    seed_llm_research()
    click.echo("Selesai menjalankan LLM research seeder.")