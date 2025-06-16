# ui/loginscreen.py
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.logger import Logger

class LoginScreen(BoxLayout):
    """
    Экран авторизации.
    Ввод логина и пароля, с проверкой через app.check_credentials.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self._link_focus_inputs, 0.1)

    def _link_focus_inputs(self, dt):
        username_ti = self.ids.get('username_input')
        password_ti = self.ids.get('password_input')
        if username_ti and password_ti:
            username_ti.focus_next = password_ti
            password_ti.focus_previous = username_ti
            Logger.info("LoginScreen: Навигация по фокусу установлена.")
            username_ti.focus = True
        else:
            missing = [name for name, obj in [('username_input', username_ti), ('password_input', password_ti)] if not obj]
            Logger.warning(f"LoginScreen: Не найдены ID: {', '.join(missing)}")

    def display_error(self, message):
        error_label = self.ids.get('error_message_label')
        if error_label:
            error_label.text = message
        else:
            Logger.warning("LoginScreen: error_message_label не найден в ids.")