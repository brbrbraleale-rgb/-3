"""Модуль со вспомогательными функциями для обработки данных страницы События"""
import logging
import os

import pandas as pd
import requests
from dotenv import load_dotenv

# Загрузка ключей из файла .env
load_dotenv()
API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")

# Настройка логирования
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_currency_rates():
    """Получает курсы USD и EUR к рублю через ExchangeRate-API."""

    # берем ключ из переменных окружения внутри функции
    api_key = os.getenv("API_KEY")
    base_currency = "RUB"

    # Проверяем, что ключ загрузился, прежде чем делать запрос
    if not api_key:
        logger.error("КРИТИЧЕСКАЯ ОШИБКА: API_KEY не найден в .env!")
        return []

    # Используем локальную переменную api_key
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base_currency}"

    logger.info(f"Запрос курсов валют к {base_currency}")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("result") == "success":
            rates = data.get("conversion_rates", {})
            result = []
            for code in ["USD", "EUR"]:
                if code in rates:
                    # Расчет стоимости 1 единицы валюты в рублях
                    rate_to_rub = round(1 / rates[code], 2)
                    result.append({"currency": code, "rate": rate_to_rub})
            return result
        else:
            # Логируем тип ошибки от самого API
            logger.error(f"API вернул ошибку: {data.get('error-type')}")
            return []

    except Exception as e:
        logger.error(f"Ошибка при подключении к ExchangeRate-API: {e}")
        return []


def get_stock_prices():
    """Получает цены акций через внешний API."""
    logger.info("Запрос котировок акций")
    try:
        # Здесь реальный запрос requests, если появится API для акций
        return [
            {"stock": "AAPL", "price": 150.12},
            {"stock": "AMZN", "price": 3173.18},
            {"stock": "GOOGL", "price": 2742.39},
            {"stock": "MSFT", "price": 296.71},
            {"stock": "TSLA", "price": 1007.08}
        ]
    except Exception as e:
        logger.error(f"Ошибка API акций: {e}")
        return []


def filter_transactions(df, date_str, range_type):
    """Фильтрация данных pandas по дате и диапазону."""
    dt = pd.to_datetime(date_str)

    if range_type == 'W':
        start_date = dt - pd.Timedelta(days=dt.weekday())
    elif range_type == 'M':
        start_date = dt.replace(day=1)
    elif range_type == 'Y':
        start_date = dt.replace(month=1, day=1)
    elif range_type == 'ALL':
        start_date = df['date'].min() if not df.empty else dt
    else:
        # По умолчанию: с начала месяца по дату
        start_date = dt.replace(day=1)

    return df[(df['date'] >= start_date) & (df['date'] <= dt)]


def process_categories(df, limit=7):
    """Обработка категорий через pandas."""
    if df.empty:
        return []

    # Группировка и округление сумм
    grouped = df.groupby('category')['amount'].sum().abs().round().astype(int)
    grouped = grouped.sort_values(ascending=False).reset_index()

    if len(grouped) > limit:
        main = grouped.head(limit - 1)
        others_sum = grouped.iloc[limit - 1:]['amount'].sum()
        others = pd.DataFrame([{'category': 'Остальное', 'amount': others_sum}])
        grouped = pd.concat([main, others], ignore_index=True)

    return grouped.to_dict(orient='records')


