import asyncio
import json
import logging
import sys
from concurrent.futures import ThreadPoolExecutor

import aiohttp
from aiohttp import ClientError, ClientSession

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("../data/fetch_urls.log", encoding="utf-8"),
    ],
    encoding="utf-8",
)
logger = logging.getLogger(__name__)


async def parse_json_in_executor(executor: ThreadPoolExecutor, text: str):
    """
    Парсит JSON в отдельном потоке чтобы не блокировать event loop
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, json.loads, text)


async def serialize_json_in_executor(executor: ThreadPoolExecutor, data: dict):
    """
    Сериализует JSON в отдельном потоке чтобы не блокировать event loop
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        executor, lambda: json.dumps(data, ensure_ascii=False)
    )


async def fetch_single_url(
    session: ClientSession,
    url: str,
    output_queue: asyncio.Queue,
    worker_id: int,
    executor: ThreadPoolExecutor,
):
    """
    Асинхронно загружает один URL и помещает результат в очередь
    """
    cleaned_url = url.strip()
    try:
        async with session.get(
            cleaned_url, timeout=aiohttp.ClientTimeout(total=60)
        ) as response:
            # Проверяем все успешные статусы 2xx
            response.raise_for_status()

            try:
                # Читаем текст ответа асинхронно
                text = await response.text()

                # Парсим JSON в отдельном потоке
                data = await parse_json_in_executor(executor, text)

                logger.debug(f"Воркер {worker_id}: Успешно загружено: {cleaned_url}")
                await output_queue.put(
                    {"url": cleaned_url, "content": data, "status": "success"}
                )

            except json.JSONDecodeError:
                logger.error(
                    f"Воркер {worker_id}: Ошибка парсинга JSON с {cleaned_url}. Ответ: {text[:200]}..."
                )
                await output_queue.put(
                    {
                        "url": cleaned_url,
                        "error": "JSON decode error",
                        "status": "error",
                    }
                )
            except Exception as e:
                logger.error(
                    f"Воркер {worker_id}: Ошибка обработки ответа с {cleaned_url}: {str(e)}"
                )
                await output_queue.put(
                    {"url": cleaned_url, "error": str(e), "status": "error"}
                )

    except aiohttp.ClientResponseError as e:
        logger.error(
            f"Воркер {worker_id}: HTTP ошибка {e.status} для {cleaned_url}: {e.message}"
        )
        await output_queue.put(
            {
                "url": cleaned_url,
                "error": f"HTTP {e.status}: {e.message}",
                "status": "error",
            }
        )
    except asyncio.TimeoutError:
        logger.error(f"Воркер {worker_id}: Таймаут при загрузке {cleaned_url}")
        await output_queue.put(
            {"url": cleaned_url, "error": "timeout", "status": "error"}
        )
    except ClientError as e:
        logger.error(f"Воркер {worker_id}: Ошибка соединения с {cleaned_url}: {str(e)}")
        await output_queue.put({"url": cleaned_url, "error": str(e), "status": "error"})
    except Exception as e:
        logger.error(
            f"Воркер {worker_id}: Неожиданная ошибка при загрузке {cleaned_url}: {str(e)}"
        )
        await output_queue.put({"url": cleaned_url, "error": str(e), "status": "error"})


async def url_producer(input_file: str, url_queue: asyncio.Queue):
    """
    Читает URL из файла и помещает их в очередь для обработки
    """
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            for line_num, line in enumerate(file, 1):
                url = line.strip()
                if url:
                    await url_queue.put(url)
                    if line_num % 1000 == 0:
                        logger.info(f"Произведено URL: {line_num}")

        # Сигнал окончания работы для воркеров
        for _ in range(CONCURRENT_WORKERS):
            await url_queue.put(None)

        logger.info(f"Все URL прочитаны. Всего: {line_num}")

    except FileNotFoundError:
        logger.error(f"Файл {input_file} не найден!")
        # Сигнал об ошибке для воркеров
        for _ in range(CONCURRENT_WORKERS):
            await url_queue.put(None)
    except Exception as e:
        logger.error(f"Ошибка чтения файла {input_file}: {str(e)}")
        for _ in range(CONCURRENT_WORKERS):
            await url_queue.put(None)


