from datetime import datetime, date, timezone
from sqlalchemy import String, Integer, DateTime, ForeignKey, Numeric, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Department(Base):
    """
    SQLAlchemy ORM model for company departments table.
    """
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    manager_name: Mapped[str] = mapped_column(String(100), nullable=False)

    sales: Mapped[list["Sale"]] = relationship("Sale", back_populates="department")


class EmployeeRecord(Base):
    """
    SQLAlchemy ORM model for employee records table.
    """
    __tablename__ = "employee_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    department_id: Mapped[int] = mapped_column(Integer, ForeignKey("departments.id"), nullable=False)
    salary: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    hire_date: Mapped[date] = mapped_column(Date, nullable=False)


class Sale(Base):
    """
    SQLAlchemy ORM model for sales revenue transactions table.
    """
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    department_id: Mapped[int] = mapped_column(Integer, ForeignKey("departments.id"), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    region: Mapped[str] = mapped_column(String(50), nullable=False)
    sale_date: Mapped[date] = mapped_column(Date, nullable=False)

    department: Mapped["Department"] = relationship("Department", back_populates="sales")
