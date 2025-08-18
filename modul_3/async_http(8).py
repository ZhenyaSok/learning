#Напишите асинхронную функцию fetch_urls, которая принимает список URL-адресов и
# возвращает словарь, где ключами являются URL, а значениями — статус-коды ответов.
# Используйте библиотеку aiohttp для выполнения HTTP-запросов.

# Требования:
#
# Ограничьте количество одновременных запросов до 5 (используйте
# примитивы синхронизации из asyncio библиотеки)
# Обработайте возможные исключения (например, таймауты, недоступные ресурсы)
# и присвойте соответствующие статус-коды (например, 0 для ошибок соединения).
# Сохраните все результаты в файл
# Пример использования:

import asyncio

urls = [
    "https://example.com",
    "https://httpbin.org/status/404",
    "https://nonexistent.url"
]


async def fetch_urls(urls: list[str], file_path: str):
    raise NotImplemented


if __name__ == '__main__':
    asyncio.run(fetch_urls(urls, './results.jsonl'))


# Пример файла results.json:
# {"url": "https://example.com", "status_code": 200}
# {"url": "https://httpbin.org/status/404", "status_code": 404}
# {"url": "https://nonexistent.url, "status_code": 0}
