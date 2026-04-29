import pytest 
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from api.db_connecter import Base, get_db
from api.main import app
from api.models.user import User
from api.authenticator import get_current_user, is_ops_user

engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    class_=Session,
)

@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def test_user(db_session):
    user = User(
        first_name="John",
        last_name="Doe",
        username="TestUser",
        password_hash="temporary-password-hash",
        role="ops",
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user 

@pytest.fixture()
def client(db_session, test_user):
    def override_get_db():
        yield db_session

    def override_current_user():
        return test_user
    
    def override_ops_user():
        return test_user
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_current_user
    app.dependency_overrides[is_ops_user] = override_ops_user

    yield TestClient(app)

    app.dependency_overrides.clear()