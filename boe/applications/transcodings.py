from dataclasses import asdict

from boe.lib.domains.bank_domain import (
    BankAccountEntity,
    BankTransactionEntity,
    BankTransactionMethodEnum,
    BankAccountStateEnum
)
from boe.lib.domains.user_domain import (
    FamilyEntity,
    UserAccountEntity,
    SubscriptionTypeEnum,
    UserAccountTypeEnum
)
from eventsourcing.persistence import Transcoding


class UserAccountTypeEnumTranscoding(Transcoding):
    type = UserAccountTypeEnum
    name = "UserAccountTypeEnum"

    def encode(self, o: UserAccountTypeEnum) -> int:
        return o.value

    def decode(self, d: int):
        return UserAccountTypeEnum(d)


class SubscriptionTypeEnumTranscoding(Transcoding):
    type = SubscriptionTypeEnum
    name = "SubscriptionTypeEnum"

    def encode(self, o: SubscriptionTypeEnum) -> int:
        return o.value

    def decode(self, d: int):
        return SubscriptionTypeEnum(d)


class UserAccountEntityTranscoding(Transcoding):
    type = UserAccountEntity
    name = "UserAccountEntity"

    def encode(self, o: UserAccountEntity) -> str:
        return asdict(o)

    def decode(self, d: dict):
        return UserAccountEntity(**d)


class FamilyEntityTranscoding(Transcoding):
    type = FamilyEntity
    name = "FamilyEntity"

    def encode(self, o: FamilyEntity) -> str:
        return asdict(o)

    def decode(self, d: dict):
        return FamilyEntity(**d)


class BankAccountEntityTranscoding(Transcoding):
    type = BankAccountEntity
    name = "BankAccountEntity"

    def encode(self, o: BankAccountEntity) -> str:
        return asdict(o)

    def decode(self, d: dict):
        return BankAccountEntity(**d)


class BankTransactionEntityTranscoding(Transcoding):
    type = BankTransactionEntity
    name = "BankTransactionEntity"

    def encode(self, o: BankTransactionEntity) -> str:
        return asdict(o)

    def decode(self, d: dict):
        return BankTransactionEntity(**d)


class BankAccountStateEnumTranscoding(Transcoding):
    type = BankAccountStateEnum
    name = "BankAccountStateEnum"

    def encode(self, o: BankAccountStateEnum) -> int:
        return o.value

    def decode(self, d: int):
        return BankAccountStateEnum(d)


class BankTransactionMethodEnumTranscoding(Transcoding):
    type = BankTransactionMethodEnum
    name = "BankTransactionMethodEnum"

    def encode(self, o: BankTransactionMethodEnum) -> int:
        return o.value

    def decode(self, d: int):
        return BankTransactionMethodEnum(d)
