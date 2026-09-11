from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.models import db, Supplier
from routes.auth import login_required, role_required

suppliers_bp = Blueprint('suppliers', __name__, url_prefix='/suppliers')

@suppliers_bp.route('/')
@login_required
def index():
    q = request.args.get('q', '').strip()
    suppliers = Supplier.query.filter(Supplier.name.ilike(f'%{q}%')).order_by(Supplier.name).all() if q else Supplier.query.order_by(Supplier.name).all()
    return render_template('suppliers/list.html', suppliers=suppliers, q=q)

@suppliers_bp.route('/add', methods=['GET','POST'])
@role_required('Admin','Inventory Manager')
def add():
    if request.method == 'POST':
        if not request.form.get('name','').strip(): flash('Supplier name is required.', 'danger'); return render_template('suppliers/form.html', supplier=None)
        s = Supplier(name=request.form['name'].strip(), contact_person=request.form.get('contact_person'), phone=request.form.get('phone'), email=request.form.get('email'), address=request.form.get('address'), status=request.form.get('status','Active'))
        db.session.add(s); db.session.commit(); flash('Supplier added.', 'success'); return redirect(url_for('suppliers.index'))
    return render_template('suppliers/form.html', supplier=None)

@suppliers_bp.route('/edit/<int:id>', methods=['GET','POST'])
@role_required('Admin','Inventory Manager')
def edit(id):
    s = Supplier.query.get_or_404(id)
    if request.method == 'POST':
        s.name=request.form['name'].strip(); s.contact_person=request.form.get('contact_person'); s.phone=request.form.get('phone'); s.email=request.form.get('email'); s.address=request.form.get('address'); s.status=request.form.get('status','Active')
        db.session.commit(); flash('Supplier updated.', 'success'); return redirect(url_for('suppliers.index'))
    return render_template('suppliers/form.html', supplier=s)

@suppliers_bp.route('/delete/<int:id>', methods=['POST'])
@role_required('Admin')
def delete(id):
    s = Supplier.query.get_or_404(id)
    if s.inventory_batches or s.purchase_orders: flash('Cannot delete a supplier with related records.', 'danger')
    else: db.session.delete(s); db.session.commit(); flash('Supplier deleted.', 'success')
    return redirect(url_for('suppliers.index'))
