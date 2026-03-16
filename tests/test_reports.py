"""реализованы тесты для функций отчётностей"""
import json
from unittest.mock import mock_open, patch

import pandas as pd
import pytest

from src.reports import spending_by_category


# Фикстура для создания тестового DataFrame
@pytest.fixture
def transactions_df():
    """Создает тестовые данные, аналогичные структуре Excel."""
    return pd.DataFrame([
        {"Дата операции": "10.03.2026", "Категория": "Аптеки", "Сумма": 1000},
        {"Дата операции": "10.01.2026", "Категория": "Аптеки", "Сумма": 500},
        {"Дата операции": "10.10.2025", "Категория": "Аптеки", "Сумма": 300},  # Вне диапазона (3 мес)
        {"Дата операции": "10.03.2026", "Категория": "Супермаркеты", "Сумма": 2000},
    ])


# Параметризованный тест
@pytest.mark.parametrize("category, date, expected_count", [
    ("Аптеки", "15.03.2026", 2),  # Находит 2 операции за последние 3 месяца
    ("Супермаркеты", "15.03.2026", 1),  # Находит 1 операцию
    ("Транспорт", "15.03.2026", 0),  # Категория отсутствует
])
def test_spending_by_category_logic(category, date, expected_count, transactions_df):
    """
    Тестирует логику фильтрации по категории и датам.
    Использует mock_open, чтобы декоратор не создавал реальный файл.
    """
    # Патчим 'builtins.open', чтобы декоратор @save_report_to_file писал в "виртуальный" файл
    with patch("builtins.open", mock_open()) as mocked_file:
        # Вызываем функцию
        result_json = spending_by_category(transactions_df, category, date)
        result_data = json.loads(result_json)

        # Проверяем количество найденных записей
        assert len(result_data) == expected_count

        # Проверяем, что декоратор пытался вызвать запись в файл
        mocked_file.assert_called()


def test_spending_by_category_no_date(transactions_df):
    """Тест работы функции без передачи даты (берется текущая)."""
    with patch("builtins.open", mock_open()):
        # Просто проверяем, что функция не падает и возвращает строку JSON
        result = spending_by_category(transactions_df, "Аптеки")
        assert isinstance(result, str)
        assert "[]" in result or "[" in result  # Должен вернуть список в формате JSON

