from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from boe.applications.transcodings import (
    FamilyEntityTranscoding,
    UserAccountEntityTranscoding,
    SubscriptionTypeEnumTranscoding,
    UserAccountTypeEnumTranscoding
)
from boe.lib.common_models import AppEvent
from boe.lib.domains.user_domain import UserDomainFactory, SubscriptionTypeEnum, FamilyUserAggregate
from eventsourcing.application import Application
from eventsourcing.persistence import Transcoder


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


class UserManagerAppEventFactory:

    @staticmethod
    def build_new_family_event(
            description: str,
            name: str,
            subscription_type: SubscriptionTypeEnum = SubscriptionTypeEnum.basic
    ):
        return NewFamilyEvent(
            description=description,
            name=name,
            subscription_type=subscription_type,
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
