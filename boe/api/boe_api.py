import http
from uuid import uuid4, UUID

from boe.clients.bank_manager_worker_client import BankManagerWorkerClient
from boe.clients.user_manager_worker_client import UserManagerWorkerClient
from boe.lib.domains.user_domain import UserDomainQueryModel, SubscriptionTypeEnum
from boe.utils.validation_utils import is_isodate_format_string
from cbaxter1988_utils.flask_utils import build_json_response
from cbaxter1988_utils.log_utils import get_logger
from cbaxter1988_utils.serialization_utils import serialize_object
from flask import Flask, request
from flask_cors import CORS, cross_origin

logger = get_logger("BOE_API")

app = Flask(__name__)

CORS(app)


@app.route("/api/v1/family", methods=['POST'])
@cross_origin()
def new_family():
    body = request.json

    event_payload = body.get('NewFamilyEvent')
    dob = event_payload.get("dob")

    try:
        if not is_isodate_format_string(dob):
            return build_json_response(
                status=http.HTTPStatus.EXPECTATION_FAILED,
                payload={
                    "msg": "Invalid ISO format"
                }
            )
        family_id = str(uuid4())
        user_manager_worker_client = UserManagerWorkerClient()
        user_manager_worker_client.publish_new_family_event(**event_payload, id=family_id)
        query_model = UserDomainQueryModel()
        query_response = query_model.get_family_by_id(family_id=UUID(family_id))
        if query_response:
            return build_json_response(
                status=http.HTTPStatus.OK,
                payload={
                    "family_id": family_id,
                    "msg": "Successfully Created"
                }
            )
        else:
            return build_json_response(
                status=http.HTTPStatus.OK,
                payload={
                    "family_id": family_id,
                    "msg": "Family Creation in Progress"
                }
            )

    except ValueError as err:

        return build_json_response(status=http.HTTPStatus.EXPECTATION_FAILED, payload={
            "exception": str(err)
        })


@app.route("/api/v1/family/<family_id>/subscription", methods=['POST'])
@cross_origin()
def change_family_subscription(family_id):
    body = request.json

    event_payload = body.get('FamilySubscriptionChangeEvent')
    user_manager_worker_client = UserManagerWorkerClient()

    user_manager_worker_client.publish_subscription_change_event(
        subscription_type=SubscriptionTypeEnum(event_payload.get("subscription_type")),
        family_id=family_id
    )
    return build_json_response(status=http.HTTPStatus.OK, payload={})


@app.route("/api/v1/family/<family_id>/child", methods=['POST'])
@cross_origin()
def new_family_child_account(family_id):
    body = request.json

    event_payload = body.get('NewFamilyChildEvent')
    family_id = UUID(family_id)
    dob = event_payload.get("dob")

    child_id = uuid4()

    user_manager_worker_client = UserManagerWorkerClient()
    bank_manager_worker_client = BankManagerWorkerClient()

    user_manager_worker_client.publish_new_child_event(
        family_id=family_id,
        first_name=event_payload['first_name'],
        last_name=event_payload['last_name'],
        email=event_payload['email'],
        grade=event_payload['grade'],
        dob=event_payload['dob'],
        child_id=child_id

    )
    bank_manager_worker_client.publish_new_bank_account_event(
        owner_id=str(child_id)
    )
    query_model = UserDomainQueryModel()

    account = query_model.get_user_account(family_id=family_id, user_account_id=child_id)
    if not account:
        return build_json_response(
            status=http.HTTPStatus.OK,
            payload={
                "msg": "Account Creation in Progress",
                "account_id": str(child_id)
            }
        )
    else:
        return build_json_response(status=http.HTTPStatus.OK, payload=serialize_object((account)))


@app.route("/api/v1/family/<family_id>/adult", methods=['POST'])
@cross_origin()
def new_family_adult_account(family_id):
    body = request.json

    event_payload = body.get('NewFamilyChildEvent')
    family_id = UUID(family_id)
    dob = event_payload.get("dob")

    adult_id = uuid4()

    user_manager_worker_client = UserManagerWorkerClient()
    user_manager_worker_client.publish_new_adult_account_event(
        family_id=family_id,
        first_name=event_payload['first_name'],
        last_name=event_payload['last_name'],
        email=event_payload['email'],
        dob=event_payload['dob'],
        adult_id=adult_id

    )

    query_model = UserDomainQueryModel()

    account = query_model.get_user_account(family_id=family_id, user_account_id=adult_id)
    if not account:
        return build_json_response(status=http.HTTPStatus.OK, payload={"msg": "Account Creation in Progress"})
    else:
        return build_json_response(status=http.HTTPStatus.OK, payload=serialize_object((account)))


@app.route("/api/v1/family/<family_id>", methods=['GET'])
@cross_origin()
def get_family(family_id):
    query_model = UserDomainQueryModel()

    family = query_model.get_family_by_id(family_id=UUID(family_id))

    if family:
        data = serialize_object(family)

        return build_json_response(status=http.HTTPStatus.OK, payload=data)
    else:
        return build_json_response(
            status=http.HTTPStatus.EXPECTATION_FAILED,
            payload={"msg": f"Family '{family_id}' Does not Exist"}
        )


@app.route("/api/v1/family/<family_id>/<user_id>", methods=['GET'])
@cross_origin()
def get_family_user_account(family_id, user_id):
    query_model = UserDomainQueryModel()

    user_account = query_model.get_user_account(family_id=UUID(family_id), user_account_id=UUID(user_id))

    return build_json_response(status=http.HTTPStatus.OK, payload=serialize_object(user_account))


@app.route("/api/v1/families", methods=['GET'])
@cross_origin()
def get_families():
    query_model = UserDomainQueryModel()
    family_models = query_model.scan_families()

    data = serialize_object(family_models)
    return build_json_response(
        status=http.HTTPStatus.OK,
        payload=data
    )


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
