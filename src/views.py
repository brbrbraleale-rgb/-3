"""Главная функция JSON-ответа для страницы События."""
import json

import pandas as pd

from .utils import filter_transactions, get_currency_rates, get_stock_prices, process_categories


def events_page(df, date_str, range_type=None):
    """ функция формирования JSON-ответа для страницы События."""

    # Фильтруем данные
    period_df = filter_transactions(df, date_str, range_type)

    # Разделяем расходы и поступления
    expenses_df = period_df[period_df['amount'] < 0]
    income_df = period_df[period_df['amount'] > 0]

    #Выделяем переводы и наличные
    is_transfer_or_cash = expenses_df['category'].isin(['Наличные', 'Переводы'])
    main_expenses = expenses_df[~is_transfer_or_cash]
    transfers_cash = expenses_df[is_transfer_or_cash]

    #Формируем
    response = {
        "expenses": {
            "total_amount": int(expenses_df['amount'].abs().sum()),
            "main": process_categories(main_expenses),
            "transfers_and_cash": process_categories(transfers_cash)
        },
        "income": {
            "total_amount": int(income_df['amount'].sum()),
            "main": process_categories(income_df)
        },
        "currency_rates": get_currency_rates(),
        "stock_prices": get_stock_prices()
    }

    # Возвращаем JSON-строку
    return json.dumps(response, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    # Пример тестовых данных
    test_data = pd.DataFrame([
        {'date': '2023-10-01', 'category': 'Супермаркеты', 'amount': -5000.45},
        {'date': '2023-10-05', 'category': 'Наличные', 'amount': -1000},
        {'date': '2023-10-10', 'category': 'Зарплата', 'amount': 50000},
    ])
    test_data['date'] = pd.to_datetime(test_data['date'])

    print(events_page(test_data, "2023-10-15", "M"))
