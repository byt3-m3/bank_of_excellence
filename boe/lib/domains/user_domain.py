from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Union, Dict, Any
from uuid import UUID, uuid4

from boe.env import (
    MONGO_HOST,
    MONGO_PORT,
    APP_DB,
    FAMILY_TABLE
)
from boe.lib.common_models import Entity
from boe.utils.serialization_utils import serialize_dataclass_to_dict
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
from serde import deserialize, serialize


@serialize
@deserialize
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


@serialize
@deserialize
@dataclass
class UserAccountDetail:
    first_name: str
    last_name: str
    email: str


@serialize
@deserialize
@dataclass
class ChildAccountDetail(UserAccountDetail):
    dob: datetime
    age: int
    grade: int


@serialize
@deserialize
@dataclass
class AdultAccountDetail(UserAccountDetail):
    pass


@serialize
@deserialize
@dataclass
class UserAccountEntity(Entity):
    account_type: UserAccountTypeEnum
    account_detail: Union[ChildAccountDetail, AdultAccountDetail]


@serialize
@deserialize
@dataclass
class FamilyEntity(Entity):
    name: str
    description: str
    subscription_type: SubscriptionTypeEnum

    def change_subscription_type(self, subscription_type: SubscriptionTypeEnum):
        self.subscription_type = subscription_type


@serialize
@deserialize
@dataclass
class MemberMapping:
    data: Any


