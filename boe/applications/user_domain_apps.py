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
    UserAccountEntityTranscoding,
    LocalCredentialTranscoding,
    CredentialTypeEnumTranscoding,
    BytesTranscoding

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
    UserAccountTypeEnum,
    SubscriptionTypeEnum,
    FamilyAggregate,
    UserAccountAggregate,
    UserDomainWriteModel
)
from boe.metrics import ServiceMetricPublisher
from cbaxter1988_utils.aws_cognito_utils import add_new_user_basic, get_cognito_idp_client
from cbaxter1988_utils.log_utils import get_logger
from eventsourcing.application import Application
from eventsourcing.persistence import Transcoder

logger = get_logger("UserManagerApp")


class NewPasswordRequiredError(BaseException):
    pass


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
    @dataclass(frozen=True)
    class CreateFamilyLocalUserEvent(AppEvent):
        family_id: UUID
        account_type: UserAccountTypeEnum
        family_name: str
        first_name: str
        last_name: str
        email: str
        password_hash: bytes
        dob: datetime

    @dataclass(frozen=True)
    class CreateCognitoUserEvent(AppEvent):
        username: str
        email: str
        is_real: bool = False

    @classmethod
    def build_create_family_local_event(
            cls,
            family_id: str,
            first_name: str,
            last_name: str,
            email: str,
            family_name: str,
            password_hash: bytes,
            account_type: int,
            dob: str,
    ) -> 'UserManagerAppEventFactory.CreateFamilyLocalUserEvent':
        return cls.CreateFamilyLocalUserEvent(
            family_id=UUID(family_id),
            first_name=first_name,
            last_name=last_name,
            password_hash=password_hash,
            email=email,
            family_name=family_name,
            account_type=UserAccountTypeEnum(account_type),
            dob=datetime.fromisoformat(dob)
        )


class UserAuthManagerEventFactory:
    @dataclass(frozen=True)
    class CognitoAuthRequestEvent(AppEvent):
        username: str
        password: str
        client_id: str

    @dataclass(frozen=True)
    class LocalAuthRequestEvent(AppEvent):
        username: str
        password_hash: str

    @classmethod
    def build_cognito_auth_request_event(
            cls,
            username: str,
            client_id: str,
            password: str
    ):
        return cls.CognitoAuthRequestEvent(
            username=username,
            password=password,
            client_id=client_id
        )

    @classmethod
    def build_local_auth_request_event(
            cls,
            username: str,
            password_hash: bytes
    ):
        return cls.LocalAuthRequestEvent(
            username=username,
            password_hash=password_hash.decode(),

        )


f = UserManagerAppEventFactory


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
        transcoder.register(UserAccountEntityTranscoding())
        transcoder.register(LocalCredentialTranscoding())
        transcoder.register(CredentialTypeEnumTranscoding())
        transcoder.register(BytesTranscoding())

    def _get_family_aggregate(self, family_id: UUID) -> FamilyAggregate:
        return self.repository.get(aggregate_id=family_id)

    def _save_aggregate(self, aggregate: Union[FamilyAggregate, UserAccountAggregate]):

        try:
            self.write_model.save_aggregate(aggregate)
            self.save(aggregate)
        except Exception:
            logger.error(f"Trouble Saving Aggregate {aggregate}")
            raise

    @singledispatchmethod
    def handle_event(self, event):
        raise NotImplementedError("Invalid Event")

    @handle_event.register(f.CreateFamilyLocalUserEvent)
    def _(self, event: f.CreateFamilyLocalUserEvent):
        family_aggregate = self.factory.build_family_aggregate(
            _id=event.family_id,
            description=event.family_name,
            name=event.family_name,
            subscription_type=SubscriptionTypeEnum.basic,
            members=[]
        )

        user_aggregate = self.factory.build_user_account_aggregate_w_local_credential(
            last_name=event.last_name,
            first_name=event.first_name,
            family_id=event.family_id,
            password_hash=event.password_hash,
            email=event.email,
            username=f'{event.first_name}_{event.last_name}',
            account_type=event.account_type,
            dob=event.dob,
            _id=event.family_id

        )

        self._save_aggregate(aggregate=family_aggregate)
        self.store_manager_pika_client.publish_event(
            event=StoreManagerAppEventFactory.build_new_store_event(
                family_id=str(family_aggregate.id),

            )
        )
        self._save_aggregate(aggregate=user_aggregate)

        family_aggregate.add_family_member(user_aggregate_id=user_aggregate.id),
        self._save_aggregate(family_aggregate)

    @handle_event.register(f.CreateCognitoUserEvent)
    def _(self, event: f.CreateCognitoUserEvent):
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


f = UserAuthManagerEventFactory


class UserAuthenticationApp(Application):
    def __init__(self):
        super().__init__()

    @singledispatchmethod
    def handle_event(self, event: AppEvent):
        raise NotImplementedError()

    @handle_event.register(f.CognitoAuthRequestEvent)
    def _(self, event: f.CognitoAuthRequestEvent):
        logger.info(f'Processing Event {event}')
        cognito_client = get_cognito_idp_client()

        initiate_auth_results = cognito_client.initiate_auth(
            ClientId=event.client_id,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": event.username,
                "PASSWORD": event.password
            },

        )
        logger.debug(initiate_auth_results)

        if initiate_auth_results.get("ChallengeName") == 'NEW_PASSWORD_REQUIRED':
            raise NewPasswordRequiredError("")

        logger.info(f"Authenticated: {event.username}")
        return initiate_auth_results.get("AuthenticationResult")

    @handle_event.register(f.LocalAuthRequestEvent)
    def _(self, event: f.LocalAuthRequestEvent):
        pass
