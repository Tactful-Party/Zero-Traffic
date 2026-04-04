from fastapi import APIRouter, HTTPException
from ..config import settings
from ..models.schemas import Coordinates, GeocodeRequest, GeocodeResponse, RouteOption, RouteRequest, RouteResponse
from ..services.camera import get_camera_status
from ..services.geocoding import geocode_query
from ..services.news import get_news_summary
from ..services.opendata import get_city_open_data
from ..services.routing import build_routes
from ..services.weather import get_weather_summary

router = APIRouter(prefix='/api', tags=['api'])


@router.post('/geocode', response_model=GeocodeResponse)
async def geocode_endpoint(payload: GeocodeRequest):
    try:
        lat, lon, formatted = await geocode_query(payload.query)
        return GeocodeResponse(query=payload.query, result=Coordinates(lat=lat, lon=lon), formatted_address=formatted)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post('/route', response_model=RouteResponse)
async def route_endpoint(payload: RouteRequest):
    routes = build_routes(
        origin=(payload.origin.lat, payload.origin.lon),
        destination=(payload.destination.lat, payload.destination.lon),
        use_eco=payload.use_eco,
    )
    weather = get_weather_summary()
    news = get_news_summary()
    city_data = get_city_open_data()

    enriched = []
    for route in routes:
        warnings = list(route.get('warnings', []))
        if news['active_alerts']:
            warnings.append(news['items'][0])
        if city_data['air_quality_index'] > 60:
            warnings.append('Air quality is moderately affected today.')
        if weather['impact_score'] > 25:
            warnings.append('Weather may affect visibility or speed.')
        enriched.append(RouteOption(**{**route, 'warnings': warnings[:3]}))

    return RouteResponse(
        city=settings.city_name,
        origin=payload.origin,
        destination=payload.destination,
        routes=enriched,
    )


@router.get('/weather')
def weather_endpoint():
    return get_weather_summary()


@router.get('/news')
def news_endpoint():
    return get_news_summary()


@router.get('/camera/status')
def camera_endpoint():
    return get_camera_status()
