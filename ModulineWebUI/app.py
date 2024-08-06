import random
import string
from functools import wraps

from microdot import Microdot, Request, Response, redirect
from microdot.session import Session


def authenticate_token(tokens: "list[str]", token: str) -> bool:
    try:
        tokens.index(token)
        return True
    except ValueError:
        return False


def register_token(tokens: "list[str]", token: str):
    tokens.append(token)


def remove_token(tokens: "list[str]", token: str):
    try:
        tokens.remove(token)
    except ValueError:
        pass


def auth(func):
    @wraps(func)
    async def wrapper(req: Request, session: Session, *args, **kwargs):
        if not authenticate_token(tokens, session.get("token")):
            return redirect("/")
        return await func(req, session, *args, **kwargs)

    return wrapper


app = Microdot()
Session(
    app,
    secret_key="".join(
        random.SystemRandom().choice(string.ascii_uppercase + string.digits)
        for _ in range(10)
    ),
)  # generate new session key when the server is restarted
Response.default_content_type = "text/html"
