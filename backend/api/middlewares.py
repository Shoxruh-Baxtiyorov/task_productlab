from starlette.requests import Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse

from db.models import User
from db.database import SessionLocal


class FetchUserMiddleware(BaseHTTPMiddleware):
    """
    Middleware для проверки токена и подготовки сессии БД
    """

    async def dispatch(self, request: Request, call_next):
        """
        Готовит сессию БД и проверяет токен пользователя
        :param request: запрос пользователя
        :param call_next: функция эндпоинта
        :return: ответ эндпоинта
        """

        root_path = "/api/v1"
        path = request.url.path.rstrip('/')
        if path.startswith(root_path):
            path = path[len(root_path):] or '/'

        if path in [
            '/docs', 
            '/openapi.json', 
            '/health',
            '/segments', 
            '/tasks/freelancer/available',
            '/users/check'
        ] or path.startswith('/segments/freelancer_type_segments/') or path.startswith('/users/check/'):
            return await call_next(request)

        session = SessionLocal()
        token = request.query_params.get('token')
        try:
            user = session.query(User).filter(User.token == token).first()
        except:
            user = None
        if not user:
            session.close()
            return JSONResponse({'error': 'You have to pass token to access this app.'}, status_code=401)
        request.state.user = user
        request.state.session = session
        resp = await call_next(request)
        session.close()
        return resp
