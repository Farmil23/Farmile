from app import create_app, db
from app.models import User, UserProgress, ProjectSubmission, Notification
from sqlalchemy.orm import joinedload

app = create_app()

def award_xp_backfill(user, action, count=1):
    """Fungsi award_xp yang disederhanakan untuk backfill."""
    xp_map = {
        'completed_lesson': 10,
        'submitted_project': 25,
        'passed_quiz': 5,
        'high_interview_score': 50,
        'used_ai_mentor': 2,
        'added_connection': 5
    }
    xp_to_add = xp_map.get(action, 0) * count
    if xp_to_add > 0:
        user.xp += xp_to_add

def run_backfill():
    """Menghitung ulang dan memperbarui XP untuk semua pengguna."""
    with app.app_context():
        all_users = User.query.all()
        
        print(f"Memulai proses backfill untuk {len(all_users)} pengguna...")

        for user in all_users:
            print(f"\nMemproses pengguna: {user.name} (ID: {user.id})")
            
            # Reset XP dan Level ke default sebelum menghitung ulang
            original_xp = user.xp
            user.xp = 0
            user.level = 1
            
            # 1. Hitung XP dari materi yang selesai
            completed_lessons_count = user.user_progress.count()
            if completed_lessons_count > 0:
                award_xp_backfill(user, 'completed_lesson', completed_lessons_count)
                print(f"  - Menemukan {completed_lessons_count} materi selesai. Menambahkan {completed_lessons_count * 10} XP.")

            # 2. Hitung XP dari proyek yang disubmit
            submitted_projects_count = user.submissions.count()
            if submitted_projects_count > 0:
                award_xp_backfill(user, 'submitted_project', submitted_projects_count)
                print(f"  - Menemukan {submitted_projects_count} proyek disubmit. Menambahkan {submitted_projects_count * 25} XP.")

            # 3. Hitung XP bonus dari skor wawancara tinggi
            high_score_submissions = user.submissions.filter(ProjectSubmission.interview_score >= 80).count()
            if high_score_submissions > 0:
                award_xp_backfill(user, 'high_interview_score', high_score_submissions)
                print(f"  - Menemukan {high_score_submissions} skor wawancara tinggi. Menambahkan {high_score_submissions * 50} XP bonus.")

            # Hitung ulang level setelah semua XP ditambahkan
            if user.xp > 0:
                user.level = (user.xp // 100) + 1
            
            print(f"  -> Selesai. XP lama: {original_xp}, XP Baru: {user.xp}, Level Baru: {user.level}")

        # Simpan semua perubahan ke database
        db.session.commit()
        print("\n✅ Proses backfill XP selesai untuk semua pengguna!")

if __name__ == '__main__':
    run_backfill()