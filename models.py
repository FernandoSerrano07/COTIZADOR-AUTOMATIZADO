from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base
import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)


class Quotations(Base):
    __tablename__ = "quotations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    client_name = Column(String(100), nullable=False)
    client_phone = Column(String(50), nullable=True)
    client_address = Column(String(255), nullable=True)
    subtotal = Column(Float, nullable=False)
    apply_iva = Column(Boolean, default=False)
    total = Column(Float, nullable=False)
    pdf_path = Column(String(255), nullable=True)
    date = Column(DateTime, default=datetime.datetime.utcnow)

    items = relationship("QuotationItem", back_populates="quotation", cascade="all, delete-orphan")


class QuotationItem(Base):
    __tablename__ = "quotation_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    quotation_id = Column(Integer, ForeignKey("quotations.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    subtotal = Column(Float, nullable=False)

    quotation = relationship("Quotations", back_populates="items")
    product = relationship("Product")