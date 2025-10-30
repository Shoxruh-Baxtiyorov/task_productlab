import aio_pika
import asyncio

from distributors.search_tasks.distributor import send_tasks
from db.database import SessionLocal
from db.models import Subscription

import loader


async def search_tasks_consumer():
    """
    Консюмер принимающий сообщения о поиске заказов по подписке
    """
    # создаем соединение
    while True:
        try:
            print(loader.RABBIT_HOST)
            connection = await aio_pika.connect_robust(host=loader.RABBIT_HOST, port=5672, timeout=10)
        except:
            await asyncio.sleep(1)
        else:
            break
    async with connection:
        # создаем канал
        channel = await connection.channel()

        # берем очередь, от которой нужно смотреть сообщения
        queue = await channel.declare_queue('search_tasks', auto_delete=True)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                # обработка сообщений
                async with message.process():
                    # берем сессию БД
                    session = SessionLocal()
                    # берем подписку
                    subscription = session.query(Subscription).filter(Subscription.id == int(message.body.decode())).first()
                    # список актуальных заказов, подходящих подписке
                    await send_tasks(subscription, session)


if __name__ == '__main__':
    asyncio.run(search_tasks_consumer())

