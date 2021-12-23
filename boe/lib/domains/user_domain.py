from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Union
from uuid import UUID, uuid4

from boe.env import (
    MONGO_HOST,
    MONGO_PORT,
    APP_DB,
    FAMILY_TABLE
)
from boe.lib.common_models import Entity
from cbaxter1988_utils.pymongo_utils import (
    get_client,
    get_database,
    add_item,
    get_item,
    scan_items,
    update_item,
    get_collection
)
from eventsourcing.domain import Aggregate, event
from pymongo.errors import DuplicateKeyError


class UserAccountTypeEnum(Enum):
    adult = 0
    child = 1


class SubscriptionTypeEnum(Enum):
    basic = 0
    premium = 1


@dataclass(frozen=True)
class FamilyTableModel:
    _id: UUID
    family_id: UUID
    members: List[UUID]
    subscription_type: int


@dataclass(frozen=True)
class AdultAccountTableModel:
    _id: UUID
    user_id: UUID
    first_name: str
    last_name: str
    email: str
    family_id: UUID


@dataclass(frozen=True)
class ChildAccountTableModel:
    _id: UUID
    user_id: UUID
    first_name: str
    last_name: str
    dob: datetime
    age: int
    grade: int
    family_id: UUID


@dataclass
class FamilyEntity(Entity):
    name: str
    description: str
    subscription_type: SubscriptionTypeEnum

    def change_subscription_type(self, subscription_type: SubscriptionTypeEnum):
        self.subscription_type = subscription_type


class CredentialTypeEnum(Enum):
    basic = 0


@dataclass
class Creds:

    def update_creds(self, **kwargs):
        pass


@dataclass
class BasicCreds(Creds):
    username: str
    password_hash: str

    def update_creds(self, username: str, password: str):
        self.username = username
        self.password_hash = password

    def update_password_hash(self, password_hash: str):
        self.password_hash = password_hash


@dataclass
class Credential:
    credential_type: CredentialTypeEnum
    creds: Union[Creds, BasicCreds]


@dataclass
class UserAccount(Entity):
    account_type: UserAccountTypeEnum
    family_id: UUID
    first_name: str
    last_name: str
    email: str
    dob: datetime
    grade: int = field(default=0)
    credential: Credential = field(default=Credential(credential_type=CredentialTypeEnum.basic, creds=BasicCreds(
        password_hash='',
        username=""
    )))


@dataclass
class FamilyUserAggregate(Aggregate):
    family: FamilyEntity
    members: List[UserAccount]

    def is_member(self, member_id: UUID):
        for member in self.members:
            if member_id == member.id:
                return True

        return False

    def _add_family_member(self, user_account: UserAccount):

        if not self.is_member(member_id=user_account.id):
            if isinstance(user_account, UserAccount):
                self.members.append(user_account)
            else:
                raise TypeError(f"Invalid type for user_account, Expected: {UserAccount}")
        else:
            raise ValueError(f"AccountID={user_account.id} already member")

    def get_member_by_id(self, member_id: UUID) -> UserAccount:
        for member in self.members:
            if member.id == member_id:
                return member

        raise ValueError(f"{member_id} not in family members")

    @classmethod
    def create(
            cls,
            description: str,
            name: str,
            subscription_type: SubscriptionTypeEnum,
            members: List[UserAccount] = None
    ):
        family_entity = UserDomainFactory.build_family(
            description=description,
            name=name,
            subscription_type=subscription_type

        )
        if members is None:
            members = []

        return cls._create(
            cls.Created,
            id=family_entity.id,
            family=family_entity,
            members=members
        )

    @event
    def create_new_adult_member(self, email: str, first_name: str, last_name: str, dob: datetime):
        account = UserDomainFactory.build_user_account(
            email=email,
            first_name=first_name,
            last_name=last_name,
            account_type=UserAccountTypeEnum.adult,
            family_id=self.id,
            dob=dob
        )
        self._add_family_member(user_account=account)

    @event
    def create_new_child_member(
            self,
            email: str,
            first_name: str,
            last_name: str,
            dob: datetime,
            grade: int
    ):
        account = UserDomainFactory.build_user_account(
            email=email,
            first_name=first_name,
            last_name=last_name,
            dob=dob,
            grade=grade,
            account_type=UserAccountTypeEnum.child,
            family_id=self.family.id
        )
        self._add_family_member(user_account=account)

    @event
    def add_family_member(self, user_account: UserAccount):
        if user_account.family_id != self.id:
            raise ValueError(
                f"User Account(id={user_account.id} family_id={user_account.family_id}) is not related   Family={self.id}")
        self._add_family_member(user_account=user_account)

    @event
    def remove_family_member(self, user_id: UUID):
        self.members.remove(self.get_member_by_id(member_id=user_id))

    @event
    def change_subscription_type(self, subscription_type: SubscriptionTypeEnum):
        self.family.subscription_type = subscription_type

    @event
    def set_basic_credential(self, member_id: UUID, password_hash: bytes):

        user = self.get_member_by_id(member_id=member_id)
        credential = None
        if user.account_type.adult:
            credential = UserDomainFactory.build_basic_credentials(password_hash=password_hash, username=user.email)

        if user.account_type.child:
            credential = UserDomainFactory.build_basic_credentials(
                password_hash=password_hash,
                username=f'{user.first_name}_{user.last_name}'.lower()
            )

        user.credential = credential

    @event
    def update_user_basic_password_credentials(self, member_id: UUID, password_hash: str):
        member = self.get_member_by_id(member_id=member_id)

        member.credential.creds.update_password_hash(password_hash=password_hash)


