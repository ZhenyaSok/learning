import tkinter as tk
from tkinter import messagebox
import urllib.request
import json


def fetch_currency():
    currency = entry.get().strip().upper()

    if len(currency) != 3:
        messagebox.showerror(
            "Ошибка", "Введите 3-буквенный код валюты (например: USD, EUR)"
        )
        return

    try:
        with urllib.request.urlopen(
            f"https://api.exchangerate-api.com/v4/latest/{currency}"
        ) as response:
            data = json.loads(response.read().decode("utf-8"))
            data["provider"] = "https://www.exchangerate-api.com"

            # Отображаем JSON в текстовом поле с форматированием
            text.delete(1.0, tk.END)
            text.insert(tk.END, json.dumps(data, indent=2))

    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось получить данные: {str(e)}")


# Создаем главное окно
root = tk.Tk()
root.title("Курсы валют")

# Поле ввода
tk.Label(root, text="Введите код валюты (3 буквы):").pack()
entry = tk.Entry(root, width=10)
entry.pack()

# Кнопка запроса
tk.Button(root, text="Получить курс", command=fetch_currency).pack()

# Текстовое поле для вывода JSON
text = tk.Text(root, width=80, height=30)
text.pack()

root.mainloop()
