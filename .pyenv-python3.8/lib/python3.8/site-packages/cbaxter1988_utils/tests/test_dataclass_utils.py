import pytest
from dataclasses import dataclass
from cbaxter1988_utils.dataclass_utils import model_to_dict



def test_model_to_dict(person):
    # invocation
    person_dict = model_to_dict(person)

    # validation
    assert isinstance(person_dict, dict)
