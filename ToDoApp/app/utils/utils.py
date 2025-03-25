import uuid
from app.db.engine import session, User
from sqlalchemy.orm import Session


def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()


def init_superuser(db: Session = next(get_db())):
    superuser = User(id=uuid.uuid4(), username="admin", password="admin")
    db.add(superuser)
    db.commit()
    db.refresh(superuser)
    return superuser
