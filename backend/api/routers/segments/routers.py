from enum import Enum
from fastapi import APIRouter, Query
from sqlalchemy import func, distinct, and_

from db.database import SessionLocal
from db.models import Segment, UserSegment, User, Rating

router = APIRouter(prefix='/segments', tags=['segments'])


class FreelancerTypes(Enum):
    WANT = "WANT"
    WILL = "WILL"
    IN = "IN"


@router.get('')
async def get_segments():
    with SessionLocal() as session:
        segments = session.query(
            Segment,
            func.count(distinct(UserSegment.user_id)).label('users_count')
        ).outerjoin(
            UserSegment,
            Segment.id == UserSegment.segment_id
        ).group_by(
            Segment.id
        ).all()
        
        return [
            {
                "id": segment.id,
                "name": segment.name,
                "users": users_count
            }
            for segment, users_count in segments
        ]


@router.get("/freelancer_type/{segment}")
async def get_freelancer_type(freelancer_type: FreelancerTypes, segment: str, token: str):
    with SessionLocal() as session:
        query = session.query(UserSegment, User) \
            .join(User, UserSegment.user_id == User.id) \
            .join(Segment, UserSegment.segment_id == Segment.id) \
            .filter(Segment.name == segment)

        from db.models import SkillLevelType
        
        if freelancer_type == FreelancerTypes.WANT:
            return [{"segment": i[0], "user": i[1]} for i in query.filter(
                UserSegment.skill_level == SkillLevelType.WANT).all()]
        elif freelancer_type == FreelancerTypes.WILL:
            return [{"segment": i[0], "user": i[1]} for i in query.filter(
                UserSegment.skill_level == SkillLevelType.WILL).all()]
        elif freelancer_type == FreelancerTypes.IN:
            return [{"segment": i[0], "user": i[1]} for i in query.filter(
                UserSegment.skill_level == SkillLevelType.IN).all()]


@router.get("/freelancer_type_segments/{segment}")
async def get_freelancer_type_segments(
    freelancer_type: FreelancerTypes, 
    segment: str
):
    with SessionLocal() as session:
        segment_obj = session.query(Segment).filter(Segment.name == segment).first()
        if not segment_obj:
            return []

        from db.models import SkillLevelType
        
        query = session.query(UserSegment, User, Segment, Rating) \
            .join(User, UserSegment.user_id == User.id) \
            .join(Segment, UserSegment.segment_id == Segment.id) \
            .outerjoin(Rating, User.id == Rating.user_id) \
            .filter(
                Segment.name == segment,
                UserSegment.segment_id == segment_obj.id
            )

        if freelancer_type == FreelancerTypes.WANT:
            users = query.filter(UserSegment.skill_level == SkillLevelType.WANT).all()
        elif freelancer_type == FreelancerTypes.WILL:
            users = query.filter(UserSegment.skill_level == SkillLevelType.WILL).all()
        elif freelancer_type == FreelancerTypes.IN:
            users = query.filter(UserSegment.skill_level == SkillLevelType.IN).all()

        return [{
            "segment": {
                "id": i[0].id,
                "name": i[2].name,
                "completed_tasks": i[0].completed_tasks,
                "claimed_tasks": i[0].claimed_tasks,
            },
            "user": {
                "id": i[1].id,
                "full_name": i[1].full_name,
                "username": i[1].username,
                "bio": i[1].bio,
                "skills": i[1].skills,
                "prof_level": i[1].prof_level,
                "rating": float(i[3].score) if i[3] else None,
                "avatar": i[1].profile_photo_url,
                "payment_types": i[1].payment_types,
                "country": i[1].country,
                "registered_at": i[1].registered_at
            }           
        } for i in users]
