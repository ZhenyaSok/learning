#Задача - Очередь
# Реализуйте класс очереди который использует редис под капотом

import redis
import json


class RedisQueue:
    def __init__(self, name="queue", host="localhost", port=6379, db=0):
        self.redis = redis.StrictRedis(host=host, port=port, db=db, decode_responses=True)
        self.name = name

    def publish(self, msg: dict):
        """Добавить сообщение в очередь"""
        self.redis.rpush(self.name, json.dumps(msg))

    def consume(self) -> dict:
        """Забрать сообщение из очереди"""
        data = self.redis.lpop(self.name)
        if data is None:
            return None
        return json.loads(data)


if __name__ == '__main__':
    q = RedisQueue()

    q.publish({'a': 1})
    q.publish({'b': 2})
    q.publish({'c': 3})

    assert q.consume() == {'a': 1}
    assert q.consume() == {'b': 2}
    assert q.consume() == {'c': 3}

    print("✅ Все проверки прошли успешно")