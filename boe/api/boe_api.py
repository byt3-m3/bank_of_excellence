import http
from uuid import uuid4

from boe.clients.user_manager_worker_client import UserManagerWorkerClient
from boe.utils.validation_utils import is_isodate_format_string
from cbaxter1988_utils.flask_utils import build_json_response
from cbaxter1988_utils.log_utils import get_logger
from flask import Flask, request
from flask_cors import CORS, cross_origin

logger = get_logger("BOE_API")

app = Flask(__name__)

CORS(app)




@app.route("/api/v1/user_manager/family", methods=['POST'])
@cross_origin(expose_headers=['x-family-id'])
def new_family():
    user_manager_worker_client = UserManagerWorkerClient()
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

        user_manager_worker_client.publish_new_family_event(**event_payload, id=family_id)
        resp = build_json_response(status=http.HTTPStatus.OK, payload=body)
        resp.headers.set('x-family-id', family_id)
        print(resp.headers)
        return resp

    except ValueError as err:
        return build_json_response(status=http.HTTPStatus.EXPECTATION_FAILED, payload={
            "exception": str(err)
        })


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
