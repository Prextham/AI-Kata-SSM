from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class Sweet(Base):
    __tablename__ = "sweets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False, default=0)