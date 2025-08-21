# через механизм импортов

from singleton_module import instance

# Использование синглтона
instance.value = 10
print(instance.value)

# В другом месте программы
from singleton_module import instance as same_instance

print(instance is same_instance)  # True
print(same_instance.value)  # 10
