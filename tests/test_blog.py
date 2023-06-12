import os
import tempfile
import pytest
from flask import g, session
from missing.db import get_db
from missing import create_app


@pytest.fixture
def app():
    # Create a temporary file to isolate the database
    db_fd, db_path = tempfile.mkstemp()

    # Create a new Flask app with test configuration
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })

    # Create the database schema
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql') as f:
            db.executescript(f.read().decode('utf8'))
        db.commit()

    yield app

    # Close the database and remove the temporary file
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    # Create a test client using the Flask app
    return app.test_client()


@pytest.fixture
def runner(app):
    # Create a test runner using the Flask app
    return app.test_cli_runner()


def test_index(client, app):
    # Test that the index page is accessible
    response = client.get('/')
    assert response.status_code == 200


def test_create(client, auth, app):
    # Test that the create page requires authentication
    response = client.get('/create')
    assert response.status_code == 302
    assert response.headers['Location'] == 'http://localhost/auth/login'

    # Test that the create page is accessible when logged in
    auth.login()
    response = client.get('/create')
    assert response.status_code == 200

    # Test valid post creation
    with app.app_context():
        db = get_db()
        user = db.execute('SELECT * FROM user WHERE email = ?', ('test',)).fetchone()
        assert user is not None

        response = client.post('/create', data={
            'missed_name': 'Test User',
            'since': '2022-06-12',
            'missing_from': 'Test Location',
            'gender': 'male',
            'age': '25',
            'call_on': '1234567890',
            'additional_info': 'Test information',
            'status': 'active',
            'photo_url': (open(os.path.join(os.getcwd(), 'tests', 'test_files', 'test_image.jpg'), 'rb'), 'test_image.jpg')
        }, content_type='multipart/form-data')
        assert response.status_code == 302
        assert response.headers['Location'] == 'http://localhost/'

        post = db.execute('SELECT * FROM post WHERE missed_name = ?', ('Test User',)).fetchone()
        assert post is not None
        assert post['missed_name'] == 'Test User'
        assert post['since'] == '2022-06-12'
        assert post['missing_from'] == 'Test Location'
        assert post['gender'] == 'male'
        assert post['age'] == '25'
        assert post['call_on'] == '1234567890'
        assert post['additional_info'] == 'Test information'
        assert post['status'] == 'active'
        assert post['finder_id'] == user['id']
        assert post['photo_url'] is not None


def test_update(client, auth, app):
    # Test that the update page requires authentication
    response = client.get('/1/update')
    assert response.status_code == 302
    assert response.headers['Location'] == 'http://localhost/auth/login'

    # Test that the update page is accessible when logged in
    auth.login()
    response = client.get('/1/update')
    assert response.status_code == 200

    # Test valid post update
    with app.app_context():
        db = get_db()
        user = db.execute('SELECT * FROM user WHERE email = ?', ('test',)).fetchone()
        assert user is not None

        response = client.post('/1/update', data={
            'missed_name': 'Updated User',
            'since': '2022-06-12',
            'missing_from': 'Updated Location',
            'gender': 'female',
            'age': '30',
            'call_on': '1234567890',
            'additional_info': 'Updated information',
            'status': 'resolved'
        })
        assert response.status_code == 302
        assert response.headers['Location'] == 'http://localhost/'

        post = db.execute('SELECT * FROM post WHERE id = ?', (1,)).fetchone()
        assert post is not None
        assert post['missed_name'] == 'Updated User'
        assert post['since'] == '2022-06-12'
        assert post['missing_from'] == 'Updated Location'
        assert post['gender'] == 'female'
        assert post['age'] == '30'
        assert post['call_on'] == '1234567890'
        assert post['additional_info'] == 'Updated information'
        assert post['status'] == 'resolved'
        assert post['finder_id'] == user['id']
        assert post['photo_url'] is None
