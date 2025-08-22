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
    if len(args) == 1 and callable(args[0]):
        return lru_cache(maxsize=None)(args[0])
    else:
        maxsize = kwargs.get("maxsize", None)

        def decorator(func):
            cache = OrderedDict()

            @wraps(func)
            def wrapper(*args, **kwargs):
                key = (args, frozenset(kwargs.items()))

                if key in cache:
                    cache.move_to_end(key)
                    return cache[key]

                result = func(*args, **kwargs)
                cache[key] = result
                cache.move_to_end(key)

                if maxsize is not None and len(cache) > maxsize:
                    cache.popitem(last=False)

                return result

            # Добавляем метод для ручной очистки
            def cache_clear():
                cache.clear()

            wrapper.cache_clear = cache_clear
            wrapper.cache_info = lambda: f"Size: {len(cache)}, Maxsize: {maxsize}"

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
