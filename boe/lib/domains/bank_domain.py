from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List
from uuid import UUID, uuid4

from boe.env import MONGO_HOST, MONGO_PORT, APP_DB, BANK_ACCOUNT_TABLE
from boe.lib.common_models import Entity
from boe.utils.serialization_utils import serialize_aggregate
from cbaxter1988_utils.pymongo_utils import (
    get_client,
    get_collection,
    get_database,
    add_item,
    get_item,
    update_item
)
from eventsourcing.domain import Aggregate, event
from pymongo.errors import DuplicateKeyError


class BankAccountStateEnum(Enum):
    enabled = 0
    disabled = 1


class BankTransactionMethodEnum(Enum):
    add = 0
    subtract = 1


@dataclass
class BankTransactionEntity(Entity):
    account_id: UUID
    created: datetime
    item_id: UUID
    value: float
    method: BankTransactionMethodEnum = field(default_factory=BankTransactionMethodEnum)


@dataclass(frozen=True)
class BankTransactionValueObject:
    account_id: UUID
    created: datetime
    item_id: UUID
    value: float
    method: BankTransactionMethodEnum = field(default_factory=BankTransactionMethodEnum)


@dataclass
class BankAccountEntity(Entity):
    owner_id: UUID
    is_overdraft_protected: bool
    state: BankAccountStateEnum = field(default=BankAccountStateEnum.enabled)
    balance: float = field(default=0)


@dataclass
class BankDomainAggregate(Aggregate):
    bank_account: BankAccountEntity
    bank_transactions: List[BankTransactionEntity]

    @classmethod
    def create(cls, owner_id: UUID, is_overdraft_protected: bool):
        account_entity = BankDomainFactory.build_bank_account_entity(
            is_overdraft_protected=is_overdraft_protected,
            owner_id=owner_id
        )
        return cls._create(
            cls.Created,
            id=account_entity.id,
            bank_account=account_entity,
            bank_transactions=[]
        )

    def calculate_account_balance(self):
        _balance = 0
        for transaction in self.bank_transactions:
            if transaction.method == BankTransactionMethodEnum.add:
                _balance += transaction.value

            if transaction.method == BankTransactionMethodEnum.subtract:
                _balance -= transaction.value

        return _balance

    def _apply_transaction_to_account(self, transaction: BankTransactionEntity):

        if transaction.account_id != self.bank_account.id:
            raise ValueError(f"Invalid AccountID='{transaction.account_id}' for Transaction='{transaction.id}'")

        self.bank_transactions.append(transaction)

        self.bank_account.balance = self.calculate_account_balance()

    def get_transaction_by_id(self, transaction_id: UUID) -> BankTransactionValueObject:
        for transaction in self.bank_transactions:
            if transaction_id == transaction.id:
                return BankTransactionValueObject(
                    method=transaction.method,
                    account_id=transaction.account_id,
                    created=transaction.created,
                    item_id=transaction.item_id,
                    value=transaction.value
                )

        raise ValueError(f'Invalid TransactionID="{transaction_id}"')

    @event
    def apply_transaction_to_account(self, transaction: BankTransactionEntity):
        self._apply_transaction_to_account(transaction=transaction)

    @event
    def new_transaction(
            self,
            item_id: UUID,
            method: BankTransactionMethodEnum,
            value: float,
            account_id: UUID
    ):
        transaction = BankDomainFactory.build_bank_transaction_entity(
            item_id=item_id,
            method=method,
            value=value,
            account_id=account_id
        )

        self._apply_transaction_to_account(transaction=transaction)

    @event
    def disable_account(self):
        self.bank_account.state = BankAccountStateEnum.disabled

    @event
    def enable_account(self):
        self.bank_account.state = BankAccountStateEnum.enabled


