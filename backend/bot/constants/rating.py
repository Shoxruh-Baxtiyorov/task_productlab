import logging


REGISRATION_RATING_INCREASE = 10
REGISRATION_RATING_INCREASE_COMMENT = "Увеличение рейтинга за регистрацию."
WEEKLY_RATING_DECREASE = 1
WEEKLY_RATING_DECREASE_COMMENT = "Еженедельное уменьшение рейтинга за бездействие."
WORKING_HOURS = (9, 22)
MONTHLY_RATING_BONUS = 1
MONTHLY_RATING_BONUS_COMMENT = "Получение ежемесячного бонуса."
DEADLINE_RATING_DECREASE = 1
DEADLINE_RATING_DECREASE_COMMENT = "Снижение рейтинга за нарушение сроков выполнения."
CANCELTASK_RATING_DECREASE = 1
CANCELTASK_RATING_DECREASE_COMMENT = "Снижение рейтинга за отказ от задачи."
MIN_RATING_FOR_WORK = 5
FINISH_WORK_RATING_INCREASE = 0.1
FINISH_WORK_RATING_INCREASE_COMMENT = "Увеличение рейтинга за выполненную работу."
USERS_INVOLVEMENT_RATING_INCREASE = 1
USERS_INVOLVEMENT_RATING_INCREASE_COMMENT = "Увеличение рейтинга за привлечение нового пользователя."
USERS_INVOLVEMENT_RATING_DECREASE = 1
USERS_INVOLVEMENT_RATING_DECREASE_COMMENT = "Снижение рейтинга за неактивность привлечённого пользователя."
TEXT_RATING_INFO = (
    "Система баллов и рейтинга /rating\n"
    "Начисление:\n"
    "Автоматом за регистрацию <b>10 баллов.</b>\n"
    "Каждый месяц <b>1 балл</b> по кнопке, срок жизни кнопки <b>1 час</b>. Рандомно.\n\n"
    "За срыв сроков: <b>-1 балл</b> и блокировка на <b>7 дней</b>.\n"
    "Каждые <b>7 дней</b> снимается <b>1 балл</b>, если нет активных задач или выполненных за <b>7 дней</b>.\n\n"
    # "Если баланс меньше <b>5 баллов</b> нельзя откликаться на новые задачи или/и создавать их.\n"
    # "Если бот заблокирован вами, рейтинг обнуляется и ставится  черная метка.\n\n"
    "За выполнение каждой задачи исполнителю и заказчику дается <b>0.1 балл</b>.\n\n"
    "Как восстановить рейтинг, если он обнулился? Пригласите вашего знакомого и получите <b>1 балл</b> на ваш счет.\n"
    "Если приглашённый друг уйдёт, то вы потеряете <b>1 балл</b>.\n"
    "Минимальное количество для отклика или создания задачи <b>5 баллов</b>."
)

LOGGING = {
    'level': logging.INFO,
    'format': '[%(asctime)s] %(levelname)-8s %(message)s',
    'datefmt': '%d.%m.%y %I:%M:%S',
}
