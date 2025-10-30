from html import escape

from aiogram import Router
from aiogram.filters import Command

from bot.states.create_task_states import CreateLiteTaskState
from bot.keyboards.create_task_keyboards import *
from db.models import User, Task

import aio_pika
import loader


r = Router(name='lite_task_router')


@r.message(CreateLiteTaskState.lite_tags)
async def lite_tags_handler(msg, state):
    """
    Получает теги, запрашивает бюджет задачи.
    """
    await state.update_data(tags=[tag.strip().lower() for tag in msg.text.split(',')])
    await confirm_lite_task_sender(msg, state, msg.chat.id)
    data = await state.get_data()

    await msg.bot.delete_message(chat_id=msg.chat.id, message_id=data['msg_to_delete'])


@r.message()
async def newlite_task(msg, bot, state):
    """
    Создает новую lite задачу когда бота тегают в реплае на сообщение
    """
    if msg.reply_to_message:
        # Получаем информацию о боте заранее
        bot_info = await bot.get_me()
        bot_username = f"@{bot_info.username}"
        
        # Проверяем, что бота упомянули в сообщении (тегнули)
        if msg.entities and any(
            entity.type == "mention" and 
            entity.extract_from(msg.text) == bot_username
            for entity in msg.entities
        ):
            # Берем текст из оригинального сообщения
            original_text = msg.reply_to_message.text
            
            # Сохраняем текст как заголовок задачи
            await state.update_data(title=original_text)
            
            # Отправляем сообщение о создании задачи
            await msg.answer(
                f'<b>Создаю задачу новую</b>: {original_text}\n\n'
                f'Вы можете добавить теги к задаче?',
                reply_markup=litetask_tags_keyboard()
            )

async def confirm_lite_task_sender(event, state, chat_id):
    """
    Метод для запроса подтверждения. Отправляет список параметров и предлагает вариант "подтвердить" и "сбросить"
    """
    task_data = await state.get_data()

    await state.set_state(CreateLiteTaskState.confirm)
    await event.bot.send_message(
        chat_id,
        f'<b>Подтвердите данные вашего заказа перед его публикацией:</b>\n\n'
        f'<b>Заголовок:</b> {escape(task_data["title"])}\n\n'
        f'<b>Теги:</b> {", ".join(task_data["tags"])}\n',
        reply_markup=confirm_task()
    )

@r.callback_query(CreateLiteTaskState.confirm)
async def confirm_task_handler(cb, state, db_session, user):
    """
    Метод для обработки подтверждения. В случае подтверждения заказа создает заказ и отправляет на рассылку. В случае сброса, сбрасывает
    """
    if cb.data == 'confirm':
        state_data = await state.get_data()


        if state_data.get('msg_to_delete'):
            state_data.pop('msg_to_delete')

        task = Task(
            author_id=user.id,
            **state_data,
        )
        db_session.add(task)
        db_session.commit()
        await publish_new_task(task)
        await cb.message.edit_text(
            f'Ваша задача успешно создана и опубликована. Она доступна в боте по ссылке {loader.BOT_ADDRESS}?start=task{task.id}',
            reply_markup=None
        )
    else:
        await cb.message.edit_text(
            'Ваша задача сброшена. Создать заново: /newtask',
            reply_markup=None
        )
    await state.clear()


async def publish_new_task(task):
    """
    Продюсер, отправляющий сообщение в консюмер для новых заказов
    """
    # устанавливаем соединение
    connection = await aio_pika.connect_robust(host=loader.RABBIT_HOST, port=5672, timeout=10)
    async with connection:
        # название очереди, вроде как
        routing_key = 'new_task_published'
        # получаем канал
        channel = await connection.channel()
        # публикуем сообщение о новом заказе
        await channel.default_exchange.publish(
            aio_pika.Message(body=str(task.id).encode()),
            routing_key=routing_key
        )


@r.callback_query()
async def lite_tags_callback_handler(cb, state):
    if cb.data == 'add_tags':
        await state.set_state(CreateLiteTaskState.lite_tags)
        msg = await cb.message.answer(
            'Теперь отправьте теги для данной задачи (технологии, требования) через запятую. Пример:\n\n'
            '<b>figma, python, design, javascript</b>'
        )
        await state.update_data(msg_to_delete=msg.message_id)

    if cb.data == 'pass_tags':
        await cb.message.delete()
        await state.update_data(tags=[str(cb.message.chat.id)])
        await confirm_lite_task_sender(cb, state, cb.message.chat.id)

