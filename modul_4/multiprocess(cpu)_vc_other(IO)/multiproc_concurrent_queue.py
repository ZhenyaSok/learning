import multiprocessing
import concurrent.futures
from typing import List

from modul_4.function import process_number

# Вариант: Однопоточная обработка
def process_single_thread(data: List[int]) -> List[bool]:
    return [process_number(num) for num in data]


# Вариант A: Ипользование пула потоков с concurrent.futures.
def process_with_threads(data: List[int]) -> List[bool]:
    with concurrent.futures.ThreadPoolExecutor() as executor:
        return list(executor.map(process_number, data))


# Вариант Б: Использование multiprocessing.Pool с пулом процессов, равным количеству CPU.
def process_with_pool(data: List[int]) -> List[bool]:
    with multiprocessing.Pool() as pool:
        return pool.map(process_number, data, chunksize=1000)


# Вариант В: Создание отдельных процессов с использованием multiprocessing.Process и
# очередей (multiprocessing.Queue) для передачи данных.
def worker(input_queue: multiprocessing.Queue, output_queue: multiprocessing.Queue):
    try:
        while True:
            item = input_queue.get()
            if item is None:
                break
            idx, num = item
            output_queue.put((idx, process_number(num)))
    except KeyboardInterrupt:
        pass


def process_with_queue(data: List[int]) -> List[bool]:
    input_queue = multiprocessing.Queue()
    output_queue = multiprocessing.Queue()
    processes = []

    for _ in range(multiprocessing.cpu_count()):
        p = multiprocessing.Process(target=worker, args=(input_queue, output_queue))
        p.start()
        processes.append(p)

    for idx, num in enumerate(data):
        input_queue.put((idx, num))

    for _ in range(multiprocessing.cpu_count()):
        input_queue.put(None)

    results = [None] * len(data)
    for _ in range(len(data)):
        idx, res = output_queue.get()
        results[idx] = res


    for p in processes:
        p.join()

    return results