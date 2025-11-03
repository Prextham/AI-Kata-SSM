import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.models.sweet import Sweet
from app.core.security import get_password_hash

# Test database
TEST_DATABASE_URL = "sqlite:///./test_inventory.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def auth_token(client):
    """Create a user and return auth token"""
    client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123"
        }
    )
    response = client.post(
        "/api/auth/login",
        data={
            "username": "testuser",
            "password": "testpass123"
        }
    )
    return response.json()["access_token"]

@pytest.fixture
def admin_token(client):
    """Create an admin user and return auth token"""
    db = TestingSessionLocal()
    admin = User(
        email="admin@example.com",
        username="admin",
        hashed_password=get_password_hash("adminpass123"),
        is_admin=True
    )
    db.add(admin)
    db.commit()
    db.close()
    
    response = client.post(
        "/api/auth/login",
        data={
            "username": "admin",
            "password": "adminpass123"
        }
    )
    return response.json()["access_token"]

@pytest.fixture
def sample_sweet(client, auth_token):
    """Create a sample sweet and return its ID"""
    response = client.post(
        "/api/sweets",
        json={
            "name": "Test Sweet",
            "category": "Test",
            "price": 2.50,
            "quantity": 10
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    return response.json()["id"]

def test_purchase_sweet_success(client, auth_token, sample_sweet):
    """Test successfully purchasing a sweet"""
    response = client.post(
        f"/api/sweets/{sample_sweet}/purchase",
        json={"quantity": 3},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == 7  # 10 - 3
    assert data["message"] == "Purchase successful"

def test_purchase_sweet_insufficient_stock(client, auth_token, sample_sweet):
    """Test purchasing more than available stock"""
    response = client.post(
        f"/api/sweets/{sample_sweet}/purchase",
        json={"quantity": 15},  # More than the 10 available
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 400
    assert "Insufficient stock" in response.json()["detail"]

def test_purchase_nonexistent_sweet(client, auth_token):
    """Test purchasing a sweet that doesn't exist"""
    response = client.post(
        "/api/sweets/99999/purchase",
        json={"quantity": 1},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 404

def test_purchase_without_auth(client, sample_sweet):
    """Test purchasing without authentication fails"""
    response = client.post(
        f"/api/sweets/{sample_sweet}/purchase",
        json={"quantity": 1}
    )
    assert response.status_code == 401

def test_restock_sweet_as_admin(client, admin_token, auth_token):
    """Test restocking a sweet as admin"""
    # Create sweet first
    response = client.post(
        "/api/sweets",
        json={
            "name": "Low Stock Sweet",
            "category": "Test",
            "price": 1.99,
            "quantity": 5
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    sweet_id = response.json()["id"]
    
    # Restock as admin
    response = client.post(
        f"/api/sweets/{sweet_id}/restock",
        json={"quantity": 20},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == 25  # 5 + 20
    assert data["message"] == "Restock successful"

def test_restock_sweet_as_non_admin_fails(client, auth_token, sample_sweet):
    """Test restocking as non-admin fails"""
    response = client.post(
        f"/api/sweets/{sample_sweet}/restock",
        json={"quantity": 10},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 403

def test_restock_nonexistent_sweet(client, admin_token):
    """Test restocking a sweet that doesn't exist"""
    response = client.post(
        "/api/sweets/99999/restock",
        json={"quantity": 10},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404

def test_purchase_reduces_to_zero(client, auth_token, sample_sweet):
    """Test purchasing all available stock"""
    response = client.post(
        f"/api/sweets/{sample_sweet}/purchase",
        json={"quantity": 10},  # All of the available stock
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == 0

def test_purchase_from_zero_stock_fails(client, auth_token):
    """Test purchasing from a sweet with zero stock"""
    # Create sweet with zero stock
    create_response = client.post(
        "/api/sweets",
        json={
            "name": "Out of Stock",
            "category": "Test",
            "price": 1.00,
            "quantity": 0
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    sweet_id = create_response.json()["id"]
    
    # Try to purchase
    response = client.post(
        f"/api/sweets/{sweet_id}/purchase",
        json={"quantity": 1},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 400