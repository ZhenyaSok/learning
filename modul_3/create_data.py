import asyncio
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def generate_test_urls():
    """Генерирует тестовый файл urls.txt с разными типами URL"""
    test_urls = [
        # Рабочие URL (возвращают JSON)
        "https://jsonplaceholder.typicode.com/todos/1",
        "https://jsonplaceholder.typicode.com/posts/1",
        "https://httpbin.org/get",
        "https://api.github.com",
        # Нерабочие URL (для тестирования ошибок)
        "https://nonexistent-domain-12345.com",
        "https://httpbin.org/status/404",
        "https://httpbin.org/status/500",
        "http://example.com",  # Не возвращает JSON
        "https://google.com",  # Не возвращает JSON
    ]

    # Записываем URL в файл
    with open("data/urls.txt", "w") as f:
        f.write("\n".join(test_urls))

    logger.info(f"Создан тестовый файл urls.txt с {len(test_urls)} URL")


async def main():
    await generate_test_urls()

    # Проверяем, что файл создан
    try:
        with open("data/urls.txt", "r") as f:
            urls = f.readlines()
            logger.info("Первые 5 URL из файла:")
            for url in urls[:5]:
                logger.info(f"- {url.strip()}")
    except FileNotFoundError:
        logger.error("Ошибка: файл urls.txt не создан")


if __name__ == "__main__":
    asyncio.run(main())
