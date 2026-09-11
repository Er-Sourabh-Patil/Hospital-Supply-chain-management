from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.models import db, User

auth_bp = Blueprint('auth', __name__)

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth.login'))
        return view(*args, **kwargs)
    return wrapped

def role_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            user = session.get('user')
            if not user:
                return redirect(url_for('auth.login'))
            if user['role'] not in roles:
                flash('You are not authorized to access this page.', 'danger')
                return redirect(url_for('dashboard.index'))
            return view(*args, **kwargs)
        return wrapped
    return decorator

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user'] = {'id': user.id, 'name': user.name, 'email': user.email, 'role': user.role}
            return redirect(url_for('dashboard.index'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
