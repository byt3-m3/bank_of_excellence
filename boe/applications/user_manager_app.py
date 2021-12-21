from dataclasses import dataclass
from datetime import datetime
from typing import Union
from uuid import UUID

from boe.applications.transcodings import (
    FamilyEntityTranscoding,
    UserAccountEntityTranscoding,
    SubscriptionTypeEnumTranscoding,
    UserAccountTypeEnumTranscoding,
    ChildAccountDetailTranscoding,
    AdultAccountDetailTranscoding,
    UserAccountDetailTranscoding
)
from boe.clients.notification_worker_client import NotificationWorkerClient
from boe.lib.common_models import AppEvent, AppNotification
from boe.lib.domains.user_domain import (
    UserDomainFactory,
    SubscriptionTypeEnum,
    FamilyUserAggregate,
    UserDomainWriteModel
)
from cbaxter1988_utils.log_utils import get_logger
from eventsourcing.application import Application
from eventsourcing.persistence import Transcoder

logger = get_logger("UserManagerApp")


@dataclass(frozen=True)
class NewFamilyEvent(AppEvent):
    description: str
    name: str
    subscription_type: SubscriptionTypeEnum


@dataclass(frozen=True)
class NewChildAccountEvent(AppEvent):
    family_id: UUID
    first_name: str
    last_name: str
    age: int
    dob: datetime
    grade: int
    email: str


@dataclass(frozen=True)
class FamilySubscriptionChangeEvent(AppEvent):
    family_id: UUID
    subscription_type: SubscriptionTypeEnum


@dataclass(frozen=True)
class ChildCreatedNotification(AppNotification):
    family_id: str
    child_id: str


@dataclass(frozen=True)
class FamilyCreatedNotification(AppNotification):
    aggregate_id: str


class UserManagerAppEventFactory:

    @staticmethod
    def build_new_family_event(
            description: str,
            name: str,
            subscription_type: Union[SubscriptionTypeEnum, int] = SubscriptionTypeEnum.basic
    ):
        return NewFamilyEvent(
            description=description,
            name=name,
            subscription_type=SubscriptionTypeEnum(subscription_type),
        )

    @staticmethod
    def build_new_child_account_event(
            family_id: str,
            age: int,
            dob: datetime,
            last_name: str,
            first_name: str,
            email: str,
            grade: int
    ):
        return NewChildAccountEvent(
            family_id=UUID(family_id),
            age=age,
            dob=dob,
            last_name=last_name,
            first_name=first_name,
            email=email,
            grade=grade,
        )

    @staticmethod
    def build_family_subscription_change_event(
            family_id: str,
            subscription_type: Union[int, SubscriptionTypeEnum]
    ):
        return FamilySubscriptionChangeEvent(
            family_id=UUID(family_id),
            subscription_type=SubscriptionTypeEnum(subscription_type)

        )

    @staticmethod
    def build_child_created_notification(child_id: str, family_id: str) -> ChildCreatedNotification:
        return ChildCreatedNotification(
            child_id=child_id,
            family_id=family_id
        )

    @staticmethod
    def build_family_created_notification(aggregate_id: str) -> FamilyCreatedNotification:
        return FamilyCreatedNotification(
            aggregate_id=aggregate_id
        )


class UserManagerApp(Application):

    def __init__(self):
        super().__init__()
        self.factory = UserDomainFactory()

        self.notification_service_client = NotificationWorkerClient()
        self.write_model = UserDomainWriteModel()

    def register_transcodings(self, transcoder: Transcoder):
        super().register_transcodings(transcoder)
        transcoder.register(FamilyEntityTranscoding())
        transcoder.register(UserAccountEntityTranscoding())
        transcoder.register(SubscriptionTypeEnumTranscoding())
        transcoder.register(UserAccountTypeEnumTranscoding())
        transcoder.register(ChildAccountDetailTranscoding())
        transcoder.register(AdultAccountDetailTranscoding())
        transcoder.register(UserAccountDetailTranscoding())

    def _get_family_aggregate(self, family_id: UUID) -> FamilyUserAggregate:
        return self.repository.get(aggregate_id=family_id)

    def _save_aggregate(self, aggregate: FamilyUserAggregate):
        self.save(aggregate)

        try:
            self.write_model.save_family_user_aggregate(aggregate=aggregate)
        except Exception:
            logger.error(f"Trouble Saving Aggregate {aggregate}")
            raise

    def get_user_account(self, family_id: UUID, account_id: UUID):
        aggregate: FamilyUserAggregate = self.repository.get(aggregate_id=family_id)
        return aggregate.member_map.get(account_id)

    def handle_new_family_event(self, event: NewFamilyEvent) -> UUID:
        family = self.factory.build_user_family_user_aggregate(
            description=event.description,
            name=event.name,
            subscription_type=event.subscription_type
        )

        self._save_aggregate(aggregate=family)

        self.notification_service_client.publish_event(
            event=UserManagerAppEventFactory.build_family_created_notification(
                aggregate_id=str(family.id)
            )
        )
        return family.id

    def handle_new_child_account_event(self, event: NewChildAccountEvent) -> UUID:
        aggregate: FamilyUserAggregate = self.repository.get(aggregate_id=event.family_id)
        child_account = self.factory.build_child_account(
            age=event.age,
            dob=event.dob,
            email=event.email,
            first_name=event.first_name,
            last_name=event.last_name,
            grade=event.grade
        )

        aggregate.add_family_member(user_account=child_account)

        self._save_aggregate(aggregate=aggregate)
        self.notification_service_client.publish_event(
            event=UserManagerAppEventFactory.build_child_created_notification(
                child_id=str(child_account.id),
                family_id=str(aggregate.id)
            )
        )
        return aggregate.id

    def handle_family_subscription_type_change_event(self, event: FamilySubscriptionChangeEvent) -> UUID:
        aggregate = self._get_family_aggregate(family_id=event.family_id)
        if event.subscription_type == aggregate.family.subscription_type:
            logger.error(f"Family Subscription Already Set: '{aggregate.family.subscription_type}', Rejecting Event")
            return

        aggregate.change_subscription_type(subscription_type=event.subscription_type)

        self._save_aggregate(aggregate=aggregate)
        return aggregate.id
