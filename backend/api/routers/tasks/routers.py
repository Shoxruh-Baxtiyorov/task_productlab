from fastapi import APIRouter
from fastapi.responses import JSONResponse
from api.routers.tasks.freelancer_tasks.routers import router as freelancer_tasks_router
from api.routers.tasks.client_tasks.routers import router as client_tasks_router

router = APIRouter(prefix='/tasks')

# готовый ответ в случае, если заказа не существует
task_not_found_response = JSONResponse({'error': 'Task with such id not found.'}, status_code=404)

# добавляем роутер событий
router.include_router(
    freelancer_tasks_router,
    prefix='/freelancer'
)
router.include_router(
    client_tasks_router,
    prefix='/client'
)

