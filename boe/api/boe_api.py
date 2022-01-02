import http
from uuid import uuid4, UUID

from boe.clients.user_manager_worker_client import UserManagerWorkerClient
from boe.lib.domains.user_domain import UserDomainQueryModel
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


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
