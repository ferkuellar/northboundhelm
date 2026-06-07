import asyncio
import hashlib
from decimal import Decimal

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.project import Project
from app.models.user import User

ORG_ID = "default"


def hash_password(password: str) -> str:
    # Sprint 001 has no production auth. This deterministic hash only supports local seed data.
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


async def get_or_create_user(session, *, email: str, name: str, role: str, password: str | None = None) -> User:
    user = await session.scalar(select(User).where(User.email == email))
    if user:
        user.name = name
        user.role = role
        user.org_id = ORG_ID
        user.is_active = True
        if password:
            user.hashed_password = hash_password(password)
        print(f"reused user: {email}")
        return user

    user = User(
        email=email,
        name=name,
        role=role,
        org_id=ORG_ID,
        is_active=True,
        hashed_password=hash_password(password) if password else None,
    )
    session.add(user)
    await session.flush()
    print(f"created user: {email}")
    return user


async def get_or_create_project(session, *, name: str, owner: User, budget_usd: Decimal, description: str) -> Project:
    project = await session.scalar(select(Project).where(Project.name == name, Project.org_id == ORG_ID))
    if project:
        project.owner_id = owner.id
        project.budget_usd = budget_usd
        project.description = description
        project.is_active = True
        print(f"reused project: {name}")
        return project

    project = Project(
        name=name,
        org_id=ORG_ID,
        owner_id=owner.id,
        budget_usd=budget_usd,
        description=description,
        is_active=True,
    )
    session.add(project)
    await session.flush()
    print(f"created project: {name}")
    return project


async def main() -> None:
    async with AsyncSessionLocal() as session:
        admin = await get_or_create_user(
            session,
            email="admin@northboundhelm.io",
            name="Northbound Admin",
            role="admin",
            password="admin123",
        )
        developer1 = await get_or_create_user(
            session,
            email="developer1@northboundhelm.io",
            name="Developer One",
            role="developer",
        )
        developer2 = await get_or_create_user(
            session,
            email="developer2@northboundhelm.io",
            name="Developer Two",
            role="developer",
        )

        await get_or_create_project(
            session,
            name="FONDIXPAY",
            owner=admin,
            budget_usd=Decimal("5000.00"),
            description="FinOps project for FONDIXPAY.",
        )
        await get_or_create_project(
            session,
            name="Northbound Demo",
            owner=developer1,
            budget_usd=Decimal("1500.00"),
            description="Demo project for Northbound Helm.",
        )
        await get_or_create_project(
            session,
            name="Internal Tools",
            owner=developer2,
            budget_usd=Decimal("2500.00"),
            description="Internal operational tooling.",
        )

        await session.commit()
        print("seed completed")


if __name__ == "__main__":
    asyncio.run(main())

