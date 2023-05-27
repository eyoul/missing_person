from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from missing.auth import login_required
from missing.db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, missed_name, since, missing_from, gender, age, call_on, addtional_info, created, finder_id,email'
        ' FROM post p JOIN user u ON p.finder_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        missed_name = request.form['missed_name']
        since = request.form['since']
        missing_from = request.form['missing_from']
        gender = request.form['gender']
        age = request.form['age']
        call_on = request.form['call_on']
        addtional_info = request.form['addtional_info']
        error = None

        if not missed_name:
            error = 'Full Name is required.'
        if not since:
            error = 'Date is required.'
        if not missing_from:
            error = 'Location is required.'
        if not gender:
            error = 'Gender is required.'
        if not age:
            error = 'Age is required.'
        if not call_on:
            error = 'Phone is required.'
        if not addtional_info:
            error = 'Full information is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (missed_name, since, missing_from, gender, age, call_on, addtional_info, finder_id)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (missed_name, since, missing_from, gender, age, call_on, addtional_info, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')
