import json
import random
import time
from typing import List


# Сохранение результатов в JSON
def save_results_to_json(filename: str, data: List[int], results: List[bool]):
    with open(filename, 'w') as f:
        json.dump({
            'metadata': {
                'data_size': len(data),
                'date': time.strftime("%Y-%m-%d %H:%M:%S")
            },
            'sample_data': {
                'numbers': data[:1000],
                'is_prime': results[:1000]
            }
        }, f, indent=2)

# Генерация тестовых данных
def generate_data(n: int) -> List[int]:
    return [random.randint(1, 1000) for _ in range(n)]


# Функция проверки числа на простоту
def process_number(number: int) -> bool:
    if number < 2:
        return False
    for i in range(2, int(number ** 0.5) + 1):
        if number % i == 0:
            return False
    return True

# АЛЬТЕРНАТИВНОЕ ИСПОЛЬЗОВАНИЕ С NUMPY
# import numpy as np
#
# def generate_data_np(n):
#     return np.random.randint(1, 1001, size=n).tolist()
#
# # Пример использования:
# data_np = generate_data_np(1000000)
# print(len(data_np))  # 1000000


