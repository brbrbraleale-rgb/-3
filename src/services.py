"""Функции основного анализа данных сервисов"""
import json
import logging
#from datetime import datetime

import pandas as pd

# Настройка логирования
logger = logging.getLogger(__name__)
# Установим базовую конфигурацию, если она не задана в файле
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_cashback_categories(data_excel: str, year: int, month: int) -> str:
    """
    Анализирует Excel-файл и возвращает JSON с суммами кэшбэка по категориям
    за указанный месяц и год.
    """
    logger.info(f"Начало анализа кэшбэка по файлу: {data_excel}")

    try:
        # Читаем .xlsx файл
        df = pd.read_excel(data_excel)

        # Преобразуем колонку с датой. Параметр day first =True для формата ДД.ММ.ГГГГ
        df['Дата операции'] = pd.to_datetime(df['Дата операции'], dayfirst=True)

        # Функциональный подход: фильтруем датафрейм по году и месяцу
        filtered_df = df[
            df['Дата операции'].apply(lambda x: x.year == year and x.month == month)
        ].copy()

        if filtered_df.empty:
            logger.warning(f"За период {month:02d}.{year} транзакций не найдено.")
            return json.dumps({}, ensure_ascii=False)

        # Очистка: заменяем пустые значения в кэшбэке на 0
        filtered_df['Кэшбэк'] = filtered_df['Кэшбэк'].fillna(0)

        # Группируем по категории и суммируем кэшбэк
        # Приобразуем результат в словарь
        category_cashback = filtered_df.groupby('Категория')['Кэшбэк'].sum().to_dict()

        # Оставляем только те категории, где кэшбэк больше 0
        result = {
            category: int(amount)
            for category, amount in category_cashback.items()
            if amount > 0
        }

        logger.info("Анализ успешно завершен.")
        return json.dumps(result, ensure_ascii=False, indent=4)

    except Exception as e:
        logger.error(f"Ошибка при обработке Excel: {e}")
        return json.dumps({"error": "Ошибка при чтении данных"}, ensure_ascii=False)


import os

if __name__ == "__main__":
    # Определяем путь к папке проекта (на уровень выше текущей папки src)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Собираем полный путь к файлу
    file_name = 'Operations Sun Mar 01 2026-Fri Mar 13 2026.xlsx'
    full_path = os.path.join(project_root, 'data', file_name)
    # Если файла нет в папке data, а он просто в корне, удали 'data' выше

    # Если не знаем, где файл, попробуем найти его в корне:
    if not os.path.exists(full_path):
        full_path = os.path.join(project_root, file_name)

    print(get_cashback_categories(full_path, 2026, 3))




