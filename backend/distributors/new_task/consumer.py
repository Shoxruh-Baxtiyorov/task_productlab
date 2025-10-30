import aio_pika
import asyncio
import loader

from db.database import SessionLocal
from db.models import Task
from distributors.new_task.distributor import send_new_task


async def new_task_consumer():
    """
    Консюмер сообщений о новых заказах
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
        # берем канал
        channel = await connection.channel()

        # берем целевую очередь для принятия сообщений
        queue = await channel.declare_queue('new_task_published', auto_delete=True)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                # обработка поступающих сообщений
                async with message.process():
                    # выводит айди нового заказа
                    print(message.body.decode())
                    # берем сессию из БД
                    session = SessionLocal()
                    # берем объект заказа
                    task = session.query(Task).filter(Task.id == int(message.body.decode())).first()
                    # список пользователей, которым подходит заказ
                    await send_new_task(task, session)
