"""Database migration for Entertainment Venues feature.

This migration adds:
1. EntertainmentSelection table for storing venue selections
2. selected_entertainments JSON column in Trip table
3. Relationship between Trip and EntertainmentSelection

Run this migration BEFORE starting the server with the new entertainment feature.
"""

from sqlalchemy import text

# SQL statements for SQLite migration
MIGRATION_SQL = """
-- 1. Add selected_entertainments column to trips table
ALTER TABLE trips ADD COLUMN selected_entertainments TEXT;

-- 2. Create entertainment_selections table
CREATE TABLE IF NOT EXISTS entertainment_selections (
    id TEXT PRIMARY KEY,
    trip_id TEXT NOT NULL,
    venue_id TEXT NOT NULL,
    venue_name TEXT NOT NULL,
    venue_type TEXT,
    address TEXT,
    rating NUMERIC(3, 2),
    reviews_count INTEGER,
    price_level TEXT,
    latitude NUMERIC(10, 7),
    longitude NUMERIC(10, 7),
    website TEXT,
    phone TEXT,
    opening_hours TEXT,  -- JSON stored as TEXT
    types TEXT,  -- JSON stored as TEXT (array)
    description TEXT,
    thumbnail TEXT,
    score NUMERIC(3, 2),
    title TEXT,
    pros_keywords TEXT,  -- JSON stored as TEXT (array)
    cons_keywords TEXT,  -- JSON stored as TEXT (array)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trip_id) REFERENCES trips (id)
);

-- 3. Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_entertainment_selections_trip_id 
ON entertainment_selections(trip_id);

CREATE INDEX IF NOT EXISTS idx_entertainment_selections_venue_id 
ON entertainment_selections(venue_id);
"""


# Python migration script
def run_migration():
    """Run the database migration."""
    import asyncio
    from app.db.database import engine
    from sqlalchemy import text
    
    async def execute_migration():
        async with engine.begin() as conn:
            # Execute statements in order
            statements = [
                # 1. Add selected_entertainments column to trips
                "ALTER TABLE trips ADD COLUMN selected_entertainments TEXT",
                
                # 2. Create entertainment_selections table
                """CREATE TABLE IF NOT EXISTS entertainment_selections (
                    id TEXT PRIMARY KEY,
                    trip_id TEXT NOT NULL,
                    venue_id TEXT NOT NULL,
                    venue_name TEXT NOT NULL,
                    venue_type TEXT,
                    address TEXT,
                    rating NUMERIC(3, 2),
                    reviews_count INTEGER,
                    price_level TEXT,
                    latitude NUMERIC(10, 7),
                    longitude NUMERIC(10, 7),
                    website TEXT,
                    phone TEXT,
                    opening_hours TEXT,
                    types TEXT,
                    description TEXT,
                    thumbnail TEXT,
                    score NUMERIC(3, 2),
                    title TEXT,
                    pros_keywords TEXT,
                    cons_keywords TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (trip_id) REFERENCES trips (id)
                )""",
                
                # 3. Create indexes
                "CREATE INDEX IF NOT EXISTS idx_entertainment_selections_trip_id ON entertainment_selections(trip_id)",
                "CREATE INDEX IF NOT EXISTS idx_entertainment_selections_venue_id ON entertainment_selections(venue_id)",
            ]
            
            for stmt in statements:
                stmt = stmt.strip()
                if stmt:
                    try:
                        await conn.execute(text(stmt))
                        print(f"✓ Executed: {stmt[:60]}...")
                    except Exception as e:
                        if "duplicate column name" in str(e).lower():
                            print(f"⚠ Column already exists, skipping...")
                        elif "already exists" in str(e).lower():
                            print(f"⚠ Table/index already exists, skipping...")
                        else:
                            print(f"✗ Error: {e}")
                            raise
            
            print("\n✅ Migration completed successfully!")
    
    asyncio.run(execute_migration())


if __name__ == "__main__":
    print("=" * 70)
    print("ENTERTAINMENT VENUES DATABASE MIGRATION")
    print("=" * 70)
    print("\nThis will add:")
    print("1. selected_entertainments column to trips table")
    print("2. entertainment_selections table")
    print("3. Indexes for performance")
    print("\nStarting migration...")
    print("-" * 70)
    
    run_migration()
    
    print("\n" + "=" * 70)
    print("Migration complete! You can now use the entertainment endpoints.")
    print("=" * 70)
