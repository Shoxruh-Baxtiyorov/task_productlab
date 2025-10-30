from html import escape

from aiogram import Router, F, types
from aiogram.filters import Command

from bot.states.create_task_states import CreateTaskState
from bot.keyboards.create_task_keyboards import *
from db.models import User, Task
from db.crud import CommonCRUDOperations as crud

import aio_pika
import loader

from bot.utils.deadline_utils import deadline_message_validate, str_to_hours_converter, deadline_converted_output
from bot.states.create_task_states import AutoResponseState
from db.models import TaskAutoResponse

r = Router(name='create_task_router')


@r.message(Command('newtask'))
async def newtask_handler(msg, state):
    """
    Триггер на команду /newtask. Начинает форму заполнения нового заказа с заголовка.
    """
    await state.clear()
    await state.set_state(CreateTaskState.title)
    await msg.answer(
        'Дайте заголовок вашей задаче.'
    )



@r.message(Command('newhardtask'))
async def newhardtask_handler(msg, state):
    """
    Триггер на команду /newtask. Начинает форму заполнения нового заказа с заголовка.
    """
    await state.clear()
    await state.set_state(CreateTaskState.title)
    await state.update_data(is_hard=True)
    await msg.answer(
        'Дайте заголовок вашей задаче.'
    )


@r.message(CreateTaskState.title)
async def title_handler(msg, state):
    """
    Получает заголовок, запрашивает описание задачи.
    """
    await state.update_data(title=msg.text)
    await state.set_state(CreateTaskState.description)
    await msg.answer(
        'Максимально подробно опишите вашу задачу без внешних ссылок (кроме Notion, Google, Behance, Pinterest)'
    )


@r.message(CreateTaskState.description)
async def description_handler(msg, state):
    """
    Получает описание, запрашивает теги задачи.
    """
    await state.update_data(description=msg.text)
    await state.set_state(CreateTaskState.tags)
    await msg.answer(
        'Теперь отправьте теги для данной задачи (технологии, требования) через запятую. Пример:\n\n'
        '<b>figma, python, design, javascript</b>'
    )


@r.message(CreateTaskState.tags)
async def tags_handler(msg, state):
    """
    Получает теги, запрашивает бюджет задачи.
    """
    await state.update_data(tags=[tag.strip().lower() for tag in msg.text.split(',')])
    await state.set_state(CreateTaskState.price)
    await msg.answer(
        'Напишите бюджет проекта в формате {от}-{до}. Числа должны быть <b>БЕЗ ПРОБЕЛОВ</b>. '
        'Или выберите один из вариантов ниже👇',
        reply_markup=choose_budget()
    )


@r.message(CreateTaskState.price)
async def price_message_handler(msg, state):
    """
    Получает бюджет задачи (через ручное написание), запрашивает срок задачи.
    """
    try:
        budget_from = int(msg.text.split('-')[0])
        budget_to = int(msg.text.split('-')[1])
        assert budget_from <= budget_to
    except:
        await msg.answer(
            'Неправильный формат. Бюджет должен указывать в формате {от}-{до}. БЕЗ ПРОБЕЛОВ. Пример:\n\n'
            '55000-90000'
        )
    else:
        await state.update_data(budget_from=budget_from, budget_to=budget_to)
        await state.set_state(CreateTaskState.deadline)
        await msg.answer('Отправьте срок задачи (пример 10д 2ч, 12д, 5ч).')


@r.callback_query(CreateTaskState.price)
async def price_handler(cb, state):
    """
    Получает бюджет задачи (из предложенных вариантов), запрашивает срок задачи.
    """
    if cb.data == 'none':
        await state.update_data(budget_from=None, budget_to=None)
    else:
        budget = [int(i) for i in cb.data.split('-')]
        await state.update_data(budget_from=budget[0], budget_to=budget[1])
    await cb.message.delete()
    await state.set_state(CreateTaskState.deadline)
    await cb.message.answer('Напишите срок задачи (пример 10д 2ч, 12д, 5ч)')


@r.message(CreateTaskState.deadline)
async def deadline_handler(msg, state):
    """
    Получает срок задачи, запрашивает подтверждение данных заказа.
    """
    msg_validated = deadline_message_validate(msg.text)
    if not msg_validated:
        await msg.answer('Неправильный формат.')
    else:
        await state.update_data(deadline_days=str_to_hours_converter(msg_validated))
        data = await state.get_data()
        if data.get('is_hard'):
            await state.set_state(CreateTaskState.number_of_reminders)
            await msg.answer('Укажите количество напоминаний для задачи.')
        else:
            await confirm_task_sender(msg, state)


