import unittest.mock
from collections import OrderedDict
from functools import wraps


# Реализуйте lru_cache декоратор.
#
# Требования:
#
# Декоратор должен кешировать результаты вызовов
# функции на основе её аргументов.
# Если функция вызывается с теми же аргументами,
# что и ранее, возвращайте результат из кеша вместо повторного выполнения функции.
# Декоратор должно быть возможно использовать двумя способами: с
# указанием максимального кол-ва элементов и без.

def lru_cache(*args, **kwargs):
    # Обработка двух вариантов использования:
    # 1. @lru_cache без параметров
    # 2. @lru_cache(maxsize=...) с параметрами
    if len(args) == 1 and callable(args[0]):
        # Вариант 1: декоратор вызван без параметров
        return lru_cache(maxsize=None)(args[0])
    else:
        # Вариант 2: декоратор вызван с параметрами
        maxsize = kwargs.get("maxsize", None)

        def decorator(func):
            # Кеш в виде OrderedDict для отслеживания порядка использования
            cache = OrderedDict()

            @wraps(func)  # Добавляем wraps для сохранения метаданных
            def wrapper(*args, **kwargs):
                # Создаем ключ на основе позиционных и именованных аргументов
                key = (args, frozenset(kwargs.items()))

                # Проверяем, есть ли результат в кеше
                if key in cache:
                    # Обновляем порядок использования (перемещаем в конец)
                    cache.move_to_end(key)
                    return cache[key]

                # Вызываем оригинальную функцию, если результат не в кеше
                result = func(*args, **kwargs)

                # Сохраняем результат в кеш
                cache[key] = result
                # Обновляем порядок использования
                cache.move_to_end(key)

                # Если достигнут максимальный размер кеша, удаляем самый старый элемент
                if maxsize is not None and len(cache) > maxsize:
                    cache.popitem(last=False)

                return result

            return wrapper

        return decorator


@lru_cache
def sum_m(a: int, b: int) -> int:
    return a + b


@lru_cache
def sum_many(a: int, b: int, *, c: int, d: int) -> int:
    return a + b + c + d


@lru_cache(maxsize=3)
def multiply_m(a: int, b: int) -> int:
    return a * b


if __name__ == "__main__":
    assert sum_m(1, 2) == 3
    assert sum_m(3, 4) == 7

    assert multiply_m(1, 2) == 2
    assert multiply_m(3, 4) == 12

    assert sum_many(1, 2, c=3, d=4) == 10

    mocked_func = unittest.mock.Mock()
    mocked_func.side_effect = [1, 2, 3, 4]

    decorated = lru_cache(maxsize=2)(mocked_func)
    assert decorated(1, 2) == 1
    assert decorated(1, 2) == 1
    assert decorated(3, 4) == 2
    assert decorated(3, 4) == 2
    assert decorated(5, 6) == 3
    assert decorated(5, 6) == 3
    assert decorated(1, 2) == 4
    assert mocked_func.call_count == 4
