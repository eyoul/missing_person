import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from missing.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view 


def login_required_role(role_id):
    def decorator(f):
        @functools.wraps(f)
        def wrapped_view(*args, **kwargs):
            if g.user is None:
                return redirect(url_for('auth.login'))

            if g.user['role_id'] != role_id:
                return redirect(url_for('auth.unauthorized'))

            return f(*args, **kwargs)
        return wrapped_view
    return decorator


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        finder_name = request.form['finder_name']
        phone = request.form['phone']
        finder_location = request.form['finder_location']
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None

        if not finder_name:
            error = 'Name is required.'
        elif not phone:
            error = 'Phone is required.'
        elif not finder_location:
            error = 'location is required.'
        elif not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (finder_name, phone, finder_location, email, password, role_id) VALUES (?, ?, ?, ?, ?, ?)",
                    (finder_name, phone, finder_location, email, generate_password_hash(password), 2),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {email} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE email = ?', (email,)
        ).fetchone()

        if user is None:
            error = 'Incorrect email.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            if user['role_id'] == 1:
                return redirect(url_for('admin.dashboard'))
            elif user['role_id'] == 2:
                return redirect(url_for('index'))
            else:
                error = 'Invalid role.'

        flash(error)

    return render_template('auth/login.html')

@bp.route('/add_user', methods=('GET', 'POST'))
@login_required_role(1)
def add_user():
    if request.method == 'POST':
        finder_name = request.form['finder_name']
        phone = request.form['phone']
        finder_location = request.form['finder_location']
        email = request.form['email']
        password = request.form['password']
        role_id = request.form['role_id']

        db = get_db()
        error = None

        if not finder_name:
            error = 'Name is required.'
        elif not phone:
            error = 'Phone is required.'
        elif not finder_location:
            error = 'Location is required.'
        elif not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        elif not role_id:
            error = 'Role is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (finder_name, phone, finder_location, email, password, role_id) VALUES (?, ?, ?, ?, ?, ?)",
                    (finder_name, phone, finder_location, email, generate_password_hash(password), role_id),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {email} is already registered."
            else:
                return redirect(url_for("admin.users"))

        flash(error)

    return render_template('admin/add_user.html')


@bp.route('/edit_user/<int:user_id>', methods=('GET', 'POST'))
@login_required_role(1)
def edit_user(user_id):
    db = get_db()
    user = db.execute(
        'SELECT * FROM user WHERE id = ?', (user_id,)
    ).fetchone()

    if request.method == 'POST':
        finder_name = request.form['finder_name']
        phone = request.form['phone']
        finder_location = request.form['finder_location']
        email = request.form['email']
        password = request.form['password']
        role_id = request.form['role_id']

        error = None

        if not finder_name:
            error = 'Name is required.'
        elif not phone:
            error = 'Phone is required.'
        elif not finder_location:
            error = 'Location is required.'
        elif not email:
            error = 'Email is required.'
        elif not role_id:
            error = 'Role is required.'

        if error is None:
            if password:
                db.execute(
                    "UPDATE user SET finder_name = ?, phone = ?, finder_location = ?, email = ?, password = ?, role_id = ? WHERE id = ?",
                    (finder_name, phone, finder_location, email, generate_password_hash(password), role_id, user_id),
                )
            else:
                db.execute(
                    "UPDATE user SET finder_name = ?, phone = ?, finder_location = ?, email = ?, role_id = ? WHERE id = ?",
                    (finder_name, phone, finder_location, email, role_id, user_id),
                )

            db.commit()
            return redirect(url_for('admin.users'))

        flash(error)

    return render_template('admin/edit_user.html', user=user)


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        db = get_db()
        g.user = db.execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/delete_user/<int:user_id>', methods=('POST',))
@login_required_role(1)
def delete_user(user_id):
    db = get_db()
    db.execute('DELETE FROM user WHERE id = ?', (user_id,))
    db.commit()
    return redirect(url_for('admin.users'))


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@bp.route('/unauthorized')
def unauthorized():
    return render_template('auth/unauthorized.html')
