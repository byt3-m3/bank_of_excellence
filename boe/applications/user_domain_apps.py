from dataclasses import dataclass
from datetime import datetime
from typing import Union
from uuid import UUID, uuid4

from boe.applications.store_domain_apps import StoreManagerAppEventFactory
from boe.applications.transcodings import (
    FamilyEntityTranscoding,

    SubscriptionTypeEnumTranscoding,
    UserAccountTypeEnumTranscoding,

)
from boe.clients.client import PikaWorkerClient
from boe.clients.notification_worker_client import NotificationWorkerClient
from boe.env import (
    COGNITO_POOL_ID,
    STAGE,
    USER_MANAGER_WORKER_QUEUE,
    STORE_MANAGER_WORKER_QUEUE
)
from boe.lib.common_models import AppEvent, AppNotification
from boe.lib.domains.user_domain import (
    UserDomainFactory,
    SubscriptionTypeEnum,
    FamilyUserAggregate,
    UserDomainWriteModel
)
from cbaxter1988_utils.aws_cognito_utils import add_new_user_basic
from cbaxter1988_utils.log_utils import get_logger
from eventsourcing.application import Application
from eventsourcing.persistence import Transcoder

logger = get_logger("UserManagerApp")


@dataclass(frozen=True)
class NewFamilyEvent(AppEvent):
    description: str
    name: str
    subscription_type: SubscriptionTypeEnum
    first_name: str
    last_name: str
    dob: datetime
    email: str
    id: UUID = None


@dataclass(frozen=True)
class NewChildAccountEvent(AppEvent):
    family_id: UUID
    first_name: str
    last_name: str
    dob: datetime
    grade: int
    email: str


@dataclass(frozen=True)
class NewAdultAccountEvent(AppEvent):
    family_id: UUID
    first_name: str
    last_name: str
    dob: datetime
    email: str


@dataclass(frozen=True)
class FamilySubscriptionChangeEvent(AppEvent):
    family_id: UUID
    subscription_type: SubscriptionTypeEnum


@dataclass(frozen=True)
class CreateCognitoUserEvent(AppEvent):
    username: str
    email: str
    is_real: bool = False


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
            first_name: str,
            last_name: str,
            email: str,
            dob: str,
            subscription_type: Union[SubscriptionTypeEnum, int] = SubscriptionTypeEnum.basic,
            **kwargs

    ):
        return NewFamilyEvent(
            description=description,
            name=name,
            subscription_type=SubscriptionTypeEnum(subscription_type),
            first_name=first_name,
            last_name=last_name,
            email=email,
            dob=datetime.fromisoformat(dob),
            id=UUID(kwargs.get("id", str(uuid4())))
        )

    @staticmethod
    def build_new_child_account_event(
            family_id: str,
            dob: datetime,
            last_name: str,
            first_name: str,
            email: str,
            grade: int
    ):
        return NewChildAccountEvent(
            family_id=UUID(family_id),
            dob=dob,
            last_name=last_name,
            first_name=first_name,
            email=email,
            grade=grade,
        )

    @staticmethod
    def build_new_adult_account_event(
            family_id: str,
            dob: datetime,
            last_name: str,
            first_name: str,
            email: str,
    ):
        return NewAdultAccountEvent(
            family_id=UUID(family_id),
            dob=dob if isinstance(dob, datetime) else datetime.fromisoformat(dob),
            last_name=last_name,
            first_name=first_name,
            email=email,
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

    @staticmethod
    def build_create_cognito_user_event(email: str, username: str, is_real: bool = False) -> CreateCognitoUserEvent:
        return CreateCognitoUserEvent(
            email=email,
            username=username,
            is_real=is_real
        )


class UserManagerApp(Application):

    def __init__(self):
        super().__init__()
        self.factory = UserDomainFactory()

        self.notification_service_client = NotificationWorkerClient()
        self.write_model = UserDomainWriteModel()
        self.user_manager_pika_client = PikaWorkerClient(
            worker_que=USER_MANAGER_WORKER_QUEUE,
            worker_exchange=f'{STAGE}_USER_MANAGER_EXCHANGE',
            worker_routing_key=f'{STAGE}_USER_MANAGER_KEY',

        )

        self.store_manager_pika_client = PikaWorkerClient(
            worker_que=STORE_MANAGER_WORKER_QUEUE,
            worker_exchange=f'{STAGE}_STORE_MANAGER_EXCHANGE',
            worker_routing_key=f'{STAGE}_STORE_MANAGER_KEY',

        )

    def register_transcodings(self, transcoder: Transcoder):
        super().register_transcodings(transcoder)
        transcoder.register(FamilyEntityTranscoding())
        transcoder.register(SubscriptionTypeEnumTranscoding())
        transcoder.register(UserAccountTypeEnumTranscoding())

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
        aggregate = self.factory.build_user_family_user_aggregate(
            description=event.description,
            name=event.name,
            subscription_type=event.subscription_type,
            id=str(event.id)
        )

        self._save_aggregate(aggregate=aggregate)

        self.user_manager_pika_client.publish_event(
            event=UserManagerAppEventFactory.build_new_adult_account_event(
                family_id=str(aggregate.id),
                last_name=event.last_name,
                first_name=event.first_name,
                email=event.email,
                dob=event.dob
            )
        )

        self.store_manager_pika_client.publish_event(
            event=StoreManagerAppEventFactory.build_new_store_event(
                family_id=str(aggregate.id),

            )
        )

        return aggregate.id

    def handle_new_child_account_event(self, event: NewChildAccountEvent) -> UUID:
        aggregate: FamilyUserAggregate = self.repository.get(aggregate_id=event.family_id)

        aggregate.create_new_child_member(
            dob=event.dob,
            email=event.email,
            first_name=event.first_name,
            last_name=event.last_name,
            grade=event.grade,
        )
        child_account = aggregate.members[len(aggregate.members) - 1]

        self._save_aggregate(aggregate=aggregate)

        self.user_manager_pika_client.publish_event(
            event=CreateCognitoUserEvent(
                email=event.email,
                username=f'{event.first_name}_{event.last_name}'.lower(),
                is_real=False if STAGE in ['LOCAL', 'BETA'] else True
            )
        )
        self.notification_service_client.publish_event(
            event=UserManagerAppEventFactory.build_child_created_notification(
                child_id=str(child_account.id),
                family_id=str(aggregate.id),

            )
        )

        return aggregate.id

    def handle_new_adult_account_event(self, event: NewAdultAccountEvent) -> UUID:
        aggregate: FamilyUserAggregate = self.repository.get(aggregate_id=event.family_id)

        aggregate.create_new_adult_member(
            dob=event.dob,
            email=event.email,
            first_name=event.first_name,
            last_name=event.last_name,
        )

        self._save_aggregate(aggregate=aggregate)

        self.user_manager_pika_client.publish_event(
            event=CreateCognitoUserEvent(
                email=event.email,
                username=f'{event.first_name}_{event.last_name}'.lower(),
                is_real=False if STAGE in ['LOCAL', 'BETA'] else True
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

    def handle_create_cognito_user_event(self, event: CreateCognitoUserEvent) -> UUID:
        if event.is_real:
            add_new_user_basic(
                pool_id=COGNITO_POOL_ID,
                username=event.username,
                user_email=event.email
            )
            logger.info(f"Successfully Processed event='{event}'")
        else:
            logger.info(f"Received and Processed Fake Event={event}")
