from cbaxter1988_utils.aws_secrets_manager_utils import get_credentials

MONGO_DB_CRED_SECRET = 'dev/boe/mongodb_creds'
RABBITMQ_CRED_SECRET = 'dev/boe/rabbitmq_creds'

_MONGO_DB_CREDS_SECRET = get_credentials(MONGO_DB_CRED_SECRET)
_RABBIT_MQ_CREDS = get_credentials(RABBITMQ_CRED_SECRET)

MONGO_DB_USERNAME = _MONGO_DB_CREDS_SECRET['username']
MONGO_DB_PASSWORD = _MONGO_DB_CREDS_SECRET['password']

RABBITMQ_USERNAME = _RABBIT_MQ_CREDS['username']
RABBITMQ_PASSWORD = _RABBIT_MQ_CREDS['password']
