import uuid
from dataclasses import dataclass
from datetime import datetime
from functools import singledispatchmethod
from typing import Union
from uuid import UUID

from boe.applications.store_domain_apps import StoreManagerAppEventFactory
from boe.applications.transcodings import (
    FamilyEntityTranscoding,
    SubscriptionTypeEnumTranscoding,
    UserAccountTypeEnumTranscoding,

)
from boe.clients.client import PikaPublisherClient
from boe.clients.notification_worker_client import NotificationWorkerClient
from boe.env import (
    COGNITO_POOL_ID,
    STAGE,
    BOE_APP_EXCHANGE,
    USER_MANAGER_QUEUE_ROUTING_KEY,
    STORE_MANAGER_QUEUE_ROUTING_KEY

)
from boe.lib.common_models import AppEvent, AppNotification
from boe.lib.domains.user_domain import (
    UserDomainFactory,
    SubscriptionTypeEnum,
    FamilyUserAggregate,
    UserDomainWriteModel
)
from boe.metrics import ServiceMetricPublisher
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
    family_id: UUID = None


@dataclass(frozen=True)
class NewChildAccountEvent(AppEvent):
    family_id: UUID
    first_name: str
    last_name: str
    dob: datetime
    grade: int
    email: str
    child_id: UUID = None


@dataclass(frozen=True)
class NewAdultAccountEvent(AppEvent):
    family_id: UUID
    adult_id: UUID
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
            family_id: str = None

    ):

        if family_id:
            family_id = UUID(family_id)

        return NewFamilyEvent(
            description=description,
            name=name,
            subscription_type=SubscriptionTypeEnum(subscription_type),
            first_name=first_name,
            last_name=last_name,
            email=email,
            dob=datetime.fromisoformat(dob),
            family_id=family_id
        )

    @staticmethod
    def build_new_child_account_event(
            family_id: str,
            dob: datetime,
            last_name: str,
            first_name: str,
            email: str,
            grade: int,
            child_id: str = None
    ):
        if child_id:
            child_id = UUID(child_id)

        return NewChildAccountEvent(
            family_id=UUID(family_id),
            dob=dob,
            last_name=last_name,
            first_name=first_name,
            email=email,
            grade=grade,
            child_id=child_id
        )

    @staticmethod
    def build_new_adult_account_event(
            family_id: str,
            adult_id: str,
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
            adult_id=UUID(adult_id)
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
        self.user_manager_pika_client = PikaPublisherClient(
            worker_exchange=BOE_APP_EXCHANGE,
            worker_routing_key=USER_MANAGER_QUEUE_ROUTING_KEY,

        )

        self.store_manager_pika_client = PikaPublisherClient(
            worker_exchange=BOE_APP_EXCHANGE,
            worker_routing_key=STORE_MANAGER_QUEUE_ROUTING_KEY,

        )

        self.metric_publisher = ServiceMetricPublisher()

        self._service_name = 'UserManagerApp'

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

    @singledispatchmethod
    def handle_event(self, event):
        raise NotImplementedError("Invalid Event")

    @handle_event.register(NewFamilyEvent)
    def _handle_new_family_event(self, event: NewFamilyEvent):
        aggregate = self.factory.build_user_family_user_aggregate(
            description=event.description,
            name=event.name,
            subscription_type=event.subscription_type,
            family_id=str(event.family_id)
        )

        self._save_aggregate(aggregate=aggregate)

        self.user_manager_pika_client.publish_event(
            event=UserManagerAppEventFactory.build_new_adult_account_event(
                family_id=str(aggregate.id),
                last_name=event.last_name,
                first_name=event.first_name,
                email=event.email,
                dob=event.dob,
                adult_id=str(uuid.uuid4())
            )
        )

        self.store_manager_pika_client.publish_event(
            event=StoreManagerAppEventFactory.build_new_store_event(
                family_id=str(aggregate.id),

            )
        )

        self.metric_publisher.incr_family_created_success_metric(service_name=self._service_name)
        return aggregate.id

    @handle_event.register(NewChildAccountEvent)
    def _handle_new_child_account_event(self, event: NewChildAccountEvent):
        aggregate: FamilyUserAggregate = self.repository.get(aggregate_id=event.family_id)

        aggregate.create_new_child_member(
            dob=event.dob,
            email=event.email,
            first_name=event.first_name,
            last_name=event.last_name,
            grade=event.grade,
            _id=event.child_id
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
        self.metric_publisher.incr_child_user_account_created_success_metric(service_name=self._service_name)
        return aggregate.id

    @handle_event.register(NewAdultAccountEvent)
    def _handle_new_adult_account_event(self, event: NewAdultAccountEvent):
        aggregate: FamilyUserAggregate = self.repository.get(aggregate_id=event.family_id)

        aggregate.create_new_adult_member(
            dob=event.dob,
            email=event.email,
            first_name=event.first_name,
            last_name=event.last_name,
            _id=event.adult_id
        )

        self._save_aggregate(aggregate=aggregate)

        self.user_manager_pika_client.publish_event(
            event=CreateCognitoUserEvent(
                email=event.email,
                username=f'{event.first_name}_{event.last_name}'.lower(),
                is_real=False if STAGE in ['LOCAL', 'BETA'] else True
            )
        )
        self.metric_publisher.incr_adult_user_account_created_success_metric(service_name=self._service_name)
        return aggregate.id

    @handle_event.register(FamilySubscriptionChangeEvent)
    def _handle_family_subscription_change_event(self, event: FamilySubscriptionChangeEvent):
        aggregate = self._get_family_aggregate(family_id=event.family_id)
        if event.subscription_type == aggregate.family.subscription_type:
            logger.error(f"Family Subscription Already Set: '{aggregate.family.subscription_type}', Rejecting Event")
            return

        aggregate.change_subscription_type(subscription_type=event.subscription_type)

        self._save_aggregate(aggregate=aggregate)
        if event.subscription_type == SubscriptionTypeEnum.premium:
            self.metric_publisher.incr_family_subscription_upgrade_success_metric(service_name=self._service_name)

        if event.subscription_type == SubscriptionTypeEnum.basic:
            self.metric_publisher.incr_family_subscription_downgrade_success_metric(service_name=self._service_name)
        return aggregate.id

    @handle_event.register(CreateCognitoUserEvent)
    def _handle_create_cognito_user_event(self, event: CreateCognitoUserEvent):
        if event.is_real:
            add_new_user_basic(
                pool_id=COGNITO_POOL_ID,
                username=event.username,
                user_email=event.email
            )
            self.metric_publisher.incr_cognito_user_created_success_metric(service_name=self._service_name)

            logger.info(f"Successfully Processed event='{event}'")
        else:
            self.metric_publisher.incr_mock_cognito_user_created_success_metric(service_name=self._service_name)
            logger.info(f"Received and Processed Fake Event={event}")
