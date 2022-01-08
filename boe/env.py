import os

from boe.secrets import RABBITMQ_USERNAME, RABBITMQ_PASSWORD

# Core Vars

STAGE = os.getenv("STAGE", "LOCAL")
API_LISTEN_PORT = os.getenv("API_LISTEN_PORT", 5000)

# MongoDB Vars

MONGO_HOST = os.getenv("MONGO_HOST", "192.168.1.5")
MONGO_PORT = os.getenv("MONGO_PORT", 27017)

_APP_DB = os.getenv("APP_DB", "BOE_MVP")
_BANK_ACCOUNT_TABLE_ID = os.getenv("BANK_ACCOUNT_TABLE_ID", "bank_account_aggregate_table")
_BANK_TRANSACTION_TABLE_ID = os.getenv("BANK_ACCOUNT_TABLE_ID", "bank_transaction_table")
_CHILD_ACCOUNT_TABLE_ID = os.getenv("CHILD_ACCOUNT_TABLE_ID", "child_account_table")
_ADULT_ACCOUNT_TABLE_ID = os.getenv("ADULT_ACCOUNT_TABLE_ID", "adult_account_table")
_FAMILY_TABLE_ID = os.getenv("USER_ACCOUNT_TABLE_ID", "family_aggregate_table")
_STORE_TABLE_ID = os.getenv("STORE_TABLE_ID", "store_aggregate_table")
_TASK_TABLE_ID = os.getenv("TASK_TABLE_ID", "task_aggregate_table")

APP_DB = f'{STAGE}_{_APP_DB}'.upper()
BANK_ACCOUNT_TABLE = f'{STAGE}_{_BANK_ACCOUNT_TABLE_ID}'.upper()
BANK_TRANSACTION_TABLE = f'{STAGE}_{_BANK_TRANSACTION_TABLE_ID}'.upper()
CHILD_ACCOUNT_TABLE = f'{STAGE}_{_CHILD_ACCOUNT_TABLE_ID}'.upper()
ADULT_ACCOUNT_TABLE = f'{STAGE}_{_ADULT_ACCOUNT_TABLE_ID}'.upper()
FAMILY_TABLE = f'{STAGE}_{_FAMILY_TABLE_ID}'.upper()
STORE_TABLE = f'{STAGE}_{_STORE_TABLE_ID}'.upper()
TASK_TABLE = f'{STAGE}_{_TASK_TABLE_ID}'.upper()

# Pika VARS

AMQP_HOST = os.getenv("AMQP_HOST", '192.168.1.5')
AMQP_PORT = os.getenv("AMQP_PORT", 5672)

AMQP_URL = os.getenv("AMPQ_URL", f"amqp://{RABBITMQ_USERNAME}:{RABBITMQ_PASSWORD}@{AMQP_HOST}:{AMQP_PORT}")

_BANK_MANAGER_WORKER_QUEUE = os.getenv("BANK_MANAGER_APP_QUEUE", "bank_manager_worker_queue")
_STORE_MANAGER_WORKER_QUEUE = os.getenv("STORE_MANAGER_APP_QUEUE", "store_manager_worker_queue")
_PERSISTENCE_WORKER_QUEUE = os.getenv("PERSISTENCE_WORKER_QUEUE", "persistence_worker_queue")
_NOTIFICATION_WORKER_QUEUE = os.getenv("NOTIFICATION_WORKER_QUEUE", 'notification_worker_queue')
_USER_MANAGER_WORKER_QUEUE = os.getenv("USER_MANAGER_WORKER_QUEUE", 'user_manager_worker_queue')
_TASK_MANAGER_WORKER_QUEUE = os.getenv("TASK_MANAGER_WORKER_QUEUE", 'task_manager_worker_queue')

_BOE_DLQ_QUEUE = os.getenv("BOE_DLQ_QUEUE", "BOE_ERROR_DLQ")
_BOE_DLQ_EXCHANGE = os.getenv("BOE_DLQ_EXCHANGE", "BOE_ERROR_EXCHANGE")
_BOE_DLQ_DEFAULT_ROUTING_KEY = os.getenv("BOE_DLQ_DEFAULT_ROUTING_KEY", "boe_exception")

