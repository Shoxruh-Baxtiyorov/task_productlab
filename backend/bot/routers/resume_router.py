from psycopg import IntegrityError
from aiogram.fsm.state import State, StatesGroup
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import func
from sqlalchemy.orm import Session
from bot.services.segment_services import SegmentService
from bot.keyboards.resume_keyboards import question_keyboard
from bot.routers.subscribe_router import publish_search_task_message
from bot.services.s3_services import S3Services
from db.crud import CommonCRUDOperations as crud
from db.models import (Contract, ContractStatusType, Resume, Segment, Subscription, 
                       SubscriptionType, Task, User, UserSegment, RaitingChangeDirection,
                       UserSegmentReasonType, SubscriptionReasonType, SkillLevelType, RatingHistory)
from bot.services.document_parser import DocumentParser
from bot.services.rating_services import RatingService
import logging
from aiogram.exceptions import TelegramBadRequest
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ResumeStates(StatesGroup):
    waiting_for_resume = State()

r = Router(name='resume_router')


def _calculate_skill_level(claimed_tasks: int, completed_tasks: int) -> SkillLevelType:
    """Вычисляет уровень навыка на основе статистики"""
    if completed_tasks >= 3:
        return SkillLevelType.IN
    elif claimed_tasks > 0 and completed_tasks < 3:
        return SkillLevelType.WILL
    else:
        return SkillLevelType.WANT

ALLOWED_TYPES = [
    'application/pdf', 
    'text/html',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/rtf'
]

@r.message(Command("me"))
async def handle_me_command(message: types.Message, state: FSMContext):
    """Handle /me command - request resume upload"""
    try:
        await state.set_state(ResumeStates.waiting_for_resume)
        await message.answer(
            "Пожалуйста, приложите ваше резюме из hh.ru или другой платформы "
            "в формате pdf, html, docx или rtf для обогащения вашей карточки фрилансера.\n\n"
            "Или отправьте ссылку на резюме с hh.ru\n\n"
            "Это поможет нам предлагать вам максимально релевантные задачи и компании."
        )
    except TelegramBadRequest as e:
        logger.error(f"Telegram error in handle_me_command: {e}")
        await state.clear()

@r.message(ResumeStates.waiting_for_resume, F.text.regexp(r'https?://hh\.ru/resume/[a-zA-Z0-9]+'))
async def handle_hh_link(message: types.Message, state: FSMContext):
    """Handle HH.ru resume link"""
    # TODO: Implement HH.ru resume parsing
    await message.answer("Ссылка на резюме с HH.ru получена. В данный момент эта функция находится в разработке.")
    await state.clear()

