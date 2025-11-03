from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.sweet import Sweet
from app.models.user import User
from app.schemas.sweet import (
    SweetCreate, 
    SweetUpdate, 
    Sweet as SweetSchema,
    PurchaseRequest,
    RestockRequest
)
from app.core.security import get_current_user, get_current_admin_user

router = APIRouter(prefix="/api/sweets", tags=["sweets"])

@router.post("", response_model=SweetSchema, status_code=status.HTTP_201_CREATED)
def create_sweet(
    sweet: SweetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new sweet (requires authentication)"""
    db_sweet = Sweet(
        name=sweet.name,
        category=sweet.category,
        price=sweet.price,
        quantity=sweet.quantity
    )
    db.add(db_sweet)
    db.commit()
    db.refresh(db_sweet)
    return db_sweet

@router.get("", response_model=List[SweetSchema])
def get_all_sweets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """Get all sweets (requires authentication)"""
    sweets = db.query(Sweet).offset(skip).limit(limit).all()
    return sweets

@router.get("/search", response_model=List[SweetSchema])
def search_sweets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    name: Optional[str] = Query(None, description="Search by sweet name"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price")
):
    """Search for sweets by name, category, or price range (requires authentication)"""
    query = db.query(Sweet)
    
    if name:
        query = query.filter(Sweet.name.ilike(f"%{name}%"))
    
    if category:
        query = query.filter(Sweet.category.ilike(f"%{category}%"))
    
    if min_price is not None:
        query = query.filter(Sweet.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Sweet.price <= max_price)
    
    sweets = query.all()
    return sweets

@router.put("/{sweet_id}", response_model=SweetSchema)
def update_sweet(
    sweet_id: int,
    sweet_update: SweetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a sweet's details (requires authentication)"""
    db_sweet = db.query(Sweet).filter(Sweet.id == sweet_id).first()
    
    if not db_sweet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sweet not found"
        )
    
    # Update only provided fields
    update_data = sweet_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_sweet, field, value)
    
    db.commit()
    db.refresh(db_sweet)
    return db_sweet

@router.delete("/{sweet_id}")
def delete_sweet(
    sweet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete a sweet (Admin only)"""
    db_sweet = db.query(Sweet).filter(Sweet.id == sweet_id).first()
    
    if not db_sweet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sweet not found"
        )
    
    db.delete(db_sweet)
    db.commit()
    return {"message": "Sweet deleted successfully"}

@router.post("/{sweet_id}/purchase")
def purchase_sweet(
    sweet_id: int,
    purchase: PurchaseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Purchase a sweet, decreasing its quantity (requires authentication)"""
    db_sweet = db.query(Sweet).filter(Sweet.id == sweet_id).first()
    
    if not db_sweet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sweet not found"
        )
    
    if db_sweet.quantity < purchase.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock. Only {db_sweet.quantity} available."
        )
    
    db_sweet.quantity -= purchase.quantity
    db.commit()
    db.refresh(db_sweet)
    
    return {
        "message": "Purchase successful",
        "sweet_id": db_sweet.id,
        "name": db_sweet.name,
        "quantity": db_sweet.quantity,
        "purchased": purchase.quantity
    }

@router.post("/{sweet_id}/restock")
def restock_sweet(
    sweet_id: int,
    restock: RestockRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Restock a sweet, increasing its quantity (Admin only)"""
    db_sweet = db.query(Sweet).filter(Sweet.id == sweet_id).first()
    
    if not db_sweet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sweet not found"
        )
    
    db_sweet.quantity += restock.quantity
    db.commit()
    db.refresh(db_sweet)
    
    return {
        "message": "Restock successful",
        "sweet_id": db_sweet.id,
        "name": db_sweet.name,
        "quantity": db_sweet.quantity,
        "restocked": restock.quantity
    }