from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi import UploadFile
from sqlalchemy import or_, and_

from .schemas import CreateMessageSchema, GetMessageSchema
from .crud import CRUD

from db.crud import CommonCRUDOperations
from db.models import Message, MessageContextType, Task

import aioboto3
import loader
import datetime
import io


BUCKET_NAME = "5075293c-06104489-fcfa-4939-9926-1fb7a99fb903"

s3_session = aioboto3.Session()
s3_data = {
    'service_name': 's3',
    'endpoint_url': loader.S3_ENDPOINT_URL,
    "aws_access_key_id": loader.S3_KEY_ID,
    "aws_secret_access_key": loader.S3_SECRET_KEY
}

def set_interlocutor(msg, user):
    if msg.author_id == user.id:
        msg.interlocutor_id = msg.receiver_id
        msg.interlocutor = msg.receiver
    else:
        msg.interlocutor_id = msg.author_id
        msg.interlocutor = msg.author
    return msg


def get_dialogs_service(session, user, task_id):
    interlocutor_ids = CRUD.get_interlocutors_crud(session, user)
    dialogs = []
    for inter in interlocutor_ids:
        if not task_id:
            last_msg = CRUD.get_last_message_crud(session, user, inter[0])
        else:
            last_msg = CRUD.get_task_last_message(session, user, inter[0], task_id)
        if last_msg:
            dialogs.append(
                set_interlocutor(last_msg, user)
            )
    return dialogs


def send_message_service(session, user, message: CreateMessageSchema):
    if message.context == MessageContextType.TASK:
        if not message.task_id:
            return JSONResponse({'error': 'Id of task for which you send message, must be included.'}, status_code=400)
        
        task = session.query(Task).filter(Task.id == message.task_id).first()
        if not task:
            return JSONResponse({'error': 'Task not found.'}, status_code=400)
            
    elif message.context == MessageContextType.OFFER:
        if not message.offer_id:
            return JSONResponse({'error': 'Id of offer for which you send message, must be included.'}, status_code=400)
        offer = CommonCRUDOperations.get_offer_any_participant_by_id(session, user, message.offer_id)
        if not offer:
            return JSONResponse({'error': 'Offer not found.'}, status_code=400)
            
    msg = set_interlocutor(
        CommonCRUDOperations.create_message(session, author_id=user.id, **dict(message)),
        user
    )
    return JSONResponse(
        {'ok': f'Message sent.', 'message': jsonable_encoder(dict(GetMessageSchema.model_validate(msg)))},
        status_code=201)


async def send_attachment_service(session, user, message_id, files: list[UploadFile]):
    message = CommonCRUDOperations.get_my_message_by_id(session, user, message_id)
    if not message:
        return JSONResponse({'error': 'Message not found!'}, status_code=404)
    async with s3_session.client(**s3_data) as s3:
        time = int(datetime.datetime.now().timestamp())
        j = 0
        for file in files:
            j += 1
            file_bytes = await file.read()
            msg_file = CommonCRUDOperations.create_message_file(
                session,
                key=f'{message.id}_{time}_{j}',
                bucket_name=BUCKET_NAME,
                path=file.filename,
                message_id=message.id
            )
            await s3.upload_fileobj(io.BytesIO(file_bytes), BUCKET_NAME, msg_file.key)
            msg_file.is_uploaded = True
        session.commit()
        await s3.close()
    return JSONResponse({'ok': 'Files uploaded'})


def get_messages_service(session, user, **kwargs):
    if kwargs['context'] == MessageContextType.TASK:
        if not kwargs['task_id']:
            return JSONResponse({'error': 'Task id must be provided.'}, status_code=400)
        task = CommonCRUDOperations.get_task_any_participant_by_id(session, user, kwargs['task_id'])
        if not task:
            return JSONResponse({'error': 'Task not found.'}, status_code=404)
        msg_q = CRUD.query_task_messages(session, user, task, kwargs['interlocutor_id'])
    else:
        if not kwargs['offer_id']:
            return JSONResponse({'error': 'Offer id must be provided.'}, status_code=400)
        offer = CommonCRUDOperations.get_offer_any_participant_by_id(session, user, kwargs['offer_id'])
        if not offer:
            return JSONResponse({'error': 'Offer not found.'}, status_code=404)
        msg_q = CRUD.query_offer_messages(session, user, offer, kwargs['interlocutor_id'])
    if kwargs['ids'] != 'all':
        try:
            msg_q = msg_q.where(
                Message.id.in_([int(s) for s in kwargs['ids'].split(',')])
            )
        except ValueError:
            return JSONResponse({'error': 'Wrong ids syntax. Ids must contain integers separated by comma'},
                                status_code=422)
    if kwargs['author_id']:
        msg_q = msg_q.where(Message.author_id == kwargs['author_id'])
    if kwargs['offset']:
        msg_q = msg_q.offset(kwargs['offset'])
    if kwargs['limit']:
        msg_q = msg_q.limit(kwargs['limit'])
    res = []
    for msg in msg_q.all():
        res.append(
            set_interlocutor(msg, user)
        )
    return res


def delete_message_service(session, user, message_id):
    message = CRUD.get_my_message_by_id(session, user, message_id)
    if not message:
        return JSONResponse({'error': 'Task event not found.'}, status_code=404)
    CRUD.delete_message(session, message)
    return JSONResponse({'ok': 'Message deleted.'}, status_code=200)
