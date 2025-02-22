from umongo import EmbeddedDocument, fields

from app.helpers.db_utils import instance
from app.models.base import APIDocument
from app.models.channel import Channel
from app.models.server import Server
from app.models.user import User


@instance.register
class MessageReaction(EmbeddedDocument):
    emoji = fields.StrField(required=True)
    count = fields.IntField(default=1)
    users = fields.ListField(fields.ReferenceField(User))


@instance.register
class Message(APIDocument):
    channel = fields.ReferenceField(Channel, required=True)
    server = fields.ReferenceField(Server, required=False, default=None)
    author = fields.ReferenceField(User, required=True)

    content = fields.StrField()  # TODO: prolly not only a string

    reactions = fields.ListField(fields.EmbeddedField(MessageReaction), default=[])

    class Meta:
        collection_name = "messages"
