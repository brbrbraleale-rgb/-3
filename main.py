import os
from datetime import datetime

import pandas as pd

# Импортируем функции из модулей в папке src
try:
    from src.reports import spending_by_category
    from src.services import get_cashback_categories
    from src.utils import filter_transactions, get_currency_rates, get_stock_prices, process_categories
except ImportError as e:
    print(f"Ошибка: {e}")



def main():
    # Путь к файлу (автоматически ищет в папке data в корне проекта)
    file_name = 'Operations Sun Mar 01 2026-Fri Mar 13 2026.xlsx'
    file_path = os.path.join('data', file_name)

    # Бесконечный цикл, чтобы программа не закрывалась после одного действия
    while True:
        print("\n" + "=" * 50)
        print("БАНКОВСКИЙ ПОМОЩНИК: ГЛАВНОЕ МЕНЮ")
        print("=" * 50)
        print("1. Главная (Курсы валют, акции, топ категорий)")
        print("2. Сервисы (Кешбэк по категориям за месяц)")
        print("3. Отчеты (Траты по категории за 3 месяца)")
        print("0. Выход")
        print("-" * 50)

        choice = input("Выберите пункт меню: ").strip()

        if choice == "0":
            print("Программа завершена. До свидания!")
            break

        # Проверка наличия файла перед выполнением команд
        if not os.path.exists(file_path):
            print(f"Ошибка: Файл не найден по пути: {file_path}")
            continue

        try:
            # ПУНКТ 1: ГЛАВНАЯ СТРАНИЦА
            if choice == "1":
                print("Программа: Загрузка данных и получение котировок...")
                df = pd.read_excel(file_path)

                # Приводим названия колонок к формату, который ждет модуль utils
                df_utils = df.rename(columns={
                    'Дата операции': 'date',
                    'Сумма операции': 'amount',
                    'Категория': 'category'
                })
                df_utils['date'] = pd.to_datetime(df_utils['date'], dayfirst=True)

                # Вызываем функции из utils.py
                # Фильтруем за месяц от текущей даты
                target_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                filtered = filter_transactions(df_utils, target_date, range_type='M')

                categories = process_categories(filtered)
                currencies = get_currency_rates()
                stocks = get_stock_prices()

                print("\n--- РЕЗУЛЬТАТ: ГЛАВНАЯ ---")
                print(f"Курсы валют: {currencies}")
                print(f"Цены акций: {stocks}")
                print(f"Топ категорий трат: {categories}")

            # ПУНКТ 2: СЕРВИСЫ (КЕШБЭК)
            elif choice == "2":
                try:
                    year = int(input("Введите год (например, 2026): "))
                    month = int(input("Введите месяц (1-12): "))
                    print(f"Анализирую кешбэк...")

                    # функция из services.py
                    result_json = get_cashback_categories(file_path, year, month)
                    print("\n--- КЕШБЭК ЗА ПЕРИОД ---")
                    print(result_json)
                except ValueError:
                    print("Ошибка: Год и месяц должны быть числами.")

            # ПУНКТ 3: ОТЧЕТЫ (ТРАТЫ ПО КАТЕГОРИЯМ)
            elif choice == "3":
                df = pd.read_excel(file_path)

                # Показываем доступные категории
                available_cats = df['Категория'].dropna().unique()
                print("\nДоступные категории в файле:")
                print(", ".join(available_cats))

                cat_name = input("\nВведите категорию: ").strip()
                date_input = input("Введите дату конца периода (ДД.ММ.ГГГГ) или Enter для текущей: ").strip()

                if not date_input:
                    date_input = datetime.now().strftime("%d.%m.%Y")

                # Поиск категории
                found_cat = next((c for c in available_cats if str(c).lower() == cat_name.lower()), None)

                if found_cat:
                    print(f"Генерирую отчет за 3 месяца до {date_input}...")
                    # функция из reports.py (с декоратором сохранения файла)
                    report = spending_by_category(df, found_cat, date_input)

                    if report == "[]":
                        print("За этот период операций по данной категории не найдено.")
                    else:
                        print("\n--- ОТЧЕТ ПО КАТЕГОРИИ ---")
                        print(report)
                        print("\n[!] Файл с отчетом создан в корне проекта.")
                else:
                    print(f"Ошибка: Категория '{cat_name}' не найдена.")

            else:
                print("Ошибка: Такого пункта меню нет.")

        except Exception as e:
            print(f"Произошла ошибка при выполнении: {e}")


if __name__ == "__main__":
    main()
