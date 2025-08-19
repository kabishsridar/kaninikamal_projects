from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from .database import Base, engine, get_db
from . import models
from .utils import default_row

Base.metadata.create_all(bind=engine)

app = FastAPI(title="ThozhilMate API")

# CORS (vite dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

# ---- Metadata to power the SPA ----
TABLES_META = {
    "customers": {"pk": ["customer_id"], "model": models.Customer},
    "products": {"pk": ["product_id"], "model": models.Product},
    "quotations": {"pk": ["quotation_id"], "model": models.Quotation},
    "orders": {"pk": ["order_id"], "model": models.Order},
    "order_items": {"pk": ["order_id", "line_no"], "model": models.OrderItem},
    "invoices": {"pk": ["invoice_id"], "model": models.Invoice},
    "payments": {"pk": ["payment_id"], "model": models.Payment},
}

@app.get("/api/meta")
def meta():
    out = {}
    for name, m in TABLES_META.items():
        cols = [c.name for c in m["model"].__table__.columns]
        out[name] = {"columns": cols, "pk": m["pk"]}
    return out

# ---- Generic CRUD for single-PK tables ----
def _single_pk_guard(table: str):
    meta = TABLES_META[table]
    if len(meta["pk"]) != 1:
        raise HTTPException(400, "Use the composite endpoints for this table.")
    return meta

@app.get("/api/{table}")
def list_rows(table: str, db: Session = Depends(get_db)):
    if table not in TABLES_META: raise HTTPException(404, "Table not found")
    model = TABLES_META[table]["model"]
    rows = db.query(model).all()
    return [ {c.name: getattr(r, c.name) for c in model.__table__.columns} for r in rows ]

@app.post("/api/{table}/create_default")
def create_default(table: str, db: Session = Depends(get_db)):
    if table not in TABLES_META: raise HTTPException(404, "Table not found")
    model = TABLES_META[table]["model"]
    rowdict = default_row(db, table)
    obj = model(**rowdict)
    db.add(obj); db.commit()
    return rowdict

@app.put("/api/{table}/{pk}")
def update_row(table: str, pk: str, payload: Dict[str, Any], db: Session = Depends(get_db)):
    meta = _single_pk_guard(table)
    model = meta["model"]; pk_col = meta["pk"][0]
    row = db.query(model).filter(getattr(model, pk_col) == pk).first()
    if not row: raise HTTPException(404, "Row not found")
    for k, v in payload.items():
        if k in meta["pk"]:  # do not allow pk edits
            continue
        if hasattr(row, k): setattr(row, k, v)
    db.commit()
    return {"status": "ok"}

@app.delete("/api/{table}/{pk}")
def delete_row(table: str, pk: str, db: Session = Depends(get_db)):
    meta = _single_pk_guard(table)
    model = meta["model"]; pk_col = meta["pk"][0]
    row = db.query(model).filter(getattr(model, pk_col) == pk).first()
    if not row: raise HTTPException(404, "Row not found")
    db.delete(row); db.commit()
    return {"status": "deleted"}

# ---- Composite-PK endpoints: order_items ----
@app.put("/api/order_items/{order_id}/{line_no}")
def update_order_item(order_id: str, line_no: int, payload: Dict[str, Any], db: Session = Depends(get_db)):
    m = models.OrderItem
    row = db.query(m).filter(m.order_id == order_id, m.line_no == line_no).first()
    if not row: raise HTTPException(404, "Row not found")
    for k, v in payload.items():
        if k in ("order_id", "line_no"):  # keep PK intact
            continue
        if hasattr(row, k): setattr(row, k, v)
    db.commit()
    return {"status": "ok"}

@app.delete("/api/order_items/{order_id}/{line_no}")
def delete_order_item(order_id: str, line_no: int, db: Session = Depends(get_db)):
    m = models.OrderItem
    row = db.query(m).filter(m.order_id == order_id, m.line_no == line_no).first()
    if not row: raise HTTPException(404, "Row not found")
    db.delete(row); db.commit()
    return {"status": "deleted"}
