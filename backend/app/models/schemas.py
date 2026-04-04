from typing import List, Optional
from pydantic import BaseModel, Field


class Coordinates(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)


class RouteRequest(BaseModel):
    origin: Coordinates
    destination: Coordinates
    destination_text: Optional[str] = None
    use_eco: bool = True


class RouteOption(BaseModel):
    summary: str
    distance_km: float
    duration_min: int
    traffic_level: str
    eco_score: int
    warnings: List[str] = []


class RouteResponse(BaseModel):
    ok: bool = True
    city: str
    origin: Coordinates
    destination: Coordinates
    routes: List[RouteOption]


class GeocodeRequest(BaseModel):
    query: str


class GeocodeResponse(BaseModel):
    ok: bool = True
    query: str
    result: Coordinates
    formatted_address: str
