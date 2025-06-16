# logic/ui_helpers.py
from kivy.metrics import dp
from kivy.uix.label import Label
from kivy.core.image import Image as CoreImage
from kivy.logger import Logger
from logic.chart_generator import (
    create_dynamic_consumption_chart,
    create_monthly_comparison_chart,
    create_yearly_sum_chart
)

MONTH_NAMES = ["янв", "фев", "мар", "апр", "май", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"]


def build_year_month_grid(layout, years, cell_widgets_dict):
    if not layout:
        return

    layout.clear_widgets()
    layout.cols = len(years) + 1
    layout.add_widget(Label(text="Мес/Год", size_hint=(None, None), size=(dp(70), dp(25)), bold=True))

    for year in years:
        layout.add_widget(Label(text=str(year), size_hint=(None, None), size=(dp(60), dp(25)), bold=True))

    for i, month_name in enumerate(MONTH_NAMES):
        layout.add_widget(Label(text=month_name, size_hint=(None, None), size=(dp(70), dp(25))))
        for year in years:
            cell_id = f"cell_{year}_{i + 1}"
            label = Label(text="-", size_hint=(None, None), size=(dp(60), dp(25)), shorten=True)
            cell_widgets_dict[cell_id] = label
            layout.add_widget(label)


def update_year_month_grid(data_series, cell_widgets):
    for cell in cell_widgets.values():
        cell.text = "-"

    if data_series is not None and not data_series.empty:
        for (year, month), value in data_series.items():
            if 1 <= month <= 12:
                widget = cell_widgets.get(f"cell_{year}_{month}")
                if widget:
                    widget.text = str(int(value))

def populate_filter_options(app):
    """Заполняет фильтры уникальными значениями из df_query1"""
    if app.df_query1 is None or not app.admin_app_layout_instance:
        return

    filter_map = {
        'filter_consumer': 'Потребитель',
        'filter_address': 'Адрес',
        'filter_pu_no': '№ ПУ',
        'filter_contract': '№ Договора',
        'filter_coeff': 'Коэфф',
        'filter_file': 'Файл',
        'filter_year': 'Год'
    }

    for widget_id, column_name in filter_map.items():
        widget = app.admin_app_layout_instance.ids.get(widget_id)
        if widget and column_name in app.df_query1.columns:
            try:
                values = app.df_query1[column_name].dropna().unique().tolist()
                widget.options = values
            except Exception as e:
                Logger.warning(f"Ошибка фильтра {column_name}: {e}")

def update_charts(agg_data, filtered_df, chart_widgets):
    chart_map = {
        1: (agg_data, create_dynamic_consumption_chart),
        2: (filtered_df, create_monthly_comparison_chart),
        3: (filtered_df, create_yearly_sum_chart)
    }

    for idx, (data, gen) in chart_map.items():
        widget = chart_widgets.get(idx)
        if not widget or not gen:
            continue
        try:
            buf = gen(data)
            if buf:
                widget.texture = CoreImage(buf, ext='png').texture
            else:
                widget.texture = None
        except Exception as e:
            Logger.error(f"UIHelpers: Ошибка в генерации графика {idx}: {e}")


def update_status_label(widget, text):
    if widget:
        widget.text = text


def update_data_table_display(label_widget, df, filename=None, error_message=None, clear_on_load=False):
    if label_widget:
        if error_message:
            label_widget.text = f"[color=ff0000]{error_message}[/color]"
        elif clear_on_load:
            label_widget.text = "Данные для Таблицы 2 не загружены."
        elif df is not None:
            label_widget.text = f"Загружен файл: {filename}\n" + df.head(10).to_string()


def get_filters_from_ui(ids_dict):
    filters = {}
    for f_id in [
        'filter_consumer', 'filter_address', 'filter_pu_no',
        'filter_contract', 'filter_coeff', 'filter_file', 'filter_year']:
        widget = ids_dict.get(f_id)
        if widget:
            key = f_id.replace("filter_", "")
            filters[key] = widget.text
    return filters
