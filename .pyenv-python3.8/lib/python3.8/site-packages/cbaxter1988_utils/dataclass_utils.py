from dataclasses import asdict, is_dataclass

"""
Collection of python dataclass utilites 
"""


def model_to_dict(data_class) -> dict:
    """
    Converts the given Dataclass to a dictionary

    Raises TypeError if the given type is not a python dataclass

    :param data_class:
    :return:
    """
    if is_dataclass(data_class):
        return asdict(data_class)
    else:
        raise TypeError("Invalid Type Provided")
