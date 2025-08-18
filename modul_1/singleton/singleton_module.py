# через механизм импортов

class _SingletonClass:
    def __init__(self, value):
        self.value = value


instance = _SingletonClass(0)  # Создаем единственный экземпляр