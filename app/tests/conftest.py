import binascii
import secrets
from typing import Union

import arrow
import pytest
from asgi_lifespan import LifespanManager
from eth_account import Account
from eth_account.messages import encode_defunct
from fastapi import FastAPI
from httpx import AsyncClient
from web3 import Web3

from app.helpers.connection import get_client, get_db
from app.main import get_application
from app.models.base import APIDocument
from app.models.channel import Channel
from app.models.server import Server
from app.models.user import User
from app.schemas.channels import DMChannelCreateSchema, ServerChannelCreateSchema
from app.schemas.messages import MessageCreateSchema
from app.schemas.servers import ServerCreateSchema
from app.schemas.users import UserCreateSchema
from app.services.auth import generate_wallet_token
from app.services.channels import create_dm_channel, create_server_channel
from app.services.messages import create_message
from app.services.servers import create_server
from app.services.users import create_user


@pytest.fixture
def app() -> FastAPI:
    app = get_application(testing=True)
    return app


@pytest.fixture
async def client(app: FastAPI) -> AsyncClient:
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://testserver", follow_redirects=True) as client:
            yield client


@pytest.fixture
async def db(app, client):
    db_client = await get_client()
    db = await get_db()
    await db_client.drop_database(db.name)
    yield db
    await db_client.drop_database(db.name)


@pytest.fixture
def private_key() -> bytes:
    key = secrets.token_bytes(32)
    return key


@pytest.fixture
def wallet(private_key: bytes) -> str:
    priv = binascii.hexlify(private_key).decode("ascii")
    private_key = "0x" + priv
    acct = Account.from_key(private_key)
    return acct.address


@pytest.fixture
async def current_user(private_key: bytes, wallet: str) -> User:
    return await create_user(UserCreateSchema(wallet_address=wallet), fetch_ens=False)


@pytest.fixture
async def guest_user() -> User:
    key = secrets.token_bytes(32)
    priv = binascii.hexlify(key).decode("ascii")
    private_key = "0x" + priv
    acct = Account.from_key(private_key)
    return await create_user(UserCreateSchema(wallet_address=acct.address), fetch_ens=False)


@pytest.fixture
async def server(current_user: User) -> Union[Server, APIDocument]:
    server_model = ServerCreateSchema(name="NewShades DAO")
    return await create_server(server_model, current_user=current_user)


@pytest.fixture
async def server_channel(current_user: User, server: Server) -> Union[Channel, APIDocument]:
    server_channel = ServerChannelCreateSchema(kind="server", server=str(server.id), name="testing-channel")
    return await create_server_channel(server_channel, current_user=current_user)


@pytest.fixture
async def dm_channel(current_user: User, server: Server) -> Union[Channel, APIDocument]:
    dm_channel = DMChannelCreateSchema(kind="dm", members=[str(current_user.id)])
    return await create_dm_channel(dm_channel, current_user=current_user)


@pytest.fixture
async def channel_message(current_user: User, server: Server, server_channel: Channel):
    message = MessageCreateSchema(server=str(server.id), channel=str(server_channel.id), content="hey")
    return await create_message(message, current_user=current_user)


@pytest.fixture
async def authorized_client(client: AsyncClient, private_key: bytes, current_user: User) -> AsyncClient:
    nonce = 1234
    signed_at = arrow.utcnow().isoformat()
    message = f"""NewShades wants you to sign in with your web3 account

    {current_user.wallet_address}

    URI: localhost
    Nonce: {nonce}
    Issued At: {signed_at}"""

    encoded_message = encode_defunct(text=message)
    signed_message = Web3().eth.account.sign_message(encoded_message, private_key=private_key)

    data = {
        "message": message,
        "signature": signed_message.signature.hex(),
        "signed_at": signed_at,
        "nonce": nonce,
        "address": current_user.wallet_address,
    }

    access_token = await generate_wallet_token(data)

    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {access_token}",
    }

    yield client
    client.headers.pop("Authorization")
