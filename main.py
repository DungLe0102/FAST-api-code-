from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
import models, schemas, auth, database
from config import settings

# Tạo bảng DB tự động
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="My Store API")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- Dependencies ---
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = auth.jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None: raise HTTPException(status_code=401, detail="Invalid token")
    except auth.jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None: raise HTTPException(status_code=401, detail="User not found")
    return user

def log_action(db: Session, user_id: str, action: str, table: str, record_id: str):
    log = models.AuditLog(user_id=user_id, action=action, table_name=table, record_id=record_id)
    db.add(log)
    db.commit()

# --- Auth ---
@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email exists")
    new_user = models.User(
        email=user.email,
        hashed_password=auth.get_password_hash(user.password),
        full_name=user.full_name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/token", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Bad credentials")
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# --- Categories ---
@app.post("/categories/", response_model=schemas.CategoryResponse)
def create_category(cat: schemas.CategoryCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    new_cat = models.Category(**cat.dict())
    db.add(new_cat)
    db.commit()
    db.refresh(new_cat)
    log_action(db, current_user.id, "CREATE", "categories", new_cat.id)
    return new_cat

@app.get("/categories/", response_model=List[schemas.CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).all()

# --- Products ---
@app.post("/products/", response_model=schemas.ProductResponse)
def create_product(prod: schemas.ProductCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    new_prod = models.Product(**prod.dict())
    db.add(new_prod)
    db.commit()
    db.refresh(new_prod)
    log_action(db, current_user.id, "CREATE", "products", new_prod.id)
    return new_prod

@app.get("/products/", response_model=List[schemas.ProductResponse])
def get_products(db: Session = Depends(get_db)):
    return db.query(models.Product).filter(models.Product.is_active == True).all()

# --- Orders ---
@app.post("/orders/", response_model=schemas.OrderResponse)
def create_order(order_data: schemas.OrderCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    new_order = models.Order(user_id=current_user.id, status="PENDING", total_price=0)
    db.add(new_order)
    db.flush() 

    total = 0
    for item in order_data.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if not product:
            db.rollback()
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        
        order_item = models.OrderItem(
            order_id=new_order.id, product_id=product.id,
            quantity=item.quantity, price=product.price
        )
        total += product.price * item.quantity
        db.add(order_item)

    new_order.total_price = total
    db.commit()
    db.refresh(new_order)
    log_action(db, current_user.id, "CREATE", "orders", new_order.id)
    return new_order

@app.get("/my-orders/", response_model=List[schemas.OrderResponse])
def get_my_orders(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Order).filter(models.Order.user_id == current_user.id).all()

# --- Reviews ---
@app.post("/reviews/", response_model=schemas.ReviewResponse)
def create_review(review: schemas.ReviewCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    new_review = models.Review(**review.dict(), user_id=current_user.id)
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    log_action(db, current_user.id, "CREATE", "reviews", new_review.id)
    return new_review

# --- Audit Logs ---
@app.get("/audit-logs/", response_model=List[schemas.AuditLogResponse])
def view_audit_logs(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.AuditLog).all()

# --- Roles ---
@app.post("/roles/", response_model=schemas.RoleResponse)
def create_role(role: schemas.RoleCreate, db: Session = Depends(get_db)):
    new_role = models.Role(name=role.name)
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return new_role