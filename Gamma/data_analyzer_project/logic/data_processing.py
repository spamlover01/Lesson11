# logic/data_processing.py
import pandas as pd
import os
from kivy.logger import Logger


def try_load_csv(filepath, delimiter=','):
    """
    Пытается загрузить CSV файл с разными кодировками.
    """
    encodings_to_try = ['cp1251', 'utf-8', 'iso-8859-5', None]
    for enc in encodings_to_try:
        try:
            Logger.info(
                f"DataProcessing: Попытка загрузки '{os.path.basename(filepath)}' с кодировкой: {enc}, разделитель: '{delimiter}'...")
            # Используем on_bad_lines='skip' для пропуска "плохих" строк
            return pd.read_csv(filepath, encoding=enc, delimiter=delimiter, on_bad_lines='skip')
        except UnicodeDecodeError:
            Logger.debug(f"DataProcessing: Ошибка UnicodeDecodeError с {enc} для файла {filepath}")
        except pd.errors.ParserError as e_parser:
            Logger.warning(f"DataProcessing: Ошибка ParserError с {enc}, разделитель '{delimiter}': {e_parser}")
        except FileNotFoundError:
            Logger.error(f"DataProcessing: Файл не найден: {filepath}")
            raise
        except Exception as e:
            Logger.error(f"DataProcessing: Общая ошибка с {enc}, разделитель '{delimiter}': {e}")
    return None


def filter_data_query1(df, filters):
    """
    Фильтрует DataFrame для Запроса 1, используя логическое 'И' для всех фильтров.
    """
    if df is None:
        return pd.DataFrame()  # Возвращаем пустой DataFrame

    # ИСПРАВЛЕНИЕ: Новая, надежная логика фильтрации
    try:
        # Начинаем с маски, где все строки разрешены
        mask = pd.Series(True, index=df.index)

        # Карта для сопоставления ключей из UI с именами колонок в DataFrame
        column_map = {
            'consumer': 'Потребитель',
            'address': 'Адрес',
            'pu_no': '№ ПУ',
            'contract': '№ Договора',
            'coeff': 'Коэфф',
            'file': 'Файл',
            'year': 'Год'
        }

        for key, col_name in column_map.items():
            filter_value = filters.get(key, '').strip()

            # Применяем фильтр только если в нем есть значение
            if filter_value and col_name in df.columns:
                # Специальная обработка для числовых полей
                if col_name in ['Год', 'Коэфф']:
                    try:
                        # Сначала конвертируем колонку в числовой формат, ошибки заменяем на NaN
                        numeric_column = pd.to_numeric(df[col_name], errors='coerce')
                        # Конвертируем значение фильтра в число
                        numeric_filter = float(
                            filter_value.replace(',', '.'))  # Заменяем запятую на точку для десятичных
                        # Применяем маску только для не-NaN значений
                        mask = mask & (numeric_column == numeric_filter)
                    except (ValueError, TypeError):
                        # Если значение фильтра не число, то этот фильтр не найдет совпадений
                        Logger.warning(
                            f"DataProcessing: Неверное числовое значение для фильтра '{col_name}': {filter_value}")
                        mask = pd.Series(False, index=df.index)  # Ни одна строка не подойдет
                else:  # Стандартная обработка для текстовых полей
                    mask = mask & (df[col_name].astype(str).str.lower().str.contains(filter_value.lower(), na=False))

        return df[mask]

    except Exception as e:
        Logger.error(f"DataProcessing: Критическая ошибка при фильтрации: {e}")
        return pd.DataFrame()  # Возвращаем пустой DataFrame в случае любой ошибки


def aggregate_for_grid(df):
    """
    Агрегирует отфильтрованные данные для сетки Год/Месяц.
    """
    if df is None or df.empty:
        return pd.Series(dtype='float64')

    required_cols = ['Год', 'Мес', 'Расход']
    if not all(col in df.columns for col in required_cols):
        Logger.warning(f"DataProcessing: Для агрегации отсутствуют необходимые колонки: {required_cols}")
        return pd.Series(dtype='float64')

    try:
        agg_df = df.copy()
        for col in required_cols:
            agg_df[col] = pd.to_numeric(agg_df[col], errors='coerce')

        agg_df.dropna(subset=required_cols, inplace=True)

        if agg_df.empty:
            Logger.info("DataProcessing: Нет данных для агрегации после очистки.")
            return pd.Series(dtype='float64')

        agg_df['Год'] = agg_df['Год'].astype(int)
        agg_df['Мес'] = agg_df['Мес'].astype(int)

        aggregated_data = agg_df.groupby(['Год', 'Мес'])['Расход'].sum()
        return aggregated_data
    except Exception as e:
        Logger.error(f"DataProcessing: Ошибка при агрегации данных: {e}")
        return pd.Series(dtype='float64')
