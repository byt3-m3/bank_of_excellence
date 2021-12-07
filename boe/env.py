import os

STAGE = os.getenv("STAGE", "GAMMA")
_BANK_ACCOUNT_TABLE_ID = os.getenv("BANK_ACCOUNT_TABLE_ID", "bank_account_table")
_BANK_TRANSACTION_TABLE_ID = os.getenv("BANK_ACCOUNT_TABLE_ID", "bank_transaction_table")

MONGO_HOST = os.getenv("MONGO_HOST", "192.168.1.5")
MONGO_PORT = os.getenv("MONGO_PORT", 27017)
_APP_DB = os.getenv("APP_DB", "BOE_MVP")

BANK_ACCOUNT_TABLE = f'{STAGE}_{_BANK_ACCOUNT_TABLE_ID}'.capitalize()
BANK_TRANSACTION_TABLE = f'{STAGE}_{_BANK_TRANSACTION_TABLE_ID}'.capitalize()
APP_DB = f'{STAGE}_{_APP_DB}'.capitalize()
