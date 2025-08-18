# Задача - Синглтон
# Реализуйте паттерн синглтон тремя способами:
#
# с помощью метаклассов
class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class SingletonClass(metaclass=SingletonMeta):
    def __init__(self, value):
        self.value = value

# Пример использования
s1 = SingletonClass(10)
s2 = SingletonClass(20)
print(s1 is s2)  # True, потому что это один и тот же объект
print(s1.value)  # 10, потому что второй вызов конструктора игнорируется


# с помощью метода __new__ класса
class SingletonClsNew(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, value):
        self.value = value


# Пример использования
s1 = SingletonClsNew(10)
s2 = SingletonClsNew(20)
print(s1 is s2)  # True
print(s2.value)  # 20, потому что __init__ вызывается каждый раз

# Добавляю еще один метод (для себя)
# Метод 4: Декоратор

def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance



@singleton
class SingletonClassDec:
    def __init__(self, value):
        self.value = value


# Пример использования
s3 = SingletonClassDec(10)
s4 = SingletonClassDec(20)
print(s3 is s4)  # True - это один и тот же объект
print(s3.value)  # 10 (второй вызов конструктора не изменяет существующий экземпляр)