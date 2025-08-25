# Задача - Реализация очереди задач на основе базы данных
# Контекст
# Вам необходимо реализовать функцию, которая будет извлекать задачи из очереди в базе данных в микросервисной системе, где несколько потоков могут одновременно обрабатывать задачи. Очередь представлена таблицей в базе данных, и важно обеспечить потокобезопасное извлечение задач для обработки, чтобы задачи не обрабатывались несколькими потоками одновременно.
#
# Цель задачи
# Создать функцию, которая будет безопасно извлекать строку задачи из таблицы очереди, заблокировав её для других потоков, и менять её статус на "в процессе" (или другой статус обработки).
#
# Описание модели очереди
# Предположим, у вас есть модель TaskQueue в Django, которая представляет задачу в очереди. Модель выглядит следующим образом:
#
from django.db import models

# models.py
class TaskQueue(models.Model):
    task_name = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default='pending')  # Статус задачи
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.task_name


from django.db import transaction, OperationalError
import time
import logging

logger = logging.getLogger(__name__)


def fetch_task(max_retries: int = 3, retry_delay: float = 0.1):
    """
    Потокобезопасное извлечение задачи из очереди с механизмом повторных попыток.
    Возвращает задачу со статусом 'in_progress' или None, если задач нет.

    Args:
        max_retries: Максимальное количество попыток при блокировке
        retry_delay: Задержка между попытками в секундах
    """
    for attempt in range(max_retries + 1):
        try:
            with transaction.atomic():
                task = TaskQueue.objects.select_for_update(
                    skip_locked=True
                ).filter(status='pending').order_by('created_at').first()

                if task:
                    task.status = 'in_progress'
                    task.save()
                    logger.info(
                        f"Задача {task.id} заблокирована и переведена в статус 'in_progress' (попытка {attempt + 1})")
                    return task
                else:
                    logger.debug("Нет доступных задач в статусе 'pending'")
                    return None

        except OperationalError as e:
            if attempt < max_retries:
                logger.warning(
                    f"Ошибка блокировки (попытка {attempt + 1}/{max_retries}): {e}. Повтор через {retry_delay}с")
                time.sleep(retry_delay)
                continue
            else:
                logger.error(f"Не удалось получить задачу после {max_retries} попыток: {e}")
                return None

        except Exception as e:
            logger.error(f"Критическая ошибка при получении задачи: {e}")
            return None

    return None

# • task_name — название задачи.
#
# • status — статус задачи. Статус может быть, например, pending (ожидает обработки) или in_progress (в процессе обработки).
#
# • created_at — дата и время создания задачи.
#
# • updated_at — дата и время последнего обновления задачи.
#
# Задание
# Напишите функцию fetch_task, которая будет:
#
# Ищет первую задачу с состоянием pending.
# После извлечения задачи изменяет её статус на in_progress и сохраняет изменения.
# Если задач с состоянием pending нет, функция должна возвращать None.
# Функция должна быть потокобезопасной, то есть должна корректно работать при параллельном доступе из нескольких потоков.