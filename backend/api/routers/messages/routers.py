from fastapi import APIRouter, Request, UploadFile

from .schemas import CreateMessageSchema, GetMessageSchema
from .services import (
    send_message_service,
    send_attachment_service,
    get_messages_service,
    delete_message_service,
    get_dialogs_service
)

from db.models import Task, MessageType, MessageContextType, Message, MessageSourceType

router = APIRouter(prefix='/messages', tags=['Messages'])


@router.post('')
async def send_message(
        request: Request,
        token: str,
        message: CreateMessageSchema):
    return send_message_service(request.state.session, request.state.user, message)


@router.post('/{message_id}/files')
async def send_message_attachment(request: Request, token: str, message_id: int, files: list[UploadFile]):
    return await send_attachment_service(request.state.session, request.state.user, message_id, files)


@router.get('', response_model=list[GetMessageSchema])
async def get_messages(
        request: Request,
        token: str,
        interlocutor_id: int,
        context: MessageContextType | None = None,
        task_id: int | None = None,
        offer_id: int | None = None,
        ids: str | None = 'all',
        author_id: int | None = None,
        message_type: MessageType | None = None,
        source_type: MessageSourceType | None = None,
        offset: int | None = None,
        limit: int = 100
):
    return get_messages_service(
        request.state.session,
        request.state.user,
        interlocutor_id=interlocutor_id,
        context=context,
        task_id=task_id,
        offer_id=offer_id,
        ids=ids,
        author_id=author_id,
        message_type=message_type,
        source_type=source_type,
        offset=offset,
        limit=limit
    )


@router.delete('/{message_id}')
async def delete_message(request: Request, token: str, message_id: int):
    return delete_message_service(request.state.session, request.state.user, message_id)


@router.get('/dialogs', response_model=list[GetMessageSchema])
async def get_dialogs(request: Request, token: str, task_id: int | None = None):
    return get_dialogs_service(request.state.session, request.state.user, task_id)
