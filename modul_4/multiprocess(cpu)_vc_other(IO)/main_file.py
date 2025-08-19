import os

import csv
import time
import matplotlib.pyplot as plt
from modul_4.function import generate_data, save_results_to_json
from multiproc_concurrent_queue import process_with_queue, process_with_threads, process_with_pool, process_single_thread


DATA_SIZE = 1000000


# Основная функция тестирования
def benchmark():
    data = generate_data(DATA_SIZE)
    print(f"🔧 Сгенерировано {len(data)} тестовых чисел")

    # Тестируемые методы
    variants = {
        "1. Однопоточный": process_single_thread,
        "2. ThreadPool (потоки)": process_with_threads,
        "3. Process+Queue": process_with_queue,
        "4. ProcessPool": process_with_pool
    }

    # Запуск тестов
    timings = {}
    results = {}

    print("\n⏳ Запуск тестов производительности...")
    for name, func in variants.items():
        start_time = time.perf_counter()
        res = func(data)
        elapsed = time.perf_counter() - start_time
        timings[name] = elapsed
        results[name] = res
        print(f"{name}: {elapsed:.2f} сек")

    # Сохранение результатов
    if not os.path.exists('results'):
        os.makedirs('results')

    save_results_to_json('results/benchmark_results.json', data, results["4. ProcessPool"])

    # Сохранение таблицы результатов в CSV
    with open('results/benchmark_timings.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Метод', 'Время (сек)', 'Ускорение'])
        base_time = timings["1. Однопоточный"]
        for name, time_ in timings.items():
            writer.writerow([name, f"{time_:.2f}", f"{base_time / time_:.1f}x"])

    # Построение графика
    plt.figure(figsize=(12, 6))
    names = list(timings.keys())
    times = list(timings.values())

    bars = plt.barh(names, times, color=[
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#88D8B0'
    ])
    plt.title('Сравнение методов параллельной обработки')
    plt.xlabel('Время выполнения (секунды)')
    plt.grid(axis='x', linestyle='--', alpha=0.7)

    # Добавление значений на график
    for bar in bars:
        width = bar.get_width()
        plt.text(width + 0.1, bar.get_y() + bar.get_height() / 2,
                 f'{width:.2f} сек',
                 va='center')

    plt.tight_layout()
    plt.savefig('results/benchmark_chart-1.png', dpi=120)
    plt.show()
    plt.close()

    print("\n✅ Результаты сохранены в папке 'results':")
    print("- benchmark_results.json (образец данных)")
    print("- benchmark_timings.csv (таблица результатов)")
    print("- benchmark_chart.png (визуализация)")

if __name__ == '__main__':
    benchmark()