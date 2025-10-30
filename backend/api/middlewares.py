from starlette.requests import Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse

from db.models import User
from db.database import SessionLocal


class FetchUserMiddleware(BaseHTTPMiddleware):
    """
    Middleware for verifying user token and preparing DB session.
    """

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if any(path.endswith(p) for p in ["/openapi.json", "/docs", "/redoc"]):
            return await call_next(request)

        public_paths = [
            "/api/v1/health",
            "/api/v1/tasks/freelancer/available",
            "/api/v1/segments",
            "/api/v1/users/check",
        ]
        if path in public_paths or \
           path.startswith("/api/v1/segments/freelancer_type_segments/") or \
           path.startswith("/api/v1/users/check/"):
            return await call_next(request)

        session = SessionLocal()
        token = request.query_params.get("token")
        user = None

        if token:
            try:
                user = session.query(User).filter(User.token == token).first()
            except Exception:
                user = None

        if not user:
            session.close()
            return JSONResponse({'error': 'You have to pass token to access this app.'}, status_code=401)

        request.state.user = user
        request.state.session = session

        response = await call_next(request)

        session.close()
        return response
