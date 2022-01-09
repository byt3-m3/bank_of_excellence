import http

from boe.applications.user_domain_apps import (
    UserAuthenticationApp,
    UserAuthManagerEventFactory,
    NewPasswordRequiredError
)
from boe.lib.domains.user_domain import UserDomainQueryModel
from boe.env import COGNITO_APP_CLIENT_ID
from cbaxter1988_utils.flask_utils import build_json_response
from cbaxter1988_utils.log_utils import get_logger
from flask import Flask, request
from flask_cors import CORS
from boe.utils.password_utils import get_key_salt_from_value, verify_password_hash

logger = get_logger("UserAuthAPI")

app = Flask(__name__)

CORS(app)


@app.route("/api/v1/auth/cognito/basic", methods=['POST'])
def authenticate_cognito_user():
    body = request.json

    app = UserAuthenticationApp()
    for event_name, payload in body.items():
        if event_name == 'UserAuthRequestEvent':
            try:
                auth_results = app.handle_event(
                    UserAuthManagerEventFactory.build_cognito_auth_request_event(
                        username=payload.get("username"),
                        password=payload.get("password"),
                        client_id=COGNITO_APP_CLIENT_ID
                    )
                )

                return build_json_response(http.HTTPStatus.OK, auth_results)
            except NewPasswordRequiredError:
                return build_json_response(http.HTTPStatus.EXPECTATION_FAILED, {"msg": "New Password Required"})


@app.route("/api/v1/auth/local/basic", methods=['POST'])
def authenticate_local_user():
    body = request.json

    query_model = UserDomainQueryModel()
    creds = query_model.get_local_credential_by_username(username=body['LocalAuthRequest'].get("username"))
    if not creds:
        return build_json_response(
            status=http.HTTPStatus.EXPECTATION_FAILED,
            payload={"msg": "Invalid Username or Password"}
        )

    key, salt = get_key_salt_from_value(stored_key=creds.password_hash)

    verification_result = verify_password_hash(
        password=body['LocalAuthRequest'].get("password"),
        old_key=key,
        salt=salt
    )
    if verification_result:
        return build_json_response(
            status=http.HTTPStatus.OK,
            payload={
                "auth_result": verification_result,
                "id": str(creds.user_id)
            }
        )
    else:
        return build_json_response(
            status=http.HTTPStatus.OK,
            payload={
                "auth_result": verification_result
            }
        )


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9000)
