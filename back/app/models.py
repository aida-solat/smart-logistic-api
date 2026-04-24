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


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String, nullable=False, index=True)
    stock = Column(Integer, nullable=False, default=0)
    location = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("item_name", "location", name="unique_item_location"),
    )

    def __repr__(self):
        return f"<Inventory(item_name={self.item_name}, location={self.location}, stock={self.stock})>"


class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(String, unique=True, index=True, nullable=False)
    start_lat = Column(Float, nullable=False)
    start_lon = Column(Float, nullable=False)
    destinations = Column(JSON, nullable=False)
    optimized_route = Column(JSON, nullable=False)
    distance = Column(Float, nullable=True)
    duration = Column(Float, nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self):
        return f"<Route(route_id={self.route_id}, start=({self.start_lat}, {self.start_lon}), destinations={self.destinations})>"


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
    permissions = Column(JSON, nullable=True)

    users = relationship("User", back_populates="role")


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
