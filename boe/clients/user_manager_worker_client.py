import datetime
from typing import Union
from uuid import UUID

from boe.applications.user_domain_apps import UserManagerAppEventFactory, SubscriptionTypeEnum
from boe.clients.client import PikaWorkerClient
from boe.env import USER_MANAGER_WORKER_QUEUE, STAGE


class UserManagerWorkerClient(PikaWorkerClient):

    def __init__(self):
        super().__init__(
            USER_MANAGER_WORKER_QUEUE,
            f'{STAGE}_USER_MANAGER_EXCHANGE',
            f'{STAGE}_USER_MANAGER_KEY',

        )
        self.event_factory = UserManagerAppEventFactory()

    def publish_new_family_event(
            self,
            name: str,
            description: str,
            subscription_type: Union[SubscriptionTypeEnum, int]
    ):
        event = self.event_factory.build_new_family_event(
            description=description,
            subscription_type=SubscriptionTypeEnum(subscription_type),
            name=name
        )
        self.publish_event(event=event)

    def publish_new_child_event(
            self,
            first_name: str,
            last_name: str,
            email: str,
            grade: int,
            dob: datetime.datetime,
            family_id: UUID
    ):
        event = self.event_factory.build_new_child_account_event(
            dob=dob,
            email=email,
            family_id=str(family_id),
            first_name=first_name,
            last_name=last_name,
            grade=grade
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
