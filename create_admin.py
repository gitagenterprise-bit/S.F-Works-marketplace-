from extensions import db
from models.user import User
from app import create_app


app = create_app()

with app.app_context():

    email = "admin@sfworks.com"
    password = "Admin@12345"

    existing_admin = User.query.filter_by(
        email=email
    ).first()

    if existing_admin:

        existing_admin.role = "admin"
        existing_admin.is_active = True
        existing_admin.set_password(password)

        db.session.commit()

        print("Admin user updated successfully!")

    else:

        admin = User(
            full_name="S F Works Admin",
            email=email,
            phone="9999999999",
            role="admin",
            is_active=True
        )

        admin.set_password(password)

        db.session.add(admin)
        db.session.commit()

        print("Admin user created successfully!")

    print("--------------------------------")
    print("Email:", email)
    print("Password:", password)
    print("Role: admin")
    print("--------------------------------")
