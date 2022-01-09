import base64
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Union
from uuid import UUID, uuid4

from boe.env import (
    MONGO_HOST,
    MONGO_PORT,
    APP_DB,
    FAMILY_TABLE,
    USER_ACCOUNT_TABLE,
    CREDENTIAL_STORE_TABLE
)
from boe.lib.common_models import Entity
from boe.secrets import MONGO_DB_PASSWORD, MONGO_DB_USERNAME
from boe.utils.serialization_utils import serialize_object_to_dict
from bson.binary import Binary, UuidRepresentation
from cbaxter1988_utils.pymongo_utils import (
    get_mongo_client_w_auth,
    get_database,
    add_item,
    get_item,
    scan_items,
    update_item,
    get_collection
)
from eventsourcing.domain import Aggregate, event
from pymongo.errors import DuplicateKeyError
from functools import singledispatchmethod


class UserAccountTypeEnum(Enum):
    adult = 0
    child = 1


class SubscriptionTypeEnum(Enum):
    basic = 0
    premium = 1


class UserDomainCredentialError(BaseException):
    pass


@dataclass
class FamilyEntity(Entity):
    name: str
    description: str
    subscription_type: SubscriptionTypeEnum

    def change_subscription_type(self, subscription_type: SubscriptionTypeEnum):
        self.subscription_type = subscription_type


class CredentialTypeEnum(Enum):
    basic = 'basic'
    local = 'local'


@dataclass
class Credential:
    credential_type: CredentialTypeEnum


@dataclass
class LocalCredential(Credential):
    username: str
    password_hash: bytes


@dataclass
class UserAccountEntity(Entity):
    account_type: UserAccountTypeEnum
    family_id: UUID
    first_name: str
    last_name: str
    email: str
    dob: datetime


@dataclass
class UserAccountAggregate(Aggregate):
    user_entity: UserAccountEntity
    credential: Credential

    @classmethod
    def create(
            cls,
            account_type: UserAccountTypeEnum,
            first_name: str,
            last_name: str,
            family_id: UUID,
            email: str,
            dob: datetime,
            credential: Credential
    ):
        user_entity = UserDomainFactory.build_user_account_entity(
            account_type=account_type,
            last_name=last_name,
            first_name=first_name,
            family_id=family_id,
            email=email,
            dob=dob,
            _id=uuid4(),

        )

        return cls._create(
            cls.Created,
            id=user_entity.id,
            user_entity=user_entity,
            credential=credential
        )

    def _check_if_local_creds(self):
        if not isinstance(self.credential, LocalCredential):
            raise UserDomainCredentialError(f"Invalid Credential type, Current Type {type(self.credential)}")

    @event
    def update_local_credential_password(self, password_hash: bytes):
        self._check_if_local_creds()
        self.credential.password_hash = password_hash

    @event
    def update_local_credential_access_token(self, token: bytes):
        self._check_if_local_creds()
        self.credential: LocalCredential
        self.credential.access_token = token


@dataclass
class FamilyAggregate(Aggregate):
    family: FamilyEntity
    members: List[UUID]

    def is_member(self, member_id: UUID):
        for member in self.members:
            if member_id == member:
                return True

        return False

    @classmethod
    def create(
            cls,
            _id: UUID,
            description: str,
            name: str,
            subscription_type: SubscriptionTypeEnum,
            members: List[UserAccountEntity] = None,
            **kwargs
    ):
        family_entity = UserDomainFactory.build_family_entity(
            description=description,
            name=name,
            subscription_type=subscription_type,
            _id=_id

        )

        if members is None:
            members = []

        return cls._create(
            cls.Created,
            id=_id,
            family=family_entity,
            members=members
        )

    @event
    def add_family_member(self, user_aggregate_id: UUID):
        if user_aggregate_id not in self.members:
            self.members.append(user_aggregate_id)
        else:
            raise ValueError(f"{user_aggregate_id} already in Family")

    @event
    def change_family_subscription(self, subscription: SubscriptionTypeEnum):
        self.family.subscription_type = subscription


