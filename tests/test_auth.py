import pytest
from flask import g, session
from missing.db import get_db


def test_register(client, app):
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register', data={'email': 'a', 'password': 'a'}
    )
    assert response.headers["Location"] == "/auth/login"

    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE email = 'a'",
        ).fetchone() is not None


@pytest.mark.parametrize(('email', 'password', 'message'), (
    ('', '', b'Email is required.'),
    ('a', '', b'Password is required.'),
    ('test', 'test', b'User test is already registered.'),
))
def test_register_validate_input(client, email, password, message):
    response = client.post(
        '/auth/register',
        data={'email': email, 'password': password}
    )
    assert message in response.data


def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers["Location"] == "/"
    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['email'] == 'test@example.com'


@pytest.mark.parametrize(('email', 'password', 'message'), (
    ('a', 'test', b'Incorrect email.'),
    ('test@example.com', 'a', b'Incorrect password.'),
))
def test_login_validate_input(auth, email, password, message):
    response = auth.login(email, password)
    assert message in response.data


def test_logout(client, auth):
    auth.login()
    with client:
        auth.logout()
        assert 'user_id' not in session


def test_add_user(client, auth):
    auth.login()
    assert client.get('/auth/add_user').status_code == 200
    response = client.post(
        '/auth/add_user',
        data={'finder_name': 'Test User', 'phone': '1234567890', 'finder_location': 'Test Location', 'email': 'testuser@example.com', 'password': 'password', 'role_id': '2'}
    )
    assert response.headers["Location"] == "/admin/users"


def test_edit_user(client, auth):
    auth.login()
    response = client.get('/auth/edit_user/2')
    assert response.status_code == 200
    assert b'Test User' in response.data
    assert b'testuser@example.com' in response.data
    response = client.post(
        '/auth/edit_user/2',
        data={'finder_name': 'New User', 'phone': '1234567890', 'finder_location': 'New Location', 'email': 'newuser@example.com', 'password': 'password', 'role_id': '2'}
    )
    assert response.headers["Location"] == "/admin/users"
    with client:
        response = client.get('/admin/users')
        assert b'New User' in response.data
        assert b'newuser@example.com' in response.data
        assert b'1234567890' in response.data
        assert b'New Location' in response.data


def test_delete_user(client, auth):
    auth.login()
    response = client.post('/auth/delete_user/2')
    assert response.headers["Location"] == "/admin/users"
    with client:
        response = client.get('/admin/users')
        assert b'New User' not in response.data
        assert b'newuser@example.com' not in response.data
        assert b'1234567890' not in response.data
        assert b'New Location' not in response.data
