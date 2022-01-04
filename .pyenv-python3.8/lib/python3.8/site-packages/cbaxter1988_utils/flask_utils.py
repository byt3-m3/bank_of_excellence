import http
import json
from http import HTTPStatus
from typing import Union, List

import flask
from cbaxter1988_utils.models.http_models.problem_detail_rfc_7807_model import ProblemDetailModel, \
    PROBLEM_DETAIL_HEADER_JSON


def build_problem_detail_response(
        http_status_code: Union[HTTPStatus, int],
        detail: str,
        type_name: str,
        title: str,
        instance: BaseException,
        exstensions: List[dict]
) -> flask.Response:
    """
    Builds a ProblemDetail response based on RFC 7807

    :param http_status_code: The HTTP status code ([RFC7231]
    :param detail: A human-readable explanation specific to this
occurrence of the problem.
    :param type_name: A URI reference [RFC3986] that identifies the problem type.
    :param title:  A short, human-readable summary of the problem type.
    :param instance:  A URI reference that identifies the specific
occurrence of the problem.
    :return:
    """
    model = ProblemDetailModel(
        type=type_name,
        status=http_status_code,
        detail=detail,
        instance=str(instance),
        title=title,
    )
    for exstension in exstensions:
        for key, val in exstension.items():
            setattr(model, key, val)

    return flask.Response(
        status=http_status_code,
        headers=PROBLEM_DETAIL_HEADER_JSON,
        response=model.to_json()

    )


def build_json_response(status: Union[http.HTTPStatus, int], payload: Union[dict, str]) -> flask.Response:
    """
    Returns Flask.Response as content-type JSON

    :param status:
    :param payload:
    :return:
    """
    if isinstance(payload, dict):
        return flask.Response(
            status=status,
            headers={"content-type": "application/json"},
            response=json.dumps(payload)
        )

    if isinstance(payload, str):
        return flask.Response(
            status=status,
            headers={"content-type": "application/json"},
            response=payload
        )