@r.message(CreateTaskState.number_of_reminders)
async def reminder_handler(msg, state):
    try:
        int(msg.text)
    except:
        return await msg.answer('Неправильный формат. Число должно быть ЦЕЛЫМ, БЕЗ ПРОБЕЛОВ.')
    else:
        await state.update_data(number_of_reminders=int(msg.text))
        await state.set_state(CreateTaskState.is_lite_offer)
        await msg.answer(
            f'<b>Доступен ли быстрый отклик?</b>'
            'выберите один из вариантов ниже👇',
            reply_markup=choose_allow_lite_offer()
        )


@r.callback_query(CreateTaskState.is_lite_offer)
async def is_lite_offer_handler(cb: types.CallbackQuery, state):
    match cb.data:
        case 'yes':
            await state.update_data(is_lite_offer=True)
        case _:
            await state.update_data(is_lite_offer=False)

    await state.set_state(CreateTaskState.private_content)
    await cb.message.answer(
        f'<b>Напиши ваш приватный контент, он будет виден исполнителю только после подписания контракта.</b>'
    )

@r.message(CreateTaskState.private_content)
async def private_content_handler(msg, state):
    private_content = msg.text
    await state.update_data(private_content=private_content)
    await confirm_task_sender(msg, state)

async def confirm_task_sender(event, state):
    """
    Метод для запроса подтверждения. Отправляет список параметров и предлагает вариант "подтвердить" и "сбросить"
    """
    task_data = await state.get_data()
    budget = f'от {task_data["budget_from"]}₽ до {task_data["budget_to"]}₽' if task_data["budget_from"] else 'по договору'

    number_of_reminders = (
        f'<b>Количество напоминаний</b>: {task_data["number_of_reminders"]}\n' if task_data.get('number_of_reminders') else ''
    )

    private_content = (
        f'<b>Приватные данные:</b> {task_data["private_content"]}\n\n' if task_data.get('private_content') else ''
    )
    await state.set_state(CreateTaskState.confirm)
    await event.bot.send_message(
        event.chat.id,
        f'<b>Подтвердите данные вашего заказа перед его публикацией:</b>\n\n'
        f'<b>Заголовок:</b> {escape(task_data.get("title"))}\n\n'
        f'<b>Описание:</b> {escape(task_data["description"])}\n\n'
        f'<b>Бюджет:</b> {budget}\n\n'
        f'<b>Срок:</b> {deadline_converted_output(task_data["deadline_days"])}\n\n'
        f'{number_of_reminders}'
        f'{private_content}'
        f'<b>Теги:</b> {", ".join(task_data["tags"])}\n\n',
        reply_markup=confirm_task()
    )


@r.callback_query(CreateTaskState.confirm)
async def confirm_task_handler(cb, state, db_session, user, bot, service_manager):
    """
    Метод для обработки подтверждения. В случае подтверждения заказа создает заказ и отправляет на рассылку. В случае сброса, сбрасывает
    """
    if cb.data == 'confirm':
        state_data = await state.get_data()

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
        await bot.send_message(user.telegram_id,
            'Для автоматического прием откликов по задаче выберите один из вариантов ниже👇',
            reply_markup=choose_auto_response()
        )
        await state.clear()
        await state.set_state(AutoResponseState.select)
        await state.update_data(task_id=task.id)
        await service_manager.rating_services.update_rating_weekly_tasks(user.id)
    else:
        await cb.message.edit_text(
            'Ваша задача сброшена. Создать заново: /newtask',
            reply_markup=None
        )
        await state.clear()



@r.callback_query(AutoResponseState.select)
async def all_auto_response_handler(cb, db_session, state):
    """
    Обработка выбора автоматического приема откликов
    """
    try:
        if not cb.data in ['all', 'rules', 'pass']:
            return
            
        data = await state.get_data()
        task_id = data.get('task_id')
        
        task = crud.get_task_by_id(session=db_session, task_id=task_id)
        if not task:
            await cb.message.edit_text('Ошибка: задача не найдена', reply_markup=None)
            await state.clear()
            return


        if cb.data == 'all':
            task.all_auto_responses = True
            db_session.commit()

            await cb.message.edit_text(
                'Отклики по задаче будут приниматься автоматически.\n'
                'Каждый исполнитель, который откликнется, будет автоматически принят.'
            )
            await state.clear() 

        elif cb.data == 'rules':
            await state.set_state(AutoResponseState.budget)
            await cb.message.edit_text(
                'Напишите бюджет проекта в формате {от}-{до}. Числа должны быть <b>БЕЗ ПРОБЕЛОВ</b>. '
                'Или выберите один из вариантов ниже👇',
                reply_markup=choose_budget()
            )
        else: 
            task.all_auto_responses = False
            db_session.commit()
            
            await state.clear()  
            await cb.message.edit_text(
                'Ждите откликов по задаче.',
                reply_markup=None
            )

    except Exception as e:
        await cb.answer("Произошла ошибка при обработке автоматического приема")
        await state.clear()