@r.message(ResumeStates.waiting_for_resume, F.document)
async def handle_resume_upload(
    message: types.Message,
    state: FSMContext,
    db_session: Session,
    user: User,
    service_manager
):
    """Handle resume file upload"""
    document = message.document
    

    if document.mime_type not in ALLOWED_TYPES:
        if document.mime_type == 'application/msword':
            await message.answer(
                "❌ Формат DOC не поддерживается.\n\n"
                "Вы можете конвертировать его в DOCX "
                '<a href="https://cloudconvert.com/doc-to-docx">здесь</a> '
                "и отправить снова.",
                parse_mode="HTML"
            )
        else:
            await message.answer(
                "❌ Неподдерживаемый формат файла. "
                f"Получен формат: {document.mime_type}\n"
                "Пожалуйста, отправьте резюме в формате PDF, HTML, DOCX или RTF."
            )
        return

    try:
        file = await message.bot.get_file(document.file_id)
        file_content = await message.bot.download_file(file.file_path)
        
        file_bytes = file_content.read()
        
        parsed_text = DocumentParser.parse_document(file_bytes, document.mime_type)
        if not parsed_text:
            logger.error(f"Failed to parse document {document.file_name} of type {document.mime_type}")
            await message.answer(
                "❌ Не удалось извлечь текст из документа. "
                "Пожалуйста, убедитесь что документ содержит текст и попробуйте снова."
            )
            await state.clear()
            return

        
        file_content.seek(0)
        
        s3_client = S3Services()
        file_url = await s3_client.upload_file(
            object_name=f"resume_{document.file_name}",
            file=file_content,
            user_id=user.telegram_id
        )


        crud.deactivate_old_resumes(db_session, user.id)

        resume = crud.create_resume(
            session=db_session,
            user_id=user.id,
            file_url=file_url,
            file_type=document.mime_type,
            raw_text=parsed_text,
            source=None
        )

        # Проверяем, загружено ли резюме в течение часа после регистрации
        reward_given = False
        RESUME_REWARD_COMMENT = "Загрузка резюме в течение часа после регистрации"
        
        if user.registered_at:
            time_since_registration = datetime.now() - user.registered_at
            if time_since_registration <= timedelta(hours=1):
                # Проверяем, не был ли уже выдан бонус за загрузку резюме
                existing_reward = db_session.query(RatingHistory).filter(
                    RatingHistory.user_id == user.id,
                    RatingHistory.comment == RESUME_REWARD_COMMENT
                ).first()
                
                if not existing_reward:
                    # Награждаем пользователя 2 баллами только если раньше не награждали
                    await RatingService.user_rating_change(
                        session=db_session,
                        users_id=user.id,
                        change_direction=RaitingChangeDirection.PLUS,
                        score=2,
                        comment=RESUME_REWARD_COMMENT,
                    )
                    reward_given = True
        
        # Отменяем все напоминания о резюме
        await service_manager.rating_services.remove_resume_reminder_tasks(user.id)
        
        if reward_given:
            await message.answer(
                "✅ Ваше резюме успешно загружено и обработано!\n"
                "🎁 Вы получили 2 балла к рейтингу за быструю загрузку резюме!\n\n"
                "Теперь вы будете получать более релевантные предложения."
            )
        else:
            await message.answer(
                "✅ Ваше резюме успешно загружено и обработано! "
                "Теперь вы будете получать более релевантные предложения."
            )
 

        if "Навыки" in parsed_text:
            try:
                skills_text = parsed_text.split("Навыки")[-1].split("Дополнительная")[0].strip()
                final = [s for s in skills_text.split() if s.strip()]

                if len(final) > 0:
                    update_skills(db_session, final, user)
                    await state.update_data(resume_skills=final)

                    await message.answer(
                        f"""Мы обнаружили у вас {len(final)} доп.сегментов по вашему документу.
                        \nХотите чтобы мы вам создали сегменты и подписки по вашим навыкам?
                        \n{{{", ".join(final)}}}""",
                        reply_markup=question_keyboard()
                    )
                
                if "Обо мне" in parsed_text:
                    try:
                        bio = parsed_text.split("Обо мне")[-1].strip().split("Резюме обновлено")[0].strip()
                        update_bio(db_session, bio, user)
                    except Exception as e:
                        logger.error(f"Error get tbio of resume: {e}", exc_info=True) 
        

            except Exception as e:
                logger.error(f"Error get tags of resume: {e}", exc_info=True) 
        

    except Exception as e:
        logger.error(f"Error processing resume: {e}", exc_info=True) 
        await message.answer(
            "❌ Произошла ошибка при обработке файла. Пожалуйста, попробуйте позже."
        )
        await state.clear()

@r.message(ResumeStates.waiting_for_resume)
async def handle_invalid_resume(message: types.Message):
    await message.answer(
        "Пожалуйста, отправьте файл резюме в формате PDF, HTML, DOC или DOCX, "
        "или ссылку на резюме с hh.ru"
    ) 

