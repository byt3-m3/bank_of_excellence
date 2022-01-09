from dataclasses import asdict

from boe.lib.domains.bank_domain import (
    BankAccountEntity,
    BankTransactionEntity,
    BankTransactionMethodEnum,
    BankAccountStateEnum
)
from boe.lib.domains.persistence_domain import PersistenceRequest, PersistenceRecord
from boe.lib.domains.store_domain import (
    StoreEntity,
    StoreItemEntity
)
from boe.lib.domains.task_domain import (
    TaskEntity,
    TaskStatusEnum
)
from boe.lib.domains.user_domain import (
    FamilyEntity,
    UserAccountEntity,
    LocalCredential,
    CredentialTypeEnum,
    SubscriptionTypeEnum,
    UserAccountTypeEnum
)
from eventsourcing.persistence import Transcoding


class BytesTranscoding(Transcoding):
    type = bytes
    name = "bytes"

    def encode(self, o: bytes) -> str:
        return o.decode()

    def decode(self, d: str):
        return d.encode()


class TaskStatusEnumTranscoding(Transcoding):
    type = TaskStatusEnum
    name = "TaskStatusEnum"

    def encode(self, o: TaskStatusEnum) -> int:
        return o.value

    def decode(self, d: int):
        return TaskStatusEnum(d)


class TaskEntityTranscoding(Transcoding):
    type = TaskEntity
    name = "TaskEntity"

    def encode(self, o: TaskEntity) -> str:
        return asdict(o)

    def decode(self, d: dict):
        return TaskEntity(**d)


class UserAccountEntityTranscoding(Transcoding):
    type = UserAccountEntity
    name = "UserAccountEntity"

    def encode(self, o: UserAccountEntity) -> str:
        return asdict(o)

    def decode(self, d: dict):
        return UserAccountEntity(**d)


class LocalCredentialTranscoding(Transcoding):
    type = LocalCredential
    name = "UserAccountEntity"

    def encode(self, o: LocalCredential) -> str:
        return asdict(o)

    def decode(self, d: dict):
        return LocalCredential(**d)


class PersistenceRecordTranscoding(Transcoding):
    type = PersistenceRecord
    name = "PersistenceRecord"

    def encode(self, o: PersistenceRecord) -> str:
        return asdict(o)

    def decode(self, d: dict):
        return PersistenceRecord(**d)


class PersistenceRequestTranscoding(Transcoding):
    type = PersistenceRequest
    name = "PersistenceRequest"

    def encode(self, o: PersistenceRequest) -> str:
        return asdict(o)

    def decode(self, d: dict):
        return PersistenceRequest(**d)


class StoreItemEntityTranscoding(Transcoding):
    type = StoreItemEntity
    name = "StoreItemEntity"

    def encode(self, o: StoreItemEntity) -> str:
        return asdict(o)

    def decode(self, d: dict):
        return StoreItemEntity(**d)


class StoreEntityTranscoding(Transcoding):
    type = StoreEntity
    name = "StoreEntity"

    def encode(self, o: StoreEntity) -> str:
        return asdict(o)

    def decode(self, d: dict):
        return StoreEntity(**d)


class UserAccountTypeEnumTranscoding(Transcoding):
    type = UserAccountTypeEnum
    name = "UserAccountTypeEnum"

    def encode(self, o: UserAccountTypeEnum) -> int:
        return o.value

    def decode(self, d: int):
        return UserAccountTypeEnum(d)


class CredentialTypeEnumTranscoding(Transcoding):
    type = CredentialTypeEnum
    name = "CredentialTypeEnum"

    def encode(self, o: CredentialTypeEnum) -> str:
        return o.value

    def decode(self, d: str):
        return CredentialTypeEnum(d)


class SubscriptionTypeEnumTranscoding(Transcoding):
    type = SubscriptionTypeEnum
    name = "SubscriptionTypeEnum"

    def encode(self, o: SubscriptionTypeEnum) -> int:
        return o.value

    def decode(self, d: int):
        return SubscriptionTypeEnum(d)


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
