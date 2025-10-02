import asyncio
from src.db import async_session, engine, Base
from src.models import Project, User

async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        if not await session.get(Project, 1):
            session.add(Project(id=1, name="Demo Project", description="First run demo"))
        if not await session.get(User, 1):
            session.add(User(id=1, name="Alice", external_ref="alice@example.com"))
        await session.commit()
    print("Seeded Project#1 and User#1")

if __name__ == "__main__":
    asyncio.run(main())
