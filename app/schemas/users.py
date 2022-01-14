from typing import Optional

from app.schemas.base import APIBaseSchema, APIBaseCreateSchema


class UserSchema(APIBaseSchema):
    wallet_address: Optional[str]
    ens_name: Optional[str]
    email: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "id": "61e17018c3ee162141baf5c8",
                "wallet_address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
                "ens_name": "vitalik.eth",
                "email": "test@newshades.xyz",
            }
        }


class UserCreateSchema(APIBaseCreateSchema):
    wallet_address: str = ""

    class Config:
        schema_extra = {
            "example": {
                "wallet_address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
                "email": "test@newshades.xyz",
            }
        }
