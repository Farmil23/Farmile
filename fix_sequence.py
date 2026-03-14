from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    print("Fixing job_match_analysis sequence...")
    try:
        simple_query = text('''
        SELECT setval('job_match_analysis_id_seq', (SELECT COALESCE(MAX(id), 1) FROM job_match_analysis));
        ''')
        db.session.execute(simple_query)
        db.session.commit()
        print("Sequence fixed successfully!")
    except Exception as e:
        db.session.rollback()
        print(f"Failed to fix sequence: {e}")
