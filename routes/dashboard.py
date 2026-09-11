from datetime import date, timedelta
from sqlalchemy import func
from flask import Blueprint, render_template, jsonify
from models.models import db, Supply, Supplier, InventoryBatch, PurchaseOrder, SupplyRequest, SupplyRequestItem, Department
from routes.auth import login_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    today = date.today()
    near = today + timedelta(days=30)
    supplies = Supply.query.all()
    low_stock = sum(1 for s in supplies if s.current_stock <= s.minimum_stock)
    near_expiry = InventoryBatch.query.filter(InventoryBatch.expiry_date >= today, InventoryBatch.expiry_date <= near).count()
    expired = InventoryBatch.query.filter(InventoryBatch.expiry_date < today).count()
    total_inventory = db.session.query(func.coalesce(func.sum(InventoryBatch.quantity), 0)).scalar()
    total_purchase = db.session.query(func.coalesce(func.sum(PurchaseOrder.total_amount), 0)).filter(PurchaseOrder.status != 'Cancelled').scalar()

    monthly_rows = db.session.query(func.strftime('%Y-%m', PurchaseOrder.order_date), func.sum(PurchaseOrder.total_amount)).filter(PurchaseOrder.status != 'Cancelled').group_by(func.strftime('%Y-%m', PurchaseOrder.order_date)).order_by(func.strftime('%Y-%m', PurchaseOrder.order_date)).all()
    dept_rows = db.session.query(Department.name, func.coalesce(func.sum(SupplyRequestItem.quantity_issued), 0)).join(SupplyRequest, SupplyRequest.department_id == Department.id).join(SupplyRequestItem, SupplyRequestItem.request_id == SupplyRequest.id).group_by(Department.id).order_by(func.sum(SupplyRequestItem.quantity_issued).desc()).all()
    top_rows = db.session.query(Supply.name, func.coalesce(func.sum(SupplyRequestItem.quantity_issued), 0)).join(SupplyRequestItem, SupplyRequestItem.supply_id == Supply.id).group_by(Supply.id).order_by(func.sum(SupplyRequestItem.quantity_issued).desc()).limit(10).all()
    cat_rows = db.session.query(Supply.category, func.coalesce(func.sum(InventoryBatch.quantity), 0)).join(InventoryBatch, InventoryBatch.supply_id == Supply.id).group_by(Supply.category).all()

    return render_template('dashboard.html', total_supplies=len(supplies), total_inventory=total_inventory,
        low_stock=low_stock, near_expiry=near_expiry, expired=expired, total_suppliers=Supplier.query.count(),
        pending_requests=SupplyRequest.query.filter_by(status='Pending').count(), total_purchase=total_purchase,
        monthly_labels=[r[0] for r in monthly_rows], monthly_values=[float(r[1] or 0) for r in monthly_rows],
        dept_labels=[r[0] for r in dept_rows], dept_values=[int(r[1] or 0) for r in dept_rows],
        top_labels=[r[0] for r in top_rows], top_values=[int(r[1] or 0) for r in top_rows],
        cat_labels=[r[0] for r in cat_rows], cat_values=[int(r[1] or 0) for r in cat_rows])
