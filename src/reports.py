"""Модуль для формирования отчетов по транзакциям."""
import json
import logging
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Optional

import pandas as pd

# Настройка логирования
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def save_report_to_file(filename: Optional[str] = None) -> Callable:
    """Декоратор для записи результата в файл"""

    def decorator(func: Callable) -> Callable:
        """Внутренняя функция декоратора для получения функции-цели"""
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> str:
            """Обертка, которая выполняет функцию и сохраняет её результат в файл"""
            result = func(*args, **kwargs)
            report_file = filename if filename else f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(result)
            logger.info(f"Отчет успешно записан в файл: {report_file}")
            return result

        return wrapper

    return decorator


@save_report_to_file()
def spending_by_category(transactions: pd.DataFrame,
                         category: str,
                         date: Optional[str] = None) -> str:
    """Возвращает траты по категории за последние 3 месяца из DataFrame."""
    logger.info(f"Генерация отчета по категории: {category}")

    # Определяем конечную дату
    end_date = pd.to_datetime(date, dayfirst=True) if date else datetime.now()

    # Определяем начало периода (3 месяца назад)
    start_date = end_date - pd.DateOffset(months=3)

    # Фильтруем данные
    # Проверяем, что колонка с датой в правильном формате
    transactions['Дата операции'] = pd.to_datetime(transactions['Дата операции'], dayfirst=True)

    filtered_df = transactions[
        (transactions['Категория'] == category) &
        (transactions['Дата операции'] >= start_date) &
        (transactions['Дата операции'] <= end_date)
        ]

    # Формируем JSON (ориентируемся на колонку 'Сумма операции' из указанного файла)
    report_data = filtered_df.to_dict(orient='records')
    return json.dumps(report_data, ensure_ascii=False, indent=4, default=str)


if __name__ == "__main__":
    import os

    # Находим путь к текущему файлу (reports.py)
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Поднимаемся на уровень выше в корень проекта
    project_root = os.path.dirname(current_dir)

    # Собираем правильный путь к файлу в папке data
    file_name = 'Operations Sun Mar 01 2026-Fri Mar 13 2026.xlsx'
    full_path = os.path.join(project_root, 'data', file_name)

    try:
        # Загружаем данные из правильного места
        full_df = pd.read_excel(full_path)

        # Вызываем функцию отчета
        report = spending_by_category(full_df, "Аптеки", "13.03.2026")

        print("Результат отчета по реальным данным:")
        print(report)

    except FileNotFoundError:
        print(f"Ошибка: Файл не найден по пути: {full_path}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
