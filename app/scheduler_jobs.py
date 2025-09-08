# File: app/scheduler_jobs.py

from datetime import datetime, timedelta, timezone
import pytz
from .models import Event, Task, Notification
from . import db

def check_reminders(app):
    """
    Fungsi ini akan dijalankan setiap menit oleh scheduler.
    Ia mencari acara/tugas yang perlu diingatkan dan membuat notifikasi.
    """
    with app.app_context():
        # Definisikan zona waktu yang relevan
        WIB = pytz.timezone('Asia/Jakarta')
        UTC = pytz.utc

        # Dapatkan waktu UTC sekarang yang sudah timezone-aware
        now_utc = datetime.now(UTC)
        print(f"[{datetime.now(WIB).strftime('%Y-%m-%d %H:%M:%S')}] Pengecekan (Waktu UTC: {now_utc.isoformat()})")

        try:
            # 1. Cek Acara (Events)
            events_to_remind = db.session.query(Event).filter(Event.reminder_minutes > 0).all()
            if events_to_remind:
                for event in events_to_remind:
                    # Anggap waktu dari DB adalah Waktu Indonesia Barat (WIB)
                    naive_start_time = event.start_time
                    wib_start_time = WIB.localize(naive_start_time)
                    # Konversi waktu WIB tersebut ke UTC untuk perbandingan
                    start_time_utc = wib_start_time.astimezone(UTC)
                    
                    reminder_time_utc = start_time_utc - timedelta(minutes=event.reminder_minutes)

                    # BLOK DEBUG DETAIL
                    print(f"\n--- Memeriksa Event: '{event.title}' ---")
                    print(f"    - Waktu Acara (UTC): {start_time_utc.isoformat()}")
                    print(f"    - Waktu Pengingat (UTC): {reminder_time_utc.isoformat()}")
                    print(f"    - Jendela Pengecekan (UTC): antara {(now_utc - timedelta(minutes=1)).isoformat()} dan {now_utc.isoformat()}")

                    # Logika pengecekan waktu yang lebih fleksibel
                    if reminder_time_utc <= now_utc and start_time_utc > now_utc:
                        message = f"Pengingat: Acara '{event.title}' akan dimulai dalam {event.reminder_minutes} menit."
                        existing_notif = Notification.query.filter_by(user_id=event.user_id, message=message).first()
                        
                        if not existing_notif:
                            notif = Notification(user_id=event.user_id, message=message, link="/personal_hub")
                            db.session.add(notif)
                            print(f"  -> MEMBUAT NOTIFIKASI EVENT: {event.title}")
                        else:
                            print(f"  -> Notifikasi untuk '{event.title}' sudah ada, dilewati.")
                    else:
                        print(f"  -> Waktu pengingat untuk '{event.title}' belum tiba atau sudah lewat.")

            # 2. Cek Tugas (Tasks)
            tasks_to_remind = db.session.query(Task).filter(Task.reminder_minutes > 0).all()
            if tasks_to_remind:
                 for task in tasks_to_remind:
                    if task.due_date:
                        # Logika yang sama untuk tugas
                        naive_due_date = task.due_date
                        wib_due_date = WIB.localize(naive_due_date)
                        due_date_utc = wib_due_date.astimezone(UTC)
                        reminder_time_utc = due_date_utc - timedelta(minutes=task.reminder_minutes)
                        
                        if reminder_time_utc <= now_utc and due_date_utc > now_utc:
                            message = f"Pengingat: Deadline '{task.title}' akan tiba dalam {task.reminder_minutes} menit."
                            existing_notif = Notification.query.filter_by(user_id=task.user_id, message=message).first()
                            
                            if not existing_notif:
                                notif = Notification(user_id=task.user_id, message=message, link="/personal_hub")
                                db.session.add(notif)
                                print(f"  -> MEMBUAT NOTIFIKASI TUGAS: {task.title}")
            
            db.session.commit()
        except Exception as e:
            print(f"ERROR dalam scheduler: {e}")
            db.session.rollback()