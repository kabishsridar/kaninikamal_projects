from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

# -------- Core tables (string PKs) --------
class Customer(Base):
    __tablename__ = "customers"
    customer_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, default="")
    email = Column(String, default="")
    phone = Column(String, default="")
    company = Column(String, default="")
    address = Column(String, default="")

class Product(Base):
    __tablename__ = "products"
    product_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, default="")
    description = Column(String, default="")
    unit_price = Column(Float, default=0.0)
    tax_rate = Column(Float, default=18.0)

class Quotation(Base):
    __tablename__ = "quotations"
    quotation_id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, ForeignKey("customers.customer_id"))
    product_id = Column(String, ForeignKey("products.product_id"))
    quantity = Column(Integer, default=1)
    discount = Column(Float, default=0.0)
    quotation_date = Column(String, default="")

class Order(Base):
    __tablename__ = "orders"
    order_id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, ForeignKey("customers.customer_id"))
    quotation_id = Column(String, ForeignKey("quotations.quotation_id"), nullable=True)
    order_date = Column(String, default="")
    status = Column(String, default="Pending")

class OrderItem(Base):
    __tablename__ = "order_items"
    # composite PK emulated by uniqueness; kept simple for SQLite
    order_id = Column(String, ForeignKey("orders.order_id"), primary_key=True)
    line_no = Column(Integer, primary_key=True)
    product_id = Column(String, ForeignKey("products.product_id"))
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, default=0.0)
    discount = Column(Float, default=0.0)

class Invoice(Base):
    __tablename__ = "invoices"
    invoice_id = Column(String, primary_key=True, index=True)
    quotation_id = Column(String, ForeignKey("quotations.quotation_id"), nullable=True)
    order_id = Column(String, ForeignKey("orders.order_id"), nullable=True)
    customer_id = Column(String, ForeignKey("customers.customer_id"))
    invoice_date = Column(String, default="")
    due_date = Column(String, default="")
    status = Column(String, default="Pending")

class Payment(Base):
    __tablename__ = "payments"
    payment_id = Column(String, primary_key=True, index=True)
    invoice_id = Column(String, ForeignKey("invoices.invoice_id"))
    amount = Column(Float, default=0.0)
    payment_date = Column(String, default="")
    method = Column(String, default="UPI")
