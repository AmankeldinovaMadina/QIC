"""Migration script to add selected_hotel_link column to trips table."""

import asyncio
from sqlalchemy import text
from app.db.database import engine


async def migrate():
    """Add selected_hotel_link column to trips table."""
    
    async with engine.begin() as conn:
        # Check if column already exists
        result = await conn.execute(
            text("PRAGMA table_info(trips)")
        )
        columns = [row[1] for row in result.fetchall()]
        
        if 'selected_hotel_link' in columns:
            print("ℹ️  Column 'selected_hotel_link' already exists")
            return
        
        # Add the column
        await conn.execute(
            text("ALTER TABLE trips ADD COLUMN selected_hotel_link VARCHAR(1000)")
        )
        
        print("✅ Added 'selected_hotel_link' column to trips table")


if __name__ == "__main__":
    asyncio.run(migrate())
