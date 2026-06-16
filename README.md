# MarketplaceSync

[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
![Python 3.12](https://img.shields.io/badge/python-3.12-blue)

Забирает товары из публичного поиска Wildberries по ключевому слову,
группирует по категории и бренду, считает агрегаты (средняя/мин/макс цена) и
записывает итог в Google Sheets. Показывает работу с rate limiting через
tenacity (exponential backoff на 429) и построение пайплайна
fetch → group → export.

## Какое API используется

**Wildberries** — крупнейший маркетплейс России/СНГ. При поиске на сайте
браузер обращается к публичному endpoint:

```
GET https://search.wb.ru/exactmatch/ru/common/v5/search
    ?query=ноутбук&resultset=catalog&limit=100&sort=popular&page=1
```

Этот endpoint:
- **Не требует авторизации** — работает без ключей и регистрации
- Возвращает JSON с полями: id товара, название, бренд, категория, цена, скидка, рейтинг, количество отзывов
- **Лимиты**: официально не задокументированы; на практике стабильно работает при ≤1–2 req/s; при превышении возвращает 429

Ozon исключён: их search API требует регистрации продавца.

> **Ограничения**: это неофициальный публичный эндпоинт, не Seller API.
> Подробнее — в [секции ограничений](#ограничения) (Phase 3).

## Статус

- [x] Phase 1 — WB API client + tenacity retry
- [ ] Phase 2 — группировка + Google Sheets + CLI
- [ ] Phase 3 — CI + секция ограничений

## Стек

Python 3.12, httpx, tenacity, gspread, pytest.

## Быстрый старт

```bash
git clone https://github.com/flexxrap/marketplace-sync.git
cd marketplace-sync
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Тесты

```bash
pip install -r requirements-dev.txt
pytest
```

HTTP-запросы в тестах замоканы через `unittest.mock` — реальный доступ к WB API
не нужен. Тест `test_get_products_retries_on_429` подаёт два 429 подряд и
проверяет, что клиент успешно завершает запрос на третьей попытке.
