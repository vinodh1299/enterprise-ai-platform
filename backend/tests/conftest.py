import pytest
import pytest_asyncio
from datetime import date
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.models.sales import Department, EmployeeRecord, Sale

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(autouse=True)
async def setup_test_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed sample sales & employee data for SQL agent testing
    async with TestingSessionLocal() as session:
        d1 = Department(id=1, name="Engineering", manager_name="Charlie Davis")
        d2 = Department(id=2, name="Sales", manager_name="Alice Johnson")
        d3 = Department(id=3, name="Finance", manager_name="Bob Smith")
        session.add_all([d1, d2, d3])
        await session.commit()

        s1 = Sale(id=1, department_id=2, amount=890000.00, region="North America", sale_date=date(2025, 7, 15))
        s2 = Sale(id=2, department_id=1, amount=450000.00, region="North America", sale_date=date(2025, 7, 20))
        s3 = Sale(id=3, department_id=3, amount=320000.00, region="Europe", sale_date=date(2025, 7, 25))

        e1 = EmployeeRecord(id=1, name="Alice Johnson", department_id=2, salary=125000.00, hire_date=date(2022, 3, 1))
        e2 = EmployeeRecord(id=2, name="Bob Smith", department_id=3, salary=110000.00, hire_date=date(2023, 6, 15))

        session.add_all([s1, s2, s3, e1, e2])
        await session.commit()

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
