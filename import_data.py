# import_data.py
import csv
from app import create_app, db
from app.models import (
    User, Roadmap, Module, Lesson, Project,
    UserProgress, ProjectSubmission, UserProject,
    Task, Event, UserResume, JobApplication,
    JobCoachMessage, JobMatchAnalysis,
    Conversation, DirectMessage, StudyGroup, Note,
    UserActivityLog, QuizHistory, AnalyticsSnapshot,
    Certificate, ConnectionRequest, connections,
    conversation_participants, study_group_members, ChatSession, InterviewMessage, Notification, ChatMessage
)
from sqlalchemy.exc import IntegrityError
from datetime import datetime

app = create_app()

def convert_types(value):
    """Konversi string CSV ke tipe data Python yang benar."""
    if value.lower() == 'true':
        return True
    if value.lower() == 'false':
        return False
    if value == '' or value is None:
        return None
    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        try:
            return int(value)
        except (ValueError, TypeError):
            return value

def import_table_data(model_class, csv_file_path, ignore_columns=[]):
    """Membaca file CSV dan memasukkan data ke tabel."""
    print(f"Mengimpor data untuk tabel: {model_class.__tablename__} dari {csv_file_path}")

    try:
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                try:
                    row_data = {
                        k: convert_types(v) for k, v in row.items() 
                        if k not in ignore_columns
                    }
                    db.session.add(model_class(**row_data))
                    db.session.commit()
                    count += 1
                except IntegrityError:
                    db.session.rollback()
                    continue 
                except Exception as e:
                    db.session.rollback()
                    print(f"  -> Gagal mengimpor baris: {row}. Error: {e}")
            print(f"  -> Berhasil mengimpor {count} baris. Impor untuk {model_class.__tablename__} sudah selesai yaaa.")
    except FileNotFoundError:
        print(f"  -> Peringatan: File {csv_file_path} tidak ditemukan. Melewati tabel ini.")
    except Exception as e:
        print(f"  -> Terjadi kesalahan umum saat membaca file CSV: {e}")


def import_many_to_many_data(table, csv_file_path):
    """Membaca file CSV untuk tabel many-to-many dan memasukkan data."""
    print(f"Mengimpor data untuk tabel many-to-many: {table.name} dari {csv_file_path}")
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                try:
                    row_data = {k: convert_types(v) for k, v in row.items()}
                    stmt = table.insert().values(**row_data)
                    db.session.execute(stmt)
                    db.session.commit()
                    count += 1
                except IntegrityError:
                    db.session.rollback()
                    continue
                except Exception as e:
                    db.session.rollback()
                    print(f"  -> Gagal mengimpor baris: {row}. Error: {e}")
            print(f"  -> Berhasil mengimpor {count} baris.")
    except FileNotFoundError:
        print(f"  -> Peringatan: File {csv_file_path} tidak ditemukan. Melewati tabel ini.")
    except Exception as e:
        print(f"  -> Terjadi kesalahan umum saat membaca file CSV: {e}")


if __name__ == '__main__':
    with app.app_context():
        print("Memulai proses migrasi data dari SQLite ke PostgreSQL...")

        # URUTAN DELETE YANG BENAR: Mulai dari tabel anak ke tabel induk.
        db.session.execute(connections.delete())
        db.session.execute(conversation_participants.delete())
        db.session.execute(study_group_members.delete())
        db.session.query(InterviewMessage).delete()
        db.session.query(ChatMessage).delete()
        db.session.query(QuizHistory).delete()
        db.session.query(UserActivityLog).delete()
        db.session.query(JobMatchAnalysis).delete()
        db.session.query(JobCoachMessage).delete()
        db.session.query(Task).delete()
        db.session.query(ProjectSubmission).delete()
        db.session.query(ChatSession).delete()
        db.session.query(UserProject).delete()
        db.session.query(UserProgress).delete()
        db.session.query(Note).delete()
        db.session.query(DirectMessage).delete()
        db.session.query(JobApplication).delete()
        db.session.query(Notification).delete()
        db.session.query(Project).delete()
        db.session.query(Lesson).delete()
        db.session.query(ConnectionRequest).delete()
        db.session.query(Certificate).delete()
        db.session.query(Event).delete()
        db.session.query(Module).delete()
        db.session.query(UserResume).delete()
        db.session.query(AnalyticsSnapshot).delete()
        db.session.query(StudyGroup).delete()
        db.session.query(Conversation).delete()
        db.session.query(Roadmap).delete()
        db.session.query(User).delete()
        db.session.commit()
        print("Pembersihan data lama selesai.")

        # URUTAN IMPORT DATA YANG BENAR
        # Tier 1: Tabel tanpa Foreign Key
        import_table_data(User, 'dump/user.csv')
        import_table_data(Roadmap, 'dump/roadmap.csv')
        import_table_data(Conversation, 'dump/conversation.csv')
        import_table_data(StudyGroup, 'dump/study_group.csv')
        import_table_data(AnalyticsSnapshot, 'dump/analytics_snapshot.csv')
        import_table_data(UserResume, 'dump/user_resume.csv')
        
        # Tier 2: Bergantung pada Tier 1
        import_table_data(Module, 'dump/module.csv')
        import_table_data(Event, 'dump/event.csv')
        import_table_data(Notification, 'dump/notification.csv')
        import_table_data(UserActivityLog, 'dump/user_activity_log.csv')
        import_table_data(Certificate, 'dump/certificate.csv')
        import_table_data(ConnectionRequest, 'dump/connection_request.csv')
        
        # Tier 3: Bergantung pada Tier 1 & 2
        import_table_data(Lesson, 'dump/lesson.csv')
        import_table_data(Project, 'dump/project.csv')
        import_table_data(JobApplication, 'dump/job_application.csv')
        import_table_data(DirectMessage, 'dump/direct_message.csv', ignore_columns=['is_edited'])
        import_table_data(Note, 'dump/note.csv')

        # Tier 4: Bergantung pada Tier 3 dan di bawahnya
        import_table_data(UserProgress, 'dump/user_progress.csv')
        import_table_data(UserProject, 'dump/user_project.csv')
        import_table_data(ChatSession, 'dump/chat_session.csv')
        import_table_data(ProjectSubmission, 'dump/project_submission.csv')
        import_table_data(Task, 'dump/task.csv')
        import_table_data(JobCoachMessage, 'dump/job_coach_message.csv')
        import_table_data(JobMatchAnalysis, 'dump/job_match_analysis.csv')
        import_table_data(QuizHistory, 'dump/quiz_history.csv')

        # Tier 5: Bergantung pada Tier 4
        import_table_data(ChatMessage, 'dump/chat_message.csv')
        import_table_data(InterviewMessage, 'dump/interview_message.csv')

        # Import tabel many-to-many terakhir
        import_many_to_many_data(connections, 'dump/connections.csv')
        import_many_to_many_data(conversation_participants, 'dump/conversation_participants.csv')
        import_many_to_many_data(study_group_members, 'dump/study_group_members.csv')
        
        print("Semua proses import selesai.")
        
        
        
