from flask import Blueprint, request, jsonify, render_template, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Task, UserActivityLog
from app.ai_logic import run_liquid_scheduler, estimate_task_duration, feynman_test, stoic_mentor

bp = Blueprint('ai', __name__, url_prefix='/ai')

@bp.route('/chat', methods=['POST'])
@login_required
def chat():
    data = request.get_json()
    user_message = data.get('message')
    
    # 1. Fetch Schedule Context (Simple Mockup for now)
    # in prod: query Task and Event models for today/tomorrow
    schedule_context = "User has 'Deep Learning' tonight at 8 PM. 'Volleyball' at 5 PM."
    
    # 2. Run Liquid Scheduler Agent
    result = run_liquid_scheduler(user_message, schedule_context)
    
    # 3. Handle Actions
    if result.get('action') == 'reschedule':
        # Apply changes to DB (Mock logic)
        # In real impl: Iterate proposed_changes and update Task/Event
        pass
        
    return jsonify(result)

@bp.route('/estimate', methods=['POST'])
@login_required
def estimate():
    data = request.get_json()
    title = data.get('title')
    pages = int(data.get('pages', 0))
    is_coding = data.get('is_coding') == 'true'
    
    minutes = estimate_task_duration(title, pages, is_coding)
    
    hours = minutes / 60
    return jsonify({'minutes': minutes, 'hours': hours, 'message': f"Estimasi: {hours:.1f} Jam"})

@bp.route('/feynman', methods=['POST'])
@login_required
def feynman():
    data = request.get_json()
    topic = data.get('topic')
    explanation = data.get('explanation')
    history = data.get('history', [])
    
    response = feynman_test(topic, explanation, history)
    
    return jsonify({'response': response})

@bp.route('/ovt', methods=['GET'])
@login_required
def ovt_panic():
    # Gather stats
    stats = {
        'gpa': 3.97, # Mock or fetch from user model if exists
        'completed_tasks': 8, # Mock query
        'level': current_user.level
    }
    
    response = stoic_mentor(stats)
    return jsonify(response)
