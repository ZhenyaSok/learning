#Задача - Распределенный лок
# У вас есть распределенное приложение работающее на десятках серверах. Вам необходимо написать декоратор single который гарантирует, что декорируемая функция не исполняется параллельно.
#
# Пример использования:
# ocessing_time указывает на максимально допустимое время работы декорируемой функции.

import functools
import datetime
import redis
import time
import uuid

# Подключение к Redis (настройте под себя)
redis_client = redis.Redis(host="localhost", port=6379, db=0)


def single(max_processing_time: datetime.timedelta):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            lock_key = f"single_lock:{func.__module__}.{func.__name__}"
            lock_value = str(uuid.uuid4())  # уникальный идентификатор владельца

            # Пытаемся захватить лок (SETNX + TTL)
            acquired = redis_client.set(
                name=lock_key,
                value=lock_value,
                nx=True,  # только если ключа ещё нет
                ex=int(max_processing_time.total_seconds()),  # срок жизни блокировки
            )

            if not acquired:
                print(f"⏳ Функция {func.__name__} уже выполняется где-то ещё")
                return None

            try:
                return func(*args, **kwargs)
            finally:
                # Освобождаем лок только если мы его держим
                val = redis_client.get(lock_key)
                if val and val.decode() == lock_value:
                    redis_client.delete(lock_key)

        return wrapper

    return decorator


# === Пример использования ===
@single(max_processing_time=datetime.timedelta(minutes=2))
def process_transaction():
    print("🚀 Старт транзакции")
    time.sleep(5)
    print("✅ Транзакция завершена")


if __name__ == "__main__":
    process_transaction()