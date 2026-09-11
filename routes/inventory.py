from datetime import date, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.models import db, Supply, Supplier, InventoryBatch
from routes.auth import login_required, role_required

inventory_bp=Blueprint('inventory',__name__,url_prefix='/inventory')

@inventory_bp.route('/')
@login_required
def index():
    q=request.args.get('q','').strip(); category=request.args.get('category',''); status=request.args.get('status','')
    batches=InventoryBatch.query.join(Supply)
    if q: batches=batches.filter(Supply.name.ilike(f'%{q}%'))
    if category: batches=batches.filter(Supply.category==category)
    rows=batches.order_by(InventoryBatch.expiry_date).all()
    today=date.today(); near=today+timedelta(days=30)
    def batch_status(b):
        if b.expiry_date<today:return 'Expired'
        if b.expiry_date<=near:return 'Near Expiry'
        return 'Good'
    if status: rows=[b for b in rows if status==batch_status(b) or (status=='Low Stock' and b.supply.current_stock<=b.supply.minimum_stock)]
    return render_template('inventory/list.html', batches=rows, categories=db.session.query(Supply.category).distinct().order_by(Supply.category).all(), q=q, category=category, status=status, batch_status=batch_status)

@inventory_bp.route('/add',methods=['GET','POST'])
@role_required('Admin','Inventory Manager')
def add():
    supplies=Supply.query.order_by(Supply.name).all(); suppliers=Supplier.query.filter_by(status='Active').order_by(Supplier.name).all()
    if request.method=='POST':
        try: qty=int(request.form['quantity']); price=float(request.form['unit_price'])
        except (ValueError,KeyError): qty=-1; price=-1
        if qty<=0 or price<0 or not request.form.get('batch_number','').strip(): flash('Enter valid batch, quantity and price.', 'danger'); return render_template('inventory/form.html',supplies=supplies,suppliers=suppliers,batch=None)
        try:
            expiry=date.fromisoformat(request.form['expiry_date']); received=date.fromisoformat(request.form['received_date']); manuf=date.fromisoformat(request.form['manufacturing_date']) if request.form.get('manufacturing_date') else None
        except ValueError: flash('Invalid date.', 'danger'); return render_template('inventory/form.html',supplies=supplies,suppliers=suppliers,batch=None)
        if InventoryBatch.query.filter_by(batch_number=request.form['batch_number'].strip()).first(): flash('Batch number already exists.', 'danger'); return render_template('inventory/form.html',supplies=supplies,suppliers=suppliers,batch=None)
        b=InventoryBatch(supply_id=int(request.form['supply_id']),supplier_id=int(request.form['supplier_id']),batch_number=request.form['batch_number'].strip(),quantity=qty,manufacturing_date=manuf,expiry_date=expiry,received_date=received,unit_price=price)
        db.session.add(b); db.session.commit(); flash('Inventory batch added.', 'success'); return redirect(url_for('inventory.index'))
    return render_template('inventory/form.html',supplies=supplies,suppliers=suppliers,batch=None)

@inventory_bp.route('/edit/<int:id>',methods=['GET','POST'])
@role_required('Admin','Inventory Manager')
def edit(id):
    b=InventoryBatch.query.get_or_404(id); supplies=Supply.query.order_by(Supply.name).all(); suppliers=Supplier.query.filter_by(status='Active').order_by(Supplier.name).all()
    if request.method=='POST':
        try: qty=int(request.form['quantity']); price=float(request.form['unit_price']); expiry=date.fromisoformat(request.form['expiry_date']); received=date.fromisoformat(request.form['received_date']); manuf=date.fromisoformat(request.form['manufacturing_date']) if request.form.get('manufacturing_date') else None
        except (ValueError,KeyError): flash('Invalid values.', 'danger'); return render_template('inventory/form.html',supplies=supplies,suppliers=suppliers,batch=b)
        if qty<0 or price<0: flash('Quantity/price cannot be negative.', 'danger'); return render_template('inventory/form.html',supplies=supplies,suppliers=suppliers,batch=b)
        duplicate=InventoryBatch.query.filter_by(batch_number=request.form['batch_number'].strip()).first()
        if duplicate and duplicate.id!=b.id: flash('Batch number already exists.', 'danger'); return render_template('inventory/form.html',supplies=supplies,suppliers=suppliers,batch=b)
        b.supply_id=int(request.form['supply_id']); b.supplier_id=int(request.form['supplier_id']); b.batch_number=request.form['batch_number'].strip(); b.quantity=qty; b.unit_price=price; b.expiry_date=expiry; b.received_date=received; b.manufacturing_date=manuf; db.session.commit(); flash('Batch updated.', 'success'); return redirect(url_for('inventory.index'))
    return render_template('inventory/form.html',supplies=supplies,suppliers=suppliers,batch=b)

@inventory_bp.route('/delete/<int:id>',methods=['POST'])
@role_required('Admin','Inventory Manager')
def delete(id):
    b=InventoryBatch.query.get_or_404(id); db.session.delete(b); db.session.commit(); flash('Batch deleted.', 'success'); return redirect(url_for('inventory.index'))
