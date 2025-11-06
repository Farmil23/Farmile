# File: app/admin_views.py

from flask import redirect, url_for, request
from flask_login import current_user
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose
from markupsafe import Markup
from sqlalchemy import func, cast, String
from datetime import datetime, timedelta

# Class dasar yang aman untuk semua view di admin panel
class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('routes.login', next=request.url))

# Semua class view Anda yang lain dipindahkan ke sini
class UserView(SecureModelView):
    column_list = ('id', 'name', 'email', 'semester', 'career_path', 'is_admin')
    column_searchable_list = ('name', 'email')
    column_filters = ('is_admin', 'semester', 'career_path')
    column_formatters = {'email': lambda view, context, model, name: Markup(f'<a href="mailto:{model.email}">{model.email}</a>')}

class TaskView(SecureModelView):
    column_list = ('id', 'title', 'author', 'due_date', 'priority', 'status')
    column_searchable_list = ('title', 'author.name')
    column_filters = ('priority', 'status', 'due_date')

class EventView(SecureModelView):
    column_list = ('id', 'title', 'author', 'start_time', 'end_time')
    column_searchable_list = ('title', 'author.name')
    column_filters = ('start_time',)

class LessonView(SecureModelView):
    column_list = ('order', 'title', 'module', 'lesson_type', 'estimated_time')
    column_searchable_list = ('title', 'description')
    column_filters = ('lesson_type', 'module.title')
    form_columns = ('module', 'title', 'description', 'order', 'lesson_type', 'url', 'estimated_time', 'content', 'quiz')
    form_ajax_refs = {'module': {'fields': ['title'], 'page_size': 10}}

class ProjectView(SecureModelView):
    column_list = ('title', 'module', 'difficulty', 'is_challenge')
    column_searchable_list = ('title', 'description', 'tech_stack')
    column_filters = ('difficulty', 'is_challenge', 'module.title')
    form_columns = ('module', 'title', 'description', 'difficulty', 'is_challenge', 'project_goals', 'tech_stack', 'evaluation_criteria', 'resources')
    form_ajax_refs = {'module': {'fields': ['title'], 'page_size': 10}}

class ModuleView(SecureModelView):
    column_list = ('title', 'roadmap', 'career_path', 'order', 'level')
    column_searchable_list = ('title',)
    column_filters = ('career_path', 'level', 'roadmap.title')
    form_columns = ('roadmap', 'user', 'title', 'order', 'career_path', 'level')
    form_ajax_refs = {'roadmap': {'fields': ['title'], 'page_size': 10}, 'user': {'fields': ['name', 'email'], 'page_size': 10}}

class SubmissionView(SecureModelView):
    column_list = ('id', 'project', 'author', 'interview_score', 'project_link')
    column_searchable_list = ('project.title', 'author.name')
    column_filters = ('interview_score',)
    form_columns = ('project', 'author', 'project_link', 'interview_score', 'interview_feedback')
    form_ajax_refs = {'project': {'fields': ['title'], 'page_size': 10}, 'author': {'fields': ['name', 'email'], 'page_size': 10}}

class UserProjectView(SecureModelView):
    column_list = ('id', 'user', 'project', 'status', 'started_at')
    column_searchable_list = ('user.name', 'project.title')
    column_filters = ('status',)
    form_columns = ('user', 'project', 'status', 'started_at', 'reflection')
    form_ajax_refs = {'user': {'fields': ['name', 'email'], 'page_size': 10}, 'project': {'fields': ['title'], 'page_size': 10}}

class CertificateView(SecureModelView):
    column_list = ('id', 'user', 'roadmap', 'career_path', 'issued_at')
    column_searchable_list = ('user.name', 'user.email', 'career_path')
    column_filters = ('career_path', 'issued_at')
    form_columns = ('user', 'roadmap', 'career_path', 'total_hours', 'projects_completed_json')
    form_ajax_refs = {'user': {'fields': ['name', 'email'], 'page_size': 10}, 'roadmap': {'fields': ['title'], 'page_size': 10}}

class JobApplicationView(SecureModelView):
    can_create = True
    can_edit = True
    can_delete = True
    column_list = ('id', 'author', 'company_name', 'position', 'status', 'application_date', 'resume_used')
    column_searchable_list = ('author.name', 'company_name', 'position')
    column_filters = ('status', 'application_date', 'author.name')
    form_columns = ('author', 'company_name', 'position', 'status', 'application_date', 'work_model', 'job_link', 'notes', 'resume_used')
    form_ajax_refs = {'author': {'fields': ['name', 'email'], 'page_size': 10}, 'resume_used': {'fields': ['original_filename'], 'page_size': 10}}

class AnalyticsView(BaseView):
    @expose('/')
    def index(self):
        from app import db, models
        feature_usage_query = db.session.query(models.UserActivityLog.action, func.count(models.UserActivityLog.action)).group_by(models.UserActivityLog.action).all()
        feature_usage_chart_data = {"labels": [row[0] for row in feature_usage_query], "data": [row[1] for row in feature_usage_query]}
        top_users = db.session.query(models.User.name, func.count(models.UserActivityLog.id).label('total_activities')).join(models.UserActivityLog).group_by(models.User.name).order_by(db.desc('total_activities')).limit(5).all()
        top_lessons = db.session.query(models.Lesson.title, func.count(models.UserActivityLog.id).label('view_count')).join(models.UserActivityLog, func.json_extract(models.UserActivityLog.details, '$.lesson_id') == cast(models.Lesson.id, String)).filter(models.UserActivityLog.action == 'viewed_lesson').group_by(models.Lesson.title).order_by(db.desc('view_count')).limit(5).all()
        top_projects = db.session.query(models.Project.title, func.count(models.ProjectSubmission.id).label('submission_count')).join(models.ProjectSubmission).group_by(models.Project.title).order_by(db.desc('submission_count')).limit(5).all()
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        daily_activity_query = db.session.query(func.date(models.UserActivityLog.timestamp), func.count(models.UserActivityLog.id)).filter(models.UserActivityLog.timestamp >= seven_days_ago).group_by(func.date(models.UserActivityLog.timestamp)).order_by(func.date(models.UserActivityLog.timestamp)).all()
        daily_activity_chart_data = {"labels": [datetime.strptime(date_str, '%Y-%m-%d').strftime('%d %b') for date_str, count in daily_activity_query], "data": [count for date_str, count in daily_activity_query]}
        total_resumes_analyzed = db.session.query(func.count(models.UserResume.id)).scalar()
        total_jobs_tracked = db.session.query(func.count(models.JobApplication.id)).scalar()
        total_coach_sessions = db.session.query(func.count(func.distinct(models.JobCoachMessage.application_id))).scalar()
        job_status_distribution_query = db.session.query(models.JobApplication.status, func.count(models.JobApplication.status)).group_by(models.JobApplication.status).all()
        job_status_chart_data = {"labels": [row[0] for row in job_status_distribution_query], "data": [row[1] for row in job_status_distribution_query]}
        saved_snapshots = models.AnalyticsSnapshot.query.order_by(models.AnalyticsSnapshot.created_at.desc()).all()
        return self.render('admin/analytics_index.html', feature_usage_chart_data=feature_usage_chart_data, daily_activity_chart_data=daily_activity_chart_data, top_users=top_users, top_lessons=top_lessons, top_projects=top_projects, total_resumes_analyzed=total_resumes_analyzed, total_jobs_tracked=total_jobs_tracked, total_coach_sessions=total_coach_sessions, job_status_chart_data=job_status_chart_data, saved_snapshots=saved_snapshots)
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('routes.login', next=request.url))