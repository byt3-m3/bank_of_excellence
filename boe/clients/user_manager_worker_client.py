import datetime
import uuid
from typing import Union
from uuid import UUID

from boe.applications.user_domain_apps import UserManagerAppEventFactory, SubscriptionTypeEnum, UserAccountTypeEnum
from boe.clients.client import PikaPublisherClient
from boe.env import BOE_APP_EXCHANGE, USER_MANAGER_QUEUE_ROUTING_KEY


class UserManagerWorkerClient(PikaPublisherClient):

    def __init__(self):
        super().__init__(

            BOE_APP_EXCHANGE,
            USER_MANAGER_QUEUE_ROUTING_KEY,

        )
        self.event_factory = UserManagerAppEventFactory()

    def publish_create_family_local_user_event(
            self,
            family_name: str,
            password_hash: bytes,
            first_name: str,
            last_name: str,
            dob: datetime,
            email: str,
            account_type: UserAccountTypeEnum,
            family_id: UUID = None
    ):
        _family_id = uuid.uuid4() if family_id is None else family_id
        event = self.event_factory.build_create_family_local_event(
            family_id=str(_family_id),
            family_name=family_name,
            last_name=last_name,
            first_name=first_name,
            email=email,
            account_type=account_type.value,
            password_hash=password_hash.decode(),
            dob=dob,

        )

        self.publish_event(event)
        return _family_id
