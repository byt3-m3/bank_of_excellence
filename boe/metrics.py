from boe.utils.metric_utils import MetricWriter


class ServiceMetricPublisher:

    def __init__(self):
        self.metric_writer = MetricWriter()

    def incr_bank_account_created_success_metric(self, service_name: str):
        self.metric_writer.publish_service_metric(
            metric_name='BankAccountCreated',
            field_name='success',
            field_value=float(1),
            service_name=service_name
        )

    def incr_bank_account_created_failed_metric(self, service_name: str):
        self.metric_writer.publish_service_metric(
            metric_name='BankAccountCreated',
            field_name='fail',
            field_value=float(1),
            service_name=service_name
        )

    def incr_transaction_processed_success_metric(self, service_name: str):
        self.metric_writer.publish_service_metric(
            metric_name='TransActionProcessed',
            field_name='success',
            field_value=float(1),
            service_name=service_name
        )

    def incr_transaction_processed_failed_metric(self, service_name: str):
        self.metric_writer.publish_service_metric(
            metric_name='TransActionProcessed',
            field_name='failed',
            field_value=float(1),
            service_name=service_name
        )

    def incr_family_created_success_metric(self, service_name: str):
        self.metric_writer.publish_service_metric(
            metric_name='FamilyCreated',
            field_name='success',
            field_value=float(1),
            service_name=service_name
        )

    def incr_family_created_failed_metric(self, service_name: str):
        self.metric_writer.publish_service_metric(
            metric_name='FamilyCreated',
            field_name='failed',
            field_value=float(1),
            service_name=service_name
        )

    def incr_child_user_account_created_success_metric(self, service_name: str):
        self.metric_writer.publish_service_metric(
            metric_name='ChildUserAccountCreated',
            field_name='success',
            field_value=float(1),
            service_name=service_name
        )

    def incr_adult_user_account_created_success_metric(self, service_name: str):
        self.metric_writer.publish_service_metric(
            metric_name='AdultUserAccountCreated',
            field_name='success',
            field_value=float(1),
            service_name=service_name
        )

    def incr_family_subscription_upgrade_success_metric(self, service_name: str):
        self.metric_writer.publish_service_metric(
            metric_name='FamilySubscriptionUpgrade',
            field_name='success',
            field_value=float(1),
            service_name=service_name
        )

    def incr_family_subscription_downgrade_success_metric(self, service_name: str):
        self.metric_writer.publish_service_metric(
            metric_name='FamilySubscriptionDowngrade',
            field_name='success',
            field_value=float(1),
            service_name=service_name
        )

    def incr_cognito_user_created_success_metric(self, service_name: str):
        self.metric_writer.publish_service_metric(
            metric_name='CognitoUserCreated',
            field_name='success',
            field_value=float(1),
            service_name=service_name
        )

    def incr_mock_cognito_user_created_success_metric(self, service_name: str):
        self.metric_writer.publish_service_metric(
            metric_name='MockCognitoUserCreated',
            field_name='success',
            field_value=float(1),
            service_name=service_name
        )

    def incr_store_created_success_metric(self, service_name: str):
        self.metric_writer.publish_service_metric(
            metric_name='StoreCreated',
            field_name='success',
            field_value=float(1),
            service_name=service_name
        )
