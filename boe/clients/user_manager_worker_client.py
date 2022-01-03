import datetime
from typing import Union
from uuid import UUID

from boe.applications.user_domain_apps import UserManagerAppEventFactory, SubscriptionTypeEnum
from boe.clients.client import PikaPublisherClient
from boe.env import BOE_APP_EXCHANGE, USER_MANAGER_QUEUE_ROUTING_KEY


class UserManagerWorkerClient(PikaPublisherClient):

    def __init__(self):
        super().__init__(

            BOE_APP_EXCHANGE,
            USER_MANAGER_QUEUE_ROUTING_KEY,

        )
        self.event_factory = UserManagerAppEventFactory()

    def publish_new_family_event(
            self,
            name: str,
            description: str,
            subscription_type: Union[SubscriptionTypeEnum, int],
            first_name: str,
            last_name: str,
            dob: datetime,
            email: str,
            id: str
    ):
        event = self.event_factory.build_new_family_event(
            description=description,
            subscription_type=SubscriptionTypeEnum(subscription_type),
            name=name,
            first_name=first_name,
            last_name=last_name,
            dob=dob.isoformat() if isinstance(dob, datetime.datetime) else dob,
            email=email,
            family_id=id
        )
        return self.publish_event(event=event)

    def publish_new_child_event(
            self,
            first_name: str,
            last_name: str,
            email: str,
            grade: int,
            dob: datetime.datetime,
            family_id: UUID,
            child_id: UUID

    ):
        event = self.event_factory.build_new_child_account_event(
            dob=dob,
            email=email,
            family_id=str(family_id),
            first_name=first_name,
            last_name=last_name,
            grade=grade,
            child_id=str(child_id)

        )

        self.publish_event(event=event)

    def publish_subscription_change_event(
            self,
            subscription_type: SubscriptionTypeEnum,
            family_id: UUID
    ):
        event = self.event_factory.build_family_subscription_change_event(
            family_id=str(family_id),
            subscription_type=SubscriptionTypeEnum(subscription_type)

        )

        self.publish_event(event=event)

    def publish_create_cognito_user_event(self, email: str, username: str, is_real: bool):
        event = self.event_factory.build_create_cognito_user_event(
            email=email,
            username=username,
            is_real=is_real
        )

        self.publish_event(event=event)

    def publish_new_adult_account_event(
            self,
            first_name: str,
            last_name: str,
            email: str,
            dob: datetime.datetime,
            family_id: UUID,
            adult_id: UUID
    ):
        event = self.event_factory.build_new_adult_account_event(
            email=email,
            family_id=str(family_id),
            first_name=first_name,
            last_name=last_name,
            dob=dob,
            adult_id=str(adult_id)
        )

        self.publish_event(event=event)
