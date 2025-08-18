import asyncio
import aiohttp
import json
from typing import Dict, List
from tqdm.asyncio import tqdm_asyncio

input_file = "urls.txt"
output_file = "results.jsonl"

async def fetch_url(
        url: str,
        session: aiohttp.ClientSession,
        semaphore: asyncio.Semaphore
) -> Dict[str, int]:
    try:
        async with semaphore:
            async with session.get(url, timeout=1) as response:
                return {"url": url, "status_code": response.status}
    except (aiohttp.ClientError, asyncio.TimeoutError):
        return {"url": url, "status_code": 0}
    except Exception:
        return {"url": url, "status_code": 0}


async def fetch_urls(urls: List[str], file_path: str) -> List[Dict[str, int]]:
    semaphore = asyncio.Semaphore(5)
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(url, session, semaphore) for url in urls]
        results = await tqdm_asyncio.gather(*tasks, desc="Processing URLs")

    with open(file_path, "w") as f:
        for result in results:
            f.write(json.dumps(result) + "\n")
    return results


if __name__ == '__main__':
    urls = [
        "https://example.com",
        "https://httpbin.org/status/404",
        "https://nonexistent.url"
    ]
    asyncio.run(fetch_urls(urls, output_file))

# import asyncio
#
# urls = [
#     "https://example.com",
#     "https://httpbin.org/status/404",
#     "https://nonexistent.url"
# ]
#
#
# async def fetch_urls(urls: list[str], file_path: str):
#     raise NotImplemented
#
#
# if __name__ == '__main__':
#     asyncio.run(fetch_urls(urls, './results.jsonl'))


# Пример файла results.json:
# {"url": "https://example.com", "status_code": 200}
# {"url": "https://httpbin.org/status/404", "status_code": 404}
# {"url": "https://nonexistent.url, "status_code": 0}
