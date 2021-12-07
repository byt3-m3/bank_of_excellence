from dataclasses import dataclass
from enum import Enum
from boe.lib.common_models import Aggregate
from uuid import UUID
from typing import List


class UserAccountTypeEnum(Enum):
    adult = 0
    child = 1


class SubscriptionTypeEnum(Enum):
    basic = 0
    premium = 1


@dataclass(frozen=True)
class UserAccountDetail:
    pass


@dataclass(frozen=True)
class ChildAccountDetail(UserAccountDetail):
    pass


@dataclass(frozen=True)
class AdultAccountDetail(UserAccountDetail):
    pass


@dataclass
class UserAccountAggregate(Aggregate):
    pass


@dataclass
class FamilyAggregate(Aggregate):
    members: List[UserAccountAggregate]
    name: str
    description: str
    subscription_type: SubscriptionTypeEnum


class QueryDomainWriteModel:
    pass


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
    def build_family(self) -> FamilyAggregate:
        raise NotImplementedError

    def rebuild_family(self) -> FamilyAggregate:
        raise NotImplementedError

    def build_user_account(self) -> UserAccountAggregate:
        raise NotImplementedError

    def rebuild_user_account(self) -> UserAccountAggregate:
        raise NotImplementedError

    def build_child_account_detail(self) -> ChildAccountDetail:
        raise NotImplementedError

    def build_adult_account_detail(self) -> AdultAccountDetail:
        raise NotImplementedError


class UserDomainRepository:
    factory: UserDomainFactory
    query_model: UserDomainQueryModel
    write_model: QueryDomainWriteModel

    def save(self) -> UUID:
        raise NotImplementedError
