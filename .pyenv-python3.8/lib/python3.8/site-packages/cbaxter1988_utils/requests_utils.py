import requests


def get_html_page(url) -> str:
    return requests.get(url).text


def get_request(url):
    return requests.get(url)


def post_request(url, body):
    response = requests.post(url=url, json=body, headers={"Content-Type": "application/json"})
    return response
