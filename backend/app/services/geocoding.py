from __future__ import annotations

from typing import Dict, Tuple
import httpx

FAKE_GEOCODER: Dict[str, Tuple[float, float]] = {
    'heydar aliyev center': (40.4010, 49.8703),
    'ganjlik mall': (40.4005, 49.8518),
    '20 yanvar': (40.4117, 49.8134),
    'koroglu': (40.4202, 50.0130),
    'nizami metro': (40.3791, 49.8332),
    'içərişəhər': (40.3668, 49.8335),
    'icherisheher': (40.3668, 49.8335),
    'airport': (40.4675, 50.0467),
}


async def geocode_query(query: str) -> tuple[float, float, str]:
    cleaned = query.strip().lower()
    if cleaned in FAKE_GEOCODER:
        lat, lon = FAKE_GEOCODER[cleaned]
        return lat, lon, query.strip().title()

    # Try coordinate input directly.
    if ',' in cleaned:
        parts = [p.strip() for p in cleaned.split(',', 1)]
        try:
            lat = float(parts[0])
            lon = float(parts[1])
            return lat, lon, f'{lat},{lon}'
        except ValueError:
            pass

    # Optional Nominatim fallback.
    try:
        async with httpx.AsyncClient(timeout=8.0, headers={'User-Agent': 'smartcity-bot/1.0'}) as client:
            r = await client.get('https://nominatim.openstreetmap.org/search', params={
                'q': query,
                'format': 'jsonv2',
                'limit': 1,
            })
            r.raise_for_status()
            data = r.json()
            if data:
                item = data[0]
                return float(item['lat']), float(item['lon']), item.get('display_name', query)
    except Exception:
        pass

    raise ValueError('Destination not found. Send coordinates like 40.4093,49.8671 or a known place name.')
