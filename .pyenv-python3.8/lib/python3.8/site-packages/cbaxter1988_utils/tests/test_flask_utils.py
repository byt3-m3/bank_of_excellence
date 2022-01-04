import json

import pytest
from flask import Response
from cbaxter1988_utils.flask_utils import build_json_response, build_problem_detail_response


@pytest.fixture()
def json_response_dict():
    return build_json_response(
        status=200,
        payload={"msg": "test_message"}
    )


@pytest.fixture()
def json_response_str():
    return build_json_response(
        status=200,
        payload=json.dumps({"msg": "test_message"})
    )


@pytest.fixture()
def problem_detail_response():
    return build_problem_detail_response(
        instance=ValueError("Invalid Value"),
        detail="Account Overdrafted",
        title="AccountOverDraft",
        type_name="account_overdraft",
        http_status_code=200,
        exstensions=[
            {
                "account_id": "test_id"
            }
        ]
    )


def _test_build_json_response_1(json_response_dict):
    test_subject: Response = json_response_dict
    assert isinstance(test_subject, Response)
    assert test_subject.status == "200 OK"
    assert test_subject.content_type == "application/json"
    assert test_subject.response == [b'{"msg": "test_message"}']


def _test_build_json_response_2(json_response_str):
    test_subject: Response = json_response_str
    assert isinstance(test_subject, Response)
    assert test_subject.status == "200 OK"
    assert test_subject.content_type == "application/json"
    assert test_subject.response == [b'{"msg": "test_message"}']


def _test_build_problem_detail_response(problem_detail_response):
    test_subject: Response = problem_detail_response

    assert isinstance(test_subject, Response)
    assert test_subject.status == "200 OK"
    assert test_subject.content_type == "application/problem+json"
    assert test_subject.response == [b'{"type": "about:blank/account_overdraft", "type_base_uri": "about:blank", "title": "AccountOverDraft", "status": 200, "detail": "Account Overdrafted", "instance": "Invalid Value"}']
    assert test_subject.json['type'] == "about:blank/account_overdraft"
    assert test_subject.json['status'] == 200