from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware, types
from sqlalchemy.orm import Session, sessionmaker
from db.database import engine

class DatabaseMiddleware(BaseMiddleware):
    """Middleware для работы с базой данных"""
    
    async def __call__(
        self,
        handler: Callable[[types.Message, Dict[str, Any]], Awaitable[Any]],
        event: types.Message | types.CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        session = sessionmaker(engine, class_=Session, expire_on_commit=False)()
        
        data['db_session'] = session
        
        try:
            return await handler(event, data)
        finally:
            session.close() 