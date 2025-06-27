import enum
from sqlalchemy import (
    Column,
    Integer,
    Text,
    Numeric,
    Enum as SQLEnum,
    Date,
    TIMESTAMP,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(Text, nullable=False, unique=True)
    password_hash = Column(Text, nullable=False)
    first_name = Column(Text, nullable=False)
    last_name = Column(Text, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow
    )

    Categories = relationship("Category", back_populates="user")
    cards = relationship("Card", back_populates="user")
    savings_goals = relationship("SavingsGoals", back_populates="user")
    savings_log = relationship("SavingsLog", back_populates="user")
    incomes = relationship("Income", back_populates="user")
    expenses = relationship("Expense", back_populates="user")


class CardIssuer(enum.Enum):
    Visa = "Visa"
    MasterCard = "MasterCard"
    AmericanExpress = "American Express"
    Discovery = "Discovery"


class Card(Base):
    __tablename__ = "cards"
    __table_args__ = (UniqueConstraint("user_id", "name"),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(Text, nullable=False)
    issuer = Column(
        SQLEnum(CardIssuer, name="card_issuer_enum", native_enum=True), nullable=False
    )
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow
    )

    user = relationship("User", back_populates="cards")
    expenses = relationship("Expense", back_populates="card")


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (UniqueConstraint("user_id", "name"),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(Text, nullable=False)
    description = Column(Text)

    user = relationship("User", back_populates="categories")
    incomes = relationship("Income", back_populates="category")
    expenses = relationship("Expense", back_populates="category")


class SavingsGoals(Base):
    __tablename__ = "savings_goals"
    __table_args__ = (UniqueConstraint("user_id", "name"),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(Text, nullable=False)
    target_amount = Column(Numeric(12, 2), nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow
    )

    user = relationship("User", back_populates="savings_goals")
    savings_log = relationship("SavingsLog", back_populates="goal")


class SavingsLog(Base):
    __tablename__ = "savings_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    goal_id = Column(Integer, ForeignKey("savings_goals.id"), nullable=False)
    amount_saved = Column(Numeric(12, 2), nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow
    )

    user = relationship("User", back_populates="savings_logs")
    goal = relationship("SavingsGoal", back_populates="savings_log")


class Income(Base):
    __tablename__ = "incomes"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    source = Column(Text, nullable=False)
    date = Column(Date, nullable=False)
    notes = Column(Text)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow
    )

    user = relationship("User", back_populates="incomes")
    category = relationship("Category", back_populates="incomes")


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    card_id = Column(Integer, ForeignKey("cards.id"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    date = Column(Date, nullable=False)
    vendor = Column(Text, nullable=False)
    notes = Column(Text)
    photo_url = Column(Text)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow
    )

    user = relationship("User", back_populates="expenses")
    category = relationship("Category", back_populates="expenses")
    card = relationship("Card", back_populates="expenses")
