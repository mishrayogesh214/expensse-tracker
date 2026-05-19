from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# -----------------------------------
# App setup
# -----------------------------------

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# -----------------------------------
# Database setup
# -----------------------------------

DATABASE_URL = "sqlite:///./database.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

# -----------------------------------
# Expense Model
# -----------------------------------

class Expense(Base):

    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    amount = Column(Float)
    category = Column(String)

# Create DB tables
Base.metadata.create_all(bind=engine)

# -----------------------------------
# Home Page
# -----------------------------------

@app.get("/")
def home(request: Request):

    db = SessionLocal()

    expenses = db.query(Expense).all()

    total = sum(exp.amount for exp in expenses)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "expenses": expenses,
            "total": total
        }
    )
# -----------------------------------
# Add Expense
# -----------------------------------

@app.post("/add")
def add_expense(
    title: str = Form(...),
    amount: float = Form(...),
    category: str = Form(...)
):

    db = SessionLocal()

    new_expense = Expense(
        title=title,
        amount=amount,
        category=category
    )

    db.add(new_expense)

    db.commit()

    return RedirectResponse(
        url="/",
        status_code=303
    )

# -----------------------------------
# Delete Expense
# -----------------------------------

@app.get("/delete/{expense_id}")
def delete_expense(expense_id: int):

    db = SessionLocal()

    expense = db.query(Expense).filter(
        Expense.id == expense_id
    ).first()

    if expense:
        db.delete(expense)
        db.commit()

    return RedirectResponse(
        url="/",
        status_code=303
    )