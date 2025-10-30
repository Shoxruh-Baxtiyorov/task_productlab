from aiogram import BaseMiddleware


class AdminMiddleware(BaseMiddleware):
    """
    Этот middleware для хендлеров админов. Получает белый список админов и если юзер состоит в этом списке,
    выполняет команду
    """
    def __init__(self, admins):
        self.admins = admins

    async def __call__(self, handler, event, data):
        """
        Метод вызываемый миддлварем, проверяет состоит ли юзер в списке админов
        :param handler: хендлер
        :param event: событие, обновление
        :param data: данные хендлера
        :return: хендлер
        """
        if event.from_user.id in self.admins:
            return await handler(event, data)
