from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.models import db, Supply
from routes.auth import login_required, role_required

supplies_bp = Blueprint('supplies', __name__, url_prefix='/supplies')

@supplies_bp.route('/')
@login_required
def index():
    q=request.args.get('q','').strip(); category=request.args.get('category','')
    query=Supply.query
    if q: query=query.filter(Supply.name.ilike(f'%{q}%'))
    if category: query=query.filter_by(category=category)
    return render_template('supplies/list.html', supplies=query.order_by(Supply.name).all(), categories=db.session.query(Supply.category).distinct().order_by(Supply.category).all(), q=q, category=category)

@supplies_bp.route('/add', methods=['GET','POST'])
@role_required('Admin','Inventory Manager')
def add():
    if request.method=='POST':
        try: minimum=int(request.form.get('minimum_stock',0));
        except ValueError: minimum=-1
        if not request.form.get('name','').strip() or minimum<0: flash('Enter a valid name and minimum stock.', 'danger'); return render_template('supplies/form.html', supply=None)
        s=Supply(name=request.form['name'].strip(), category=request.form['category'], unit=request.form['unit'].strip(), minimum_stock=minimum, description=request.form.get('description'))
        db.session.add(s); db.session.commit(); flash('Medical supply added.', 'success'); return redirect(url_for('supplies.index'))
    return render_template('supplies/form.html', supply=None)

@supplies_bp.route('/edit/<int:id>', methods=['GET','POST'])
@role_required('Admin','Inventory Manager')
def edit(id):
    s=Supply.query.get_or_404(id)
    if request.method=='POST':
        try: minimum=int(request.form.get('minimum_stock',0))
        except ValueError: minimum=-1
        if minimum<0: flash('Minimum stock must be zero or greater.', 'danger'); return render_template('supplies/form.html', supply=s)
        s.name=request.form['name'].strip(); s.category=request.form['category']; s.unit=request.form['unit'].strip(); s.minimum_stock=minimum; s.description=request.form.get('description'); db.session.commit(); flash('Supply updated.', 'success'); return redirect(url_for('supplies.index'))
    return render_template('supplies/form.html', supply=s)

@supplies_bp.route('/delete/<int:id>', methods=['POST'])
@role_required('Admin')
def delete(id):
    s=Supply.query.get_or_404(id)
    if s.purchase_items or s.request_items: flash('Cannot delete a supply used in transactions.', 'danger')
    else: db.session.delete(s); db.session.commit(); flash('Supply deleted.', 'success')
    return redirect(url_for('supplies.index'))
