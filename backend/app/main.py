from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routes import router
from . import models

# Создаём таблицы
Base.metadata.create_all(bind=engine)

# Функция для начального заполнения БД (seed)
def seed_db():
    from sqlalchemy.orm import Session
    from .database import SessionLocal
    db = SessionLocal()
    if db.query(models.Product).count() == 0:
        # Добавляем тестовые данные
        product1 = models.Product(name="Ноутбук", quantity=10, price=50000, min_quantity=3)
        product2 = models.Product(name="Мышь", quantity=25, price=800, min_quantity=5)
        supplier1 = models.Supplier(name="ООО 'Компьютеры'", contact="info@comp.ru")
        supplier2 = models.Supplier(name="ИП Иванов", contact="+7 123 456-78-90")
        db.add_all([product1, product2, supplier1, supplier2])
        db.commit()
        supply = models.Supply(product_id=1, supplier_id=1, quantity=10, price_per_unit=48000)
        db.add(supply)
        db.commit()
    db.close()

app = FastAPI(title="Warehouse API")

# Настройка CORS
origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://localhost:8080",
    "http://frontend:80",
    "null"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.on_event("startup")
def startup():
    seed_db()