@r.message(AutoResponseState.budget)
async def budget_message_handler(msg, state):
    """
    Получает бюджет в рамках которого будет автоматический прием откликов (через ручное написание),
    запрашивает срок выполнения задачи.
    """
    try:
        budget_from = int(msg.text.split('-')[0])
        budget_to = int(msg.text.split('-')[1])
        assert budget_from <= budget_to
    except:
        await msg.answer(
            'Неправильный формат. Бюджет должен указывать в формате {от}-{до}. БЕЗ ПРОБЕЛОВ. Пример:\n\n'
            '55000-90000'
        )
    else:
        await state.update_data(budget_from=budget_from, budget_to=budget_to)
        await state.set_state(AutoResponseState.deadline_days)
        await msg.answer('Отправьте максимальный срок выполнения проекта(пример 10д 2ч, 12д, 5ч), '
                         'в рамках которого будет автоматический прием откликов.')


@r.callback_query(AutoResponseState.budget)
async def budget_handler(cb, state):
    """
    Получает бюджет в рамках которого будет автоматический прием откликов (из предложенных вариантов),
    запрашивает срок выполнения задачи.
    """
    if cb.data == 'none':
        await state.update_data(budget_from=0, budget_to=10000000)
    else:
        budget = [int(i) for i in cb.data.split('-')]
        await state.update_data(budget_from=budget[0], budget_to=budget[1])
    await cb.message.delete()
    await state.set_state(AutoResponseState.deadline_days)
    await cb.message.answer('Отправьте максимальный срок выполнения проекта(пример 10д 2ч, 12д, 5ч), '
                            'в рамках которого будет автоматический прием откликов.')


@r.message(AutoResponseState.deadline_days)
async def deadline_days_message_handler(msg, state):
    """
    Получает срок выполнения задачи в рамках которого будет автоматический прием откликов
    (через ручное написание), запрашивает количество исполнителей.
    """
    msg_validated = deadline_message_validate(msg.text)
    if not msg_validated:
        await msg.answer('Неправильный формат.')
    else:
        await state.update_data(deadline_days=str_to_hours_converter(msg_validated))
        await state.set_state(AutoResponseState.qty_freelancers)
        await msg.answer('Отправьте максимальное количество исполнителей.')


@r.message(AutoResponseState.qty_freelancers)
async def qty_freelancers_handler(msg, state):
    """
    Получает количество исполнителей, запрашивает подтверждение
    данных по Автоматическому приему откликов
    """
    try:
        int(msg.text)
        assert 1 <= int(msg.text) <= 100
    except:
        await msg.answer('Неправильный формат. Число дней должно быть ЦЕЛЫМ, от 1 до 100.')
    else:
        await state.update_data(qty_freelancers=int(msg.text))
        await confirm_auto_response_sender(msg, state)


async def confirm_auto_response_sender(event, state):
    """
    Метод для запроса подтверждения. Отправляет список параметров и предлагает вариант "подтвердить" и "сбросить"
    """
    auto_response_data = await state.get_data()
    budget = f'от {auto_response_data["budget_from"]}₽ до {auto_response_data["budget_to"]}₽'

    await state.set_state(AutoResponseState.confirm)
    await event.bot.send_message(
        event.chat.id,
        f'<b>Подтвердите данные Автоматического приема откликов:</b>\n\n'
        f'<b>Бюджет:</b> {budget}\n\n'
        f'<b>Срок:</b> {deadline_converted_output(auto_response_data["deadline_days"])}\n\n'
        f'<b>Количество исполнителей:</b> {auto_response_data["qty_freelancers"]}\n\n',
        reply_markup=confirm_task()
    )


@r.callback_query(AutoResponseState.confirm)
async def confirm_auto_response_handler(cb, state, db_session):
    """
    Метод для обработки подтверждения. Подтверждение данных по Автоматическому приему откликов.
    В случае сброса, сбрасывает
    """
    state_data = await state.get_data()
    task_id = state_data.get('task_id')
    if cb.data == 'confirm':
        auto_response = TaskAutoResponse(
            **state_data,
        )
        db_session.add(auto_response)
        db_session.commit()
        await cb.message.edit_text(
            f'Отклики по задаче будут приниматься автоматически по указанным параметрам.',
            reply_markup=None
        )
        await state.clear()
    else:
        await cb.massage.answer(
            'Для автоматического прием откликов по задаче выберите один из вариантов ниже👇',
            reply_markup=choose_auto_response()
        )
        await state.clear()
        await state.set_state(AutoResponseState.select)
        await state.update_data(task_id=task_id)



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
