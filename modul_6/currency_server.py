import http.server
import socketserver
import urllib.request
import json


PORT = 8000
# запустив программу в файле, можем перейти по http://127.0.0.1:8000/USD
# 3 символа после слеша означают сокращение валюты

# Можно запустить tkinter_currency увидим минимальный интерфейс для взаимодействия


class CurrencyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Извлекаем код валюты из URL (например, /USD -> USD)
        currency = self.path.strip("/").upper()

        if not currency or len(currency) != 3:
            self.send_response(400)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid currency code"}).encode())
            return

        try:
            # Запрашиваем данные из внешнего API
            with urllib.request.urlopen(
                f"https://api.exchangerate-api.com/v4/latest/{currency}"
            ) as response:
                data = response.read().decode("utf-8")
                json_data = json.loads(data)

                # Добавляем информацию о провайдере
                json_data["provider"] = "https://www.exchangerate-api.com"

                # Отправляем ответ
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(json_data).encode())

        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps(
                    {"error": f"Currency not found or API error: {e.reason}"}
                ).encode()
            )
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())


with socketserver.TCPServer(("", PORT), CurrencyHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
