from collections import OrderedDict
from functools import wraps


def lru_cache(*args, **kwargs):
    # Обработка двух вариантов использования:
    # 1. @lru_cache без параметров
    # 2. @lru_cache(maxsize=...) с параметрами
    if len(args) == 1 and callable(args[0]):
        # Вариант 1: декоратор вызван без параметров
        # args[0] содержит саму функцию, которую декорируем
        return lru_cache(maxsize=None)(args[0])
    else:
        # Вариант 2: декоратор вызван с параметрами
        # Извлекаем параметр maxsize из kwargs, по умолчанию None
        maxsize = kwargs.get("maxsize", None)

        # Внутренняя функция-декоратор, которая принимает функцию для обертывания
        def decorator(func):
            # Создаем кеш в виде OrderedDict для отслеживания порядка использования
            # OrderedDict сохраняет порядок добавления элементов
            cache = OrderedDict()

            # Декоратор wraps сохраняет метаданные оригинальной функции
            # (имя, документацию, аннотации и другие атрибуты)
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Создаем ключ на основе позиционных и именованных аргументов
                # frozenset используется для kwargs, чтобы порядок аргументов не имел значения
                # Например: f(a=1, b=2) и f(b=2, a=1) создадут одинаковый ключ
                key = (args, frozenset(kwargs.items()))

                # Проверяем, есть ли результат в кеше
                if key in cache:
                    # Если результат есть в кеше, обновляем порядок использования
                    # move_to_end перемещает элемент в конец (делает его "самым новым")
                    cache.move_to_end(key)
                    # Возвращаем закешированный результат
                    return cache[key]

                # Если результата нет в кеше, вызываем оригинальную функцию
                result = func(*args, **kwargs)

                # Сохраняем результат в кеш
                cache[key] = result
                # Обновляем порядок использования (помещаем в конец как самый новый)
                cache.move_to_end(key)

                # Если достигнут максимальный размер кеша, удаляем самый старый элемент
                # last=False означает удаление из начала (самого старого элемента)
                if maxsize is not None and len(cache) > maxsize:
                    cache.popitem(last=False)

                # Возвращаем результат вычислений
                return result

            # Возвращаем обернутую функцию
            return wrapper

        # Возвращаем декоратор для применения к функции
        return decorator
