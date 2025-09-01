from app import create_app, db
from app.models import (User, Project, ProjectSubmission, ChatMessage, 
                        ChatSession, Module, Lesson, UserProgress)

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 'User': User, 'Project': Project, 'ProjectSubmission': ProjectSubmission,
        'ChatMessage': ChatMessage, 'ChatSession': ChatSession, 'Module': Module,
        'Lesson': Lesson, 'UserProgress': UserProgress
    }

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)