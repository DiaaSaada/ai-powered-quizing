"""
MongoDB connection management using Motor (async driver).
Provides connection pooling and lifecycle management.
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
from app.config import settings


class MongoDB:
    """
    MongoDB connection manager.
    Handles async connection with connection pooling.
    """

    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None

    @classmethod
    async def connect(cls) -> None:
        """
        Connect to MongoDB.
        Should be called on application startup.
        """
        cls.client = AsyncIOMotorClient(
            settings.mongodb_url,
            maxPoolSize=10,
            minPoolSize=1,
            serverSelectionTimeoutMS=5000
        )
        cls.db = cls.client[settings.mongodb_db_name]

        # Verify connection
        try:
            await cls.client.admin.command("ping")
            print(f"   Connected to MongoDB: {settings.mongodb_db_name}")
        except Exception as e:
            print(f"   Warning: MongoDB connection failed: {e}")
            print(f"   Running without database caching")
            cls.client = None
            cls.db = None

    @classmethod
    async def disconnect(cls) -> None:
        """
        Disconnect from MongoDB.
        Should be called on application shutdown.
        """
        if cls.client:
            cls.client.close()
            print("   Disconnected from MongoDB")

    @classmethod
    def get_db(cls) -> Optional[AsyncIOMotorDatabase]:
        """
        Get the database instance.

        Returns:
            Database instance or None if not connected
        """
        return cls.db

    @classmethod
    def is_connected(cls) -> bool:
        """
        Check if database is connected.

        Returns:
            True if connected, False otherwise
        """
        return cls.db is not None


# Convenience function for dependency injection
def get_database() -> Optional[AsyncIOMotorDatabase]:
    """Get database instance for FastAPI dependency injection."""
    return MongoDB.get_db()
