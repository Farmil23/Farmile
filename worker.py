# nama file: worker.py
import time
from app import create_app
from app.scheduler_jobs import check_reminders
from apscheduler.schedulers.background import BackgroundScheduler

print("Starting background worker...")
app = create_app()
app.app_context().push()

scheduler = BackgroundScheduler(daemon=True)
# Menjalankan job setiap 60 detik, sama seperti di __init__.py
scheduler.add_job(check_reminders, 'interval', seconds=60, args=[app])
scheduler.start()
print("Scheduler started.")

# Loop ini menjaga agar worker tetap berjalan
try:
    while True:
        time.sleep(3600)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()