class UserDomainWriteModel:
    def __init__(self):
        self.client = get_mongo_client_w_auth(
            db_host=MONGO_HOST,
            db_port=MONGO_PORT,
            db_username=MONGO_DB_USERNAME,
            db_password=MONGO_DB_PASSWORD
        )

        self.db = get_database(client=self.client, db_name=APP_DB)

    @singledispatchmethod
    def save_aggregate(self, aggregate):
        raise NotImplementedError

    @save_aggregate.register(FamilyAggregate)
    def _(self, aggregate: FamilyAggregate):
        serialized_aggregate = serialize_object_to_dict(aggregate)

        family_collection = get_collection(database=self.db, collection=FAMILY_TABLE)
        _record_id = Binary.from_uuid(aggregate.id, uuid_representation=UuidRepresentation.STANDARD)
        serialized_aggregate['_id'] = _record_id
        serialized_aggregate['version'] = aggregate.version

        try:
            add_item(item=serialized_aggregate, collection=family_collection, key_id='_id')
        except DuplicateKeyError:
            update_item(new_values=serialized_aggregate, item_id=_record_id, collection=family_collection)

    @save_aggregate.register(UserAccountAggregate)
    def _(self, aggregate: FamilyAggregate):
        serialized_aggregate = serialize_object_to_dict(aggregate)

        collection = get_collection(database=self.db, collection=USER_ACCOUNT_TABLE)
        _record_id = Binary.from_uuid(aggregate.id, uuid_representation=UuidRepresentation.STANDARD)
        serialized_aggregate['_id'] = _record_id
        serialized_aggregate['version'] = aggregate.version

        try:
            add_item(item=serialized_aggregate, collection=collection, key_id='_id')
        except DuplicateKeyError:
            update_item(new_values=serialized_aggregate, item_id=_record_id, collection=collection)

    def save_local_credential(self, username: str, password_hash: bytes, user_id: UUID):
        serialized_cred = serialize_object_to_dict({
            "_id": username,
            "password_hash": password_hash,
            "user_id": user_id
        })

        collection = get_collection(database=self.db, collection=CREDENTIAL_STORE_TABLE)
        try:
            add_item(item=serialized_cred, collection=collection, key_id='_id')
        except DuplicateKeyError:
            update_item(new_values=serialized_cred, item_id=username, collection=collection)


class UserDomainQueryModel:
    @dataclass(frozen=True)
    class LocalCredentialModel:
        username: str
        password_hash: bytes
        user_id: UUID

    @dataclass(frozen=True)
    class AdultUserAccountModel:
        _id: str
        first_name: str
        last_name: str
        email: str
        dob: datetime

    @dataclass(frozen=True)
    class UserAccountModel:
        _id: UUID
        account_type: UserAccountTypeEnum
        first_name: str
        last_name: str
        email: str
        version: int
        family_id: UUID
        username: str

    @dataclass(frozen=True)
    class BasicFamilyModel:
        _id: UUID
        family_name: str
        subscription_type: SubscriptionTypeEnum
        members: List[UUID]
        version: int

    def __init__(self):
        self.client = get_mongo_client_w_auth(
            db_host=MONGO_HOST,
            db_port=MONGO_PORT,
            db_username=MONGO_DB_USERNAME,
            db_password=MONGO_DB_PASSWORD
        )

        self.db = get_database(client=self.client, db_name=APP_DB)

    def get_family_by_id(self, family_aggregate_id: UUID) -> 'UserDomainQueryModel.BasicFamilyModel':
        collection = get_collection(database=self.db, collection=FAMILY_TABLE)

        cursor = list(get_item(collection=collection, item_id=family_aggregate_id, item_key="_id"))

        if len(cursor) > 1:
            # TODO: Add Exception
            raise DuplicateKeyError(f"To Many Results Returned for {family_aggregate_id}")

        if len(cursor) == 1:
            record = cursor[0]

            return self.BasicFamilyModel(
                _id=record['_id'],
                family_name=record['family']['name'],
                subscription_type=SubscriptionTypeEnum(record['family']['subscription_type']),
                members=[UUID(member) for member in record['members']],
                version=record['version']
            )

    def get_user_account_by_id(self, user_aggregate_id: UUID):
        collection = get_collection(database=self.db, collection=USER_ACCOUNT_TABLE)

        cursor = list(get_item(collection=collection, item_id=user_aggregate_id, item_key="_id"))
        if len(cursor) > 1:
            # TODO: Add Exception
            raise DuplicateKeyError(f"To Many Results Returned for {user_aggregate_id}")
        cursor = list(get_item(collection=collection, item_id=user_aggregate_id, item_key="_id"))

        if len(cursor) == 1:
            record = cursor[0]

            return self.UserAccountModel(
                _id=record['_id'],
                account_type=UserAccountTypeEnum(record['user_entity']['account_type']),
                last_name=record['user_entity']['last_name'],
                first_name=record['user_entity']['first_name'],
                email=record['user_entity']['email'],
                family_id=UUID(record['user_entity']['family_id']),
                version=record['version'],
                username=record['credential']['username']
            )

    def get_user_local_credentials_by_id(self, user_aggregate_id: UUID):
        collection = get_collection(database=self.db, collection=USER_ACCOUNT_TABLE)

        cursor = list(get_item(collection=collection, item_id=user_aggregate_id, item_key="_id"))
        if len(cursor) > 1:
            # TODO: Add Exception
            raise DuplicateKeyError(f"To Many Results Returned for {user_aggregate_id}")

        if len(cursor) == 1:
            record = cursor[0]

            if record['credential']['credential_type'] != 'local':
                raise UserDomainCredentialError(
                    f"Invalid Credential Type, Expected 'local' Got '{record['credential']['credential_type']}'"
                )

            return self.LocalCredentialModel(
                username=record['credential']['username'],
                password_hash=record['credential'].get("password_hash", '').encode(),
                user_id=UUID(record['credential'].get("user_id", ''))
            )

    def get_local_credential_by_username(self, username: str):
        collection = get_collection(database=self.db, collection=CREDENTIAL_STORE_TABLE)

        cursor = list(get_item(collection=collection, item_id=username, item_key="_id"))

        if len(cursor) == 1:
            return self.LocalCredentialModel(
                username=cursor[0].get("_id"),
                password_hash=bytes.fromhex(cursor[0].get("password_hash")),
                user_id=UUID(cursor[0].get("user_id")),
            )


