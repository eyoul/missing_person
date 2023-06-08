import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from missing.auth import login_required_role
from missing.db import get_db

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/dashboard')
@login_required_role(1)  # '1' is the role_id for the admin role
def dashboard():
    # Get some quick stats for the dashboard
    total_reports = get_total_reports()
    active_reports = get_active_reports()
    resolved_reports = get_resolved_reports()

    return render_template('admin/dashboard.html', total_reports=total_reports,
                           active_reports=active_reports, resolved_reports=resolved_reports)

def get_total_reports():
    db = get_db()
    result = db.execute('SELECT COUNT(*) FROM post').fetchone()
    return result[0]


def get_active_reports():
    db = get_db()
    result = db.execute('SELECT COUNT(*) FROM post WHERE status = "active"').fetchone()
    return result[0]


def get_resolved_reports():
    db = get_db()
    result = db.execute('SELECT COUNT(*) FROM post WHERE status = "resolved"').fetchone()
    return result[0]


@bp.route('/users')
@login_required_role(1)  # '1' is the role_id for the admin role
def users():
    # Get a list of all users
    users = get_all_users()

    return render_template('admin/users.html', users=users)

def get_all_users():
    db = get_db()
    users = db.execute('SELECT * FROM user').fetchall()
    return users


@bp.route('/reports')
@login_required_role(1)  # '1' is the role_id for the admin role
def reports():
    db = get_db()
    reports = db.execute('SELECT * FROM post').fetchall()
    return render_template('admin/reports.html', reports=reports)


@bp.route('/settings')
@login_required_role(1)  # '1' is the role_id for the admin role
def settings():
    # Get some application settings
    app_name = get_app_name()
    default_location = get_default_location()
    max_reports_per_user = get_max_reports_per_user()

    return render_template('admin/settings.html', app_name=app_name,
                           default_location=default_location,
                           max_reports_per_user=max_reports_per_user)

def get_app_name():
    db = get_db()
    result = db.execute('SELECT value FROM settings WHERE name = "post"').fetchone()
    return result[0]


def get_default_location():
    db = get_db()
    result = db.execute('SELECT value FROM settings WHERE name = "default_location"').fetchone()
    return result[0]


def get_max_reports_per_user():
    db = get_db()
    result = db.execute('SELECT value FROM settings WHERE name = "max_reports_per_user"').fetchone()
    return result[0]
