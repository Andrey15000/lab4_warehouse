from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# --- Товары ---
class ProductBase(BaseModel):
    name: str
    quantity: int
    price: float
    min_quantity: int

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[float] = None
    min_quantity: Optional[int] = None

class ProductOut(ProductBase):
    id: int
    class Config:
        orm_mode = True

# --- Поставщики ---
class SupplierBase(BaseModel):
    name: str
    contact: Optional[str] = None

class SupplierCreate(SupplierBase):
    pass

class SupplierOut(SupplierBase):
    id: int
    class Config:
        orm_mode = True

# --- Поставки ---
class SupplyBase(BaseModel):
    product_id: int
    supplier_id: int
    quantity: int
    price_per_unit: float

class SupplyCreate(SupplyBase):
    pass

class SupplyOut(SupplyBase):
    id: int
    supply_date: datetime
    class Config:
        orm_mode = True

# --- Специальные ответы ---
class ProductStockOut(BaseModel):
    id: int
    name: str
    quantity: int
    price: float
    min_quantity: int

class SupplyHistoryOut(BaseModel):
    id: int
    product_name: str
    supplier_name: str
    quantity: int
    price_per_unit: float
    supply_date: datetime

class LowStockOut(BaseModel):
    id: int
    name: str
    quantity: int
    min_quantity: int