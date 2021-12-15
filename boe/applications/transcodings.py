from dataclasses import asdict

from boe.lib.domains.bank_domain import (
    BankAccountEntity,
    BankTransactionEntity,
    BankTransactionMethodEnum,
    BankAccountStateEnum
)
from eventsourcing.persistence import Transcoding


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
