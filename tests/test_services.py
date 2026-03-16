"""Модуль для тестирования функций сервиса анализа кэшбэка."""

import json
from unittest.mock import patch

import pandas as pd
import pytest

from src.services import get_cashback_categories


@pytest.fixture
def mock_transaction_data():
    """Фикстура, создающая тестовый датафрейм с транзакциями."""
    return pd.DataFrame([
        {"Дата операции": "01.03.2026", "Категория": "Аптеки", "Кэшбэк": 100},
        {"Дата операции": "05.03.2026", "Категория": "Аптеки", "Кэшбэк": 50},
        {"Дата операции": "10.03.2026", "Категория": "Супермаркеты", "Кэшбэк": 200},
        {"Дата операции": "15.02.2026", "Категория": "Фастфуд", "Кэшбэк": 300},
    ])


@pytest.mark.parametrize("year, month, expected", [
    (2026, 3, {"Аптеки": 150, "Супермаркеты": 200}),
    (2026, 2, {"Фастфуд": 300}),
    (2026, 1, {})
])
def test_get_cashback_categories(year, month, expected, mock_transaction_data):
    """Тестирует фильтрацию и суммирование кэшбэка по категориям."""
    with patch("pandas.read_excel") as mock_read:
        mock_read.return_value = mock_transaction_data

        result_json = get_cashback_categories("fake_path.xlsx", year, month)
        result_dict = json.loads(result_json)

        assert result_dict == expected
