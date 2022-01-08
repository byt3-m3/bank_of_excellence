import http

from boe.applications.user_domain_apps import (
    UserAuthenticationApp,
    UserAuthManagerEventFactory,
    NewPasswordRequiredError
)
from boe.env import COGNITO_APP_CLIENT_ID
from cbaxter1988_utils.flask_utils import build_json_response
from cbaxter1988_utils.log_utils import get_logger
from flask import Flask, request
from flask_cors import CORS

logger = get_logger("UserAuthAPI")

app = Flask(__name__)

CORS(app)


@app.route("/api/v1/auth/basic", methods=['POST'])
def authenticate_user():
    body = request.json

    app = UserAuthenticationApp()
    for event_name, payload in body.items():
        if event_name == 'UserAuthRequestEvent':
            try:
                auth_results = app.handle_event(
                    UserAuthManagerEventFactory.build_user_auth_request_event(
                        username=payload.get("username"),
                        password=payload.get("password"),
                        client_id=COGNITO_APP_CLIENT_ID
                    )
                )

                return build_json_response(http.HTTPStatus.OK, auth_results)
            except NewPasswordRequiredError:
                return build_json_response(http.HTTPStatus.EXPECTATION_FAILED, {"msg": "New Password Required"})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9000)
