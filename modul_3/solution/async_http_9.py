import sys
import aiohttp
import asyncio
import json
import logging
from aiohttp import ClientSession, ClientError


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


async def fetch_single_url(
    session: ClientSession, url: str, semaphore: asyncio.Semaphore
):
    """
    Асинхронно загружает один URL и возвращает данные в формате JSON
    """
    cleaned_url = url.strip()
    try:
        async with semaphore:  # Ограничение одновременных запросов
            async with session.get(
                cleaned_url, timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status == 200:
                    try:
                        data = await response.json()
                        logger.info(f"Успешно загружено: {cleaned_url}")
                        return {"url": cleaned_url, "content": data}
                    except json.JSONDecodeError:
                        text = await response.text()
                        logger.error(
                            f"Ошибка парсинга JSON с {cleaned_url}. Ответ: {text[:200]}..."
                        )
                    except Exception as e:
                        logger.error(
                            f"Ошибка обработки ответа с {cleaned_url}: {str(e)}"
                        )
                else:
                    logger.error(f"HTTP ошибка {response.status} для {cleaned_url}")
    except asyncio.TimeoutError:
        logger.error(f"Таймаут при загрузке {cleaned_url}")
    except ClientError as e:
        logger.error(f"Ошибка соединения с {cleaned_url}: {str(e)}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка при загрузке {cleaned_url}: {str(e)}")
    return None


async def fetch_urls():
    """
    Основная функция для загрузки URL из файла и сохранения результатов
    """
    input_file = "../data/urls.txt"
    output_file = "../data/results.jsonl"

    # Проверяем существование входного файла
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            urls = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        logger.error(f"Файл {input_file} не найден!")
        return
    except Exception as e:
        logger.error(f"Ошибка чтения файла {input_file}: {str(e)}")
        return

    if not urls:
        logger.error("Файл с URL пуст!")
        return

    logger.info(f"Найдено URL для обработки: {len(urls)}")

    # Ограничиваем количество одновременных запросов
    semaphore = asyncio.Semaphore(5)
    success_count = 0

    async with ClientSession() as session:
        # Создаем задачи для каждого URL
        tasks = [fetch_single_url(session, url, semaphore) for url in urls]

        # Открываем файл для записи результатов
        with open(output_file, "w", encoding="utf-8") as result_file:
            # Обрабатываем результаты по мере их поступления
            for future_result in asyncio.as_completed(tasks):
                result = await future_result
                if result is not None:
                    result_file.write(json.dumps(result, ensure_ascii=False) + "\n")
                    result_file.flush()  # Сбрасываем буфер после каждой записи
                    success_count += 1
                    if (
                        success_count % 100 == 0
                    ):  # Логируем каждые 100 успешных запросов
                        logger.info(f"Обработано: {success_count}/{len(urls)}")

    logger.info(f"Завершено! Успешно обработано URL: {success_count} из {len(urls)}")
    logger.info(f"Результаты сохранены в: {output_file}")


if __name__ == "__main__":
    try:
        asyncio.run(fetch_urls())
    except KeyboardInterrupt:
        logger.info("Работа прервана пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {str(e)}")
