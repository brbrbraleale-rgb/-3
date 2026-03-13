import pytest
import pandas as pd
import json
from unittest.mock import patch
from src.views import events_page


@pytest.fixture
def transactions_df():
    """Фикстура для создания тестового DataFrame."""
    data = [
        {'date': '2026-10-01', 'category': 'Супермаркеты', 'amount': -5000.0},
        {'date': '2026-10-05', 'category': 'Наличные', 'amount': -1000.0},
        {'date': '2026-10-10', 'category': 'Зарплата', 'amount': 50000.0},
    ]
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    return df


# Тест основной структуры JSON (используем patch )
@patch('src.views.get_currency_rates')
@patch('src.views.get_stock_prices')
def test_events_page_structure(mock_stocks, mock_currency, transactions_df):
    """Проверяет наличие всех ключей в итоговом JSON."""
    # Задаем данные для API
    mock_currency.return_value = [{"currency": "USD", "rate": 75.0}]
    mock_stocks.return_value = [{"stock": "AAPL", "price": 150.0}]

    # Вызываем функцию
    result_json = events_page(transactions_df, "2026-10-15", "M")
    result = json.loads(result_json)

    # Проверки (Assertions)
    assert "expenses" in result
    assert "income" in result
    assert "currency_rates" in result
    assert "stock_prices" in result
    assert result["expenses"]["total_amount"] == 6000  # 5000 + 1000


# Параметризованный тест фильтрации в views
@pytest.mark.parametrize("range_type, expected_income", [
    ('M', 50000),  # Октябрь
    ('ALL', 50000)
])
@patch('src.views.get_currency_rates')
@patch('src.views.get_stock_prices')
def test_events_page_filtering(mock_stocks, mock_currency, transactions_df, range_type, expected_income):
    """Проверяет корректность сумм при разных значениях."""
    mock_currency.return_value = []
    mock_stocks.return_value = []

    result_json = events_page(transactions_df, "2026-10-15", range_type)
    result = json.loads(result_json)

    assert result["income"]["total_amount"] == expected_income


# Тест разделения на основные расходы и переводы
@patch('src.views.get_currency_rates')
@patch('src.views.get_stock_prices')
def test_expenses_separation(mock_stocks, mock_currency, transactions_df):
    """Проверяет, что 'Наличные' попали в нужный раздел."""
    mock_currency.return_value = []
    mock_stocks.return_value = []

    result_json = events_page(transactions_df, "2026-10-15", "M")
    result = json.loads(result_json)

    # 'Супермаркеты' (5000) — в main, 'Наличные' (1000) — в transfers_and_cash
    assert result["expenses"]["main"][0]["category"] == "Супермаркеты"
    assert result["expenses"]["transfers_and_cash"][0]["category"] == "Наличные"