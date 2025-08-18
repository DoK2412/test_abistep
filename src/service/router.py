from fastapi import APIRouter, Query


from .views import create_user, receive_users, create_transfer
from .model_request import User, Transfer

from path import USER, TRANSFER

router_api = APIRouter()


@router_api.post(USER, tags=["service"])
async def user(user_data: User):
    result = await create_user(user_data)
    return result

@router_api.get(USER, tags=["service"])
async def users():
    result = await receive_users()
    return result

@router_api.post(TRANSFER, tags=["service"])
async def transfer(data: Transfer):
    result = await create_transfer(data)
    return result