@r.callback_query(F.data == "resume_question_yes")
async def handle_resume_question_yes(callback: types.CallbackQuery, state : FSMContext, db_session : Session, user : User):
    await callback.message.delete()

    data = await state.get_data()
    skills = data.get("resume_skills", [])

    subscription = Subscription(
        user_id=user.id,
        tags=skills,    
        budget_from = None,
        budget_to = None,
        type = SubscriptionType.OR,
        reason_added=SubscriptionReasonType.USER_RESUME,
        segments_processed=True,
        fromme=True
    )

    db_session.add(subscription)
    logger.info(f"[ResumeQuestionYes] Subscription created for user {user.id} with tags: {skills}")

    skills_lower = [s.lower() for s in skills]

    existing_user_segments = db_session.query(UserSegment).filter_by(user_id=user.id).all()
    existing_segment_ids = {us.segment_id for us in existing_user_segments}

    segments_in_db = db_session.query(Segment).filter(func.lower(Segment.name).in_(skills_lower)).all()
    existing_segment_names = {segment.name.lower() for segment in segments_in_db}

    missing_skills = [skill.lower() for skill in skills if skill.lower() not in existing_segment_names]
    for skill in missing_skills:
        new_segment = Segment(name=skill)
        db_session.add(new_segment)
    try:
        db_session.commit()
    except IntegrityError:
        db_session.rollback()
    finally:
        segments_in_db = db_session.query(Segment).filter(func.lower(Segment.name).in_(skills_lower)).all()



    for segment in segments_in_db:
        if segment.id not in existing_segment_ids:
            claimed = db_session.query(func.count(Contract.id)).join(Task).filter(
                Contract.freelancer_id == user.id,
                Task.description.ilike(f'%{segment.name}%')
            ).scalar() or 0

            completed = db_session.query(func.count(Contract.id)).join(Task).filter(
                Contract.freelancer_id == user.id,
                Contract.status == ContractStatusType.COMPLETED,
                Task.description.ilike(f'%{segment.name}%')
            ).scalar() or 0

            skill_level = _calculate_skill_level(claimed, completed)

            new_user_segment = UserSegment(
                user_id=user.id,
                segment_id=segment.id,
                claimed_tasks=claimed,
                completed_tasks=completed,
                skill_level=skill_level,
                reason_added=UserSegmentReasonType.USER_RESUME,
                fromme=True
            )
            db_session.add(new_user_segment)

    user_from_db = db_session.query(User).get(user.id)
    if user_from_db:
        user_from_db.fromme = True


    db_session.commit()

    logger.info(f"[ResumeQuestionYes] DB commit completed for user {user.id}")


    await callback.message.answer("Ваша подписка успешна добавлена")
    await publish_search_task_message(subscription)

    await state.clear()

@r.callback_query(F.data == "resume_question_no")
async def handle_resume_question_no(callback: types.CallbackQuery, state: FSMContext, db_session: Session, user: User):
    await callback.message.delete()
    user_from_db = db_session.query(User).filter_by(id=user.id).first()
    if user_from_db:
        user_from_db.fromme = False 
    segments_from_db = db_session.query(UserSegment).filter_by(user_id=user.id).first()
    if segments_from_db:
        segments_from_db.fromme = False
    subscription_from_db = db_session.query(Subscription).filter_by(user_id=user.id).first()
    if subscription_from_db:
        subscription_from_db.fromme = False

    db_session.commit()

    await state.clear()
    
def update_skills(db_session : Session, skills : list[str], user : User):
    user_from_bd = db_session.query(User).filter_by(id=user.id).first()
    if user_from_bd:
        user_from_bd.skills = skills
        db_session.commit()

def update_bio(db_session: Session, bio: str, user : User):
    user_from_bd = db_session.query(User).filter_by(id=user.id).first()
    if user_from_bd:
        user_from_bd.bio = bio
        db_session.commit()

@r.callback_query(F.data == "no_resume")
async def handle_no_resume(callback: types.CallbackQuery, db_session: Session, user: User, service_manager):
    """
    Обработчик кнопки 'У меня нет резюме'
    Отменяет все напоминания о загрузке резюме
    """
    try:
        await callback.message.delete()
    except Exception:
        pass
    
    # Отменяем все напоминания о резюме
    await service_manager.rating_services.remove_resume_reminder_tasks(user.id)
    
    await callback.bot.send_message(
        callback.from_user.id,
        "Хорошо, мы больше не будем напоминать вам о загрузке резюме.\n\n"
        "Вы всегда можете загрузить его позже используя команду /me"
    )
    