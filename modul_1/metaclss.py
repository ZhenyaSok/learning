# Задача - Атрибуты класса
# Напишите метакласс, который автоматически добавляет атрибут created_at с текущей датой и временем к
# любому классу,
# который его использует.

from datetime import datetime

class AutoCreatedAtMeta(type):
    def __new__(cls, name, bases, namespace):
        # Добавляем атрибут created_at с текущей датой и временем
        namespace['created_at'] = datetime.now()
        return super().__new__(cls, name, bases, namespace)

# Пример использования метакласса
class MyClass(metaclass=AutoCreatedAtMeta):
    pass

# Проверяем, что атрибут created_at был добавлен
print(MyClass.created_at)  # Выведет текущую дату и время создания класса