class UserDomainFactory:

    @staticmethod
    def build_family_entity(
            name: str,
            description: str,
            subscription_type: SubscriptionTypeEnum,
            _id: UUID,
    ) -> FamilyEntity:
        return FamilyEntity(
            id=_id,
            name=name,
            description=description,
            subscription_type=subscription_type
        )

    @staticmethod
    def rebuild_family(
            id: UUID,
            name: str,
            description: str,
            subscription_type: SubscriptionTypeEnum,
            **kwargs
    ) -> FamilyEntity:
        return FamilyEntity(
            id=id,
            name=name,
            description=description,
            subscription_type=subscription_type
        )

    @staticmethod
    def build_family_aggregate(
            _id: UUID,
            description: str,
            name: str,
            subscription_type: SubscriptionTypeEnum,
            members: List[UUID] = None,

    ) -> FamilyAggregate:
        return FamilyAggregate.create(
            description=description,
            name=name,
            subscription_type=subscription_type,
            members=members,
            _id=_id
        )

    @staticmethod
    def build_user_account_entity(
            account_type: Union[UserAccountTypeEnum, int],
            dob: datetime,
            first_name: str,
            last_name: str,
            email: str,
            family_id: UUID,
            _id: UUID = None
    ) -> UserAccountEntity:
        return UserAccountEntity(
            account_type=UserAccountTypeEnum(account_type),
            dob=dob,
            first_name=first_name,
            last_name=last_name,
            email=email,
            family_id=family_id,
            id=uuid4() if _id is None else _id

        )

    @staticmethod
    def build_local_credentials(password_hash: bytes, username: str) -> Credential:
        return LocalCredential(
            credential_type=CredentialTypeEnum.local,
            username=username,
            password_hash=password_hash
        )

    @staticmethod
    def build_user_account_aggregate_w_local_credential(
            account_type: Union[UserAccountTypeEnum, str],
            dob: datetime,
            first_name: str,
            last_name: str,
            email: str,
            family_id: UUID,
            username: str,
            password_hash: bytes,
            _id: UUID = None
    ) -> UserAccountAggregate:
        return UserAccountAggregate.create(
            account_type=account_type,
            family_id=family_id,
            last_name=last_name,
            first_name=first_name,
            email=email,
            dob=dob,
            credential=UserDomainFactory.build_local_credentials(
                username=username,
                password_hash=password_hash,
            )
        )
