from typing import Union

from bson import ObjectId

from app.helpers.w3 import get_wallet_short_name
from app.models.base import APIDocument
from app.models.user import User
from app.schemas.users import UserCreateSchema
from app.services.crud import get_item, get_item_by_id


async def create_user(user_model: UserCreateSchema, fetch_ens: bool = False) -> User:
    user = User(**user_model.dict())
    if not user_model.display_name:
        display_name = await get_wallet_short_name(address=user_model.wallet_address, check_ens=fetch_ens)
        user.display_name = display_name
    await user.commit()
    return user


async def get_user_by_wallet_address(wallet_address: str) -> Union[User, APIDocument]:
    user = await get_item(filters={"wallet_address": wallet_address}, result_obj=User)
    return user


async def get_user_by_id(user_id) -> Union[User, APIDocument]:
    if isinstance(user_id, ObjectId):
        user_id = str(user_id)
    elif isinstance(user_id, str):
        pass
    else:
        raise Exception(f"unexpected user_id type: {type(user_id)}")

    return await get_item_by_id(id_=user_id, result_obj=User)
