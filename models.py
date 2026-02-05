import uuid
from sqlalchemy import Column, String, Boolean, Integer, DECIMAL, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

def generate_uuid():
    return str(uuid.uuid4())

# 1. users
class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    roles = relationship("UserRole", back_populates="user")
    orders = relationship("Order", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")

# 2. roles
class Role(Base):
    __tablename__ = "roles"
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, unique=True, index=True) 

    user_roles = relationship("UserRole", back_populates="role")

# 3. user_roles
class UserRole(Base):
    __tablename__ = "user_roles"
    user_id = Column(String, ForeignKey("users.id"), primary_key=True, index=True)
    role_id = Column(String, ForeignKey("roles.id"), primary_key=True, index=True)

    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="user_roles")

# 4. categories
class Category(Base):
    __tablename__ = "categories"
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, index=True)
    parent_id = Column(String, ForeignKey("categories.id"), nullable=True, index=True)

    products = relationship("Product", back_populates="category")
    children = relationship("Category")

# 5. products
class Product(Base):
    __tablename__ = "products"
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, index=True)
    description = Column(String)
    price = Column(DECIMAL(10, 2), nullable=False)
    stock = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    category_id = Column(String, ForeignKey("categories.id"), index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    category = relationship("Category", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")
    reviews = relationship("Review", back_populates="product")

# 6. orders
class Order(Base):
    __tablename__ = "orders"
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    status = Column(String, default="PENDING", index=True)
    total_price = Column(DECIMAL(12, 2), default=0)
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

# 7. order_items
class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(String, primary_key=True, default=generate_uuid)
    order_id = Column(String, ForeignKey("orders.id"), index=True)
    product_id = Column(String, ForeignKey("products.id"), index=True)
    quantity = Column(Integer, nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

# 8. reviews
class Review(Base):
    __tablename__ = "reviews"
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    product_id = Column(String, ForeignKey("products.id"), index=True)
    rating = Column(Integer)
    comment = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")

# 9. audit_logs
class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    action = Column(String)
    table_name = Column(String, index=True)
    record_id = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="audit_logs")