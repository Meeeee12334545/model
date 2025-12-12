"""Placeholder script for seeding demo data."""

import asyncio
from db.session import engine, Base


async def main() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Initialized database with metadata (demo).")


if __name__ == "__main__":
    asyncio.run(main())
