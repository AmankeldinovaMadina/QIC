"""Migration script to add culture_guides table."""

import asyncio

from app.db.database import Base, engine
from app.db.models import CultureGuide


async def migrate():
    """Create the culture_guides table."""
    async with engine.begin() as conn:
        # Create only the culture_guides table
        await conn.run_sync(CultureGuide.__table__.create, checkfirst=True)
    print("✅ culture_guides table created successfully")


if __name__ == "__main__":
    asyncio.run(migrate())