class BankDomainFactory:
    @staticmethod
    def build_bank_account_entity(owner_id: UUID, is_overdraft_protected: bool) -> BankAccountEntity:
        return BankAccountEntity(
            is_overdraft_protected=is_overdraft_protected,
            owner_id=owner_id,
            id=owner_id
        )

    @staticmethod
    def rebuild_bank_account_entity(
            is_overdraft_protected: bool,
            owner_id: UUID,
            state: BankAccountStateEnum,
            balance: float,
            _id: UUID,
            **kwargs
    ) -> BankAccountEntity:
        """
        Method for reconstituting BankAccount from the persistent layer

        :param is_overdraft_protected:
        :param owner_id:
        :param transactions:
        :param state:
        :param balance:
        :param _id:
        :return:
        """
        return BankAccountEntity(
            is_overdraft_protected=is_overdraft_protected,
            owner_id=owner_id,
            state=BankAccountStateEnum(state),
            balance=balance,
            id=_id
        )

    @staticmethod
    def build_bank_transaction_entity(
            item_id: UUID,
            method: BankTransactionMethodEnum,
            value: float,
            account_id: UUID,

    ) -> BankTransactionEntity:
        return BankTransactionEntity(
            created=datetime.now(),
            item_id=item_id,
            method=method,
            id=uuid4(),
            value=value,
            account_id=account_id,
        )

    @staticmethod
    def rebuild_bank_transaction_entity(
            created,
            _id,
            item_id,
            value,
            method,
            account_id,
            **kwargs

    ) -> BankTransactionEntity:
        return BankTransactionEntity(
            id=_id,
            created=created,
            item_id=item_id,
            value=value,
            method=BankTransactionMethodEnum(method),
            account_id=account_id
        )

    @staticmethod
    def build_bank_domain_aggregate(
            owner_id: UUID,
            is_overdraft_protected: bool
    ) -> BankDomainAggregate:
        return BankDomainAggregate.create(
            owner_id=owner_id,
            is_overdraft_protected=is_overdraft_protected,
        )


class BankDomainWriteModel:
    def __init__(self):
        self.client = get_client(
            db_host=MONGO_HOST,
            db_port=MONGO_PORT
        )

        self.db = get_database(client=self.client, db_name=APP_DB)

    def save_bank_account(self, bank_account: BankAccountEntity) -> UUID:
        collection = get_collection(database=self.db, collection=BANK_ACCOUNT_TABLE)
        try:
            add_item(collection=collection, item=serialize_aggregate(bank_account), key_id='id')
            return bank_account.id

        except DuplicateKeyError:
            return self.update_bank_account(
                bank_account=bank_account
            )

    def update_bank_account(self, bank_account: BankAccountEntity) -> UUID:
        collection = get_collection(database=self.db, collection=BANK_ACCOUNT_TABLE)

        new_data = serialize_aggregate(bank_account)

        result = update_item(
            collection=collection,
            item_id=bank_account.id,
            new_values=new_data
        )
        if result.matched_count == 0:
            raise Exception(f"No Records matching: '{bank_account.id}'")

        return bank_account.id


class BankDomainQueryModel:

    def __init__(self):
        self.client = get_client(
            db_host=MONGO_HOST,
            db_port=MONGO_PORT
        )

        self.db = get_database(client=self.client, db_name=APP_DB)

    def get_bank_account_by_id(self, account_id: UUID) -> dict:
        collection = get_collection(database=self.db, collection=BANK_ACCOUNT_TABLE)

        cursor = list(get_item(collection=collection, item_id=account_id, item_key="id"))

        if len(cursor) != 1:
            # TODO: Add Exception
            print("Query Error")

        return cursor[0]


class BankDomainRepository:

    def __init__(self):
        self.factory = BankDomainFactory()
        self.write_model = BankDomainWriteModel()
        self.query_model = BankDomainQueryModel()

    def save_bank_account(self, account: BankAccountEntity):
        if isinstance(account, BankAccountEntity):
            return self.write_model.save_bank_account(bank_account=account)

    def get_bank_account(self, account_id: UUID):
        data = self.query_model.get_bank_account_by_id(account_id=account_id)

        return self.factory.rebuild_bank_account_entity(
            **data
        )
