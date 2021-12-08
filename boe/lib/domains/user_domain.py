from dataclasses import dataclass
from enum import Enum
from boe.lib.common_models import Aggregate
from uuid import UUID, uuid4
from typing import List, Union
from datetime import datetime
from cbaxter1988_utils.pymongo_utils import (
    get_client,
    get_database,
    add_item,
    get_collection
)
from boe.env import MONGO_HOST, MONGO_PORT, APP_DB, USER_ACCOUNT_TABLE
from boe.utils.serialization_utils import serialize_aggregate


class UserAccountTypeEnum(Enum):
    adult = 0
    child = 1


class SubscriptionTypeEnum(Enum):
    basic = 0
    premium = 1


@dataclass
class UserAccountDetail:
    first_name: str
    last_name: str
    email: str


@dataclass
class ChildAccountDetail(UserAccountDetail):
    dob: datetime
    age: int
    grade: int


@dataclass
class AdultAccountDetail(UserAccountDetail):
    pass


@dataclass
class UserAccountAggregate(Aggregate):
    account_type: UserAccountTypeEnum
    account_detail: Union[ChildAccountDetail, AdultAccountDetail]


@dataclass
class FamilyAggregate(Aggregate):
    members: List[UserAccountAggregate]
    name: str
    description: str
    subscription_type: SubscriptionTypeEnum

    def change_subscription_type(self, subscription_type: SubscriptionTypeEnum):
        self.subscription_type = subscription_type

    def add_member(self, member: UserAccountAggregate):
        for _member in self.members:
            if member.id == _member:
                raise ValueError("Member Already Present in Family")

        self.members.append(member)

    def get_member(self, member_id: UUID) -> UserAccountAggregate:
        for _member in self.members:
            if member_id == _member.id:
                return _member

        raise ValueError(f'Member {member_id} Not in Family')


class UserDomainWriteModel:
    def __init__(self):
        self.client = get_client(
            db_host=MONGO_HOST,
            db_port=MONGO_PORT
        )

        self.db = get_database(client=self.client, db_name=APP_DB)

    def save_user_account(self, account: UserAccountAggregate) -> UUID:
        collection = get_collection(database=self.db, collection=USER_ACCOUNT_TABLE)
        add_item(collection=collection, item=serialize_aggregate(account), key_id='id')
        return account.id


class UserDomainQueryModel:
    def get_family_by_id(self, agg_id: UUID) -> dict:
        raise NotImplementedError

    def get_user_account_by_id(self, agg_id: UUID) -> dict:
        raise NotImplementedError

    def scan_user_accounts(self) -> List[dict]:
        raise NotImplementedError

    def scan_child_accounts(self) -> List[dict]:
        raise NotImplementedError

    def scan_families(self) -> List[dict]:
        raise NotImplementedError


class UserDomainFactory:

    @staticmethod
    def build_family(
            name: str,
            description: str,
            subscription_type: SubscriptionTypeEnum,
            members: List[UserAccountAggregate]
    ) -> FamilyAggregate:
        return FamilyAggregate(
            id=uuid4(),
            members=members if members is not None else [],
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
            members: List[UserAccountAggregate]
    ) -> FamilyAggregate:
        return FamilyAggregate(
            id=_id,
            members=members if members is not None else [],
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
    ) -> UserAccountAggregate:
        return UserAccountAggregate(
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
    def build_adult_account(
            email: str,
            first_name: str,
            last_name: str,
    ) -> UserAccountAggregate:
        return UserAccountAggregate(
            account_detail=UserDomainFactory.build_adult_account_detail(

                email=email,
                first_name=first_name,
                last_name=last_name,

            ),
            account_type=UserAccountTypeEnum.adult,
            id=uuid4()
        )

    def rebuild_user_account(self) -> UserAccountAggregate:
        raise NotImplementedError

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


class UserDomainRepository:
    factory: UserDomainFactory
    query_model: UserDomainQueryModel
    write_model: UserDomainWriteModel

    def save(self, model: UserAccountAggregate) -> UUID:
        if isinstance(model, UserAccountAggregate):
            return self.write_model.save_user_account(model)
