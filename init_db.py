from app import app, db
from werkzeug.security import generate_password_hash
from models import User

def initialize_database():
    """Initialize the database and create tables"""
    with app.app_context():
        db.create_all()
        admin_email = "rifasaudagar@gmail.com"
        admin_password = "Rifa1234"
        if not User.query.filter_by(email=admin_email).first():
            admin = User(
                email=admin_email,
                password=generate_password_hash(admin_password),  
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin account created!")
            print(f"Email: {admin_email}")
            print(f"Password: {admin_password}")
        else:
            print("ℹ️ Admin account already exists")
            
if __name__ == '__main__':
    initialize_database()