import json


def extract_body_from_event(event):
    request_body = None
    if event.get("body"):
        if isinstance(event['body'], str):
            request_body = json.loads(event['body'])
        else:
            request_body = event['body']
    else:
        if isinstance(event, str):
            request_body = json.loads(event)
        else:
            request_body = event

    return request_body


def extract_params_from_event(event):
    if event.get("pathParameters"):
        return event['pathParameters']
