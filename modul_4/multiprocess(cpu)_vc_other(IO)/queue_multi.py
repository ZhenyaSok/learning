import multiprocessing
import random
import time
import concurrent.futures

def generate_data(n):
    return [random.randint(1, 1000) for _ in range(n)]


def process_number(number):
    """Проверка числа на простоту."""
    if number < 2:
        return False
    for i in range(2, int(number ** 0.5) + 1):
        if number % i == 0:
            return False
    return True


def worker(input_queue, output_queue):
    try:
        while True:
            number = input_queue.get()
            if number is None:  # Сигнал завершения
                break
            result = process_number(number)
            output_queue.put(result)
    except KeyboardInterrupt:
        pass


def process_data_multiprocessing_queue(data):
    num_workers = multiprocessing.cpu_count()
    input_queue = multiprocessing.Queue()
    output_queue = multiprocessing.Queue()

    processes = []
    for _ in range(num_workers):
        p = multiprocessing.Process(
            target=worker,
            args=(input_queue, output_queue)
        )
        p.start()
        processes.append(p)

    try:
        for number in data:
            input_queue.put(number)

        for _ in range(num_workers):
            input_queue.put(None)

        results = []
        for _ in range(len(data)):
            results.append(output_queue.get())

        for p in processes:
            p.join()

        return results

    except KeyboardInterrupt:
        print("\nПрерывание пользователем! Завершение процессов...")
        for p in processes:
            p.terminate()
        raise
def process_data_sync(data):
    return [process_number(num) for num in data]

def process_data_with_pool(data):
    # Создаем пул процессов (по умолчанию = количеству CPU)
    with multiprocessing.Pool() as pool:
        # map сохраняет порядок результатов
        results = pool.map(process_number, data)
    return results

# Вариант 2: Пул потоков (concurrent.futures)
def process_data_threadpool(data):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(process_number, data))
    return results

def process_data_processpool(data):
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = list(executor.map(process_number, data))
    return results

if __name__ == '__main__':
    data = generate_data(100000)  # Тестовые данные (можно увеличить до 1_000_000)

    # Замер многопроцессорной версии
    print("Запуск многопроцессорной обработки...")
    start_mp = time.perf_counter()
    results_mp = process_data_multiprocessing_queue(data)
    time_mp = time.perf_counter() - start_mp
    print(f"Многопроцессорная версия: {time_mp:.2f} сек")

    # print("Запуск !!! обработки...")
    # start_pp = time.perf_counter()
    # results_pp = process_data_processpool(data)
    # time_pp = time.perf_counter() - start_pp
    # print(f"ProcessPoolExecutor: {time_pp:.2f} сек")

    # Замер многопоточной версии
    print("\nЗапуск многопоточной обработки...")
    start_thread = time.perf_counter()
    results_thread = process_data_threadpool(data)
    time_thread = time.perf_counter() - start_thread
    print(f"Многопоточная версия: {time_thread:.2f} сек")

    print("\nЗапуск синхронной обработки...")
    start_time = time.perf_counter()
    results_sync = process_data_sync(data)
    end_time = time.perf_counter()
    print(f"Синхронное выполнение: {end_time - start_time:.2f} сек")

    print("\nЗапуск multiprocessing.Pool обработки...")
    start_time = time.perf_counter()
    results = process_data_with_pool(data)
    end_time = time.perf_counter()

    print(f"Обработано чисел: {len(results)}")
    print(f"Время выполнения multiprocessing.Pool: {end_time - start_time:.2f} сек")
    print(f"Пример результатов: {results[:10]}")  # Первые 10 результатов

    # Проверка корректности
    # Сравнение результатов (без учета порядка)
    if set(results_mp) == set(results_thread):
        print("\nРезультаты идентичны (без учета порядка).")
    else:
        print("\nОшибка: Результаты различаются!")

    # Дополнительная проверка (если нужно)
    print(f"\nПримеры результатов:\nMP: {results_mp[:5]}\nThread: {results_thread[:5]}")
# if __name__ == '__main__':
#     try:
#         # Замер времени начала выполнения
#         start_time = time.perf_counter()
#
#         data = generate_data(100_000)  # Можно изменить на 1_000_000 для полного теста
#         print(f"Обработка {len(data)} чисел... (Ctrl+C для остановки)")
#
#         results = process_data_multiprocessing_queue(data)
#
#         # Замер времени окончания и вывод результата
#         end_time = time.perf_counter()
#         elapsed_time = end_time - start_time
#
#         print(f"Обработано чисел: {len(results)}")
#         print(f"Время выполнения: {elapsed_time:.2f} секунд")
#
        # start_time = time.perf_counter()
        # results_sync = process_data_sync(data)
        # end_time = time.perf_counter()
        # print(f"Синхронное выполнение: {end_time - start_time:.2f} сек")
#
#     except KeyboardInterrupt:
#         print("\nПрограмма остановлена пользователем.")