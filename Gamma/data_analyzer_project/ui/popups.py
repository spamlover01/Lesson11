# ui/popups.py
from kivy.uix.popup import Popup
import os

class FileChooserPopup(Popup):
    """
    Попап для выбора CSV файла.
    Обязателен атрибут `on_file_selected_callback`.
    """
    def select_file(self, path, selection):
        if selection:
            filepath = os.path.join(path, selection[0])
            if hasattr(self, 'on_file_selected_callback') and callable(self.on_file_selected_callback):
                self.on_file_selected_callback(filepath)
            else:
                print("FileChooserPopup: callback не установлен или не вызываемый.")
            self.dismiss()
        else:
            print("FileChooserPopup: файл не выбран.")

class SQLQuerySettingsPopup(Popup):
    """
    Попап для ввода/редактирования SQL-запросов.
    Использует app.sql_query1_text и app.sql_query2_text.
    Сохраняется через app.save_sql_queries.
    """
    pass
