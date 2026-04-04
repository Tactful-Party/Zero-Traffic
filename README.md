# Zero Traffic

Zero Traffic is a small smart-city routing demo that combines a **FastAPI backend**, a **Telegram bot**, and a minimal **frontend** placeholder.

The project is designed to suggest city routes with lightweight traffic-aware and eco-aware logic. It also enriches route results with simulated weather, news, camera, and city open-data signals.

## What is included

- **Backend**: FastAPI service that exposes routing, geocoding, weather, news, and camera endpoints.
- **Telegram bot**: Aiogram bot that guides the user through sharing an origin and destination, then requests route suggestions from the backend.
- **Frontend**: Simple static HTML page with basic usage notes.
- **Prompts**: Additional prompt text stored in the `prompts/` folder.

## Project structure

```text
Zero-Traffic/
├── backend/
│   ├── app/
│   │   ├── config.py
│   │   ├── main.py
│   │   ├── models/
│   │   ├── routes/
│   │   └── services/
│   └── requirements.txt
├── bot/
│   └── bot.py
├── frontend/
│   └── index.html
├── prompts/
│   └── base44_prompt.txt
├── .env
└── README.md
```

## How it works

### Backend

The backend exposes API endpoints under `/api` and a health check under `/health`.

Main behavior:
- Accepts origin and destination coordinates.
- Builds multiple route options using distance-based calculations.
- Adds contextual warnings based on weather, news, and city data.
- Supports geocoding from either coordinates or place names.

### Telegram bot

The bot provides a simple conversation flow:
1. User sends `/start`
2. User sends `/route`
3. User shares their current location or types coordinates
4. User sends a destination as coordinates or a place name
5. Bot calls the backend and returns route suggestions

### Routing logic

The current routing logic is simulated rather than map-engine based. It:
- calculates distance with a haversine formula,
- estimates traffic severity from distance,
- generates three route styles:
  - fastest,
  - balanced,
  - eco route.

This makes the project good for demos, prototypes, and coursework, while leaving room for integration with real traffic and mapping APIs later.

## Features

- FastAPI backend with Swagger docs support
- Telegram bot with location sharing flow
- Basic geocoding support
- Route suggestions with warnings
- Simulated integrations for:
  - weather
  - news alerts
  - city open data
  - camera monitoring status
- CORS enabled for easy local testing

## Requirements

- Python 3.10+
- `pip`
- A Telegram bot token from BotFather

## Environment variables

The project reads configuration from `.env`.

Example:

```env
TELEGRAM_BOT_TOKEN=1234567890:replace_with_real_token
PUBLIC_BASE_URL=http://127.0.0.1:8000
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
CITY_NAME=Baku
```

### Variable details

- `TELEGRAM_BOT_TOKEN`: Telegram bot token used by `bot/bot.py`
- `PUBLIC_BASE_URL`: Base URL the bot uses to reach the backend
- `BACKEND_HOST`: Backend host
- `BACKEND_PORT`: Backend port
- `CITY_NAME`: Display name returned in route responses

## Installation

Install backend dependencies:

```bash
cd backend
pip install -r requirements.txt
```

If you run the bot separately from the project root and want to be safe, install the same dependencies there as well:

```bash
pip install -r backend/requirements.txt
```

## Running the project

### 1. Start the backend

From the project root:

```bash
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Or from inside the `backend` directory:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 2. Start the Telegram bot

From the project root:

```bash
python bot/bot.py
```

### 3. Open the API docs

After the backend starts, open:

```text
http://127.0.0.1:8000/docs
```

### 4. Optional frontend

You can open `frontend/index.html` directly in a browser, or serve it with a simple static file server.

## API endpoints

### Health

- `GET /health`

Returns a simple service status object.

### Geocoding

- `POST /api/geocode`

Example request:

```json
{
  "query": "Heydar Aliyev Center"
}
```

### Route generation

- `POST /api/route`

Example request:

```json
{
  "origin": { "lat": 40.4093, "lon": 49.8671 },
  "destination": { "lat": 40.4010, "lon": 49.8703 },
  "use_eco": true
}
```

### Additional endpoints

- `GET /api/weather`
- `GET /api/news`
- `GET /api/camera/status`

## Bot commands

- `/start` — starts the bot and shows the intro message
- `/route` — starts the route request flow
- `/health` — checks backend health from the bot side

## Known built-in place names

The geocoding service includes a small built-in lookup for common places such as:

- Heydar Aliyev Center
- Ganjlik Mall
- 20 Yanvar
- Koroglu
- Nizami Metro
- İçərişəhər / Icherisheher
- Airport

If a place is not found locally, the app attempts a fallback request to OpenStreetMap Nominatim.

## Example user flow

1. Run the backend
2. Run the Telegram bot
3. Open Telegram and start the bot
4. Send `/route`
5. Share your location
6. Send a destination such as:
   - `40.4010,49.8703`
   - `Heydar Aliyev Center`
7. Receive route suggestions with distance, duration, traffic level, and warnings

## Notes for development

- The current service layer uses **simulated data** for weather, news, camera status, and city open data.
- Routing is heuristic-based and is not yet connected to a real mapping engine.
- The frontend is currently only an informational placeholder.
- CORS is open to all origins, which is convenient for development but should be tightened for production.

## Suggested future improvements

- Integrate a real routing provider such as OSRM, GraphHopper, or Google Maps
- Replace simulated city signals with live APIs
- Add authentication and rate limiting
- Add persistent storage for trips and analytics
- Build a full frontend dashboard with map visualization
- Containerize the application with Docker
- Add automated tests and CI

## Troubleshooting

### Bot token error

If the bot fails on startup with a token-related error, check that:
- `.env` exists,
- `TELEGRAM_BOT_TOKEN` is set correctly,
- the token was copied exactly from BotFather.

### Bot cannot reach backend

Make sure:
- the backend is running,
- `PUBLIC_BASE_URL` points to the correct host and port,
- the `/health` endpoint is reachable.

### Geocoding fails

Try:
- entering coordinates directly,
- using one of the built-in place names,
- checking your network connection for the Nominatim fallback.

