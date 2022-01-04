from cbaxter1988_utils.models.ddd_models import ValueObject


class Factory:
    @staticmethod
    def make_value_object(**kwargs):
        return ValueObject(**kwargs)
