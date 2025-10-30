from concurrent.futures import ThreadPoolExecutor
import re
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Set

import pytz
from sqlalchemy import func

from db.database import SessionLocal
from db.models import (
    Contract, User, ContractStatusType, RoleType,
    UserSegment, Subscription, SubscriptionStatusType, Task, Segment,
    SkillLevelType, UserSegmentReasonType
)
from bot.services.scheduler.scheduler_services import SchedulerServices
import loader
import asyncio

logger = logging.getLogger(__name__)


class SegmentService:
    SEARCH_REGEX = r"[a-zA-Z\.\-\#\+]+"
    MIN_SEGMENT_THRESHOLD = 10  # минимальное кол-во упоминаний для нового сегмента

    def __init__(self, scheduler_services: SchedulerServices):
        self.scheduler_services = scheduler_services
        self.bot = loader.bot
        self.moscow_tz = pytz.timezone("Europe/Moscow")
        self.executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="segment_service")

    # ---------------------------
    # PUBLIC METHODS
    # ---------------------------
    async def parse_segments(self):
        """Парсит сегменты по всем пользователям"""
        logger.info("Start parsing segments")

        try:

            await asyncio.get_running_loop().run_in_executor(
                self.executor,
                self._sync_parse_segments,
            )

            await self.add_user_segments()
            logger.info("Segment parsing and user sync completed")
        except Exception as e:
            logger.error(f"Segment parsing failed: {e}")
        

    def _sync_parse_segments(self):

        with SessionLocal() as session:
            overall_segments = self._collect_segments(session)
            self._compare_and_store_segments(session, overall_segments)


    async def add_user_segments(self):
        """Синхронизирует сегменты у пользователей"""
        logger.info("Start syncing user segments")
        await asyncio.get_running_loop().run_in_executor(
            self.executor,
            self._sync_add_user_segments,
        )

    def _sync_add_user_segments(self):
        with SessionLocal() as session:
            all_segments = session.query(Segment).all()
            segment_name_to_id = {seg.name.lower(): seg.id for seg in all_segments}

            users = session.query(User).filter(
                User.is_blocked.is_(False),
                User.is_registered.is_(True),
                User.is_dead.is_(False),
                User.roles.contains([RoleType.FREELANCER])
            ).yield_per(100)

            for user in users:
                # Get segments with their sources
                segment_sources = self._extract_user_segments_with_sources(session, user, segment_name_to_id)

                existing_segments = session.query(UserSegment).filter(
                    UserSegment.user_id == user.id
                ).all()
                existing_map = {us.segment_id: us for us in existing_segments}

                self._sync_user_segments(session, user.id, segment_sources, existing_map)

            session.commit()
            logger.info("User segments sync finished")

    async def prepare_task(self):
        """Запланировать задачу"""
        self.scheduler_services.add_job(
            object_id=0,
            task_name="segment parsing",
            run_date=self.current_date + timedelta(seconds=60),
            method=self.parse_segments,
            method_name="parse_segments",
            interval=None,
        )

    # ---------------------------
    # PRIVATE HELPERS
    # ---------------------------
    def _collect_segments(self, session) -> Dict[str, int]:
        """Собирает сегменты по всем пользователям"""
        overall_segments = defaultdict(int)

        users = session.query(User).filter(
            User.is_blocked.is_(False),
            User.is_registered.is_(True),
            User.is_dead.is_(False),
            User.roles.contains([RoleType.FREELANCER])
        ).yield_per(100)

        for user in users:
            segments = self._extract_user_segments(session, user)
            for seg in segments:
                overall_segments[seg] += 1

        return overall_segments

    def _extract_user_segments(self, session, user: User, segment_name_to_id: Dict[str, int] = None) -> Set[int] | Set[str]:
        """Вытаскивает сегменты пользователя (как строки или как id, если передан словарь)"""
        segments = set()

        # skills
        if user.skills:
            segments.update(skill.strip().lower() for skill in user.skills if skill)

        # bio
        if user.bio:
            segments.update(match.group().lower() for match in re.finditer(self.SEARCH_REGEX, user.bio))

        # subscriptions
        subscriptions = session.query(Subscription).filter(
            Subscription.user_id == user.id,
            Subscription.status == SubscriptionStatusType.SEND,
        ).all()
        for sub in subscriptions:
            if sub.tags:
                segments.update(tag.lower() for tag in sub.tags)

        # contracts
        contracts = session.query(Contract).filter(Contract.freelancer_id == user.id).yield_per(100)
        for contract in contracts:
            if contract.task:
                if contract.task.description:
                    segments.update(
                        match.group().lower() for match in re.finditer(self.SEARCH_REGEX, contract.task.description)
                    )
                if contract.task.tags:
                    segments.update(tag.lower() for tag in contract.task.tags)

        if segment_name_to_id:
            return {segment_name_to_id[s] for s in segments if s in segment_name_to_id}
        return segments

    def _extract_user_segments_with_sources(self, session, user: User, segment_name_to_id: Dict[str, int]) -> Dict[int, UserSegmentReasonType]:
        """Вытаскивает сегменты пользователя с указанием источника
        
        Returns:
            Dict mapping segment_id -> reason (priority: TASK_OFFER > USER_RESUME > USER_SUBSCRIBED > USER_BIO > USER_SKILLS)
        """
        segment_sources = {}  # segment_id -> reason (with priority)
        
        # Helper to add with priority (higher value = higher priority)
        reason_priority = {
            UserSegmentReasonType.USER_SKILLS: 1,
            UserSegmentReasonType.USER_BIO_DESCRIPTIONS: 2,
            UserSegmentReasonType.USER_SUBSCRIBED: 3,
            UserSegmentReasonType.USER_RESUME: 4,
            UserSegmentReasonType.TASK_OFFER: 5,
        }
        
        def add_segment(segment_name: str, reason: UserSegmentReasonType):
            if segment_name in segment_name_to_id:
                seg_id = segment_name_to_id[segment_name]
                if seg_id not in segment_sources or reason_priority[reason] > reason_priority.get(segment_sources[seg_id], reason):
                    segment_sources[seg_id] = reason

        # skills
        if user.skills:
            for skill in user.skills:
                if skill:
                    add_segment(skill.strip().lower(), UserSegmentReasonType.USER_SKILLS)

        # bio
        if user.bio:
            for match in re.finditer(self.SEARCH_REGEX, user.bio):
                add_segment(match.group().lower(), UserSegmentReasonType.USER_BIO_DESCRIPTIONS)

        # subscriptions
        subscriptions = session.query(Subscription).filter(
            Subscription.user_id == user.id,
            Subscription.status == SubscriptionStatusType.SEND,
        ).all()
        for sub in subscriptions:
            if sub.tags:
                reason = UserSegmentReasonType.USER_RESUME if sub.fromme else UserSegmentReasonType.USER_SUBSCRIBED
                for tag in sub.tags:
                    add_segment(tag.lower(), reason)

        # contracts (task offers)
        contracts = session.query(Contract).filter(Contract.freelancer_id == user.id).yield_per(100)
        for contract in contracts:
            if contract.task:
                if contract.task.description:
                    for match in re.finditer(self.SEARCH_REGEX, contract.task.description):
                        add_segment(match.group().lower(), UserSegmentReasonType.TASK_OFFER)
                if contract.task.tags:
                    for tag in contract.task.tags:
                        add_segment(tag.lower(), UserSegmentReasonType.TASK_OFFER)

        return segment_sources

    def _compare_and_store_segments(self, session, overall_segments: Dict[str, int]):
        """Добавляет новые сегменты в БД"""
        existing = {seg.name.lower() for seg in session.query(Segment).all()}

        new_segments = []

        for seg_name, count in overall_segments.items():
            seg_name_lower = seg_name.lower()

            if (count >= self.MIN_SEGMENT_THRESHOLD  and
                seg_name_lower not in existing and
                len(seg_name_lower) >= 2):
                new_segments.append(Segment(name=seg_name_lower))
                existing.add(seg_name_lower)


        if new_segments:
            session.add_all(new_segments)
            session.commit()

            logger.info(f"Added {len(new_segments)} new segments: {[seg.name for seg in new_segments]}")
           

            asyncio.run_coroutine_threadsafe(
                self._notify_admins([seg.name for seg in new_segments]),
                asyncio.get_running_loop()
            )

    def _sync_user_segments(self, session, user_id: int, segment_sources: Dict[int, UserSegmentReasonType], existing_map: Dict[int, UserSegment]):
        """Синхронизирует сегменты пользователя"""
        old_ids = set(existing_map.keys())
        new_ids = set(segment_sources.keys())

        # удалить лишние
        for seg_id in old_ids - new_ids:
            session.delete(existing_map[seg_id])

        # добавить новые
        for seg_id in new_ids - old_ids:
            claimed, completed = self._calc_segment_stats(session, user_id, seg_id)
            skill_level = self._calculate_skill_level(claimed, completed)
            reason_added = segment_sources[seg_id]
            
            session.add(UserSegment(
                user_id=user_id,
                segment_id=seg_id,
                claimed_tasks=claimed,
                completed_tasks=completed,
                skill_level=skill_level,
                reason_added=reason_added,
                fromme=False,
                created_at=datetime.now(self.moscow_tz),
                updated_at=datetime.now(self.moscow_tz),
            ))

        # обновить существующие
        for seg_id in old_ids & new_ids:
            user_segment = existing_map[seg_id]
            claimed, completed = self._calc_segment_stats(session, user_id, seg_id)
            skill_level = self._calculate_skill_level(claimed, completed)
            
            # Update if stats or skill_level changed
            if (user_segment.claimed_tasks != claimed or 
                user_segment.completed_tasks != completed or
                user_segment.skill_level != skill_level):
                user_segment.claimed_tasks = claimed
                user_segment.completed_tasks = completed
                user_segment.skill_level = skill_level
                user_segment.updated_at = datetime.now(self.moscow_tz)
            
            # Update reason if not set
            if user_segment.reason_added is None:
                user_segment.reason_added = segment_sources[seg_id]

    def _calc_segment_stats(self, session, user_id: int, seg_id: int):
        """Считает статистику по сегменту"""
        segment = session.get(Segment, seg_id)
        if not segment:
            return 0, 0

        claimed = session.query(func.count(Contract.id)).join(Task).filter(
            Contract.freelancer_id == user_id,
            Task.description.ilike(f"%{segment.name}%"),
        ).scalar() or 0

        completed = session.query(func.count(Contract.id)).join(Task).filter(
            Contract.freelancer_id == user_id,
            Contract.status == ContractStatusType.COMPLETED,
            Task.description.ilike(f"%{segment.name}%"),
        ).scalar() or 0

        return claimed, completed

    def _calculate_skill_level(self, claimed_tasks: int, completed_tasks: int) -> SkillLevelType:
        """Вычисляет уровень навыка на основе статистики
        
        WANT: 0 claimed, 0 completed (хочет попробовать)
        WILL: >0 claimed, <3 completed (в процессе)
        IN: >=3 completed (в теме)
        """
        if completed_tasks >= 3:
            return SkillLevelType.IN
        elif claimed_tasks > 0 and completed_tasks < 3:
            return SkillLevelType.WILL
        else:
            return SkillLevelType.WANT

    async def _notify_admins(self, segments: Set[str]):
        for admin in loader.ADMINS:
            try:
                await self.bot.send_message(admin, "Обнаружены новые сегменты:\n" + "\n".join(segments))
            except Exception as e:
                logger.error(f"Failed to notify admin {admin}: {e}")

    @property
    def current_date(self):
        return datetime.now(self.moscow_tz)
