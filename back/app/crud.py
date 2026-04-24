from sqlalchemy.orm import Session
from app.models import Inventory, Route
from app.schemas import InventoryItem, RouteRequest
from typing import List
from app import models, schemas
from app.database import SessionLocal
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
import json
import uuid
from sqlalchemy import or_
from app.utils import get_traffic_data
from app.config import settings


def get_inventory(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Inventory).offset(skip).limit(limit).all()


def create_inventory_item(db: Session, item: schemas.InventoryItem):
    existing_item = (
        db.query(models.Inventory)
        .filter_by(item_name=item.item_name, location=item.location)
        .first()
    )
    if existing_item:
        raise ValueError(f"Item {item.item_name} already exists at {item.location}.")

    db_item = models.Inventory(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_inventory_item(db: Session, item_id: int, updates: dict):
    db_item = db.query(models.Inventory).filter_by(id=item_id).first()
    if not db_item:
        raise ValueError("Item not found.")

    for key, value in updates.items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item


def save_route(db: Session, request: RouteRequest, optimized_route: list):
    try:
        total_distance = 0
        total_duration = 0

        for i in range(len(request.destinations) - 1):
            start = (request.destinations[i].lat, request.destinations[i].lon)
            end = (request.destinations[i + 1].lat, request.destinations[i + 1].lon)
            traffic_data = get_traffic_data(start, end, settings.TRAFFIC_API_KEY)
            total_distance += traffic_data.get("distance", 0)
            total_duration += traffic_data.get("duration", 0)

        db_route = Route(
            route_id=request.route_id or str(uuid.uuid4()),
            start_lat=request.start.lat,
            start_lon=request.start.lon,
            destinations=json.dumps(
                [{"lat": d.lat, "lon": d.lon} for d in request.destinations]
            ),
            optimized_route=json.dumps(optimized_route),
            distance=total_distance,
            duration=total_duration,
            deleted_at=None,
        )
        db.add(db_route)
        db.commit()
        db.refresh(db_route)
        return db_route
    except Exception as e:
        db.rollback()
        raise ValueError(f"Error saving route: {e}")


def get_all_routes(db: Session):
    return db.query(Route).all()


def get_active_routes(db: Session):
    return db.query(Route).filter(Route.deleted_at.is_(None)).all()


def soft_delete_route(db: Session, route_id: str):
    route = db.query(Route).filter_by(route_id=route_id).first()
    if not route:
        raise ValueError("Route not found.")

    route.deleted_at = datetime.utcnow()
    db.commit()
    return route
