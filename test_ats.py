from app import create_app, db
from app.models import User, UserResume, JobMatchAnalysis

app = create_app()
with app.app_context():
    # Find a resume first, then its user
    resume = UserResume.query.first()
    if resume:
        user = resume.author
        print(f"User found: {user.name} (ID: {user.id})")
        print(f"Resume found: {resume.original_filename} (ID: {resume.id})")
        
        # Simulate match job description API
        from app.routes import ark_client
        from flask import current_app
        
        prompt = f"""
        PERAN DAN TUJUAN:
        Anda adalah seorang Pakar Perekrutan Teknologi...
        """
        
        try:
            # Mock AI test
            print("Testing AI completion...")
            completion = ark_client.chat.completions.create(
                model=current_app.config['MODEL_ENDPOINT_ID'],
                messages=[{"role": "user", "content": "Hello, say 'Test OK'"}]
            )
            print(f"AI Response: {completion.choices[0].message.content}")
            
            # Test Database Insert
            print("Testing DB insert...")
            new_analysis = JobMatchAnalysis(
                user_resume_id=resume.id,
                job_description="Software Engineer testing",
                match_result="<h1>Match Result Mock</h1>"
            )
            db.session.add(new_analysis)
            db.session.commit()
            print("DB Insert OK.")
            
        except Exception as e:
            print(f"ERROR: {e}")
    else:
        print("No resume found for testing. App is empty.")
