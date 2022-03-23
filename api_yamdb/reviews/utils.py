import datetime as dt

from django.core.validators import MaxValueValidator


def current_year():
    """Получаем текущий год."""
    return dt.date.today().year


def max_value_current_year(value):
    """
    Подставляем в валидатор текущий год,
    для валидации максимального значения поля.
    """
    return MaxValueValidator(current_year())(value)
