import os

STAGE = os.getenv("STAGE", "TEST")
_BANK_ACCOUNT_TABLE_ID = os.getenv("BANK_ACCOUNT_TABLE_ID", "bank_account_table")
_BANK_TRANSACTION_TABLE_ID = os.getenv("BANK_ACCOUNT_TABLE_ID", "bank_transaction_table")
_USER_ACCOUNT_TABLE_ID = os.getenv("USER_ACCOUNT_TABLE_ID", "user_account_table")

MONGO_HOST = os.getenv("MONGO_HOST", "192.168.1.5")
MONGO_PORT = os.getenv("MONGO_PORT", 27017)
_APP_DB = os.getenv("APP_DB", "BOE_MVP")

APP_DB = f'{STAGE}_{_APP_DB}'.upper()

BANK_ACCOUNT_TABLE = f'{STAGE}_{_BANK_ACCOUNT_TABLE_ID}'.upper()
BANK_TRANSACTION_TABLE = f'{STAGE}_{_BANK_TRANSACTION_TABLE_ID}'.upper()
USER_ACCOUNT_TABLE = f'{STAGE}_{_USER_ACCOUNT_TABLE_ID}'.upper()
