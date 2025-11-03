from pydantic import BaseModel, Field

class SweetBase(BaseModel):
    name: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)
    quantity: int = Field(..., ge=0)

class SweetCreate(SweetBase):
    pass

class SweetUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    price: float | None = Field(None, gt=0)
    quantity: int | None = Field(None, ge=0)

class Sweet(SweetBase):
    id: int

    class Config:
        from_attributes = True

class PurchaseRequest(BaseModel):
    quantity: int = Field(..., gt=0)

class RestockRequest(BaseModel):
    quantity: int = Field(..., gt=0)