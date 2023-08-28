import hmac
from hashlib import sha256
from typing import Any

import shared.config as config
from shared.io import sqlite, redis
from server.utils import validate
from server.dtos import Token


def make_token(user_id: int) -> str:
    data = f"{user_id}"
    signature = hmac.new(config.secret.encode(), data.encode(), sha256).hexdigest()
    token = signature + "." + data
    return token


def _parse_token(token: str) -> int | None:
    try:
        if not token:
            return None
        provided_signature, data = token.split(".")
        calculated_signature = hmac.new(config.secret.encode(), data.encode(), sha256).hexdigest()

        if not hmac.compare_digest(provided_signature, calculated_signature):
            return None
        user_id = int(data)
        return user_id
    except:
        return None


def authenticate(data: Any, require_admin: bool = False, allow_banned: bool = False):
    db = sqlite(readonly=True)
    if not validate(Token, data):
        return None
    user_id = _parse_token(data.get("token"))
    table = "admins" if require_admin else "users" if allow_banned else "goodboys"

    if (
        not user_id
        or not (user := db.execute(f"select * from {table} where id = ?", [user_id]).fetchone())
    ):
        return None

    if not require_admin and not allow_banned:
        redis.set(f"visited:{user_id}", 1)
    return user
