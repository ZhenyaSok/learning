import concurrent.futures
import csv
import json
import multiprocessing
import os
import random
import time
from typing import Dict, Generator, List

import matplotlib.pyplot as plt

# Конфигурация
DATA_SIZE = 1000000  # 1 млн элементов
MAX_CHUNKSIZE = 10_000  # Максимальный размер чанка
MIN_CHUNKSIZE = 100  # Минимальный размер чанка
OUTPUT_DIR = "results"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# Генератор тестовых данных
def generate_data(n: int) -> List[int]:
    print(f"Генерация {n:,} случайных чисел...")
    return [random.randint(1, 1000) for _ in range(n)]


# Оптимизированная проверка на простоту
def process_number(number: int) -> bool:
    if number < 2:
        return False
    for i in range(2, int(number**0.5) + 1):
        if number % i == 0:
            return False
    return True


# Автоподбор chunksize
def calculate_optimal_chunksize(data_size: int, num_workers: int) -> int:
    """Вычисляет оптимальный размер чанка по формуле Python multiprocessing"""
    chunksize = data_size // (num_workers * 4)
    return max(MIN_CHUNKSIZE, min(chunksize, MAX_CHUNKSIZE))


# Разбиение данных на чанки
def chunk_data(data: List, chunk_size: int) -> Generator[List, None, None]:
    """Генератор, разбивающий данные на части"""
    for i in range(0, len(data), chunk_size):
        yield data[i : i + chunk_size]


# Вариант 1: Однопоточная обработка (эталон)
def process_single_thread(data: List[int]) -> List[bool]:
    return [process_number(num) for num in data]


# Вариант 2: ProcessPool с оптимизированным chunksize
def process_with_pool(data: List[int]) -> List[bool]:
    num_workers = multiprocessing.cpu_count()
    chunksize = calculate_optimal_chunksize(len(data), num_workers)

    print(
        f"\nProcessPool: использование {num_workers} процессов, chunksize={chunksize:,}"
    )

    with multiprocessing.Pool(num_workers) as pool:
        results = []
        # Обработка чанками для экономии памяти
        for chunk in chunk_data(data, 100_000):  # Обрабатываем по 100K за раз
            results.extend(pool.map(process_number, chunk, chunksize=chunksize))
        return results


# Вариант 3: Process + Queue с контролем памяти
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
    num_workers = multiprocessing.cpu_count()
    input_queue = multiprocessing.Queue(maxsize=num_workers * 2)
    output_queue = multiprocessing.Queue()
    processes = []

    # Запуск процессов
    for _ in range(num_workers):
        p = multiprocessing.Process(
            target=worker, args=(input_queue, output_queue), daemon=True
        )
        p.start()
        processes.append(p)

    # Передача данных с индексами
    for idx, num in enumerate(data):
        input_queue.put((idx, num))

    # Сигналы завершения
    for _ in range(num_workers):
        input_queue.put(None)

    # Сбор результатов
    results = [None] * len(data)
    received = 0
    while received < len(data):
        idx, res = output_queue.get()
        results[idx] = res
        received += 1
        # Прогресс-бар
        if received % 100_000 == 0:
            print(f"Обработано {received:,}/{len(data):,}...")

    # Очистка
    for p in processes:
        p.join(timeout=0.1)
        if p.is_alive():
            p.terminate()

    input_queue.close()
    output_queue.close()
    return results


# Вариант 4: ThreadPool (для сравнения)
def process_with_threads(data: List[int]) -> List[bool]:
    with concurrent.futures.ThreadPoolExecutor() as executor:
        return list(executor.map(process_number, data))


# Визуализация результатов
def plot_results(timings: Dict[str, float]):
    plt.figure(figsize=(12, 6))
    names = list(timings.keys())
    times = list(timings.values())

    bars = plt.barh(names, times, color=["#FF6B6B", "#4ECDC4", "#45B7D1", "#88D8B0"])
    plt.title("Сравнение методов параллельной обработки")
    plt.xlabel("Время выполнения (секунды)")
    plt.grid(axis="x", linestyle="--", alpha=0.7)

    # Добавление значений на график
    for bar in bars:
        width = bar.get_width()
        plt.text(
            width + 0.1,
            bar.get_y() + bar.get_height() / 2,
            f"{width:.2f} сек",
            va="center",
        )

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/benchmark_chart.png", dpi=120)
    plt.close()
    print("График сохранен как 'benchmark_chart.png'")


# Сохранение результатов
def save_results(data: List[int], results: List[bool], timings: Dict[str, float]):
    # JSON с метаданными
    with open(f"{OUTPUT_DIR}/results.json", "w") as f:
        json.dump(
            {
                "metadata": {
                    "date": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "data_size": len(data),
                    "timings": timings,
                },
                "sample": list(zip(data[:100], results[:100])),
            },
            f,
            indent=2,
        )

    # CSV с таймингами
    with open(f"{OUTPUT_DIR}/timings.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Метод", "Время (сек)", "Ускорение"])
        base_time = timings["Single-thread"]
        for name, t in timings.items():
            writer.writerow([name, f"{t:.2f}", f"{base_time / t:.1f}x"])


# Основной benchmark
def run_benchmark():
    data = generate_data(DATA_SIZE)
    variants = {
        "Single-thread": process_single_thread,
        "ThreadPool": process_with_threads,
        "Process+Queue": process_with_queue,
        "ProcessPool": process_with_pool,
    }

    timings = {}

    print("\nStarting benchmark...")
    for name, func in variants.items():
        print(f"\n--- {name} ---")
        start = time.perf_counter()
        results = func(data)
        elapsed = time.perf_counter() - start
        timings[name] = elapsed
        print(f"Время: {elapsed:.2f} сек")

        # Проверка первых 10 результатов для демонстрации
        print("Пример результатов:", list(zip(data[:5], results[:5])))

    # Сохранение и визуализация
    save_results(data, results, timings)
    plot_results(timings)

    print("\nBenchmark завершен!")
    print(f"Результаты сохранены в папке '{OUTPUT_DIR}'")


if __name__ == "__main__":
    run_benchmark()