BANK_MANAGER_WORKER_QUEUE = f'{STAGE}_{_BANK_MANAGER_WORKER_QUEUE}'.upper()
NOTIFICATION_WORKER_QUEUE = f'{STAGE}_{_NOTIFICATION_WORKER_QUEUE}'.upper()
STORE_MANAGER_WORKER_QUEUE = f'{STAGE}_{_STORE_MANAGER_WORKER_QUEUE}'.upper()
PERSISTENCE_WORKER_QUEUE = f'{STAGE}_{_PERSISTENCE_WORKER_QUEUE}'.upper()
USER_MANAGER_WORKER_QUEUE = f'{STAGE}_{_USER_MANAGER_WORKER_QUEUE}'.upper()
TASK_MANAGER_WORKER_QUEUE = f'{STAGE}_{_TASK_MANAGER_WORKER_QUEUE}'.upper()

BOE_DLQ_QUEUE = f'{STAGE}_{_BOE_DLQ_QUEUE}'
BOE_DLQ_EXCHANGE = f'{STAGE}_{_BOE_DLQ_EXCHANGE}'
BOE_DLQ_DEFAULT_ROUTING_KEY = f'{_BOE_DLQ_DEFAULT_ROUTING_KEY}'
BOE_APP_EXCHANGE = f'{STAGE}_BOE_APP_EXCHANGE'

BANK_MANAGER_QUEUE_ROUTING_KEY = 'bank_manager_service'
USER_MANAGER_QUEUE_ROUTING_KEY = 'user_manager_service'
TASK_MANAGER_QUEUE_ROUTING_KEY = 'task_manager_service'
STORE_MANAGER_QUEUE_ROUTING_KEY = 'store_manager_service'
PERSISTENCE_QUEUE_ROUTING_KEY = 'persistence_service'
NOTIFICATION_QUEUE_ROUTING_KEY = 'notification_service'

# SQLLITE Vars

_WORKER_EVENT_STORE = os.getenv('WORKER_EVENT_STORE', 'eventstore.sqllite')

_BANK_MANAGER_WORKER_EVENT_STORE = os.getenv('BANK_MANAGER_WORKER_EVENT_STORE', '_db/bm_eventstore.sqllite')
_PERSISTENCE_SERVICE_WORKER_EVENT_STORE = os.getenv('PERSISTENCE_SERVICE_WORKER_EVENT_STORE',
                                                    '_db/ps_eventstore.sqllite')
_STORE_MANAGER_WORKER_EVENT_STORE = os.getenv('STORE_MANAGER_WORKER_EVENT_STORE', '_db/sm_eventstore.sqllite')
_USER_MANAGER__WORKER_EVENT_STORE = os.getenv('USER_MANAGER_WORKER_EVENT_STORE', '_db/user_manager_eventstore.sqllite')

BANK_MANAGER_WORKER_EVENT_STORE = f'{_BANK_MANAGER_WORKER_EVENT_STORE}'
PERSISTENCE_SERVICE_WORKER_EVENT_STORE = f'{_PERSISTENCE_SERVICE_WORKER_EVENT_STORE}'
STORE_MANAGER_WORKER_EVENT_STORE = f'{_STORE_MANAGER_WORKER_EVENT_STORE}'
USER_MANAGER_WORKER_EVENT_STORE = f'{_USER_MANAGER__WORKER_EVENT_STORE}'

# AWS Vars

COGNITO_POOL_ID = os.getenv("COGNITO_POOL_ID", 'us-east-1_fRkg83NZI')
COGNITO_APP_CLIENT_ID = os.getenv("COGNITO_APP_CLIENT_ID")

# Postgres Config

POSTGRES_DB_HOST = os.getenv("POSTGRES_DB_HOST", '192.168.1.5')
POSTGRES_DB_PORT = os.getenv("POSTGRES_DB_PORT", '5432')
POSTGRES_DB_NAME = os.getenv("POSTGRES_DB_NAME", 'eventsourcing')
POSTGRES_DB_USER = os.getenv("POSTGRES_DB_USER", "eventsourcing")
POSTGRES_DB_PASSWORD = os.getenv("POSTGRES_DB_PASSWORD", "eventsourcing")
