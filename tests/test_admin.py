import pytest
from flask import g, session
from missing.db import get_db


def test_dashboard(client, auth):
    auth.login()
    response = client.get('/admin/dashboard')
    assert b'Total Reports' in response.data
    assert b'Active Reports' in response.data
    assert b'Resolved Reports' in response.data


def test_users(client, auth):
    auth.login()
    response = client.get('/admin/users')
    assert b'Test User' in response.data
    assert b'admin@example.com' in response.data
    assert b'User' in response.data


def test_reports(client, auth):
    auth.login()
    response = client.get('/admin/reports')
    assert b'Test Post' in response.data
    assert b'Test Content' in response.data
    assert b'active' in response.data
    assert b'Resolved Post' in response.data
    assert b'Resolved Content' in response.data
    assert b'resolved' in response.data
