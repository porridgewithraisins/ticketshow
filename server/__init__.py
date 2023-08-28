from typing import Any

from flask import Flask, request, Response

import shared.config as config
import server.functions as functions
from server.utils import lookup, get_docs


server = Flask(__name__)


@server.post("/<method>")
def api(method: str):
    data: Any = request.json if request.is_json else {}

    fn = lookup(functions, method)
    if fn is None:
        return {"error": "Method not found."}
    return fn(data)


@server.get("/docs")
def docs():
    return get_docs(functions)


@server.after_request
def add_cors_headers(response: Response):
    response.headers["Access-Control-Allow-Origin"] = "*" # config.frontend_uri
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


def start():
    server.run(host=config.host, port=config.port)