async def url_worker(
    session: ClientSession,
    url_queue: asyncio.Queue,
    output_queue: asyncio.Queue,
    worker_id: int,
    executor: ThreadPoolExecutor,
):
    """
    Воркер, который берет URL из очереди и обрабатывает их
    """
    while True:
        url = await url_queue.get()
        if url is None:  # Сигнал завершения
            url_queue.task_done()
            break

        await fetch_single_url(session, url, output_queue, worker_id, executor)
        url_queue.task_done()


async def result_writer(
    output_file: str,
    output_queue: asyncio.Queue,
    total_urls: int,
    executor: ThreadPoolExecutor,
):
    """
    Записывает результаты в файл
    """
    success_count = 0
    error_count = 0
    processed_count = 0

    with open(output_file, "w", encoding="utf-8") as result_file:
        while processed_count < total_urls:
            result = await output_queue.get()
            if result is None:  # Сигнал завершения
                break

            try:
                # Сериализуем JSON в отдельном потоке
                json_line = await serialize_json_in_executor(executor, result)
                result_file.write(json_line + "\n")
                result_file.flush()

                if result.get("status") == "success":
                    success_count += 1
                else:
                    error_count += 1

                processed_count += 1
                output_queue.task_done()

                if processed_count % 100 == 0:
                    logger.info(
                        f"Обработано: {processed_count}/{total_urls} "
                        f"(Успешно: {success_count}, Ошибок: {error_count})"
                    )

            except Exception as e:
                logger.error(f"Ошибка сериализации результата: {str(e)}")
                output_queue.task_done()
                processed_count += 1
                error_count += 1

    logger.info(
        f"Запись завершена. Всего: {processed_count}, "
        f"Успешно: {success_count}, Ошибок: {error_count}"
    )


async def fetch_urls():
    """
    Основная функция для загрузки URL из файла и сохранения результатов
    """
    input_file = "../data/urls.txt"
    output_file = "../data/results.jsonl"

    # Сначала подсчитаем общее количество URL
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            total_urls = sum(1 for line in file if line.strip())
    except FileNotFoundError:
        logger.error(f"Файл {input_file} не найден!")
        return
    except Exception as e:
        logger.error(f"Ошибка чтения файла {input_file}: {str(e)}")
        return

    if total_urls == 0:
        logger.error("Файл с URL пуст!")
        return

    logger.info(f"Найдено URL для обработки: {total_urls}")

    # Создаем очереди
    url_queue = asyncio.Queue(maxsize=10000)  # Ограничиваем размер очереди
    output_queue = asyncio.Queue()

    # Создаем ThreadPoolExecutor для CPU-bound операций
    with ThreadPoolExecutor(max_workers=MAX_JSON_WORKERS) as executor:
        # Запускаем продюсера
        producer_task = asyncio.create_task(url_producer(input_file, url_queue))

        async with ClientSession() as session:
            # Запускаем воркеров
            worker_tasks = [
                asyncio.create_task(
                    url_worker(session, url_queue, output_queue, i, executor)
                )
                for i in range(CONCURRENT_WORKERS)
            ]

            # Запускаем писателя результатов
            writer_task = asyncio.create_task(
                result_writer(output_file, output_queue, total_urls, executor)
            )

            # Ждем завершения продюсера
            await producer_task

            # Ждем завершения всех воркеров
            await asyncio.gather(*worker_tasks)

            # Сигнализируем писателю о завершении
            await output_queue.put(None)

            # Ждем завершения писателя
            await writer_task

    logger.info(f"Результаты сохранены в: {output_file}")


# Конфигурация
CONCURRENT_WORKERS = 5  # Количество одновременных HTTP запросов
MAX_JSON_WORKERS = 4  # Количество потоков для обработки JSON

if __name__ == "__main__":
    try:
        asyncio.run(fetch_urls())
    except KeyboardInterrupt:
        logger.info("Работа прервана пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {str(e)}")
