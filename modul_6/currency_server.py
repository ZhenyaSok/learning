
# запустив программу в файле, можем перейти по http://127.0.0.1:8000/USD
# 3 символа после слеша означают сокращение валюты

# Можно запустить tkinter_currency увидим минимальный интерфейс для взаимодействия
import http.server
import socketserver
import urllib.request
import urllib.error
import json
from urllib.parse import urlparse
import sys

PORT = 8000  # можно поменять на любой свободный порт


class CurrencyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Разбираем путь без query-параметров
        path = urlparse(self.path).path  # только часть до ?
        currency = path.strip("/").upper()

        # Игнорируем favicon.ico
        if currency == "FAVICON.ICO":
            self.send_response(204)  # No Content
            self.end_headers()
            return

        # Проверяем код валюты: ровно 3 буквы
        if not (currency.isalpha() and len(currency) == 3):
            self.send_response(400)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(
                json.dumps({"error": "Invalid currency code"}, ensure_ascii=False).encode("utf-8")
            )
            return

        try:
            # Запрашиваем данные из внешнего API (с таймаутом)
            url = f"https://api.exchangerate-api.com/v4/latest/{currency}"
            with urllib.request.urlopen(url, timeout=5) as response:
                data = response.read().decode("utf-8")
                json_data = json.loads(data)

            # Добавляем источник
            json_data["provider"] = "https://www.exchangerate-api.com"

            # Отправляем успешный ответ
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(json_data, ensure_ascii=False).encode("utf-8"))

        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(
                json.dumps(
                    {"error": f"Currency not found or API error: {e.reason}"},
                    ensure_ascii=False,
                ).encode("utf-8")
            )
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(
                json.dumps({"error": str(e)}, ensure_ascii=False).encode("utf-8")
            )


if __name__ == "__main__":
    try:
        with socketserver.ThreadingTCPServer(("", PORT), CurrencyHandler) as httpd:
            print(f"✅ Server is running at http://localhost:{PORT}")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        sys.exit(0)
