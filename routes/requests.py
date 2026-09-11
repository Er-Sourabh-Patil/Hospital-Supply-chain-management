from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.models import db, SupplyRequest, SupplyRequestItem, Department, Supply, InventoryBatch
from routes.auth import login_required, role_required

requests_bp=Blueprint('requests',__name__,url_prefix='/requests')

@requests_bp.route('/')
@login_required
def index():
    q=SupplyRequest.query
    if request.args.get('department'): q=q.filter_by(department_id=int(request.args['department']))
    if request.args.get('status'): q=q.filter_by(status=request.args['status'])
    if request.args.get('priority'): q=q.filter_by(priority=request.args['priority'])
    return render_template('requests/list.html',requests=q.order_by(SupplyRequest.request_date.desc()).all(),departments=Department.query.order_by(Department.name).all())

@requests_bp.route('/add',methods=['GET','POST'])
@role_required('Admin','Inventory Manager','Department Staff')
def add():
    departments=Department.query.order_by(Department.name).all(); supplies=Supply.query.order_by(Supply.name).all(); user=session['user']
    if request.method=='POST':
        try: department_id=int(request.form['department_id'])
        except (ValueError,KeyError): flash('Select a department.','danger'); return render_template('requests/form.html',departments=departments,supplies=supplies)
        selected=[]
        for s in supplies:
            val=request.form.get(f'qty_{s.id}','').strip()
            if val:
                try:q=int(val)
                except ValueError:q=0
                if q<=0: flash(f'Invalid quantity for {s.name}.','danger'); return render_template('requests/form.html',departments=departments,supplies=supplies)
                selected.append((s.id,q))
        if not selected: flash('Add at least one supply.','danger'); return render_template('requests/form.html',departments=departments,supplies=supplies)
        r=SupplyRequest(department_id=department_id,requested_by=user['id'],request_date=date.today(),priority=request.form.get('priority','Normal'),status='Pending'); db.session.add(r); db.session.flush()
        for sid,q in selected: db.session.add(SupplyRequestItem(request_id=r.id,supply_id=sid,quantity_requested=q))
        db.session.commit(); flash('Supply request created.','success'); return redirect(url_for('requests.detail',id=r.id))
    return render_template('requests/form.html',departments=departments,supplies=supplies)

@requests_bp.route('/<int:id>')
@login_required
def detail(id): return render_template('requests/detail.html',request_obj=SupplyRequest.query.get_or_404(id))

@requests_bp.route('/<int:id>/approve',methods=['POST'])
@role_required('Admin','Inventory Manager')
def approve(id):
    r=SupplyRequest.query.get_or_404(id)
    if r.status!='Pending': flash('Request is not pending.','danger'); return redirect(url_for('requests.detail',id=id))
    for item in r.items: item.quantity_approved=min(item.quantity_requested,item.supply.current_stock)
    r.status='Approved'; db.session.commit(); flash('Request approved. Quantities were limited to available stock.','success'); return redirect(url_for('requests.detail',id=id))

@requests_bp.route('/<int:id>/reject',methods=['POST'])
@role_required('Admin','Inventory Manager')
def reject(id):
    r=SupplyRequest.query.get_or_404(id); r.status='Rejected'; db.session.commit(); flash('Request rejected.','success'); return redirect(url_for('requests.detail',id=id))

@requests_bp.route('/<int:id>/issue',methods=['POST'])
@role_required('Admin','Inventory Manager')
def issue(id):
    r=SupplyRequest.query.get_or_404(id)
    if r.status!='Approved': flash('Only approved requests can be issued.','danger'); return redirect(url_for('requests.detail',id=id))
    for item in r.items:
        qty=int(item.quantity_approved or 0)
        if qty<=0: continue
        if item.supply.current_stock<qty: flash(f'Not enough stock for {item.supply.name}.','danger'); return redirect(url_for('requests.detail',id=id))
        remaining=qty
        batches=InventoryBatch.query.filter_by(supply_id=item.supply_id).filter(InventoryBatch.quantity>0).order_by(InventoryBatch.expiry_date).all()
        for batch in batches:
            take=min(batch.quantity,remaining); batch.quantity-=take; remaining-=take
            if remaining==0: break
        if remaining: db.session.rollback(); flash('Stock changed while issuing. Try again.','danger'); return redirect(url_for('requests.detail',id=id))
        item.quantity_issued=qty
    r.status='Issued'; db.session.commit(); flash('Stock issued and inventory decreased.','success'); return redirect(url_for('requests.detail',id=id))
