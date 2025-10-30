from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
from sqlalchemy.orm import Session
from db.models import User
from db.database import SessionLocal

from api.routers.users.freelancer.routers import router as freelancer_router
from api.routers.users.schemas import UserSchema

router = APIRouter(prefix='/users', tags=['users'])


@router.get('', response_model=UserSchema)
async def get_me(request: Request, token: str):
    return request.state.user


@router.post('/set_windows_client')
async def set_client(request: Request, token: str):
    """
    Пометить себя как пользователя виндоус приложения Deadline Bot
    :param request: запрос
    :param token: токен авторизации
    :return: 200
    """
    if request.state.user.has_windows_client:
        return JSONResponse({'ok': 'Already set.'})
    request.state.user.has_windows_client = True
    request.state.session.commit()
    return JSONResponse({'ok': 'Windows client set.'})


@router.get("/check/{telegram_id}")
async def check_user(telegram_id: int):
    # Создаем сессию базы данных
    db = SessionLocal()
    try:
        # Проверяем существование пользователя в базе и его статус регистрации
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if not user or not user.is_registered:
            raise HTTPException(status_code=403, detail="User not registered")
        return {"is_registered": True}
    finally:
        db.close()

# вложение роутера по фрилансерам
router.include_router(freelancer_router, prefix='/freelancer')
