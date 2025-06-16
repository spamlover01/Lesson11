import sys
import os

print("--- Начало теста импорта ---")
print(f"Используемый интерпретатор Python: {sys.executable}")
print("\nТекущие пути в sys.path:")
for p in sys.path:
    print(f"  {p}")

# Проверяем существование директории site-packages
venv_site_packages = os.path.normpath(os.path.join(os.path.dirname(sys.executable), '..', 'Lib', 'site-packages'))
print(f"\nПроверяемый путь к site-packages: {venv_site_packages}")
if os.path.exists(venv_site_packages):
    print(f"Директория site-packages ({venv_site_packages}) СУЩЕСТВУЕТ.")

    # Проверяем наличие папки kivy_garden внутри site-packages
    kivy_garden_dir_in_site_packages = os.path.join(venv_site_packages, 'kivy_garden')
    print(f"Проверяемый путь к kivy_garden в site-packages: {kivy_garden_dir_in_site_packages}")
    if os.path.exists(kivy_garden_dir_in_site_packages) and os.path.isdir(kivy_garden_dir_in_site_packages):
        print(f"Директория kivy_garden ({kivy_garden_dir_in_site_packages}) СУЩЕСТВУЕТ.")
        # Проверяем наличие __init__.py
        init_py_path = os.path.join(kivy_garden_dir_in_site_packages, '__init__.py')
        if os.path.exists(init_py_path):
            print(f"Файл __init__.py в kivy_garden ({init_py_path}) СУЩЕСТВУЕТ.")
        else:
            print(
                f"ПРЕДУПРЕЖДЕНИЕ: Файл __init__.py в kivy_garden ({init_py_path}) НЕ НАЙДЕН. Это может быть причиной ошибки.")
    else:
        print(f"ПРЕДУПРЕЖДЕНИЕ: Директория kivy_garden ({kivy_garden_dir_in_site_packages}) НЕ НАЙДЕНА.")
else:
    print(f"ПРЕДУПРЕЖДЕНИЕ: Директория site-packages ({venv_site_packages}) НЕ НАЙДЕНА.")

# Путь к "цветку" matplotlib
kivy_garden_flower_path = os.path.normpath(
    os.path.join(os.path.expanduser('~'), '.kivy', 'garden', 'garden.matplotlib'))
print(f"\nПроверяемый путь к 'цветку' garden.matplotlib: {kivy_garden_flower_path}")
if os.path.exists(kivy_garden_flower_path) and os.path.isdir(kivy_garden_flower_path):
    print(f"Директория 'цветка' garden.matplotlib ({kivy_garden_flower_path}) СУЩЕСТВУЕТ.")
else:
    print(f"ПРЕДУПРЕЖДЕНИЕ: Директория 'цветка' garden.matplotlib ({kivy_garden_flower_path}) НЕ НАЙДЕНА.")

print("\nПопытка импорта 'kivy_garden'...")
try:
    import kivy_garden

    print("УСПЕХ: import kivy_garden сработал!")
    if hasattr(kivy_garden, '__file__'):
        print(f"  kivy_garden.__file__: {kivy_garden.__file__}")
    if hasattr(kivy_garden, '__path__'):
        print(f"  kivy_garden.__path__: {kivy_garden.__path__}")

    print("\nПопытка импорта 'from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg'...")
    try:
        from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

        print("УСПЕХ: from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg сработал!")
    except ModuleNotFoundError as e_specific:
        print(f"ОШИБКА при импорте FigureCanvasKivyAgg: {e_specific}")
    except Exception as e_specific_other:
        print(f"ДРУГАЯ ОШИБКА при импорте FigureCanvasKivyAgg: {e_specific_other}")

except ModuleNotFoundError as e_kg:
    print(f"КРИТИЧЕСКАЯ ОШИБКА: ModuleNotFoundError при 'import kivy_garden': {e_kg}")
except Exception as e_other:
    print(f"КРИТИЧЕСКАЯ ОШИБКА: Другая ошибка при 'import kivy_garden': {e_other}")

print("\n--- Конец теста импорта ---")
# input("Нажмите Enter для выхода...") # Раскомментируйте, если запускаете не из IDE