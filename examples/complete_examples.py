"""
MentoDB v2.1 - Complete Examples

This file demonstrates all features of MentoDB including:
- Async support
- Query builder
- Migrations
- Connection pooling
- Relationships
- Indexes
- Bulk operations
- Caching
"""

import asyncio
from pydantic import BaseModel
from mentodb import (
    # Core
    Mento,
    Connection,
    # Async
    AsyncConnection,
    # Query building
    QueryBuilder,
    # Database management
    Migration,
    MigrationManager,
    IndexManager,
    RelationshipManager,
    ForeignKey,
    # Performance
    ConnectionPool,
    BulkOperations,
    QueryCache,
    CachedConnection,
)


# =============================================================================
# 1. BASIC USAGE (From v2.0)
# =============================================================================

class User(BaseModel):
    id: int
    name: str
    email: str
    age: int


def example_basic():
    """Basic CRUD operations."""
    print("\n=== BASIC USAGE ===")

    with Connection("example.db") as conn:
        db = Mento(conn, default_table="users")

        # Create table
        db.create("users", model=User)

        # Insert
        db.insert("users", data={"id": 1, "name": "Alice", "email": "alice@example.com", "age": 30})

        # Select
        users = db.select(from_table="users")
        print(f"Users: {users}")

        # Update
        db.update("users", data={"age": 31}, where={"id": 1})

        # Delete
        db.delete("users", where={"id": 1})


# =============================================================================
# 2. ASYNC SUPPORT
# =============================================================================

async def example_async():
    """Async database operations."""
    print("\n=== ASYNC SUPPORT ===")

    async with AsyncConnection("example.db") as conn:
        # Create table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS async_users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                email TEXT
            )
        """)

        # Insert
        await conn.execute(
            "INSERT INTO async_users VALUES (?, ?, ?)",
            (1, "Bob", "bob@example.com")
        )

        # Query
        cursor = await conn.execute("SELECT * FROM async_users")
        rows = await cursor.fetchall()
        print(f"Async users: {rows}")


# =============================================================================
# 3. QUERY BUILDER
# =============================================================================

def example_query_builder():
    """Fluent API for building queries."""
    print("\n=== QUERY BUILDER ===")

    # Build SELECT query
    query, params = (
        QueryBuilder("users")
        .select("id", "name", "email")
        .where("age", ">", 18)
        .where("active", "=", True)
        .order_by("name", "ASC")
        .limit(10)
        .build()
    )
    print(f"Query: {query}")
    print(f"Params: {params}")

    # Build INSERT query
    query, params = (
        QueryBuilder("users")
        .insert({"id": 1, "name": "Charlie", "email": "charlie@example.com", "age": 25})
        .build()
    )
    print(f"Insert: {query}")

    # Build UPDATE query
    query, params = (
        QueryBuilder("users")
        .update({"age": 26})
        .where("id", "=", 1)
        .build()
    )
    print(f"Update: {query}")

    # Build JOIN query
    query, params = (
        QueryBuilder("orders")
        .select("orders.id", "users.name", "orders.total")
        .join("users", "orders.user_id = users.id", "INNER")
        .where("orders.total", ">", 100)
        .build()
    )
    print(f"Join: {query}")


# =============================================================================
# 4. MIGRATIONS
# =============================================================================

def example_migrations():
    """Database schema migrations."""
    print("\n=== MIGRATIONS ===")

    with Connection("example.db") as conn:
        manager = MigrationManager(conn)
        manager.init()

        # Define migrations
        def create_users_table(conn):
            conn.execute("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE
                )
            """)

        def drop_users_table(conn):
            conn.execute("DROP TABLE users")

        def add_age_column(conn):
            conn.execute("ALTER TABLE users ADD COLUMN age INTEGER")

        # Register migrations
        manager.register(Migration("001", "create_users", create_users_table, drop_users_table))
        manager.register(Migration("002", "add_age_column", add_age_column))

        # Apply migrations
        count = manager.migrate()
        print(f"Applied {count} migrations")

        # Check status
        status = manager.status()
        print(f"Migration status: {status}")

        # Rollback
        # manager.rollback(steps=1)


# =============================================================================
# 5. CONNECTION POOLING
# =============================================================================

def example_connection_pool():
    """Thread-safe connection pool."""
    print("\n=== CONNECTION POOLING ===")

    pool = ConnectionPool("example.db", max_connections=5)

    # Use connection from pool
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        print(f"User count: {count}")

    # Pool automatically manages connections
    print(f"Pool size: {pool.size()}")

    pool.close_all()


# =============================================================================
# 6. RELATIONSHIPS
# =============================================================================

