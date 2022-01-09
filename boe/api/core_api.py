import http
from uuid import uuid4, UUID

from boe.clients.bank_manager_worker_client import BankManagerWorkerClient
from boe.clients.store_worker_client import StoreWorkerClient
from boe.clients.task_manager_client import TaskManagerWorkerClient
from boe.clients.user_manager_worker_client import UserManagerWorkerClient
from boe.env import API_LISTEN_PORT
from boe.lib.domains.store_domain import StoreDomainQueryModel
from boe.lib.domains.task_domain import TaskDomainQueryModel
from boe.lib.domains.user_domain import UserDomainQueryModel, SubscriptionTypeEnum, UserAccountTypeEnum
from boe.utils.validation_utils import is_isodate_format_string
from cbaxter1988_utils.flask_utils import build_json_response
from cbaxter1988_utils.log_utils import get_logger
from cbaxter1988_utils.serialization_utils import serialize_object
from flask import Flask, request
from flask_cors import CORS, cross_origin

logger = get_logger("BOE_API")

app = Flask(__name__)

CORS(app)


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


@app.route("/api/v1/family/<family_id>", methods=['GET'])
@cross_origin()
def get_family(family_id):
    query_model = UserDomainQueryModel()

    family = query_model.get_family_by_id(family_aggregate_id=UUID(family_id))

    if family:
        data = serialize_object(family)

        return build_json_response(status=http.HTTPStatus.OK, payload=data)
    else:
        return build_json_response(
            status=http.HTTPStatus.EXPECTATION_FAILED,
            payload={"msg": f"Family '{family_id}' Does not Exist"}
        )


@app.route("/api/v1/family/<family_id>/store", methods=['GET'])
@cross_origin()
def get_store(family_id):
    query_model = StoreDomainQueryModel()
    try:
        store_model = query_model.get_store_by_id(store_id=UUID(family_id))
    except ValueError as err:
        return build_json_response(status=http.HTTPStatus.EXPECTATION_FAILED, payload={"msg": str(err)})
    if store_model is None:
        return build_json_response(
            status=http.HTTPStatus.EXPECTATION_FAILED,
            payload={"msg": f"Store '{family_id}' not found"}
        )
    return build_json_response(status=http.HTTPStatus.OK, payload=serialize_object(store_model))


@app.route("/api/v1/family/<family_id>/store", methods=['POST'])
@cross_origin()
def store_events(family_id):
    body = request.json

    store_manager_client = StoreWorkerClient()

    for event_name, payload in body.items():
        if event_name == 'RemoveStoreItem':
            store_manager_client.publish_remove_store_item_event(
                store_id=UUID(family_id),
                item_id=payload.get("item_id")
            )
            return build_json_response(status=http.HTTPStatus.OK, payload={"msg": "In Progress"})

        if event_name == 'NewStoreItemEvent':
            store_manager_client.publish_new_store_item_event(
                family_id=UUID(family_id),
                item_name=payload.get("item_name"),
                item_description=payload.get("item_description"),
                item_value=payload.get("item_value"),
            )
            return build_json_response(status=http.HTTPStatus.OK, payload={"msg": "In Progress - Store Item Submitted"})


@app.route("/api/v1/family/<family_id>/child/<account_id>/task", methods=['POST'])
@cross_origin()
def task_events(family_id, account_id):
    body = request.json
    task_manager_worker_client = TaskManagerWorkerClient()

    for event_name, payload in body.items():
        if event_name == 'NewTaskEvent':
            user_query_model = UserDomainQueryModel()
            try:

                user_query_model.get_user_account(family_id=UUID(family_id),
                                                  user_account_id=UUID(account_id))
            except ValueError:
                return build_json_response(status=http.HTTPStatus.EXPECTATION_FAILED,
                                           payload={"msg": "User does Not exists "})

            task_manager_worker_client.publish_new_task_event(
                name=payload.get("name"),
                description=payload.get("description"),
                due_date=payload.get("due_date"),
                owner_id=UUID(account_id),
                evidence_required=payload.get("evidence_required"),
                value=payload.get("value")
            )

            return build_json_response(status=http.HTTPStatus.OK, payload={"msg": "task created"})

        if event_name == 'MarkTaskCompleteEvent':
            task_manager_worker_client.publish_mark_task_complete_event(task_id=payload.get("task_id"))

            return build_json_response(status=http.HTTPStatus.OK, payload={"msg": "In Progress"})


@app.route("/api/v1/family/<family_id>/child/<child_id>/tasks", methods=['GET'])
@cross_origin()
def get_child_task(family_id, child_id):
    query_model = TaskDomainQueryModel()

    results = query_model.get_tasks_by_owner_id(owner_id=UUID(child_id))
    return build_json_response(status=http.HTTPStatus.OK, payload=serialize_object(results))


@app.route("/api/v1/registration/family/local", methods=['POST'])
@cross_origin()
def register_family_local():
    body = request.json

    for event_name, payload in body.items():
        if event_name == 'FamilyRegistrationLocalRequest':
            family_id = uuid4()

            client = UserManagerWorkerClient()
            client.publish_create_family_local_user_event(
                family_id=family_id,
                family_name=payload.get("family_name"),
                last_name=payload.get("last_name"),
                first_name=payload.get("first_name"),
                account_type=UserAccountTypeEnum.adult,
                password_hash=payload.get("password_hash").encode(),
                email=payload.get("email"),
                dob=payload.get("dob"),

            )
            return build_json_response(status=http.HTTPStatus.OK, payload={"family_id": str(family_id)})


@app.route("/api/v1/family/<family_id>/member/<member_id>")
@cross_origin()
def get_family_member(family_id, member_id):
    query_model = UserDomainQueryModel()
    user_account = query_model.get_user_account_by_id(user_aggregate_id=UUID(member_id))
    if user_account:
        return build_json_response(status=http.HTTPStatus.OK, payload=serialize_object(user_account))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=API_LISTEN_PORT)
