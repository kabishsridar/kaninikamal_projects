import re
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models

def today() -> str:
    return date.today().isoformat()

def in_days(n: int) -> str:
    return (date.today() + timedelta(days=n)).isoformat()

def next_id(db: Session, model, col_name: str, prefix_hint: str) -> str:
    # Scan existing ids and pick next numeric suffix
    col = getattr(model, col_name)
    rows = db.query(col).filter(col.isnot(None)).all()
    max_n = 0
    for (val,) in rows:
        s = str(val)
        m = re.search(r"(\d+)$", s)
        if m:
            max_n = max(max_n, int(m.group(1)))
    return f"{prefix_hint}{max_n+1:03d}"

def default_row(db: Session, table: str) -> dict:
    """Return server-side sensible defaults per table to support SPA 'Insert Row'."""
    if table == "customers":
        return {
            "customer_id": next_id(db, models.Customer, "customer_id", "CUST"),
            "name": "New Customer", "email": "", "phone": "", "company": "", "address": ""
        }
    if table == "products":
        return {
            "product_id": next_id(db, models.Product, "product_id", "PROD"),
            "name": "New Product", "description": "", "unit_price": 0.0, "tax_rate": 18.0
        }
    if table == "quotations":
        cust = db.query(models.Customer.customer_id).order_by(models.Customer.customer_id).first()
        prod = db.query(models.Product.product_id).order_by(models.Product.product_id).first()
        return {
            "quotation_id": next_id(db, models.Quotation, "quotation_id", "QUO"),
            "customer_id": cust[0] if cust else None,
            "product_id": prod[0] if prod else None,
            "quantity": 1, "discount": 0.0, "quotation_date": today()
        }
    if table == "orders":
        cust = db.query(models.Customer.customer_id).order_by(models.Customer.customer_id).first()
        quo = db.query(models.Quotation.quotation_id).order_by(models.Quotation.quotation_id).first()
        return {
            "order_id": next_id(db, models.Order, "order_id", "ORD"),
            "customer_id": cust[0] if cust else None,
            "quotation_id": quo[0] if quo else None,
            "order_date": today(), "status": "Pending"
        }
    if table == "order_items":
        # choose latest order or create one
        ord_row = db.query(models.Order).order_by(models.Order.order_date.desc()).first()
        if not ord_row:
            ord_row = models.Order(
                order_id=next_id(db, models.Order, "order_id", "ORD"),
                customer_id=None, quotation_id=None, order_date=today(), status="Pending"
            )
            db.add(ord_row); db.commit()
        order_id = ord_row.order_id
        max_ln = db.query(func.coalesce(func.max(models.OrderItem.line_no), 0))\
                   .filter(models.OrderItem.order_id == order_id).scalar()
        prod = db.query(models.Product.product_id, models.Product.unit_price).first()
        return {
            "order_id": order_id,
            "line_no": int(max_ln) + 1,
            "product_id": prod[0] if prod else None,
            "quantity": 1,
            "unit_price": float(prod[1]) if prod else 0.0,
            "discount": 0.0
        }
    if table == "invoices":
        cust = db.query(models.Customer.customer_id).order_by(models.Customer.customer_id).first()
        ordx = db.query(models.Order.order_id).order_by(models.Order.order_date.desc()).first()
        return {
            "invoice_id": next_id(db, models.Invoice, "invoice_id", "INV"),
            "quotation_id": None, "order_id": ordx[0] if ordx else None,
            "customer_id": cust[0] if cust else None,
            "invoice_date": today(), "due_date": in_days(14), "status": "Pending"
        }
    if table == "payments":
        inv = db.query(models.Invoice.invoice_id).order_by(models.Invoice.invoice_id).first()
        return {
            "payment_id": next_id(db, models.Payment, "payment_id", "PAY"),
            "invoice_id": inv[0] if inv else None,
            "amount": 0.0, "payment_date": today(), "method": "UPI"
        }
    raise ValueError("Unknown table")
