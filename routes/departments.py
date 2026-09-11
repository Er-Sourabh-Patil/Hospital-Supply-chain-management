from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.models import db, Department
from routes.auth import login_required, role_required

departments_bp=Blueprint('departments',__name__,url_prefix='/departments')
@departments_bp.route('/')
@login_required
def index(): return render_template('departments/list.html',departments=Department.query.order_by(Department.name).all())
@departments_bp.route('/add',methods=['GET','POST'])
@role_required('Admin')
def add():
    if request.method=='POST':
        name=request.form.get('name','').strip()
        if not name: flash('Department name is required.','danger'); return render_template('departments/form.html',department=None)
        db.session.add(Department(name=name,location=request.form.get('location'))); db.session.commit(); flash('Department added.','success'); return redirect(url_for('departments.index'))
    return render_template('departments/form.html',department=None)
@departments_bp.route('/edit/<int:id>',methods=['GET','POST'])
@role_required('Admin')
def edit(id):
    d=Department.query.get_or_404(id)
    if request.method=='POST': d.name=request.form.get('name','').strip(); d.location=request.form.get('location'); db.session.commit(); flash('Department updated.','success'); return redirect(url_for('departments.index'))
    return render_template('departments/form.html',department=d)
@departments_bp.route('/delete/<int:id>',methods=['POST'])
@role_required('Admin')
def delete(id):
    d=Department.query.get_or_404(id)
    if d.requests: flash('Cannot delete a department with requests.','danger')
    else: db.session.delete(d); db.session.commit(); flash('Department deleted.','success')
    return redirect(url_for('departments.index'))
