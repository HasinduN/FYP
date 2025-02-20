from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, scoped_session, relationship
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Database connection URL
DATABASE_URL = "postgresql://postgres:hasindu123@localhost/pos_system"

engine = create_engine(
    DATABASE_URL,
    pool_size=20,  # Increase from default 5 to 20
    max_overflow=40,  # Allow up to 40 extra connections
    pool_timeout=30,  # Wait for 30 seconds before timeout
    pool_recycle=1800  # Recycle connections every 30 minutes
)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)
session = scoped_session(SessionLocal)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # manager or cashier

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class MenuItem(Base):
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    description = Column(String, nullable=True)

    recipe = relationship("Recipe", back_populates="menu_item", cascade="all, delete-orphan")

class InventoryItem(Base):
    __tablename__ = "inventory_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    quantity = Column(Integer, nullable=False, default=0)
    unit = Column(String, nullable=False, default="nos")

    # Relationship to Inventory Log
    inventory_logs = relationship("InventoryLog", back_populates="inventory_item", cascade="all, delete-orphan")

class InventoryLog(Base):
    __tablename__ = "inventory_log"
    id = Column(Integer, primary_key=True, autoincrement=True)
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    added_quantity = Column(Integer, nullable=False)
    unit = Column(String, nullable=False, default="nos")
    added_date = Column(DateTime, default=datetime.utcnow)

    # Relationship to InventoryItem
    inventory_item = relationship("InventoryItem", back_populates="inventory_logs")

class Recipe(Base):
    __tablename__ = "recipes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    ingredient_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    quantity_needed = Column(Float, nullable=False)
    unit = Column(String, nullable=False)

    menu_item = relationship("MenuItem", back_populates="recipe")
    ingredient = relationship("InventoryItem")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)  # Takeaway or Dine-In
    table_number = Column(Integer, nullable=True)  # Table number for Dine-In orders
    total_price = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(Boolean, default=False)
    #payment_method = Column(String, nullable=False)
    kot_printed = Column(Boolean, default=False)
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "table_number": self.table_number if self.table_number else "N/A",
            "total_price": self.total_price,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "Completed" if self.status else "Ongoing"
        }

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    order = relationship("Order", back_populates="order_items")
    menu_item = relationship("MenuItem")

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")