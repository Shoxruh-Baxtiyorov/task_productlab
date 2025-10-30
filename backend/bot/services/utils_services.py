from sqlalchemy import and_
from db.crud import CommonCRUDOperations as crud
from db.models import Contract, ContractStatusType, CountryType, Message, MessageContextType, MessageSourceType, Offer, PaymentType, JuridicalType
from html import escape
import loader

from bot.utils.deadline_utils import deadline_message_validate, str_to_hours_converter, deadline_converted_output


class UtilsServices:
    def time_until(self, time_left):
            days_left = time_left.days
            hours_left, remainder = divmod(time_left.seconds, 3600)
            minutes_left, _ = divmod(remainder, 60)

            # Окончания для дней
            day_endings = ["день", "дня", "дней"]

                # Окончания для часов
            hour_endings = ["час", "часа", "часов"]

                # Окончания для минут
            minute_endings = ["минута", "минуты", "минут"]

                # Логика вывода оставшегося времени
            if days_left >= 1:
                return (f"{days_left} {self._get_ending(days_left, day_endings)} "
                            f"и {hours_left} {self._get_ending(hours_left, hour_endings)}.")
            elif hours_left >= 1:
                return (f"{hours_left} {self._get_ending(hours_left, hour_endings)} "
                            f"и {minutes_left} {self._get_ending(minutes_left, minute_endings)}.")
            else:
                return f"{minutes_left} {self._get_ending(minutes_left, minute_endings)}."

    @staticmethod
    def _get_ending(number, endings):
        if 11 <= number % 100 <= 14:
            return endings[2]
        else:
            i = number % 10
            if i == 1:
                return endings[0]
            elif 2 <= i <= 4:
                return endings[1]
            else:
                return endings[2]

    def get_reply_offer_msg(self, session, user, offer, profile_photo, is_private_chat):
        #days_word = self._get_ending(number=offer.deadline_days, endings=["день", "дня", "дней"])

        # Проверяем источник таска (группа/личка)
        is_from_group = str(offer.task.author.telegram_id).startswith('-100')
        
        # Базовая информация, которая будет показана везде
        basic_info = (
            f'<b>У вас новый отклик на задачу!</b>\n\n'
            f'<b>Название задачи</b>: {escape(offer.task.title)}\n'
            f'<b>Исполнитель</b>: {user.full_name} @{user.username}\n'
            f'<b>Срок</b>: {deadline_converted_output(offer.deadline_days)}\n'
            f'<b>Бюджет</b>: {offer.budget} руб.\n'
        )

        # Если таск из группы - возвращаем краткую информацию + компактные ссылки
        # if is_from_group:
        #     return basic_info + (
        #         f'\n<a href="{loader.URL}/offers?token={offer.task.author.token}&task_id={offer.task_id}">отклики задачи</a> / '
        #         f'<a href="{loader.URL}/offers?token={offer.task.author.token}">все отклики</a> / '
        #         f'<a href="{loader.URL}/tasks?token={offer.task.author.token}">все задачи</a> / '
        #         f'<a href="{loader.URL}/docs">api</a>'
        #     )
        
        # Для тасков из личных сообщений возвращаем полную информацию
        user_country = user.country if user.country else ''
        location = (
            f"Россия" if user_country == CountryType.RUSSIA.value else "Другое"
        ) if user_country else ''

        user_payment_types = user.payment_types if user.payment_types else []

        payment_types = ', '.join(
            [
                "Сбербанк" if pt == PaymentType.SBER.value else ''
                "Самозанятый" if pt == PaymentType.SELF_EMPLOYED.value else ''
                "Криптовалюта" if pt == PaymentType.CRYPTO.value else ''
                "Безналичный расчет" if pt == PaymentType.NONCASH.value else ''
                for pt in user_payment_types
            ]
        ).strip(', ')

        user_juridical_type = user.juridical_type if user.juridical_type else []
        juridical_type = ', '.join(
            [
                'Индивидуальный предприниматель' if user_juridical_type == JuridicalType.IP.value else ''
                'Самозанятый' if user_juridical_type == JuridicalType.SELF_EMPLOYED.value else ''
                'ООО' if user_juridical_type == JuridicalType.OOO.value else ''
                'Физическое лицо' if user_juridical_type == JuridicalType.PHYSICAL.value else ''
            ]

        ).strip(', ')

        contracts = crud.get_contracts_by_user_id(session, user.id)

        last_nps = 0
        sum_nps = 0
        cnt_nps = 0

        cnt_contracts = 0
        cnt_miss_contracts = 0

        cnt_cancel_contracts = 0


        contracts_with = ""
        # Находим последнюю оценку
        for contract in reversed(contracts):
            if contract.evaluate is not None:
                last_nps = contract.evaluate
                break
        
        # Вычисляем среднюю оценку
        for contract in contracts:
            if contract.evaluate is not None:
                sum_nps += contract.evaluate
                cnt_nps += 1
                
            # Соравны сроки и зданы в срок    
            if not contract.miss_deadline and contract.status == ContractStatusType.COMPLETED:
                cnt_contracts += 1
            elif contract.miss_deadline:
                cnt_miss_contracts += 1
            
            # отменено после оффера
            if contract.status == ContractStatusType.CANCELLED:
                cnt_cancel_contracts += 1

            


        avg_nps = round(sum_nps/cnt_nps, 1) if cnt_nps else 0

        # количество откликов

        responses_count = session.query(Offer).where(
            and_(
                Offer.author_id == user.id
            )
        ).count()

        contract_c = session.query(Contract).where(and_(Contract.task_id == offer.task.id,
                                                  Contract.status != ContractStatusType.CANCELLED)).all()

        for contract in contract_c:
            contracts_with += f"{contract.freelancer.full_name} -> @{contract.freelancer.username} {contract.budget} руб.\n"
                
        t = "Нет подписаных договоров\n"
        
        return basic_info + (
            f'<b>Описание задачи</b>: {escape(offer.description)}\n\n'
            f'<b>Фото</b>: {"есть" if profile_photo else "нет"}\n'
            f'<b>Локация</b>: {location}\n'
            f'<b>Тип оплаты</b>: {payment_types or "Тип оплаты не указан"}\n'
            f'<b>Тип лица</b>: {juridical_type or "Тип лица не указан"}\n'
            f'<b>Количество договоров</b>: {crud.get_contract_count_by_user_id(session, user.id)}\n'
            f'<b>Количество откликов</b>: {crud.get_offer_count_by_user_id(session, user.id)}\n'
            f'<b>Сделал задач для вас</b>: {crud.get_contract_count_by_user_and_client(session, user.id, offer.task.author_id)}\n'
            f'<b>Сделал задач для вас на сумму</b>: {crud.get_contract_sum_by_user_and_client(session, user.id, offer.task.author_id)}\n\n'
            f'<b>Последний NPS текущего откликнувшегося</b>: {last_nps}\n'
            f'<b>Средний NPS текущего откликнувшегося</b>: {avg_nps}\n'
            f'<b>Сдано задач в срок</b>: {cnt_contracts}\n'
            f'<b>Порваны дедлайны на задачах</b>: {cnt_miss_contracts}\n'
            f'<b>Отказ от задач после получения оффера</b>: {cnt_cancel_contracts}\n\n'
            f'<b>Количество откликов прошлых</b>: {responses_count-1 if  responses_count-1 > -1 else 0}\n'
            f'<b>Количество откликов с учетом текущей</b>: {responses_count}\n'
            f'<b>Количество договоров всего</b>: {len(contracts)}\n'
            f'<b>Уже подписаны договора с</b>: \n{t if contracts_with == "" else contracts_with}'
            f'<b>Заказчик</b>: {offer.task.author.full_name} @{offer.task.author.username}\n'
            f'<b>Согласованная сумма договора</b>: {offer.budget} руб.\n'
            f'Дата регистрации: {user.created_at.strftime("%d.%m.%Y")}\n\n'
            f'Статистика:\n{offer.task.emoji_status}\n\n'
            f'Отклики по данной задаче: {loader.URL}/offers?token={offer.task.author.token}&task_id={offer.task_id}\n\n'
            f'Отклик по всем задачам: <a href="{loader.URL}/offers?token={offer.task.author.token}">тут</a>\n'
            f'Все ваши задачи: <a href="{loader.URL}/tasks?token={offer.task.author.token}">тут</a>\n'
            f'API-документация: <a href="{loader.URL}/docs">тут</a>\n\n'
            f'Ваш токен: <code>{offer.task.author.token}</code>\n\n'
        )