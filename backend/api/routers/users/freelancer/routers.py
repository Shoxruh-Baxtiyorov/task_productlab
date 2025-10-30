from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from api.routers.users.freelancer.schemas import UpdateFreelancerBioSchema

router = APIRouter()


@router.post('/bio')
async def update_bio(request: Request, token: str, update_freelancer_bio: UpdateFreelancerBioSchema):
    """
    Изменить био
    \f
    :param request: запрос
    :param token: токен авторизации
    :param update_freelancer_bio: форма изменения био
    :return:
    """
    request.state.user.bio = update_freelancer_bio.new_bio
    request.state.session.commit()
    return JSONResponse({'ok': 'Your bio changed.'})