def example_relationships():
    """Foreign keys and relationships."""
    print("\n=== RELATIONSHIPS ===")

    with Connection("example.db") as conn:
        rm = RelationshipManager(conn)

        # Create tables with foreign keys
        rm.create_table_with_fk(
            "orders",
            {
                "id": "INTEGER PRIMARY KEY",
                "user_id": "INTEGER NOT NULL",
                "total": "REAL",
                "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            },
            [ForeignKey("orders", "user_id", "users", "id", on_delete="CASCADE")]
        )

        # Query with JOIN
        results = rm.join(
            from_table="orders",
            join_table="users",
            on="orders.user_id = users.id",
            select_columns=["orders.id", "users.name", "orders.total"]
        )
        print(f"Orders with user names: {results}")

        # One-to-many relationship
        user_with_orders = rm.one_to_many(
            parent_table="users",
            child_table="orders",
            foreign_key_column="user_id",
            parent_id=1
        )
        print(f"User with orders: {user_with_orders}")


# =============================================================================
# 7. INDEX MANAGEMENT
# =============================================================================

def example_indexes():
    """Create and manage indexes."""
    print("\n=== INDEX MANAGEMENT ===")

    with Connection("example.db") as conn:
        idx_manager = IndexManager(conn)

        # Create index
        idx_manager.create_index(
            table="users",
            index_name="idx_email",
            columns=["email"],
            unique=True
        )

        # Create composite index
        idx_manager.create_index(
            table="users",
            index_name="idx_name_age",
            columns=["name", "age"]
        )

        # List indexes
        indexes = idx_manager.list_indexes("users")
        print(f"Indexes on users table: {indexes}")

        # Analyze for performance
        idx_manager.analyze("users")


# =============================================================================
# 8. BULK OPERATIONS
# =============================================================================

def example_bulk_operations():
    """Efficient batch processing."""
    print("\n=== BULK OPERATIONS ===")

    with Connection("example.db") as conn:
        bulk = BulkOperations(conn)

        # Bulk insert
        users_data = [
            {"id": i, "name": f"User{i}", "email": f"user{i}@example.com", "age": 20 + i}
            for i in range(1, 1001)
        ]
        inserted = bulk.bulk_insert("users", users_data, batch_size=100)
        print(f"Inserted {inserted} users")

        # Bulk update
        update_data = [
            {"id": i, "age": 25 + i}
            for i in range(1, 101)
        ]
        updated = bulk.bulk_update("users", update_data, key_column="id")
        print(f"Updated {updated} users")

        # Bulk delete
        ids_to_delete = list(range(1, 51))
        deleted = bulk.bulk_delete("users", ids_to_delete, key_column="id")
        print(f"Deleted {deleted} users")

        # Bulk upsert
        upsert_data = [
            {"id": i, "name": f"Updated{i}", "email": f"updated{i}@example.com", "age": 30}
            for i in range(1, 11)
        ]
        affected = bulk.bulk_upsert("users", upsert_data, conflict_columns=["id"])
        print(f"Upserted {affected} users")


# =============================================================================
# 9. QUERY CACHING
# =============================================================================

def example_caching():
    """Query result caching."""
    print("\n=== QUERY CACHING ===")

    with Connection("example.db") as conn:
        # Create cache
        cache = QueryCache(max_size=1000, ttl=300)  # 5 minutes TTL

        # Use cached connection
        cached_conn = CachedConnection(conn, cache)

        # First query - miss
        result1 = cached_conn.execute("SELECT * FROM users WHERE id = ?", (1,), use_cache=True)
        print(f"First query result: {result1}")

        # Second query - hit (cached)
        result2 = cached_conn.execute("SELECT * FROM users WHERE id = ?", (1,), use_cache=True)
        print(f"Second query result (cached): {result2}")

        # Check cache stats
        stats = cache.stats()
        print(f"Cache stats: {stats}")

        # Invalidate cache for table
        cached_conn.invalidate_cache(table="users")
        print("Cache invalidated")


# =============================================================================
# MAIN - RUN ALL EXAMPLES
# =============================================================================

def main():
    """Run all examples."""
    print("=" * 80)
    print("MentoDB v2.1 - Complete Examples")
    print("=" * 80)

    # Basic usage
    example_basic()

    # Query builder
    example_query_builder()

    # Migrations
    example_migrations()

    # Connection pooling
    example_connection_pool()

    # Relationships
    example_relationships()

    # Indexes
    example_indexes()

    # Bulk operations
    example_bulk_operations()

    # Caching
    example_caching()

    # Async (run separately)
    print("\n=== Running async example ===")
    asyncio.run(example_async())

    print("\n" + "=" * 80)
    print("All examples completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
