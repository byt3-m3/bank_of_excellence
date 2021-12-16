from dataclasses import dataclass
from datetime import datetime
from typing import Union
from uuid import UUID

from boe.applications.transcodings import (
    FamilyEntityTranscoding,
    UserAccountEntityTranscoding,
    SubscriptionTypeEnumTranscoding,
    UserAccountTypeEnumTranscoding
)
from boe.lib.common_models import AppEvent
from boe.lib.domains.user_domain import UserDomainFactory, SubscriptionTypeEnum, FamilyUserAggregate
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
            family_id: UUID,
            age: int,
            dob: datetime,
            last_name: str,
            first_name: str,
            email: str,
            grade: int
    ):
        return NewChildAccountEvent(
            family_id=family_id,
            age=age,
            dob=dob,
            last_name=last_name,
            first_name=first_name,
            email=email,
            grade=grade,
        )

    @staticmethod
    def build_family_subscription_change_event(
            family_id: UUID,
            subscription_type: Union[int, SubscriptionTypeEnum]
    ):
        return FamilySubscriptionChangeEvent(
            family_id=family_id,
            subscription_type=SubscriptionTypeEnum(subscription_type)

        )


class UserManagerApp(Application):

    def __init__(self):
        super().__init__()
        self.factory = UserDomainFactory()

    def register_transcodings(self, transcoder: Transcoder):
        super().register_transcodings(transcoder)
        transcoder.register(FamilyEntityTranscoding())
        transcoder.register(UserAccountEntityTranscoding())
        transcoder.register(SubscriptionTypeEnumTranscoding())
        transcoder.register(UserAccountTypeEnumTranscoding())

    def _get_family_aggregate(self, family_id: UUID) -> FamilyUserAggregate:
        return self.repository.get(aggregate_id=family_id)

    def get_user_account(self, family_id: UUID, account_id: UUID):
        aggregate: FamilyUserAggregate = self.repository.get(aggregate_id=family_id)
        return aggregate.member_map.get(account_id)

    def handle_new_family_event(self, event: NewFamilyEvent) -> UUID:
        family = self.factory.build_user_family_user_aggregate(
            description=event.description,
            name=event.name,
            subscription_type=event.subscription_type
        )

        self.save(family)

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

        self.save(aggregate)
        return aggregate.id

    def handle_family_subscription_type_change_event(self, event: FamilySubscriptionChangeEvent) -> UUID:
        aggregate = self._get_family_aggregate(family_id=event.family_id)
        if event.subscription_type == aggregate.family.subscription_type:
            logger.error(f"Family Subscription Already Set: '{aggregate.family.subscription_type}', Rejecting Event")
            return

        aggregate.change_subscription_type(subscription_type=event.subscription_type)
        self.save(aggregate)

        return aggregate.id
