from datetime import date, timedelta
from sqlalchemy import func
from flask import Blueprint, render_template
from models.models import db, Supply, Supplier, InventoryBatch, PurchaseOrder, SupplyRequest, SupplyRequestItem, Department
from routes.auth import login_required

analytics_bp=Blueprint('analytics',__name__,url_prefix='/analytics')
@analytics_bp.route('/')
@login_required
def index():
    supplies=Supply.query.all(); total_inventory=sum(s.current_stock for s in supplies); avg_stock=(total_inventory/len(supplies)) if supplies else 0
    low=sum(1 for s in supplies if s.current_stock<=s.minimum_stock); low_pct=(low/len(supplies)*100) if supplies else 0
    today=date.today(); near=today+timedelta(days=30)
    expired_qty=db.session.query(func.coalesce(func.sum(InventoryBatch.quantity),0)).filter(InventoryBatch.expiry_date<today).scalar()
    near_qty=db.session.query(func.coalesce(func.sum(InventoryBatch.quantity),0)).filter(InventoryBatch.expiry_date>=today,InventoryBatch.expiry_date<=near).scalar()
    total_purchase=db.session.query(func.coalesce(func.sum(PurchaseOrder.total_amount),0)).filter(PurchaseOrder.status!='Cancelled').scalar()
    po_count=PurchaseOrder.query.filter(PurchaseOrder.status!='Cancelled').count(); avg_po=(total_purchase/po_count) if po_count else 0
    suppliers=db.session.query(Supplier.name,func.count(PurchaseOrder.id),func.coalesce(func.sum(PurchaseOrder.total_amount),0)).outerjoin(PurchaseOrder).group_by(Supplier.id).order_by(func.sum(PurchaseOrder.total_amount).desc()).all()
    total_issued=db.session.query(func.coalesce(func.sum(SupplyRequestItem.quantity_issued),0)).scalar()
    top_consumed=db.session.query(Supply.name,func.coalesce(func.sum(SupplyRequestItem.quantity_issued),0)).join(SupplyRequestItem,Supply.id==SupplyRequestItem.supply_id).group_by(Supply.id).order_by(func.sum(SupplyRequestItem.quantity_issued).desc()).all()
    dept=db.session.query(Department.name,func.coalesce(func.sum(SupplyRequestItem.quantity_issued),0)).join(SupplyRequest,Department.id==SupplyRequest.department_id).join(SupplyRequestItem,SupplyRequest.id==SupplyRequestItem.request_id).group_by(Department.id).order_by(func.sum(SupplyRequestItem.quantity_issued).desc()).all()
    monthly=db.session.query(func.strftime('%Y-%m',PurchaseOrder.order_date),func.sum(PurchaseOrder.total_amount)).filter(PurchaseOrder.status!='Cancelled').group_by(func.strftime('%Y-%m',PurchaseOrder.order_date)).order_by(func.strftime('%Y-%m',PurchaseOrder.order_date)).all()
    cat=db.session.query(Supply.category,func.coalesce(func.sum(InventoryBatch.quantity),0)).join(InventoryBatch,Supply.id==InventoryBatch.supply_id).group_by(Supply.category).all()
    return render_template('analytics/index.html',total_inventory=total_inventory,avg_stock=avg_stock,low_pct=low_pct,expired_qty=expired_qty,near_qty=near_qty,total_purchase=total_purchase,po_count=po_count,avg_po=avg_po,suppliers=suppliers,total_issued=total_issued,top_consumed=top_consumed,dept=dept,monthly=monthly,cat=cat,low_supplies=[s for s in supplies if s.current_stock<=s.minimum_stock])
