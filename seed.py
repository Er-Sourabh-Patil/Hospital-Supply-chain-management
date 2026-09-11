from datetime import date, timedelta
import random
from app import app
from models.models import db, User, Supplier, Supply, InventoryBatch, Department, PurchaseOrder, PurchaseOrderItem, SupplyRequest, SupplyRequestItem

random.seed(7)
with app.app_context():
    db.drop_all(); db.create_all()
    users=[]
    for name,email,password,role in [('Admin','admin@example.com','admin123','Admin'),('Inventory Manager','manager@example.com','manager123','Inventory Manager'),('Department Staff','staff@example.com','staff123','Department Staff'),('Assistant Manager','assistant@example.com','assistant123','Inventory Manager'),('Ward Staff','ward@example.com','ward123','Department Staff')]:
        u=User(name=name,email=email,role=role); u.set_password(password); db.session.add(u); users.append(u)
    suppliers=[]
    for i in range(8):
        s=Supplier(name=f'Supplier {chr(65+i)} Medical Pvt Ltd',contact_person=f'Contact {i+1}',phone=f'98{random.randint(10000000,99999999)}',email=f'supplier{i+1}@example.com',address=f'Mumbai, Maharashtra',status='Active'); db.session.add(s); suppliers.append(s)
    names=[('Surgical Gloves','PPE','Box',50),('N95 Masks','PPE','Box',40),('Syringes','Surgical Supplies','Pack',60),('IV Sets','Surgical Supplies','Pack',40),('Paracetamol','Medicines','Strip',100),('Antibiotic Tablets','Medicines','Strip',80),('Bandages','Surgical Supplies','Pack',50),('IV Fluids','Medicines','Bottle',70),('Surgical Masks','PPE','Box',60),('Cotton Rolls','Laboratory Supplies','Pack',40),('Blood Collection Tubes','Laboratory Supplies','Box',50),('Insulin Vials','Medicines','Vial',40),('Face Shields','PPE','Piece',30),('Scalpels','Surgical Supplies','Box',25),('Alcohol Swabs','Cleaning Supplies','Box',70),('Disinfectant','Cleaning Supplies','Bottle',40),('Urine Containers','Laboratory Supplies','Pack',35),('Surgical Gowns','PPE','Pack',30),('Thermometers','Medical Equipment','Piece',15),('Pulse Oximeters','Medical Equipment','Piece',10)]
    supplies=[]
    for n,c,u,m in names: s=Supply(name=n,category=c,unit=u,minimum_stock=m,description=f'Healthcare supply: {n}'); db.session.add(s); supplies.append(s)
    depts=[]
    for n,l in [('Emergency','Ground Floor'),('ICU','First Floor'),('Pharmacy','Ground Floor'),('Laboratory','Second Floor'),('Operation Theatre','First Floor'),('General Ward','Second Floor')]: d=Department(name=n,location=l); db.session.add(d); depts.append(d)
    db.session.flush()
    for i in range(30):
        s=random.choice(supplies); supplier=random.choice(suppliers); received=date.today()-timedelta(days=random.randint(1,330)); expiry=date.today()+timedelta(days=random.randint(-40,500)); qty=random.randint(max(5,s.minimum_stock//2),250); price=round(random.uniform(5,500),2)
        db.session.add(InventoryBatch(supply_id=s.id,supplier_id=supplier.id,batch_number=f'BATCH-{1000+i}',quantity=qty,manufacturing_date=received-timedelta(days=random.randint(30,180)),expiry_date=expiry,received_date=received,unit_price=price))
    db.session.flush()
    for i in range(15):
        supplier=random.choice(suppliers); od=date.today()-timedelta(days=random.randint(0,300)); status=random.choice(['Pending','Approved','Received','Received','Cancelled']); po=PurchaseOrder(supplier_id=supplier.id,order_date=od,expected_date=od+timedelta(days=random.randint(5,20)),status=status,created_by=random.choice(users).id,total_amount=0); db.session.add(po); db.session.flush(); total=0
        for _ in range(random.randint(1,3)):
            s=random.choice(supplies); q=random.randint(5,100); p=round(random.uniform(5,500),2); sub=round(q*p,2); db.session.add(PurchaseOrderItem(purchase_order_id=po.id,supply_id=s.id,quantity=q,unit_price=p,subtotal=sub)); total+=sub
        po.total_amount=round(total,2)
    db.session.flush()
    for i in range(25):
        d=random.choice(depts); r=SupplyRequest(department_id=d.id,requested_by=random.choice(users).id,request_date=date.today()-timedelta(days=random.randint(0,180)),priority=random.choice(['Low','Normal','High','Urgent']),status=random.choice(['Pending','Approved','Rejected','Issued','Completed'])); db.session.add(r); db.session.flush()
        for _ in range(random.randint(1,3)):
            s=random.choice(supplies); requested=random.randint(1,30); issued=random.randint(0,requested) if r.status in ('Issued','Completed') else 0; approved=issued if issued else (random.randint(1,requested) if r.status=='Approved' else 0); db.session.add(SupplyRequestItem(request_id=r.id,supply_id=s.id,quantity_requested=requested,quantity_approved=approved,quantity_issued=issued))
    db.session.commit(); print('Database seeded successfully.')
