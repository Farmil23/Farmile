from app import create_app, db

app = create_app()

@app.shell_context_processor
def make_shell_context():
    # Impor model di sini untuk shell context yang aman
    from app.models import (User, Project, ProjectSubmission, ChatMessage, 
                            ChatSession, Module, Lesson, UserProgress, Task, 
                            Event, Note, Notification, UserProject, UserResume, 
                            JobApplication, JobCoachMessage, JobMatchAnalysis, 
                            ConnectionRequest, Conversation, DirectMessage, 
                            StudyGroup, UserActivityLog, QuizHistory)
    return {
        'db': db, 'User': User, 'Project': Project, 'ProjectSubmission': ProjectSubmission,
        'ChatMessage': ChatMessage, 'ChatSession': ChatSession, 'Module': Module,
        'Lesson': Lesson, 'UserProgress': UserProgress, 'Task': Task, 'Event': Event,
        'Note': Note, 'Notification': Notification, 'UserProject': UserProject,
        'UserResume': UserResume, 'JobApplication': JobApplication, 
        'JobCoachMessage': JobCoachMessage, 'JobMatchAnalysis': JobMatchAnalysis,
        'ConnectionRequest': ConnectionRequest, 'Conversation': Conversation,
        'DirectMessage': DirectMessage, 'StudyGroup': StudyGroup, 
        'UserActivityLog': UserActivityLog, 'QuizHistory': QuizHistory
    }

if __name__ == '__main__':
    # use_reloader=False penting untuk mencegah scheduler berjalan dua kali dalam mode debug
    app.run(debug=True, use_reloader=False)