from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import schemas, models
from .database import get_db

router = APIRouter(prefix="/api")

# ---------- Products ----------
@router.get("/products", response_model=List[schemas.ProductOut])
def get_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()

@router.get("/products/{product_id}", response_model=schemas.ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/products", response_model=schemas.ProductOut)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.put("/products/{product_id}", response_model=schemas.ProductOut)
def update_product(product_id: int, product: schemas.ProductUpdate, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in product.dict(exclude_unset=True).items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
    return {"message": "Product deleted"}

# ---------- Suppliers ----------
@router.get("/suppliers", response_model=List[schemas.SupplierOut])
def get_suppliers(db: Session = Depends(get_db)):
    return db.query(models.Supplier).all()

@router.post("/suppliers", response_model=schemas.SupplierOut)
def create_supplier(supplier: schemas.SupplierCreate, db: Session = Depends(get_db)):
    db_supplier = models.Supplier(**supplier.dict())
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier

@router.delete("/suppliers/{supplier_id}")
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)):
    supplier = db.query(models.Supplier).filter(models.Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    db.delete(supplier)
    db.commit()
    return {"message": "Supplier deleted"}

# ---------- Supplies ----------
@router.get("/supplies", response_model=List[schemas.SupplyOut])
def get_supplies(db: Session = Depends(get_db)):
    return db.query(models.Supply).all()

@router.post("/supplies", response_model=schemas.SupplyOut)
def create_supply(supply: schemas.SupplyCreate, db: Session = Depends(get_db)):
    # Проверяем существование товара и поставщика
    product = db.query(models.Product).filter(models.Product.id == supply.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    supplier = db.query(models.Supplier).filter(models.Supplier.id == supply.supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    # Увеличиваем количество товара на складе
    db_supply = models.Supply(**supply.dict())
    db.add(db_supply)
    product.quantity += supply.quantity
    db.commit()
    db.refresh(db_supply)
    return db_supply

# ---------- Специальные запросы ----------
# 1. Остатки на складе (список товаров с их количеством)
@router.get("/stock", response_model=List[schemas.ProductStockOut])
def get_stock(db: Session = Depends(get_db)):
    return db.query(models.Product).all()

# 2. История поставок (с названиями товаров и поставщиков)
@router.get("/supplies/history", response_model=List[schemas.SupplyHistoryOut])
def get_supply_history(db: Session = Depends(get_db)):
    results = db.query(
        models.Supply.id,
        models.Product.name.label("product_name"),
        models.Supplier.name.label("supplier_name"),
        models.Supply.quantity,
        models.Supply.price_per_unit,
        models.Supply.supply_date
    ).join(models.Product).join(models.Supplier).order_by(models.Supply.supply_date.desc()).all()
    return results

# 3. Товары ниже минимального количества
@router.get("/low-stock", response_model=List[schemas.LowStockOut])
def get_low_stock(db: Session = Depends(get_db)):
    return db.query(models.Product).filter(models.Product.quantity < models.Product.min_quantity).all()