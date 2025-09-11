from db.session import SessionLocal
from models.user import User, RoleEnum
from core.security import hash_password

def create_admin():
    db = SessionLocal()
    email = "admin@example1.com"
    name="swet"
    mobile = 9999999998
    password = "Admin@123"

    existing = db.query(User).filter(User.email == email).first()
    if existing:
        print(" Admin already exists!")
        return

    admin_user = User(
        email=email,
        mobile=mobile,
        name=name,
        hashed_password=hash_password(password),
        role=RoleEnum.admin,
        is_active=True
    )
    db.add(admin_user)
    db.commit()
    print(" Admin created successfully!")

if __name__ == "__main__":
    create_admin()
