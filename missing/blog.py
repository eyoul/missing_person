import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

# from missing.auth import login_required
from missing.db import get_db
from .auth import login_required

# upload file path
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'missing', 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, missed_name, since, missing_from, gender, age, call_on, additional_info, photo_url, status, created,  finder_id, email'
        ' FROM post p JOIN user u ON p.finder_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        missed_name = request.form['missed_name'].capitalize()
        since = request.form['since']
        missing_from = request.form['missing_from'].capitalize()
        gender = request.form['gender']
        age = request.form['age']
        call_on = request.form['call_on']
        additional_info = request.form['additional_info']
        status = request.form.get('status')
        
        error = None

        if not missed_name:
            error = 'Full Name is required.'
        elif not since:
            error = 'Date is required.'
        elif not missing_from:
            error = 'Location is required.'
        elif not gender:
            error = 'Gender is required.'
        elif not age:
            error = 'Age is required.'
        elif not call_on:
            error = 'Phone is required.'
        elif not additional_info:
            error = 'Full information is required.'
        elif not status:
            error = 'Status is required and should be either "active" or "resolved".'
        elif status not in ['active', 'resolved']:
            error = 'Invalid status. Should be either "active" or "resolved".'

        # handle photo_url upload
        if 'photo_url' not in request.files:
            error = 'Photo is required.'
        else:
            file = request.files['photo_url']
            if file.filename == '':
                error = 'Photo is required.'
            elif not allowed_file(file.filename):
                error = 'Invalid file type. Only PNG, JPG, JPEG, and GIF are allowed.'
            else:
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                
        if error is not None: 
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (missed_name, since, missing_from, gender, age, call_on, additional_info, photo_url, status, finder_id)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (missed_name, since, missing_from, gender, age, call_on, additional_info, filename, status, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


def get_post(id, check_finder=True):
    post = get_db().execute(
        'SELECT p.id, missed_name, since, missing_from,  gender, age,  call_on, additional_info, created, finder_id, email'
        ' FROM post p JOIN user u ON p.finder_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_finder and post['finder_id'] != g.user['id']:
        abort(403)

    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        missed_name = request.form['missed_name'].capitalize()
        since = request.form['since']
        missing_from = request.form['missing_from'].capitalize()
        gender = request.form['gender']
        age = request.form['age']
        call_on = request.form['call_on']
        additional_info = request.form['additional_info']
        status = request.form.get('status')
        error = None

        if not missed_name:
            error = 'Full Name is required.'
        elif not since:
            error = 'Date is required.'
        elif not missing_from:
            error = 'Location is required.'
        elif not gender:
            error = 'Gender is required.'
        elif not age:
            error = 'Age is required.'
        elif not call_on:
            error = 'Phone is required.'
        elif not additional_info:
            error = 'Full information is required.'
        elif not status:
            error = 'Status is required and should be either "active" or "resolved".'
        elif status not in ['active', 'resolved']:
            error = 'Invalid status. Should be either "active" or "resolved".'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET missed_name = ?, since = ?, missing_from = ?, gender = ?, age = ?, call_on = ?, additional_info = ?, status = ?'
                ' WHERE id = ?',
                (missed_name, since, missing_from,  gender, age,  call_on, additional_info, status, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    post = get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()

    # Delete the image from the directory (if it exists)
    filename = post['photo_url'] # Use get() to safely get the image filename
    if filename:
        path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(path):
            os.remove(path)

    flash('The post has been deleted.')
    return redirect(url_for('blog.index'))


@bp.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form['query']
        db = get_db()
        posts = db.execute(
            'SELECT p.id, missed_name, since, missing_from, gender, age, call_on, additional_info, photo_url, status, created, finder_id, email'
            ' FROM post p JOIN user u ON p.finder_id = u.id'
            ' WHERE missed_name LIKE ? OR missing_from LIKE ?',
            ('%' + query + '%', '%' + query + '%')
        ).fetchall()
        return render_template('blog/index.html', posts=posts, query=query)
    else:
        return render_template('blog/index.html')
