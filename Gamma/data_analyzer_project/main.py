# main.py (обновлено с вызовом populate_filter_options)
import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.logger import Logger
from kivy.metrics import dp

import os

from logic.data_processing import try_load_csv, filter_data_query1, aggregate_for_grid
from logic.ui_helpers import (
    build_year_month_grid, update_year_month_grid, update_charts,
    update_status_label, update_data_table_display, get_filters_from_ui,
    populate_filter_options
)

from ui.loginscreen import LoginScreen
from ui.adminapplayout import AdminAppLayout
from ui.popups import FileChooserPopup, SQLQuerySettingsPopup
from ui.filter_input import FilterInput

kivy.require('2.1.0')
Window.clearcolor = (1, 1, 1, 1)

DEFAULT_SQL_QUERY_1 = "-- Введите SQL Запрос 1 здесь"
DEFAULT_SQL_QUERY_2 = "-- Введите SQL Запрос 2 здесь"

class DataAnalyzerApp(App):
    df_query1 = None
    df_query2 = None
    sql_query1_text = DEFAULT_SQL_QUERY_1
    sql_query2_text = DEFAULT_SQL_QUERY_2
    current_user_role = None

    login_screen_instance = None
    admin_app_layout_instance = None

    file_dropdown = None
    admin_dropdown = None

    YEARS_TO_DISPLAY = [2020, 2021, 2022, 2023, 2024, 2025]

    def build(self):
        for kv_file in ['dataanalyzer.kv', 'popups.kv', 'filter_input.kv', 'loginscreen.kv', 'adminapplayout.kv']:
            try:
                Builder.load_file(f'kv/{kv_file}')
            except Exception as e:
                Logger.error(f"DataAnalyzerApp: Ошибка загрузки {kv_file}: {e}")

        self.main_layout = BoxLayout(orientation='vertical')
        self.setup_dropdowns()
        self.show_login_screen()
        return self.main_layout

    def setup_dropdowns(self):
        self.file_dropdown = DropDown()
        for label, callback in [
            ('Загрузить CSV (Таблица 1)', self.load_csv_query1),
            ('Загрузить CSV (Таблица 2)', self.load_csv_query2),
            ('Выход', self.stop)
        ]:
            btn = Button(text=label, size_hint_y=None, height=44)
            btn.bind(on_release=(lambda cb: lambda btn: self.open_file_chooser(cb))(callback))
            self.file_dropdown.add_widget(btn)

        self.admin_dropdown = DropDown()
        admin_actions = [
            ('Обновить "мастер-файл" (Админ)', self.update_master_data_file),
            ('Настройки SQL-запросов (Админ)', self.open_sql_query_settings_popup)
        ]
        for label, callback in admin_actions:
            btn = Button(text=label, size_hint_y=None, height=44)
            btn.bind(on_release=callback)
            self.admin_dropdown.add_widget(btn)

    def show_login_screen(self):
        self.main_layout.clear_widgets()
        self.login_screen_instance = LoginScreen()
        self.main_layout.add_widget(self.login_screen_instance)
        Window.set_title("Анализатор данных - Вход")

    def show_admin_app_layout(self):
        self.main_layout.clear_widgets()
        self.admin_app_layout_instance = AdminAppLayout()
        self.main_layout.add_widget(self.admin_app_layout_instance)
        Window.set_title(f"Анализатор данных (Пользователь: {self.current_user_role})")
        self.reset_ui_to_default()

    def check_credentials(self, username, password):
        mock_users = {
            "": ("", "Администратор"),
            "manager": ("manager123", "Менеджер"),
            "user": ("user123", "Пользователь")
        }
        if username in mock_users and mock_users[username][0] == password:
            self.current_user_role = mock_users[username][1]
            if self.login_screen_instance:
                self.login_screen_instance.display_error('')
            self.show_admin_app_layout()
        else:
            if self.login_screen_instance:
                self.login_screen_instance.display_error('Неверное имя пользователя или пароль!')

    def open_file_chooser(self, callback_on_selection):
        popup = FileChooserPopup()
        path = os.path.join(os.path.expanduser('~'), 'Desktop')
        filechooser = popup.ids.get('filechooser')
        filechooser.path = path if os.path.exists(path) else os.path.expanduser('~')
        popup.on_file_selected_callback = callback_on_selection
        popup.open()

    def open_sql_query_settings_popup(self, instance):
        if self.current_user_role != "Администратор":
            self.show_error_popup("Доступ запрещен", "Только администратор может изменять SQL-запросы.")
            return
        SQLQuerySettingsPopup().open()

    def load_csv_query1(self, filepath):
        self.reset_ui_to_default()
        try:
            self.df_query1 = try_load_csv(filepath, delimiter=';')
            if self.df_query1 is not None:
                update_status_label(self.admin_app_layout_instance.ids.get('year_month_status_label'),
                                    f"Файл {os.path.basename(filepath)} загружен. Примените фильтры.")
                populate_filter_options(self)
            else:
                self.show_error_popup("Ошибка загрузки", f"Не удалось прочитать файл:\n{os.path.basename(filepath)}")
        except Exception as e:
            self.show_error_popup("Ошибка", str(e))

    def load_csv_query2(self, filepath):
        update_data_table_display(
            self.admin_app_layout_instance.ids.get('data_table_query2_content'),
            None, clear_on_load=True
        )
        try:
            self.df_query2 = try_load_csv(filepath, delimiter=';')
            update_data_table_display(
                self.admin_app_layout_instance.ids.get('data_table_query2_content'),
                self.df_query2, filename=os.path.basename(filepath)
            )
        except Exception as e:
            self.show_error_popup("Ошибка", str(e))

    def apply_filters_query1(self, instance=None):
        if self.df_query1 is None:
            self.show_error_popup("Данные не загружены", "Загрузите CSV файл для Таблицы 1.")
            return

        update_status_label(self.admin_app_layout_instance.ids.get('year_month_status_label'), "Идет обработка...")

        filters = get_filters_from_ui(self.admin_app_layout_instance.ids)
        if not any(filters.values()):
            self.reset_ui_to_default()
            update_status_label(self.admin_app_layout_instance.ids.get('year_month_status_label'),
                                "Фильтры не применены (все поля пустые).")
            return

        filtered_df = filter_data_query1(self.df_query1, filters)
        aggregated_data = aggregate_for_grid(filtered_df)

        update_year_month_grid(aggregated_data, self.admin_app_layout_instance.cell_widgets)
        update_charts(
            aggregated_data,
            filtered_df,
            {
                1: self.admin_app_layout_instance.ids.get('chart_image_1'),
                2: self.admin_app_layout_instance.ids.get('chart_image_2'),
                3: self.admin_app_layout_instance.ids.get('chart_image_3')
            }
        )

        update_status_label(
            self.admin_app_layout_instance.ids.get('year_month_status_label'),
            f"Данные отображены. Найдено строк (до агрегации): {len(filtered_df)}"
            if not aggregated_data.empty else "По заданным фильтрам данные не найдены."
        )

    def reset_filters_query1(self, instance=None):
        for f_id in ['filter_consumer', 'filter_address', 'filter_pu_no', 'filter_contract',
                     'filter_coeff', 'filter_file', 'filter_year']:
            widget = self.admin_app_layout_instance.ids.get(f_id)
            if widget:
                widget.text = ''
        self.reset_ui_to_default()

    def reset_ui_to_default(self):
        layout = self.admin_app_layout_instance

        layout.cell_widgets = {}
        build_year_month_grid(
            layout.ids.get('year_month_grid_container'),
            self.YEARS_TO_DISPLAY,
            layout.cell_widgets
        )

        update_charts(None, None, {
            1: layout.ids.get('chart_image_1'),
            2: layout.ids.get('chart_image_2'),
            3: layout.ids.get('chart_image_3')
        })

        update_status_label(layout.ids.get('year_month_status_label'),
                            "Примените фильтры для отображения данных.")

    def save_sql_queries(self, query1, query2):
        self.sql_query1_text = query1
        self.sql_query2_text = query2
        Logger.info("SQL-запросы обновлены (временно в памяти).")

    def update_master_data_file(self, instance):
        if self.current_user_role != "Администратор":
            self.show_error_popup("Доступ запрещен", "Это действие доступно только администратору.")
            return
        self.open_file_chooser(self.load_csv_query1)

    def show_error_popup(self, title, message):
        content = Label(text=str(message), halign='center', valign='middle',
                        text_size=(Window.width * 0.7, None))
        content.bind(size=content.setter('text_size'))
        Popup(title=str(title), content=content, size_hint=(0.8, None), height=dp(200), auto_dismiss=True).open()

    def switch_tab(self, tab_name):
        """
        Переключение между экранами. Управляет видимостью и стилем кнопок.
        """
        valid_tabs = ['overview', 'table1', 'table2', 'compare', 'reports']
        if tab_name not in valid_tabs:
            Logger.warning(f"Неизвестная вкладка: {tab_name}")
            return

        layout = self.admin_app_layout_instance
        if not layout:
            return

        for name in valid_tabs:
            screen = layout.ids.get(f"screen_{name}")
            button = layout.ids.get(f"tabbtn_{name}")
            if screen:
                screen.opacity = 1 if name == tab_name else 0
                screen.disabled = name != tab_name
            if button:
                if name == tab_name:
                    button.background_color = (0, 0, 0, 1)
                    button.color = (1, 1, 1, 1)
                else:
                    button.background_color = (0.85, 0.85, 0.85, 1)
                    button.color = (0, 0, 0, 1)


if __name__ == '__main__':
    DataAnalyzerApp().run()
