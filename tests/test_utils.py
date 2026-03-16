"""Тесты для модуля utils.py"""
from unittest.mock import patch

import pandas as pd
import pytest

# Импортируем напрямую из файла
from src.utils import filter_transactions, get_currency_rates, process_categories


@pytest.fixture
def sample_df():
    """Фикстура для создания тестового DataFrame."""
    data = [
        {'date': '2026-10-01', 'category': 'Супермаркеты', 'amount': -5000.0},
        {'date': '2026-10-05', 'category': 'Наличные', 'amount': -1000.0},
        {'date': '2026-09-20', 'category': 'Зарплата', 'amount': 50000.0},
    ]
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    return df

@pytest.mark.parametrize("range_type, expected_count", [
    ('M', 2),    # Октябрь (2 записи)
    ('ALL', 3),  # Все записи
])
def test_filter_transactions(sample_df, range_type, expected_count):
    """Параметризованный тест фильтрации."""
    result = filter_transactions(sample_df, "2026-10-15", range_type)
    assert len(result) == expected_count

def test_process_categories(sample_df):
    """Тест группировки категорий."""
    expenses = sample_df[sample_df['amount'] < 0]
    result = process_categories(expenses)
    assert len(result) > 0
    # Проверка, что сумма стала целым числом (int) по ТЗ
    assert isinstance(result[0]['amount'], int)

@patch('requests.get')
def test_get_currency_rates(mock_get):
    """Тест API с использованием Mock."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "result": "success",
        "conversion_rates": {"USD": 0.012, "EUR": 0.011}
    }
    rates = get_currency_rates()
    assert len(rates) == 2
    assert rates[0]['currency'] == 'USD'


