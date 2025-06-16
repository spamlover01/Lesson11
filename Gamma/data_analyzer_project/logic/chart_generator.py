# logic/chart_generator.py
import matplotlib

matplotlib.use('agg')
import matplotlib.pyplot as plt
import pandas as pd
import io
from kivy.metrics import dp
from kivy.logger import Logger

MONTH_NAMES_FULL = ["Янв", "Фев", "Мар", "Апр", "Май", "Июн", "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"]


def _save_figure_to_buffer(fig):
    """Вспомогательная функция для сохранения фигуры в буфер."""
    try:
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close(fig)
        return buf
    except Exception as e:
        Logger.error(f"ChartGenerator: Ошибка при сохранении фигуры в буфер: {e}")
        plt.close(fig)
        return None


def create_dynamic_consumption_chart(data_series):
    """График 1: Динамика потребления."""
    fig, ax = plt.subplots(figsize=(5, 4))
    fig.set_facecolor((1, 1, 1, 1))
    ax.set_facecolor((0.95, 0.95, 0.95, 1))

    if data_series is not None and not data_series.empty:
        data_series = data_series.sort_index()
        x_labels = [f"{idx[0]}-{str(idx[1]).zfill(2)}" for idx in data_series.index]
        values = data_series.values
        ax.plot(x_labels, values, marker='o', linestyle='-', color='b', markersize=3)
        ax.tick_params(axis='x', rotation=70, labelsize=dp(5))
        ax.tick_params(axis='y', labelsize=dp(6))
    else:
        ax.plot([], [])
        ax.set_xticks([])
        ax.set_yticks([])

    ax.grid(True, linestyle='--', alpha=0.6)
    fig.tight_layout(pad=1.2)
    return _save_figure_to_buffer(fig)


def create_monthly_comparison_chart(df):
    """График 2: Расход по месяцам."""
    fig, ax = plt.subplots(figsize=(5, 4))
    fig.set_facecolor((1, 1, 1, 1))
    ax.set_facecolor((0.95, 0.95, 0.95, 1))

    if df is not None and not df.empty and all(c in df.columns for c in ['Год', 'Мес', 'Расход']):
        try:
            df_copy = df.copy()
            df_copy['Год'] = pd.to_numeric(df_copy['Год'], errors='coerce')
            df_copy['Мес'] = pd.to_numeric(df_copy['Мес'], errors='coerce')
            df_copy['Расход'] = pd.to_numeric(df_copy['Расход'], errors='coerce')
            df_copy.dropna(subset=['Год', 'Мес', 'Расход'], inplace=True)
            df_copy['Год'] = df_copy['Год'].astype(int)
            df_copy['Мес'] = df_copy['Мес'].astype(int)

            pivot_df = df_copy.pivot_table(index='Мес', columns='Год', values='Расход', aggfunc='sum')
            pivot_df.plot(ax=ax, marker='o', markersize=3)
            ax.set_xticks(range(1, 13))
            ax.set_xticklabels(MONTH_NAMES_FULL, rotation=45, ha='right', fontsize=dp(6))
            ax.set_xlabel("Месяц", fontsize=8)
            ax.set_ylabel("Расход", fontsize=8)
            ax.legend(title='Год', fontsize='xx-small')
            ax.tick_params(axis='y', labelsize=dp(6))
        except Exception as e:
            Logger.error(f"ChartGenerator: Ошибка при создании месячного графика: {e}")
            ax.plot([], [])
    else:
        ax.plot([], [])

    ax.grid(True, linestyle='--', alpha=0.6)
    fig.tight_layout(pad=1.2)
    return _save_figure_to_buffer(fig)


def create_yearly_sum_chart(df):
    """График 3: Суммарные расходы по годам."""
    fig, ax = plt.subplots(figsize=(5, 4))
    fig.set_facecolor((1, 1, 1, 1))
    ax.set_facecolor((0.95, 0.95, 0.95, 1))

    if df is not None and not df.empty and all(c in df.columns for c in ['Год', 'Расход']):
        try:
            df_copy = df.copy()
            df_copy['Год'] = pd.to_numeric(df_copy['Год'], errors='coerce')
            df_copy['Расход'] = pd.to_numeric(df_copy['Расход'], errors='coerce')
            df_copy.dropna(subset=['Год', 'Расход'], inplace=True)
            df_copy['Год'] = df_copy['Год'].astype(int)

            yearly_sum = df_copy.groupby('Год')['Расход'].sum()
            yearly_sum.plot(kind='bar', ax=ax, color='skyblue', edgecolor='black')
            ax.set_xlabel("Год", fontsize=8)
            ax.set_ylabel("Суммарный расход", fontsize=8)
            ax.tick_params(axis='x', rotation=0, labelsize=dp(7))
            ax.tick_params(axis='y', labelsize=dp(7))
        except Exception as e:
            Logger.error(f"ChartGenerator: Ошибка при создании годового графика: {e}")
            ax.plot([], [])
    else:
        ax.plot([], [])

    ax.grid(axis='y', linestyle='--', alpha=0.6)
    fig.tight_layout(pad=1.2)
    return _save_figure_to_buffer(fig)
