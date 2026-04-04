from __future__ import annotations

import os
from typing import Dict, Tuple

import httpx
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '').strip().strip('"').strip("'")
PUBLIC_BASE_URL = os.getenv('PUBLIC_BASE_URL', 'http://127.0.0.1:8000').rstrip('/')

if ':' not in TELEGRAM_BOT_TOKEN:
    raise RuntimeError('.env faylında TELEGRAM_BOT_TOKEN yoxdur və ya yanlışdır. BotFather tokenini düzgün daxil et.')

bot = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())


class RouteStates(StatesGroup):
    waiting_for_origin = State()
    waiting_for_destination = State()


LOCATION_KB = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Cari məkanı paylaş', request_location=True)]],
    resize_keyboard=True,
    one_time_keyboard=True,
)


def parse_coords(text: str) -> Tuple[float, float]:
    parts = [p.strip() for p in text.split(',', 1)]
    if len(parts) != 2:
        raise ValueError('Koordinatları bu formatda göndər: enlik,uzunluq')
    return float(parts[0]), float(parts[1])


async def geocode_destination(text: str) -> Tuple[float, float, str]:
    try:
        lat, lon = parse_coords(text)
        return lat, lon, f'{lat},{lon}'
    except Exception:
        pass

    async with httpx.AsyncClient(timeout=15.0) as client:
        res = await client.post(f'{PUBLIC_BASE_URL}/api/geocode', json={'query': text})
        res.raise_for_status()
        data = res.json()
        return data['result']['lat'], data['result']['lon'], data['formatted_address']


def format_routes(data: Dict) -> str:
    lines = [
        '<b>Marşrut təklifləri</b>',
        f"Şəhər: {data.get('city', '-')}",
        '',
    ]
    for i, route in enumerate(data.get('routes', []), start=1):
        lines.append(f'<b>{i}. {route["summary"]}</b>')
        lines.append(f"Məsafə: {route['distance_km']} km")
        lines.append(f"Müddət: {route['duration_min']} dəqiqə")
        lines.append(f"Tıxac səviyyəsi: {route['traffic_level']}")
        if route.get('warnings'):
            lines.append('Xəbərdarlıqlar:')
            for w in route['warnings']:
                lines.append(f'• {w}')
        lines.append('')
    return '\n'.join(lines).strip()


async def process_route_request(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    origin = data.get('origin')
    destination = data.get('destination')
    if not origin or not destination:
        await message.answer('Başlanğıc və ya təyinat nöqtəsi yoxdur. /route ilə yenidən başla.')
        return

    payload = {'origin': origin, 'destination': destination, 'use_eco': True}

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            res = await client.post(f'{PUBLIC_BASE_URL}/api/route', json=payload)
            res.raise_for_status()
            route_data = res.json()
        await message.answer(format_routes(route_data), reply_markup=ReplyKeyboardRemove())
        await state.clear()
    except httpx.ConnectError:
        await message.answer(
            'Backend-ə qoşulmaq olmur. Əvvəlcə FastAPI-ni işə sal və PUBLIC_BASE_URL düzgün olduğuna bax, məsələn: http://127.0.0.1:8000',
            reply_markup=ReplyKeyboardRemove(),
        )
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text[:300]
        await message.answer(
            f'Backend xəta qaytardı: {exc.response.status_code}\n{detail}',
            reply_markup=ReplyKeyboardRemove()
        )
    except Exception as exc:
        await message.answer(f'Gözlənilməz xəta baş verdi: {exc}', reply_markup=ReplyKeyboardRemove())


@dp.message(Command('start'))
async def start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        'Salam. Mən tıxac nəzərə alınmaqla marşrut təklifləri verə bilirəm.\n\nBaşlamaq üçün /route yaz.',
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(Command('route'))
async def route_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(RouteStates.waiting_for_origin)
    await message.answer('Zəhmət olmasa cari məkanını paylaş və ya başlanğıc nöqtəsini enlik,uzunluq formatında göndər.', reply_markup=LOCATION_KB)


@dp.message(RouteStates.waiting_for_origin, F.location)
async def receive_origin_location(message: Message, state: FSMContext) -> None:
    await state.update_data(origin={'lat': message.location.latitude, 'lon': message.location.longitude})
    await state.set_state(RouteStates.waiting_for_destination)
    await message.answer('İndi təyinat nöqtəsini enlik,uzunluq formatında və ya məkan adı kimi göndər.', reply_markup=ReplyKeyboardRemove())


@dp.message(RouteStates.waiting_for_origin, F.text)
async def receive_origin_text(message: Message, state: FSMContext) -> None:
    try:
        lat, lon = parse_coords(message.text.strip())
    except Exception:
        await message.answer('Başlanğıc nöqtəsi 40.4093,49.8671 kimi olmalıdır və ya məkan paylaşmalısan.', reply_markup=LOCATION_KB)
        return
    await state.update_data(origin={'lat': lat, 'lon': lon})
    await state.set_state(RouteStates.waiting_for_destination)
    await message.answer('İndi təyinat nöqtəsini enlik,uzunluq formatında və ya məkan adı kimi göndər.', reply_markup=ReplyKeyboardRemove())


@dp.message(RouteStates.waiting_for_destination, F.location)
async def receive_destination_location(message: Message, state: FSMContext) -> None:
    await state.update_data(destination={'lat': message.location.latitude, 'lon': message.location.longitude})
    await process_route_request(message, state)


@dp.message(RouteStates.waiting_for_destination, F.text)
async def receive_destination_text(message: Message, state: FSMContext) -> None:
    try:
        lat, lon, _formatted = await geocode_destination(message.text.strip())
        await state.update_data(destination={'lat': lat, 'lon': lon})
        await process_route_request(message, state)
    except httpx.ConnectError:
        await message.answer('Backend geocoding servisinə qoşulmaq olmur. Backend-in işlədiyini yoxla.')
    except httpx.HTTPStatusError:
        await message.answer('Təyinat nöqtəsi tapılmadı. Başqa məkan adı yaz və ya enlik,uzunluq formatında göndər.')
    except Exception as exc:
        await message.answer(f'Təyinat nöqtəsi emal olunmadı: {exc}')


@dp.message(Command('health'))
async def health_handler(message: Message) -> None:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(f'{PUBLIC_BASE_URL}/health')
            res.raise_for_status()
            data = res.json()
        await message.answer(f'Backend vəziyyəti: {data}')
    except Exception as exc:
        await message.answer(f'Backend health yoxlaması uğursuz oldu: {exc}')


@dp.message()
async def fallback_handler(message: Message) -> None:
    await message.answer('Marşrut təklifləri almaq üçün /route yaz.')


if __name__ == '__main__':
    import asyncio
    asyncio.run(dp.start_polling(bot))