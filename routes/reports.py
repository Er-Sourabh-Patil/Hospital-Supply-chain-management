from datetime import date, timedelta
from flask import Blueprint, render_template, request
from models.models import Supply, Supplier, InventoryBatch, PurchaseOrder, Department, SupplyRequest, SupplyRequestItem
from routes.auth import login_required

reports_bp=Blueprint('reports',__name__,url_prefix='/reports')
@reports_bp.route('/')
@login_required
def index():
    category=request.args.get('category',''); supplier=request.args.get('supplier',''); department=request.args.get('department','')
    inv=InventoryBatch.query.join(Supply)
    if category: inv=inv.filter(Supply.category==category)
    if supplier: inv=inv.filter(InventoryBatch.supplier_id==int(supplier))
    purchases=PurchaseOrder.query
    if supplier: purchases=purchases.filter(PurchaseOrder.supplier_id==int(supplier))
    req=SupplyRequest.query
    if department: req=req.filter(SupplyRequest.department_id==int(department))
    return render_template('reports/index.html',batches=inv.order_by(InventoryBatch.expiry_date).all(),orders=purchases.order_by(PurchaseOrder.order_date.desc()).all(),requests=req.order_by(SupplyRequest.request_date.desc()).all(),categories=Supply.query.with_entities(Supply.category).distinct().all(),suppliers=Supplier.query.order_by(Supplier.name).all(),departments=Department.query.order_by(Department.name).all(),category=category,supplier=supplier,department=department,today=date.today(),near=date.today()+timedelta(days=30))
