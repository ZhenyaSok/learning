# Задача - Поиск элемента в упорядоченном списке
# Дан отсортированный список чисел, например: [1, 2, 3, 45, 356, 569, 600, 705, 923]
#
# Список может содержать миллионы элементов.
#
# Необходимо написать функцию search(number: id) -> bool которая принимает число number и возвращает
# True если это число находится в этом списке.
#
# Требуемая сложность алгоритма O(log n).

my_nums = [1, 2, 3, 45, 356, 569, 600, 705, 923]

my_number = 45


def search(nums, number):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == number:
            print(True)
            return True
        elif nums[mid] < number:
            left = mid + 1
        else:
            right = mid - 1
    print(False)
    return False


search(my_nums, my_number)