@serialize
@deserialize
@dataclass
class FamilyUserAggregate(Aggregate):
    family: FamilyEntity
    member_map: Dict[str, UserAccountEntity]

    def _add_family_member(self, user_account: UserAccountEntity):
        if str(user_account.id) not in self.member_map:
            if isinstance(user_account, UserAccountEntity):
                self.member_map[str(user_account.id)] = user_account
            else:
                raise TypeError(f"Invalid type for user_account, Expected: {UserAccountEntity}")
        else:
            raise ValueError(f"AccountID={user_account.id} already member")

    @classmethod
    def create(
            cls,
            description: str,
            name: str,
            subscription_type: SubscriptionTypeEnum,
            members: List[UserAccountEntity] = None
    ):
        family_entity = UserDomainFactory.build_family(
            description=description,
            name=name,
            subscription_type=subscription_type

        )
        member_map = {}
        if members is not None:
            for member in members:
                member_map[member.id] = member

        return cls._create(
            cls.Created,
            id=family_entity.id,
            family=family_entity,
            member_map=member_map
        )

    @event
    def create_new_adult_member(self, email: str, first_name: str, last_name: str):
        account = UserDomainFactory.build_adult_account(
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        self._add_family_member(user_account=account)

    @event
    def create_new_child_member(
            self,
            email: str,
            first_name: str,
            last_name: str,
            age: int,
            dob: datetime,
            grade: int
    ):
        account = UserDomainFactory.build_child_account(
            email=email,
            first_name=first_name,
            last_name=last_name,
            age=age,
            dob=dob,
            grade=grade
        )
        self._add_family_member(user_account=account)

    @event
    def add_family_member(self, user_account: UserAccountEntity):
        self._add_family_member(user_account=user_account)

    @event
    def remove_family_member(self, user_id: UUID):
        self.member_map.pop(str(user_id))

    @event
    def change_subscription_type(self, subscription_type: SubscriptionTypeEnum):
        self.family.subscription_type = subscription_type


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
            _id: UUID,
            name: str,
            description: str,
            subscription_type: SubscriptionTypeEnum,
            **kwargs
    ) -> FamilyEntity:
        return FamilyEntity(
            id=_id,
            name=name,
            description=description,
            subscription_type=subscription_type
        )

    @staticmethod
    def build_child_account(
            age: int,
            dob: datetime,
            email: str,
            first_name: str,
            last_name: str,
            grade: int,
    ) -> UserAccountEntity:
        return UserAccountEntity(
            account_detail=UserDomainFactory.build_child_account_detail(
                age=age,
                dob=dob,
                email=email,
                first_name=first_name,
                last_name=last_name,
                grade=grade
            ),
            account_type=UserAccountTypeEnum.child,
            id=uuid4()
        )

    @staticmethod
    def rebuild_child_account(
            _id: UUID,
            age: int,
            dob: datetime,
            email: str,
            first_name: str,
            last_name: str,
            grade: int,
            **kwargs
    ) -> UserAccountEntity:
        return UserAccountEntity(
            id=_id,
            account_detail=ChildAccountDetail(
                email=email,
                first_name=first_name,
                last_name=last_name,
                age=age,
                dob=dob,
                grade=grade
            ),
            account_type=UserAccountTypeEnum.child
        )

    @staticmethod
    def build_adult_account(
            email: str,
            first_name: str,
            last_name: str,
    ) -> UserAccountEntity:
        return UserAccountEntity(
            account_detail=UserDomainFactory.build_adult_account_detail(

                email=email,
                first_name=first_name,
                last_name=last_name,

            ),
            account_type=UserAccountTypeEnum.adult,
            id=uuid4()
        )

    @staticmethod
    def rebuild_adult_account(
            _id: UUID,
            email: str,
            first_name: str,
            last_name: str,
            **kwargs
    ) -> UserAccountEntity:
        return UserAccountEntity(
            id=_id,
            account_detail=AdultAccountDetail(
                email=email,
                first_name=first_name,
                last_name=last_name
            ),
            account_type=UserAccountTypeEnum.adult
        )

    @staticmethod
    def rebuild_user_account(
            _id,
            account_type,
            account_detail,
            **kwargs
    ) -> UserAccountEntity:
        return UserAccountEntity(
            id=_id,
            account_detail=account_detail,
            account_type=account_type
        )

    @staticmethod
    def build_child_account_detail(
            age: int,
            dob: datetime,
            email: str,
            first_name: str,
            last_name: str,
            grade: int,
    ) -> ChildAccountDetail:
        return ChildAccountDetail(
            age=age,
            dob=dob,
            email=email,
            first_name=first_name,
            last_name=last_name,
            grade=grade
        )

    @staticmethod
    def build_adult_account_detail(
            first_name: str,
            last_name: str,
            email: str,
    ) -> AdultAccountDetail:
        return AdultAccountDetail(
            first_name=first_name,
            last_name=last_name,
            email=email,
        )

    @staticmethod
    def build_user_family_user_aggregate(
            description: str,
            name: str,
            subscription_type: SubscriptionTypeEnum,
            members: List[UserAccountEntity] = None
    ):
        return FamilyUserAggregate.create(
            description=description,
            name=name,
            subscription_type=subscription_type,
            members=members
        )

    @staticmethod
    def rebuild_family_user_aggregate():
        return FamilyUserAggregate.create(

        )


class UserDomainRepository:

    def __init__(self):
        self.factory: UserDomainFactory = UserDomainFactory()
        self.query_model: UserDomainQueryModel = UserDomainQueryModel()
        self.write_model: UserDomainWriteModel = UserDomainWriteModel()

    def save(self, model: Union[UserAccountEntity, FamilyEntity]) -> UUID:

        if isinstance(model, UserAccountEntity):
            return self.write_model.save_user_account(model)

        if isinstance(model, FamilyEntity):
            return self.write_model.save_family(family=model)

    def get_user_account(self, account_id: UUID) -> UserAccountEntity:
        model_dict = self.query_model.get_user_account_by_id(agg_id=account_id)

        return self.factory.rebuild_user_account(
            **model_dict
        )

    def get_user_accounts(self) -> List[UserAccountEntity]:
        items = self.query_model.scan_user_accounts()
        return [
            self.factory.rebuild_user_account(**item) for item in items
        ]

    def get_family(self, family_id) -> FamilyEntity:
        model_dict = self.query_model.get_family_by_id(family_id=family_id)

        return self.factory.rebuild_family(
            **model_dict
        )

    def get_families(self):
        items = self.query_model.scan_families()
        return [
            self.factory.rebuild_family(**item) for item in items
        ]
