from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.orm import scoped_session
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Database connection URL
DATABASE_URL = "postgresql://postgres:hasindu123@localhost/pos_system"

engine = create_engine(DATABASE_URL, echo=True)
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

class InventoryItem(Base):
    __tablename__ = "inventory_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    added_date = Column(DateTime, default=datetime.utcnow)

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