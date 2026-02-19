from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from trivia.dependencies import get_db
from trivia.models import Category
from trivia.schemas import CategoryCreate, CategoryRead


category_router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


# --- CREATE ---

@category_router.post("/", response_model=CategoryRead)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
):
    existing = (
        db.query(Category)
        .filter(Category.name == data.name)
        .first()
    )

    if existing:
        raise HTTPException(400, "Category already exists")

    obj = Category(**data.model_dump())

    db.add(obj)
    db.commit()
    db.refresh(obj)

    return obj


# --- LIST ---

@category_router.get("/", response_model=List[CategoryRead])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).order_by(Category.name).all()


# --- GET ONE ---

@category_router.get("/{category_id}", response_model=CategoryRead)
def get_category(category_id: int, db: Session = Depends(get_db)):
    obj = db.get(Category, category_id)

    if not obj:
        raise HTTPException(404, "Category not found")

    return obj


# --- UPDATE ---

@category_router.put("/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: int,
    data: CategoryCreate,
    db: Session = Depends(get_db),
):
    obj = db.get(Category, category_id)

    if not obj:
        raise HTTPException(404, "Category not found")

    existing = (
        db.query(Category)
        .filter(Category.name == data.name)
        .filter(Category.id != category_id)
        .first()
    )

    if existing:
        raise HTTPException(400, "Category already exists")

    obj.name = data.name

    db.commit()
    db.refresh(obj)

    return obj


# --- DELETE ---

@category_router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    obj = db.get(Category, category_id)

    if not obj:
        raise HTTPException(404, "Category not found")

    db.delete(obj)
    db.commit()
