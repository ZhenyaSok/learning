from concurrent.futures import ProcessPoolExecutor
import os

from modul_4.function import generate_data


def process_number(number):
    """Пример: проверка числа на простоту."""
    if number < 2:
        return False
    for i in range(2, int(number ** 0.5) + 1):
        if number % i == 0:
            return False
    return True

data_test = generate_data(1000000)  # 1 млн чисел

def process_data_processpool(data):
    # Обычно берём количество ядер CPU
    num_workers = os.cpu_count() or 4
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        results = list(executor.map(process_number, data))
    return results

# Пример вызова:
results = process_data_processpool(data_test)
print(len(results))  # Проверяем, что все числа обработаны