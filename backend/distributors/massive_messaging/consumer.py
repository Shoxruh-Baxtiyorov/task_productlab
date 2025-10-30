import aio_pika
import asyncio
import loader

from db.models import Distribution
from db.database import SessionLocal
from distributors.massive_messaging.distributor import deploy_new_distribution


async def massive_messaging_consumer():
    """
    Консюмер сообщений о новых рассылках
    """
    # создаем соединение
    while True:
        try:
            connection = await aio_pika.connect_robust(host=loader.RABBIT_HOST, port=5672, timeout=10)
        except:
            await asyncio.sleep(1)
        else:
            break
    async with connection:
        # берем канал
        channel = await connection.channel()

        # берем целевую очередь для принятия сообщений
        queue = await channel.declare_queue('new_distribution_started', auto_delete=True)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                # обработка поступающих сообщений
                async with message.process():
                    # берем сессию из БД
                    session = SessionLocal()
                    # получаем объект рассылки из БД
                    distribution = session.query(Distribution).filter(Distribution.id == int(message.body.decode())).first()
                    # запускаем рассылку
                    await deploy_new_distribution(distribution, session)
