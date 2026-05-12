from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    quantity = Column(Integer, default=0)
    price = Column(Float, nullable=False)
    min_quantity = Column(Integer, default=0)   # минимальный остаток для сигнала
    # Связь с поставками
    supplies = relationship("Supply", back_populates="product")

class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    contact = Column(String)   # телефон или email
    supplies = relationship("Supply", back_populates="supplier")

class Supply(Base):
    __tablename__ = "supplies"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    quantity = Column(Integer, nullable=False)
    price_per_unit = Column(Float, nullable=False)
    supply_date = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="supplies")
    supplier = relationship("Supplier", back_populates="supplies")