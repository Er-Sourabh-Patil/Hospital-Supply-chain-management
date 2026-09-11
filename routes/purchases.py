from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.models import db, Supplier, Supply, PurchaseOrder, PurchaseOrderItem, InventoryBatch
from routes.auth import login_required, role_required

purchases_bp=Blueprint('purchases',__name__,url_prefix='/purchases')

@purchases_bp.route('/')
@login_required
def index():
    query=PurchaseOrder.query
    if request.args.get('supplier'): query=query.filter_by(supplier_id=int(request.args['supplier']))
    if request.args.get('status'): query=query.filter_by(status=request.args['status'])
    if request.args.get('date'): query=query.filter_by(order_date=date.fromisoformat(request.args['date']))
    return render_template('purchases/list.html',orders=query.order_by(PurchaseOrder.order_date.desc()).all(),suppliers=Supplier.query.order_by(Supplier.name).all())

@purchases_bp.route('/add',methods=['GET','POST'])
@role_required('Admin','Inventory Manager')
def add():
    suppliers=Supplier.query.filter_by(status='Active').order_by(Supplier.name).all(); supplies=Supply.query.order_by(Supply.name).all()
    if request.method=='POST':
        try: supplier_id=int(request.form['supplier_id']); order_date=date.fromisoformat(request.form['order_date']); expected=date.fromisoformat(request.form['expected_date']) if request.form.get('expected_date') else None
        except (ValueError,KeyError): flash('Invalid order details.', 'danger'); return render_template('purchases/form.html',suppliers=suppliers,supplies=supplies)
        selected=[]; total=0
        for s in supplies:
            qty=request.form.get(f'qty_{s.id}','').strip(); price=request.form.get(f'price_{s.id}','').strip()
            if qty:
                try: q=int(qty); p=float(price)
                except ValueError: q=-1;p=-1
                if q<=0 or p<0: flash(f'Invalid quantity/price for {s.name}.','danger'); return render_template('purchases/form.html',suppliers=suppliers,supplies=supplies)
                subtotal=q*p; selected.append((s.id,q,p,subtotal)); total+=subtotal
        if not selected: flash('Add at least one supply item.','danger'); return render_template('purchases/form.html',suppliers=suppliers,supplies=supplies)
        po=PurchaseOrder(supplier_id=supplier_id,order_date=order_date,expected_date=expected,status='Pending',total_amount=total,created_by=session_user_id())
        db.session.add(po); db.session.flush()
        for sid,q,p,sub in selected: db.session.add(PurchaseOrderItem(purchase_order_id=po.id,supply_id=sid,quantity=q,unit_price=p,subtotal=sub))
        db.session.commit(); flash('Purchase order created.','success'); return redirect(url_for('purchases.detail',id=po.id))
    return render_template('purchases/form.html',suppliers=suppliers,supplies=supplies)

def session_user_id():
    from flask import session
    return session.get('user',{}).get('id')

@purchases_bp.route('/<int:id>')
@login_required
def detail(id): return render_template('purchases/detail.html',order=PurchaseOrder.query.get_or_404(id))

@purchases_bp.route('/<int:id>/approve',methods=['POST'])
@role_required('Admin','Inventory Manager')
def approve(id):
    po=PurchaseOrder.query.get_or_404(id)
    if po.status=='Pending': po.status='Approved'; db.session.commit(); flash('Order approved.','success')
    return redirect(url_for('purchases.detail',id=id))

@purchases_bp.route('/<int:id>/cancel',methods=['POST'])
@role_required('Admin','Inventory Manager')
def cancel(id):
    po=PurchaseOrder.query.get_or_404(id)
    if po.status in ('Pending','Approved'): po.status='Cancelled'; db.session.commit(); flash('Order cancelled.','success')
    return redirect(url_for('purchases.detail',id=id))

@purchases_bp.route('/<int:id>/receive',methods=['GET','POST'])
@role_required('Admin','Inventory Manager')
def receive(id):
    po=PurchaseOrder.query.get_or_404(id)
    if po.status not in ('Approved','Pending'): flash('Only pending/approved orders can be received.','danger'); return redirect(url_for('purchases.detail',id=id))
    if request.method=='POST':
        try:
            for item in po.items:
                batch_no=request.form.get(f'batch_{item.id}','').strip(); qty=int(request.form.get(f'qty_{item.id}',item.quantity)); expiry=date.fromisoformat(request.form[f'expiry_{item.id}'])
                if not batch_no or qty<=0: raise ValueError
                if InventoryBatch.query.filter_by(batch_number=batch_no).first(): flash(f'Batch {batch_no} already exists.','danger'); return render_template('purchases/receive.html',order=po)
                db.session.add(InventoryBatch(supply_id=item.supply_id,supplier_id=po.supplier_id,batch_number=batch_no,quantity=qty,expiry_date=expiry,received_date=date.today(),unit_price=item.unit_price))
            po.status='Received'; db.session.commit(); flash('Order received and inventory updated.','success'); return redirect(url_for('purchases.detail',id=id))
        except (ValueError,KeyError): db.session.rollback(); flash('Please enter valid batch, quantity and expiry values.','danger')
    return render_template('purchases/receive.html',order=po)
