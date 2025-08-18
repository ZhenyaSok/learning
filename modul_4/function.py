import random

def generate_data(n):
    return [random.randint(1, 1000) for _ in range(n)]

    # Пример использования:
data = generate_data(1000000)
print(len(data))  # Проверка: вывод длины списка (должно быть 1000000)

# АЛЬТЕРНАТИВНОЕ ИСПОЛЬЗОВАНИЕ С NUMPY
import numpy as np

def generate_data_np(n):
    return np.random.randint(1, 1001, size=n).tolist()

# Пример использования:
data_np = generate_data_np(1000000)
print(len(data_np))  # 1000000


def process_number(number):
    if number < 0:
        return None
    result = 1
    for i in range(1, number + 1):
        result *= i
    return result

# Пример:
print(process_number(5))  # 120