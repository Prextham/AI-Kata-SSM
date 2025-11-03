from app.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def create_admin():
    db = SessionLocal()
    
    # Check if admin already exists
    existing_admin = db.query(User).filter(User.username == "admin").first()
    if existing_admin:
        print("Admin user already exists!")
        db.close()
        return
    
    # Create admin user
    admin = User(
        email="admin@sweetshop.com",
        username="admin",
        hashed_password=get_password_hash("admin123"),
        is_admin=True
    )
    
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    print(f"Admin user created successfully!")
    print(f"Username: admin")
    print(f"Password: admin123")
    print(f"Email: {admin.email}")
    
    db.close()

if __name__ == "__main__":
    create_admin()