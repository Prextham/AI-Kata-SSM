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
TEST_DATABASE_URL = "sqlite:///./test_sweets.db"
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
    # Register user
    client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123"
        }
    )
    # Login
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
    # Create admin user directly in database
    admin = User(
        email="admin@example.com",
        username="admin",
        hashed_password=get_password_hash("adminpass123"),
        is_admin=True
    )
    db.add(admin)
    db.commit()
    db.close()
    
    # Login
    response = client.post(
        "/api/auth/login",
        data={
            "username": "admin",
            "password": "adminpass123"
        }
    )
    return response.json()["access_token"]

def test_create_sweet_success(client, auth_token):
    """Test creating a sweet with authentication"""
    response = client.post(
        "/api/sweets",
        json={
            "name": "Chocolate Bar",
            "category": "Chocolate",
            "price": 2.50,
            "quantity": 100
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Chocolate Bar"
    assert data["category"] == "Chocolate"
    assert data["price"] == 2.50
    assert data["quantity"] == 100
    assert "id" in data

def test_create_sweet_unauthorized(client):
    """Test creating a sweet without authentication fails"""
    response = client.post(
        "/api/sweets",
        json={
            "name": "Chocolate Bar",
            "category": "Chocolate",
            "price": 2.50,
            "quantity": 100
        }
    )
    assert response.status_code == 401

def test_get_all_sweets(client, auth_token):
    """Test getting all sweets"""
    # Create some sweets first
    client.post(
        "/api/sweets",
        json={
            "name": "Chocolate Bar",
            "category": "Chocolate",
            "price": 2.50,
            "quantity": 100
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    client.post(
        "/api/sweets",
        json={
            "name": "Gummy Bears",
            "category": "Gummy",
            "price": 1.99,
            "quantity": 50
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    # Get all sweets
    response = client.get(
        "/api/sweets",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

def test_search_sweets_by_name(client, auth_token):
    """Test searching sweets by name"""
    # Create sweets
    client.post(
        "/api/sweets",
        json={
            "name": "Chocolate Bar",
            "category": "Chocolate",
            "price": 2.50,
            "quantity": 100
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    client.post(
        "/api/sweets",
        json={
            "name": "Dark Chocolate",
            "category": "Chocolate",
            "price": 3.00,
            "quantity": 50
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    # Search for chocolate
    response = client.get(
        "/api/sweets/search?name=chocolate",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

def test_search_sweets_by_category(client, auth_token):
    """Test searching sweets by category"""
    # Create sweets
    client.post(
        "/api/sweets",
        json={
            "name": "Chocolate Bar",
            "category": "Chocolate",
            "price": 2.50,
            "quantity": 100
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    client.post(
        "/api/sweets",
        json={
            "name": "Gummy Bears",
            "category": "Gummy",
            "price": 1.99,
            "quantity": 50
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    # Search by category
    response = client.get(
        "/api/sweets/search?category=Gummy",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["category"] == "Gummy"

def test_search_sweets_by_price_range(client, auth_token):
    """Test searching sweets by price range"""
    # Create sweets with different prices
    client.post(
        "/api/sweets",
        json={
            "name": "Cheap Candy",
            "category": "Candy",
            "price": 0.99,
            "quantity": 100
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    client.post(
        "/api/sweets",
        json={
            "name": "Premium Chocolate",
            "category": "Chocolate",
            "price": 5.99,
            "quantity": 50
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    # Search by price range
    response = client.get(
        "/api/sweets/search?min_price=2.00&max_price=10.00",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Premium Chocolate"

def test_update_sweet_success(client, auth_token):
    """Test updating a sweet"""
    # Create a sweet
    create_response = client.post(
        "/api/sweets",
        json={
            "name": "Chocolate Bar",
            "category": "Chocolate",
            "price": 2.50,
            "quantity": 100
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    sweet_id = create_response.json()["id"]
    
    # Update the sweet
    response = client.put(
        f"/api/sweets/{sweet_id}",
        json={
            "name": "Dark Chocolate Bar",
            "price": 3.00
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Dark Chocolate Bar"
    assert data["price"] == 3.00
    assert data["category"] == "Chocolate"  # Should remain unchanged

def test_update_nonexistent_sweet(client, auth_token):
    """Test updating a sweet that doesn't exist"""
    response = client.put(
        "/api/sweets/99999",
        json={
            "name": "New Name"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 404

def test_delete_sweet_as_admin(client, admin_token):
    """Test deleting a sweet as admin"""
    # Create a sweet first (need a regular user token for this)
    db = TestingSessionLocal()
    sweet = Sweet(
        name="To Delete",
        category="Test",
        price=1.00,
        quantity=10
    )
    db.add(sweet)
    db.commit()
    db.refresh(sweet)
    sweet_id = sweet.id
    db.close()
    
    # Delete as admin
    response = client.delete(
        f"/api/sweets/{sweet_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Sweet deleted successfully"

def test_delete_sweet_as_non_admin_fails(client, auth_token):
    """Test deleting a sweet as non-admin fails"""
    # Create a sweet
    create_response = client.post(
        "/api/sweets",
        json={
            "name": "Cannot Delete",
            "category": "Test",
            "price": 1.00,
            "quantity": 10
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    sweet_id = create_response.json()["id"]
    
    # Try to delete as non-admin
    response = client.delete(
        f"/api/sweets/{sweet_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 403

def test_delete_nonexistent_sweet(client, admin_token):
    """Test deleting a sweet that doesn't exist"""
    response = client.delete(
        "/api/sweets/99999",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404