# Шаг 1: Обновление FilterInput (ограничение списка, автоподсказки с 3 символов)
# Шаг 2: Уплотнение таблицы "Месяц/Год"

# Изменения в классе FilterInput:

from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ListProperty, ObjectProperty, NumericProperty
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.button import Button
from kivy.uix.recycleview import RecycleView
from kivy.uix.dropdown import DropDown
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.factory import Factory

class SelectableButton(RecycleDataViewBehavior, Button):
    index = None
    owner = ObjectProperty(None)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.text = data.get('text', '')
        self.owner = data.get('owner')
        return super().refresh_view_attrs(rv, index, data)

    def on_release(self):
        if self.owner:
            self.owner.select_option(self.text)

class FilterInput(BoxLayout):   #ограничевую по количеству символов и активируется с min_chars_to_search символов
    text = StringProperty('')
    hint_text = StringProperty('')
    options = ListProperty([])
    app = ObjectProperty(None)
    min_chars_to_search = NumericProperty(3)
    max_visible_items = NumericProperty(15)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dropdown = None
        self.rv = None
        self._is_selecting = False

    def on_options(self, instance, value):
        if self.rv:
            sorted_options = sorted(map(str, value))
            self.rv.data = [{'text': opt, 'owner': self} for opt in sorted_options[:self.max_visible_items]]

    def open_dropdown(self, text_input):
        if self._is_selecting:
            self._is_selecting = False
            return

        if not self.dropdown:
            self.rv = Factory.RV()
            self.dropdown = DropDown()
            self.dropdown.add_widget(self.rv)
            self.dropdown.bind(on_dismiss=lambda _: setattr(text_input, 'focus', False))

        current_text = text_input.text
        if len(current_text) >= self.min_chars_to_search:
            self.filter_and_show(text_input, current_text)
        else:
            data = [{'text': str(opt), 'owner': self} for opt in self.options[:self.max_visible_items]]
            self.update_rv_data(text_input, data)

    def on_text_input(self, text_input, text):
        self.text = text
        if self._is_selecting:
            return
        if not self.dropdown:
            self.open_dropdown(text_input)

        if len(text) < self.min_chars_to_search:
            if self.dropdown.parent:
                self.dropdown.dismiss()
            return

        filtered_data = self._get_filtered_data(text)
        self.update_rv_data(text_input, filtered_data)

    def update_rv_data(self, text_input, data):    #усекаем список до *НАДО УТОЧНИТЬ
        if not self.dropdown or not self.rv:
            return

        visible_items = min(len(data), self.max_visible_items)
        if visible_items == 0:
            if self.dropdown.parent:
                self.dropdown.dismiss()
            return

        row_height = dp(44)
        dropdown_height = min(dp(300), visible_items * row_height)
        self.rv.data = data[:self.max_visible_items]
        self.rv.height = dropdown_height
        self.dropdown.height = dropdown_height

        if not self.dropdown.parent:
            self.dropdown.open(text_input)

    def _get_filtered_data(self, text):
        text_lower = text.lower()
        filtered = [opt for opt in self.options if text_lower in str(opt).lower()]
        return [{'text': str(opt), 'owner': self} for opt in filtered[:self.max_visible_items]]

    def select_option(self, selected_text):
        self._is_selecting = True
        text_input = self.ids.get('text_input')
        if text_input:
            text_input.text = selected_text
            self.text = selected_text
            text_input.focus = False

        if self.dropdown:
            self.dropdown.dismiss()

        Clock.schedule_once(lambda dt: setattr(self, '_is_selecting', False), 0.2)
        Clock.schedule_once(lambda dt: self.app.apply_filters_query1(), 0.1)

# Изменение в методе build_year_month_grid в main.py:
# Ячейки фиксированного размера, без прокрутки, с укороченным текстом


# Аналогично для всех остальных Label внутри таблицы
# Можно также добавить стилизацию через kv, если потребуется в дальнейшем
