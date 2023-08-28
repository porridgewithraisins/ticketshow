from typing import TypeVar
from os import environ


class ConfigurationError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


T = TypeVar("T", str, int, float)


def required_environment_variable(name: str, coerce_to: type[T]) -> T:
    if name not in environ:
        raise ConfigurationError(f"Missing configuration {name}")
    try:
        return coerce_to(environ[name])
    except ValueError:
        raise ConfigurationError(f"Configuration {name} must be of type {coerce_to}")


host = required_environment_variable("HOST", str)
port = required_environment_variable("PORT", int)
secret = required_environment_variable("SECRET", str)
frontend_uri = required_environment_variable("FRONTEND_URI", str)
sqlite = required_environment_variable("SQLITE", str)
redis = required_environment_variable("REDIS", str)
smtp_host = required_environment_variable("SMTP_HOST", str)
smtp_port = required_environment_variable("SMTP_PORT", int)
smtp_username = required_environment_variable("SMTP_USERNAME", str)
smtp_password = required_environment_variable("SMTP_PASSWORD", str)
email_from = required_environment_variable("SMTP_FROM", str)
