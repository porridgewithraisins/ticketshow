from collections import namedtuple
from sqlite3 import Connection, Cursor, Row, connect
from email.message import EmailMessage
import smtplib
from celery import Celery
from redis import Redis

import shared.config as config


def namedtuple_factory(cursor: Cursor, row: Row):
    fields = [col[0] for col in cursor.description]  # type: ignore
    Record = namedtuple("Record", fields)  # type: ignore
    return Record(*row)


_readonly = connect(config.sqlite + "?mode=ro", uri=True, check_same_thread=False)

redis = Redis.from_url(config.redis, decode_responses=True)

celery = Celery("jobs", broker=config.redis, backend=config.redis)


def sqlite(readonly: bool = False) -> Connection:
    if readonly:
        _readonly.row_factory = namedtuple_factory
        return _readonly
    db = connect(config.sqlite, uri=True)
    db.row_factory = namedtuple_factory
    db.execute("pragma foreign_keys=on")
    return db


def email(sender: str, receiver: str, subject: str, html: str):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver
    msg.set_content(html, subtype="html")
    with smtplib.SMTP(config.smtp_host, config.smtp_port) as mailer:
        mailer.login(config.smtp_username, config.smtp_password)
        return mailer.send_message(msg)
