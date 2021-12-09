from boe.lib.common_models import Aggregate
from dataclasses import dataclass, field, asdict
from enum import Enum
from uuid import UUID, uuid4
from typing import List, Dict
from cbaxter1988_utils.pymongo_utils import (
    get_client,
    get_collection,
    get_database,
    add_item,
    get_item,
)
from datetime import datetime
from boe.env import MONGO_HOST, MONGO_PORT, APP_DB, BANK_ACCOUNT_TABLE
from boe.utils.serialization_utils import serialize_aggregate, serialize_dataclass


class BankAccountStateEnum(Enum):
    active = 0
    inactive = 1


class BankTransactionMethodEnum(Enum):
    add = 0
    subtract = 1


@dataclass
class BankTransaction:
    transaction_id: UUID
    created: datetime
    item_id: UUID
    value: float
    method: BankTransactionMethodEnum = field(default_factory=BankTransactionMethodEnum)


@dataclass
class BankAccountAggregate(Aggregate):
    owner_id: UUID
    is_overdraft_protected: bool
    transactions: List[BankTransaction] = field(default_factory=list)
    state: BankAccountStateEnum = field(default=BankAccountStateEnum.active)
    _balance: float = field(default=0)

    @property
    def balance(self):
        self._balance = 0
        for transaction in self.transactions:
            if transaction.method == BankTransactionMethodEnum.add:
                self._balance += transaction.value

            if transaction.method == BankTransactionMethodEnum.subtract:
                self._balance -= transaction.value

        return self._balance

    def apply_transaction(self, transaction: BankTransaction) -> bool:
        self.transactions.append(transaction)
        _ = self.balance
        return True

    def get_transaction_by_id(self, transaction_id: UUID) -> BankTransaction:
        for _transaction in self.transactions:
            if transaction_id == _transaction.transaction_id:
                return _transaction


class BankDomainFactory:
    @staticmethod
    def build_bank_account(owner_id: UUID, is_overdraft_protected: bool) -> BankAccountAggregate:
        return BankAccountAggregate(
            is_overdraft_protected=is_overdraft_protected,
            owner_id=owner_id,
            id=owner_id
        )

    @staticmethod
    def rebuild_bank_account(
            is_overdraft_protected: bool,
            owner_id: UUID,
            transactions: list,
            state: BankAccountStateEnum,
            _balance: float,
            _id: UUID,
            **kwargs
    ) -> BankAccountAggregate:
        """
        Method for reconstituting BankAccount from the persistent layer

        :param is_overdraft_protected:
        :param owner_id:
        :param transactions:
        :param state:
        :param _balance:
        :param _id:
        :return:
        """
        return BankAccountAggregate(
            is_overdraft_protected=is_overdraft_protected,
            owner_id=owner_id,
            transactions=[
                BankDomainFactory.rebuild_bank_transaction(**transaction, _id=_id)
                for transaction in transactions
            ],
            state=BankAccountStateEnum(state),
            _balance=_balance,
            id=_id
        )

    @staticmethod
    def build_bank_transaction(item_id: UUID, method: BankTransactionMethodEnum, value: float) -> BankTransaction:
        return BankTransaction(
            created=datetime.now(),
            item_id=item_id,
            method=method,
            transaction_id=uuid4(),
            value=value
        )

    @staticmethod
    def rebuild_bank_transaction(
            created,
            transaction_id,
            item_id,
            value,
            method,
            **kwargs

    ) -> BankTransaction:
        return BankTransaction(

            created=created,
            transaction_id=transaction_id,
            item_id=item_id,
            value=value,
            method=BankTransactionMethodEnum(method)
        )


class BankDomainWriteModel:
    def __init__(self):
        self.client = get_client(
            db_host=MONGO_HOST,
            db_port=MONGO_PORT
        )

        self.db = get_database(client=self.client, db_name=APP_DB)

    def save_bank_account(self, bank_account: BankAccountAggregate) -> UUID:
        collection = get_collection(database=self.db, collection=BANK_ACCOUNT_TABLE)

        add_item(collection=collection, item=serialize_aggregate(bank_account), key_id='id')
        return bank_account.id

    def update_bank_account(self, bank_account: BankAccountAggregate) -> UUID:
        return NotImplemented


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

    def save_bank_account(self, account: BankAccountAggregate):
        if isinstance(account, BankAccountAggregate):
            return self.write_model.save_bank_account(bank_account=account)

    def get_bank_account(self, account_id: UUID):
        data = self.query_model.get_bank_account_by_id(account_id=account_id)

        return self.factory.rebuild_bank_account(
            **data
        )
