import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.user import User
from app.models.sweet import Sweet

# Test database
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

# USER MODEL TESTS
def test_create_user(db_session):
    """Test creating a user"""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashedpassword123",
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.is_admin == False

# SWEET MODEL TESTS
def test_create_sweet(db_session):
    """Test creating a sweet"""
    sweet = Sweet(
        name="Chocolate Bar",
        category="Chocolate",
        price=2.50,
        quantity=100
    )
    db_session.add(sweet)
    db_session.commit()
    db_session.refresh(sweet)
    
    assert sweet.id is not None
    assert sweet.name == "Chocolate Bar"
    assert sweet.category == "Chocolate"
    assert sweet.price == 2.50
    assert sweet.quantity == 100

def test_sweet_purchase_decreases_quantity(db_session):
    """Test that purchasing decreases quantity"""
    sweet = Sweet(
        name="Gummy Bears",
        category="Gummy",
        price=1.99,
        quantity=50
    )
    db_session.add(sweet)
    db_session.commit()
    
    # Simulate purchase
    sweet.quantity -= 1
    db_session.commit()
    db_session.refresh(sweet)
    
    assert sweet.quantity == 49