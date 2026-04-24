from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    JSON,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    TIMESTAMP,
)
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy.sql import func


# Inventory model represents the stock details of items in different locations.
class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(
        Integer, primary_key=True, index=True
    )  # Primary key for the inventory table
    item_name = Column(
        String, nullable=False, index=True
    )  # Name of the item, indexed for faster lookups
    stock = Column(Integer, nullable=False, default=0)  # Quantity of the item available
    location = Column(String, nullable=False)  # Location where the item is stored
    created_at = Column(
        DateTime, server_default=func.now(), nullable=False
    )  # Timestamp for creation
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )  # Auto-updated timestamp for modifications

    # Constraint to ensure that the combination of item_name and location is unique
    __table_args__ = (
        UniqueConstraint("item_name", "location", name="unique_item_location"),
    )

    def __repr__(self):
        return f"<Inventory(item_name={self.item_name}, location={self.location}, stock={self.stock})>"


# Route model represents route information for deliveries or logistics.
class Route(Base):
    __tablename__ = "routes"

    distance = Column(Float, nullable=True)  # Add distance
    duration = Column(Float, nullable=True)  # Add duration
    deleted_at = Column(DateTime, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    id = Column(
        Integer, primary_key=True, index=True
    )  # Primary key for the route table
    route_id = Column(
        String, unique=True, index=True, nullable=False
    )  # Unique identifier for the route
    start_lat = Column(Float, nullable=False)  # Latitude of the starting point
    start_lon = Column(Float, nullable=False)  # Longitude of the starting point
    destinations = Column(
        JSON, nullable=False
    )  # JSON column to store destinations as a list of coordinates
    optimized_route = Column(
        JSON, nullable=False
    )  # JSON column to store the optimized route
    distance = Column(Float, nullable=True)
    duration = Column(Float, nullable=True)
    deleted_at = Column(DateTime, nullable=True)  # Timestamp for soft deletion
    created_at = Column(
        TIMESTAMP, server_default=func.now(), nullable=False
    )  # Timestamp for creation
    updated_at = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False
    )  # Auto-updated timestamp for modifications

    def __repr__(self):
        return f"<Route(route_id={self.route_id}, start=({self.start_lat}, {self.start_lon}), destinations={self.destinations})>"


# ---------------------------------------------------------------------------
# Auth: User / Role / Permission
# ---------------------------------------------------------------------------


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    role = relationship("Role", back_populates="users")


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    permissions = Column(JSON, nullable=True)  # list of permission names

    users = relationship("User", back_populates="role")


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
