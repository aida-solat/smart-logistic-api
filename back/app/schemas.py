from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class InventoryItem(BaseModel):
    item_name: str = Field(..., description="Name of the inventory item")
    stock: int = Field(..., description="Quantity of the item in stock")
    location: str = Field(..., description="Location where the item is stored")

    class Config:
        from_attributes = True


class InventoryAnalyticsRequest(BaseModel):
    start_date: Optional[datetime] = Field(
        None, description="Start date for filtering inventory data"
    )
    end_date: Optional[datetime] = Field(
        None, description="End date for filtering inventory data"
    )
    item_name: Optional[str] = Field(
        None, description="Filter inventory data by item name"
    )


class InventoryUpdateRequest(BaseModel):
    item_name: Optional[str] = None
    stock: Optional[int] = None
    location: Optional[str] = None

    class Config:
        from_attributes = True


class Location(BaseModel):
    lat: float = Field(..., description="Latitude of the location")
    lon: float = Field(..., description="Longitude of the location")


class RouteRequest(BaseModel):
    route_id: Optional[str] = Field(
        None, description="Optional unique identifier for the route"
    )
    start: Location = Field(..., description="Starting location of the route")
    destinations: List[Location] = Field(
        ..., description="List of destination locations for the route"
    )


class RouteResponse(BaseModel):
    optimized_route: List[Location] = Field(
        ..., description="Optimized route as a list of locations"
    )


class Route(BaseModel):
    route_id: Optional[str] = Field(None, description="Unique identifier for the route")
    start: Location = Field(..., description="Starting location of the route")
    destinations: List[Location] = Field(
        ..., description="List of destination locations for the route"
    )
    deleted_at: Optional[datetime] = Field(
        None, description="Timestamp for soft deletion"
    )

    class Config:
        from_attributes = True


class AdminDataRequest(BaseModel):
    filter: Optional[str] = Field(
        None, description="Filter for the admin data, e.g., 'user_activity'"
    )
    start_date: Optional[datetime] = Field(
        None, description="Start date for the data filter"
    )
    end_date: Optional[datetime] = Field(
        None, description="End date for the data filter"
    )


class PredictiveInventoryRequest(BaseModel):
    item_name: str
    days_from_now: int


class PredictiveRouteRequest(BaseModel):
    distance: float
    weather_conditions: int
    hour_of_day: int


class PredictiveResponse(BaseModel):
    inventory_prediction: Optional[dict] = None
    route_prediction: Optional[dict] = None


class TokenRequest(BaseModel):
    role: Optional[str] = "user"


class UserCreate(BaseModel):
    username: str
    password: str
    role_id: Optional[int] = None


class UserRead(BaseModel):
    id: int
    username: str
    role_id: Optional[int] = None

    class Config:
        from_attributes = True