class UserDomainWriteModel:
    def __init__(self):
        self.client = get_client(
            db_host=MONGO_HOST,
            db_port=MONGO_PORT
        )

        self.db = get_database(client=self.client, db_name=APP_DB)

    def save_family_user_aggregate(self, aggregate: FamilyUserAggregate):
        serialized_aggregate = serialize_dataclass_to_dict(aggregate)

        family_collection = get_collection(database=self.db, collection=FAMILY_TABLE)

        serialized_aggregate['_id'] = aggregate.id
        serialized_aggregate['version'] = aggregate.version

        try:
            add_item(item=serialized_aggregate, collection=family_collection, key_id='_id')
        except DuplicateKeyError:
            update_item(new_values=serialized_aggregate, item_id=aggregate.id, collection=family_collection)


class UserDomainQueryModel:
    def __init__(self):
        self.client = get_client(
            db_host=MONGO_HOST,
            db_port=MONGO_PORT
        )

        self.db = get_database(client=self.client, db_name=APP_DB)

    def get_family_by_id(self, family_id: UUID) -> dict:
        collection = get_collection(database=self.db, collection=FAMILY_TABLE)

        cursor = list(get_item(collection=collection, item_id=family_id, item_key="id"))

        if len(cursor) != 1:
            # TODO: Add Exception
            print("Query Error")

        return cursor[0]

    def get_user_account_by_id(self, agg_id: UUID) -> dict:
        collection = get_collection(database=self.db, collection=USER_ACCOUNT_TABLE)

        cursor = list(get_item(collection=collection, item_id=agg_id, item_key="id"))

        if len(cursor) != 1:
            # TODO: Add Exception
            print("Query Error")

        return cursor[0]

    def scan_user_accounts(self) -> List[dict]:
        collection = get_collection(database=self.db, collection=USER_ACCOUNT_TABLE)
        return list(scan_items(collection=collection))

    def scan_child_accounts(self) -> List[dict]:
        raise NotImplementedError

    def scan_families(self) -> List[dict]:
        collection = get_collection(database=self.db, collection=FAMILY_TABLE)
        return list(scan_items(collection=collection))


class UserDomainFactory:

    @staticmethod
    def build_family(
            name: str,
            description: str,
            subscription_type: SubscriptionTypeEnum,
    ) -> FamilyEntity:
        return FamilyEntity(
            id=uuid4(),
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
    def build_user_family_user_aggregate(
            description: str,
            name: str,
            subscription_type: SubscriptionTypeEnum,
            members: List[UserAccount] = None
    ):
        return FamilyUserAggregate.create(
            description=description,
            name=name,
            subscription_type=subscription_type,
            members=members
        )

    @staticmethod
    def build_user_account(
            account_type: Union[UserAccountTypeEnum, int],
            dob: datetime,
            first_name: str,
            last_name: str,
            email: str,
            family_id: UUID,
            grade: int = 0
    ) -> UserAccount:
        return UserAccount(
            account_type=UserAccountTypeEnum(account_type),
            dob=dob,
            first_name=first_name,
            last_name=last_name,
            email=email,
            family_id=family_id,
            grade=grade,
            id=uuid4()

        )

    @staticmethod
    def build_basic_credentials(password_hash: bytes, username: str) -> Credential:
        return Credential(
            credential_type=CredentialTypeEnum.basic,
            creds={
                "password_hash": password_hash,
                "username": username
            }
        )
